---
id: mem-concept-terms-data-and-storage
title: Data and Storage
type: concept
tags: []
systems: [sys-portfolio, sys-projection, sys-governance]
source_model: anthropic/claude-sonnet-5
project: d-system
created: 2026-09-07
updated: 2026-09-23
confidence: high
related: [mem-concept-json-sot, mem-concept-terms-memory-and-retrieval]
scope: global
---

Grouped definitions per [PROMPT-004](../../docs/02-prompts/PROMPT-004-terminology-and-architecture.md).

### Source of truth

The one location authoritative for a given fact — human-readable JSON under the data root for
business data (`D_SYSTEM_DATA_ROOT` if set, else the tracked `_data/`), the tracked `_data/tags.json`
and `_data/ideas.jsonl` for shared taxonomy and the idea log, and Markdown under `brain/` for durable
memory. Not something that can drift from its own derived copy: nothing is ever written back into it
from a derived layer, so the direction of truth only ever flows one way. See
`docs/04-decisions/ADR-009-structure-content-boundary.md`.

### Projection

The mechanical build step, `tools/rebuild_db.py`, that validates every source file and then drops
and recreates every DuckDB table from the data root's entity JSON, the tracked `tags.json` and
`ideas.jsonl`, and `brain/` Markdown. Not a store in its own right — it holds nothing that is not
already in the source of truth, so rerunning it is always safe and never lossy.

### Derived layer

Any read-optimized or rendered copy built from the source of truth rather than written to directly:
the DuckDB database, and the generated files `docs/08-governance/catalog.md`,
`docs/08-governance/GLOSSARY.md`, `docs/00-working/ideas.md` and `_public/overview/index.html`. Not
editable — a change always goes to the source, then a rebuild or regeneration, never the other
direction.

### `_data/`

The tracked default data root: a fictional example set with one JSON file per record under
`projects/`, `people/`, `commitments/` and `tasks/`, plus workbench layouts under `workbench/`, the
shared `tags.json`, and the append-only idea log `ideas.jsonl`. Not the owner's actual portfolio —
real records live under `_private/portfolio/` and are read when `D_SYSTEM_DATA_ROOT` points there;
`tags.json` and `ideas.jsonl` are always read from here regardless. See
`docs/04-decisions/ADR-009-structure-content-boundary.md`.

### `_public/`

Tracked home for shareable generated outputs — HTML pages such as the overview page
(`_public/overview/index.html`, written by `tools/generate_overview.py`) and the SVG diagrams under
`_public/images/`. Not a source of truth: a page here is rendered from data or templates elsewhere and
is regenerated rather than edited.

### `_private/`

Gitignored storage for the owner's real portfolio records (`_private/portfolio/`), credentials, raw
dumps and personal notes. Not scanned for documents by the governance check, but its portfolio
records are read and validated when `D_SYSTEM_DATA_ROOT` points at them; no tool writes to it
unless the owner directs it. See `docs/04-decisions/ADR-009-structure-content-boundary.md`.

### `_working/`

Gitignored, ungoverned home for ephemeral plans — task detail for a phase that already exists. Not
archived and not deleted without the owner's explicit approval, even though nothing stops an agent
from doing so mechanically. See `docs/01-plans/PLAN-015-ephemeral-working-plans.md`.

### Portfolio

The collection of the owner's real records — projects, people, commitments, tasks and the other
entity types — that the system exists to track, kept under `_private/portfolio/`. Not the same as
`_data/`, which is tracked *structure* and a fictional example set rather than the portfolio's
*content*. See `docs/04-decisions/ADR-009-structure-content-boundary.md`.

### Entity (data sense)

One domain record type validated by a JSON Schema under `schemas/` — project, person, commitment,
task, interaction, decision, waiting-on and development event, one JSON file per record under the
data root (the list is `ENTITY_DIRECTORIES` in `src/db/source_validation.py`). Not the same as a
memory `entity`, the `brain/` memory type holding facts about a thing; see Memory and Retrieval for
that sense. Tags and ideas are also schema-validated but are not entities: each lives in one shared
tracked file.
