"""
This code is based on content found in the LangGraph documentation: https://python.langchain.com/docs/tutorials/graph/#advanced-implementation-with-langgraph
"""

from typing import Any, Callable, Dict

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_neo4j import Neo4jGraph

from .....cypher_query_store.yaml_store import get_example_queries_from_yaml
from ....components.state import CypherState
from ....components.text2cypher.generation.prompts import (
    create_text2cypher_generation_prompt_template,
)

generation_prompt = create_text2cypher_generation_prompt_template()


def create_text2cypher_generation_node(
    llm: BaseChatModel, graph: Neo4jGraph, cypher_query_yaml_file_path: str = "./"
) -> Callable[[CypherState], Dict[str, Any]]:
    text2cypher_chain = generation_prompt | llm | StrOutputParser()

    def generate_cypher(state: CypherState) -> Dict[str, Any]:
        """
        Generates a cypher statement based on the provided schema and user input
        """

        NL = "\n"
        fewshot_examples = (NL * 2).join(
            [
                f"Question: {el['human']}{NL}Cypher:{el['assistant']}"
                for el in get_example_queries_from_yaml(cypher_query_yaml_file_path)
            ]
        )
        generated_cypher = text2cypher_chain.invoke(
            {
                "question": state.get("subquestion"),
                "fewshot_examples": fewshot_examples,
                "schema": graph.schema,
            }
        )
        return {"statement": generated_cypher, "steps": ["generate_cypher"]}

    return generate_cypher
