from typing import Any, Dict, List, Union

import regex as re

from .regex_patterns import (
    get_node_label_pattern,
    get_node_pattern,
    get_node_variable_pattern,
    get_property_pattern,
    get_relationship_pattern,
    get_relationship_type_pattern,
    get_relationship_variable_pattern,
    get_variable_operator_property_pattern,
)


def extract_entities_for_validation(
    cypher_statement: str,
) -> Dict[str, List[Dict[str, Union[str, int, float]]]]:
    nodes = _extract_nodes_and_properties_from_cypher_statement(cypher_statement)
    rels = _extract_relationships_and_properties_from_cypher_statement(cypher_statement)

    return {"nodes": nodes, "relationships": rels}


def _extract_nodes_and_properties_from_cypher_statement(
    cypher_statement: str,
) -> List[Dict[str, Any]]:
    """
    Extract Node and Property pairs from the Cypher statement.

    Parameters
    ----------
    cypher_statement : str
        The statement.

    Returns
    -------
    List[Dict[str, Any]]
        A List of Python dictionaries with keys `labels`, `operator`, `property_name` and `property_value`.
    """
    result = list()

    nodes = re.findall(get_node_pattern(), cypher_statement)

    # find all variable assignments and process match clauses
    for n in nodes:
        variables = re.findall(get_node_variable_pattern(), n)
        labels = re.findall(get_node_label_pattern(), n)
        k = variables[0] if len(variables) > 0 else None
        label = labels[0] if len(labels) > 0 else None

        match_props = re.findall(get_property_pattern(), n)
        match_props = match_props[0] if len(match_props) > 0 else None

        # process ids in the MATCH clause
        if match_props is not None:
            match_props_parsed: List[Dict[str, Any]] = (
                process_match_clause_property_ids(match_props)
            )
            [e.update({"labels": label, "operator": "="}) for e in match_props_parsed]
            result.extend(match_props_parsed)
        else:
            result.extend([{"labels": label}])

        # find and process property filters based on variables
        if k is not None:
            filters: List[Dict[str, Any]] = re.findall(
                get_variable_operator_property_pattern(variable=k), cypher_statement
            )
            [e.update({"labels": label}) for e in filters]
            result.extend(filters)

    return result


def _extract_relationships_and_properties_from_cypher_statement(
    cypher_statement: str,
) -> List[Dict[str, Any]]:
    """
    Extract Relationship and Property pairs from the Cypher statement.

    Parameters
    ----------
    cypher_statement : str
        The statement.

    Returns
    -------
    List[Dict[str, Any]]
        A List of Python dictionaries with keys `rel_types`, `operator`, `property_name` and `property_value`.
    """
    result = list()

    rels = re.findall(get_relationship_pattern(), cypher_statement)

    # find all variable assignments and process match clauses
    for n in rels:
        variables = re.findall(get_relationship_variable_pattern(), n)
        rel_type = re.findall(get_relationship_type_pattern(), n)
        rel_type = rel_type[0] if len(rel_type) > 0 else None
        k = variables[0] if len(variables) > 0 else None

        match_props = re.findall(get_property_pattern(), n)
        match_props = match_props[0] if len(match_props) > 0 else None

        # process ids in the MATCH clause
        if match_props is not None:
            match_props_parsed: List[Dict[str, Any]] = (
                process_match_clause_property_ids(match_props)
            )
            [
                e.update({"rel_type": rel_type, "operator": "="})
                for e in match_props_parsed
            ]
            result.extend(match_props_parsed)
        else:
            result.extend([{"rel_type": rel_type}])

        # find and process property filters based on variables
        if k is not None:
            filters: List[Dict[str, Any]] = re.findall(
                get_variable_operator_property_pattern(variable=k), cypher_statement
            )
            [e.update({"rel_type": rel_type}) for e in filters]
            result.extend(filters)

    return result


def process_match_clause_property_ids(
    match_clause_section: str,
) -> List[Dict[str, Any]]:
    parts = match_clause_section.split(",")
    result = list()
    for part in parts:
        k_and_v = part.split(":")
        if len(k_and_v) == 2:
            k, v = k_and_v
        else:
            continue
        result.append(
            {
                "property_name": _process_prop_key(k),
                "property_value": _process_prop_val(v),
            }
        )
    return result


def _process_prop_key(prop: str) -> str:
    prop = prop.strip()
    return prop.strip("{")


def _process_prop_val(prop: str) -> str:
    prop = prop.strip()
    prop = prop.strip("}")
    return prop.replace('"', "")


def parse_labels_or_types(labels_str: str) -> List[str]:
    """Parse labels or types in cases with & / | and !."""

    if "&" in labels_str:
        labels = [l.strip() for l in labels_str.split("&")]
    elif "|" in labels_str:
        labels = [l.strip() for l in labels_str.split("|")]
    elif ":" in labels_str:
        labels = [l.strip() for l in labels_str.split(":")]
    else:
        labels = [labels_str]

    labels = [l for l in labels if not l.startswith("!")]

    return labels
