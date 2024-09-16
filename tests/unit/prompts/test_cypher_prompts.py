from src.ps_genai_agents.prompts.cypher_prompts import create_cypher_prompt


def test_create_cypher_prompt_inputs() -> None:
    p = create_cypher_prompt(
        graph_schema="this is my schema.",
        examples_yaml_path="data/iqs/queries/queries.yml",
    )

    final_p = p.format(question="my question.")

    assert "this is my schema." in final_p
    assert "my question." in final_p
