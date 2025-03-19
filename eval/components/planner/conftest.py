from typing import Any, Callable, Coroutine, Dict, List

import evaluate
import pytest
from langchain_openai import ChatOpenAI

from agent.components.planner import create_planner_node
from agent.components.state import InputState


@pytest.fixture(scope="module")
def planner_node(
    llm_openai_gpt_4o: ChatOpenAI,
) -> Callable[[InputState], Coroutine[Any, Any, Dict[str, Any]]]:
    return create_planner_node(llm=llm_openai_gpt_4o)


@pytest.fixture(scope="module")
def planner_langsmith_dataset_name() -> str:
    return "Planner Dataset"


@pytest.fixture(scope="function")
def validate_planner_task_count() -> Callable[[Dict[str, Any], Dict[str, Any]], bool]:
    def _validate_planner_task_count(
        outputs: Dict[str, Any], reference_outputs: Dict[str, Any]
    ) -> bool:
        """Evaluate whether the response contains the same number of tasks as the reference."""
        return len(outputs["response"]) == len(reference_outputs["answer"])

    return _validate_planner_task_count


@pytest.fixture(scope="function")
def validate_planner_task_rouge() -> (
    Callable[[Dict[str, Any], Dict[str, Any]], List[Dict[str, float]]]
):
    def _validate_planner_task_rouge(
        outputs: Dict[str, Any], reference_outputs: Dict[str, Any]
    ) -> List[Dict[str, float]]:
        """Evaluate the response using ROUGE metric.

        Returns
        -------
        ROUGE-1
        ROUGE-2
        ROUGE-L
        ROUGE-LSUM
        """

        rouge = evaluate.load("rouge")

        output_tasks = ["\n".join(outputs["response"])]
        ref_tasks = ["\n".join(reference_outputs["answer"])]

        scores = rouge.compute(predictions=output_tasks, references=ref_tasks)
        return [{"key": k, "score": v} for k, v in scores.items()]

    return _validate_planner_task_rouge
