from typing import Any, Callable, Coroutine, Dict, List

import pytest
from langsmith import Client

from ps_genai_agents.components.state import InputState


@pytest.mark.asyncio
async def test_planner_task_generation(
    langsmith_client: Client,
    planner_node: Callable[[InputState], Coroutine[Any, Any, Dict[str, Any]]],
    planner_langsmith_dataset_name: str,
    validate_planner_task_count: Callable[[Any], bool],
    validate_planner_task_rouge: Callable[
        [Dict[str, List[str]]], List[Dict[str, float]]
    ],
) -> None:
    async def planner_node_with_task_list_output(
        state: InputState,
    ) -> Dict[str, List[str]]:
        res = await planner_node(state)
        return {"response": [t.question for t in res.get("tasks", list())]}

    await langsmith_client.aevaluate(
        planner_node_with_task_list_output,  # type: ignore
        data=planner_langsmith_dataset_name,
        evaluators=[validate_planner_task_count, validate_planner_task_rouge],  # type: ignore[list-item]
        experiment_prefix="planner-task-generation",
        max_concurrency=2,
    )
