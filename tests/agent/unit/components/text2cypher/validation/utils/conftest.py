from typing import Any, Dict, List

import pytest

from agent.components.text2cypher.validation.models import (
    CypherValidationTask,
)


@pytest.fixture(scope="function")
def utils_structured_graph_schema() -> Dict[str, Any]:
    return {
        "node_props": {
            "NodeA": [
                {"property": "prop_1", "type": "STRING", "values": ["a", "b"]},
                {"property": "prop_2", "type": "INTEGER", "min": 0, "max": 10},
            ],
            "NodeB": [
                {"property": "prop_1", "type": "STRING", "values": ["a", "b"]},
            ],
        },
        "rel_props": {
            "REL_A": [
                {"property": "prop_1", "type": "STRING", "values": ["a", "b"]},
            ]
        },
        "relationships": [{"start": "NodeA", "type": "REL_A", "end": "NodeB"}],
        "metadata": {},
    }


@pytest.fixture(scope="function")
def utils_node_tasks() -> List[CypherValidationTask]:
    return [
        CypherValidationTask.model_validate(
            {
                "labels_or_types": "NodeA",
                "property_name": "prop_1",
                "property_value": "a",
                "operator": "=",
            }
        ),
        CypherValidationTask.model_validate(
            {
                "labels_or_types": "NodeA",
                "property_name": "prop_2",
                "property_value": 10,
                "operator": "=",
            }
        ),
        CypherValidationTask.model_validate(
            {
                "labels_or_types": "NodeA&NodeB",
                "property_name": "prop_1",
                "property_value": "a",
                "operator": "=",
            }
        ),
    ]


@pytest.fixture(scope="function")
def utils_rel_tasks() -> List[CypherValidationTask]:
    return [
        CypherValidationTask.model_validate(
            {
                "labels_or_types": "REL_A",
                "property_name": "prop_1",
                "property_value": "a",
                "operator": "=",
            }
        )
    ]


@pytest.fixture(scope="function")
def nodes_task_or() -> CypherValidationTask:
    return CypherValidationTask(
        labels_or_types="NodeA|NodeB",
        operator="=",
        property_type="STRING",
        property_name="prop_1",
        property_value="1",
    )


@pytest.fixture(scope="function")
def nodes_task_and() -> CypherValidationTask:
    return CypherValidationTask(
        labels_or_types="NodeA&NodeB",
        operator="=",
        property_type="STRING",
        property_name="prop_1",
        property_value="1",
    )


@pytest.fixture(scope="function")
def nodes_task_and_many() -> CypherValidationTask:
    return CypherValidationTask(
        labels_or_types="NodeA&NodeB&NodeC&NodeD",
        operator="=",
        property_type="STRING",
        property_name="prop_1",
        property_value="1",
    )


@pytest.fixture(scope="function")
def nodes_task_colon() -> CypherValidationTask:
    return CypherValidationTask(
        labels_or_types="NodeA:NodeB",
        operator="=",
        property_type="STRING",
        property_name="prop_1",
        property_value="1",
    )


@pytest.fixture(scope="function")
def nodes_task_colon_not() -> CypherValidationTask:
    return CypherValidationTask(
        labels_or_types="NodeA:!NodeB",
        operator="=",
        property_type="STRING",
        property_name="prop_1",
        property_value="1",
    )


@pytest.fixture(scope="function")
def nodes_task_standard() -> CypherValidationTask:
    return CypherValidationTask(
        labels_or_types="NodeA",
        operator="=",
        property_type="STRING",
        property_name="prop_1",
        property_value="1",
    )


@pytest.fixture(scope="function")
def nodes_task_not() -> CypherValidationTask:
    return CypherValidationTask(
        labels_or_types="!NodeA",
        operator="=",
        property_type="STRING",
        property_name="prop_1",
        property_value="1",
    )
