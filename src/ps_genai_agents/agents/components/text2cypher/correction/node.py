"""
This code is based on content found in the LangGraph documentation: https://python.langchain.com/docs/tutorials/graph/#advanced-implementation-with-langgraph
"""

from typing import Callable

from agents.components.state import CypherState
from agents.components.text2cypher.correction.prompts import (
    create_text2cypher_correction_prompt_template,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_neo4j import Neo4jGraph

correction_cypher_prompt = create_text2cypher_correction_prompt_template()


def create_text2cypher_correction_node(
    llm: BaseChatModel, graph: Neo4jGraph
) -> Callable[[CypherState], CypherState]:
    """
    Create a Text2Cypher query correction node for a LangGraph workflow.

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

    correct_cypher_chain = correction_cypher_prompt | llm | StrOutputParser()

    def correct_cypher(state: CypherState) -> CypherState:
        """
        Correct the Cypher statement based on the provided errors.
        """

        corrected_cypher = correct_cypher_chain.invoke(
            {
                "question": state.get("subquestion"),
                "errors": state.get("errors"),
                "cypher": state.get("statement"),
                "schema": graph.schema,
            }
        )

        return {
            "next_action": "validate_cypher",
            "statement": corrected_cypher,
            "steps": ["correct_cypher"],
        }

    return correct_cypher
