from typing import List, Literal, Optional

from langchain_core.language_models import BaseChatModel
from langchain_neo4j import Neo4jGraph
from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.types import Send

from ..agents import create_text2cypher_agent
from ..components.final_answer import create_final_answer_node
from ..components.gather_cypher import create_gather_cypher_node
from ..components.guardrails import create_guardrails_node
from ..components.query_parser import create_query_parser_node
from ..components.state import (
    InputState,
    OutputState,
    OverallState,
)
from ..components.summarize import create_summarization_node
from ..components.tool_selection import create_tool_selection_node


def create_text2cypher_workflow(
    llm: BaseChatModel,
    graph: Neo4jGraph,
    scope_description: Optional[str] = None,
    cypher_query_yaml_file_path: str = "./",
) -> CompiledStateGraph:
    """
    Create a Text2Cypher Agent workflow using LangGraph.
    This workflow expands upon the Text2Cypher agent with guardrails, a query parser, individual subquery processing and summarization.

    Returns
    -------
    CompiledStateGraph
        The workflow.
    """

    guardrails = create_guardrails_node(
        llm=llm, graph=graph, scope_description=scope_description
    )
    query_parser = create_query_parser_node(llm=llm)
    text2cypher = create_text2cypher_agent(
        llm=llm, graph=graph, cypher_query_yaml_file_path=cypher_query_yaml_file_path
    )
    gather_cypher = create_gather_cypher_node()
    tool_select = create_tool_selection_node(llm=llm)
    summarize = create_summarization_node(llm=llm)
    final_answer = create_final_answer_node()

    main_graph_builder = StateGraph(OverallState, input=InputState, output=OutputState)

    main_graph_builder.add_node(guardrails)
    main_graph_builder.add_node(query_parser)
    main_graph_builder.add_node("text2cypher", text2cypher)
    main_graph_builder.add_node(gather_cypher)
    main_graph_builder.add_node(tool_select)
    main_graph_builder.add_node(summarize)
    main_graph_builder.add_node(final_answer)

    main_graph_builder.add_edge(START, "guardrails")
    main_graph_builder.add_conditional_edges(
        "guardrails",
        guardrails_condition,
    )
    main_graph_builder.add_conditional_edges(
        "query_parser", query_mapper_edge, ["text2cypher"]
    )
    main_graph_builder.add_edge("text2cypher", "gather_cypher")
    main_graph_builder.add_edge("gather_cypher", "tool_select")
    main_graph_builder.add_conditional_edges("tool_select", tool_select_condition)
    main_graph_builder.add_edge("summarize", "tool_select")
    main_graph_builder.add_edge("final_answer", END)

    return main_graph_builder.compile()


def guardrails_condition(
    state: OverallState,
) -> Literal["query_parser", "final_answer"]:
    match state.get("next_action"):
        case "final_answer":
            return "final_answer"
        case "end":
            return "final_answer"
        case "query_parser":
            return "query_parser"
        case _:
            return "final_answer"


def tool_select_condition(
    state: OverallState,
) -> Literal["summarize", "final_answer"]:
    match state.get("next_action"):
        case "summarize":
            return "summarize"
        case "final_answer":
            return "final_answer"
        case _:
            return "final_answer"


def query_mapper_edge(state: OverallState) -> List[Send]:
    """Map each sub question to a Text2Cypher subgraph."""

    return [
        Send("text2cypher", {"subquestion": question.subquestion})
        for question in state.get("subquestions", list())
    ]
