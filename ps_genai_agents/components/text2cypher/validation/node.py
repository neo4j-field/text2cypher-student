"""
This code is based on content found in the LangGraph documentation: https://python.langchain.com/docs/tutorials/graph/#advanced-implementation-with-langgraph
"""

from typing import Any, Callable, Dict

from langchain_core.language_models import BaseChatModel
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema
from neo4j.exceptions import CypherSyntaxError

from ....components.state import CypherState
from ....components.text2cypher.validation.models import ValidateCypherOutput
from ....components.text2cypher.validation.prompts import (
    create_text2cypher_validation_prompt_template,
)
from .validators import (
    correct_cypher_query_relationship_direction,
    validate_cypher_query_syntax,
    validate_cypher_query_with_llm,
)

validation_prompt_template = create_text2cypher_validation_prompt_template()


def create_text2cypher_validation_node(
    llm: BaseChatModel, graph: Neo4jGraph
) -> Callable[[CypherState], Dict[str, Any]]:
    """
    Create a Text2Cypher query validation node for a LangGraph workflow.

    Parameters
    ----------
    llm : BaseChatModel
        The LLM to use for processing.
    graph : Neo4jGraph
        The Neo4j graph wrapper.

    Returns
    -------
    Callable[[CypherState], CypherState]
        The LangGraph node.
    """

    validate_cypher_chain = validation_prompt_template | llm.with_structured_output(
        ValidateCypherOutput
    )

    # Cypher query corrector is experimental
    # corrector_schema = [
    #     Schema(el["start"], el["type"], el["end"])
    #     for el in graph.structured_schema.get("relationships")
    # ]
    # cypher_query_corrector = CypherQueryCorrector(corrector_schema)

    def validate_cypher(state: CypherState) -> Dict[str, Any]:
        """
        Validates the Cypher statements and maps any property values to the database.
        """
        errors = []
        mapping_errors = []
        # Check for syntax errors
        # try:
        #     graph.query(f"EXPLAIN {state.get('statement')}")
        # except CypherSyntaxError as e:
        #     errors.append(e.message)
        syntax_error = validate_cypher_query_syntax(
            graph=graph, cypher_statement=state.get("statement", "")
        )
        if syntax_error is not None:
            errors.append(syntax_error)

        # Experimental feature for correcting relationship directions
        # corrected_cypher = cypher_query_corrector(state.get("statement"))
        corrected_cypher = correct_cypher_query_relationship_direction(
            graph=graph, cypher_statement=state.get("statement", "")
        )

        if not corrected_cypher:
            errors.append("The generated Cypher statement doesn't fit the graph schema")
        if not corrected_cypher == state.get("statement"):
            print("Relationship direction was corrected")
        # Use LLM to find additional potential errors and get the mapping for values
        # llm_output = validate_cypher_chain.invoke(
        #     {
        #         "question": state.get("subquestion"),
        #         "schema": graph.schema,
        #         "cypher": state.get("statement"),
        #     }
        # )
        # print(llm_output)
        # if llm_output.errors:
        #     errors.extend(llm_output.errors)
        # if llm_output.filters:
        #     for filter in llm_output.filters:
        #         # Do mapping only for string values
        #         if (
        #             not [
        #                 prop
        #                 for prop in graph.structured_schema["node_props"][
        #                     filter.node_label
        #                 ]
        #                 if prop["property"] == filter.property_key
        #             ][0]["type"]
        #             == "STRING"
        #         ):
        #             continue
        #         mapping = graph.query(
        #             f"MATCH (n:{filter.node_label}) WHERE toLower(n.`{filter.property_key}`) = toLower($value) RETURN 'yes' LIMIT 1",
        #             {"value": filter.property_value},
        #         )
        #         if not mapping:
        #             print(
        #                 f"Missing value mapping for {filter.node_label} on property {filter.property_key} with value {filter.property_value}"
        #             )
        #             mapping_errors.append(
        #                 f"Missing value mapping for {filter.node_label} on property {filter.property_key} with value {filter.property_value}"
        #             )
        llm_errors = validate_cypher_query_with_llm(
            validate_cypher_chain=validate_cypher_chain,
            question=state.get("subquestion", ""),
            graph=graph,
            cypher_statement=state.get("statement", ""),
        )
        errors.extend(llm_errors.get("errors", []))
        mapping_errors.extend(llm_errors.get("mapping_errors", []))
        # if mapping_errors:
        #     next_action = "__end__"
        if errors or mapping_errors:
            next_action = "correct_cypher"
        else:
            next_action = "execute_cypher"
        return {
            "next_action_cypher": next_action,
            "statement": corrected_cypher,
            "errors": errors,
            "steps": ["validate_cypher"],
        }

    return validate_cypher
