from ps_genai_agents.components.text2cypher.validation.utils.cypher_extractors import (
    _extract_nodes_and_properties_from_cypher_statement,
    _extract_relationships_and_properties_from_cypher_statement,
    parse_labels_or_types,
    process_match_clause_property_ids,
)


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


def test_extract_nodes_and_properties_from_cypher_statement_1(
    cypher_statement_1: str,
) -> None:
    ents = _extract_nodes_and_properties_from_cypher_statement(cypher_statement_1)

    answer = [
        {"labels": "Node"},
        {"labels": None, "property_name": "id", "property_value": "001"},
    ]

    no_labels = [x for x in answer if x.get("labels", "") is None]
    assert len(ents) == len(answer)
    assert no_labels[0].get("property_name") == "id"
    assert no_labels[0].get("property_value") == "001"


def test_extract_relationships_and_properties_from_cypher_statement_1(
    cypher_statement_1: str,
) -> None:
    ents = _extract_relationships_and_properties_from_cypher_statement(
        cypher_statement_1
    )

    answer = [
        {"rel_type": "RELATIONSHIP", "property_name": None, "property_value": None}
    ]

    assert len(ents) == len(answer)
    assert answer[0].get("rel_type") == "RELATIONSHIP"
    assert answer[0].get("property_name", "wrong") is None
    assert answer[0].get("property_value", "wrong") is None
