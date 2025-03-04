from typing import Any, Callable, Coroutine, Dict, List

from langchain_neo4j import Neo4jGraph

from ...constants import NO_CYPHER_RESULTS
from ..state import PredefinedCypherInputState
from ..text2cypher.state import CypherOutputState


def create_predefined_cypher_node(
    graph: Neo4jGraph, predefined_cypher_dict: Dict[str, str]
) -> Callable[
    [PredefinedCypherInputState],
    Coroutine[Any, Any, Dict[str, List[CypherOutputState] | List[str]]],
]:
    """
    Create a predefined Cypher execution node for a LangGraph workflow.

    Parameters
    ----------
    graph : Neo4jGraph
        The Neo4j graph wrapper.
    predefined_cypher_dict : Dict[str, str]
        A Python dictionary with Cypher query names as keys and parameterized Cypher queries as values.

    Returns
    -------
    Callable[[PredefinedCypherInputState], Dict[str, List[CypherOutputState] | List[str]]]
        The LangGraph node named `predefined_cypher`.
    """

    async def predefined_cypher(
        state: PredefinedCypherInputState,
    ) -> Dict[str, List[CypherOutputState] | List[str]]:
        """
        Executes a predefined Cypher statement with found parameters.
        """
        errors = list()
        # tool_call: ToolCall | None = state.get("tool_call")
        # assert tool_call is not None, "no tool call found in `predefined_cypher` node"
        statement_name = state.get("query_name", "")
        params = state.get(
            "query_parameters", dict()
        )  # these should have been validated already during LLM output parsing

        statement = predefined_cypher_dict.get(statement_name)

        if statement is not None:
            records = graph.query(query=statement, params=params)
        else:
            errors.append(
                f"Unable to find the specified Cypher statement: {statement_name}"
            )
            records = list()

        return {
            "cyphers": [
                CypherOutputState(
                    **{
                        "task": state.get("task", ""),
                        "statement": statement or "",
                        "parameters": params,
                        "errors": errors,
                        "records": records or NO_CYPHER_RESULTS,
                        "steps": ["execute_predefined_cypher"],
                    }
                )
            ],
            "steps": ["execute_predefined_cypher"],
        }

    return predefined_cypher
