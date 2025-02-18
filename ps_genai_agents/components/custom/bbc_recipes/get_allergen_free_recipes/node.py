from typing import Any, Callable, Coroutine, Dict, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables.base import Runnable
from langchain_neo4j import Neo4jGraph

from .....components.text2cypher.state import (
    CypherInputState,
    CypherOutputState,
    CypherState,
)
from .....constants import NO_CYPHER_RESULTS
from .cypher_statements import create_allergens_cypher_statement
from .models import AllergensNEROutput
from .prompts import create_allergens_prompt_template


def create_get_allergen_free_recipes_node(
    llm: BaseChatModel, graph: Neo4jGraph
) -> Callable[[CypherInputState], Coroutine[Any, Any, dict[str, Any]]]:
    """
    Create a get_allergen_free_recipes node to be used in a LangGraph workflow.

    Parameters
    ----------
    llm: BaseChatModel
        The LLM used to perform NER to extract allergens.
    graph: Neo4jGraph
        The Neo4j graph wrapper.

    Returns
    -------
    Callable[[CypherInputState], OverallState]
        The LangGraph node.
    """

    prompt = create_allergens_prompt_template()

    chain: Runnable[Dict[str, Any], Any] = prompt | llm.with_structured_output(
        AllergensNEROutput
    )

    async def get_allergen_free_recipes(state: CypherInputState) -> Dict[str, Any]:
        """
        Decides if the question is in scope.
        """

        response: AllergensNEROutput = await chain.ainvoke(
            {"user_input": state.get("subquestion", "")}
        )

        statement = create_allergens_cypher_statement(response.allergens)

        records = graph.query(statement)
        steps = ["get_allergen_free_recipes_tool"]

        return {
            "cyphers": [
                CypherOutputState(
                    **{
                        "subquestion": state.get("subquestion", ""),
                        "statement": statement,
                        "errors": list(),
                        "records": records if records else NO_CYPHER_RESULTS,
                        "steps": steps,
                    }
                )
            ],
            "steps": steps,
        }

    return get_allergen_free_recipes
