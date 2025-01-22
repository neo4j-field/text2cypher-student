from ps_genai_agents.components.text2cypher.validation.utils.cypher_extractors import (
    _extract_nodes_and_properties_from_cypher_statement,
    _extract_relationships_and_properties_from_cypher_statement,
)


def test_extract_nodes_and_properties_from_cypher_statement_valid(
    cypher_statement_1_valid: str,
) -> None:
    res = _extract_nodes_and_properties_from_cypher_statement(cypher_statement_1_valid)
    assert len(res) == 5


def test_extract_relationships_and_properties_from_cypher_statement_valid(
    cypher_statement_1_valid: str,
) -> None:
    res = _extract_relationships_and_properties_from_cypher_statement(
        cypher_statement_1_valid
    )
    assert len(res) == 1


def test_extract_nodes_and_properties_from_cypher_statement_invalid(
    cypher_statement_1_invalid: str,
) -> None:
    res = _extract_nodes_and_properties_from_cypher_statement(
        cypher_statement_1_invalid
    )
    assert len(res) == 5


def test_extract_relationships_and_properties_from_cypher_statement_invalid(
    cypher_statement_1_invalid: str,
) -> None:
    res = _extract_relationships_and_properties_from_cypher_statement(
        cypher_statement_1_invalid
    )
    assert len(res) == 2


def test_extract_nodes_and_properties_from_cypher_statement_iqs_valid(
    cypher_statement_iqs_valid: str,
) -> None:
    res = _extract_nodes_and_properties_from_cypher_statement(
        cypher_statement_iqs_valid
    )
    print(res)
    assert len(res) == 5


def test_extract_relationships_and_properties_from_cypher_statement_iqs_valid(
    cypher_statement_iqs_valid: str,
) -> None:
    res = _extract_relationships_and_properties_from_cypher_statement(
        cypher_statement_iqs_valid
    )
    assert len(res) == 0
