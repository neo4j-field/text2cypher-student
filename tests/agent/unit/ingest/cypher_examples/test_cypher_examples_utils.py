from typing import Dict, List

from agent.ingest.cypher_examples.utils import (
    remove_preexisting_nodes_from_ingest_tasks,
)


def test_remove_preexisting_nodes_from_ingest_tasks(
    unembedded_cypher_examples: List[Dict[str, str]],
) -> None:
    PREEXISTING_NUM = 3
    preexisting_nodes = {
        x.get("question", "") for x in unembedded_cypher_examples[:PREEXISTING_NUM]
    }  # 3 tasks

    assert len(preexisting_nodes) > 0

    result = remove_preexisting_nodes_from_ingest_tasks(
        unembedded_cypher_examples, preexisting_nodes
    )

    assert len(result) == len(unembedded_cypher_examples) - PREEXISTING_NUM
