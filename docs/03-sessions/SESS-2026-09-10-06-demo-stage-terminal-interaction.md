---
schema_version: 1
id: doc-session-demo-stage-terminal-interaction
code: SESS-2026-09-10-06
title: Demo stage orchestration — stage terminal interaction (phase-demo-06)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-demo-stage]
depends_on: [doc-live-demo, doc-prompt-demo-build-delegation-pack]
---

# Demo stage orchestration — stage terminal interaction (phase-demo-06)

## Phase

`phase-demo-06` — Stage terminal interaction: session tabs, guarded drop, command injection.

## Verification

- `cd ts && npm run build` — `tsc -b && vite build` succeeds; `dist/index.html`,
  `dist/assets/index-CfxlgVqL.css` (12.82 kB), `dist/assets/index-DAUn58IC.js` (495.40 kB); 38
  modules transformed, built in ~1s.
- `uv run pytest` — `476 passed, 2 warnings`. No failures; the catalog-drift failure recorded
  earlier in this session cleared on its own once this branch's own checkpoint commit (`b1bb28d`)
  regenerated and committed `docs/08-governance/catalog.md` — confirmed by rerunning the same test
  after that commit landed.
- `uv run ruff check src/ test/` — `All checks passed!`
- `uv run mypy src/` — `Success: no issues found in 23 source files`.
- `uv run python -m src.governance` — `Governance OK: 18 systems, 136 documents, 15 memories, 111
  backlog phases`, exit 0.
- `uv run python tools/check_no_private_content.py`, run with all changes staged (`git add -A`
  first) — `check_no_private_content: OK` (repeated at each commit above, all clean).
- Adversarial review (D06-A) — dispatched by the coordinator; see the fix-cycle entry below.
  Playwright browser verification (D06-W) — not yet dispatched; follows from the coordinator once
  this fix cycle is reported green.

