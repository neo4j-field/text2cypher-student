from typing import Any, Callable, Dict, List

from agents.components.state import OutputState, OverallState
from agents.components.tool_selection.models import ToolSelectionOutput
from agents.components.tool_selection.prompts import (
    create_tool_selection_prompt_template,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

generate_tool_select_prompt = create_tool_selection_prompt_template()


def create_tool_selection_node(
    llm: BaseChatModel,
) -> Callable[[OverallState], OverallState]:
    """
    Create a tool_select node for a LangGraph workflow.

    Parameters
    ----------
    llm : BaseChatModel
        The LLM to perform processing.

    Returns
    -------
    Callable[[OverallState], OutputState]
        The LangGraph node.
    """

    generate_tool_select = generate_tool_select_prompt | llm.with_structured_output(
        ToolSelectionOutput
    )

    def tool_select(state: OverallState) -> OverallState:
        """
        Select an appropriate tool to perform requested task.
        """

        response = generate_tool_select.invoke(
            {
                "question": state.get("question"),
                "does_summary_exist": state.get("summary") is not None,
            }
        )
        return {"next_action": response.tool_selection, "steps": ["tool_select"]}

    return tool_select
