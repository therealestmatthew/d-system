---
schema_version: 1
id: doc-session-plan-quality-standard
code: SESS-2026-09-22-09
title: Plan-corpus audit and the plan and requirement quality standard
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-gov-docs]
depends_on: [doc-idea-graph-lifecycle]
---

# Plan-corpus audit and the plan and requirement quality standard

## Phase

`phase-idg-10` — Audit the plan corpus and write the plan-quality standard.

## Verification

```
$ uv run python -m src.governance
Governance OK: 35 systems, 320 documents, 30 memories, 293 backlog phases
```

Run in the worktree `/code/d-system-worktrees/phase-idg-10` after rebasing onto `dev` at `348bdae`.

The standard's mechanical plan check was also run by hand, from a scratch script implementing the
rule exactly as `GOV-010` states it, against eleven existing plans:

```
PLAN-001-agent-memory-system.md missing: ['Context', 'Design', 'Work', 'Verification', 'Boundaries', 'Open questions']
PLAN-002-mini-systems-proposal.md missing: ['Context', 'Design', 'Work', 'Verification', 'Boundaries', 'Open questions']
PLAN-005-document-code-system.md missing: ['Design', 'Boundaries']
PLAN-010-code-reservation-enforcement.md missing: ['Design', 'Boundaries']
PLAN-016-idea-record-system.md missing: ['Verification', 'Boundaries', 'Open questions']
PLAN-019-idea-priority-queue.md missing: ['Boundaries']
PLAN-020-portable-agent-workflows.md missing: ['Work', 'Boundaries', 'Open questions']
PLAN-026-concurrency-git-safety.md missing: ['Boundaries', 'Open questions']
PLAN-029-idea-graph-lifecycle.md missing: ['Boundaries', 'Open questions']
PLAN-038-backlog-status-regression-guard missing: ['Verification', 'Open questions']
PLAN-043-literature-review-report-page.m missing: ['Context', 'Verification', 'Open questions']
```

The standard applies only to documents written after it, so existing plans failing the check is
expected. The result shows the check runs and separates documents. It is not a compliance finding
against the corpus.

## Acceptance

- `REQ-014 R17 holds: every judgement names plans from the corpus on both sides.` — **Met.** Each of
  judgements P1–P10, Q1–Q5 and T1–T2, and the Length section, has a "Meets it" and a "Does not"
  list, each naming at least one document from `docs/01-plans/` or `docs/06-requirements/`.
- `The standard names a section list a later plan can be checked against mechanically.` — **Met.**
  `GOV-010` has tables of accepted headings, a stated match rule and a grep form. The hand-run check
  above is one implementation of that rule.
- `It is written so phase-idg-12 can measure a draft against it, which is what R20 requires of it.`
  — **Met.** The conformance rule is stated as required and conditional sections, with the
  condition for each named in terms of front matter (`depends_on` kind) or backlog facts (phase
  count).
- `The two bullets above … are judged by the session-close independent review, not by a mechanical
  command.` — **Met** in that the review below is that judgement. See `## Review`.

## Backlog

`status: active`, held by `agent-builder-a`. `next_action`: all acceptance conditions met and
reviewed. The branch awaits the owner's integration approval. Completion is written on `dev`
immediately after integration, per `GOV-003`'s coordinator-completion rule.

## Unresolved

- Integration onto `dev` has not happened and needs the owner's approval. Until it does, the phase
  cannot be marked complete (`GOV-003`, *Coordinator completion replaces owner-invoked
  /session-close*, condition 3).
