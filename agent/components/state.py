from operator import add
from typing import Annotated, Any, Dict, List

from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from ..components.models import Task
from .text2cypher.state import CypherOutputState


class InputState(TypedDict):
    """The input state for multi agent workflows."""

    question: str
    data: List[Dict[str, Any]]
    messages: Annotated[List[BaseMessage], add]


class OverallState(TypedDict):
    """The main state in multi agent workflows."""

    question: str
    tasks: Annotated[List[Task], add]
    next_action: str
    cyphers: Annotated[List[CypherOutputState], add]
    summary: str
    steps: Annotated[List[Any], add]
    messages: Annotated[List[BaseMessage], add]


class OutputState(TypedDict):
    """The final output for multi agent workflows."""

    answer: str
    question: str
    steps: List[Any]
    cyphers: List[CypherOutputState]
    messages: Annotated[List[BaseMessage], add]


class TaskState(TypedDict):
    """The state of a task."""

    question: str
    parent_task: str
    data: CypherOutputState
