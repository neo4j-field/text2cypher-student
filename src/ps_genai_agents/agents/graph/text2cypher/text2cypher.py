import json
import os
from typing import Any, Dict, List, Optional, Union

from langchain.agents import (
    AgentExecutor,
    create_openai_tools_agent,
)
from langchain.tools import tool
from langchain_core.agents import AgentAction
from langchain_core.runnables.base import Runnable

# from services.llms import get_openai_chat_llm
# from neo4j_genai.llm import OpenAILLM
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation
from neo4j import GraphDatabase
from neo4j_graphrag.schema import get_schema

from ....prompts import (
    create_agent_prompt,
    create_cypher_prompt,
    create_final_summary_prompt_without_lists,
)

# from tools import (
#     final_answer_tool,
#     get_openai_neo4j_vector_search_tool,
#     get_openai_text2cypher_tool,
# )
from ....tools import create_neo4j_text2cypher_tool

# from agents import create_gpt_4o_tools_agent
# from chains import get_cypher_chain, get_vector_chain
# from database import get_neo4j_graph, get_neo4j_vectorstore
from .state import AgentState
from .types.response import Response

# chat_llm = OpenAILLM(model_name="gpt-4o")
chat_llm = ChatOpenAI(model="gpt-4o")
driver = GraphDatabase.driver(
    uri=os.environ.get("NEO4J_URI", ""),
    auth=(os.environ.get("NEO4J_USERNAME"), os.environ.get("NEO4J_PASSWORD")),
)

# neo4j_vector_search = get_openai_neo4j_vector_search_tool()
# text2cypher = get_openai_text2cypher_tool()

# tools = [neo4j_vector_search, text2cypher]
text2cypher_prompt = create_cypher_prompt(
    graph_schema=get_schema(driver=driver),
    examples_yaml_path="../data/iqs/queries/queries.yml",
)

text2cypher_tool = create_neo4j_text2cypher_tool(
    driver=driver, llm=chat_llm, custom_prompt=text2cypher_prompt
)
tools = [text2cypher_tool]

# agent_runnable = create_gpt_4o_tools_agent(chat_llm=chat_llm, tools=tools)
agent_prompt = create_agent_prompt()
agent_runnable = create_openai_tools_agent(
    prompt=agent_prompt, llm=chat_llm, tools=tools
)
# text2cypher_agent_runnable = create_gpt_4o_tools_agent(
#     chat_llm=chat_llm, tools=[text2cypher]
# )


# def get_sources(tool_execution_result: Dict[str, Any]) -> List[str]:
#     if "source_documents" not in tool_execution_result:
#         return []

#     return [doc.metadata["source"] for doc in tool_execution_result["source_documents"]]


# -----------
# NODES
# -----------


# This a helper class we have that is useful for running tools
# It takes in an agent action and calls that tool and returns the result
tool_executor = ToolExecutor(tools)


# Define the agent
def agent(data: Any) -> Dict[str, Any]:
    print("> run_agent")
    print("initial data: ", data)
    agent_outcome = agent_runnable.invoke(data)
    for x in agent_outcome:
        print(x)
    # print([x.tool_input["query"] for x in agent_outcome])
    return {
        "agent_outcome": agent_outcome,
        "sub_questions": [
            x.tool_input["query"] if not isinstance(x, tuple) else ""
            for x in agent_outcome
        ],
    }


# # Define the function to execute tools
def text2cypher_node(data: Dict[str, Any]) -> Dict[str, Any]:
    # Get the most recent agent_outcome - this is the key added in the `agent` above

    print("> text2cypher node")
    agent_action = data["agent_outcome"]
    print("agent action: ", len(agent_action), agent_action)
    intermediate_steps = list()
    # cypher: List[str] = list()
    # cypher_result: List[str] = list()

    tool_params = agent_action[0].tool_input

    output = execute_text2cypher(tool_params)
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

    print(output)
    print()

    return {
        "agent_outcome": agent_outcome,
        "intermediate_steps": intermediate_steps,
        "cypher": output.get("cypher"),
        "cypher_result": output.get("cypher_result"),
    }


