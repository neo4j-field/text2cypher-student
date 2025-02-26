"""
A tool_selection node must
* take a single task at a time
* retrieve a list of available tools
    * text2cypher
    * viz
        * may dynamically provide this according to Task details
    * custom pre-written cypher executors
        * these can be numerous and may be retrieved in the same fashion as CypherQuery node contents
    * unstructured text search (sim search)
* decide the appropriate tool for the task
* generate and validate parameters for the selected tool
* send the validated parameters to the appropriate tool node
"""

from collections.abc import Sequence
from typing import Any, Callable, Coroutine, Dict, List, Literal, Set, Union
from uuid import uuid4

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, InvalidToolCall, ToolCall
from langchain_core.runnables.base import Runnable
from langchain_core.tools import BaseTool
from langgraph.types import Command, Send
from pydantic import BaseModel

from ...components.state import ToolSelectionInputState, ToolSelectionOutputState
from ...components.tool_selection.prompts import create_tool_selection_prompt_template

tool_selection_prompt = create_tool_selection_prompt_template()


def create_tool_selection_node(
    llm: BaseChatModel,
    tool_schemas: Sequence[BaseModel],
    default_to_text2cypher: bool = True,
) -> Callable[[ToolSelectionInputState], Coroutine[Any, Any, Command[Any]]]:
    """
    Create a tool_selection node to be used in a LangGraph workflow.

    Parameters
    ----------
    llm : BaseChatModel
        The LLM used to process data.
    tool_schemas : Sequence[Union[Dict[str, Any], type, Callable, BaseTool]
        tools schemas that inform the LLM which tools are available.
    default_to_text2cypher : bool, optional
        Whether to attempt Text2Cypher if no tool calls are returned by the LLM, by default True

    Returns
    -------
    Callable[[ToolSelectionInputState], ToolSelectionOutputState]
        The LangGraph node.
    """

    tool_selection_chain: Runnable[Dict[str, Any], Any] = (
        tool_selection_prompt | llm.bind_tools(tools=tool_schemas)  # type: ignore[arg-type]
    )

    # get a set of tool names that require the custom cypher executor
    tool_names: Set[str] = {
        t.model_json_schema().get("title", "") for t in tool_schemas
    }

    tool_names.discard("text2cypher")
    tool_names.discard("visualize")

    next_node_options = ["text2cypher", "error_tool_selection", "predefined_cypher"]

    async def tool_selection(  # type: ignore[return]
        state: ToolSelectionInputState,
    ) -> Command[Literal[*next_node_options]]:  # type: ignore
        """
        Choose the appropriate tool for the given task.
        """

        go_to_text2cypher: Command[Literal["text2cypher"]] = Command(
            goto=Send(
                "text2cypher",
                {
                    "task": state.get("question", ""),
                    "steps": ["tool_selection"],
                },
            )
        )

        # if possible determine tool without LLM
        if len(tool_names) == 1 and tool_names.pop().lower() == "text2cypher":
            return go_to_text2cypher

        # use LLM to determine tool
        tool_selection_output: AIMessage = await tool_selection_chain.ainvoke(
            {"question": state.get("question", "")}
            # state.get("question", "")
        )

        tool_calls: List[ToolCall] = tool_selection_output.tool_calls

        # route to chosen tool node
        if tool_calls:
            chosen_tool_call: ToolCall = tool_calls[0]
            tool_name: str = chosen_tool_call.get("name", "").lower()

            if tool_name == "text2cypher":
                return go_to_text2cypher
            elif tool_name in tool_names:
                return Command(
                    goto=Send(
                        "predefined_cypher",
                        {
                            "task": state.get("question", ""),
                            "tool_call": chosen_tool_call,
                            "steps": ["tool_selection"],
                        },
                    )
                )

        elif default_to_text2cypher:
            return go_to_text2cypher
        # handle instance where no tool is chosen
        else:
            invalid_tool_calls: List[InvalidToolCall] = (
                tool_selection_output.invalid_tool_calls
            )
            if len(invalid_tool_calls) > 0:
                invalid_tool_call: InvalidToolCall = invalid_tool_calls[0]
            else:
                invalid_tool_call = InvalidToolCall(
                    name="tool_selection",
                    args=None,
                    id="err-" + str(uuid4()),
                    error=f"Unable to assign tool to question: '{state.get("question", "")}'",
                )
            return Command(
                goto=Send(
                    "error_tool_selection",
                    {
                        "task": state.get("question", ""),
                        "tool_call": invalid_tool_call,
                        "steps": ["tool_selection"],
                    },
                )
            )

    return tool_selection
