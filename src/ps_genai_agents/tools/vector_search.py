"""
This file contains the Vector Search tool used in the Agent architecture.
"""

from typing import Any, Dict

from langchain.tools import tool
from neo4j import Driver
from neo4j_genai.embedder import Embedder
from neo4j_genai.retrievers import VectorRetriever


def create_neo4j_vector_search_tool(
    driver: Driver, embedder: Embedder, index_name: str
) -> Any:
    """
    Create a Neo4jVectorSearch tool with the provided vector chain.

    Parameters
    ----------
    driver : Driver
        The Neo4j Python driver instance to use.
    embedder: Embedder
        An embedding service that adheres to the Neo4j GenAI Python library Embedder interface.
    index_name: str
        The name of the vector index in the database.

    Returns
    -------
    Callable
        The tool.
    """

    @tool("Neo4jVectorSearch", return_direct=False)  # type: ignore[misc]
    def neo4j_vector_search(query: str, top_k: int = 10) -> Dict[str, Any]:
        """
        * Use only for:
            - Answering questions about summaries of verbatims.
            - Analyzing unstructured text.
        * Do NOT use for aggregations or maths such as:
            - Calculating proportions, ratios or counts.
            - Finding total of verbatims under Categories, Problems, Questions or Vehicles.
            - Finding vehicle lists.
        * Use full question as input.
        """

        retriever = VectorRetriever(driver, index_name, embedder)

        return {"result": retriever.search(query_text=query, top_k=top_k).items}

    return neo4j_vector_search
