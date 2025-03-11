from langsmith import Client

client = Client()

DATASET_NAME = "Planner Dataset"

examples = [
    ("How many books are in the database?", ["How many books are in the database?"]),
    (
        "How many books are there and what is the most common author name?",
        ["How many books are there?", "What is the most common author name?"],
    ),
    (
        "Summarize the responses under fcd10 for honda pilot. What is the men to women proportion for these responses and what is the problem for fcd10?",
        [
            "Summarize the responses under fcd10 for Honda Pilot.",
            "What is the men to women proportion for the fcd10 Honda Pilot responses?",
            "What is the problem for fcd10?",
        ],
    ),
    (
        "What are some easy recipes I can make? Also can you share how many ingredients you know about?",
        ["What are some easy recipes?", "How many ingredients are there?"],
    ),
    (
        "What are recipes that are vegan? Are there any that are quick to make?",
        ["What are some quick vegan recipes?"],
    ),
]

inputs = [{"question": input_prompt} for input_prompt, _ in examples]
outputs = [{"answer": output_answer} for _, output_answer in examples]

# Programmatically create a dataset in LangSmith
if not client.has_dataset(dataset_name=DATASET_NAME):
    client.create_dataset(
        dataset_name=DATASET_NAME,
        description="A planner must take an input question and return the individual indepenedent tasks within.",
    )

    # Add examples to the dataset
    client.create_examples(inputs=inputs, outputs=outputs, dataset_name=DATASET_NAME)
else:
    print(f"Dataset {DATASET_NAME} already exists.")
