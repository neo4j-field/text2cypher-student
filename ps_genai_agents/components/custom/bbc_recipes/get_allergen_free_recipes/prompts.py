from langchain_core.prompts import ChatPromptTemplate

allergens_system = """
You are an expert at entity extraction. You must extract all allergens found in the input.
"""


def create_allergens_prompt_template() -> ChatPromptTemplate:
    """
    Create an allergens prompt template.

    Returns
    -------
    ChatPromptTemplate
        The prompt template.
    """

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                allergens_system,
            ),
            (
                "human",
                "{user_input}",
            ),
        ]
    )
