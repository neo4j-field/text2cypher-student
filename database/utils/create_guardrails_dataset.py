from langsmith import Client

client = Client()

DATASET_NAME = "Guardrails Dataset - BBC Recipes"

examples = [
    ("How many trees are in my neighborhood?", "end"),
    ("What are some good insurance rates?", "end"),
    ("Can you help me analyze this supply chain data?", "end"),
    ("What are good use cases for graph databases?", "end"),
    ("What is the meaning of life?", "end"),
    ("How many recipes do you know?", "planner"),
    ("What are some dairy free recipes?", "planner"),
    ("What author has written the most recipes?", "planner"),
    ("What can I make with eggs and milk?", "planner"),
    ("Please recommend a quick dinner.", "planner"),
]

inputs = [{"question": input_prompt} for input_prompt, _ in examples]
outputs = [{"answer": output_answer} for _, output_answer in examples]

# Programmatically create a dataset in LangSmith
if not client.has_dataset(dataset_name=DATASET_NAME):
    client.create_dataset(
        dataset_name=DATASET_NAME,
        description="A guardrail must prevent out of scope questions from progressing in the workflow.",
    )

    # Add examples to the dataset
    client.create_examples(inputs=inputs, outputs=outputs, dataset_name=DATASET_NAME)
else:
    print(f"Dataset {DATASET_NAME} already exists.")
