from typing import List

from pydantic import BaseModel, Field


class AllergensNEROutput(BaseModel):
    allergens: List[str] = Field(
        description="A list of allergens found in the input question."
    )


class get_allergen_free_recipes(BaseModel):
    """Retrieve a list of recipes that do not include the provided 'allergens'."""

    allergens: List[str] = Field(..., description="A list of food allergens")
