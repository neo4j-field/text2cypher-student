"""
This file contains Cypher validators that may be used in the Text2Cypher validation node.
"""

from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union

from langchain_core.runnables.base import Runnable
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema
from neo4j.exceptions import CypherSyntaxError

from ....components.text2cypher.validation.models import ValidateCypherOutput
from .utils.cypher_extractors import (
    extract_entities_for_validation,
    parse_labels_or_types,
)
from .utils.enums import (
    create_node_properties_enum,
    create_node_property_values_enum,
    create_relationship_properties_enum,
    create_relationship_property_values_enum,
)
from .utils.ranges import (
    create_node_property_values_range,
    create_relationship_property_values_range,
)
from .utils.utils import update_task_list_with_property_type


def validate_cypher_query_syntax(
    graph: Neo4jGraph, cypher_statement: str
) -> Optional[str]:
    """
    Validate the Cypher statement syntax by running an EXPLAIN query.

    Parameters
    ----------
    graph : Neo4jGraph
        The Neo4j graph wrapper.
    cypher_statement : str
        The Cypher statement to validate.

    Returns
    -------
    Optional[str]
        If the statement contains invalid syntax, return an error message, else return None
    """
    try:
        graph.query(f"EXPLAIN {cypher_statement}")
    except CypherSyntaxError as e:
        return str(e.message)
    return None


def correct_cypher_query_relationship_direction(
    graph: Neo4jGraph, cypher_statement: str
) -> str:
    """
    Correct Relationship directions in the Cypher statement with LangChain's `CypherQueryCorrector`.

    Parameters
    ----------
    graph : Neo4jGraph
        The Neo4j graph wrapper.
    cypher_statement : str
        The Cypher statement to validate.

    Returns
    -------
    str
        The Cypher statement with corrected Relationship directions.
    """
    # Cypher query corrector is experimental
    corrector_schema = [
        Schema(el["start"], el["type"], el["end"])
        for el in graph.structured_schema.get("relationships", list())
    ]
    cypher_query_corrector = CypherQueryCorrector(corrector_schema)

    corrected_cypher: str = cypher_query_corrector(cypher_statement)

    return corrected_cypher


def validate_cypher_query_with_llm(
    validate_cypher_chain: Runnable[Dict[str, Any], Any],
    question: str,
    graph: Neo4jGraph,
    cypher_statement: str,
) -> Dict[str, List[str]]:
    """
    Validate the Cypher statement with an LLM.
    Use declared LLM to find Node and Property pairs to validate.
    Validate Node and Property pairs against the Neo4j graph.

    Parameters
    ----------
    validate_cypher_chain : RunnableSerializable
        The LangChain LLM to perform processing.
    question : str
        The question associated with the Cypher statement.
    graph : Neo4jGraph
        The Neo4j graph wrapper.
    cypher_statement : str
        The Cypher statement to validate.

    Returns
    -------
    Dict[str, List[str]]
        A Python dictionary with keys `errors` and `mapping_errors`, each with a list of found errors.
    """

    errors: List[str] = []
    mapping_errors: List[str] = []

    llm_output: ValidateCypherOutput = validate_cypher_chain.invoke(
        {
            "question": question,
            "schema": graph.schema,
            "cypher": cypher_statement,
        }
    )
    if llm_output.errors:
        errors.extend(llm_output.errors)
    if llm_output.filters:
        for filter in llm_output.filters:
            # Do mapping only for string values
            if (
                not [
                    prop
                    for prop in graph.structured_schema["node_props"][filter.node_label]
                    if prop["property"] == filter.property_key
                ][0]["type"]
                == "STRING"
            ):
                continue
            mapping = graph.query(
                f"MATCH (n:{filter.node_label}) WHERE toLower(n.`{filter.property_key}`) = toLower($value) RETURN 'yes' LIMIT 1",
                {"value": filter.property_value},
            )
            if not mapping:
                mapping_error = f"Missing value mapping for {filter.node_label} on property {filter.property_key} with value {filter.property_value}"
                mapping_errors.append(mapping_error)
    return {"errors": errors, "mapping_errors": mapping_errors}


