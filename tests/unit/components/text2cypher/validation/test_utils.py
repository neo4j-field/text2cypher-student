from ps_genai_agents.components.text2cypher.validation._utils import (
    get_node_label_pattern,
    get_node_pattern,
    get_property_pattern,
    parse_labels_or_types,
    process_match_clause_property_ids,
)


def test_get_property_pattern(prop_1: str) -> None: ...


def test_get_node_pattern(node_1: str) -> None: ...


def test_get_node_label_pattern() -> None:
    pat = get_node_label_pattern()
    assert pat.findall("(n:Node)")[0] == "Node"
    assert pat.findall("(m {id:'001'})") == []
    assert pat.findall("(nodeA:Node {id:'001'})")[0] == "Node "
    assert pat.findall("(node_1:N)")[0] == "N"
    assert pat.findall("(node_1:Node{id:'001'})")[0] == "Node"
    assert pat.findall("(nodeA:`Node one` {id:'001'})")[0] == "Node one"
    assert pat.findall("(node_1:Node|NodeB{id:'001'})")[0] == "Node|NodeB"
    assert pat.findall("(node_1:Node&NodeB {id:'001'})")[0] == "Node&NodeB "


def test_process_match_clause_property_ids_single(
    match_clause_property_id: str,
) -> None:
    res = process_match_clause_property_ids(match_clause_property_id)

    assert len(res) == 1
    assert res[0].get("property_name") == "model"
    assert res[0].get("property_value") == "Odyssey"


def test_process_match_clause_property_ids_multiple(
    match_clause_property_ids: str,
) -> None:
    res = process_match_clause_property_ids(match_clause_property_ids)

    assert len(res) == 2


def test_process_match_clause_property_ids_bad_input() -> None:
    res = process_match_clause_property_ids("bad input!")

    assert len(res) == 0


def test_parse_labels_or_types_or() -> None:
    res = parse_labels_or_types("NodeA|NodeB")

    assert len(res) == 2
    assert res[0] == "NodeA"
    assert res[1] == "NodeB"


def test_parse_labels_or_types_and() -> None:
    res = parse_labels_or_types("NodeA&NodeB")

    assert len(res) == 2
    assert res[0] == "NodeA"
    assert res[1] == "NodeB"


def test_parse_labels_or_types_semicolon() -> None:
    res = parse_labels_or_types("NodeA:NodeB")

    assert len(res) == 2
    assert res[0] == "NodeA"
    assert res[1] == "NodeB"


def test_parse_labels_or_types_and_length_4() -> None:
    res = parse_labels_or_types("NodeA&NodeB&NodeC&NodeD")

    assert len(res) == 4
    assert res[0] == "NodeA"
    assert res[1] == "NodeB"
    assert res[2] == "NodeC"
    assert res[3] == "NodeD"


def test_parse_labels_or_types_exclamation() -> None:
    res = parse_labels_or_types("NodeA:!NodeB")

    assert len(res) == 1
    assert res[0] == "NodeA"


def test_parse_labels_or_types_single() -> None:
    res = parse_labels_or_types("NodeA")

    assert len(res) == 1
    assert res[0] == "NodeA"


def test_parse_labels_or_types_single_exclamation() -> None:
    res = parse_labels_or_types("!NodeA")

    assert len(res) == 0
