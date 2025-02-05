"""
This file contains classes that manage the state of a Text2Cypher Agent or subgraph.
"""

from operator import add
from typing import Annotated, Any, Dict, List

from typing_extensions import TypedDict


class CypherInputState(TypedDict):
    subquestion: str


class CypherState(TypedDict):
    subquestion: str
    statement: str
    errors: List[str]
    records: List[Dict[str, Any]]
    next_action_cypher: str
    attempts: int
    steps: Annotated[List[str], add]


class CypherOutputState(TypedDict):
    subquestion: str
    statement: str
    errors: List[str]
    records: List[Dict[str, Any]]
    steps: List[str]
