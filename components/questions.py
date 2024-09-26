from typing import List, Literal

iqs_questions = [
    "How many vehicles are there?",
    "Summarize the responses under fcd10 for honda pilot. What is the men to women proportion for these responses and what is the problem for fcd10?",
    "What are the top 5 most severe problems for women aged 30-34 for all Acura models?",
    "Please summarize the verbatims for 2023 RDX for question 010 Trunk/TG Touch-Free Sensor DTU and create categories for the problems. As an output, I want the summary, corresponding categories and their verbatims",
    "What are the top 5 problems about seats for each age buckets for men over the age of 53?",
    "What are the top 5 problems about seats for each age buckets over the age of 53? Summarize the responses for each bucket",
    "What is the customer with the most reported problems? Can you list the problems, summarize them and include the problem id's as well as the customer gender and age range.",
    "Summarize and compare the sentiment for responses related to noise and sound in Honda Accord and Honda Pilot for women and return the number of responses considered.",
    "What color is the sky?",
]

patient_journey_questions = []


def get_demo_questions(source: Literal["IQS", "Patient Journey"]) -> List[str]:
    return iqs_questions if source == "IQS" else patient_journey_questions

def get_examples_location(source: Literal["IQS", "Patient Journey"]) -> List[str]:
    return "data/iqs/queries/queries.yml" if source == "IQS" else "data/patient_journey/queries/queries.yml"
