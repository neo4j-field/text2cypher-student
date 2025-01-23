import os

import streamlit as st
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI

from ps_genai_agents.ui.components import chat, display_chat_history, sidebar
from ps_genai_agents.workflows import create_text2cypher_with_visualization_workflow


def initialize_state() -> None:
    """
    Initialize the application state.
    """

    if "agent" not in st.session_state:
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
            cypher_query_yaml_file_path="data/iqs/queries/queries.yml",
            scope_description="This application may answer questions related to customer feedback on Honda vehicles.",
            max_cypher_generation_attempts=3,
            attempt_cypher_execution_on_final_attempt=True,
            llm_cypher_validation=False,
        )
        st.session_state["messages"] = list()
        st.session_state["source"] = "IQS"


def run_app() -> None:
    """
    Run the Streamlit application.
    """

    st.title("PS GenAI Retreat Workshop")
    sidebar()
    display_chat_history()
    # Prompt for user input and save and display
    if question := st.chat_input():
        st.session_state["current_question"] = question

    if "current_question" in st.session_state:
        chat(str(st.session_state.get("current_question", "")))


if __name__ == "__main__":
    initialize_state()
    run_app()
