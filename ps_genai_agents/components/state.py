from operator import add
from typing import Annotated, Any, Dict, List, Optional

from pydantic_core import ErrorDetails
from typing_extensions import TypedDict

from ..components.models import SubQuestion


class CypherState(TypedDict):
    subquestion: str
    statement: str
    errors: List[str]
    records: List[Dict[str, Any]]
    next_action_cypher: str
    attempts: int
    steps: Annotated[List[str], add]


class CypherHistoryRecord(TypedDict):
    subquestion: str
    statement: str
    records: List[Dict[str, Any]]


class HistoryRecord(TypedDict):
    """Information that may be relevant to future user questions."""

    question: str
    answer: str
    cyphers: List[CypherHistoryRecord]


def update_history(
    history: List[HistoryRecord], new: List[HistoryRecord]
) -> List[HistoryRecord]:
    """
    Update the history record. Allow only a max number of records to be stored at any time.

    Parameters
    ----------
    history : List[HistoryRecord]
        The current history list.
    new : List[HistoryRecord]
        The new record to add. Should be a single entry list.

    Returns
    -------
    List[HistoryRecord]
        A new List with the record added and old records removed to maintain size.
    """

    SIZE: int = 5

    history.extend(new)
    return history[-SIZE:]


class VisualizationState(TypedDict):
    subquestion: str
    records: List[Dict[str, Any]]
    title: str
    x_axis_key: str
    y_axis_key: str
    hue_key: Optional[str]
    chart_type: str
    chart_description: str
    errors: List[ErrorDetails]
    next_action_visualization: str
    steps: Annotated[List[str], add]


class VisualizationOutputState(TypedDict):
    subquestion: str
    chart: Any
    chart_description: str
    steps: List[str]


class InputState(TypedDict):
    question: str
    history: Annotated[List[HistoryRecord], update_history]


class OverallState(TypedDict):
    question: str
    subquestions: Annotated[List[SubQuestion], add]
    next_action: str
    cyphers: Annotated[List[CypherState], add]
    summary: str
    visualizations: Annotated[List[VisualizationOutputState], add]
    steps: Annotated[List[str], add]
    history: Annotated[List[HistoryRecord], update_history]


class OutputState(TypedDict):
    """The final output."""

    answer: str
    question: str
    steps: List[str]
    cyphers: List[CypherState]
    visualizations: List[VisualizationOutputState]
    history: Annotated[List[HistoryRecord], update_history]
