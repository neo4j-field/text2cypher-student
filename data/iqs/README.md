# IQS Data

This directory contains data on customer feedback and demographics for Honda vehicles.

## Data Loading

1. Unzip dataset/iqs-data.zip
2. Ensure your `.env` file contains the proper Neo4j and OpenAI credentials
3. From the project root run: `make load_iqs`

If you would like to only load the IQS data and not the Cypher Query vector store, you may run
```
poetry run python3 data/iqs/ingest/ingest_iqs.py
```
from the project root. This doesn't require any LLM provider credentials.
