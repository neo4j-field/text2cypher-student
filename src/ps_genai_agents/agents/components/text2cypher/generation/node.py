"""
This code is based on content found in the LangGraph documentation: https://python.langchain.com/docs/tutorials/graph/#advanced-implementation-with-langgraph
"""

from typing import Callable

from agents.components.state import CypherState
from agents.components.text2cypher.generation.prompts import (
    create_text2cypher_generation_prompt_template,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_neo4j import Neo4jGraph
from queries.queries import get_example_queries

generation_prompt = create_text2cypher_generation_prompt_template()


def create_text2cypher_generation_node(
    llm: BaseChatModel, graph: Neo4jGraph
) -> Callable[[CypherState], CypherState]:
    text2cypher_chain = generation_prompt | llm | StrOutputParser()

    def generate_cypher(state: CypherState) -> CypherState:
        """
        Generates a cypher statement based on the provided schema and user input
        """

        NL = "\n"
        fewshot_examples = (NL * 2).join(
            [
                f"Question: {el['human']}{NL}Cypher:{el['assistant']}"
                for el in get_example_queries("queries/queries.yaml")
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
