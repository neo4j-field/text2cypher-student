from typing import Dict, List
from unittest.mock import MagicMock

import pytest

from ps_genai_agents.embeddings import EmbedderProtocol
from ps_genai_agents.ingest.cypher_examples.models import CypherIngestRecord


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
def embedded_cypher_examples(
    unembedded_cypher_examples: List[Dict[str, str]],
) -> List[CypherIngestRecord]:
    return [
        CypherIngestRecord(
            cypher_statement=node.get("cypher_statement", ""),
            question=node.get("question", ""),
            question_embedding=[0.1, 0.2, 0.3],
            embedding_model="test-model",
        )
        for node in unembedded_cypher_examples
    ]


@pytest.fixture(scope="function")
def mock_embedder() -> MagicMock:
    m = MagicMock(spec=EmbedderProtocol)

    m.embed_query.return_value = [0.1, 0.2, 0.3]

    return m
