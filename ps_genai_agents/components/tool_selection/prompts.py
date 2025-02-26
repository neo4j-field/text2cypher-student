from typing import Dict

from langchain_core.prompts import ChatPromptTemplate

system = """
You are responsible for choosing the appropriate tool for the given question. Use only the tools available to you. 
You should select the text2cypher tool, unless another tool exactly matches what the question is asking for. 
"""


def create_tool_selection_prompt_template() -> ChatPromptTemplate:
    """
    Create a tool selection prompt template.

    Returns
    -------
    ChatPromptTemplate
        The prompt template.
    """

    message = "Question: {question}"

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system,
            ),
            (
                "human",
                (message),
            ),
        ]
    )


# def _format_tool_options(tool_options_dict: Dict[str, str]) -> str:
#     result = "Tool Options:"
#     for t in tool_options_dict.items():
#         result += f"\n* {t.get("name", "")}({t.get("parameters", "")}): {t.get("description", "")}"

#     return result
