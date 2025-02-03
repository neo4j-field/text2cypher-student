from typing import Any, Dict, Literal

from ps_genai_agents.components.text2cypher.validation.models import (
    Neo4jStructuredSchemaPropertyNumber,
)
from ps_genai_agents.components.text2cypher.validation.validators import (
    validate_property_value_with_enum,
    validate_property_value_with_range,
    validate_property_with_enum,
)


def test_validate_node_properties_with_enum() -> None: ...


def test_validate_relationship_properties_with_enum() -> None: ...


def test_validate_node_properties_with_range() -> None: ...


def test_validate_relationship_properties_with_range() -> None: ...


def test_extract_entities_for_validation() -> None: ...


def test_validate_property_value_with_enum_single_label_valid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    property_value = "a"

    res = validate_property_value_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        property_value=property_value,
        node_or_rel=node_or_rel,
    )

    assert res is None


def test_validate_property_value_with_enum_single_label_invalid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    property_value = "f"

    res = validate_property_value_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        property_value=property_value,
        node_or_rel=node_or_rel,
    )

    assert res is not None
    assert (
        res
        == f"{node_or_rel} {labels_or_types} with property {property_name} = {property_value} not found in graph database."
    )


def test_validate_property_value_with_enum_multi_and_label_valid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    property_value = "a"
    and_or: Literal["and", "or"] = "and"

    res = validate_property_value_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        property_value=property_value,
        node_or_rel=node_or_rel,
        and_or=and_or,
    )

    assert res is None


def test_validate_property_value_with_enum_multi_and_label_invalid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    property_value = "d"
    and_or: Literal["and", "or"] = "and"

    res = validate_property_value_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        property_value=property_value,
        node_or_rel=node_or_rel,
        and_or=and_or,
    )

    assert res is not None
    assert (
        res
        == f"{node_or_rel}(s) ['NodeA'] with property {property_name} = {property_value} not found in graph database."
    )


def test_validate_property_value_with_enum_multi_or_label_valid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    property_value = "d"
    and_or: Literal["and", "or"] = "or"

    res = validate_property_value_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        property_value=property_value,
        node_or_rel=node_or_rel,
        and_or=and_or,
    )

    assert res is None


def test_validate_property_value_with_enum_multi_or_label_invalid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    property_value = "g"
    and_or: Literal["and", "or"] = "or"

    res = validate_property_value_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        property_value=property_value,
        node_or_rel=node_or_rel,
        and_or=and_or,
    )

    assert res is not None
    assert (
        res
        == f"None of {node_or_rel}s {labels_or_types} have property {property_name} = {property_value} in graph database."
    )


def test_validate_property_name_with_enum_single_label_valid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"

    res = validate_property_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
    )

    assert res is None


def test_validate_property_name_with_enum_single_label_invalid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA"]
    property_name = "prop_3"
    node_or_rel: Literal["Node", "Relationship"] = "Node"

    res = validate_property_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
    )

    assert res is not None
    assert (
        res
        == f"{node_or_rel} {labels_or_types} does not have the property {property_name} in the graph database."
    )


def test_validate_property_name_with_enum_multi_and_label_valid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    and_or: Literal["and", "or"] = "and"

    res = validate_property_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
    )

    assert res is None


def test_validate_property_name_with_enum_multi_and_label_invalid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_2"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    and_or: Literal["and", "or"] = "and"

    res = validate_property_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
    )

    assert res is not None
    assert (
        res
        == f"{node_or_rel}(s) ['NodeB'] do(es) not have the property {property_name} in the graph database."
    )


def test_validate_property_name_with_enum_multi_or_label_valid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_2"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    and_or: Literal["and", "or"] = "or"

    res = validate_property_with_enum(
        enum_dict=node_property_values_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
    )

    assert res is None


def test_validate_property_name_with_enum_multi_or_label_invalid(
    node_property_names_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_3"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    and_or: Literal["and", "or"] = "or"

    res = validate_property_with_enum(
        enum_dict=node_property_names_enum_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
    )

    assert res is not None
    assert (
        res
        == f"None of {node_or_rel}s {labels_or_types} have the property {property_name} in the graph database."
    )


def test_validate_property_value_with_range_single_label_valid(
    node_property_values_range_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"

    res = validate_property_value_with_range(
        enum_dict=node_property_values_range_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        property_value=5,
    )

    assert res is None


def test_validate_property_value_with_range_single_label_invalid(
    node_property_values_range_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    property_value = 15

    res = validate_property_value_with_range(
        enum_dict=node_property_values_range_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        property_value=property_value,
    )

    assert res is not None
    assert (
        res
        == f"{node_or_rel} {labels_or_types[0]} has property {property_name} = {property_value} which is out of range 0.0 to 10.0 in graph database."
    )


def test_validate_property_value_with_range_multi_and_label_valid(
    node_property_values_range_dict: Dict[
        str, Dict[str, Neo4jStructuredSchemaPropertyNumber]
    ],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    and_or: Literal["and", "or"] = "and"
    property_value = 9

    res = validate_property_value_with_range(
        enum_dict=node_property_values_range_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
        property_value=property_value,
    )

    assert res is None


def test_validate_property_value_with_range_multi_and_label_invalid(
    node_property_values_range_dict: Dict[
        str, Dict[str, Neo4jStructuredSchemaPropertyNumber]
    ],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    and_or: Literal["and", "or"] = "and"
    property_value = 14

    res = validate_property_value_with_range(
        enum_dict=node_property_values_range_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
        property_value=property_value,
    )
    invalid_labels_or_types = ["NodeA with property prop_1 range 0.0 to 10.0"]

    assert res is not None
    assert (
        res
        == f"{node_or_rel}(s) {', '.join(invalid_labels_or_types)} have property {property_name} = {property_value} which is out of range in graph database."
    )


def test_validate_property_value_with_range_multi_or_label_valid(
    node_property_values_range_dict: Dict[
        str, Dict[str, Neo4jStructuredSchemaPropertyNumber]
    ],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    and_or: Literal["and", "or"] = "or"
    property_value = 13

    res = validate_property_value_with_range(
        enum_dict=node_property_values_range_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
        property_value=property_value,
    )

    assert res is None


def test_validate_property_value_with_range_multi_or_label_invalid(
    node_property_values_range_dict: Dict[
        str, Dict[str, Neo4jStructuredSchemaPropertyNumber]
    ],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel: Literal["Node", "Relationship"] = "Node"
    and_or: Literal["and", "or"] = "or"
    property_value = 20

    res = validate_property_value_with_range(
        enum_dict=node_property_values_range_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
        property_value=property_value,
    )

    invalid_labels_or_types = [
        "NodeA with property prop_1 range 0.0 to 10.0",
        "NodeB with property prop_1 range 0.0 to 15.0",
    ]

    assert res is not None
    assert (
        res
        == f"All of {node_or_rel}s {', '.join(invalid_labels_or_types)} have property {property_name} = {property_value} which is out of range in graph database."
    )
