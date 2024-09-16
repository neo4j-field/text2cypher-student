from unittest.mock import MagicMock

import pytest
from neo4j import Driver
from neo4j_genai.embedder import Embedder
from neo4j_genai.llm import OpenAILLM


@pytest.fixture(scope="function")
def mock_driver() -> MagicMock:
    return MagicMock(spec=Driver)


@pytest.fixture(scope="function")
def mock_llm() -> MagicMock:
    return MagicMock(spec=OpenAILLM)


@pytest.fixture(scope="function")
def mock_embedder() -> MagicMock:
    return MagicMock(spec=Embedder)
