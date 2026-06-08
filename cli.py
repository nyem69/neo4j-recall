#!/usr/bin/env python3
"""CLI for neo4j-recall — store and query vector-indexed memories."""

import argparse
import json
import sys
import os

from dotenv import load_dotenv


def cmd_setup(args):
    from setup import setup
    setup(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "codegraph"),
        provider=os.getenv("EMBEDDING_PROVIDER"),
    )


def cmd_store(args):
    from recall import store
    memory_id = store(
        text=args.text,
        source=args.source,
        session_id=args.session,
        tags=args.tags.split(",") if args.tags else None,
    )
    print(json.dumps({"id": memory_id, "status": "stored"}))


def cmd_query(args):
    from recall import query
    results = query(
        text=args.text,
        top_k=args.top_k,
        min_score=args.min_score,
        tag_filter=args.tag,
    )
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        if not results:
            print("No matching memories found.")
            return
        for r in results:
            score = f"{r['score']:.3f}"
            print(f"[{score}] {r['text'][:120]}")
            if r.get("tags"):
                print(f"        tags: {', '.join(r['tags'])}")
            print()


def cmd_search(args):
    from recall import search_text
    results = search_text(args.keyword, limit=args.limit)
    for r in results:
        print(f"[{r['score']:.2f}] {r['text'][:120]}")


def cmd_stats(args):
    from recall import stats
    data = stats()
    print(json.dumps(data, indent=2, default=str))


def cmd_delete(args):
    from recall import delete
    if delete(args.id):
        print(f"Deleted {args.id}")
    else:
        print(f"Not found: {args.id}")


def main():
    load_dotenv(override=True)

    parser = argparse.ArgumentParser(
        prog="recall",
        description="Neo4j vector-indexed memory for AI assistants",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # setup
    sub.add_parser("setup", help="Create vector index in Neo4j")

    # store
    p_store = sub.add_parser("store", help="Store a memory")
    p_store.add_argument("text", help="Memory text")
    p_store.add_argument("--source", default="manual", help="Source identifier")
    p_store.add_argument("--session", help="Session ID")
    p_store.add_argument("--tags", help="Comma-separated tags")

    # query
    p_query = sub.add_parser("query", help="Semantic similarity search")
    p_query.add_argument("text", help="Query text")
    p_query.add_argument("--top-k", type=int, default=5, help="Max results")
    p_query.add_argument("--min-score", type=float, default=0.6, help="Min similarity")
    p_query.add_argument("--tag", help="Filter by tag")
    p_query.add_argument("--json", action="store_true", help="JSON output")

    # search
    p_search = sub.add_parser("search", help="Fulltext keyword search")
    p_search.add_argument("keyword", help="Search keyword")
    p_search.add_argument("--limit", type=int, default=10)

    # stats
    sub.add_parser("stats", help="Memory store statistics")

    # delete
    p_del = sub.add_parser("delete", help="Delete a memory")
    p_del.add_argument("id", help="Memory ID")

    args = parser.parse_args()
    commands = {
        "setup": cmd_setup,
        "store": cmd_store,
        "query": cmd_query,
        "search": cmd_search,
        "stats": cmd_stats,
        "delete": cmd_delete,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
