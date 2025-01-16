"""
This code is based on content found in the LangGraph documentation: https://python.langchain.com/docs/tutorials/graph/#advanced-implementation-with-langgraph
"""

from typing import Any, Callable, Dict

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

from ...components.state import OverallState
from ...components.summarize.prompts import create_summarization_prompt_template

generate_summary_prompt = create_summarization_prompt_template()


def create_summarization_node(
    llm: BaseChatModel,
) -> Callable[[OverallState], Dict[str, Any]]:
    """
    Create a Summarization node for a LangGraph workflow.

    Parameters
    ----------
    llm : BaseChatModel
        The LLM do perform processing.

    Returns
    -------
    Callable[[OverallState], OutputState]
        The LangGraph node.
    """

    generate_summary = generate_summary_prompt | llm | StrOutputParser()

    def summarize(state: OverallState) -> Dict[str, Any]:
        """
        Summarize results of the performed Cypher queries.
        """

        summary = generate_summary.invoke(
            {
                "question": state.get("question"),
                "results": [
                    cypher.get("records") for cypher in state.get("cyphers", list())
                ],
            }
        )
        return {"summary": summary, "steps": ["summarize"]}

    return summarize
