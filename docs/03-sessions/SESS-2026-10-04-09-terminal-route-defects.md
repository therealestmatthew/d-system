---
schema_version: 1
id: doc-session-terminal-route-defects
code: SESS-2026-10-04-09
title: Fix the terminal route's cap race, cap refusal reason and shell override
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-api, sys-demo-stage, sys-wb-terminal]
depends_on: [doc-workbench-features-defects]
---

# Fix the terminal route's cap race, cap refusal reason and shell override

## Phase

`phase-wbf-09` — Terminal route defects: cap race, shell override, close reason.

## Verification

Run in `/code/d-system-worktrees/phase-wbf-09` on `agent/phase-wbf-09`, branched from dev `e9fc437`.

`uv run pytest test/test_demo_terminal.py`

```
50 passed, 1 warning
```

`uv run pytest`

```
1454 passed, 1 skipped, 1 warning
```

`uv run python -m src.governance`

```
Governance OK: 44 systems, 434 documents, 36 memories, 347 backlog phases
```

Also run: `uv run ruff check src/ test/` (`All checks passed!`), `uv run mypy src/` (`Success: no
issues found in 47 source files`), and in `ts/`, `npm run lint` (`tsc --noEmit`, no errors) and
`npx vite build` (built).

Client check for R21. A local server (`D_SYSTEM_DEMO_TERMINAL=1 uvicorn src.main:app`) and Node
22's WHATWG `WebSocket` (the browser API: same `CloseEvent` code and reason). The script opens six
sessions, then a seventh, and prints the seventh's `CloseEvent`:

- this branch: `opened=true code=4001 reason=Maximum of 6 concurrent terminal sessions reached`
- dev's route (run from a scratch copy of `dev`): `timeout opened=6`, no `close` event for the
  seventh socket within 10 seconds, so no code or reason reached the client.

A headless Chrome page with the same script dumped its DOM before the sockets finished
(`--dump-dom` snapshots at load), so it gave no result.

## Acceptance

- REQ-012 R20, the reservation precedes the accept: Met. `terminal_websocket` checks
  `_slots_in_use()` and adds the session id to `RESERVED` with no `await` between them, before
  `_run_session` awaits `accept()`; `finally` releases the slot on any exit.
  `test_slot_is_reserved_before_accept_and_released_on_failure` records one reserved slot at the
  moment `accept()` is called and an empty registry after a failure;
  `test_reserved_slots_count_against_the_cap` and
  `test_refused_shell_request_releases_its_reserved_slot` cover the cap count and the release.
  As the acceptance says, the race itself was never reproduced under asyncio.
- REQ-012 R21, a refused connection delivers the structured code and reason, and the panel shows
  it: Met for delivery (the updated `test_seventh_concurrent_session_is_refused_while_six_are_open`
  and the client check above). The panel side is met by reading `TerminalRegion.tsx`: the
  `close` handler now sets the refusal when `event.code === 4001` even after the socket opened,
  and `connectionRefusalMessage` returns `event.reason` for codes of 4000 and above with a
  non-empty reason. No browser render of the panel was run; the repository has no frontend test
  for this component.
- REQ-012 R22, as amended by owner ruling: Met.
  `test_explicit_shell_request_is_honoured_over_the_operator_override` sets
  `D_SYSTEM_DEMO_SHELL=/bin/sh`: `?shell=bash` prints `SHELLKIND=bash`, and no param prints
  `SHELLKIND=other`. `_executable_for_shell`'s docstring states the rule and the ruling.

## Backlog

`status: active`. `next_action`: independent review, then READY.

## Unresolved

- The panel's display of the cap reason is verified by code reading only (R21).
