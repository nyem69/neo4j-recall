"""Create the Memory vector index in Neo4j."""

import os
import sys

from neo4j import GraphDatabase
from dotenv import load_dotenv

from embed import dimensions


def setup(uri: str, user: str, password: str, provider: str | None = None):
    dim = dimensions(provider)
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        # Create constraint for Memory nodes
        session.run("""
            CREATE CONSTRAINT memory_id IF NOT EXISTS
            FOR (m:Memory) REQUIRE m.id IS UNIQUE
        """)

        # Create vector index on Memory.embedding
        session.run(f"""
            CREATE VECTOR INDEX memory_embeddings IF NOT EXISTS
            FOR (m:Memory) ON (m.embedding)
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {dim},
                    `vector.similarity_function`: 'cosine'
                }}
            }}
        """)

        # Create fulltext index for keyword fallback
        session.run("""
            CREATE FULLTEXT INDEX memory_text IF NOT EXISTS
            FOR (m:Memory) ON EACH [m.text]
        """)

        # Verify
        result = session.run("SHOW INDEXES YIELD name, type, labelsOrTypes WHERE 'Memory' IN labelsOrTypes RETURN name, type")
        indexes = [(r["name"], r["type"]) for r in result]

    driver.close()

    print(f"[setup] Memory indexes created (dimensions={dim}):")
    for name, idx_type in indexes:
        print(f"  {name} ({idx_type})")


if __name__ == "__main__":
    load_dotenv()
    setup(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "codegraph"),
        provider=os.getenv("EMBEDDING_PROVIDER"),
    )
