from typing import List, Literal, Optional

from langchain_core.language_models import BaseChatModel
from langchain_neo4j import Neo4jGraph
from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.types import Send

from .components.final_answer import create_final_answer_node
from .components.gather_cypher import create_gather_cypher_node
from .components.guardrails import create_guardrails_node
from .components.query_parser import create_query_parser_node
from .components.state import (
    CypherState,
    InputState,
    OutputState,
    OverallState,
    VisualizationState,
)
from .components.summarize import create_summarization_node
from .components.text2cypher import (
    create_text2cypher_correction_node,
    create_text2cypher_execution_node,
    create_text2cypher_generation_node,
    create_text2cypher_validation_node,
)
from .components.tool_selection import create_tool_selection_node
from .components.visualize import (
    create_chart_details_node,
    create_chart_generation_node,
    create_correct_chart_details_node,
    create_validate_chart_details_node,
)


def create_simple_text2cypher_agent(
    llm: BaseChatModel, graph: Neo4jGraph, cypher_query_yaml_file_path: str = "./"
) -> CompiledStateGraph:
    """
    Create a Text2Cypher Agent workflow using LangGraph.
    This workflow contains only Text2cypher components with no guardrails, query parser or summarizer.

    Returns
    -------
    CompiledStateGraph
        The workflow.
    """

    generate_cypher = create_text2cypher_generation_node(
        llm=llm, graph=graph, cypher_query_yaml_file_path=cypher_query_yaml_file_path
    )
    validate_cypher = create_text2cypher_validation_node(llm=llm, graph=graph)
    correct_cypher = create_text2cypher_correction_node(llm=llm, graph=graph)
    execute_cypher = create_text2cypher_execution_node(graph=graph)

    text2cypher_graph_builder = StateGraph(
        CypherState, input=CypherState, output=OverallState
    )
    text2cypher_graph_builder.add_node(generate_cypher)
    text2cypher_graph_builder.add_node(validate_cypher)
    text2cypher_graph_builder.add_node(correct_cypher)
    text2cypher_graph_builder.add_node(execute_cypher)

    text2cypher_graph_builder.add_edge(START, "generate_cypher")
    text2cypher_graph_builder.add_edge("generate_cypher", "validate_cypher")
    text2cypher_graph_builder.add_conditional_edges(
        "validate_cypher",
        validate_cypher_condition,
    )
    text2cypher_graph_builder.add_edge("correct_cypher", "validate_cypher")
    text2cypher_graph_builder.add_edge("execute_cypher", END)

    return text2cypher_graph_builder.compile()


def create_text2cypher_with_visualization_agent(
    llm: BaseChatModel,
    graph: Neo4jGraph,
    scope_description: Optional[str] = None,
    cypher_query_yaml_file_path: str = "./",
) -> CompiledStateGraph:
    """
    Create a Text2Cypher Agent workflow with visualization capabilities using LangGraph.

    Returns
    -------
    CompiledStateGraph
        The workflow.
    """

    guardrails = create_guardrails_node(
        llm=llm, graph=graph, scope_description=scope_description
    )
    query_parser = create_query_parser_node(llm=llm)
    text2cypher = create_simple_text2cypher_agent(
        llm=llm, graph=graph, cypher_query_yaml_file_path=cypher_query_yaml_file_path
    )
    gather_cypher = create_gather_cypher_node()
    tool_select = create_tool_selection_node(llm=llm)
    visualize = create_visualization_agent(llm=llm)
    summarize = create_summarization_node(llm=llm)
    final_answer = create_final_answer_node()

    main_graph_builder = StateGraph(OverallState, input=InputState, output=OutputState)

    main_graph_builder.add_node(guardrails)
    main_graph_builder.add_node(query_parser)
    main_graph_builder.add_node("text2cypher", text2cypher)
    main_graph_builder.add_node(gather_cypher)
    main_graph_builder.add_node(tool_select)
    main_graph_builder.add_node("visualize", visualize)
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
    main_graph_builder.add_conditional_edges(
        "gather_cypher", viz_mapper_edge, ["visualize", "tool_select"]
    )
    main_graph_builder.add_conditional_edges("tool_select", tool_select_condition)
    main_graph_builder.add_edge("summarize", "tool_select")
    main_graph_builder.add_edge("visualize", "tool_select")
    main_graph_builder.add_edge("final_answer", END)

    return main_graph_builder.compile()


def create_visualization_agent(llm: BaseChatModel) -> CompiledStateGraph:
    """
    Create a visualization Agent workflow using LangGraph.

    Returns
    -------
    CompiledStateGraph
        The workflow.
    """

    generate_chart_details = create_chart_details_node(llm=llm)
    validate_chart_details = create_validate_chart_details_node()
    correct_chart_details = create_correct_chart_details_node(llm=llm)
    generate_chart = create_chart_generation_node()

    g_builder = StateGraph(VisualizationState, output=OverallState)
    g_builder.add_node(generate_chart_details)
    g_builder.add_node(validate_chart_details)
    g_builder.add_node(correct_chart_details)
    g_builder.add_node(generate_chart)

    g_builder.add_edge(START, "generate_chart_details")
    g_builder.add_edge("generate_chart_details", "validate_chart_details")
    g_builder.add_edge("correct_chart_details", "validate_chart_details")
    g_builder.add_conditional_edges(
        "validate_chart_details", validate_chart_details_conditional_edge
    )
    g_builder.add_edge("generate_chart", END)

    return g_builder.compile()


def validate_chart_details_conditional_edge(
    state: VisualizationState,
) -> Literal["correct_chart_details", "generate_chart", "__end__"]:
    match state.get("next_action_visualization"):
        case "correct_chart_details":
            return "correct_chart_details"
        case "generate_chart":
            return "generate_chart"
        case "__end__":
            return "__end__"
        case _:
            return "__end__"


def validate_cypher_condition(
    state: CypherState,
) -> Literal["correct_cypher", "execute_cypher", "__end__"]:
    match state.get("next_action_cypher"):
        case "correct_cypher":
            return "correct_cypher"
        case "execute_cypher":
            return "execute_cypher"
        case "__end__":
            return "__end__"
        case _:
            return "__end__"


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


def viz_mapper_edge(state: OverallState) -> List[Send]:
    """Map each sub question to a Visualize subgraph if a visual is required."""

    indexes = [
        idx
        for idx, subquestion in enumerate(state.get("subquestions", []))
        if subquestion.requires_visualization
    ]
    tasks = list()

    for idx in indexes:
        cypher_state: CypherState = state.get("cyphers", list())[idx]
        task = Send(
            "visualize",
            {
                "subquestion": cypher_state.get("subquestion"),
                "records": cypher_state.get("records"),
            },
        )
        tasks.append(task)

    return tasks or [Send("tool_select", state)]
