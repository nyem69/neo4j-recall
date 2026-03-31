---
name: recall
description: Store and retrieve vector-indexed memories from Neo4j for cross-session context recall
---

# Recall — Vector Memory Skill

Store and query memories with semantic similarity search, backed by Neo4j vector indexes.

## When to Use

- **On session start**: Query recent relevant memories to prime context
- **After learning something important**: Store it for future sessions
- **When the user references past work**: Search for related memories

## Commands

### Store a memory
```bash
cd ~/PROJECTS/LLM/neo4j-recall
python cli.py store "The user prefers concise Telegram reports with emoji headers" --source jin --tags "preference,format"
```

### Query by similarity
```bash
python cli.py query "how does the user want reports formatted" --top-k 3
```

### Keyword search (fallback)
```bash
python cli.py search "Telegram report"
```

### Check stats
```bash
python cli.py stats
```

## Integration Pattern

When jin starts a new session or receives a complex task:

1. **Recall**: Query memories related to the task topic
2. **Apply**: Use recalled context to inform your approach
3. **Store**: After task completion, store any new learnings

### What to Store

- User preferences discovered during conversation
- Project decisions and their rationale
- Investigation findings and conclusions
- Employee performance observations
- Domain knowledge that isn't in files

### What NOT to Store

- Ephemeral task state (use todos instead)
- Information already in `~/.jinn/knowledge/` files
- Raw data or full documents (store summaries)
- Anything derivable from code or git history

## Tags Convention

Use consistent tags for filtering:
- `preference` — user preferences
- `project:<name>` — project-specific context
- `employee:<name>` — employee-related observations
- `domain:<topic>` — domain knowledge
- `decision` — key decisions and rationale
- `investigation` — findings from investigations
