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
Governance OK: 18 systems, 138 documents, 15 memories, 112 backlog phases
```

`uv run python tools/check_no_private_content.py` with the changes staged
```
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (436 tracked files, 0 identifiers checked)
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
pass produced a complete, real 15-minute total. Four would-need-explaining findings were
recorded: a port collision with a peer agent's dev servers on 8010/5180; the `/idea-triage` step
marker overclaiming shell-only executability; the nonexistent `/overview-build` command; and a
sequencing gap between `demo_reset.py prepare` parking the overview skill and the
overview-skill-rebuild step's instruction to invoke it.

## Acceptance

- Both dry-runs complete within 15 minutes with every step inside its timebox, and their times
  are recorded in the runbook (REQ-006 R09) — **Not met**. Times are recorded for both passes,
  but `/idea-triage`'s subagent-dispatch half was not executed by either rehearsal agent (a
  rehearsal-tooling constraint, not a proven step failure), so neither pass produced a complete,
  verified 15-minute total. See `## Verification` above and the runbook's Rehearsal Findings
  section.
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
  findings), and confirmed live during this session's `prepare`/`restore` cycles — `git diff`
  over `_data/ideas.jsonl` across both rehearsal passes showed only appended lines, never a
  deletion or rewrite.

## Backlog

`phase-demo-05` — `status: active`, `agent: agent-demo-content`.

`next_action`: Report the D05-G phase-gate finding on diff scope (item 9: the branch touches
`_data/ideas.jsonl`, `docs/00-working/ideas.md` and `_public/overview/index.html`, which are not
declared deliverables but are the sanctioned, designed output of running this phase's own
`demo_reset.py prepare` and the two rehearsal passes — a mismatch between the pack's generic
"nothing outside deliverable paths" gate line and this phase's own scope, not a defect to fix by
reverting permanent idea-log entries) up to the coordinator for a ruling. Separately unresolved:
whether `/idea-triage`'s full round-trip (including the subagent dispatch) can be verified by an
agent at all, or whether R09's 15-minute total needs a human-driven timed pass; and whether the
overview-skill-rebuild step's sequencing against `demo_reset.py prepare` needs an owner decision.
The R06 Windows smoke check remains entirely owner-machine work.

## Unresolved

- D05-A (adversarial review) and D05-W (Playwright rehearsal pass) are coordinator-dispatched,
  not yet run.
- The D05-G phase-gate verdict is red on diff-scope (item 9) for the reasons above; needs a
  coordinator ruling rather than an orchestrator override.
- `/idea-triage`'s subagent-dispatch half is unverified by both rehearsal passes.
- The REQ-006 R06 Windows terminal smoke check has not been run — owner-machine work, outstanding.
- The overview-skill-rebuild step's sequencing against `demo_reset.py prepare` parking the skill
  needs an owner decision on intended narrative (skill stays parked through this step, versus
  restored first), not an orchestrator guess.
