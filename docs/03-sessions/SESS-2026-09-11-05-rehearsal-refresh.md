---
schema_version: 1
id: doc-session-rehearsal-refresh
code: SESS-2026-09-11-05
title: Rehearsal refresh (phase-wb-07) checkpoint
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-demo-stage]
depends_on: [doc-workbench]
---

# Rehearsal refresh (phase-wb-07) checkpoint

## Phase

`phase-wb-07` — Rehearsal refresh: runbook, Windows checks, owner-driven timing.

## Verification

- `uv run python -m src.governance` (orchestrator run, in the worktree):
  ```
  Governance OK: 18 systems, 163 documents, 16 memories, 119 backlog phases
  ```
- `uv run python tools/check_no_private_content.py` with the changes staged (orchestrator
  run, in the worktree):
  ```
  note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
  check_no_private_content: OK (497 tracked files, 0 identifiers checked)
  ```
- Playwright rehearsal pass over the runbook's browser-marked steps (demo-validator-web,
  pack W07-W): not run — this is the coordinator's dispatch, not this orchestrator's.
- The executed Windows checklist and both dry-runs' recorded times in the runbook:
  not run — owner-machine, owner-driven work; not performed by any agent.
- W07-C1 (demo-creator-docs): rewrote `docs/00-working/demo-runbook.md` and
  `docs/00-working/demo-windows-setup.md` against the final workbench UI (commit `0855033`).
- Talking-points finalization (this orchestrator, its own authored prose per its charter):
  finalized the presenter-facing step copy over the creator's skeleton (commit `7b4f663`),
  then fixed after a runbook gap found by rehearsal pass 1 (commit `110f421`).
- W07-V1 (demo-validator-code), first pass: **FAIL** — one finding: both Dry-Run `/orient`
  rows' narration described the notes strip as "carrying my talking points," reattaching the
  retired "talking points" panel label (REQ-007 W01) to the presenter's scripted narration.
  Fixed directly by this orchestrator (audience-facing prose is its own to write, not a
  creator/validator fix-cycle item) — commit `84001d6`.
- W07-V1, re-validation: **PASS**, no findings. Confirmed the "talking points" phrase no
  longer appears anywhere in either document, the step shape (commands/fallback/timebox)
  holds, timeboxes sum to 15m, Windows checklist covers all five required items, and
  `tools/demo_reset.py`/OPS-013 remain untouched by the diff.
- Agent-driven rehearsal pass 1 (W07-R, `demo-validator-web`): completed and recorded in the
  runbook (commit `47a81d3`). Three findings, one addressed (the `/orient` step now
  instructs starting a `claude` session before `/idea`); two left as noted, non-blocking
  observations (the `_parked` skill entry rendering in the dropdown; the ~85s `/orient`
  measurement against its 1m timebox, attributed to cold-start latency rather than the
  live-segment's on-stage time).
- Agent-driven rehearsal pass 2 (W07-R), attempt 1: dispatched after a fresh
  `demo_reset.py prepare`; truncated by its turn limit mid-investigation of a "collapse"
  finding before delivering a final report. No `SendMessage` tool was available to this
  orchestrator to resume the truncated agent (despite the task-notification instructing
  its use), so a fresh general-purpose agent was asked to pick up the work; it correctly
  reported it had no memory of the original investigation rather than fabricating a report,
  and flagged an unverified observation (a blank terminal panel in its own screenshots) it
  declined to characterize without further driving the browser.
- Agent-driven rehearsal pass 2 (W07-R), attempt 2: worktree state cleaned (stray
  backend/frontend processes on 8010/5180 killed, `demo_reset.py restore` then a fresh
  `prepare` run), dispatched again from a clean state with an explicit instruction not to
  get sidetracked by side findings before completing the full step-by-step pass. Truncated
  again by its turn limit mid-investigation of the zero-scroll/viewport checks, before
  delivering a final report.
- Per the binding two-cycle rule (no third quiet retry), this orchestrator stopped after
  the second truncated attempt and is reporting the blocker up rather than dispatching a
  third time. Worktree cleaned again afterward: stray servers killed, `demo_reset.py
  restore` run, `git status` confirmed clean with no stray artifacts from either aborted
  attempt.

## Acceptance

- The runbook describes the workbench UI only, with per-step commands, fallbacks and
  timeboxes summing inside 15 minutes (REQ-007 W13) — **Met**: W07-V1 passed clean on
  re-validation confirming this exact obligation, quoting the step rows and the 15m total.
- The R06 smoke check and both shell round-trips are recorded as passing on the
  presentation machine — **Not met**: owner-machine, owner-driven work not yet performed by
  the owner. Cannot be performed by an agent.
- Both owner-driven dry-runs complete within 15 minutes with every step inside its timebox,
  per-step times recorded — the REQ-006 R09 conditions deferred from phase-demo-05 are
  closed, not re-deferred — **Not met**: owner-driven work not yet performed. The
  agent-driven mechanics-check passes (pack W07-R) are explicitly distinct from these and
  do not close R09 per the runbook's own labeling; pass 1 is recorded, pass 2 is not yet
  completed after two truncated dispatch attempts.

## Backlog

- `status: active`, `agent: agent-demo-content`.
- `next_action`: W07-C1, talking points, W07-V1 (pass on re-validation) and agent-driven
  rehearsal pass 1 are done. Agent-driven rehearsal pass 2 (W07-R) has been dispatched
  twice and truncated by its turn limit both times before reporting, without a SendMessage
  tool available to resume the truncated agent; a third dispatch was withheld per the
  no-third-retry rule and reported up. Once pass 2 completes and is recorded, dispatch
  W07-G, then the owner-machine Windows checks and both timed dry-runs remain outstanding,
  owner-driven only.
- `result`: see `backlog.yaml`'s `result` field for this phase, mirrored from the same
  facts recorded above.

## Unresolved

- Agent-driven rehearsal pass 2 (pack W07-R) has not completed: two dispatch attempts, both
  truncated by the subagent's turn limit mid-investigation before delivering a final
  step-by-step report. This orchestrator has no `SendMessage` tool in its current toolset
  to resume a truncated agent as the standing lesson (idea `000077`) requires, and stopped
  short of a third dispatch per the binding two-cycle rule. Reported up as a blocking
  finding: the coordinator should decide whether to grant a larger turn budget for this
  dispatch, split it into smaller sub-checks, or otherwise resolve the resume-tooling gap.
- W07-G (phase gate) has not been dispatched — it depends on pass 2 being recorded first.
- The owner-machine, owner-driven items (REQ-006 R06 terminal smoke check, the CMD and
  PowerShell round-trips of REQ-007 W12, and both owner-driven timed dry-runs closing
  REQ-006 R09) remain entirely outstanding. None of these can be performed by an agent;
  they close only on the owner's own recorded results in the runbook and Windows checklist.
