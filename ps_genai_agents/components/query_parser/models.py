from typing import List, Optional

from pydantic import BaseModel, Field

from ...components.models import SubQuestion


class QueryParserOutput(BaseModel):
    subquestions: List[Optional[SubQuestion]] = Field(
        default=[],
        description="A list of subquestions that exist in the input question, if any exist.",
    )
