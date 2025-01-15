from typing import Any


def create_final_summary_prompt(tool_execution_result: Any, question: str) -> str:
    """
    Create the final LLM prompt asking to summarize the results of the last tool used.

    Parameters
    ----------
    tool_execution_result : Any
        The final result of the chain.
    question : str
        The user question provided to the LLM.

    Returns
    -------
    str
        The constructed prompt.
    """

    return f"""Human:
    Fact: {tool_execution_result}

    * Summarise the above fact as if you are answering this question "{question}"
    * When the fact is not empty, assume the question is valid and the answer is true
    * Do not return helpful or extra text or apologies
    * Just return summary to the user. DO NOT start with "Here is a summary"
    * List the results in rich text format if there are more than one results
    * Don't report empty String results, but include results that are 0 or 0.0.
    Assistant:
    """


def create_final_summary_prompt_without_lists(
    tool_execution_result: Any, question: str
) -> str:
    """
    Create the final LLM prompt asking to summarize the results of the last tool used.
    LLM will attempt to return results in a non-list format.

    Parameters
    ----------
    tool_execution_result : Any
        The final result of the chain.
    question : str
        The user question provided to the LLM.

    Returns
    -------
    str
        The constructed prompt.
    """

    return f"""Human:
    Fact: {tool_execution_result}

    * Summarise the above fact as if you are answering this question "{question}"
    * When the fact is not empty, assume the question is valid and the answer is true
    * Do not return extra text or apologies
    * Just return summary to the user. DO NOT start with "Here is a summary"
    * Don't report empty String results, but include results that are 0 or 0.0.
    * Only use bulletpoints to improve readability. Do not just list the provided Facts. Do not ever use more than a FEW bulletpoints.
    Assistant:
    """
