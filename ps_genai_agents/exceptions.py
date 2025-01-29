class PSGenAIAgentsError(Exception):
    """Global Exception"""

    ...


class CypherExampleRetrieverError(PSGenAIAgentsError):
    """Exception raised when an error occurs while a Cypher Example Retriever is retrieving examples."""

    ...
