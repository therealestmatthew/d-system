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
  `dist/assets/index-CfxlgVqL.css` (12.82 kB), `dist/assets/index-BGb0orNz.js` (495.33 kB); 38
  modules transformed, built in under 1.2s.
- `uv run pytest` — `1 failed, 473 passed, 2 warnings`. The single failure
  (`test/test_codes.py::test_committed_catalog_matches_regenerated_output`) is pre-existing
  catalog drift — reproduced identically on plain `dev` in the primary checkout with none of this
  phase's changes present; not introduced by this phase's diff. See `## Unresolved`.
- `uv run ruff check src/ test/` — `All checks passed!`
- `uv run mypy src/` — `Success: no issues found in 23 source files`.
- `uv run python -m src.governance` — `Governance OK: 18 systems, 135 documents, 15 memories, 111
  backlog phases`, exit 0.
- `uv run python tools/check_no_private_content.py`, run with all changes staged (`git add -A`
  first) — `check_no_private_content: OK (429 tracked files, 0 identifiers checked)`.
- Adversarial review (D06-A) and Playwright browser verification (D06-W) — not yet dispatched. Per
  `PROMPT-018`'s completion-gate convention and `GOV-003`'s demo-track completion decision, both
  are dispatched by the build coordinator at `PROMPT-015` step 8, not by this orchestrator.

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
- `next_action`: Resolve the `uv run pytest` catalog-drift failure with the coordinator (same
  pre-existing, cross-phase condition already reported against `phase-demo-02`), then dispatch
  D06-A and D06-W (coordinator-owned) before requesting the owner's approval to integrate
  `agent/phase-demo-06` into `dev`.

## Unresolved

- `uv run pytest` fails `test/test_codes.py::test_committed_catalog_matches_regenerated_output`.
  Reproduced identically on plain `dev` in the primary checkout at `/code/d-system` with none of
  this phase's changes present — pre-existing catalog drift, not introduced by this phase's diff
  (which touches only `src/api/routes/demo_terminal.py`, `test/test_demo_terminal.py`,
  `ts/public/demo-commands.json` and `ts/src/stage/`). Reported up rather than fixed, since
  regenerating and committing `docs/08-governance/catalog.md` is outside this phase's declared
  deliverable paths and outside this orchestrator's authority to fix on `dev` unilaterally.
- D06-A (adversarial review) and D06-W (Playwright browser verification), and integration into
  `dev`, are all outstanding and require the coordinator/owner, not this orchestrator, to proceed.
- The D06-G dispatch's first run ended mid-checklist with no recorded findings; the resumed run
  used its own item numbering rather than the checklist's, reported `RED` on pytest correctly, but
  did not report against three of the six checklist items. This orchestrator completed those three
  directly rather than dispatching a third phase-gate attempt (which would exceed the two-fix-cycle
  bound for a single work item, and the gap was a reporting omission, not a defect found).
