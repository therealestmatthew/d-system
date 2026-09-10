---
schema_version: 1
id: doc-session-demo-content-runbook-reset-rehearsals
code: SESS-2026-09-10-07
title: Demo content, runbook, reset tool and rehearsals
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage, sys-demo-overview]
depends_on: [doc-live-demo]
---

# Demo content, runbook, reset tool and rehearsals

## Phase

`phase-demo-05` — Demo content, runbook, reset tool and rehearsals.

## Verification

`uv run pytest`
```
495 passed, 2 warnings
```

`uv run ruff check src/ test/`
```
All checks passed!
```

`uv run mypy src/`
```
Success: no issues found in 23 source files
```

`uv run python -m src.governance`
```
Governance OK: 18 systems, 139 documents, 15 memories, 112 backlog phases
```

`uv run python tools/check_no_private_content.py` with the changes staged
```
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (437 tracked files, 0 identifiers checked)
```

Adversarial review (demo-adversary, pack D05-A) — not run this session. Dispatched by the
coordinator at PROMPT-015 step 8, not by this orchestrator, per the demo-track completion gate
(GOV-003).

Playwright rehearsal pass over the runbook's browser-marked steps (demo-validator-web, pack
D05-W) — not run this session, same reason.

Two fresh-eyes rehearsal passes (demo-validator-code, pack D05-R, dispatched by this
orchestrator) were run cold against `docs/00-working/demo-runbook.md`, separated by
`uv run python tools/demo_reset.py prepare`. Both passes' per-step times and findings are
recorded in the runbook itself (Dry-Run 1, Dry-Run 2 and Rehearsal Findings sections). Summary:
CLI-executable steps measured 10s (pass 1, partial) and 14s (pass 2, partial) against their
timeboxes — well inside budget for the steps that could run — but `/idea-triage`'s subagent half
could not be executed by either rehearsal agent (forbidden from dispatching subagents), so no
pass produced a complete, real 15-minute total.

The coordinator resolved the branch's diff-scope mismatch directly on `dev` (commit `9753a88`:
declared `_data/ideas.jsonl`, `docs/00-working/ideas.md` and `_public/overview` as this phase's
deliverables) and cleared the stray dev-server port collision. This orchestrator then applied a
one-commit fix cycle (`e1e3886`, pre-rebase) addressing all four Rehearsal Findings as narrative
and procedure corrections to `docs/00-working/demo-runbook.md` — no tool changed:
- `/orient` gained an explicit port-free precondition (`ss -tlnp | grep -E "8010|5180"`).
- `overview-skill rebuild` no longer references the nonexistent `/overview-build`; it now
  describes the real live-segment action (build/invoke the `d-system-overview` skill live), with
  `uv run python tools/generate_overview.py` as the concrete fallback command.
- `overview-skill rebuild`'s Step Markers entry states the parked-skill design plainly: `prepare`
  parks the pre-built skill on purpose so the live rebuild is real, and `restore` is the named
  fallback.
- `/idea-triage`'s Step Markers entry now states its discovery half is CLI-measurable and its
  subagent-dispatch half runs only in the presenter's own Claude Code session, so a rehearsal
  agent records it as partially measured, not failed.

The branch was then rebased onto `dev` at `9753a88` (`git rebase`, one conflict in
`docs/09-backlog/backlog.yaml` resolved by keeping both sides — the widened deliverables list from
`dev` and this session's record/next_action — no conflict occurred in `_data/ideas.jsonl`; its
append-only invariant was independently confirmed: `dev`'s log had 374 lines, this branch's has
377, and `git diff dev...HEAD -- _data/ideas.jsonl` shows only added lines, never a removed one).
The catalog was checked against a fresh regeneration and found already current (empty diff); no
regeneration commit was needed.

D05-G (phase gate, `demo-validator-check`) was re-dispatched verbatim after the rebase and
returned **all 9 checklist items PASS**, including item 9 (diff scope), which is now green against
the widened deliverables declaration.

## Acceptance

- Both dry-runs complete within 15 minutes with every step inside its timebox, and their times
  are recorded in the runbook (REQ-006 R09) — **Not met**. Times are recorded for both passes,
  but `/idea-triage`'s subagent-dispatch half was not executed by either rehearsal agent (a
  rehearsal-tooling constraint, not a proven step failure, and now documented as such in the
  runbook's Step Markers section), so neither pass produced a complete, verified 15-minute total.
  See `## Verification` above and the runbook's Rehearsal Findings section.
- The R06 smoke check on the presentation machine is recorded as passing in the runbook —
  **Not met**. The Windows checklist (`docs/00-working/demo-windows-setup.md`) carries the R06
  smoke-check procedure and an owner-fillable result block, but the check itself requires the
  Windows presentation machine and has not been run — outstanding owner-machine work, reported
  plainly per this build's governance protocol, not claimed as done.
- `demo_reset.py prepare` parks the skill, seeds the fallback idea without duplication, and
  regenerates outputs; `demo_reset.py restore` returns the pre-built skill byte-identical; both
  are double-run idempotent and never delete or rewrite idea-log content or governed documents —
  **Met**. Proven by D05-C1's 19-test suite (allowlist refusal, prepare→restore round-trip,
  no-duplicate seed, both idempotences) and D05-V1's independent validation (verdict: PASS, no
  findings), and confirmed live during this session's `prepare`/`restore` cycles and the
  post-rebase append-only check above.

## Backlog

`phase-demo-05` — `status: active`, `agent: agent-demo-content`.

`next_action`: D05-G is green on all 9 items after the coordinator's fix cycle 1/2 and the
rebase onto `dev` at `9753a88`. Report this to the coordinator so it can dispatch D05-A
(adversarial review) and D05-W (Playwright rehearsal pass) per GOV-003. Still outstanding, not
fixable from this worktree: whether `/idea-triage`'s subagent half can be timed by an agent at
all, or whether R09's full 15-minute total needs a presenter-driven pass; and the REQ-006 R06
Windows smoke check, which is owner-machine work.

## Unresolved

- D05-A (adversarial review) and D05-W (Playwright rehearsal pass) are coordinator-dispatched,
  not yet run.
- `/idea-triage`'s subagent-dispatch half remains unverified by both rehearsal passes; the
  runbook now documents this as a rehearsal-tooling limitation rather than a step defect.
- The REQ-006 R06 Windows terminal smoke check has not been run — owner-machine work, outstanding.
