from typing import Any, Dict, List

from ps_genai_agents.components.text2cypher.validation.utils.utils import (
    update_task_list_with_property_type,
)


def test_update_task_list_with_property_type_nodes(
    utils_structured_graph_schema: Dict[str, Dict[str, List[Dict[str, Any]]]],
    utils_node_tasks: List[Dict[str, Any]],
) -> None:
    result = update_task_list_with_property_type(
        tasks=utils_node_tasks,
        structure_graph_schema=utils_structured_graph_schema,
        node_or_rel="node",
    )

    assert result[0].get("labels") == "NodeA"
    assert result[1].get("labels") == "NodeA"
    assert result[2].get("labels") == "NodeA&NodeB"
    assert result[0].get("property_type") == "STRING"
    assert result[1].get("property_type") == "INTEGER"
    assert result[2].get("property_type") == "STRING"


def test_update_task_list_with_property_type_rels(
    utils_structured_graph_schema: Dict[str, Dict[str, List[Dict[str, Any]]]],
    utils_rel_tasks: List[Dict[str, Any]],
) -> None:
    result = update_task_list_with_property_type(
        tasks=utils_rel_tasks,
        structure_graph_schema=utils_structured_graph_schema,
        node_or_rel="rel",
    )

    assert len(result) == 1
    assert result[0].get("rel_types") == "REL_A"
    assert result[0].get("property_type") == "STRING"
