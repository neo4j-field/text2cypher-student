from langchain import hub
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_agent_prompt() -> ChatPromptTemplate:
    """
    Create the base prompt template for an agent.

    Returns
    -------
    ChatPromptTemplate
        The prompt template.
    """

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
          You are a human assistant and you can retrieve survey response information from Neo4j.
          Use your tools to answer questions.
          If you do not have a tool to answer the question, say so.
          If an ID is present in the query, use Text2Cypher.
          Do not generate Cypher unless it is via the Text2Cypher tool!
          """,
            ),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )


def get_openai_functions_agent_prompt() -> str:
    return str(hub.pull("hwchase17/openai-tools-agent"))
