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
  returned and asserts `os.fstat` on it raises after the request).
- No slot is held after a startup failure, and the full suite passes: Met (all three tests assert
  an empty registry; 1457 passed).

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of backlog.yaml was changed.

## Unresolved

- The panel shows its refusal message only for a socket that never opened or for code 4001
  (`ts/src/stage/TerminalRegion.tsx`). A startup failure closes with 4003 after the socket
  opened, so the panel shows a closed terminal without the reason. Changing the panel was outside
  this instruction.
