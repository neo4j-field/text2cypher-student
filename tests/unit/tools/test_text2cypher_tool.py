from typing import Callable
from unittest.mock import MagicMock

import pytest

from src.ps_genai_agents.tools.text2cypher import create_neo4j_text2cypher_tool


def test_create_text2cypher_tool(mock_driver: MagicMock, mock_llm: MagicMock) -> None:
    t2c = create_neo4j_text2cypher_tool(
        llm=mock_llm, driver=mock_driver, custom_prompt="custom prompt"
    )

    assert isinstance(t2c, Callable)


def test_create_text2cypher_tool_no_prompt_args(
    mock_driver: MagicMock, mock_llm: MagicMock
) -> None:
    with pytest.raises(AssertionError):
        create_neo4j_text2cypher_tool(llm=mock_llm, driver=mock_driver)
