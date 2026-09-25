---
schema_version: 1
id: doc-idea-realization-plugin-document-governance
code: PLAN-048.05
title: Idea-realization plugin — the document-governance engine
kind: plan
status: approved
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-documents]
depends_on: [doc-idea-realization-plugin, doc-governance-protocol, doc-document-code-protocol]
parent: doc-idea-realization-plugin
---

# The document-governance engine

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-05`. Covers `REQ-031` R16
and R17.

## Context and scope

`src/governance/codes.py` (parsing, allocation, catalog rendering) and `reservations.py` (the
exclusive-file reservation under the git common directory) are portable as they stand;
`__main__.py`'s `audit()` (lines 165–314) is the document scan, tied to `systems.yaml`,
`codes.yaml`, `_data/tags.json`, `brain/` and a hard-coded exempt list (analysis 04 §2, §7). The
mechanical section check for plans is a shell script inside `GOV-018` step 1 with no tool behind
it.

## Decisions

- **The document scan ports without memories and without tags.** `brain/` validation and the
  `tags` field's taxonomy check are this repository's; `REQ-031` R16 excludes memories. Rejected:
  porting them (a `brain/` and a `tags.json` in every target). Cost: a target that wants memories
  writes its own check.
- **The exempt list is `userConfig` (`exempt_files`)**, not code. Rejected: the literal list.
- **Kind-specific lifecycle sets live in one table in `scripts/documents.py`**, not split between
  schema and code as the source has them (analysis 04 §7, last risk). Rejected: copying the split.
- **`plan-check` is a script**, the shell check made a tool with the same table. Rejected: shipping
  the shell script (not testable in the suite).
- **The code register and systems registry ship empty**, as templates the scaffold copies.

## Work and dependencies

1. `scripts/codes.py`, `scripts/reservations.py`, `scripts/documents.py`;
   `scripts/checks/documents.py`; the `next-code`, `release-code` and `catalog` subcommands
   registered with `scripts/cli.py` (phase-plug-01's dispatcher).
2. Schemas: document, codes, systems; templates: `codes.yaml`, `systems.yaml`, requirement and
   plan documents.
3. `scripts/plan_check.py`.
4. Port `test_codes.py` (including the multi-worktree reservation tests), `test_governance.py`
   minus the tests that scan this repository, and add `plan_check` tests.

Prerequisite: `phase-plug-01`.

## Acceptance and verification

As the backlog entry states. The case that must fail: an unknown document kind; two worktrees
receiving the same code; a hand-edited catalog; a plan draft missing its boundaries section.

## Execution order

Runs after phase-plug-01, alongside phase-plug-02 (wave 2), on its own sub-system and files.

## Out of scope

Backlog rules (`phase-plug-04`), generators (`phase-plug-06`), memories, tags.

## Open questions

- Whether the catalog renders backlog phases (as the source's does) when the backlog feature is
  not scaffolded. Planner, in this phase; leans to rendering the section only when the backlog file
  exists.
