import os
from typing import Any, Dict, List, Optional, Union

from langchain.agents import (
    create_openai_tools_agent,
)
from langchain.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
from langchain_core.agents import AgentAction
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation

from ....prompts import (
    create_agent_prompt,
    create_final_summary_prompt_without_lists,
    create_graphqa_chain_cypher_prompt,
)
from ....tools import create_langchain_text2cypher_tool
from .state import AgentState
from .types.response import Response


def create_text2cypher_graph_agent(
    chat_llm: Optional[ChatOpenAI] = None, neo4j_graph: Optional[Neo4jGraph] = None, example_queries_location: Optional[str] = None
) -> CompiledGraph:
    """
    Create a Text2Cypher graph agent.

    Parameters
    ----------
    chat_llm : Optional[ChatOpenAI], optional
        The LangChain OpenAI chat LLM to use, by default None
    neo4j_graph : Optional[Neo4jGraph], optional
        The LangChain Neo4jGraph object to use, by default None
    example_queries_location : Optional[str] = None
        The location of the yaml file to use containing example queries, by default None

    Returns
    -------
    CompiledGraph
        The graph agent.
    """

    example_queries_loc = example_queries_location or "data/iqs/queries/queries.yml"

    chat_llm = chat_llm or ChatOpenAI(model="gpt-4o")

    text2cypher_prompt = create_graphqa_chain_cypher_prompt(
        examples_yaml_path=example_queries_loc
    )

    if neo4j_graph is not None:
        graph = neo4j_graph
    else:
        graph = Neo4jGraph(
            url=os.environ.get("NEO4J_URI"),
            username=os.environ.get("NEO4J_USERNAME"),
            password=os.environ.get("NEO4J_PASSWORD"),
            enhanced_schema=True,
            driver_config={"liveness_check_timeout": 0},
        )

    graphqa_chain = GraphCypherQAChain.from_llm(
        chat_llm,
        graph=graph,
        cypher_prompt=text2cypher_prompt,
        return_direct=True,
        Verbose=True,
        return_intermediate_steps=True,
        top_k=100,
    )

    text2cypher_tool = create_langchain_text2cypher_tool(cypher_chain=graphqa_chain)

    tools = [text2cypher_tool]

    agent_prompt = create_agent_prompt()
    agent_runnable = create_openai_tools_agent(
        prompt=agent_prompt, llm=chat_llm, tools=tools
    )

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
        agent_action = data.get("agent_outcome")
        print("agent action: ", len(agent_action), agent_action)
        intermediate_steps = list()

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

            try:
                retries += 1
                output = tool_executor.invoke(invocation)
                print(f"Cypher attempt: {retries}")
            except Exception as e:
                print(f"Cypher generation error on attempt {str(retries)}. Error: {e}")
                output = {
                    "result": list(),
                    "cypher": "",
                    "error": e,
                    "query": params.get("query"),
                }

            if "error" in output:
                params["query"] = f"""
    Cypher generation failed for query:
    {output.get("query", "")}

    Error:
    {output.get("error")}

    Consider the following fixes:
    - instead of matching on a property, use fuzzy matching.
    """
            elif not output["result"]:
                print()
                print("current Cypher query: ", params.get("query"))
                print(output)
                print()
                params["query"] = f"""
    The following Cypher is not accurate. Fix the errors and return valid Cypher.
    {str(output["intermediate_steps"][-1]["query"])}

    Consider the following fixes:
    - instead of matching on a property, use fuzzy matching.
    """

        return {
            "intermediate_steps": [{"Text2Cypher", str(output)}],
            "cypher": [output["intermediate_steps"][-1]["query"]],
            "cypher_result": [output.get("result")],
        }

    # Define logic that will be used to determine which conditional edge to go down
    def router(data: Dict[str, Any]) -> str:
        print("> router")
        if isinstance(data["agent_outcome"], list):
            next_action = data["agent_outcome"][0]
            print("next action: ", next_action)
            if isinstance(next_action, AgentAction):
                print(str(next_action.tool))
                print(data)
                return str(next_action.tool)
            elif isinstance(next_action, str):
                print(data)
                print(next_action)
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

    # Define Graph

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
