---
schema_version: 1
id: doc-session-phase-wb-09-layout-assignment
code: SESS-2026-09-11-08
title: phase-wb-09 layout assignment model — checkpoint
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-ui, sys-api]
depends_on: [doc-workbench]
---

# phase-wb-09 layout assignment model — checkpoint

## Phase

`phase-wb-09` — Layout assignment model — per-panel eligibility, assignment-only dialog,
concurrent shells.

## Verification

Commands run in the worktree `/code/d-system-worktrees/phase-wb-09`, branch `agent/phase-wb-09`
at `73ef92d` (three phase commits `8d7c4ea`/`7e864f9`/`b4a086a` merged forward with `dev` to
pick up unrelated upstream commits, resolving a staleness failure in the idea-log regeneration
test):

- `cd ts && npm run build`: `✓ 55 modules transformed … ✓ built` (the 500 kB chunk-size warning
  is pre-existing, not introduced by this phase).
- `uv run pytest`: `3 failed, 575 passed` — the three failures
  (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`) are the known environmental
  PTY failures (ideas `000097`/`000099`, pyenv-shim rehash lock contention under concurrent-agent
  load), unchanged in kind and count from the pre-phase baseline; confirmed by their
  pyenv-rehash-noise signature in captured PTY output, not a code defect.
- `uv run ruff check src/ test/`: `All checks passed!`
- `uv run mypy src/`: `Success: no issues found in 24 source files`
- `uv run python -m src.governance`: `Governance OK: 18 systems, 167 documents, 16 memories, 122
  backlog phases`
- `uv run python tools/check_no_private_content.py` with changes staged:
  `check_no_private_content: OK (504 tracked files, 0 identifiers checked)`
- Adversarial review (`demo-adversary`, pack `W09-A`): not yet dispatched — coordinator-owned
  per `GOV-003`'s completion gate, dispatched after the orchestrator's creator/validator loop
  closes.
- Playwright browser verification (`demo-validator-web`, pack `W09-W`): not yet dispatched —
  coordinator-owned, same gate.

Creator/validator loop, each pair reviewed by the orchestrator before commit:

- W09-C1/V1 (backend: six-session cap, `/platform` route, ADR-014 wording) — committed
  `8d7c4ea`; V1 verdict PASS, no findings; `90 passed` on the scoped test files.
- W09-C2/V2 (layout data: per-panel eligibility, schema v2, storage rework) — committed
  `7e864f9`; V2 verdict PASS, no findings; `21 passed` on the new layout-schema test.
- W09-C3/V3 (assignment dialog, switcher-only headers, concurrent-shell portal mechanism,
  platform-conditional default shell) — committed `b4a086a`; V3 verdict PASS, no findings;
  V3 specifically checked and confirmed the idea `000107` layout round-trip regression is
  closed by the portal mechanism plus W09-C2's aligned layout-file defaults, and that the
  multi-occupant header-switcher's remount-on-visibility-change behavior is unchanged
  pre-existing behavior, not a new regression.
- W09-G (phase gate, `demo-validator-check`): re-run after the `dev` merge — **ALL GATES
  GREEN** (all six checklist items PASS, including the previously-stale idea-log regeneration
  test now passing post-merge).

One operational finding resolved mid-session, not a phase defect: an uncommitted
`src/demo/factory.py` modification observed in the primary checkout was investigated and
confirmed (by the coordinator, then by its landing as `dev` commit `3e4b5cd`) to be the owner's
own separate-session work, unrelated to this phase.

## Acceptance

- Dialog offers exactly one eligible-slot selector per panel and nothing else; assigning HTML
  Viewer to the terminal slot and a shell to the main slot renders both there and survives
  reload; a cleared or old-schema store yields the pre-delta default arrangement (REQ-007 W16):
  Met by code review and the V2/V3 diff checks (per-panel selector confirmed, old-schema/
  ineligible fallback confirmed silent via `resolveAssignment`, default arrangement confirmed
  in both layout files) — not yet independently confirmed live in a browser; that measurement
  belongs to `W09-W`, not yet dispatched.
- Two shell panels visible at once each complete an independent command round-trip; a seventh
  concurrent session is refused while six are open and admitted after one closes; the platform
  route reports host platform and shell availability (REQ-007 W17): Met for the backend half —
  `test_seventh_concurrent_session_is_refused_while_six_are_open` and
  `test_refusal_is_absent_once_one_of_six_sessions_closes` both genuinely open six live
  websocket sessions and pass (V1). The two-shells-render-simultaneously and platform-route
  live measurements are `W09-W`'s to confirm, not yet dispatched.
- Each shell panel renders unclipped and fully interactive assigned to the main slot in both
  layouts (REQ-007 W15 re-run), and the persistence guard passes: Not yet independently
  confirmed live — this is `W09-W`'s stated scope and has not been dispatched.
- On Linux a fresh store defaults the terminal slot to bash; the Windows default (PowerShell)
  and a Windows two-shell round-trip are owner checks belonging to `phase-wb-07`'s checklist,
  not closed here: the Linux default-to-bash fallback is Met by code review (`getSlotPanel`'s
  platform-conditional branch, confirmed in V3); not yet independently confirmed live.

## Backlog

`phase-wb-09` — `status: active`, `agent: agent-demo-stage`. `next_action`: coordinator to
dispatch `W09-A` (adversarial review) and `W09-W` (Playwright browser verification) per the
`GOV-003` completion gate; the orchestrator's creator/validator loop and mechanical gate
(`W09-G`) are done and green. No `completion_evidence`/`result` recorded yet — those are
`session-close`'s to set once the completion gate closes.

## Unresolved

- `W09-A` and `W09-W` — the two coordinator-owned completion-gate dispatches — have not run.
- The live-browser measurements underlying three of the four acceptance conditions above are
  confirmed only by code/diff review so far, not by an actual rendered check.
</content>
