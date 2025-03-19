from neo4j import Driver

from agent.retrievers.cypher_examples.vector_store import (
    Neo4jVectorSearchCypherExampleRetriever,
)


def test_neo4j_cypher_example_retriever_empty_database(
    neo4j_driver: Driver,
    init_database: None,
    clean_database: None,
    healthcheck: None,
    neo4j_vector_search_cypher_example_retriever: Neo4jVectorSearchCypherExampleRetriever,
) -> None:
    result = neo4j_vector_search_cypher_example_retriever.get_examples(
        query="test query", k=1
    )

    assert len(result) == 0


def test_neo4j_cypher_example_retriever_hydrated_database(
    neo4j_driver: Driver,
    init_database: None,
    write_cypher_example_nodes: None,
    healthcheck: None,
    neo4j_vector_search_cypher_example_retriever: Neo4jVectorSearchCypherExampleRetriever,
) -> None:
    result = neo4j_vector_search_cypher_example_retriever.get_examples(
        query="test query", k=5
    )

    assert result.count("match n return n") == 3
    assert "Question: a" in result
    assert "Question: b" in result
    assert "Question: c" in result
