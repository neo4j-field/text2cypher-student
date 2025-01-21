from typing import Any, Dict, List

import pytest


@pytest.fixture(scope="function")
def cypher_statement_1() -> str:
    return "match (n:Node)-[r:RELATIONSHIP]->(m {id:'001'}) return n, r, m limit 5"


@pytest.fixture(scope="function")
def cypher_statement_2() -> str:
    return """
MATCH (v:Verbatim {make: "Honda", model: "Odyssey"})
WHERE v.verbatimText CONTAINS "cup holder"
WITH SUM(COUNT {MATCH (v:Verbatim) WHERE v.gender = "Male" RETURN v}) AS males,
    SUM(COUNT {MATCH (v:Verbatim) WHERE v.gender = "Female" RETURN v}) AS females
RETURN males, females, toFloat(males) / (CASE WHEN females = 0 THEN 1 ELSE females END)  AS maleToFemale
"""


@pytest.fixture(scope="function")
def cypher_statement_3() -> str: ...
@pytest.fixture(scope="function")
def cypher_statement_4() -> str: ...
@pytest.fixture(scope="function")
def cypher_statement_5() -> str: ...
@pytest.fixture(scope="function")
def cypher_statements(cypher_statement_1: str, cypher_statement_2: str) -> List[str]:
    return [cypher_statement_1, cypher_statement_2]


@pytest.fixture(scope="function")
def node_1() -> str:
    return "(n:Node {uid:'123'})"


@pytest.fixture(scope="function")
def prop_1() -> str:
    return "{uid:'123'}"


@pytest.fixture(scope="function")
def match_clause_property_id() -> str:
    return '{model: "Odyssey"}'


@pytest.fixture(scope="function")
def match_clause_property_ids() -> str:
    return '{make: "Honda", model: "Odyssey"}'


@pytest.fixture(scope="function")
def node_property_values_enum_dict() -> Dict[str, Any]:
    return {
        "NodeA": {"prop_1": ["a", "b", "c"], "prop_2": ["c", "d", "e"]},
        "NodeB": {"prop_1": ["a", "b", "c", "d"]},
    }


@pytest.fixture(scope="function")
def node_property_names_enum_dict() -> Dict[str, Any]:
    return {
        "NodeA": {"prop_1", "prop_2"},
        "NodeB": {"prop_1"},
    }


@pytest.fixture(scope="function")
def node_property_values_range_dict() -> Dict[str, Any]:
    return {
        "NodeA": {"prop_1": (0, 10), "prop_2": (11, 20)},
        "NodeB": {"prop_1": (0, 15)},
    }
