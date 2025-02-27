from typing import Any, Callable, Coroutine, Dict, List

from ....components.state import ToolSelectionErrorState
from ....components.text2cypher.state import CypherOutputState


def create_error_tool_selection_node() -> Callable[
    [ToolSelectionErrorState], Coroutine[Any, Any, Dict[str, Any]]
]:
    """
    Create a error_tool_selection node for a LangGraph workflow.

    Returns
    -------
    Callable[[OverallState], OutputState]
        The LangGraph node named `error_tool_selection`.
    """

    async def error_tool_selection(state: ToolSelectionErrorState) -> Dict[str, Any]:
        """
        Handle errors in tool selection node.
        """
        errors: List[str] = list()
        steps = ["error_tool_selection"]
        invalid_tool_call = state.get("invalid_tool_call")
        if invalid_tool_call is not None:
            error = invalid_tool_call.get("error")
            if error is not None:
                errors.append(error)
        return {
            "cyphers": [
                CypherOutputState(
                    **{
                        "task": state.get("task", ""),
                        "statement": "",
                        "errors": errors,
                        "records": list(),
                        "steps": steps,
                    }
                )
            ],
            "steps": steps,
        }

    return error_tool_selection
