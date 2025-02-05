from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest
from langchain_neo4j import Neo4jGraph


@pytest.fixture(scope="function")
def cypher_statement_1_valid() -> str:
    """
    This Cypher Statement is VALID.
    to be validated
    * NodeA.prop_1
    * NodeC.prop_1
    * REL_A.prop_5
    * NodeB.prop_1
    * NodeB.prop_3
    skipped
    * NodeA.prop_2 is skipped due to enum not present in schema
    """
    return """
MATCH (n:NodeA {prop_1: "a"})-->(m:NodeC {prop_1: "c"})
WHERE n.prop_2 = "d"
MATCH (m)-[:REL_B]-()-[r:REL_A {prop_5: "z"}]-(o:NodeB {prop_1: "b"})
WHERE o.prop_3 = 3
RETURN n.prop_1, m.prop_1, o.prop_1
"""


@pytest.fixture(scope="function")
def cypher_statement_1_invalid() -> str:
    """
    This Cypher Statement is INVALID.
    to be validated
    * NodeA.prop_1
    * NodeA.prop_2
    * NodeC.prop_2
    * REL_A.prop_5
    * REL_A.prop_7
    * NodeB.prop_1
    * NodeB.prop_3
    errors
    * NodeA.prop_1 is not in enum
    * NodeC.prop_2 does not exist
    * REL_A.prop_7 does not exist
    * NodeB.prop_3 is out of range
    """
    return """
MATCH (n:NodeA {prop_1: "d"})-->(m:NodeC {prop_2: "c"})
WHERE n.prop_2 = "d"
MATCH (m)-[:REL_B]-()-[r:REL_A {prop_5: "z", prop_7: 10}]-(o:NodeB {prop_1: "b"})
WHERE o.prop_3 = 14
RETURN n.prop_1, m.prop_1, o.prop_1
"""


@pytest.fixture(scope="function")
def cypher_statement_iqs_valid() -> str:
    """
    tasks
    * Verbatim.make = 'Honda'
    * Verbatim.verbatimText CONTAINS "cup holder"
    * Verbatim.model = "Odyssey"
    * Verbatim.gender = 'male'
    * Verbatim.gender = 'female'
    not validated
    * Verbatim.verbatimText - too many distinct
    * Verbatim.model - too many distinct
    """
    return """
MATCH (v:Verbatim {make: "Honda", model: "Odyssey"})
WHERE v.verbatimText CONTAINS "cup holder"
WITH SUM(COUNT {MATCH (v:Verbatim) WHERE v.gender = "Male" RETURN v}) AS males,
    SUM(COUNT {MATCH (v:Verbatim) WHERE v.gender = "Female" RETURN v}) AS females
RETURN males, females, toFloat(males) / (CASE WHEN females = 0 THEN 1 ELSE females END)  AS maleToFemale
"""


@pytest.fixture(scope="function")
def cypher_statement_iqs_invalid() -> str:
    """
    tasks
    * Verbatim.make = 'Ford'
    * Verbatim.verbatimContent CONTAINS "cup holder"
    * Verbatim.model = "Odyssey"
    * Verbatim.gender = 'male'
    * Verbatim.gender = 'female'
    Errors
    * Verbatim.make = 'Ford'
    * Verbatim.verbatimContent does not exist
    """
    return """
MATCH (v:Verbatim {make: "Ford", model: "Odyssey"})
WHERE v.verbatimContent CONTAINS "cup holder"
WITH SUM(COUNT {MATCH (v:Verbatim) WHERE v.gender = "Male" RETURN v}) AS males,
    SUM(COUNT {MATCH (v:Verbatim) WHERE v.gender = "Female" RETURN v}) AS females
RETURN males, females, toFloat(males) / (CASE WHEN females = 0 THEN 1 ELSE females END)  AS maleToFemale
"""


@pytest.fixture(scope="function")
def cypher_statement_patient_journey_valid() -> str:
    """
    tasks
    * Patient.id exists
    ignored

    """
    return """
MATCH (p:Patient {id:"f9437ac7"})-[:HAS_ENCOUNTER]->(e)
WHERE apoc.node.degree.in(e,'NEXT') = 0
WITH e
MATCH (e)-[:NEXT*]->(e2)
with e as e1, collect(e2) as erest
with e1 + erest as encounters
unwind encounters as e
return e.class as encounterType, e.description as encounterDescription, e.date as startDate, e.end as endDate
"""


