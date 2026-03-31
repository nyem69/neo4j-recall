# neo4j-recall

Vector-indexed memory for AI assistants, backed by Neo4j.

Store memories with semantic embeddings. Query them by meaning, not just keywords. Designed for cross-session context recall in agentic systems.

## How it works

1. Text → embedding vector (OpenAI or Ollama)
2. Vector + metadata → Neo4j `:Memory` node
3. Query text → embedding → cosine similarity search → top-k results

Uses a separate `:Memory` label — safe to run alongside existing graph data (code graphs, knowledge graphs, etc).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # edit with your credentials
python cli.py setup   # creates vector index in Neo4j
```

### Requirements

- Python 3.11+
- Neo4j 5.13+ (local or remote) with vector index support
- One of:
  - OpenAI API key (for `text-embedding-3-small`)
  - Ollama instance (for `nomic-embed-text`)

## Usage

### CLI

```bash
# Store a memory
python cli.py store "User prefers bullet-point summaries over prose" --tags "preference,format"

# Semantic search
python cli.py query "how should I format output for the user"

# Keyword search (fulltext fallback)
python cli.py search "format"

# Stats
python cli.py stats

# Delete
python cli.py delete <memory-id>
```

### Python

```python
from recall import store, query

# Store
store("PMX reshuffled cabinet in March 2026", source="investigation", tags=["politics", "malaysia"])

# Query — returns top-k similar memories with scores
results = query("Malaysian cabinet changes")
for r in results:
    print(f"[{r['score']:.3f}] {r['text']}")
```

## Configuration

Via `.env` or environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | — | Neo4j password |
| `EMBEDDING_PROVIDER` | `openai` | `openai` or `ollama` |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI model |
| `OLLAMA_BASE_URL` | `https://ollama.aga.my` | Ollama endpoint |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Ollama model |

## Architecture

```
cli.py          → CLI entry point
embed.py        → Embedding provider abstraction (OpenAI + Ollama fallback)
recall.py       → Store, query, search, delete memories
setup.py        → Create Neo4j vector + fulltext indexes
skill/SKILL.md  → jin skill integration
```

Memories are stored as `:Memory` nodes with properties:
- `id` — UUID
- `text` — original text
- `embedding` — float vector
- `source` — where the memory came from
- `session_id` — linked session
- `tags` — string array for filtering
- `created_at` — ISO timestamp

## License

MIT
