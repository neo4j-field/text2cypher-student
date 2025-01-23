"""
This file contains the code that formats queries in the queries.yml file into examples to be used in text2cypher.
"""

from typing import Dict, List

import yaml


def get_example_queries_from_yaml(file_path: str) -> List[Dict[str, str]]:
    """
    Format the queries to be used in text2cypher.
    """

    with open(file_path) as f:
        try:
            queries = yaml.safe_load(f)["queries"]
        except yaml.YAMLError as exc:
            print(exc)
    return [
        {"human": q["question"], "assistant": _format_cypher_for_example(q["cql"])}
        for q in queries
    ]


def _format_cypher_for_example(cypher: str) -> str:
    """
    Formats Cypher for use in LangChain's Example Templates.
    This involves replacing '{' with '{{' and '}' with '}}'.
    """

    cypher = cypher.replace("{", "{{")
    return cypher.replace("}", "}}")
