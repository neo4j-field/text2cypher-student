from typing import Any, Dict, List, Literal

from .cypher_extractors import parse_labels_or_types


def update_task_list_with_property_type(
    tasks: List[Dict[str, Any]],
    structure_graph_schema: Dict[str, Dict[str, List[Dict[str, Any]]]],
    node_or_rel: Literal["node", "rel"],
) -> List[Dict[str, Any]]:
    """Assign property types to each entry in the task list."""

    schema = structure_graph_schema.get(f"{node_or_rel}_props", dict())

    if node_or_rel == "node":
        label_or_type = "labels"
    else:
        label_or_type = "rel_types"

    for task in tasks:
        labels_or_types = parse_labels_or_types(task.get(label_or_type, None))
        found_types = set()

        for lt in labels_or_types:
            name_type_map = {
                d.get("property"): d.get("type") for d in schema.get(lt, dict())
            }
            found_types.add(name_type_map.get(task.get("property_name"), ""))

        if len(found_types) > 1:
            print(
                f"More than 1 type was found for {task.get(label_or_type, None)} and property {task.get("property_name")}"
            )
        elif not len(found_types):
            print(
                f"No type was found for {task.get(label_or_type, None)} and property {task.get("property_name")}"
            )

        if len(found_types) > 0:
            t = list(found_types)[0]
            task.update({"property_type": t})

    return tasks
