from typing import Dict, List
from unittest.mock import MagicMock

from neo4j import Driver

from ps_genai_agents.ingest.cypher_examples.ingest_neo4j import (
    embed_cypher_query_nodes,
    get_existing_cypher_query_node_ids,
    load_cypher_query_nodes,
)
from ps_genai_agents.ingest.cypher_examples.models import CypherIngestRecord
from ps_genai_agents.ingest.cypher_examples.utils import (
    remove_preexisting_nodes_from_ingest_tasks,
)


def test_ingest_workflow_with_fresh_database(
    unembedded_cypher_examples: List[Dict[str, str]],
    mock_embedder: MagicMock,
    neo4j_driver: Driver,
    init_database: None,
    clean_database: None,
    healthcheck: None,
) -> None:
    embedder_results = embed_cypher_query_nodes(
        mock_embedder, unembedded_cypher_examples
    )
    tasks = embedder_results.get("nodes")
    errors = embedder_results.get("failed")

    assert tasks is not None
    assert errors is not None
    assert len(tasks) == len(unembedded_cypher_examples)
    assert len(errors) == 0

    load_cypher_query_nodes(driver=neo4j_driver, nodes=tasks, database="neo4j")

    nodes_from_database = get_existing_cypher_query_node_ids(driver=neo4j_driver)

    assert len(nodes_from_database) == len(tasks)

    for task in tasks:
        assert task.question in nodes_from_database

    clean_database


def test_ingest_workflow_with_preexisting_nodes(
    unembedded_cypher_examples: List[Dict[str, str]],
    unembedded_cypher_examples_for_init: List[Dict[str, str]],
    mock_embedder: MagicMock,
    neo4j_driver: Driver,
    init_database: None,
    clean_database: None,
    healthcheck: None,
) -> None:
    # simulate preexisting nodes in database
    embedder_results = embed_cypher_query_nodes(
        mock_embedder, unembedded_cypher_examples_for_init
    )
    print("\n\nembedder results: ", embedder_results, "\n\n")
    init_tasks: List[CypherIngestRecord] = embedder_results.get("nodes", list())
    print("\n\ninit tasks: ", init_tasks, "\n\n")
    load_cypher_query_nodes(driver=neo4j_driver, nodes=init_tasks, database="neo4j")

    # test
    nodes_from_database = set(get_existing_cypher_query_node_ids(driver=neo4j_driver))

    assert len(nodes_from_database) == len(init_tasks)

    cleaned_tasks = remove_preexisting_nodes_from_ingest_tasks(
        ingest_tasks=unembedded_cypher_examples,
        existing_node_questions=nodes_from_database,
    )
    print("nodes from db: ", nodes_from_database)
    print("cleaned tasks: ", cleaned_tasks)
    assert len(cleaned_tasks) == len(unembedded_cypher_examples) - len(
        unembedded_cypher_examples_for_init
    )

    for task in cleaned_tasks:
        assert task.get("question", "") not in nodes_from_database

    clean_database
