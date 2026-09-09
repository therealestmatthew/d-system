---
id: mem-concept-json-sot
title: JSON Source-of-Truth Pattern
type: concept
tags: [frameworks, knowledge-base, python]
source_model: anthropic/claude-sonnet-4-6
project: d-system
created: 2026-09-05
updated: 2026-09-08
confidence: high
related: [mem-decision-json-first]
scope: global
---

## Summary

All persistent data lives in human-readable JSON files. DuckDB is a derived query layer rebuilt on demand — never the authoritative store. Per [ADR-009](../../docs/04-decisions/ADR-009-structure-content-boundary.md), only some of those JSON files are git-tracked: entity content (projects, people, commitments, tasks) resolves through a data root that defaults to the tracked `_data/` but points at the gitignored `_private/portfolio/` when `D_SYSTEM_DATA_ROOT` is set — which is how the owner's real records stay out of git while the tracked tree still holds a working fictional example set.

## How It Works

```
_data/projects/*.json          ← fictional example set (tracked, always)
_private/portfolio/projects/*.json  ← real records (gitignored; D_SYSTEM_DATA_ROOT=_private/portfolio)
_data/commitments/*.json       ← same split as projects/ above
_data/people/*.json            ← same split as projects/ above
_data/tags.json                ← always here — shared taxonomy, not content, never duplicated
brain/**/*.md                  ← write here (memories use Markdown + frontmatter)

tools/rebuild_db.py            ← run this to sync → DuckDB, honours D_SYSTEM_DATA_ROOT
data/d_system.duckdb           ← query here, never write directly
```

## Rules

- **Edit JSON, then rebuild.** Never INSERT directly into DuckDB — the next rebuild will overwrite it.
- **DuckDB is gitignored.** The `data/` directory is in `.gitignore`, same as `_private/`. Only `_data/` and `brain/` are committed.
- **Rebuild is idempotent.** Drop all tables, recreate from SQL schema, reload all files. Safe to run anytime.
- **One file per entity.** Each project, commitment, and task gets its own JSON file — tasks point back to their commitment by ID rather than being embedded (ADR-008). Tags are the exception — all tags live in a single `_data/tags.json` array.
- **Real content never goes in `_data/`.** Writing an entity file with real names, clients or personal content into the tracked `_data/` reintroduces exactly what ADR-009 relocated. Write it under the resolved data root instead.

## Why This Matters for AI Workflows

Any model can read and write the JSON/Markdown source files without knowing anything about DuckDB. The rebuild step is deterministic and can be triggered by any agent or human after edits. This makes the data layer model-agnostic.

## Querying

```python
import duckdb
conn = duckdb.connect("data/d_system.duckdb")
conn.execute("SELECT id, name, status FROM projects WHERE status = 'active'").fetchall()
```

Or use `tools/load_context.py` for AI-ready formatted output.
