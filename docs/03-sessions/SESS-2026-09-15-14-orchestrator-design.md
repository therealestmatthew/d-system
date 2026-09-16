---
schema_version: 1
id: doc-session-orchestrator-design
code: SESS-2026-09-15-14
title: Orchestrator child plan, daemon and watcher design
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-realization, sys-backlog]
depends_on: [doc-irs-orchestrator-design]
---

# Orchestrator child plan, daemon and watcher design

Owner-directed session with no backlog phase — **unclaimed**, branch `agent/plan-039-01`,
worktree `../d-system-worktrees/plan-039-01`. Follows `SESS-2026-09-15-13` in the same
conversation.

## What the session did

1. **Took two owner rulings** via `AskUserQuestion`, recorded as a round-3 finding on `000247`
   and committed on `dev` (`c6622d7`): begin with deeper design (the orchestrator child plan
   before any `phase-irs-*` build), and the process model is **daemon + watcher** — chosen with
   the P5 overlap explicitly presented.
2. **Wrote `PLAN-039.01` (orchestrator design)**. Its load-bearing choices: the pipeline is
   four run kinds (`intake`, `batch`, `unit`, `realization`) composed through repository
   records, not one long graph; the daemon's whole scheduler is a single `tick` callable, so a
   manual `tick` command is the degraded no-daemon mode and the test surface; gates are
   interrupts with decisions as inbox events whose durable truth is the repository artifact
   each decision produces; the daemon never merges and never invokes `/session-close`; the
   operational ledger is interim pending P5's run-ledger contract; watchers are repo-internal
   only, holding the `phase-auto-03` boundary.
3. **Applied the two backlog amendments the design forces**, in the same diff: `phase-irs-04`
   now names `doc-irs-orchestrator-design` as its plan (satisfying the open-plan-has-phases
   rule the validator raised), and `phase-irs-01` gains `depends_on: [phase-irs-04]`, since its
   dispatch mechanism was ruled to be the daemon's own watcher-plus-reconcile rather than a
   throwaway script.
4. Earlier in the same conversation, the `ARCH-006` page was placed at
   `_public/idea-realization-system.html` and integrated on the owner's instruction
   (`241e31a`).

## Verification, actual output

- `uv run python -m src.governance` — `Governance OK: 28 systems, 253 documents, 25 memories,
  274 backlog phases`. One validator rejection en route, fixed rather than bypassed: an open
  plan must own a phase (resolved by amendment 3 above, not by inventing a new phase).
- `uv run pytest` — `580 passed, 2 warnings`.

## Unresolved

- `PLAN-039.01` carries two open questions deferred to `phase-irs-04`: watcher library versus
  polling, and where the partition threshold lives (default on-demand-only until set).
- The plan is `draft`; the branch is ready for review: `git diff dev..agent/plan-039-01`.
