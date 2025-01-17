from typing import Any, Callable, Dict

from ...components.state import OverallState
from ...components.tool_selection.prompts import (
    create_tool_selection_prompt_template,
)

generate_tool_select_prompt = create_tool_selection_prompt_template()


def create_gather_visualizations_node() -> Callable[[OverallState], Dict[str, Any]]:
    """
    Create a gather_visualizations node for a LangGraph workflow.

    Returns
    -------
    Callable[[OverallState], OverallState]
        The LangGraph node.
    """

    def gather_visualizations(state: OverallState) -> Dict[str, Any]:
        """
        Gather visualization task results.
        """
        return {"steps": ["gather_visualizations"]}

    return gather_visualizations
