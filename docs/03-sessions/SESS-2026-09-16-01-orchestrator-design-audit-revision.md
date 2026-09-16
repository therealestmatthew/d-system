---
schema_version: 1
id: doc-session-orchestrator-design-audit-revision
code: SESS-2026-09-16-01
title: Orchestrator design audit and revision
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-backlog, sys-governance]
depends_on: [doc-irs-orchestrator-design]
---

# Orchestrator design audit and revision

Owner-directed session with no backlog phase — **unclaimed**, branch `agent/plan-039-01-rev`,
worktree `../d-system-worktrees/plan-039-01-rev`. Continues `SESS-2026-09-15-14`.

## What the session did

1. **Ran the owner-requested Opus audit** of `PLAN-039.01`. It returned **11 blockers, 17
   majors, 10 minors — all accepted**. The most consequential: the log's event is `created`,
   not `add`; the first tick would have dispatched 41 unattended triage runs before the broker
   exists, against `PLAN-032`'s broker-first ruling; `attempts`/`budget` in graph state
   contradicted `ADR-018`'s disposable-checkpoint claim; LangGraph has no fast-forward/rollback
   of a checkpointed thread (the correct mechanism is abandon-and-re-key); interrupt resume
   replays the containing node, so gate nodes must contain only their interrupt; the audit
   trail lived in gitignored, worktree-local, rebuild-clobbered `data/`; the unit run silently
   skipped the session record, `_tmpagent` releases and rebase-then-green; honoring `ADR-003`
   implied unacknowledged daemon commits on `dev`; nothing built the `batch` and `realization`
   graphs; and the earlier `phase-irs-01` amendment had quietly inverted the owner's
   stopgap-buildable-immediately ruling.
2. **Took four owner rulings** (round 4, via `AskUserQuestion`, recorded on `000247`,
   committed `b5bd538`): strict broker-first (`phase-irs-04` gains `phase-auto-02`);
   the durable ledger is a tracked `_data/runs.jsonl` with schema and sanctioned writer, its
   future remote/MCP home captured as idea `000250`; the stopgap inversion is undone
   (`phase-irs-01` standalone again); and the daemon proposes while a human commits every
   `dev` write.
3. **Captured `000250`** (MCP-mediated remote home for ledger and write mediation) and
   annotated `000248` (the generic-host seam does not exist yet, audit M16) and `000249`
   (external ingress is blocked by the sanctioned-writer rule, audit M17).
4. **Rewrote `PLAN-039.01`** integrating every finding: the intake row against the real idea
   state machine with a creation watermark; re-keying replacing fast-forward/rollback;
   three-field state with `attempts`/`budget` folded from the ledger; empty-wrapper gate
   nodes; tick-takes-the-lock with `flock` semantics; `Send` fan-out with per-plan G3 and
   amend-as-re-key; tracked ledger and decision inbox with writer discipline; the
   propose-then-observe `dev` model with the validator's capacity law and the unit run's
   explicit hand-off duties; budget semantics; the realization trace recorded at
   registration time; the kill switch at `_working/orchestrator-halt`; primary-checkout-only
   daemon; the orchestrator's own failure-path table; and the honest note that `000248`'s
   seam does not exist yet.
5. **Amended the surrounding set in the same diff**: `phase-irs-01` restored standalone with
   the ruled mechanism; `phase-irs-04` rewritten (four-kind scope, broker dependency, ledger
   deliverables, new acceptance); new `phase-irs-14` (batch graph) and `phase-irs-15`
   (realization graph); `phase-irs-12` gains both as dependencies; `phase-irs-11`'s
   next_action updated to the ruled kill-switch location; `REQ-022` R16's verification
   re-stated for three-field state; `PLAN-039`'s phase table, count and critical path
   updated; `sys-realization` paths gain `PLAN-039.01`.

## Verification, actual output

- `uv run python -m src.governance` — `Governance OK: 28 systems, 254 documents, 25 memories,
  276 backlog phases`.
- `uv run pytest` — `580 passed, 2 warnings`.

## Unresolved

- `PLAN-039.01` remains `draft`; two open questions stand (watcher library vs poll; where the
  partition threshold lives), both deferred to `phase-irs-04` by design.
- Audit m7's six-check discipline is partially applied (failure-path table added, authority
  and trace-through reflected in §§1, 6); a formal six-check pass belongs to this document's
  G3-category approval.
- The branch is ready for review: `git diff dev..agent/plan-039-01-rev`.
