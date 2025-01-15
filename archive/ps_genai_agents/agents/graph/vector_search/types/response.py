"""
This file contains Pydantic models that represent the final LLM Response.
"""

from typing import Any, List, Optional, Union

from langchain_core.pydantic_v1 import BaseModel, Field


class Response(BaseModel):
    """
    Final response to the question being asked
    """

    question: str = Field(description="The question asked by the user.")
    sub_questions: Optional[List[str]] = Field(
        description="The sub questions that are found by the LLM within the original question.",
        default=None,
    )
    answer: str = Field(description="The final answer to respond to the user.")
    sources: Optional[Union[List[List[str]], List[str]]] = Field(
        description="The IDs of the nodes that contain the text used to generate the response.",
        default=None,
    )

    vector_search_result: Optional[Union[List[Any], str]] = Field(
        description="The summary result of the vector search.", default=None
    )

    def display(self) -> None:
        """
        Print the response object nicely.
        """

        base = f"""
Question:
{self.question}
"""
        if self.sub_questions:
            q = ""
            for q in self.sub_questions:
                q += "\n"
            base += f"""
Sub Questions:
{q}
            """

        if self.sources:
            base += f"""
Vector Search Source IDs:
{self.sources}

Vector Search Summary:
{self.vector_search_result}
            """

        base += f"""
Final Response:
{self.answer}
        """

        print(base)
