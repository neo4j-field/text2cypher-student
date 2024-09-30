import os

import streamlit as st
from langchain.graphs import Neo4jGraph
from langchain_openai.chat_models import ChatOpenAI
from streamlit import session_state as ss

from components import chat, display_chat_history, sidebar
from src.ps_genai_agents.agents.graph import create_text2cypher_graph_agent


def initialize_state() -> None:
    """
    Initialize the application state.
    """

    if "agent" not in ss:
        ss["llm"] = ChatOpenAI(model="gpt-4o")
        ss["graph"] = Neo4jGraph(
            url=os.environ.get("IQS_NEO4J_URI"),
            username=os.environ.get("IQS_NEO4J_USERNAME"),
            password=os.environ.get("IQS_NEO4J_PASSWORD"),
            enhanced_schema=True,
            driver_config={"liveness_check_timeout": 0},
        )
        ss["agent"] = create_text2cypher_graph_agent(
            chat_llm=ss["llm"], neo4j_graph=ss["graph"],
            example_queries_location="data/iqs/queries/queries.yml"
        )
        ss["messages"] = list()
        ss["source"] = "IQS"


def run_app():
    """
    Run the Streamlit application.
    """

    st.title("PS GenAI Retreat Workshop")
    sidebar()
    display_chat_history()
    # Prompt for user input and save and display
    if question := st.chat_input():
        ss["current_question"] = question

    if "current_question" in ss:
        chat(ss.current_question)


if __name__ == "__main__":
    initialize_state()
    run_app()
