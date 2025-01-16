from typing import Any, Callable, Dict

from langchain_core.language_models import BaseChatModel

from ....components.state import VisualizationState
from ....components.visualize.generate_details.models import ChartDetailsOutput
from ....components.visualize.generate_details.prompts import (
    create_chart_details_prompt_template,
)

generate_chart_details_prompt = create_chart_details_prompt_template()


def create_chart_details_node(
    llm: BaseChatModel,
) -> Callable[[VisualizationState], Dict[str, Any]]:
    """
    Create a chart details node for a LangGraph workflow.

    Parameters
    ----------
    llm : BaseChatModel
        The LLM do perform processing.

    Returns
    -------
    Callable[[CypherState], OutputState]
        The LangGraph node.
    """

    chart_details_chain = generate_chart_details_prompt | llm.with_structured_output(
        ChartDetailsOutput
    )

    def generate_chart_details(state: VisualizationState) -> Dict[str, Any]:
        """
        Generate chart details to be used for generating a chart visualization of the data.
        """

        chart_details: ChartDetailsOutput = chart_details_chain.invoke(
            {"question": state.get("subquestion"), "data": state.get("records")}
        )
        return {
            "title": chart_details.title,
            "x_axis_key": chart_details.x_axis_key,
            "y_axis_key": chart_details.y_axis_key,
            "chart_type": chart_details.chart_type,
            "chart_description": chart_details.chart_description,
            "steps": ["generate_chart_details"],
        }

    return generate_chart_details
