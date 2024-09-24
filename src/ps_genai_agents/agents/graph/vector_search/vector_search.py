import json
import os
from typing import Any, Dict, Union

import neo4j
from langchain.agents import (
    create_openai_tools_agent,
)
from langchain_core.agents import AgentAction
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation
from neo4j import GraphDatabase
from neo4j_genai.embeddings.openai import OpenAIEmbeddings
from neo4j_genai.types import RetrieverResultItem

from ....prompts import (
    create_agent_prompt,
    create_final_summary_prompt_without_lists,
)
from ....tools import create_neo4j_vector_search_tool
from .state import AgentState
from .types.response import Response

chat_llm = ChatOpenAI(model="gpt-4o")
embedder = OpenAIEmbeddings()
driver = GraphDatabase.driver(
    uri=os.environ.get("NEO4J_URI", ""),
    auth=(os.environ.get("NEO4J_USERNAME"), os.environ.get("NEO4J_PASSWORD")),
)


INDEX_NAME = "adaEmbeddings"


def custom_record_formatter(record: neo4j.Record) -> RetrieverResultItem:
    """
    Format the returned result from Neo4j.
    """
    metadata = {
        "score": record.get("score"),
        "id": record.get("node").get("id"),
    }
    node = record.get("node")
    return RetrieverResultItem(
        content=str(node),
        metadata=metadata,
    )


vector_search_tool = create_neo4j_vector_search_tool(
    driver=driver,
    embedder=embedder,
    index_name=INDEX_NAME,
    return_properties=["id", "verbatim"],
    result_formatter=custom_record_formatter,
)

tools = [vector_search_tool]
tool_executor = ToolExecutor(tools)

agent_prompt = create_agent_prompt()
agent_runnable = create_openai_tools_agent(
    prompt=agent_prompt, llm=chat_llm, tools=tools
)


# -----------
# NODES
# -----------


def run_agent(data: Dict[str, Any]) -> Dict[str, Any]:
    print("> run_agent")
    print("initial data: ", data)
    agent_outcome = agent_runnable.invoke(data)
    for x in agent_outcome:
        print(x)
    return {
        "agent_outcome": agent_outcome,
        "sub_questions": [
            x.tool_input["query"] if not isinstance(x, tuple) else tuple()
        ],
    }


def vector_search_node(data: Dict[str, Any]) -> Dict[str, Any]:
    print("> vector search node")
    agent_action = data["agent_outcome"]
    print("agent action: ", len(agent_action), agent_action)
    intermediate_steps = []
    tool_params = agent_action[0].tool_input

    output = execute_vector_search(tool_params)
    intermediate_steps.append(output["intermediate_steps"][0])
    agent_outcome = (
        agent_action[1:]
        if len(agent_action) > 1
        else [
            AgentAction(
                tool="final_answer",
                tool_input="",
                log="No more actions to perform. Moving to summarization step.",
            )
        ]
    )
    return {
        "agent_outcome": agent_outcome,
        "intermediate_steps": intermediate_steps,
        "sources": output.get("sources"),
        "context": output.get("context"),
    }


def execute_vector_search(params: Dict[str, Any]) -> Dict[str, Any]:
    invocation = ToolInvocation(tool="Neo4jVectorSearch", tool_input=params)
    output = tool_executor.invoke(invocation)

    return {
        "intermediate_steps": [{"Neo4jVectorSearch", str(output)}],
        "sources": [x.metadata.get("id") for x in output["result"]],
        "context": [x.content for x in output["result"]],
    }


def router(data: Dict[str, Any]) -> str:
    print("> router")
    if isinstance(data["agent_outcome"], list):
        next_action = data["agent_outcome"][0]
        if isinstance(next_action, AgentAction):
            return str(next_action.tool)
        elif isinstance(next_action, str):
            return next_action
    return "error"


def final_answer(data: Dict[str, Any]) -> Dict[str, Any]:
    print("> final_answer")
    query = data["input"]
    print(data)
    most_recent_tool = data["agent_outcome"][-1].tool
    tool_execution_result = data.get("context", "")

    prompt = create_final_summary_prompt_without_lists(
        tool_execution_result=tool_execution_result, question=query
    )

    out = chat_llm.invoke(prompt)

    res_temp = {
        "used_tool": most_recent_tool,
        "answer": out.content,
        "sources": data["sources"] if "sources" in data else None,
        "context": (data["context"] if "context" in data else None),
        "question": query,
        "sub_questions": data["sub_questions"] if "sub_questions" in data else None,
    }
    return {"agent_outcome": Response(**res_temp)}


def handle_error(data: Dict[str, Any]) -> Dict[str, Any]:
    print("> handle_error")
    query = data["input"]
    print(data)
    tool_execution_result = data.get("context", "")

    prompt: Union[str, None] = (
        create_final_summary_prompt_without_lists(
            tool_execution_result=tool_execution_result, question=query
        )
        if tool_execution_result
        else None
    )

    error_response = f"The agent is unable to answer the question: {query}"

    out = chat_llm.invoke(prompt).content if prompt else error_response
    print(out)
    response_params = {
        "answer": out,
        "sources": data.get("sources"),
        "context": data.get("context"),
        "question": query,
    }
    return {"agent_outcome": Response(**response_params)}


# -----------
# WORKFLOW
# -----------


def create_vector_search_graph_agent() -> CompiledGraph:
    """
    Create a Hybrid LangGraph agent using the OpenAI GPT-4o LLM.
    Tools include only Neo4jVectorSearch.

    Returns
    -------
    Runnable
        The graph agent.
    """

    # Define a new graph
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", run_agent)
    workflow.add_node("vector_search", vector_search_node)
    workflow.add_node("error", handle_error)
    workflow.add_node("final_answer", final_answer)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        router,
        {
            "Neo4jVectorSearch": "vector_search",
            "error": "error",
        },
    )
    workflow.add_conditional_edges(
        "vector_search",
        router,
        {
            "Neo4jVectorSearch": "vector_search",
            "error": "error",
            "final_answer": "final_answer",
        },
    )
    # workflow.add_edge("vector_search", "final_answer")
    workflow.add_edge("error", END)
    workflow.add_edge("final_answer", END)

    return workflow.compile()
