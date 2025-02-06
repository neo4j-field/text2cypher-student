from typing import Any, Dict, List

from ps_genai_agents.components.text2cypher.validation.models import (
    CypherValidationTask,
    Neo4jStructuredSchema,
)
from ps_genai_agents.components.text2cypher.validation.utils.utils import (
    update_task_list_with_property_type,
)


def test_update_task_list_with_property_type_nodes(
    utils_structured_graph_schema: Dict[str, Dict[str, List[Dict[str, Any]]]],
    utils_node_tasks: List[CypherValidationTask],
) -> None:
    result = update_task_list_with_property_type(
        tasks=utils_node_tasks,
        structure_graph_schema=Neo4jStructuredSchema.model_validate(
            utils_structured_graph_schema
        ),
        node_or_rel="node",
    )

    assert result[0].labels_or_types == "NodeA"
    assert result[1].labels_or_types == "NodeA"
    assert result[2].labels_or_types == "NodeA&NodeB"
    assert result[0].property_type == "STRING"
    assert result[1].property_type == "INTEGER"
    assert result[2].property_type == "STRING"


def test_update_task_list_with_property_type_rels(
    utils_structured_graph_schema: Dict[str, Dict[str, List[Dict[str, Any]]]],
    utils_rel_tasks: List[CypherValidationTask],
) -> None:
    result = update_task_list_with_property_type(
        tasks=utils_rel_tasks,
        structure_graph_schema=Neo4jStructuredSchema.model_validate(
            utils_structured_graph_schema
        ),
        node_or_rel="rel",
    )

    assert len(result) == 1
    assert result[0].labels_or_types == "REL_A"
    assert result[0].property_type == "STRING"