def validate_cypher_query_with_schema(
    graph: Neo4jGraph, cypher_statement: str
) -> Dict[str, List[str]]:
    schema = graph.get_structured_schema
    nodes_and_rels = extract_entities_for_validation(cypher_statement=cypher_statement)

    node_tasks = update_task_list_with_property_type(
        nodes_and_rels.get("nodes", list()), schema, "node"
    )
    rel_tasks = update_task_list_with_property_type(
        nodes_and_rels.get("relationships", list()), schema, "rel"
    )

    errors: List[str] = list()

    # print("\n\n", node_tasks, "\n\n", rel_tasks, "\n\n")
    node_prop_name_enum_tasks = node_tasks
    node_prop_val_enum_tasks = [
        n for n in node_tasks if n.get("property_type") == "STRING"
    ]
    node_prop_val_range_tasks = [
        n
        for n in node_tasks
        if (n.get("property_type") == "INTEGER" or n.get("property_type") == "FLOAT")
    ]

    rel_prop_name_enum_tasks = rel_tasks
    rel_prop_val_enum_tasks = [
        n for n in rel_tasks if n.get("property_type") == "STRING"
    ]
    rel_prop_val_range_tasks = [
        n
        for n in rel_tasks
        if (n.get("property_type") == "INTEGER" or n.get("property_type") == "FLOAT")
    ]

    errors.extend(
        validate_node_property_names_with_enum(schema, node_prop_name_enum_tasks)
    )
    errors.extend(
        validate_node_property_values_with_enum(schema, node_prop_val_enum_tasks)
    )
    errors.extend(
        validate_node_property_values_with_range(schema, node_prop_val_range_tasks)
    )

    errors.extend(
        validate_relationship_property_names_with_enum(schema, rel_prop_name_enum_tasks)
    )
    errors.extend(
        validate_relationship_property_values_with_enum(schema, rel_prop_val_enum_tasks)
    )
    errors.extend(
        validate_relationship_property_values_with_range(
            schema, rel_prop_val_range_tasks
        )
    )

    return {"errors": errors, "mapping_errors": []}


def validate_node_property_values_with_enum(
    structure_graph_schema: Dict[str, Any], tasks: List[Dict[str, str]]
) -> List[str]:
    prop_values_enum = create_node_property_values_enum(structure_graph_schema)

    errors = list()

    for t in tasks:
        labels = parse_labels_or_types(t.get("labels", ""))

        prop_val_validation_error = validate_property_value_with_enum(
            enum_dict=prop_values_enum,
            labels_or_types=labels,
            node_or_rel="Node",
            property_name=t.get("property_name", ""),
            property_value=t.get("property_value", ""),
        )
        if prop_val_validation_error:
            errors.append(prop_val_validation_error)

    return errors


def validate_node_property_names_with_enum(
    structure_graph_schema: Dict[str, Any], tasks: List[Dict[str, str]]
) -> List[str]:
    prop_enum = create_node_properties_enum(structure_graph_schema)

    errors = list()

    for t in tasks:
        labels = parse_labels_or_types(t.get("labels", ""))

        prop_validation_error = validate_property_with_enum(
            enum_dict=prop_enum,
            labels_or_types=labels,
            node_or_rel="Node",
            property_name=t.get("property_name", ""),
        )

        if prop_validation_error:
            errors.append(prop_validation_error)
    return errors


def validate_relationship_property_names_with_enum(
    structure_graph_schema: Dict[str, Any], tasks: List[Dict[str, str]]
) -> List[str]:
    prop_enum = create_relationship_properties_enum(structure_graph_schema)

    errors = list()

    for t in tasks:
        rel_types = parse_labels_or_types(t.get("rel_types", ""))

        prop_validation_error = validate_property_with_enum(
            enum_dict=prop_enum,
            labels_or_types=rel_types,
            node_or_rel="Relationship",
            property_name=t.get("property_name", ""),
        )

        if prop_validation_error:
            errors.append(prop_validation_error)
    return errors


