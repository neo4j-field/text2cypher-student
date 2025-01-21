from typing import Any, Dict

from ps_genai_agents.components.text2cypher.validation.validators import (
    _extract_nodes_and_properties_from_cypher_statement,
    _extract_relationships_and_properties_from_cypher_statement,
    extract_entities_for_validation,
    validate_property_value_with_enum,
    validate_property_value_with_range,
    validate_property_with_enum,
)


def test_validate_node_properties_with_enum() -> None: ...


def test_validate_relationship_properties_with_enum() -> None: ...


def test_validate_node_properties_with_range() -> None: ...


def test_validate_relationship_properties_with_range() -> None: ...


def test_extract_entities_for_validation() -> None: ...


def test_extract_nodes_and_properties_from_cypher_statement_1(
    cypher_statement_1: str,
) -> None:
    ents = _extract_nodes_and_properties_from_cypher_statement(cypher_statement_1)

    answer = [
        {"labels": "Node"},
        {"labels": None, "property_name": "id", "property_value": "001"},
    ]

    no_labels = [x for x in answer if x.get("labels", "") is None]
    assert len(ents) == len(answer)
    assert no_labels[0].get("property_name") == "id"
    assert no_labels[0].get("property_value") == "001"


def test_extract_relationships_and_properties_from_cypher_statement_1(
    cypher_statement_1: str,
) -> None:
    ents = _extract_relationships_and_properties_from_cypher_statement(
        cypher_statement_1
    )

    answer = [
        {"rel_type": "RELATIONSHIP", "property_name": None, "property_value": None}
    ]

    assert len(ents) == len(answer)
    assert answer[0].get("rel_type") == "RELATIONSHIP"
    assert answer[0].get("property_name", "wrong") is None
    assert answer[0].get("property_value", "wrong") is None


def test_validate_property_value_with_enum_single_label_valid(
    node_property_values_enum_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA"]
    property_name = "prop_1"
    node_or_rel = "Node"
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
    node_or_rel = "Node"
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
    node_or_rel = "Node"
    property_value = "a"
    and_or = "and"

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
    node_or_rel = "Node"
    property_value = "d"
    and_or = "and"

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
    node_or_rel = "Node"
    property_value = "d"
    and_or = "or"

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
    node_or_rel = "Node"
    property_value = "g"
    and_or = "or"

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
    node_or_rel = "Node"

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
    node_or_rel = "Node"

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
    node_or_rel = "Node"
    and_or = "and"

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
    node_or_rel = "Node"
    and_or = "and"

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
    node_or_rel = "Node"
    and_or = "or"

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
    node_or_rel = "Node"
    and_or = "or"

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
    node_or_rel = "Node"

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
    node_or_rel = "Node"
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
        == f"{node_or_rel} {labels_or_types} has property {property_name} = {property_value} which is out of range {0} to {10} in graph database."
    )


def test_validate_property_value_with_range_multi_and_label_valid(
    node_property_values_range_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel = "Node"
    and_or = "and"
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
    node_property_values_range_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel = "Node"
    and_or = "and"
    property_value = 14

    res = validate_property_value_with_range(
        enum_dict=node_property_values_range_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
        property_value=property_value,
    )

    invalid_labels_or_types = ["NodeA with range 0 to 10"]

    assert res is not None
    assert (
        res
        == f"{node_or_rel}(s) {', '.join(invalid_labels_or_types)} have property {property_name} = {property_value} which is out of range in graph database."
    )


def test_validate_property_value_with_range_multi_or_label_valid(
    node_property_values_range_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel = "Node"
    and_or = "or"
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
    node_property_values_range_dict: Dict[str, Any],
) -> None:
    labels_or_types = ["NodeA", "NodeB"]
    property_name = "prop_1"
    node_or_rel = "Node"
    and_or = "or"
    property_value = 20

    res = validate_property_value_with_range(
        enum_dict=node_property_values_range_dict,
        labels_or_types=labels_or_types,
        property_name=property_name,
        node_or_rel=node_or_rel,
        and_or=and_or,
        property_value=property_value,
    )

    invalid_labels_or_types = ["NodeA with range 0 to 10", "NodeB with range 0 to 15"]

    assert res is not None
    assert (
        res
        == f"All of {node_or_rel}s {', '.join(invalid_labels_or_types)} have property {property_name} = {property_value} which is out of range in graph database."
    )
