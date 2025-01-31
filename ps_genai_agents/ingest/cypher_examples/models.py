from typing import Dict, List, TypedDict

from pydantic import BaseModel


class CypherIngestRecord(BaseModel):
    cypher_statement: str
    question: str
    question_embedding: List[float]


class EmbedderResult(TypedDict):
    nodes: List[CypherIngestRecord]
    failed: List[Dict[str, str]]
