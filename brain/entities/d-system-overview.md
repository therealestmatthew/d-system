---
id: mem-entity-d-system
title: d-system Overview
type: entity
tags: [frameworks, knowledge-base, python, react]
source_model: anthropic/claude-sonnet-4-6
project: d-system
created: 2026-09-05
updated: 2026-09-05
confidence: high
related: [mem-concept-json-sot, mem-concept-tag-taxonomy]
scope: global
---

## What It Is

Personal consulting management system. Tracks people, projects, commitments, and tasks to reduce mental overhead. Also serves as a platform for HTML generation, reporting, and agentic workflow triggering.

## Stack

| Layer | Technology |
|---|---|
| Backend API | Python 3.14, FastAPI, Pydantic v2 |
| Database | DuckDB (file-based, `data/d_system.duckdb`) |
| Frontend | React 18, TypeScript, Vite |
| Package mgr | uv (Python), npm (Node) |

## Key Commands

```bash
uv sync --extra dev                    # install deps
uv run uvicorn src.main:app --reload   # API on :8000
uv run python tools/rebuild_db.py     # sync JSON+brain → DuckDB
uv run pytest                         # tests
cd ts && npm run dev                   # UI on :5173
```

## Data Architecture

Source of truth: `_data/` (JSON) + `brain/` (Markdown). DuckDB derived. See `mem-concept-json-sot`.

## Directory Map

```
src/          FastAPI app
ts/           React/TypeScript frontend
_data/        Source JSON (projects, commitments, people, tags)
brain/        Shared model-agnostic memory (this system)
schemas/      JSON Schema definitions
sql/          DuckDB DDL
tools/        CLI scripts (rebuild_db.py, load_context.py)
templates/    HTML and style templates
docs/         Plans, prompts, sessions, decisions, requirements, architecture
```

## Project Count (as of 2026-09-05)

33 projects across: work (8 active, 3 inactive), learning (3), system (12), personal (7).

## Model Compatibility

This repo is designed to be worked on by Claude (Anthropic), GPT-4o (OpenAI), and Gemini (Google) interchangeably. The `brain/` memory system is the cross-model continuity layer.
