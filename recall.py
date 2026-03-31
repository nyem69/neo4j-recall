"""Store and query vector-indexed memories in Neo4j."""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from neo4j import GraphDatabase
from dotenv import load_dotenv

from embed import embed, dimensions


def _driver():
    return GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "codegraph")),
    )


def store(
    text: str,
    source: str = "manual",
    session_id: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> str:
    """Store a memory with its vector embedding. Returns the memory ID."""
    memory_id = str(uuid.uuid4())
    vector = embed([text])[0]
    now = datetime.now(timezone.utc).isoformat()

    driver = _driver()
    with driver.session() as session:
        session.run(
            """
            CREATE (m:Memory {
                id: $id,
                text: $text,
                embedding: $embedding,
                source: $source,
                session_id: $session_id,
                tags: $tags,
                created_at: $created_at
            })
            """,
            id=memory_id,
            text=text,
            embedding=vector,
            source=source,
            session_id=session_id or "",
            tags=tags or [],
            created_at=now,
        )
    driver.close()
    return memory_id


def query(
    text: str,
    top_k: int = 5,
    min_score: float = 0.6,
    tag_filter: Optional[str] = None,
) -> list[dict]:
    """Find memories similar to the query text."""
    vector = embed([text])[0]

    cypher = """
        CALL db.index.vector.queryNodes('memory_embeddings', $top_k, $embedding)
        YIELD node, score
        WHERE score >= $min_score
    """
    if tag_filter:
        cypher += " AND $tag IN node.tags"

    cypher += """
        RETURN node.id AS id,
               node.text AS text,
               node.source AS source,
               node.session_id AS session_id,
               node.tags AS tags,
               node.created_at AS created_at,
               score
        ORDER BY score DESC
    """

    driver = _driver()
    with driver.session() as session:
        result = session.run(
            cypher,
            embedding=vector,
            top_k=top_k,
            min_score=min_score,
            tag=tag_filter,
        )
        memories = [dict(r) for r in result]
    driver.close()
    return memories


def search_text(keyword: str, limit: int = 10) -> list[dict]:
    """Fulltext keyword search fallback."""
    driver = _driver()
    with driver.session() as session:
        result = session.run(
            """
            CALL db.index.fulltext.queryNodes('memory_text', $keyword)
            YIELD node, score
            RETURN node.id AS id,
                   node.text AS text,
                   node.source AS source,
                   node.tags AS tags,
                   node.created_at AS created_at,
                   score
            ORDER BY score DESC
            LIMIT $limit
            """,
            keyword=keyword,
            limit=limit,
        )
        memories = [dict(r) for r in result]
    driver.close()
    return memories


def delete(memory_id: str) -> bool:
    """Delete a memory by ID."""
    driver = _driver()
    with driver.session() as session:
        result = session.run(
            "MATCH (m:Memory {id: $id}) DELETE m RETURN count(m) AS deleted",
            id=memory_id,
        )
        deleted = result.single()["deleted"]
    driver.close()
    return deleted > 0


def stats() -> dict:
    """Return memory store statistics."""
    driver = _driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (m:Memory)
            RETURN count(m) AS total,
                   min(m.created_at) AS oldest,
                   max(m.created_at) AS newest
        """)
        row = result.single()
        data = dict(row) if row else {"total": 0, "oldest": None, "newest": None}

        # Tag distribution
        tag_result = session.run("""
            MATCH (m:Memory)
            UNWIND m.tags AS tag
            RETURN tag, count(*) AS count
            ORDER BY count DESC
            LIMIT 20
        """)
        data["tags"] = {r["tag"]: r["count"] for r in tag_result}

    driver.close()
    return data
