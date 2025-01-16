"""
This file contains the code that formats queries in the queries.yml file into examples to be used in text2cypher.
Only the get_example_queries and get_evaluation_queries functions should be imported from this file.
"""

from typing import Dict, List

import yaml

from .formatters import format_curly_braces


def get_example_queries(file_path: str) -> List[Dict[str, str]]:
    """
    Format the queries to be used in text2cypher.
    """

    with open(file_path) as f:
        try:
            queries = yaml.safe_load(f)["queries"]
        except yaml.YAMLError as exc:
            print(exc)

    return [
        {"human": q["question"], "assistant": format_curly_braces(q["cql"])}
        for q in queries
    ]


def get_evaluation_queries(file_path: str) -> List[Dict[str, str]]:
    """
    Format the queries to be used in test_queries.py.
    """

    with open(file_path) as f:
        try:
            queries: List[Dict[str, str]] = yaml.safe_load(f)["queries"]
        except yaml.YAMLError as exc:
            print(exc)

    return queries


if __name__ == "__main__":
    print(get_example_queries("data/iqs/queries/queries.yml"))
