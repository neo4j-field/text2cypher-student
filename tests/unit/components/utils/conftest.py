from unittest.mock import MagicMock

import pytest
from langchain_neo4j import Neo4jGraph


@pytest.fixture(scope="function")
def graph_schema_string_1() -> str:
    return """
Node properties:
- **CypherQuery**
  - `question`: STRING Example: "What is the proportion of male to female complaina"
  - `cypherStatement`: STRING Example: "MATCH (v:Verbatim {make: "Honda", model: "Odyssey""
  - `embeddingModel`: STRING Available options: ['text-embedding-ada-002', 'test-model']
  - `questionEmbedding`: LIST Min Size: 3, Max Size: 1536
- **Verbatim**
  - `id`: STRING Example: "9323AB5C"
Relationship properties:
"""


@pytest.fixture(scope="function")
def graph_schema_string_2() -> str:
    return """
Node properties:
- **Verbatim**
  - `id`: STRING Example: "9323AB5C"
- **CypherQuery**
  - `question`: STRING Example: "What is the proportion of male to female complaina"
  - `cypherStatement`: STRING Example: "MATCH (v:Verbatim {make: "Honda", model: "Odyssey""
  - `embeddingModel`: STRING Available options: ['text-embedding-ada-002', 'test-model']
  - `questionEmbedding`: LIST Min Size: 3, Max Size: 1536
Relationship properties:
"""


@pytest.fixture(scope="function")
def graph_schema_string_answer() -> str:
    return """
Node properties:
- **Verbatim**
  - `id`: STRING Example: "9323AB5C"
Relationship properties:
"""


@pytest.fixture(scope="function")
def graph_1(graph_schema_string_1: str) -> MagicMock:
    m = MagicMock(spec=Neo4jGraph)
    m.get_schema = graph_schema_string_1
    return m


@pytest.fixture(scope="function")
def graph_2(graph_schema_string_2: str) -> MagicMock:
    m = MagicMock(spec=Neo4jGraph)
    m.get_schema = graph_schema_string_2
    return m
