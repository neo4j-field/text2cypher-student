from ps_genai_agents.components.text2cypher.validation.models import (
    CypherValidationTask,
)
from ps_genai_agents.components.text2cypher.validation.utils.cypher_extractors import (
    _extract_nodes_and_properties_from_cypher_statement,
    _extract_relationships_and_properties_from_cypher_statement,
    # parse_labels_or_types,
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


def test_parse_labels_or_types_or(nodes_task_or: CypherValidationTask) -> None:
    res = nodes_task_or.parsed_labels_or_types

    assert len(res) == 2
    assert res[0] == "NodeA"
    assert res[1] == "NodeB"


def test_parse_labels_or_types_and(nodes_task_and: CypherValidationTask) -> None:
    res = nodes_task_and.parsed_labels_or_types

    assert len(res) == 2
    assert res[0] == "NodeA"
    assert res[1] == "NodeB"


def test_parse_labels_or_types_colon(nodes_task_colon: CypherValidationTask) -> None:
    res = nodes_task_colon.parsed_labels_or_types

    assert len(res) == 2
    assert res[0] == "NodeA"
    assert res[1] == "NodeB"


def test_parse_labels_or_types_and_length_4(
    nodes_task_and_many: CypherValidationTask,
) -> None:
    res = nodes_task_and_many.parsed_labels_or_types

    assert len(res) == 4
    assert res[0] == "NodeA"
    assert res[1] == "NodeB"
    assert res[2] == "NodeC"
    assert res[3] == "NodeD"


def test_parse_labels_or_types_exclamation(
    nodes_task_colon_not: CypherValidationTask,
) -> None:
    res = nodes_task_colon_not.parsed_labels_or_types

    assert len(res) == 1
    assert res[0] == "NodeA"


def test_parse_labels_or_types_single(
    nodes_task_standard: CypherValidationTask,
) -> None:
    res = nodes_task_standard.parsed_labels_or_types

    assert len(res) == 1
    assert res[0] == "NodeA"


def test_parse_labels_or_types_single_exclamation(
    nodes_task_not: CypherValidationTask,
) -> None:
    res = nodes_task_not.parsed_labels_or_types

    assert len(res) == 0


def test_extract_nodes_and_properties_from_cypher_statement_1(
    cypher_statement_1: str,
) -> None:
    ents = _extract_nodes_and_properties_from_cypher_statement(cypher_statement_1)

    answer = [
        {"labels": None, "property_name": "id", "property_value": "001"},
    ]

    assert len(ents) == len(answer)
    assert ents[0].property_name == "id"
    assert ents[0].property_value == "001"


def test_extract_relationships_and_properties_from_cypher_statement_1(
    cypher_statement_1: str,
) -> None:
    ents = _extract_relationships_and_properties_from_cypher_statement(
        cypher_statement_1
    )

    answer = [
        {"rel_types": "RELATIONSHIP", "property_name": "id", "property_value": "1"}
    ]

    assert len(ents) == len(answer)
    assert ents[0].labels_or_types == "RELATIONSHIP"
    assert ents[0].property_name == "id"
    assert ents[0].property_value == "1"
