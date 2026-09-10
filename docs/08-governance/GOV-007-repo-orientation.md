---
schema_version: 1
id: doc-repo-orientation
code: GOV-007
title: Repository Orientation
kind: governance
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-10'
systems: [sys-governance]
depends_on: []
review_after: '2026-12-08'
---

# Repository Orientation

This document outlines the project purpose, data architecture, directory layout, and framework for the system. It is abstracted to serve any agent or human onboarding to the repository.

## Project Purpose

Personal consulting management system for tracking people, projects, commitments, and tasks — reducing mental overhead by centralizing work responsibilities. Doubles as a platform for HTML generation, reporting, and agentic workflow triggering.

## Data Architecture

### Source of truth: JSON and Markdown files

```
_data/
  tags.json              ← all tag definitions (reference list)
  ideas.jsonl            ← append-only idea event log
  projects/              ← one JSON per project
  commitments/           ← one JSON per commitment
  tasks/                 ← one JSON per task; may name a parent commitment or project
  people/                ← one JSON per person/stakeholder
brain/                   ← shared memory entries (Markdown + YAML frontmatter)
```

Per [ADR-009](../04-decisions/ADR-009-structure-content-boundary.md), only some of this is
git-tracked. The tracked `_data/` entity directories hold a fictional example set that exercises
every schema; the owner's real portfolio lives at `_private/portfolio/` (gitignored) and is read
instead when `D_SYSTEM_DATA_ROOT=_private/portfolio` is set — see `data_root()` in
`src/db/source_validation.py`. `tags.json`, `ideas.jsonl` and `brain/` are shared structure rather
than portfolio content, and are always read from the tracked tree.

`ideas.jsonl` is append-only and written only by `tools/append_idea.py`; never edit it by hand.

### DuckDB: derived query layer (gitignored)

`data/d_system.duckdb` is rebuilt on demand from the source files by `tools/rebuild_db.py`. Never edit the DB directly — edit the JSON or Markdown files, then rebuild.

### Schema files: `schemas/` (JSON Schema for validation)

One schema per entity. The source preflight runs before every rebuild and enforces eleven of them:
the eight entity directories in `ENTITY_DIRECTORIES` (`src/db/source_validation.py`) — `project`,
`person`, `commitment`, `task`, `interaction`, `decision`, `waiting-on` and `development-event` —
plus `tag`, `memory` and `idea`, validated separately in the same module. The remaining schemas
cover capture, governance and backlog records and are checked elsewhere.

`sys-contracts` in [systems.yaml](systems.yaml) still describes this as six schemas and omits
`task`. It is stale; `src/db/source_validation.py` is the authority until a phase corrects it.

### DDL: `sql/001_schema.sql`, views in `sql/003_capture_views.sql`

Entity tables: `projects`, `people`, `tags`, `commitments`, `tasks`, `interactions`, `decisions`,
`waiting_on`, `development_events`, `memories`, `ideas`, `idea_events`, `idea_annotations`,
`idea_links`. Junctions: `project_people`, `project_tags`. Views: `project_activity`,
`project_last_touched`, `unfiled`.

Key relationships:
- Tasks are their own records in `_data/tasks/` and name their owning commitment by
  `commitment_id`; the rebuild loads them straight into the `tasks` table. Both parents are
  optional — a parentless task is intended, and the `unfiled` view exists to keep it visible
- `tags` field on project JSON is denormalized into both the `projects.tags` array column and the `project_tags` junction table
- `project_people` is populated from the `projects` array inside each person's JSON
- `ideas` is folded from the `idea_events` log rather than stored directly; read it through
  `src/db/ideas.py`, never by parsing the raw JSONL

## Backend Layout

```
src/
  main.py          # FastAPI app, CORS, router registration
  api/
    __init__.py    # APIRouter at /api/v1 — register route modules here
    routes/        # one file per domain
  db/
    connection.py        # get_db() context manager — yields a DuckDB connection
    source_validation.py # data_root() and the pre-rebuild schema preflight
    ideas.py             # the idea event log: fold(), legal_transitions()
  governance/      # the governance check — run as `python -m src.governance`
  capture/         # raw capture contracts
  demo/            # PTY adapter behind the live-demo terminal
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
    stage/          # live-demo stage page and its regions
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
| `sql/` | DuckDB DDL migrations and views |
| `_data/` | Tracked fictional example set, shared taxonomy and the idea log (ADR-009) |
| `brain/` | Shared model-agnostic memory entries |
| `templates/html/` | HTML page and component templates |
| `templates/styles/` | CSS / style definitions for template families |
| `templates/governance/` | Templates for governed documents |
| `test/` | pytest test suite |
| `tools/` | CLI and helper scripts; each is paired with an `OPS-*` document |
| `docs/00-working/` | Ungoverned staging for parked ideas |
| `docs/01-plans/` | Implementation plans (`PLAN-NNN-topic.md`) |
| `docs/02-prompts/` | AI prompt templates |
| `docs/03-sessions/` | Session logs |
| `docs/04-decisions/` | Architecture Decision Records (`ADR-NNN-topic.md`) |
| `docs/05-memories/` | Persistent cross-session context |
| `docs/06-requirements/` | Feature requirements (`REQ-NNN-topic.md`) |
| `docs/07-architecture/` | Architecture diagrams and docs |
| `docs/08-governance/` | Governance protocol, operations documents and the document catalog |
| `docs/09-backlog/` | The phase queue — the only place a phase is marked complete |
| `research/` | Reference material and review packs — tracked, ungoverned |
| `.claude/` | Skills, agents and slash commands |
| `data/` | Gitignored — the derived DuckDB file |
| `_working/` | Ephemeral working plans and task detail |
| `_tmpagent/` | Files agents in sibling worktrees must read |
| `_public/` | Shareable outputs |
| `_private/` | Gitignored — credentials, raw dumps, personal notes, and `portfolio/` (real records) |
