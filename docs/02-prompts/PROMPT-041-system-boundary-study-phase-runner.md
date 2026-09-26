---
schema_version: 1
id: doc-system-boundary-study-phase-runner
code: PROMPT-041
title: System boundary study phase runner
kind: prompt
status: active
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems:
  - sys-gov-docs
  - sys-backlog
depends_on:
  - doc-system-boundary-study
  - doc-system-boundary-study-requirements
---

# System boundary study phase runner

Use this prompt to continue the System Boundary Study one phase at a time. It is deliberately a phase runner, not permission to execute the whole study in one session.

## Authoritative references

- Study overview: `docs/01-plans/PLAN-050-system-boundary-study/PLAN-050-overview.md`
- Relevant child plan: resolve from the selected phase's `plan` field in `docs/09-backlog/backlog.yaml`
- Requirements: `docs/06-requirements/REQ-033-system-boundary-study.md`
- Resume log: `docs/00-working/boundary-study/phase-status.md`
- Repository workflow and safety rules: `AGENTS.md`

The child plan is the phase-local work brief. Do not read or execute every child plan unless the selected phase requires it. `AGENTS.md` overrides this prompt if they conflict.

## Prompt

> Resume the System Boundary Study using this runner. First read `AGENTS.md`, `docs/00-working/boundary-study/phase-status.md`, `docs/01-plans/PLAN-050-system-boundary-study/PLAN-050-overview.md`, and `docs/06-requirements/REQ-033-system-boundary-study.md`. Reconcile the status log against `docs/09-backlog/backlog.yaml`; the backlog is the authority for phase lifecycle state.
>
> Select only the earliest eligible unfinished study phase in this order: `phase-bnd-01`, `phase-bnd-02`, `phase-bnd-05`, `phase-bnd-03`, `phase-bnd-04`. A phase is eligible only when its dependencies are complete, it is queued or otherwise ready under the backlog rules, and no active-phase conflict or capacity limit prevents a claim. If none is eligible, report the precise blocker and do not begin another phase.
>
> Read only that selected phase's child plan, as resolved from its `plan` field, plus the backlog entry. Follow the repository claim-and-worktree protocol exactly. Work only within that phase's declared scope, deliverables, acceptance criteria, and verification commands. Do not silently broaden the study or start a second phase.
>
> Keep `docs/00-working/boundary-study/phase-status.md` useful as a concise resume log: after a valid claim, mark the selected row `in progress` with its branch and immediate next action. After work reaches a terminal handoff, append a dated history entry and update the row with the actual backlog state, branch/commit, session record, verification outcome, and the exact next action. Never mark the log `complete` until the backlog phase has been completed through the repository's owner-controlled closure process. If the branch is merely ready for review or integration, use `ready for owner review` instead. Do not put confidential identifiers in the log.
>
> Before handing off, run every required verification command and report its real result. Preserve the phase session record and all governance steps required by `AGENTS.md`. End by naming the selected phase, its status-log state, evidence, and the next eligible phase or blocker.

## Status-log contract

The status log is a tracked working aid, not a substitute for a backlog phase, session record, governed decision document, or the study's final report. Reconcile it rather than trusting it blindly. Keep one current row per study phase and short dated history entries; link to governed evidence instead of duplicating findings.
