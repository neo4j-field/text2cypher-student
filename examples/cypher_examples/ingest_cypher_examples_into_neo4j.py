import os

from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings

from ps_genai_agents.ingest.cypher_examples.ingest_neo4j import (
    embed_cypher_query_nodes,
    get_existing_questions,
    load_cypher_query_nodes,
)
from ps_genai_agents.ingest.cypher_examples.utils import (
    read_cypher_examples_from_yaml_file,
    remove_preexisting_nodes_from_ingest_tasks,
)

file_path = "data/iqs/queries/queries/yml"
driver = GraphDatabase.driver(
    uri=os.getenv("NEO4J_URI", ""),
    auth=(os.getenv("NEO4J_USERNAME", ""), os.getenv("NEO4J_PASSWORD", "")),
)
embedder = OpenAIEmbeddings()

# read question and cql pairs from a YAML file
# this is optional as long as there is a list of Python dictionaries prepared for processing
unembedded_tasks = read_cypher_examples_from_yaml_file(file_path=file_path)

# we optionally get the preexisting node ids (question property) as a set
# we can remove these from the tasks
preexisting_nodes = get_existing_questions(driver)

# remove any questions we already have in the database
cleaned_tasks = remove_preexisting_nodes_from_ingest_tasks(
    unembedded_tasks, preexisting_nodes
)

# embed the remaining tasks
# this embeds the question content
embedded_tasks_results = embed_cypher_query_nodes(embedder, cleaned_tasks)

# access the prepared nodes with embeddings with the `nodes` key
embedded_tasks = embedded_tasks_results.get("nodes", list())

# any tasks that generated errors during the embedding process can be accessed with the `failed` key
failed_embeddings = embedded_tasks_results.get("failed")

# load CypherQuery nodes into Neo4j
load_cypher_query_nodes(driver, embedded_tasks)
