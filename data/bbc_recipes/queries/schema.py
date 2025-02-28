from typing import List

from pydantic import BaseModel, Field, field_validator


class get_allergen_free_recipes(BaseModel):
    """Retrieve a list of all recipes that do not contain the provided allergens."""

    allergens: List[str] = Field(
        ..., description="A list of allergens that should be avoided in recipes."
    )


class get_most_common_ingredients_an_author_uses(BaseModel):
    """Retrieve the most common ingredients a specific author uses in their recipes."""

    author: str = Field(..., description="The full author name to search for.")

    @field_validator("author")
    def validate_author(cls, v: str) -> str:
        return v.lower()



class get_recipes_for_diet_restrictions(BaseModel):
    """Retrieve a list of recipes that adhere to the requested diet restrictions."""

    diet_restrictions: List[str] = Field(..., description="The diet restrictions.")


class get_easy_recipes(BaseModel):
    """Retrieve the desired amount of easy recipes."""

    number_of_recipes: int = Field(
        ..., description="The desired number of recipes to be returned."
    )


class get_mid_difficulty_recipes(BaseModel):
    """Retrieve the desired amount of mid difficulty recipes."""

    number_of_recipes: int = Field(
        ..., description="The desired number of recipes to be returned."
    )


class get_difficult_recipes(BaseModel):
    """Retrieve the desired amount of difficult recipes."""

    number_of_recipes: int = Field(
        ..., description="The desired number of recipes to be returned."
    )

def get_tool_schemas() -> List[type[BaseModel]]:
    return [
        get_allergen_free_recipes,
        get_most_common_ingredients_an_author_uses,
        get_recipes_for_diet_restrictions,
        get_easy_recipes,
        get_mid_difficulty_recipes,
        get_difficult_recipes
    ]