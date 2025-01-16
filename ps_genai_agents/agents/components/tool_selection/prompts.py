from langchain.prompts import ChatPromptTemplate

tool_selection_system = """
You must analyze the input question to assess which additional tool should be used to process the Cypher query results in order to sufficiently answer the question.
* 'summarize' will summarize the Cypher query results.
* 'final_result' will format the final result object and requires a summary to exist.
"""


def create_tool_selection_prompt_template() -> ChatPromptTemplate:
    """
    Create a tool selection prompt template.

    Returns
    -------
    str
        The template.
    """

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                tool_selection_system,
            ),
            (
                "human",
                (
                    """Original question: {question}
Summary Exists: {does_summary_exist}"""
                ),
            ),
        ]
    )
