from typing import Dict, List
from unittest.mock import MagicMock

from agent.ingest.cypher_examples.ingest_neo4j import (
    embed_cypher_query_nodes,
)
from agent.ingest.cypher_examples.models import CypherIngestRecord


def test_embed_cypher_query_nodes(
    unembedded_cypher_examples: List[Dict[str, str]], mock_embedder: MagicMock
) -> None:
    result = embed_cypher_query_nodes(mock_embedder, unembedded_cypher_examples)

    nodes = result.get("nodes")

    assert nodes is not None
    assert len(nodes) == len(unembedded_cypher_examples)
    assert isinstance(nodes[0], CypherIngestRecord)
