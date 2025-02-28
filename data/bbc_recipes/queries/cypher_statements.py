from typing import Dict

def get_allergen_free_recipes() -> str:
    """
    This Cypher statement will find all recipes that don't include the identified allergens and return the recipe name as well as the ingredients list.

    Parameters
    ----------
    allergens : List[str]
    """
    return """
MATCH (r:Recipe)
WHERE none(i in $allergens WHERE exists(
    (r)-[:CONTAINS_INGREDIENT]->(:Ingredient {name: i})))
RETURN r.name AS recipe,
        [(r)-[:CONTAINS_INGREDIENT]->(i) | i.name]
        AS ingredients
ORDER BY size(ingredients)
LIMIT 20
"""


def get_most_common_ingredients_an_author_uses() -> str:
    """
    Parameters
    ----------
    author : str
    """
    return """
MATCH (:Author {name: $author})-[:WROTE]->(:Recipe)-[:CONTAINS_INGREDIENT]->(i:Ingredient)
RETURN i.name as name, COUNT(*) as numRecipes
ORDER BY numRecipes DESC
LIMIT 10
"""


def get_recipes_for_diet_restrictions() -> str:
    """
    Parameters
    ----------
    diet_restrictions : List[str]
    """
    return """
MATCH (d:DietType)<-[:DIET_TYPE]-(r:Recipe)
WHERE d.name in $diet_restrictions
RETURN r.name as name
LIMIT 10
"""


def get_easy_recipes() -> str:
    """
    Parameters
    ----------
    number_of_recipes : int
    """
    return """
MATCH (r:Recipe {skillLevel: "aasy"})
RETURN r.name as name
LIMIT $number_of_recipes
"""


def get_mid_difficulty_recipes() -> str:
    """
    Parameters
    ----------
    number_of_recipes : int
    """
    return """
MATCH (r:Recipe {skillLevel: "more effort"})
RETURN r.name as name
LIMIT $number_of_recipes
"""


def get_difficult_recipes() -> str:
    """
    Parameters
    ----------
    number_of_recipes : int
    """
    return """
MATCH (r:Recipe {skillLevel: "a challenge"})
RETURN r.name as name
LIMIT $number_of_recipes
"""

def get_cypher_statements_dictionary() -> Dict[str, str]:
    """
    Get a Python dictionary with Cypher statement names as keys and parameterized Cypher statements as values.

    Returns
    -------
    Dict[str, str]
        The Cypher statements dictionary.
    """
    return {
        "get_allergen_free_recipes": get_allergen_free_recipes(),
        "get_most_common_ingredients_an_author_uses": get_most_common_ingredients_an_author_uses(),
        "get_recipes_for_diet_restrictions": get_recipes_for_diet_restrictions(),
        "get_easy_recipes": get_easy_recipes(),
        "get_mid_difficulty_recipes": get_mid_difficulty_recipes(),
        "get_difficult_recipes": get_difficult_recipes(),
    }