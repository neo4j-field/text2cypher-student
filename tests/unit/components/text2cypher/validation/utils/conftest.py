from typing import Any, Dict, List

import pytest


@pytest.fixture(scope="function")
def utils_structured_graph_schema() -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    return {
        "node_props": {
            "NodeA": [
                {"property": "prop_1", "type": "STRING"},
                {"property": "prop_2", "type": "INTEGER"},
            ],
            "NodeB": [
                {"property": "prop_1", "type": "STRING"},
            ],
        },
        "rel_props": {
            "REL_A": [
                {"property": "prop_1", "type": "STRING"},
            ]
        },
    }


@pytest.fixture(scope="function")
def utils_node_tasks() -> List[Dict[str, Any]]:
    return [
        {
            "labels": "NodeA",
            "property_name": "prop_1",
            "property_value": "a",
            "operator": "=",
        },
        {
            "labels": "NodeA",
            "property_name": "prop_2",
            "property_value": 10,
            "operator": "=",
        },
        {
            "labels": "NodeA&NodeB",
            "property_name": "prop_1",
            "property_value": "a",
            "operator": "=",
        },
    ]


@pytest.fixture(scope="function")
def utils_rel_tasks() -> List[Dict[str, Any]]:
    return [
        {
            "rel_types": "REL_A",
            "property_name": "prop_1",
            "property_value": "a",
            "operator": "=",
        }
    ]
