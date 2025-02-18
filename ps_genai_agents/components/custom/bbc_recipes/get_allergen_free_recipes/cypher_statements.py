from typing import List


def create_allergens_cypher_statement(allergens: List[str]) -> str:
    """
    This Cypher statement will find all recipes that don't include the identified allergens and return the recipe name as well as the ingredients list.
    """
    return f"""
MATCH (r:Recipe)
WHERE none(i in {str(allergens)} WHERE exists(
    (r)-[:CONTAINS_INGREDIENT]->(:Ingredient {{name: i}})))
RETURN r.name AS recipe,
        [(r)-[:CONTAINS_INGREDIENT]->(i) | i.name]
        AS ingredients
ORDER BY size(ingredients)
LIMIT 20
"""
