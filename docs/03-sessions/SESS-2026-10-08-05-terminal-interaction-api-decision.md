---
schema_version: 1
id: doc-session-terminal-interaction-api-decision
code: SESS-2026-10-08-05
title: Decide the external terminal interaction API (phase-wbf-07)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-api, sys-demo-stage, sys-contracts]
depends_on: [doc-adr-terminal-interaction-api]
---

# Decide the external terminal interaction API (phase-wbf-07)

## Phase

`phase-wbf-07` (decide the external terminal interaction API), group `G51` of
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md). Builder A (`agent-builder-a`)
under the Session Manager's pre-approved run of 2026-10-08. Branch `agent/phase-wbf-07`, cut from
the run's integration branch `ccr-b69b05b4-tdcrux`.

## Outcome

One decision record, [`ADR-030`](../04-decisions/ADR-030-terminal-interaction-api.md), covering
idea `000087` (terminal interaction API for driving demo shell sessions from outside the stage
page). Nothing was built. The record's recommendation, one decision for each of the six questions
in `REQ-012` `R15`:

- **Gating:** a second flag, `D_SYSTEM_TERMINAL_API=1`, required in addition to
  `D_SYSTEM_DEMO_TERMINAL=1`. Additive, so no rehearsed launch command changes.
- **Binding:** loopback only, using the existing launch-time check, plus a per-request peer
  address check.
- **Authentication:** a bearer token on every route, generated at startup into a file in the
  owner's profile directory, outside the repository (`~/.d-system/terminal-api/<key>.token`). The record states what an unauthenticated loopback inject allows and
  what the token does not cover.
- **Session identity:** the `ADR-014` registry id, discovered by a list route, never chosen by the
  caller; an unknown id is refused, never created.
- **Output buffering:** the pump becomes the only adapter reader and appends to a 256 KiB byte
  ring per session; HTTP reads are offset-based and non-destructive.
- **Sessions outliving the websocket:** no. `ADR-014` decision 4 stands; an accepted inject extends
  the idle bound up to a ceiling, a read never does.

It states what `ADR-014` already owns (`R16`) in a table and proposes no second registry. It gives
`phase-wbf-08` three routes with request and response shapes, the error codes, and the "routes
absent with either flag unset" rule.

## Status of the decision

**Proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08).** The ADR front
matter is `status: draft`. `phase-wbf-08` builds against it.

## Evidence

- `uv run python -m src.governance`: `Governance OK: 45 systems, 460 documents, 37 memories, 354
  backlog phases`, exit 0, after `--catalog` was run. One non-blocking warning, unrelated to this
  phase: `status-regression (dev): phase-arch-02 complete -> active`.
- `uv run ruff check src/ test/ tools/`: `All checks passed!`
- `uv run mypy src/`: `Success: no issues found in 50 source files`
- `uv run pytest`: 1 failed, 1657 passed, 1 skipped. The failure is
  `test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused` (`DID NOT RAISE
  Refused`): the session runs as root (uid 0), which ignores directory permissions. Environmental,
  unrelated to a documentation change; not re-run to quiet and not skipped.
- `cd ts && npm test`: not run. `ts/node_modules` is absent and this phase touched nothing under
  `ts/`.

## Assumptions

1. The new routes live under the existing terminal prefix, `/api/v1/demo/terminal`, not under
   `/workbench`, so `ADR-015` rule 4 (GET only) is not extended. Neither `000087` nor `REQ-012`
   names a path.
2. The numbers (256 KiB buffer, 4096 byte input limit, 64 KiB default and 256 KiB maximum read,
   10 second maximum wait) are recommendations. None is in the source ideas or requirement.
3. Token file location (`~/.d-system/terminal-api/<key>.token`, keyed by a hash of the repository
   root) is a recommendation, changed from `data/` after review finding F03.
4. The websocket route has no authentication or `Origin` check. This is from reading
   `demo_terminal.py`, not from running a test against it.
5. The ConPTY and Windows file-mode checks are owner-machine, not run.

## Awaiting ratification

The ten items under "Open items for the owner" in the ADR: the second flag; the bearer token; no
detach or reattach; an accepted inject extending the idle bound up to a one hour ceiling; documentation scope of
`phase-wbf-08`; buffer depth and input limit; the unauthenticated websocket (a separate decision);
the pointers to add on ratification (`ADR-014`, idea `000087`); the token file location; and
that the second flag also switches output capture on. The review fixes below are the Session
Manager's choices under the owner's pre-approval and are awaiting ratification too.

## Unresolved

- `phase-wbf-08`'s entry lists `src/api/routes/` and `test/` as deliverables. Mounting the new
  module needs `src/api/__init__.py`, which is outside both. Not edited here; the entry needs
  widening before it is claimed.
- The websocket route's missing authentication (item 7 in the ADR) is not decided here.

## Review

The gating review (demo-adversary) passed `f07cad0` with four major and three minor findings. The
verdict record is
`docs/08-governance/reviews/verdicts/2026-10-08-phase-wbf-07-demo-adversary.json`, copied unchanged.
Each finding is fixed in `ADR-030`:

- F01 (major): reads never extend the idle bound; an accepted inject extends it only up to
  `TERMINAL_API_INJECT_CEILING_SECONDS` (3600) since the last websocket frame. Open item 4 states
  the trade.
- F02 (major): inject reads the raw body behind the auth dependency and validates by hand, query
  parameters are parsed by hand, every error uses the shared shape, and the precedence is 403, 401,
  404, 415, 413, 422, 409.
- F03 (major): the env-var rejection now names the real differences between a file and a variable;
  the token file moves outside the repository to the owner's profile directory (open item 9).
- F04 (major): atomic creation (unlink, `O_CREAT|O_EXCL|O_NOFOLLOW`, `0o600`), an absolute path
  derived from the repository root and logged in full, a path parameter for tests, a single-process
  note, and Windows protection marked unverified.
- F05 (minor): the output record and the idle changes exist only when the second flag is set (open
  item 10).
- F06 (minor): stall coupling documented, pump drains to EOF after exit (capture on only),
  `OSError` on write maps to 409 `session_ended`, a dedicated write executor, and the lock's limit
  to HTTP requests stated.
- F07 (minor): a validation table (raw body limit, parameter bounds, session id 404-not-422, peer
  edge cases), the long-poll wake mechanism, and `after` landing mid-sequence.
