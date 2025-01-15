from typing import Callable

from agents.components.state import OverallState
from agents.components.tool_selection.prompts import (
    create_tool_selection_prompt_template,
)

generate_tool_select_prompt = create_tool_selection_prompt_template()


def create_gather_cypher_node() -> Callable[[OverallState], OverallState]:
    """
    Create a gather_cypher node for a LangGraph workflow.

    Returns
    -------
    Callable[[OverallState], OverallState]
        The LangGraph node.
    """

    def gather_cypher(state: OverallState) -> OverallState:
        """
        Gather Cypher task results.
        """

        return {"steps": ["gather_cypher"]}

    return gather_cypher
