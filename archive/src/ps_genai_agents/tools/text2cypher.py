"""
This file contains the Text2Cypher tool used in the Agent architecture.
"""

from typing import Any, Callable, Dict, List, Optional

from langchain.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.tools import tool
from neo4j import Driver, Record
from neo4j_graphrag.llm import LLMInterface
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.types import RetrieverResultItem


def create_neo4j_text2cypher_tool(
    driver: Driver,
    llm: LLMInterface,
    schema: Optional[str] = None,
    examples: Optional[List[str]] = None,
    custom_prompt: Optional[str] = None,
    result_formatter: Optional[Callable[[Record], RetrieverResultItem]] = None,
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
    result_formatter : Optional[Callable[[Record], RetrieverResultItem]], optional
        A function that defines how a neo4j.Record should be parsed.

    Returns
    -------
    Callable
        The tool.
    """

    assert (
        (schema is not None and examples is not None) or custom_prompt is not None
    ), "Please provide `schema` and `examples` args or `custom_prompt` arg to `create_neo4j_text2cypher_tool` function."

    retriever = Text2CypherRetriever(
        driver=driver,
        llm=llm,
        neo4j_schema=schema,
        examples=examples,
        custom_prompt=custom_prompt,
        result_formatter=result_formatter,
    )

    @tool("Text2Cypher", return_direct=False)  # type: ignore
    def text2cypher(query: str) -> Dict[str, Any]:
        """
        * Useful for maths and aggregations:
            - Answering questions requiring math
            - Returning lists
            - Aggregation like counting, calculating proportion, scores and totals
        * Use if looking for specific IDs.
        * Use if searching for contents of a Node.
        * Use full question as input.
        """

        result = retriever.search(query_text=query)
        return {
            "result": [x.content.data() for x in result.items],
            "cypher": [result.metadata.get("cypher")],
        }

    return text2cypher


def create_langchain_text2cypher_tool(cypher_chain: GraphCypherQAChain) -> Callable:
    """
    Create a Text2Cypher tool with the provided cypher chain.

    Parameters
    ----------
    cypher_chain : GraphCypherQAChain
        The cypher chain to use.

    Returns
    -------
    Callable
        The tool.
    """

    @tool("Text2Cypher", return_direct=False)
    def text2cypher(query: str) -> Dict[str, Any]:
        """
        * Useful for maths and aggregations:
            - Answering questions requiring math
            - Returning lists
            - Aggregation like counting, calculating proportion, scores and totals
        * Use if looking for specific IDs.
        * Use if searching for contents of a Node.
        * Use full question as input.
        """

        return cypher_chain.invoke(query)

    return text2cypher
