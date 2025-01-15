from typing import Callable

from agents.components.models import SubQuestion
from agents.components.query_parser.models import QueryParserOutput
from agents.components.query_parser.prompts import create_query_parser_prompt_template
from agents.components.state import InputState, OverallState
from langchain_core.language_models import BaseChatModel

query_parser_prompt = create_query_parser_prompt_template()


def create_query_parser_node(
    llm: BaseChatModel, ignore_node: bool = False
) -> Callable[[InputState], OverallState]:
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

    query_parser_chain = query_parser_prompt | llm.with_structured_output(
        QueryParserOutput
    )

    def query_parser(state: InputState) -> OverallState:
        """
        Break user query into chunks, if appropriate.
        """

        if not ignore_node:
            query_parser_output = query_parser_chain.invoke(
                {"question": state.get("question")}
            )
        else:
            query_parser_output = QueryParserOutput(subquestions=[])
        return {
            "next_action": "tool_selection",
            "subquestions": query_parser_output.subquestions
            or [SubQuestion(subquestion=state.get("question"))],
            "steps": ["query_parser"],
        }

    return query_parser
