from typing import Any, Dict, Tuple, Union


def create_relationship_property_values_range(
    structure_graph_schema: Dict[str, Any],
) -> Dict[str, Dict[str, Tuple[Union[int, float], Union[int, float]]]]:
    rels_dict = structure_graph_schema.get("rel_props", dict())
    return _construct_property_values_range(rels_dict)


def create_node_property_values_range(
    structure_graph_schema: Dict[str, Any],
) -> Dict[str, Dict[str, Tuple[Union[int, float], Union[int, float]]]]:
    nodes_dict = structure_graph_schema.get("node_props", dict())
    return _construct_property_values_range(nodes_dict)


def _construct_property_values_range(
    nodes_or_rels_dict: Dict[str, Any],
) -> Dict[str, Dict[str, Tuple[Union[int, float], Union[int, float]]]]:
    result = dict()

    for label_or_type, props in nodes_or_rels_dict.items():
        sub_dict = dict()
        for prop in props:
            if prop.get("type", "") == "INTEGER" or prop.get("type", "") == "FLOAT":
                sub_dict.update(
                    {
                        prop.get("property", ""): (
                            prop.get("min", float("-inf")),
                            prop.get("max", float("inf")),
                        )
                    }
                )
        result.update({label_or_type: sub_dict})

    return result