def validate_relationship_property_values_with_enum(
    structure_graph_schema: Dict[str, Any], tasks: List[Dict[str, str]]
) -> List[str]:
    prop_values_enum = create_relationship_property_values_enum(structure_graph_schema)

    errors = list()

    for t in tasks:
        rel_types = parse_labels_or_types(t.get("rel_types", ""))
        prop_val_validation_error = validate_property_value_with_enum(
            enum_dict=prop_values_enum,
            labels_or_types=rel_types,
            node_or_rel="Relationship",
            property_name=t.get("property_name", ""),
            property_value=t.get("property_value", ""),
        )
        if prop_val_validation_error:
            errors.append(prop_val_validation_error)

    return errors


def validate_node_property_values_with_range(
    structure_graph_schema: Dict[str, Any],
    tasks: List[Dict[str, Union[str, int, float]]],
) -> List[str]:
    prop_values_range = create_node_property_values_range(structure_graph_schema)

    errors = list()

    for t in tasks:
        rel_types = parse_labels_or_types(t.get("rel_types", ""))
        prop_val_validation_error = validate_property_value_with_range(
            enum_dict=prop_values_range,
            labels_or_types=rel_types,
            node_or_rel="Node",
            property_name=str(t.get("property_name", "")),
            property_value=float(t.get("property_value", float("inf"))),
        )
        if prop_val_validation_error:
            errors.append(prop_val_validation_error)

    return errors


def validate_relationship_property_values_with_range(
    structure_graph_schema: Dict[str, Any],
    tasks: List[Dict[str, Union[str, int, float]]],
) -> List[str]:
    prop_values_range = create_relationship_property_values_range(
        structure_graph_schema
    )

    errors = list()

    for t in tasks:
        rel_types = parse_labels_or_types(t.get("rel_types", ""))
        prop_val_validation_error = validate_property_value_with_range(
            enum_dict=prop_values_range,
            labels_or_types=rel_types,
            node_or_rel="Relationship",
            property_name=str(t.get("property_name", "")),
            property_value=float(t.get("property_value", float("inf"))),
        )
        if prop_val_validation_error:
            errors.append(prop_val_validation_error)

    return errors


def validate_property_value_with_enum(
    enum_dict: Dict[str, Dict[str, Set[str]]],
    labels_or_types: List[str],
    property_name: str,
    node_or_rel: str,
    property_value: str,
    and_or: Optional[Literal["and", "or"]] = None,
) -> Optional[str]:
    """Validate that a property value is found in the enum generated from the graph schema."""

    assert node_or_rel in {
        "Node",
        "Relationship",
    }, f"Invalid `node_or_rel`: {node_or_rel}"

    if and_or is None and len(labels_or_types) > 1:
        raise ValueError(
            f"Invalid combination of `labels_or_types` and `and_or`: {labels_or_types} | {and_or}"
        )

    # track labels or types that are invalid
    # compare the number of invalid to the number tested to determine to determine if valid
    invalid_labels_or_types = list()

    for lt in labels_or_types:
        props = enum_dict.get(lt)
        if props is None:
            return None
        enum = props.get(property_name)
        if enum is None:
            return None
        if property_value not in enum:
            invalid_labels_or_types.append(lt)

    if and_or is None and len(invalid_labels_or_types) > 0:  # single label or type
        return f"{node_or_rel} {labels_or_types} with property {property_name} = {property_value} not found in graph database."
    elif (
        and_or == "and"
        and 0 < len(invalid_labels_or_types)
        and len(invalid_labels_or_types) <= len(labels_or_types)
    ):
        return f"{node_or_rel}(s) {invalid_labels_or_types} with property {property_name} = {property_value} not found in graph database."
    elif and_or == "or" and len(invalid_labels_or_types) == len(labels_or_types):
        return f"None of {node_or_rel}s {labels_or_types} have property {property_name} = {property_value} in graph database."

    else:
        return None


