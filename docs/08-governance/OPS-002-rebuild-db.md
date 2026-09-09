---
schema_version: 1
id: doc-ops-rebuild-db
code: OPS-002
title: Rebuild the DuckDB projection
kind: operation
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-projection]
depends_on: [doc-governance-operations]
---

# Rebuild the DuckDB projection

## Trigger

Run after editing any file under `_data/` or any Markdown memory under `brain/`. The database is a
derived projection, not a source — nothing else updates it, and stale rows are otherwise invisible
until an API response or a query returns them.

## Command

```bash
uv run python tools/rebuild_db.py
```

## Expected result

Exit 0. Every source file validates first — a schema-invalid `_data/` or `brain/` file aborts the
whole run before any table is touched, so a bad source costs nothing. On success the script drops
and recreates all eight tables from `sql/001_schema.sql`, reloads them from the JSON and Markdown
sources, and prints a row count per table.

## Failure and recovery

A validation error prints the failing file and field; fix the source file (never edit `data/`
directly, it is gitignored and fully derived) and rerun. Because validation happens before any
table is dropped, a failed run leaves the previous database exactly as it was — there is nothing to
roll back. No recovery step ever requires dropping a table by hand.

<!-- generated:tool-reference:start -->

### Reference: `tools/rebuild_db.py`

Rebuild DuckDB from entity JSON files and brain/ Markdown memories.

Run after editing any source files:
    uv run python tools/rebuild_db.py

Every source file is validated first. The rebuild drops every table before it inserts
anything, so a file that fails halfway through leaves an empty database rather than the
one it replaced; validating up front means a bad source file costs nothing.

Entity content (projects, people, commitments, tasks, ...) is read from
`D_SYSTEM_DATA_ROOT` if set, else the tracked `_data/` — see `data_root()` in
`src/db/source_validation.py` and ADR-009. `tags.json`, `ideas.jsonl` and `brain/` are
shared structure, not portfolio content, and are always read from the tracked tree.

No CLI arguments.

Exit codes found in source: 1.

<!-- generated:tool-reference:end -->
