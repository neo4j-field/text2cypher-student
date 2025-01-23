import os

from langchain.graphs import Neo4jGraph
from streamlit import session_state as ss
from streamlit import sidebar as sb

from src.ps_genai_agents.agents.graph import create_text2cypher_graph_agent

from .questions import get_demo_questions, get_examples_location


def sidebar() -> None:
    """
    The Streamlit app side bar.
    """

    source = sb.radio("Data Source", options=["IQS", "Patient Journey"])
    if source != ss["source"]:
        ss["source"] = source
        if source == "IQS":
            ss["graph"] = Neo4jGraph(
                url=os.environ.get("IQS_NEO4J_URI"),
                username=os.environ.get("IQS_NEO4J_USERNAME"),
                password=os.environ.get("IQS_NEO4J_PASSWORD"),
                enhanced_schema=True,
                driver_config={"liveness_check_timeout": 0},
            )
        else:
            ss["graph"] = Neo4jGraph(
                url=os.environ.get("PJ_NEO4J_URI"),
                username=os.environ.get("PJ_NEO4J_USERNAME"),
                password=os.environ.get("PJ_NEO4J_PASSWORD"),
                enhanced_schema=True,
                driver_config={"liveness_check_timeout": 0},
            )
        ss["agent"] = create_text2cypher_graph_agent(
            chat_llm=ss["llm"],
            neo4j_graph=ss["graph"],
            example_queries_location=get_examples_location(source=source),
        )

    demo_questions = get_demo_questions(source=ss["source"])

    sb.title("Demo Questions")
    with sb.expander("Demo Questions"):
        for ex in demo_questions:
            if sb.button(label=ex, key=ex):
                ss.current_question = ex

    sb.divider()
    if len(ss.messages) > 0:
        if sb.button("Reset Chat", type="primary"):
            ss.messages = list()
            del ss.current_question