@pytest.fixture(scope="function")
def structured_schema_1() -> Dict[str, Any]:
    return {
        "node_props": {
            "NodeA": [
                {
                    "property": "prop_1",
                    "type": "STRING",
                    "values": ["a", "b", "c"],
                    "distinct_count": 3,
                },
                {
                    "property": "prop_2",
                    "type": "STRING",
                    "values": ["d", "e", "f"],
                    "distinct_count": 4,
                },
            ],
            "NodeB": [
                {
                    "property": "prop_1",
                    "type": "STRING",
                    "values": ["a", "b", "c"],
                    "distinct_count": 3,
                },
                {
                    "property": "prop_3",
                    "type": "INTEGER",
                    "min": "0",
                    "max": "10",
                    "distinct_count": 25,
                },
            ],
            "NodeC": [
                {
                    "property": "prop_1",
                    "type": "STRING",
                    "values": ["a", "b", "c"],
                    "distinct_count": 3,
                },
                {
                    "property": "prop_4",
                    "type": "LIST",
                    "max_size": 1536,
                    "min_size": 1536,
                },
            ],
        },
        "rel_props": {
            "REL_A": [
                {
                    "property": "prop_5",
                    "type": "STRING",
                    "values": ["x", "y", "z"],
                    "distinct_count": 3,
                },
                {
                    "property": "prop_6",
                    "type": "FLOAT",
                    "min": 0.0,
                    "max": 1.0,
                },
            ],
        },
        "relationships": [
            {"start": "NodeA", "type": "REL_A", "end": "NodeB"},
            {"start": "NodeA", "type": "REL_B", "end": "NodeC"},
        ],
    }


@pytest.fixture(scope="function")
def mock_graph_1(
    structured_schema_1: Dict[str, Dict[str, List[Dict[str, Any]]]],
) -> MagicMock:
    m = MagicMock(spec=Neo4jGraph)
    m.get_structured_schema = structured_schema_1
    return m


