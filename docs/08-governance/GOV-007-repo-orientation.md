---
schema_version: 1
id: doc-repo-orientation
code: GOV-007
title: Repository Orientation
kind: governance
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-governance]
depends_on: []
review_after: '2026-12-08'
---

# Repository Orientation

This document outlines the project purpose, data architecture, directory layout, and framework for the system. It is abstracted to serve any agent or human onboarding to the repository.

## Project Purpose

Personal consulting management system for tracking people, projects, commitments, and tasks — reducing mental overhead by centralizing work responsibilities. Doubles as a platform for HTML generation, reporting, and agentic workflow triggering.

## Data Architecture

### Source of truth: `_data/` (git-tracked JSON)

```
_data/
  tags.json              ← all tag definitions (reference list)
  projects/              ← one JSON per project
  commitments/           ← one JSON per commitment (tasks embedded as array)
  people/                ← one JSON per person/stakeholder
```

### DuckDB: derived query layer (gitignored)

`data/d_system.duckdb` is rebuilt on demand from `_data/` JSON by `tools/rebuild_db.py`. Never edit the DB directly — edit the JSON files, then rebuild.

### Schema files: `schemas/` (JSON Schema for validation)

`project.schema.json`, `commitment.schema.json`, `person.schema.json`, `tag.schema.json`

### DDL: `sql/001_schema.sql`

Tables: `projects`, `people`, `project_people`, `tags`, `project_tags`, `commitments`, `tasks`

Key relationships:
- Tasks are embedded in commitment JSON but get their own `tasks` table in DuckDB (unpacked by rebuild)
- `tags` field on project JSON is denormalized into both the `projects.tags` array column and the `project_tags` junction table
- `project_people` is populated from the `projects` array inside each person's JSON

## Backend Layout

```
src/
  main.py          # FastAPI app, CORS, router registration
  api/
    __init__.py    # APIRouter at /api/v1 — register route modules here
    routes/        # one file per domain (projects.py, commitments.py, etc.)
  db/
    connection.py  # get_db() context manager — yields a DuckDB connection
  models/          # Pydantic models (request/response shapes)
```

- `get_db()` opens a fresh connection per call; DuckDB is file-based, no pool needed at this scale.
- All routes live under `/api/v1`.

## Frontend Layout

```
ts/
  src/
    main.tsx        # React root
    App.tsx         # root component
  vite.config.ts    # proxies /api → :8000, no CORS issues in dev
```

## HTML Generation Framework

Source data (`_data/`) → templates (`templates/html/`, `templates/styles/`) → generation scripts (`tools/` or `src/`) → React UI (`ts/`) + FastAPI (`src/`). The UI supports:
- Triggering agentic workflows
- Viewing/managing source data and transformations
- Generating reports, charts, summaries
- Composable multi-page frameworks

## Directory Reference

| Directory | Purpose |
|---|---|
| `src/` | FastAPI application |
| `ts/` | React/TypeScript frontend |
| `js/` | Plain JS utilities (browser automation, one-off scripts) |
| `schemas/` | JSON Schema definitions for all data entities |
| `sql/` | DuckDB DDL migrations |
| `_data/` | Source-of-truth JSON files (git-tracked) |
| `templates/html/` | HTML page and component templates |
| `templates/styles/` | CSS / style definitions for template families |
| `test/` | pytest test suite |
| `tools/` | CLI and helper scripts (rebuild_db.py, etc.) |
| `docs/00-working/` | Ungoverned staging for parked ideas |
| `docs/01-plans/` | Implementation plans (`PLAN-NNN-topic.md`) |
| `docs/02-prompts/` | AI prompt templates |
| `docs/03-sessions/` | Session logs |
| `docs/04-decisions/` | Architecture Decision Records (`ADR-NNN-topic.md`) |
| `docs/05-memories/` | Persistent cross-session context |
| `docs/06-requirements/` | Feature requirements |
| `docs/07-architecture/` | Architecture diagrams and docs |
| `_working/` | Ephemeral working plans and task detail |
| `_tmpagent/` | Files agents in sibling worktrees must read |
| `_public/` | Shareable outputs |
| `_private/` | Gitignored — credentials, raw dumps, personal notes |
