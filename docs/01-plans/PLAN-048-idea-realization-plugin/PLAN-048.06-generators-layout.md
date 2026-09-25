---
schema_version: 1
id: doc-idea-realization-plugin-generators-layout
code: PLAN-048.06
title: Idea-realization plugin — generators, layout reference and the agreement templates
kind: plan
status: draft
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-generators]
depends_on: [doc-idea-realization-plugin]
parent: doc-idea-realization-plugin
---

# Generators, layout reference and the agreement templates

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-06`. Covers `REQ-031` R18
and R19.

## Context and scope

`tools/generate_tool_docs.py` (209 lines, `ast` only) pairs tools to operations documents by
filename and fills a marked block; `tools/generate_agent_workflows.py` (347 lines, `pyyaml`)
renders host adapters from `agent-workflows/workflows.yaml`. Both are content-agnostic; the
shipped manifest is not (analysis 04 §4). `AGENTS.md` and `CLAUDE.md` mix portable rules with this
repository's stack, data model and history (analysis 04 §5 lists each rule and its class).

## Decisions

- **Both generators take input and output roots as arguments**; nothing is derived from
  `__file__`. Rejected: copying with the paths edited.
- **The workflow manifest ships as a template with no entries**; the plugin's own skills are not
  generated through it, because a plugin's skills are its files, not a target's. Rejected: shipping
  the source manifest (eight of this repository's workflows as baggage).
- **The templates carry only the rules analysis 04 §5 classes as portable**, with four
  placeholders (`integration_branch`, `worktree_dir`, `data_root`, `confidential_dir`). Rejected:
  a full `AGENTS.md` with this repository's stack section (R02). Cost: a target adds its own stack
  and layout sections by hand, which the template's comments say.
- **The layout reference documents the directory tree the scaffold creates and why each directory
  exists**, including the manual phase-id convention (track prefix, two-digit sequence, a track
  table in the backlog README).

## Work and dependencies

1. `scripts/generate_tool_docs.py`, `scripts/generate_workflows.py`; port their tests.
2. `templates/workflows.yaml`, `templates/AGENTS.md`, `templates/CLAUDE.md`; `docs/repository-layout.md`.
3. `scripts/render_template.py` (placeholder substitution) and the test that renders both templates
   and runs the R02 check over the output.

Prerequisite: `phase-plug-05` (the operations-document convention the tool-docs generator pairs
against).

## Acceptance and verification

As the backlog entry states. The case that must fail: a hand edit inside a generated block; a
rendered template containing `{{`.

## Execution order

Runs after phase-plug-05, alongside phase-plug-03 and phase-plug-04 (wave 3), on its own sub-system and files.

## Out of scope

The governance documents themselves (`phase-plug-07`); the pre-commit hook (a target installs it
with consent through the scaffold, `phase-plug-01`).

## Open questions

- Whether the private-content check ports. Its mechanism is generic but its identifier source is
  this repository's portfolio layout (analysis 04 §4). Planner, in this phase; leans to porting the
  path-prefix half only, with `confidential_dir` as the prefix.
