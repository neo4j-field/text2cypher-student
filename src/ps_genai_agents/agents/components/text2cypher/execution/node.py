"""
This code is based on content found in the LangGraph documentation: https://python.langchain.com/docs/tutorials/graph/#advanced-implementation-with-langgraph
"""

from typing import Callable

from agents.components.state import CypherState, OverallState
from langchain_neo4j import Neo4jGraph


def create_text2cypher_execution_node(
    graph: Neo4jGraph,
) -> Callable[[CypherState], CypherState]:
    """
    Create a Text2Cypher execution node for a LangGraph workflow.

    Parameters
    ----------
    graph : Neo4jGraph
        The Neo4j graph wrapper.

    Returns
    -------
    Callable[[CypherState], CypherState]
        The LangGraph node.
    """

    no_results = "I couldn't find any relevant information in the database"

    def execute_cypher(state: CypherState) -> OverallState:
        """
        Executes the given Cypher statement.
        """

        records = graph.query(state.get("statement"))
        return {
            "cyphers": [
                {
                    "subquestion": state.get("subquestion"),
                    "statement": state.get("statement"),
                    "errors": state.get("errors"),
                    "records": records if records else no_results,
                    "steps": ["execute_cypher"],
                }
            ]
        }

    return execute_cypher
