from typing import Any, Callable, Coroutine, Dict

import pytest
from langsmith import Client

from agent.components.state import InputState


@pytest.mark.asyncio
async def test_guardrails_routing(
    langsmith_client: Client,
    guardrails_node: Callable[[InputState], Coroutine[Any, Any, Dict[str, Any]]],
    guardrails_langsmith_dataset_name: str,
    validate_guardrails: Callable[[Any], bool],
) -> None:
    await langsmith_client.aevaluate(
        guardrails_node,  # type: ignore[arg-type]
        data=guardrails_langsmith_dataset_name,
        evaluators=[validate_guardrails],  # type: ignore[list-item]
        experiment_prefix="guardrails",
        max_concurrency=2,
    )
