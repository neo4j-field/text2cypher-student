from typing import Any, Callable, Coroutine, Dict, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, InvalidToolCall, ToolCall
from langchain_core.output_parsers import PydanticToolsParser
from langgraph.types import Send

from ....state import InputState
from .prompts import create_allergens_prompt_template

prompt = create_allergens_prompt_template()


def create_supervisor_node(
    llm: BaseChatModel, tool_definitions: List[Any]
) -> Callable[[InputState], Coroutine[Any, Any, Send]]:
    chain = (
        prompt
        | llm.bind_tools(tool_definitions)
        | PydanticToolsParser(tools=tool_definitions)
    )

    async def supervisor_node(state: InputState) -> Send:
        input_contains_data = True if state.get("data") is not None else False
        response: AIMessage = await chain.ainvoke(
            {
                "question": state.get("question", ""),
                "input_contains_data": input_contains_data,
            }
        )

        tool_calls: List[ToolCall] = response.tool_calls
        invalid_tool_calls: List[InvalidToolCall] = response.invalid_tool_calls

        tool_call = tool_calls[0]
        next_action = tool_call.get("name", "")

        match next_action:
            case "text2cypher":
                return Send("text2cypher", {"subquestion": state.get("question", "")})
            case "visualization":
                return Send(
                    "visualization",
                    {
                        "subquestion": state.get("question", ""),
                        "data": state.get("data", list()),
                    },
                )
            case _:
                return Send("custom_tool", tool_call)

    return supervisor_node
