from langchain_core.prompts import ChatPromptTemplate

query_parser_system = """
You must analyze the input question and decide if distinct subquestions exist that can be answered with a database query.
If appropriate independent subquestions exist, then provide them as a list, otherwise return an empty list.
Subquestions should NOT be dependent on each other.
Return a list of questions that the agent should address.
"""


def create_query_parser_prompt_template() -> ChatPromptTemplate:
    """
    Create a query parser prompt template.

    Returns
    -------
    ChatPromptTemplate
        The prompt template.
    """
    message = """Rules:
* Return as few subquestions as possible. This is important to reduce costs.
* Ensure that the subquestions are not returning duplicated or similar information.
* Ensure that subquestions are NOT dependent on information gathered from other subquestions!
* Subquestions that are dependent on each other should be combined into a single question.
* Subquestions that return similar information should be combined into a single question.

question: {question}
"""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                query_parser_system,
            ),
            (
                "human",
                (message),
            ),
        ]
    )
