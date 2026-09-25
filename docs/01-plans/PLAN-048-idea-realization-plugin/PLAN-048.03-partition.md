---
schema_version: 1
id: doc-idea-realization-plugin-partition
code: PLAN-048.03
title: Idea-realization plugin — the partition sweep
kind: plan
status: draft
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin]
depends_on: [doc-idea-realization-plugin]
parent: doc-idea-realization-plugin
---

# The partition sweep

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-03`. Covers `REQ-031` R13.

## Context and scope

The source is `agent-workflows/partition-ideas.md` (386 lines), the two agent charters,
`tools/build_idea_corpus.py` (364 lines), the six dispatch blocks in `PROMPT-034`, and
`schemas/idea-partition-record.schema.json`. Analysis 02 §2 gives the sequence: preflight, open-set
gate, corpus, R1 and R4 in parallel, gate 1, A1, gate 2, synthesis, the audit-2 stop, A2, the gate
checklist, gate 3. §6 records that audit 2 is blocked here: the adversary runs in the primary
checkout and the draft is in the coordinator's worktree.

## Decisions

- **The synthesis draft is written to `<primary checkout>/<staging>/idea-partition-<date>.md`**,
  where the primary checkout comes from `git worktree list --porcelain` and the staging directory
  from `userConfig`, and the A2 dispatch names that absolute path. Rejected: shipping the block
  and dropping audit 2 (D8 in the overview). Cost: the draft exists in two trees until the sweep
  closes; the gate-3 checklist copies the accepted version back to the worktree.
- **The prompt pack becomes `docs/partition-pack.md` with the six fenced blocks unchanged in
  substance** and every citation of this repository's documents, phases and ideas removed
  (R02). Rejected: keeping the citations as "precedent" (they name things a target does not
  have). Cost: the pack loses its provenance, which the trace table in `phase-plug-07` keeps here.
- **The exclusion file is optional and off by default.** The source's demo-lane exclusion is this
  repository's; the flag stays for a target that wants one.

## Work and dependencies

1. `scripts/idea_corpus.py` with `--status`, `--out`, `--exclude`; test on a fixture log.
2. `docs/partition-pack.md`; `agents/partition-analyst.md`; `agents/partition-adversary.md`.
3. `skills/partition-ideas/SKILL.md` with the resolved audit-2 step and the primary-checkout path
   rule.
4. `schemas/idea-partition-record.schema.json` and a fixture-record test (none exists in the
   source — analysis 02 §5).

Prerequisite: `phase-plug-02` (fold, the log, the writer for the open-set gate).

## Acceptance and verification

As the backlog entry states. The case that must fail: a record with a seven-digit idea id fails the
schema test; the R02 check fails on a pack that still names a source document.

## Execution order

Runs after phase-plug-02, alone on sys-plugin. Every plugin phase shares `sys-plugin` and the `plugins/idea-realization/` deliverable path, so the validator allows one at a time; the overview's Execution order section gives the full sequence.

## Out of scope

Running a sweep (that is `phase-plug-08`'s exercise); the token-ceiling enforcement the source
defers; this repository's own audit-2 ruling.

## Open questions

- Whether the plugin's R1/R4 analysts are the `partition-analyst` type or a plugin-local copy with
  the same tools. Planner, in this phase; leans to the plugin-local copy, since a plugin cannot
  depend on a target's agents.
