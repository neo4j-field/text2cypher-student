from unittest.mock import MagicMock

from ps_genai_agents.components.utils.utils import (
    retrieve_and_parse_schema_from_graph_for_prompts,
)


def test_retrieve_and_parse_schema_from_graph_for_prompts_last_listed_node(
    graph_2: MagicMock, graph_schema_string_answer: str
) -> None:
    res = retrieve_and_parse_schema_from_graph_for_prompts(graph_2)

    assert res == graph_schema_string_answer


def test_retrieve_and_parse_schema_from_graph_for_prompts_middle_listed_node(
    graph_1: MagicMock, graph_schema_string_answer: str
) -> None:
    res = retrieve_and_parse_schema_from_graph_for_prompts(graph_1)

    assert res == graph_schema_string_answer
