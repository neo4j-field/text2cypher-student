"""LangGraph edges that are used in multiple workflows."""

from typing import List, Literal

from langgraph.types import Send

from ..components.state import (
    CypherState,
    OverallState,
)


def guardrails_conditional_edge(
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


def tool_select_conditional_edge(
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
        try:
            cypher_state: CypherState = state.get("cyphers", list())[idx]
        except Exception as e:
            continue
        task = Send(
            "visualize",
            {
                "subquestion": cypher_state.get("subquestion"),
                "records": cypher_state.get("records"),
            },
        )
        tasks.append(task)

    return tasks or [Send("gather_visualizations", state)]
