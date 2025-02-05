from typing import Any, Callable, Coroutine, Dict

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables.base import Runnable

from ...components.models import SubQuestion
from ...components.query_parser.models import QueryParserOutput
from ...components.query_parser.prompts import create_query_parser_prompt_template
from ...components.state import InputState

query_parser_prompt = create_query_parser_prompt_template()


def create_query_parser_node(
    llm: BaseChatModel, ignore_node: bool = False
) -> Callable[[InputState], Coroutine[Any, Any, Dict[str, Any]]]:
    """
    Create a query parser node to be used in a LangGraph workflow.

    Parameters
    ----------
    llm : BaseChatModel
        The LLM used to process data.
    ignore_node : bool, optional
        Whether to ignore this node in the workflow, by default False

    Returns
    -------
    Callable[[InputState], OverallState]
        The LangGraph node.
    """

    query_parser_chain: Runnable[Dict[str, Any], Any] = (
        query_parser_prompt | llm.with_structured_output(QueryParserOutput)
    )

    async def query_parser(state: InputState) -> Dict[str, Any]:
        """
        Break user query into chunks, if appropriate.
        """

        if not ignore_node:
            query_parser_output: QueryParserOutput = await query_parser_chain.ainvoke(
                {"question": state.get("question")}
            )
        else:
            query_parser_output = QueryParserOutput(subquestions=[])
        return {
            "next_action": "tool_selection",
            "subquestions": query_parser_output.subquestions
            or [SubQuestion(subquestion=state.get("question", ""))],
            "steps": ["query_parser"],
        }

    return query_parser