Item-level dispatch history (creator/validator pairs from `PROMPT-018`'s D06 section):

- D06-C1 (websocket control frames / resize, `src/api/routes/demo_terminal.py`,
  `test/test_demo_terminal.py`) — replaced the `receive_bytes()`-only loop with `receive()`
  handling both binary input frames (unchanged, still go to `adapter.write()`) and JSON text
  control frames (`{"type":"resize","cols":N,"rows":N}` with positive integers calls the PTY
  adapter's `resize()`, previously implemented but unused; malformed/unknown text frames are
  dropped and never reach the shell). No new endpoints, one PTY per websocket, ADR-013's gating
  and loopback binding untouched. Added four tests: resize reaches the adapter (real `stty size`
  read back through the PTY), malformed-frame safety, binary round-trip after a text frame, two
  independent concurrent sessions. `uv run pytest`/`ruff`/`mypy` all clean at commit time. D06-V1:
  PASS — no findings; confirmed no code path writes a text frame to `adapter.write()`; registration
  gating and loopback fail-fast untouched; one PTY per websocket confirmed.
- D06-C2 (session tabs, collapse, guarded drop; `ts/src/stage/TerminalRegion.tsx`,
  `StagePage.tsx`, `StagePage.css`, `Popover.tsx`) — reworked the terminal region: up to four
  `TerminalSession` instances (each its own xterm.js + websocket) stay mounted regardless of
  active tab, visibility toggled by CSS only (no unmount on tab switch); tab bar with a new-session
  control disabled at the four-session cap; fit path guarded against zero-size containers, refit on
  tab activation, sends the D06-C1 resize control frame after every successful fit; a header
  collapse control hides the region via the existing `--no-terminal` grid reflow while leaving
  every socket open; the rung-4 drop toggle and each tab's close control route through a `Popover`
  confirm before termination — no code path terminates a session without passing through the
  confirm. `Popover.tsx` gained an optional function-as-children form so a confirm action can close
  itself; the existing static-children usage (`TalkingPointsRegion`) is untouched. `npm run build`
  clean. D06-V2: PASS — no findings; confirmed via direct inspection that no conditional render
  unmounts an inactive session, the four-session cap is enforced in both the click handler and the
  disabled button attribute, and no path bypasses the confirm.
- D06-C3 (command panel and injection; `ts/public/demo-commands.json`,
  `ts/src/stage/CommandPanel.tsx`, `TerminalRegion.tsx`, `StagePage.css`) — built an in-place
  reveal in the terminal region header, entries loaded at runtime from
  `ts/public/demo-commands.json` (Vite `publicDir` static serving, confirmed unchanged in `dist/`
  after build — editing the JSON needs no rebuild); the file ships with three clearly-marked
  placeholder entries only (real content is `phase-demo-05`'s). `TerminalSession` converted to
  `forwardRef` exposing `sendCommand(text, appendNewline)` via `useImperativeHandle`, sending
  through the same websocket path `term.onData` already uses (never `term.write()`); selecting an
  entry sends its command with no trailing newline (lands un-executed on the input line), `run:
  true` entries append one. The panel renders (disabled) in every non-enabled terminal state
  rather than vanishing, and never fetches into a broken state. `npm run build` clean. Deviation
  flagged by the creator (not fixed, outside this item's frontend-only scope): unlike
  `talking-points.json`, which is served through a dedicated backend route in
  `src/api/routes/demo_stage.py`, `demo-commands.json` relies on Vite's `publicDir` convention
  instead — a backend-route parity change, if wanted, belongs to whoever owns `demo_stage.py`.
  D06-V3: PASS — no findings; grep confirmed none of the three placeholder command strings appear
  anywhere in `ts/src`; confirmed injection goes through the websocket send, not `term.write()`; no
  trailing newline unless `run: true`; confirmed no fourth page region was introduced; confirmed the
  disabled-degrade path when the terminal route is absent.
- D06-G (phase gate) — dispatched once, then resumed once after its first run ended mid-checklist
  with no recorded findings (turn-limit truncation, not a failure — resumed per the standing
  "resume, never re-run" rule). The resumed run reported `RED` on `uv run pytest` (the same
  pre-existing catalog-drift failure independently reproduced above) and did not report against
  items 3 (deliverable existence), 5 (grep for hardcoded command strings) or 6 (diff scope) using
  the checklist's own numbering. This orchestrator ran those three items itself directly in the
  worktree: all four deliverables exist on disk; none of the six placeholder strings from
  `demo-commands.json` appear in `ts/src`; `git diff --stat dev...agent/phase-demo-06` touches only
  `src/api/routes/demo_terminal.py`, `test/test_demo_terminal.py`, `ts/public/demo-commands.json`
  and four files under `ts/src/stage/` — all within the phase's declared deliverable paths, nothing
  else.

D06-A fix cycle (1 of at most 2, coordinator-dispatched adversarial review found one blocker, two
majors and one minor):

- BLOCKER — a `run:false` command entry with an embedded newline executed everything before the
  `\n` once it reached the shell (`sendCommand` shipped `entry.command` byte-for-byte, withholding
  only the trailing newline; `isCommandEntry` validated types only). Fixed at both layers:
  `CommandPanel.tsx`'s `isCommandEntry` now rejects any entry whose `command` contains a control
  character (`0x00`-`0x1f` or `0x7f`) at load time; `TerminalRegion.tsx`'s `sendCommand` also
  strips any `\r`/`\n` from `text` when it is not the one appending the trailing newline, so a
  caller that bypassed `CommandPanel` entirely still cannot smuggle one onto the wire. Commit
  `e474ccb`. Validator (`demo-validator-code`): PASS, no findings — confirmed both layers close the
  exact attack, no stray control bytes landed in either file, `npm run build` clean.
- MAJOR — an oversized resize frame (`{"type":"resize","cols":100000,...}`) raised an uncaught
  `struct.error` in `struct.pack("HHHH", ...)` (`src/demo/posix.py`, 65535-per-field limit) that
  was not a `WebSocketDisconnect`, tearing the connection down. Fixed: `cols`/`rows` are now bounded
  to `1..65535` before `adapter.resize()` is ever called; out-of-range frames drop like any other
  malformed frame. New test sends the exact finding frame plus boundary cases and asserts the
  session survives and still echoes.
- MAJOR — an abrupt disconnect (SIGKILL'd client, dropped network, no close frame) left
  `terminal_websocket`'s `await websocket.receive()` never resolving, so `finally: adapter.close()`
  never ran, orphaning the shell (proven with a hard-killed client leaving `sleep 6666` running).
  Fixed: the receive loop now wraps `websocket.receive()` in `asyncio.wait_for` with an idle
  timeout (`D_SYSTEM_DEMO_TERMINAL_IDLE_TIMEOUT_SECONDS`, default 300s, resolved fresh per
  connection); a timeout breaks the loop into the existing `finally` cleanup, so the PTY is reaped
  within the bound through the same path as a graceful disconnect, not a new one. New test shrinks
  the timeout, opens a session with no close frame ever sent, and asserts the adapter's `alive`
  flag goes `False` within the bound. Both majors: commit `2e6fda3`. Validator
  (`demo-validator-code`): PASS, no findings — confirmed the bound is exactly `1..65535`, confirmed
  the idle-timeout path reaches `adapter.close()` via the existing cleanup rather than a new one,
  confirmed both tests exercise the exact scenarios from the findings. `uv run pytest`: 476 passed.
  `ruff`/`mypy`: clean.
- MINOR (record only, no code change) — the four-session cap is enforced in the UI
  (`TerminalRegion`'s `addSession` guards at function level, held under the adversary's attack) but
  the websocket route itself has no session registry, so raw local websocket connections bypassing
  the UI can exceed four sessions. This matches ADR-013's current scope (loopback-only, no
  session-identity layer). A session registry that would close this gap is parked as idea `000087`
  (terminal interaction API for driving demo shell sessions from outside the stage page) — not
  fixed here, per the coordinator's explicit instruction to record rather than code it.

Full re-verification after the fix cycle, run by this orchestrator in the worktree: `cd ts &&
npm run build` clean (38 modules, ~1s); `uv run pytest` — `476 passed, 2 warnings`; `uv run ruff
check src/ test/` — `All checks passed!`; `uv run mypy src/` — `Success: no issues found in 23
source files`.

## Acceptance

- A long-running command in one tab survives switching tabs and collapsing/re-expanding the
  region, and a fifth tab cannot be opened (REQ-006 R10) — Not yet confirmed live. The mechanism
  exists and is code-reviewed (D06-C2/D06-V2: every session stays mounted, CSS-only visibility, cap
  enforced in two places) but has not been exercised in a real browser in this session; that
  measurement is D06-W's (Playwright), owned by the coordinator.
- Nothing terminates a session before its confirmation step; the confirmed drop and tab close
  genuinely terminate with no orphaned shell processes (REQ-006 R11) — Not yet confirmed live for
  the same reason. D06-V2 confirmed by code inspection that no termination path bypasses the
  `Popover` confirm; whether a confirmed termination leaves no orphaned PTY process is a runtime
  fact D06-A/D06-W would need to establish, not something this session observed directly.
- An injected command appears un-executed on the active tab's input line, a `run: true` entry
  executes on selection, and editing `demo-commands.json` changes the list with no page-code
  rebuild (REQ-006 R12) — Partially confirmed. The no-rebuild claim was verified directly (D06-C3
  inspected `ts/dist/demo-commands.json` post-build and confirmed placeholder content unchanged);
  the injection behavior itself (un-executed landing, `run: true` auto-execute) is code-reviewed
  (D06-V3: websocket send not `term.write()`, newline logic matches `run`) but not exercised live in
  a browser.
- A resize in the browser reaches the PTY (adapter `resize()` called), proven by a test — Met. D06-
  V1 confirmed `test_resize_text_frame_applies_to_pty_window_size` in `test/test_demo_terminal.py`
  asserts the real kernel-reported window size via `stty size` read back through the PTY after a
  resize control frame, which `uv run pytest` reproduces passing in this session.

## Backlog

- `phase-demo-06`: `status: active`, `agent: agent-demo-stage`.
- `next_action`: D06-A's fix cycle 1 is reported green (build/pytest/ruff/mypy all clean, both
  fixes validated) to the coordinator. Await D06-W (Playwright browser verification,
  coordinator-owned) before requesting the owner's approval to integrate `agent/phase-demo-06`
  into `dev`.

## Unresolved

- The `uv run pytest` catalog-drift failure recorded earlier in this session is resolved on this
  branch — this branch's own checkpoint commit (`b1bb28d`) regenerated and committed
  `docs/08-governance/catalog.md`, and the failure has not recurred since.
- D06-W (Playwright browser verification) and integration into `dev` are outstanding and require
  the coordinator/owner, not this orchestrator, to proceed.
- The MINOR finding from D06-A (no session registry at the websocket route, so the four-session
  cap can be exceeded by a client that bypasses the UI) is recorded, not fixed, per the
  coordinator's explicit instruction — see idea `000087` above.
- The D06-G dispatch's first run ended mid-checklist with no recorded findings; the resumed run
  used its own item numbering rather than the checklist's, reported `RED` on pytest correctly (a
  failure since resolved as above), but did not report against three of the six checklist items.
  This orchestrator completed those three directly rather than dispatching a third phase-gate
  attempt (which would exceed the two-fix-cycle bound for a single work item, and the gap was a
  reporting omission, not a defect found).
