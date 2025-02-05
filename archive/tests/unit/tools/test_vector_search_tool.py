from typing import Callable
from unittest.mock import MagicMock

import pytest
from src.ps_genai_agents.tools.vector_search import create_neo4j_vector_search_tool


def test_create_vector_search_tool(
    mock_driver: MagicMock, mock_embedder: MagicMock
) -> None:
    vs = create_neo4j_vector_search_tool(
        driver=mock_driver, embedder=mock_embedder, index_name="vector_index"
    )

    assert isinstance(vs, Callable)
