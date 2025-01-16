from typing import Any, Callable, Dict

from ...components.state import OverallState


def create_final_answer_node() -> Callable[[OverallState], Dict[str, Any]]:
    """
    Create a final_answer node for a LangGraph workflow.

    Parameters
    ----------
    llm : BaseChatModel
        The LLM do perform processing.

    Returns
    -------
    Callable[[OverallState], OutputState]
        The LangGraph node.
    """

    def final_answer(state: OverallState) -> Dict[str, Any]:
        """
        Construct a final answer.
        """

        ERROR = "Unable to answer the question."

        return {"answer": state.get("summary", ERROR), "steps": ["final_answer"]}

    return final_answer
