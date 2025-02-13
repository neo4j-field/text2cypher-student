import os
import warnings

import pandas as pd
from dotenv import load_dotenv
from pyneoinstance import Neo4jInstance, load_yaml_file

warnings.filterwarnings("ignore")


(
    print(".env variables loaded!")
    if load_dotenv()
    else print("Unable to load .env variables.")
)


def get_partition(data: pd.DataFrame, batch_size: int = 500) -> int:
    """
    Determine the data partition based on the desired batch size.
    """

    partition = int(len(data) / batch_size)
    return partition if partition > 1 else 1


def load_embeddings_df() -> pd.DataFrame:
    e1 = pd.read_csv("data/iqs/dataset/embeddings_1.csv").dropna(
        axis=0, subset="adaEmbedding"
    )
    e2 = pd.read_csv("data/iqs/dataset/embeddings_2.csv").dropna(
        axis=0, subset="adaEmbedding"
    )
    e3 = pd.read_csv("data/iqs/dataset/embeddings_3.csv").dropna(
        axis=0, subset="adaEmbedding"
    )
    embeddings_df = pd.concat([e1, e2, e3])
    embeddings_df["adaEmbedding"] = embeddings_df["adaEmbedding"].apply(
        lambda x: [float(val) for val in x[1:-1].split(", ")]
    )

    return embeddings_df


def main() -> None:
    df = pd.read_csv("data/iqs/dataset/neo4j_iqs_ingest.csv", sep="|")

    # load queries
    config = load_yaml_file("data/iqs/ingest/config.yaml")
    constraints = config["initializing_queries"]["constraints"]
    indexes = config["initializing_queries"]["indexes"]
    node_load_queries = config["loading_queries"]["nodes"]
    relationship_load_queries = config["loading_queries"]["relationships"]

    # # init graph connection
    graph = Neo4jInstance(
        os.environ.get("NEO4J_URI"),
        os.environ.get("NEO4J_USERNAME"),
        os.environ.get("NEO4J_PASSWORD"),
    )

    dbname = os.environ.get("NEO4J_DATABASE")

    # constraints and indexes
    try:
        graph.execute_write_queries(database=dbname, queries=list(constraints.values()))
    except Exception as e:
        print(e)

    try:
        graph.execute_write_queries(database=dbname, queries=list(indexes.values()))
    except Exception as e:
        print(e)

    # load nodes
    for item in node_load_queries.items():
        result = graph.execute_write_query_with_data(
            database=dbname,
            data=df,
            query=item[1],
            partitions=get_partition(df, 500),
        )
        print(f"Loaded {item[0]} nodes with result: {result}")

    # load rels
    for item in relationship_load_queries.items():
        result = graph.execute_write_query_with_data(
            database=dbname,
            data=df,
            query=item[1],
            partitions=get_partition(df, 500),
        )
        print(f"Loaded {item[0]} relationships with result: {result}")

    # post processing
    query = config["post_processing_queries"]["create_verbatim_text"]
    result = graph.execute_write_query(query, dbname)
    print(f"Loaded Text properties on Verbatim Nodes with result: {result}")

    # load pre-generated ada embeddings
    embeddings_df = load_embeddings_df()

    query = config["post_processing_queries"]["load_pregenerated_embeddings"]
    result = graph.execute_write_query_with_data(
        database=dbname,
        data=embeddings_df,
        query=query,
        partitions=get_partition(embeddings_df, 500),
    )
    print(f"Loaded ada Embedding properties on Verbatim Nodes with result: {result}")


if __name__ == "__main__":
    main()
