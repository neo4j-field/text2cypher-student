from typing import Any, Callable, Coroutine, Dict

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables.base import Runnable

from ...components.state import OverallState
from ...components.tool_selection.models import ToolSelectionOutput
from ...components.tool_selection.prompts import (
    create_tool_selection_prompt_template,
)

generate_tool_select_prompt = create_tool_selection_prompt_template()


def create_tool_selection_node(
    llm: BaseChatModel,
) -> Callable[[OverallState], Coroutine[Any, Any, dict[str, Any]]]:
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

    generate_tool_select: Runnable[Dict[str, Any], Any] = (
        generate_tool_select_prompt | llm.with_structured_output(ToolSelectionOutput)
    )

    async def tool_select(state: OverallState) -> Dict[str, Any]:
        """
        Select an appropriate tool to perform requested task.
        """

        response: ToolSelectionOutput = await generate_tool_select.ainvoke(
            {
                "question": state.get("question"),
                "does_summary_exist": state.get("summary") is not None,
            }
        )
        return {"next_action": response.tool_selection, "steps": ["tool_select"]}

    return tool_select
