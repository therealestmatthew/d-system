---
schema_version: 1
id: doc-terminology-architecture-prompt
code: PROMPT-004
title: Define the vocabulary and document the system architecture
kind: prompt
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-brain, sys-retrieval, sys-governance, sys-contracts]
depends_on: [doc-terminology-system]
---

# Define the vocabulary and document the system architecture

## How to use this

Open a fresh session in this repository and say:

> Read `docs/02-prompts/PROMPT-004-terminology-and-architecture.md` and follow it.

This session **writes content**. It is not a definition-first session like
[PROMPT-002](PROMPT-002-capture-and-structuring-system.md), and it does not produce a requirement or
a plan — [PLAN-012](../01-plans/PLAN-012-terminology-system.md) already governs the system this
content lives in.

**Run it before [PROMPT-003](PROMPT-003-systems-review.md).** The review argues about complexity, and
that argument needs shared vocabulary and an accurate picture of what exists. The reasoning is
circular only in appearance: this session describes what *is*, the review then decides what *should
be*. Expect the review to prune, consolidate or split some of what this session documents, and treat
that as the process working rather than as wasted effort.

## Why this exists

Within one day the system acquired governed plans and ephemeral plans, phases and tracks, systems and
subsystems, five memory types, four content folders with different rules, and document kinds, codes
and series. Three consecutive scope-creep corrections traced back to the same root: **no shared
definition of what a plan is**, so each judgement was re-derived and reached a different answer.

Vocabulary is not documentation overhead here. It is the thing whose absence has already cost three
corrections in a day.

## Part 1 — Build the scaffolding first

Nothing is written until the structure exists. Per PLAN-012:

1. Add a `systems` field to `schemas/memory.schema.json`, validated against `systems.yaml`, mirroring
   what governed documents carry. This is what makes subsystem-scoped retrieval possible — folders
   cannot do it, because `tools/load_context.py` never reads paths.
2. Add a `--system` filter to `tools/load_context.py`.
3. Write `tools/generate_glossary.py`. **Deterministic**, and built to emit *several* glossaries
   filtered by tag or domain even though only one is needed today.
4. Add a test asserting the committed glossary matches regenerated output, in the same shape as the
   existing catalog test.

## Part 2 — Define the vocabulary

Definitions are canonical in `brain/concepts/`, grouped by domain rather than one file per term.
Every definition is **one sentence of what it is, one of what it is not, and a pointer to the
governing document.** Anything longer belongs in its own concept memory that the glossary links to.

Terms known to need definitions — not exhaustive, and the session should add what it finds:

**Plans and work**
`governed plan` · `ephemeral plan` · `phase` · `track` · `next_up` · `session budget` ·
`next action` · `acceptance` · `verification` · `deliverable` · `completion evidence`

The plan distinction is the one that has already cost three corrections. Its source is
[PLAN-015](../01-plans/PLAN-015-ephemeral-working-plans.md): a governed plan says how the system
should work and outlives the work; an ephemeral plan says how one task gets done and dies with it.

**Documents and governance**
`governed document` · `document kind` · `code` · `series` · `catalog` · `reserved code` ·
`retired code` · `governance check` · `document code allocation`

**Data and storage**
`source of truth` · `projection` · `derived layer` · `_data` · `_public` · `_private` · `_working` ·
`portfolio` · `entity`

State plainly for each of the four folders **what decides that a new file belongs there**, and say so
if two would accept the same file. `_working/` is ungoverned by design — governance walks only
`docs/` and `brain/`.

**Memory and retrieval**
`brain` · `memory type` · `concept` · `entity` · `procedure` · `episode` · `decision` · `scope` ·
`confidence` · `source model`

**Systems**
`system` · `subsystem` · `domain` · `system status`

## Part 3 — Document the architecture

**One architecture overview**, governed, describing the program as a whole: what it is for, what the
subsystems are, how they depend on each other, and where data flows. This is the document a new
reader — human or model — should be given first.

**Then enrich `systems.yaml`.** Each entry's `description` should say what the subsystem does, what
it does *not* do yet, and what it depends on. Several entries are `planned` or `scaffold` with no
code; say so plainly rather than describing intent as though it were built.

**Do not write a per-subsystem architecture document yet.** Those come later, per subsystem, once one
is properly established and persists. Writing sixteen now would document aspiration, and
[PROMPT-003](PROMPT-003-systems-review.md) already asks whether `systems.yaml` is a live registry or
an aspirational map — that question should be answered before it is duplicated across sixteen files.

## Part 3b — Document the governance that exists

**Describe only.** Do not redesign it — that is
[PROMPT-005](PROMPT-005-governance-model-review.md), which asks whether governance is a kind, a
system, or both.

State what each governed document does and what it governs: `GOV-001` through `GOV-006`, `OPS-001`,
`codes.yaml`, `systems.yaml`, `catalog.md`, and the governance check itself. Say plainly for each
whether it is **mechanically enforced** or **convention** — that distinction is currently invisible
and is one of the questions PROMPT-005 will take up.

## Part 3c — Document the tooling that exists

**Describe only**, and do not build the per-tool documents — that is
[PLAN-013](../01-plans/PLAN-013-tooling-documentation.md).

For `tools/rebuild_db.py` and `tools/load_context.py`, record what each is for, what it reads and
writes, and how it fails. This feeds PLAN-013 rather than pre-empting it, and it gives the
architecture overview something accurate to say about the data flow.

## Part 4 — Verify

- `uv run python -m src.governance` exits 0.
- `uv run pytest` passes, including the new glossary-regeneration test.
- `uv run python tools/load_context.py --system sys-backlog` returns the backlog vocabulary.
- The generated glossary is regenerated and committed; no hand edits.

## What this session must not do

- **Do not hand-write the glossary.** It is generated. A hand-edited glossary is a second source of
  truth and will drift.
- **Prefer the `systems` field over subsystem folders**, but do not treat folders as forbidden. An
  earlier claim that governance blocks them was wrong: `__main__.py:226` is a prefix test, so
  `brain/concepts/<system>/file.md` passes today. Nesting under the type directory is allowed if it
  helps a human browse; it is just not what makes retrieval work, since
  `tools/load_context.py` never reads paths.
- **Do not define terms for things that do not exist.** If a term names something aspirational, say
  so in the definition.
- **Do not add a new system, kind or folder.** If something is missing, record it as a finding for
  the systems review.
