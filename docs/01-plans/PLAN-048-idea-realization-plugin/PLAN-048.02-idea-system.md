---
schema_version: 1
id: doc-idea-realization-plugin-idea-system
code: PLAN-048.02
title: Idea-realization plugin — the idea system
kind: plan
status: draft
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-ideas]
depends_on: [doc-idea-realization-plugin, doc-idea-node-classification]
parent: doc-idea-realization-plugin
---

# The idea system

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-02`. Covers `REQ-031` R08 to
R12 and R23.

## Context and scope

The source is `src/db/ideas.py` (377 lines, stdlib only), `tools/append_idea.py` (488 lines,
`jsonschema`), `tools/generate_ideas_md.py` (180 lines, `pyyaml`), `src/governance/idea_priority.py`
(38 lines, pure), `schemas/idea.schema.json`, and the three workflow sources under
`agent-workflows/`. Analysis 01 §2 lists fourteen coupling points; §7 lists ten risks, the first
being the `src` package collision. `phase-idg-01` changes the schema (record kind, four axes,
`lifecycle_remedy`, `decompose`, confidence and reason per axis, provenance; `lineage` annotation
kind; `component_of` link type; `delivered`, `resolved`, `absorbed` statuses; `promoted`
non-terminal) — analysis 01 §5.

## Decisions

- **Port after `phase-idg-01`, from the commit it landed.** Rejected: porting now and re-porting
  later (two ports of the writer). Cost: this phase waits.
- **`scripts/ideas.py` keeps `fold`'s logic byte-for-byte where it can**; only path handling and
  imports change. Rejected: a rewrite. Cost: none; the rule is that a folded state here and there
  are identical for the same log, and a test asserts it on a fixture.
- **The triage search surface is `triage_search`, a list of paths relative to the target root.**
  Rejected: the source's four literal paths. Cost: a target without documents gets an agent that
  finds nothing and says so, which is the correct finding.
- **The vocabulary document is generated from the schema by a test's inverse**: the test parses the
  document's tables and compares to the schema's enums, so the document is hand-written but cannot
  drift. Rejected: generating the document (a generator for one file).

## Work and dependencies

1. Copy the landed schema; write `scripts/ideas.py`, `scripts/idea.py` (the writer's CLI),
   `scripts/render_ideas.py`; the ideas half of `scripts/check.py` (priority queue, rendered-view
   staleness).
2. Port the writer, fold, render and priority tests to temporary logs; drop the tests that read
   this repository's committed files (analysis 01 §6 names them).
3. `docs/vocabulary.md` and its test.
4. `skills/idea/SKILL.md`, `skills/idea-triage/SKILL.md`, `agents/idea-triage.md` from the
   workflow sources, every `uv run python -m src.governance` replaced by the plugin's `check`,
   every provenance citation removed.

Prerequisites: `phase-plug-01` (paths, suite, R02 check) and `phase-idg-01`.

## Acceptance and verification

As the backlog entry states. The case that must fail: an `open → promoted` transition without
`--promoted-to` is refused; a second discard after the one revisit is refused; the vocabulary test
fails on a fixture document missing one status.

## Execution order

Runs after phase-plug-01 and phase-idg-01, alongside phase-plug-05 (wave 2). Its deliverables are its own files under the plugin, and `scripts/checks/ideas.py` is its module of the check dispatcher, so it shares no path with a peer.

## Out of scope

The partition corpus builder (`phase-plug-03`), the triage dispatcher `tools/idea_dispatch.py`
(not ported), the DuckDB projection.

## Open questions

- Whether `render` also emits the four-axis values per idea in the rendered view. Planner, in this
  phase, after reading what `phase-idg-01` renders; leans to matching it.
