from typing import Any, Callable, Dict

from ...components.state import OverallState
from ...components.tool_selection.prompts import (
    create_tool_selection_prompt_template,
)

generate_tool_select_prompt = create_tool_selection_prompt_template()


def create_gather_cypher_node() -> Callable[[OverallState], Dict[str, Any]]:
    """
    Create a gather_cypher node for a LangGraph workflow.

    Returns
    -------
    Callable[[OverallState], OverallState]
        The LangGraph node.
    """

    def gather_cypher(state: OverallState) -> Dict[str, Any]:
        """
        Gather Cypher task results.
        """
        print(
            f"GATHERED {len(state.get('cyphers', []))} of {len(state.get('subquestions', []))} TASKS."
        )
        return {"steps": ["gather_cypher"]}

    return gather_cypher
