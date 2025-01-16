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
    next_action: str
    steps: Annotated[List[str], add]


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


class OverallState(TypedDict):
    question: str
    subquestions: List[SubQuestion]
    next_action: str
    cyphers: Annotated[List[CypherState], add]
    summary: str
    visualizations: Annotated[List[VisualizationOutputState], add]
    steps: Annotated[List[str], add]


class OutputState(TypedDict):
    answer: str
    question: str
    steps: List[str]
    cyphers: List[CypherState]
    visualizations: List[VisualizationOutputState]
