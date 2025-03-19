from typing import Dict, List
from unittest.mock import MagicMock

import pytest

from ps_genai_agents.embeddings import EmbedderProtocol


@pytest.fixture(scope="function")
def unembedded_cypher_examples() -> List[Dict[str, str]]:
    nodes = [
        "NodeA",
        "NodeB",
        "NodeC",
        "NodeD",
        "NodeE",
        "NodeF",
        "NodeG",
        "NodeH",
        "NodeI",
        "NodeJ",
    ]
    return [
        {"question": f"question {node}", "cql": f"match (n:{node}) return n"}
        for node in nodes
    ]


@pytest.fixture(scope="function")
def unembedded_cypher_examples_for_init(
    unembedded_cypher_examples: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """return 3 node tasks to be loaded to simulate an already existing Cypher query vector store."""
    return unembedded_cypher_examples[:3]


@pytest.fixture(scope="function")
def mock_embedder() -> MagicMock:
    m = MagicMock(spec=EmbedderProtocol)

    m.embed_query.return_value = [0.1, 0.2, 0.3]

    return m
