"""The Cypher statements in this file are to be used in the predefined Cypher executor node."""

from typing import Dict


def get_all_vehicle_names() -> str:
    return """MATCH (v:Vehicle)
RETURN DISTINCT v.id as name"""


def get_number_of_complaints() -> str:
    return """MATCH (v:Verbatim)
RETURN COUNT(DISTINCT v) as numComplaints"""


def get_number_of_complaints_for_a_make_and_model() -> str:
    return """MATCH (v:Verbatim {make: $make, model: $model})
RETURN v.make as make, v.model as model, COUNT(DISTINCT v) as numComplaints"""


def get_number_of_complaints_for_a_make() -> str:
    return """MATCH (v:Verbatim {make: $make})
RETURN v.make as make, v.model as model, COUNT(DISTINCT v) as numComplaints"""


def get_number_of_complaints_for_a_model() -> str:
    return """MATCH (v:Verbatim {model: $model})
RETURN v.make as make, v.model as model, COUNT(DISTINCT v) as numComplaints"""


def get_cypher_statements_dictionary() -> Dict[str, str]:
    """
    Get a Python dictionary with Cypher statement names as keys and parameterized Cypher statements as values.

    Returns
    -------
    Dict[str, str]
        The Cypher statements dictionary.
    """
    return {
        "get_all_vehicle_names": get_all_vehicle_names(),
        "get_number_of_complaints": get_number_of_complaints(),
        "get_number_of_complaints_for_a_make_and_model": get_number_of_complaints_for_a_make_and_model(),
        "get_number_of_complaints_for_a_make": get_number_of_complaints_for_a_make(),
        "get_number_of_complaints_for_a_model": get_number_of_complaints_for_a_model(),
    }
