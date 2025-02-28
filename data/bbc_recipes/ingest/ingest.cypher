//set up indexes and constraints for query performance
CREATE CONSTRAINT recipe_id_nodekey IF NOT EXISTS
FOR (n:Recipe) REQUIRE (n.id) IS NODE KEY;

CREATE Constraint recipe_name_nodekey IF NOT EXISTS
FOR (n:Recipe) REQUIRE (n.name) IS NODE KEY;

CREATE CONSTRAINT ingredient_nodekey IF NOT EXISTS
FOR (n:Ingredient) REQUIRE (n.name) IS NODE KEY;

CREATE CONSTRAINT keyword_nodekey IF NOT EXISTS
FOR (n:Keyword) REQUIRE (n.name) IS NODE KEY;

CREATE CONSTRAINT diet_type_nodekey IF NOT EXISTS
FOR (n:DietType) REQUIRE (n.name) IS NODE KEY;

CREATE CONSTRAINT author_nodekey IF NOT EXISTS
FOR (n:Author) REQUIRE (n.name) IS NODE KEY;

CREATE CONSTRAINT collection_nodekey IF NOT EXISTS
FOR (n:Collection) REQUIRE (n.name) IS NODE KEY;

//import recipes to the graph
CALL apoc.load.json('https://raw.githubusercontent.com/neo4j-examples/graphgists/master/browser-guides/data/stream_clean.json') YIELD value
WITH value.page.article.id AS id,
       toLower(value.page.title) AS title,
       toLower(value.page.article.description) AS description,
       value.page.recipe.cooking_time AS cookingTime,
       value.page.recipe.prep_time AS preparationTime,
       toLower(value.page.recipe.skill_level) AS skillLevel
MERGE (r:Recipe {name: title})
ON CREATE
SET r.cookingTimeMinutes = cookingTime / 60,
    r.preparationTimeMinutes = preparationTime / 60,
    r.id = id,
    r.description = description,
    r.skillLevel = skillLevel;

//import authors and connect to recipes
CALL apoc.load.json('https://raw.githubusercontent.com/neo4j-examples/graphgists/master/browser-guides/data/stream_clean.json') YIELD value
WITH value.page.article.id AS id,
       toLower(value.page.article.author) AS author
MERGE (a:Author {name: author})
WITH a,id
MATCH (r:Recipe {id:id})
MERGE (a)-[:WROTE]->(r);

//import ingredients and connect to recipes
CALL apoc.load.json('https://raw.githubusercontent.com/neo4j-examples/graphgists/master/browser-guides/data/stream_clean.json') YIELD value
WITH value.page.article.id AS id,
       value.page.recipe.ingredients AS ingredients
MATCH (r:Recipe {id:id})
FOREACH (ingredient IN ingredients |
  MERGE (i:Ingredient {name: toLower(ingredient)})
  MERGE (r)-[:CONTAINS_INGREDIENT]->(i)
);

//import keywords and connect to recipes
CALL apoc.load.json('https://raw.githubusercontent.com/neo4j-examples/graphgists/master/browser-guides/data/stream_clean.json') YIELD value
WITH value.page.article.id AS id,
       value.page.recipe.keywords AS keywords
MATCH (r:Recipe {id:id})
FOREACH (keyword IN keywords |
  MERGE (k:Keyword {name: toLower(keyword)})
  MERGE (r)-[:KEYWORD]->(k)
);

//import dietTypes and connect to recipes
CALL apoc.load.json('https://raw.githubusercontent.com/neo4j-examples/graphgists/master/browser-guides/data/stream_clean.json') YIELD value
WITH value.page.article.id AS id,
       value.page.recipe.diet_types AS dietTypes
MATCH (r:Recipe {id:id})
FOREACH (dietType IN dietTypes |
  MERGE (d:DietType {name: toLower(dietType)})
  MERGE (r)-[:DIET_TYPE]->(d)
);

//import collections and connect to recipes
CALL apoc.load.json('https://raw.githubusercontent.com/neo4j-examples/graphgists/master/browser-guides/data/stream_clean.json') YIELD value
WITH value.page.article.id AS id,
       value.page.recipe.collections AS collections
MATCH (r:Recipe {id:id})
FOREACH (collection IN collections |
  MERGE (c:Collection {name: toLower(collection)})
  MERGE (r)-[:COLLECTION]->(c)
);
