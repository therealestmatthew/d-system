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

`status: active`. `next_action`: READY and the owner's merge approval.

## Unresolved

- The panel's display of the cap reason is verified by code reading only (R21).

## Review

Independent review by a fresh `demo-adversary` agent over `dev...HEAD` at `49ebfbe`, given
`REQ-012` R20-R22, the owner's two rulings and the phase's acceptance, and told not to read this
record. Condition by condition:

1. R20, reservation precedes accept: **Holds.** The check and `RESERVED.add` have no `await`
   between them; one outer `finally` releases the slot on every exit.
   `test_slot_is_reserved_before_accept_and_released_on_failure` fails on dev's code
   (`AttributeError: module has no attribute 'RESERVED'`).
2. R21, code and reason reach the client and the panel shows them: **Holds.** Its own run against
   a live server on a scratch port with Node's WHATWG `WebSocket`: `{"opened":true,"code":4001,
   "reason":"Maximum of 6 concurrent terminal sessions reached"}`; against dev's route the seventh
   socket stayed CONNECTING for 8 seconds with only an `error` event. The panel's new condition
   (`event.code === 4001`) does not fire for a normal end (1000) or for the shell refusal (4002).
3. R22, explicit shell honoured, override only when none is requested: **Holds.** No other caller
   in `ts/` builds a `?shell=` query; the override test fails on dev's code
   (`SHELLKIND=other` for an explicit bash request).

Verification it ran: `test/test_demo_terminal.py` 50 passed; full suite 1454 passed, 1 skipped;
governance OK; `tsc --noEmit` clean; mypy and ruff clean. With dev's route swapped in, all five new
or changed tests failed and the other 45 passed; the file was restored and `git status` stayed
clean. No file outside the deliverables changed; `workbench.py` does not read `SESSIONS`.

Findings:

1. **Minor, pre-existing.** If `create_adapter()` or `adapter.start()` raises after `accept()`,
   the slot is released but nothing closes the adapter or the websocket, and
   `PosixPtyAdapter.start()` can leak the master pty fd when `Popen` fails after `pty.openpty()`.
   The same ordering exists on dev.
2. **Informational.** An explicit `?shell=bash` now execs the PATH-resolved `bash` rather than
   the default `/bin/bash`; this is the behavior the ruling asked for.

Disposition: no blocker or major finding. Finding 1 is accepted for this phase as outside its scope
and sent to Ideation as an idea. Finding 2 needs no change.

## Decisions

- R22: the backlog asked for an OPS document or a behavior change. A new `docs/08-governance/OPS-*`
  file would have collided with `phase-grd-03`. The owner chose the behavior change (2026-10-04),
  and the claim reworded the acceptance line to match.
- The panel always sent `?shell=bash`, so the behavior change alone would have retired the
  operator override from the UI. Put to the owner, who chose to have the panel omit the param for
  bash, so the override still sets the panel's default sessions.
- `ts/src/stage/TerminalRegion.tsx` was added to the deliverables with `sys-wb-terminal`, the
  system `systems.yaml` registers it under.
- R21's refusal is accepted then closed, not sent as a JSON text frame like the shell refusal: R21
  asks for the close frame to carry the reason, and the panel already quoted `event.reason`.

## Corrections

- The first marker helper in the R22 test stopped reading once the echoed command line matched;
  it now uses `printf` so the expected text appears only in the command's output.
- While comparing with dev's route, a stale server held the port and a `pkill` pattern matched its
  own shell, leaving dev's route file in the worktree uncommitted. It was restored with
  `git checkout`; the committed fix was untouched, and the comparison was rerun from a scratch copy.

## Left undone

- The panel's display of the cap reason was not rendered in a browser; it rests on code reading.
- Review finding 1 (adapter and fd cleanup when the shell fails to start) is sent to Ideation.
