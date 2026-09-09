---
id: mem-concept-terms-data-and-storage
title: Data and Storage
type: concept
tags: []
systems: [sys-portfolio, sys-projection, sys-governance]
source_model: anthropic/claude-sonnet-5
project: d-system
created: 2026-09-07
updated: 2026-09-07
confidence: high
related: [mem-concept-json-sot, mem-concept-terms-memory-and-retrieval]
scope: global
---

Grouped definitions per [PROMPT-004](../../docs/02-prompts/PROMPT-004-terminology-and-architecture.md).

### Source of truth

The one location authoritative for a given fact — human-readable JSON under `_data/` for business
data, Markdown under `brain/` for durable memory. Not something that can drift from its own derived
copy: nothing is ever written back into it from a derived layer, so the direction of truth only ever
flows one way.

### Projection

The mechanical build step, `tools/rebuild_db.py`, that drops and recreates every DuckDB table from
`_data/` JSON and `brain/` Markdown. Not a store in its own right — it holds nothing that is not
already in the source of truth, so rerunning it is always safe and never lossy.

### Derived layer

Any read-optimized copy built from the source of truth rather than written to directly. DuckDB is the
current, and so far only, instance. Not editable — a change always goes to `_data/` or `brain/`, then
a rebuild, never the other direction.

### `_data/`

The tracked default data root: one JSON file per project, commitment and person, plus `tags.json` and
`ideas.jsonl`. Not the owner's actual portfolio by design — the tracked tree is meant to hold a
fictional exercise of every schema, and real records move to `D_SYSTEM_DATA_ROOT` once
`phase-priv-03` completes. As of this writing that move has not happened, so the tracked `_data/`
still holds real records. See `docs/04-decisions/ADR-009-structure-content-boundary.md`.

### `_public/`

Named in the directory reference as the location for shareable generated outputs. Not built yet — the
directory does not exist on disk today, and no tooling writes to it; this is an aspirational term,
recorded because it appears in `CLAUDE.md`.

### `_private/`

Gitignored storage for credentials, raw dumps and personal notes. Not scanned by the governance check
and not written to automatically by any tool — an agent reads or writes it only when the owner
directs it.

### `_working/`

Gitignored, ungoverned home for ephemeral plans — task detail for a phase that already exists. Not
archived and not deleted without the owner's explicit approval, even though nothing stops an agent
from doing so mechanically. See `docs/01-plans/PLAN-015-ephemeral-working-plans.md`.

### Portfolio

The collection of the owner's real project, commitment and person records — the content the system
exists to track. Not the same as `_data/`, which is presently their tracked location but is, by
decision, tracked *structure* rather than the portfolio's *content*. See
`docs/04-decisions/ADR-009-structure-content-boundary.md`.

### Entity (data sense)

One domain record type validated by a JSON Schema under `schemas/` — project, commitment, person,
tag, idea — one file per instance under `_data/`. Not the same as a memory `entity`, the `brain/`
memory type holding facts about a thing; see Memory and Retrieval for that sense.
