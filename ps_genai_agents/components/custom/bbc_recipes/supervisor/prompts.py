from langchain_core.prompts import ChatPromptTemplate

system = """
You are an expert at task management. You must decide which tool will be most effective in answering the provided question.
"""


def create_allergens_prompt_template() -> ChatPromptTemplate:
    """
    Create a supervisor prompt template.

    Returns
    -------
    ChatPromptTemplate
        The prompt template.
    """

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system,
            ),
            (
                "human",
                """question: {user_input}
input contains data: {input_contains_data}""",
            ),
        ]
    )
