"""
This file contains Cypher validators that may be used in the Text2Cypher validation node.
"""

from typing import Dict, List, Optional, Union

from langchain_core.runnables.base import RunnableSerializable
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema
from neo4j.exceptions import CypherSyntaxError

from ....components.text2cypher.validation.models import ValidateCypherOutput


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


def validate_cypher_query_relationship_direction(
    graph: Neo4jGraph, cypher_statement: str
) -> str:
    """
    Validate Relationship directions in the Cypher statement with LangChain's `CypherQueryCorrector`.

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
        for el in graph.structured_schema.get("relationships")
    ]
    cypher_query_corrector = CypherQueryCorrector(corrector_schema)

    corrected_cypher: str = cypher_query_corrector(cypher_statement)

    return corrected_cypher


def validate_cypher_query_with_llm(
    validate_cypher_chain: RunnableSerializable,
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
    print(llm_output)
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
                print(mapping_error)
                mapping_errors.append(mapping_error)
    return {"errors": errors, "mapping_errors": mapping_errors}


def validate_node_property_with_enum(
    graph: Neo4jGraph, node_label: str, property_name: str, property_value: str
) -> str:
    return ""


def validate_relationship_property_with_enum(
    graph: Neo4jGraph, relationship_type: str, property_name: str, property_value: str
) -> str:
    return ""


def validate_node_property_with_range(
    graph: Neo4jGraph,
    node_label: str,
    property_name: str,
    property_value: Union[int, float],
) -> str:
    return ""


def validate_relationship_property_with_range(
    graph: Neo4jGraph,
    node_label: str,
    property_name: str,
    property_value: Union[int, float],
) -> str:
    return ""


def extract_entities_for_validation(
    cypher_statement: str, graph: Neo4jGraph
) -> Dict[str, Dict[str, Union[str, int, float]]]:
    return {"": {"": ""}}
