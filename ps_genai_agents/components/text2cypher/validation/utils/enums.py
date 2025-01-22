from typing import Any, Dict, List, Set


def create_node_properties_enum(
    structure_graph_schema: Dict[str, Any],
) -> Dict[str, Set[str]]:
    nodes_dict = structure_graph_schema.get("node_props", dict())
    return _construct_properties_enum(nodes_dict)


def create_relationship_properties_enum(
    structure_graph_schema: Dict[str, Any],
) -> Dict[str, Set[str]]:
    rels_dict = structure_graph_schema.get("rel_props", dict())
    return _construct_properties_enum(rels_dict)


def create_node_property_values_enum(
    structure_graph_schema: Dict[str, Any],
) -> Dict[str, Dict[str, List[str]]]:
    nodes_dict = structure_graph_schema.get("node_props", dict())
    return _construct_property_values_enum(nodes_dict)


def create_relationship_property_values_enum(
    structure_graph_schema: Dict[str, Any],
) -> Dict[str, Dict[str, List[str]]]:
    rels_dict = structure_graph_schema.get("rel_props", dict())
    return _construct_property_values_enum(rels_dict)


def _construct_property_values_enum(
    nodes_or_rels_dict: Dict[str, Any],
) -> Dict[str, Dict[str, List[str]]]:
    result = dict()

    for label_or_type, props in nodes_or_rels_dict.items():
        sub_dict = dict()
        for prop in props:
            if prop.get("type", "") == "STRING" and len(
                prop.get("values", "")
            ) == prop.get("distinct_count"):
                sub_dict.update({prop.get("property", ""): prop.get("values", list())})
        result.update({label_or_type: sub_dict})

    return result


def _construct_properties_enum(
    nodes_or_rels_dict: Dict[str, Any],
) -> Dict[str, Set[str]]:
    return {
        k: {v.get("property") for v in lst} for k, lst in nodes_or_rels_dict.items()
    }
