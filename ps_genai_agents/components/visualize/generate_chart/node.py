from typing import Any, Callable, Dict

import pandas as pd

from ....components.state import VisualizationState
from ....components.visualize.generate_chart.charts import (
    create_bar_plot,
    create_empty_plot,
    create_line_plot,
    create_scatter_plot,
)


def create_chart_generation_node() -> Callable[[VisualizationState], Dict[str, Any]]:
    """
    Create a chart generation node for a LangGraph workflow.

    Returns
    -------
    Callable[[VisualizationState], OverallState]
        The LangGraph node.
    """

    def generate_chart(state: VisualizationState) -> Dict[str, Any]:
        """
        Generate a chart based on the provided chart details.
        """

        viz_args = {
            "data": pd.DataFrame(state.get("records")),
            "x": state.get("x_axis_key"),
            "y": state.get("y_axis_key"),
            "hue": state.get("hue_key"),
        }
        match state.get("chart_type"):
            case "scatter":
                chart = create_scatter_plot(**viz_args)
            case "line":
                chart = create_line_plot(**viz_args)
            case "bar":
                chart = create_bar_plot(**viz_args)
            case _:
                chart = create_empty_plot()

        steps = state.get("steps", list())
        steps.append("generate_chart")

        return {
            "visualizations": [
                {
                    "subquestion": state.get("subquestion"),
                    "chart": chart,
                    "chart_description": state.get("chart_description"),
                    "steps": steps,
                }
            ],
            "steps": steps,
        }

    return generate_chart