def validate_property_value_with_range(
    enum_dict: Dict[str, Dict[str, Tuple[Union[int, float], Union[int, float]]]],
    labels_or_types: str,
    property_name: str,
    node_or_rel: Literal["Node", "Relationship"],
    property_value: Union[int, float],
    and_or: Optional[Literal["and", "or"]] = None,
) -> Optional[str]:
    """Validate that a property value is found within the range generated from the graph schema."""

    assert node_or_rel in {
        "Node",
        "Relationship",
    }, f"Invalid `node_or_rel`: {node_or_rel}"

    # track labels or types that are invalid
    # compare the number of invalid to the number tested to determine to determine if valid
    invalid_labels_or_types = list()

    for lt in labels_or_types:
        props = enum_dict.get(lt)
        if props is None:
            return None
        r: Tuple[Union[int, float], Union[int, float]] = props.get(
            property_name, (float("-inf"), float("inf"))
        )
        if r is None or len(r) != 2:
            return None
        if len(r) == 2 and (property_value <= r[0] or property_value >= r[1]):
            invalid_labels_or_types.append((lt, r))

    error_message_invalid_labels_or_types = list()
    for e in invalid_labels_or_types:
        error_message_invalid_labels_or_types.append(
            f"{e[0]} with range {e[1][0]} to {e[1][1]}"
        )

    if and_or is None and len(invalid_labels_or_types) > 0:  # single label or type
        return f"{node_or_rel} {labels_or_types} has property {property_name} = {property_value} which is out of range {r[0]} to {r[1]} in graph database."
    elif (
        and_or == "and"
        and 0 < len(invalid_labels_or_types)
        and len(invalid_labels_or_types) <= len(labels_or_types)
    ):
        return f"{node_or_rel}(s) {', '.join(error_message_invalid_labels_or_types)} have property {property_name} = {property_value} which is out of range in graph database."
    elif and_or == "or" and len(invalid_labels_or_types) == len(labels_or_types):
        return f"All of {node_or_rel}s {', '.join(error_message_invalid_labels_or_types)} have property {property_name} = {property_value} which is out of range in graph database."

    else:
        return None


def validate_property_with_enum(
    enum_dict: Dict[str, Dict[str, Set[str]]],
    labels_or_types: List[str],
    property_name: str,
    node_or_rel: Literal["Node", "Relationship"],
    and_or: Optional[Literal["and", "or"]] = None,
) -> Optional[str]:
    """Validate that a property name is found in the enum generated from the graph schema."""
    assert node_or_rel in {
        "Node",
        "Relationship",
    }, f"Invalid `node_or_rel`: {node_or_rel}"

    if and_or is None and len(labels_or_types) > 1:
        raise ValueError(
            f"Invalid combination of `labels_or_types` and `and_or`: {labels_or_types} | {and_or}"
        )

    # track labels or types that are invalid
    # compare the number of invalid to the number tested to determine to determine if valid
    invalid_labels_or_types = list()

    for lt in labels_or_types:
        enum = enum_dict.get(lt)

        if enum is None:
            return None
        if property_name not in enum:
            invalid_labels_or_types.append(lt)

    if and_or is None and len(invalid_labels_or_types) > 0:  # single label or type
        return f"{node_or_rel} {labels_or_types} does not have the property {property_name} in the graph database."
    elif (
        and_or == "and"
        and 0 < len(invalid_labels_or_types)
        and len(invalid_labels_or_types) <= len(labels_or_types)
    ):
        return f"{node_or_rel}(s) {invalid_labels_or_types} do(es) not have the property {property_name} in the graph database."
    elif and_or == "or" and len(invalid_labels_or_types) == len(labels_or_types):
        return f"None of {node_or_rel}s {labels_or_types} have the property {property_name} in the graph database."

    else:
        return None
