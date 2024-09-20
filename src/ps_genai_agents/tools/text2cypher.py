"""
This file contains the Text2Cypher tool used in the Agent architecture.
"""

from typing import Any, Callable, Dict, List, Optional

from langchain.tools import tool
from neo4j import Driver
from neo4j_graphrag.llm import LLMInterface
from neo4j_graphrag.retrievers import Text2CypherRetriever


def create_neo4j_text2cypher_tool(
    driver: Driver,
    llm: LLMInterface,
    schema: Optional[str] = None,
    examples: Optional[List[str]] = None,
    custom_prompt: Optional[str] = None,
) -> Any:
    """
    Create a Text2Cypher tool.

    Parameters
    ----------
    driver : Driver
        The Neo4j Python driver instance to use.
    llm : LLMInterface
        The LLM that will generate Cypher to be run against the Neo4j database.
    schema : Optional[str], optional
        The graph schema to provide as context for Cypher generation. By default None
    examples : Optional[str], optional
        Any examples of question and Cypher pairs to provide to the LLM.  By default None
        example : ['Human: How many nodes are there?\\nAssistant: MATCH (n) RETURN COUNT(*)']
    custom_prompt : Optional[str], optional
        A custom prompt to use for Cypher generation. Will overwrite any schema or examples provided.

    Returns
    -------
    Callable
        The tool.
    """

    assert (
        (schema is not None and examples is not None) or custom_prompt is not None
    ), "Please provide `schema` and `examples` args or `custom_prompt` arg to `create_neo4j_text2cypher_tool` function."

    @tool("Text2Cypher", return_direct=False)  # type: ignore[misc]
    def text2cypher(query: str) -> Dict[str, Any]:
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
        result = retriever.search(query_text=query)
        return {"result": result.items, "cypher": result.metadata.get("cypher")}

    return text2cypher
