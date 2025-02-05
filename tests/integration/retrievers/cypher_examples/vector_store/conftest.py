from unittest.mock import MagicMock

import pytest
from neo4j import Driver

from ps_genai_agents.embeddings import EmbedderProtocol
from ps_genai_agents.retrievers.cypher_examples.vector_store import (
    Neo4jVectorSearchCypherExampleRetriever,
)


@pytest.fixture(scope="function")
def neo4j_vector_search_cypher_example_retriever(
    neo4j_driver: Driver, mock_embedder: MagicMock
) -> Neo4jVectorSearchCypherExampleRetriever:
    r = Neo4jVectorSearchCypherExampleRetriever(
        neo4j_driver=neo4j_driver,
        vector_index_name="test_vector_index",
        embedder=mock_embedder,
    )
    return r


@pytest.fixture(scope="function")
def mock_embedder() -> MagicMock:
    m = MagicMock(spec=EmbedderProtocol)

    m.embed_query.return_value = [0.1, 0.2, 0.3]

    return m


@pytest.fixture(scope="function")
def write_cypher_example_nodes(neo4j_driver: Driver, clean_database: None) -> None:
    with neo4j_driver.session() as session:
        session.run(
            """
unwind ["a", "b", "c"] as question
MERGE (n:CypherQuery {question: question})
SET
    n.cypherStatement = "match n return n",
    n.embeddingModel = 'test-model'
WITH n
CALL db.create.setNodeVectorProperty(n, 'questionEmbedding', [0.123, 0.456, 0.789])
"""
        )
