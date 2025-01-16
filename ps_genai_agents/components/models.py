from pydantic import BaseModel, Field


class SubQuestion(BaseModel):
    subquestion: str = Field(description="The subquestion text.")
    requires_visualization: bool = Field(
        default=False,
        description="Whether this subquestion requires a visual to be returned.",
    )