def execute_text2cypher(params: Dict[str, Any]) -> Dict[str, Any]:
    retries: int = 0
    output: Dict[str, Any] = {"result": list()}
    while retries < 2 and not output["result"]:
        print("params: ", params)
        invocation = ToolInvocation(tool="Text2Cypher", tool_input=params)
        # output = tool_executor.invoke(invocation)

        try:
            retries += 1
            output = tool_executor.invoke(invocation)
            print(f"Cypher attempt: {retries}")
        except Exception as e:
            print(f"Cypher generation error on attempt {str(retries)}. Error: {e}")
            output = {"result": list(), "intermediate_steps": [{"query": ""}]}

        if not output["result"]:
            print()
            print("current Cypher query: ", params.get("query"))
            print(output)
            print()
            params["query"] = f"""
The following Cypher is not accurate. Fix the errors and return valid Cypher.
{str(output['intermediate_steps'][-1]['query'])}

Consider the following fixes:
- instead of matching on a property, use fuzzy matching via the CONTAINS operator against the verbatimText property.
- make property must be one word.
- model property must be one word.
"""

    return {
        "intermediate_steps": [{"Text2Cypher", str(output)}],
        "cypher": output["intermediate_steps"][-1]["query"],
        "cypher_result": output["result"],
    }


# def text2cypher_node(data: Any) -> Dict[str, Any]:
#     # Get the most recent agent_outcome - this is the key added in the `agent` above

#     print("> text2cypher_node")
#     agent_action = data["agent_outcome"]
#     tool_call = agent_action[-1].message_log[-1].additional_kwargs["tool_calls"][-1]

#     return execute_text2cypher(query=json.loads(tool_call["function"]["arguments"]))


# Define logic that will be used to determine which conditional edge to go down
def router(data: Dict[str, Any]) -> str:
    print("> router")
    if isinstance(data["agent_outcome"], list):
        next_action = data["agent_outcome"][0]
        if isinstance(next_action, AgentAction):
            return str(next_action.tool)
        elif isinstance(next_action, str):
            return next_action
    return "error"


# this forced final_answer LLM call will be used to structure output from our
# RAG endpoint
def final_answer(data: Any) -> Dict[str, Any]:
    print("> final_answer")
    query = data["input"]
    print(data)
    most_recent_tool = data["agent_outcome"][-1].tool
    tool_execution_result = create_tool_execution_result(data)

    prompt = create_final_summary_prompt_without_lists(
        tool_execution_result=tool_execution_result, question=query
    )

    out = chat_llm.invoke(prompt)

    res_temp = {
        "used_tool": most_recent_tool,
        "answer": out.content,
        "cypher": data["cypher"] if "cypher" in data else None,
        "cypher_result": data["cypher_result"] if "cypher_result" in data else None,
        "question": query,
        "sub_questions": data["sub_questions"] if "sub_questions" in data else None,
    }
    # print("res_temp: ", res_temp)
    return {"agent_outcome": Response(**res_temp)}


def create_tool_execution_result(data: Any) -> List[str]:
    """
    Create the final tool execution results into a single entry
    for final evaluation by LLM.
    """

    cypher: List[str] = data["cypher_result"] if "cypher_result" in data else list()
    vector: List[str] = (
        data["vector_search_result"] if "vector_search_result" in data else list()
    )

    if not cypher:
        return vector
    elif isinstance(vector, str) and cypher:
        return cypher + [vector]
    elif isinstance(vector, list) and cypher:
        return cypher + vector
    else:
        return cypher


# we use the same forced final_answer LLM call to handle incorrectly formatted
# output from our query_agent
def handle_error(data: Any) -> Dict[str, Response]:
    print("> handle_error")
    query = data["input"]
    print(data)
    tool_execution_result = create_tool_execution_result(data)

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
    res_temp = {
        "answer": out,
        "sources": data["sources"] if "sources" in data else None,
        "vector_search_result": (
            data["vector_search_result"] if "vector_search_result" in data else None
        ),
        "cypher": data["cypher"] if "cypher" in data else None,
        "cypher_result": data["cypher_result"] if "cypher_result" in data else None,
        "question": query,
    }
    return {"agent_outcome": Response(**res_temp)}


def create_text2cypher_graph_agent() -> Runnable:
    """
    Create a Text2Cypher LangGraph agent using the OpenAI GPT-4o LLM.

    Returns
    -------
    Runnable
        The graph agent.
    """

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent)
    workflow.add_node("text2cypher", text2cypher_node)
    workflow.add_node("error", handle_error)
    workflow.add_node("final_answer", final_answer)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        router,
        {
            "Text2Cypher": "text2cypher",
            "error": "error",
        },
    )
    workflow.add_conditional_edges(
        "text2cypher",
        router,
        {
            "Text2Cypher": "text2cypher",
            "error": "error",
            "final_answer": "final_answer",
        },
    )

    workflow.add_edge("error", END)
    workflow.add_edge("final_answer", END)

    return workflow.compile()
