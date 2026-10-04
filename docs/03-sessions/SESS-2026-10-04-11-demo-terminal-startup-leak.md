---
schema_version: 1
id: doc-session-demo-terminal-startup-leak
code: SESS-2026-10-04-11
title: Close the adapter and websocket when demo terminal startup fails
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-demo-stage]
depends_on: []
---

# Close the adapter and websocket when demo terminal startup fails

## Phase

Unclaimed — owner-directed work, no backlog phase. `fix-demo-terminal-startup-leak` — close the
adapter, the pty master fd and the websocket when `create_adapter()` or `adapter.start()` fails
after the socket is accepted (idea `000573`, found by the `phase-wbf-09` review), with tests.

## Verification

Run in `/code/d-system-worktrees/fix-demo-terminal-startup-leak` on
`agent/fix-demo-terminal-startup-leak`, branched from dev `b8dbdad`.

`uv run python -m src.governance`

```
Governance OK: 44 systems, 434 documents, 36 memories, 347 backlog phases
```

`uv run pytest`

```
1457 passed, 1 skipped, 1 warning
```

`uv run python tools/check_no_private_content.py` (changes staged)

```
check_no_private_content: OK (1304 tracked files, 0 identifiers checked)
```

The worktree has no `_private/`, so that run checked no identifiers. `check_content()` was run on
the two changed files with the primary checkout's identifier set: `identifiers checked: 31;
violations: 0`.

Also: `uv run ruff check src/ test/` (`All checks passed!`) and `uv run mypy src/` (`Success: no
issues found in 47 source files`). With dev's route in place (and only the two new constants
appended so the tests import), the three new tests fail: `3 failed`.

## Acceptance

Self-declared from the owner's instruction; no backlog acceptance list exists for this session.

- When `adapter.start()` raises after `accept()`, the route closes the adapter and closes the
  socket with a code and reason: Met (`test_adapter_and_socket_are_closed_when_start_fails`).
- When `create_adapter()` raises after `accept()`, the route closes the socket the same way: Met
  (`test_socket_is_closed_when_create_adapter_fails`).
- A real shell that cannot spawn no longer leaks the pty master fd: Met
  (`test_pty_master_fd_is_closed_when_the_shell_cannot_spawn`, which records the fd `openpty()`
  returned and asserts `os.fstat` on it raises after the request). This is proven for the POSIX
  adapter only: `WindowsConPtyAdapter.close()` is a no-op after a failed `start()`, which is safe
  only if `pywinpty` releases its own ConPTY handle when `spawn()` raises; that is untested here.
- No slot is held after a startup failure, and the full suite passes: Met (all three tests assert
  an empty registry; 1457 passed).

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of backlog.yaml was changed.

## Unresolved

- The panel shows its refusal message only for a socket that never opened or for code 4001
  (`ts/src/stage/TerminalRegion.tsx`). A startup failure closes with 4003 after the socket
  opened, so the panel shows a closed terminal without the reason. Changing the panel was outside
  this instruction.

## Review

Independent review by a fresh `demo-adversary` agent over `b8dbdad...HEAD` at `3ed8b18`, given the
owner's instruction as relayed, idea `000573`'s title, the four self-declared conditions (marked as
written by this session) and the repository-wide gates, and told not to read this record.

1. `adapter.start()` raising closes the adapter and the socket with a code and reason: **Holds.**
   With the hunk reverted in a scratch copy the test fails (an unhandled `OSError` leaves the ASGI
   handler); on the branch it passes.
2. `create_adapter()` raising closes the socket the same way: **Holds.** Fails on the reverted copy
   (`anyio.ClosedResourceError` through the test client), passes on the branch.
3. A shell that cannot spawn no longer leaks the pty master fd: **Holds for POSIX.**
   `PosixPtyAdapter.start()` sets `_master_fd` before `Popen`, so `close()` releases it. The Windows
   path is unverified (see finding 1).
4. No slot held after a failure, and the suite passes: **Holds.** One outer `finally` releases the
   slot on every exit; 1457 passed, 1 skipped; governance, ruff, mypy and the private-content check
   clean.

Probes it cleared: `except Exception` lets `asyncio.CancelledError` through; a failing
`websocket.close()` inside the handler is suppressed and the slot is still released; no other
`4003` in `src/` or `ts/`; only the declared files changed.

Findings:

1. **Minor.** Condition 3 is proven for the POSIX adapter only; the Windows ConPTY path after a
   failed `start()` rests on code reading, and was the same before this change.

Disposition: finding 1 accepted, and condition 3's wording now states the POSIX-only proof.

## Decisions

- The fd leak sits in `PosixPtyAdapter.start()`, which stores the master fd before spawning. The
  instruction named the route file, and the route calling `adapter.close()` on failure releases
  the fd, so `src/demo/posix.py` was left unchanged.
- A startup failure closes with a new code, 4003, rather than reusing 4001 (cap) or 4002 (shell
  refusal), so a client can tell the three apart.
- The handler catches `Exception`, logs it, and returns rather than re-raising, so the ASGI server
  does not also try to close the socket.

## Left undone

- The panel does not quote the 4003 reason (see `## Unresolved`).
- No Windows test of the ConPTY adapter's cleanup after a failed `spawn()`.
