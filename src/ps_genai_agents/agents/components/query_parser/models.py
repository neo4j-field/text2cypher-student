from typing import List, Optional

from agents.components.models import SubQuestion
from pydantic import BaseModel, Field


class QueryParserOutput(BaseModel):
    subquestions: List[Optional[SubQuestion]] = Field(
        default=[],
        description="A list of subquestions that exist in the input question, if any exist.",
    )
