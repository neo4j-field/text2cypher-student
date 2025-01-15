from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ToolSelectionOutput(BaseModel):
    tool_selection: Literal["summarize", "final_result"] = Field(
        description="The next tool used to process Cypher results."
    )
