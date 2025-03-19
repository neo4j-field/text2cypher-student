import asyncio
import json
import os
import sys
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI

from agent.retrievers.cypher_examples import YAMLCypherExampleRetriever
from agent.ui.components import chat, display_chat_history, sidebar
from agent.workflows.multi_agent import (
    create_text2cypher_with_visualization_workflow,
)

if load_dotenv():
    print("Env Loaded Successfully!")
else:
    print("Unable to Load Environment.")


def get_args() -> Dict[str, Any]:
    """Parse the command line arguments to configure the application."""

    args = sys.argv
    if len(args) > 1:
        config_path: str = args[1]
        assert config_path.lower().endswith(
            ".json"
        ), f"provided file is not JSON | {config_path}"
        with open(config_path, "r") as f:
            config: Dict[str, Any] = json.load(f)
    else:
        config = dict()

    return config


def initialize_state(
    cypher_query_yaml_file_path: str,
    scope_description: str,
    example_questions: List[str] = list(),
) -> None:
    """
    Initialize the application state.
    """

    if "agent" not in st.session_state:
        cypher_example_retriever = YAMLCypherExampleRetriever(
            cypher_query_yaml_file_path=cypher_query_yaml_file_path
        )
        st.session_state["llm"] = ChatOpenAI(model="gpt-4o", temperature=0.0)
        st.session_state["graph"] = Neo4jGraph(
            url=os.environ.get("NEO4J_URI"),
            username=os.environ.get("NEO4J_USERNAME"),
            password=os.environ.get("NEO4J_PASSWORD"),
            enhanced_schema=True,
            driver_config={"liveness_check_timeout": 0},
        )
        st.session_state["agent"] = create_text2cypher_with_visualization_workflow(
            llm=st.session_state["llm"],
            graph=st.session_state["graph"],
            cypher_example_retriever=cypher_example_retriever,
            scope_description=scope_description,
            max_cypher_generation_attempts=3,
            attempt_cypher_execution_on_final_attempt=True,
            llm_cypher_validation=False,
        )
        st.session_state["messages"] = list()
        st.session_state["example_questions"] = example_questions


async def run_app(title: str = "Neo4j GenAI Demo") -> None:
    """
    Run the Streamlit application.
    """

    st.title(title)
    sidebar()
    display_chat_history()
    # Prompt for user input and save and display
    if question := st.chat_input():
        st.session_state["current_question"] = question

    if "current_question" in st.session_state:
        await chat(str(st.session_state.get("current_question", "")))


if __name__ == "__main__":
    args = get_args()
    initialize_state(
        cypher_query_yaml_file_path=args.get("cypher_query_yaml_file_path", ""),
        scope_description=args.get("scope_description", ""),
        example_questions=args.get("example_questions", list()),
    )
    asyncio.run(run_app(title=args.get("title", "")))
