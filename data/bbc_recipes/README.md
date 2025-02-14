# BBC Good Food Recipes Data

This directory contains data on recipes from BBC Good Food. 

## Data Loading

1. Ensure your `.env` file contains the proper Neo4j and OpenAI credentials
2. From the project root run: `make load_bbc_recipes`

If you would like to only load the recipe data and not the Cypher Query vector store, you may run
```
poetry run python3 data/bbc_recipes/ingest/ingest_bbc_recipes.py
```
from the project root. This doesn't require any LLM provider credentials.