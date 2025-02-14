import os

from neo4j import GraphDatabase
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

def main() -> None:
    print("Loading BBC Good Food Recipes...")
    driver = GraphDatabase.driver(uri=os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))

    print("Loading Cypher Statements...")
    with open("data/bbc_recipes/ingest/ingest.cypher") as f:
        cyphers = f.read()
        for statement in tqdm(cyphers.split(";")[:-1], desc="BBC Good Food Data Ingest"):
            with driver.session() as session:
                session.run(statement)

if __name__ == "__main__":
    main()
