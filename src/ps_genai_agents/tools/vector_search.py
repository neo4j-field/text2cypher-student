"""
This file contains the Vector Search tool used in the Agent architecture.
"""

from typing import Any, Callable, Dict, List, Optional

import neo4j
from langchain.tools import tool
from neo4j import Driver
from neo4j_genai.embedder import Embedder
from neo4j_genai.retrievers import VectorRetriever
from neo4j_genai.types import RetrieverResultItem


def create_neo4j_vector_search_tool(
    driver: Driver,
    embedder: Embedder,
    index_name: str,
    return_properties: Optional[List[str]] = None,
    result_formatter: Optional[Callable[[neo4j.Record], RetrieverResultItem]] = None,
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

    @tool("Neo4jVectorSearch", return_direct=False)  # type: ignore
    def neo4j_vector_search(query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        * Use only for:
            - Answering questions about summaries.
            - Analyzing unstructured text.
        * Do NOT use for aggregations or maths such as:
            - Calculating proportions, ratios or counts.
            - Finding totals.
            - Finding lists.
        * Use full question as input.
        """

        retriever = VectorRetriever(
            driver=driver,
            index_name=index_name,
            embedder=embedder,
            return_properties=return_properties,
            result_formatter=result_formatter,
        )

        return {"result": retriever.search(query_text=query, top_k=top_k).items}

    return neo4j_vector_search
