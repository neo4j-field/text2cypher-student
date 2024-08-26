"""
This file contains the Text2Cypher tool used in the Agent architecture.
"""

from typing import Any, Callable, Dict, List, Optional

from langchain.tools import tool
from neo4j import Driver
from neo4j_genai.llm import LLMInterface
from neo4j_genai.retrievers import Text2CypherRetriever


def create_neo4j_text2cypher_tool(
    driver: Driver,
    llm: LLMInterface,
    schema: Optional[str] = None,
    examples: Optional[List[str]] = None,
    custom_prompt: Optional[str] = None,
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

    assert (
        (schema is not None and examples is not None) or custom_prompt is not None
    ), "Please provide `schema` and `examples` args or `custom_prompt` arg to `create_neo4j_text2cypher_tool` function."

    @tool("Text2Cypher", return_direct=False)  # type: ignore[misc]
    def text2cypher(query: str, top_k: int = 100) -> Dict[str, Any]:
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

        retriever = Text2CypherRetriever(
            driver=driver,
            llm=llm,
            neo4j_schema=schema,
            examples=examples,
            custom_prompt=custom_prompt,
        )
        result = retriever.search(query_text=query, top_k=top_k)
        return {"result": result.items, "cypher": result.metadata.get("cypher")}

    return text2cypher
