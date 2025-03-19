from unittest.mock import MagicMock

from ps_genai_agents.components.text2cypher.validation.validators import (
    validate_cypher_query_with_schema,
)


def test_validate_cypher_query_with_schema_1_valid(
    cypher_statement_1_valid: str, mock_graph_1: MagicMock
) -> None:
    errors = validate_cypher_query_with_schema(
        cypher_statement=cypher_statement_1_valid, graph=mock_graph_1
    )
    assert errors is not None
    assert len(errors) == 0


def test_validate_cypher_query_with_schema_1_invalid(
    cypher_statement_1_invalid: str, mock_graph_1: MagicMock
) -> None:
    errors = validate_cypher_query_with_schema(
        cypher_statement=cypher_statement_1_invalid, graph=mock_graph_1
    )
    assert errors is not None
    assert len(errors) == 4


def test_validate_cypher_query_with_schema_iqs_valid(
    cypher_statement_iqs_valid: str, mock_graph_iqs: MagicMock
) -> None:
    errors = validate_cypher_query_with_schema(
        cypher_statement=cypher_statement_iqs_valid, graph=mock_graph_iqs
    )
    assert errors is not None
    assert len(errors) == 0


def test_validate_cypher_query_with_schema_iqs_invalid(
    cypher_statement_iqs_invalid: str, mock_graph_iqs: MagicMock
) -> None:
    errors = validate_cypher_query_with_schema(
        cypher_statement=cypher_statement_iqs_invalid, graph=mock_graph_iqs
    )
    assert errors is not None
    assert len(errors) == 2