@pytest.fixture(scope="function")
def structured_schema_iqs() -> Dict[str, Any]:
    return {
        "node_props": {
            "Customer": [
                {
                    "property": "id",
                    "type": "STRING",
                    "values": [
                        "9A79438B",
                        "938B2B87",
                        "969B423V",
                        "97A5484F",
                        "97389689",
                        "978749BE",
                        "979AB23T",
                        "97B5583G",
                        "9374BABV",
                        "96B8439A",
                    ],
                    "distinct_count": 3967,
                },
                {
                    "property": "ageBucket",
                    "type": "STRING",
                    "values": [
                        ">=70",
                        "",
                        "65-69",
                        "25-29",
                        "50-54",
                        "35-39",
                        "45-49",
                        "40-44",
                        "60-64",
                        "30-34",
                    ],
                    "distinct_count": 13,
                },
                {
                    "property": "gender",
                    "type": "STRING",
                    "values": ["Male", "Female", ""],
                    "distinct_count": 3,
                },
            ],
            "Category": [
                {
                    "property": "id",
                    "type": "STRING",
                    "values": [
                        "Exterior",
                        "Driving Experience",
                        "Features/Controls/Displays (FCD)",
                        "Driving Assistance",
                        "Infotainment",
                        "Seats",
                        "Climate",
                        "Interior",
                        "Powertrain",
                    ],
                    "distinct_count": 9,
                }
            ],
            "Problem": [
                {
                    "property": "id",
                    "type": "STRING",
                    "values": [
                        "EXT01",
                        "EXT02",
                        "EXT03",
                        "EXT04",
                        "EXT05",
                        "EXT06",
                        "EXT07",
                        "EXT08",
                        "EXT09",
                        "EXT10",
                    ],
                    "distinct_count": 214,
                },
                {
                    "property": "problem",
                    "type": "STRING",
                    "values": [
                        "EXT01: Doors - Hard to open/close",
                        "EXT02: Doors - Handle/latch/release - DTU",
                        "EXT03: Doors - Squeak/abnormal noise when opening/",
                        "EXT04: Hood - Hard to open/close",
                        "EXT05: Hood - Handle/latch/release - DTU",
                        "EXT06: Trunk/hatch/tailgate - Hard to open/close",
                        "EXT07: Trunk/hatch/tailgate - Squeak/abnormal nois",
                        "EXT08: Trunk/hatch/tailgate - Handle/latch/release",
                        "EXT09: Trunk/hatch/tailgate - Opens unexpectedly",
                        "EXT10: Trunk/hatch/tailgate - Touch-free sensor do",
                    ],
                    "distinct_count": 214,
                },
            ],
            "Question": [
                {
                    "property": "id",
                    "type": "INTEGER",
                    "min": "1",
                    "max": "223",
                    "distinct_count": 214,
                },
                {
                    "property": "question",
                    "type": "STRING",
                    "values": [
                        "#001 Doors Hard to Open/Close",
                        "#002 Doors Handle/Latch/Release DTU",
                        "#003 Doors Open/Close Noise",
                        "#004 Hood Hard to Open/Close",
                        "#005 Hood Handle/Latch/Release DTU",
                        "#006 Trunk/TG Hard to Open/Close",
                        "#007 Trunk/TG Noise Open/Close",
                        "#008 Trunk/TG Handle/Latch/Release DTU",
                        "#009 Trunk/TG Opens Unexpectedly",
                        "#010 Trunk/TG Touch-Free Sensor DTU",
                    ],
                    "distinct_count": 214,
                },
            ],
            "Vehicle": [
                {
                    "property": "id",
                    "type": "STRING",
                    "values": [
                        "Acura Integra",
                        "Acura RDX",
                        "Acura TLX",
                        "Honda Accord",
                        "Honda Civic",
                        "Honda CR-V",
                        "Honda HR-V",
                        "Honda Odyssey",
                        "Honda Passport",
                        "Honda Pilot",
                    ],
                    "distinct_count": 12,
                },
                {
                    "property": "totalProblems",
                    "type": "INTEGER",
                    "min": "2",
                    "max": "10",
                    "distinct_count": 7,
                },
            ],
            "Verbatim": [
                {
                    "property": "id",
                    "type": "STRING",
                    "values": [
                        "9323AB5C",
                        "9343262U",
                        "9353A55V",
                        "935479AW",
                        "937243AQ",
                    ],
                },
                {
                    "property": "verbatim",
                    "type": "STRING",
                    "values": [
                        "It doesn't work if I have my phone in the car.  Th",
                        "Performs well, provides accurate navigation.  Prob",
                        "When using turn by turn directions in the Nav syst",
                        "Touch pad is difficult to use",
                        "Trackpad is difficult to use",
                    ],
                },
                {
                    "property": "verbatimText",
                    "type": "STRING",
                    "values": ["acura rdx infotainment info13: built-in navigation"],
                },
                {
                    "property": "severity",
                    "type": "FLOAT",
                    "values": ["3.0", "4.0"],
                    "distinct_count": 2,
                },
                {
                    "property": "gender",
                    "type": "STRING",
                    "values": ["Female", "Male"],
                    "distinct_count": 2,
                },
                {
                    "property": "make",
                    "type": "STRING",
                    "values": ["Acura", "Honda"],
                    "distinct_count": 2,
                },
                {
                    "property": "model",
                    "type": "STRING",
                    "values": ["RDX"],
                    "distinct_count": 12,
                },
                {
                    "property": "adaEmbedding",
                    "type": "LIST",
                    "max_size": 1536,
                    "min_size": 1536,
                },
                {
                    "property": "titanEmbedding",
                    "type": "LIST",
                    "max_size": 1536,
                    "min_size": 1536,
                },
                {
                    "property": "ageBucket",
                    "type": "STRING",
                    "values": ["60-64", "55-59", "45-49"],
                    "distinct_count": 10,
                },
                {"property": "minAge", "type": "INTEGER", "min": "20", "max": "80"},
                {"property": "maxAge", "type": "INTEGER", "min": "20", "max": "80"},
            ],
        },
        "rel_props": {},
        "relationships": [
            {"start": "Customer", "type": "SUBMITTED", "end": "Verbatim"},
            {"start": "Problem", "type": "HAS_CATEGORY", "end": "Category"},
            {"start": "Question", "type": "HAS_PROBLEM", "end": "Problem"},
            {"start": "Vehicle", "type": "HAS_CATEGORY", "end": "Category"},
            {"start": "Vehicle", "type": "HAS_VERBATIM", "end": "Verbatim"},
            {"start": "Verbatim", "type": "HAS_CATEGORY", "end": "Category"},
            {"start": "Verbatim", "type": "HAS_PROBLEM", "end": "Problem"},
            {"start": "Verbatim", "type": "HAS_QUESTION", "end": "Question"},
        ],
        "metadata": {
            "constraint": [
                {
                    "id": 12,
                    "name": "problem_id",
                    "type": "UNIQUENESS",
                    "entityType": "NODE",
                    "labelsOrTypes": ["Problem"],
                    "properties": ["id"],
                    "ownedIndex": "problem_id",
                    "propertyType": None,
                },
                {
                    "id": 13,
                    "name": "question_id",
                    "type": "UNIQUENESS",
                    "entityType": "NODE",
                    "labelsOrTypes": ["Question"],
                    "properties": ["id"],
                    "ownedIndex": "question_id",
                    "propertyType": None,
                },
                {
                    "id": 8,
                    "name": "unique_category",
                    "type": "UNIQUENESS",
                    "entityType": "NODE",
                    "labelsOrTypes": ["Category"],
                    "properties": ["id"],
                    "ownedIndex": "unique_category",
                    "propertyType": None,
                },
                {
                    "id": 4,
                    "name": "unique_customer",
                    "type": "UNIQUENESS",
                    "entityType": "NODE",
                    "labelsOrTypes": ["Customer"],
                    "properties": ["id"],
                    "ownedIndex": "unique_customer",
                    "propertyType": None,
                },
                {
                    "id": 5,
                    "name": "vehicle_series",
                    "type": "UNIQUENESS",
                    "entityType": "NODE",
                    "labelsOrTypes": ["Vehicle"],
                    "properties": ["id"],
                    "ownedIndex": "vehicle_series",
                    "propertyType": None,
                },
                {
                    "id": 7,
                    "name": "verbatim_rid",
                    "type": "NODE_KEY",
                    "entityType": "NODE",
                    "labelsOrTypes": ["Verbatim"],
                    "properties": ["verbatim", "id"],
                    "ownedIndex": "verbatim_rid",
                    "propertyType": None,
                },
            ],
            "index": [
                {
                    "label": "Category",
                    "properties": ["id"],
                    "size": 9,
                    "type": "RANGE",
                    "valuesSelectivity": 1.0,
                    "distinctValues": 9.0,
                },
                {
                    "label": "Customer",
                    "properties": ["id"],
                    "size": 3967,
                    "type": "RANGE",
                    "valuesSelectivity": 1.0,
                    "distinctValues": 3967.0,
                },
                {
                    "label": "Problem",
                    "properties": ["id"],
                    "size": 214,
                    "type": "RANGE",
                    "valuesSelectivity": 1.0,
                    "distinctValues": 214.0,
                },
                {
                    "label": "Question",
                    "properties": ["id"],
                    "size": 214,
                    "type": "RANGE",
                    "valuesSelectivity": 1.0,
                    "distinctValues": 214.0,
                },
                {
                    "label": "Vehicle",
                    "properties": ["id"],
                    "size": 12,
                    "type": "RANGE",
                    "valuesSelectivity": 1.0,
                    "distinctValues": 12.0,
                },
                {
                    "label": "Verbatim",
                    "properties": ["verbatim", "id"],
                    "size": 12380,
                    "type": "RANGE",
                    "valuesSelectivity": 1.0,
                    "distinctValues": 12380.0,
                },
            ],
        },
    }


@pytest.fixture(scope="function")
def mock_graph_iqs(
    structured_schema_iqs: Dict[str, Dict[str, List[Dict[str, Any]]]],
) -> MagicMock:
    m = MagicMock(spec=Neo4jGraph)
    m.get_structured_schema = structured_schema_iqs
    return m
