---
schema_version: 1
id: doc-ops-load-context
code: OPS-003
title: Load memory context for an AI session
kind: operation
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-10-04'
systems: [sys-retrieval]
depends_on: [doc-governance-operations]
---

# Load memory context for an AI session

## Trigger

Run when a human or agent needs a bounded, formatted slice of `brain/`'s memories pasted into a
model that has no other access to this repository — a keyword search, everything for one project,
everything of one memory type, or the full set.

## Command

```bash
uv run python tools/load_context.py --query "DuckDB connection pattern"
uv run python tools/load_context.py --project example-project
uv run python tools/load_context.py --type procedure
uv run python tools/load_context.py --all
```

## Expected result

Plain Markdown on stdout: a header naming the query that produced it, then each matching memory
rendered in full. Read-only — it queries the DuckDB projection and never writes to it. Filters
combine with AND, and multiple `--tags` must all match. `--project` returns that project's memories
plus every `scope: global` memory, including the ones that carry `project: d-system`; another
project's memories and session notes are left out. Results are ordered by confidence, then newest
first, then id. At most 10 are returned unless `--limit` says otherwise; `--all` ignores every other
filter and returns everything, unless an explicit `--limit` caps it.

## Failure and recovery

Requires `data/d_system.duckdb` to exist and be current — if it is missing or stale, rebuild it
first with `tools/rebuild_db.py` ([OPS-002](OPS-002-rebuild-db.md)). An unrecognized `--type` value
is rejected by `argparse` before any query runs, listing the legal values. A `--limit` below 1,
above 9223372036854775807 (DuckDB's largest `LIMIT`), or not an integer is rejected the same way,
with exit code 2 and no query run.

<!-- generated:tool-reference:start -->

### Reference: `tools/load_context.py`

Load relevant brain memories into a formatted context block for any AI model.

Output is plain Markdown — paste into Claude, GPT-4o, Gemini, or any other model.

Usage:
    uv run python tools/load_context.py --query "DuckDB connection pattern"
    uv run python tools/load_context.py --project example-project
    uv run python tools/load_context.py --type procedure
    uv run python tools/load_context.py --tags python,frameworks
    uv run python tools/load_context.py --system sys-backlog
    uv run python tools/load_context.py --query "memory" --type concept --limit 5
    uv run python tools/load_context.py --all

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--query`, `-q` | Keyword search across title and content |  |  |  |
| `--project`, `-p` | Filter by project ID (also includes scope: global memories) |  |  |  |
| `--type`, `-t` | Filter by memory type | concept, entity, procedure, episode, decision |  |  |
| `--tags` | Comma-separated tag IDs to filter by |  |  |  |
| `--system`, `-s` | Filter by system ID from systems.yaml |  |  |  |
| `--limit`, `-n` | Max memories to return, at least 1 (default 10; unbounded with --all) |  |  |  |
| `--all` | Return all memories, unbounded unless --limit is given (ignores other filters) |  |  |  |

<!-- generated:tool-reference:end -->
