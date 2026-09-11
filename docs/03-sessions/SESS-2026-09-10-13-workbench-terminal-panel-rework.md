---
schema_version: 1
id: doc-session-workbench-terminal-panel-rework
code: SESS-2026-09-10-13
title: Demo stage orchestration — terminal panel rework, injection dropdowns, shells (phase-wb-03)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-ui, sys-demo-stage]
depends_on: [doc-workbench, doc-prompt-workbench-delegation-pack]
---

# Demo stage orchestration — terminal panel rework, injection dropdowns, shells (phase-wb-03)

## Phase

`phase-wb-03` — Terminal panel rework, injection dropdowns and shell panels: the ellipsis menu
replacing the standalone collapse control and page-level drop, drop-in-place with deactivated
injection dropdowns, the Skills/Prompts/Agents injection dropdowns fed by phase-wb-01's
enumeration route, and the Terminal (bash)/CMD/PowerShell shell panel options.

## Verification

Run in the worktree (`/code/d-system-worktrees/phase-wb-03`, branch `agent/phase-wb-03`, rebased
onto `dev` at `b044b1a`):

- `cd ts && npm run build` — `tsc -b && vite build` succeeds, `✓ 47 modules transformed`, `✓
  built in 1.05s-1.16s` across reruns (the chunk-size-over-500kB note is Vite's informational
  warning, not an error).
- `uv run pytest` — `546 passed, 3 failed`. The three failures
  (`test_posix_adapter_reports_alive_then_not_alive`,
  `test_resize_text_frame_applies_to_pty_window_size`,
  `test_two_concurrent_websocket_sessions_are_independent_shells`, all in
  `test/test_demo_terminal.py`) are the known host-wide `pyenv rehash` shim-lock contention
  (`pyenv: cannot rehash: couldn't acquire lock ...pyenv-shim`) — an environmental defect, not a
  phase finding.
- `uv run python -m src.governance` — exit 0, `Governance OK: 18 systems, 158 documents, 16
  memories, 119 backlog phases`.
- `uv run python tools/check_no_private_content.py` with all changes staged (`git add -A`
  first) — `check_no_private_content: OK (484 tracked files, 0 identifiers checked)`.

Work-item creator/validator cycles, all first-pass, no findings:

- W03-C1 (ellipsis menu, drop-in-place, injection deactivation, websocket startup-race fix),
  committed `0c36034` (pre-rebase `b7d4f3d`). W03-V1 — **PASS, no findings**: no standalone
  collapse or page-level drop control remains anywhere in `ts/src`; drop renders the info page
  inside unchanged panel bounds; confirmation guards on drop and tab close intact; sessions
  survive collapse (components stay mounted, only a CSS class and `visible` prop change); the
  Commands dropdown carries a real `disabled` attribute (not styling-only) while dropped; the
  startup-race fix guards socket handlers with a `disposed` flag and defers closing a
  still-`CONNECTING` socket rather than swallowing errors.
- W03-C2 (Skills/Prompts/Agents injection dropdowns; real `demo-commands.json` entries),
  committed `d3b9553` (pre-rebase `f0d024d`). W03-V2 — **PASS, no findings**: all three
  dropdowns render only content fetched from phase-wb-01's `/api/v1/workbench/injection-sources`
  route (no hardcoded skill/agent/prompt names — grep confirmed); injection reuses the R12 path
  (`sendToActiveSession(injection, false)`, no trailing newline, active tab's websocket only);
  dropdowns disable with drop state and degrade cleanly (404) when the route is absent;
  `demo-commands.json`'s placeholder entries are replaced with the real orient/idea/idea-triage/
  overview commands from `docs/00-working/demo-runbook.md`, and none of the four command/label
  strings appear anywhere in `ts/src` (grepped individually, zero matches).
- W03-C3 (Terminal (bash)/CMD/PowerShell shell panels), committed `7cf995a` (pre-rebase
  `6c41843`). W03-V3 — **PASS, no findings**: all three panel ids share one `TerminalRegion`
  implementation parameterized by a `shell` prop, via two thin wrapper exports
  (`TerminalRegionCmd`, `TerminalRegionPowerShell`) — no copy-pasted second terminal component;
  the backend's structured `shell_refusal` frame is rendered as the panel's own `message` field
  naming the unavailable shell, never a raw error; `shell` is used only as a literal websocket
  query-string value, never concatenated into a command — the backend allowlist
  (`SHELL_ALLOWLIST` in `src/api/routes/demo_terminal.py`) is the sole authority.

Process note: W03-C3's validator (W03-V3) was dispatched before its commit was made, contrary to
the dispatch instruction to commit each item before dispatching its validator — an orchestrator
process error, corrected by committing (`6c41843`, later rebased to `7cf995a`) immediately after;
V3 evaluated the actual worktree state, which matched what was then committed, so no re-dispatch
was needed.

Phase gate (W03-G), two dispatches: the first was cut off by an orchestrator-side API session
limit before producing any checklist result (discarded, not treated as a verdict — the same
"resume, never restart from scratch" principle governing truncated subagents was applied here by
re-dispatching cleanly after the session reset, since no partial work existed to resume). The
second dispatch, run after rebasing the branch onto `dev` (`b044b1a`), recorded:

1. Governance — PASS, `Governance OK: 18 systems, 158 documents, 16 memories, 119 backlog
   phases`.
2. Staged private-content check — PASS, `check_no_private_content: OK (484 tracked files, 0
   identifiers checked)`.
3. Deliverables present — PASS: `ts/src` reworked, `ts/public/demo-commands.json` carries
   non-placeholder entries.
4. `npm run build` — PASS. `uv run pytest` — **FAIL as reported**, `3 failed, 546 passed`, the
   same three known `pyenv`-contention failures listed above.
5. No standalone collapse/page-level drop remnants, no `demo-commands.json` command string
   embedded in `ts/src` — PASS.
6. Diff against `dev` touches nothing outside `ts/` — **FAIL as reported**:
   `_data/workbench/layouts/layout-1.json` and `layout-2.json` are also modified.

Item 6's finding is a real, reported mismatch between the gate's literal checklist and the
phase's own documented architecture: `ADR-016` (workbench layout persistence) makes a slot's
`admits` list layout data, not component code — `ts/src/workbench/panelRegistry.tsx`'s own
comment states the mechanism explicitly, and `phase-wb-02`'s prior session record shows the same
pattern already accepted at that phase's gate (its close note: "diff against `dev` touched only
`ts/` and `_data/workbench/layouts/`"). Widening the terminal slot's `admits` array to include
`terminal-cmd` and `terminal-powershell` is the only way the new shell panels become selectable
in the layout engine's dropdown; there is no `ts/`-only way to satisfy REQ-007 W12 under
`ADR-016`'s design. This orchestrator did not revert the `_data/` change or otherwise improvise
around the gate wording — reporting the mismatch rather than resolving it unilaterally, per its
charter.

## Acceptance

- No standalone collapse or page-level drop control renders; both live in the ellipsis menu with
  sessions surviving collapse and confirmation guarding drop (REQ-007 W02) — **Met**: confirmed
  by W03-V1's grep and mount-state review.
- Dropped state shows the info page inside unchanged panel bounds with all four injection
  dropdowns visible, disabled and unclickable; restore returns a working terminal (REQ-007 W03)
  — **Met for the mechanism reviewed** (the Commands dropdown, real `disabled` attribute
  confirmed by W03-V1); the Skills/Prompts/Agents dropdowns share the identical `Popover`
  `disabled` mechanism per W03-V2, but this was code-reviewed, not browser-measured — W03-W
  (browser verification, dispatched by the coordinator, not run in this session) is the
  measurement of record for the rendered claim.
- Each category injects its exact agreed text un-executed; an overrides-file relabel,
  replacement and hide take effect with no rebuild (REQ-007 W04) — **Met on the reviewed half**:
  W03-V2 confirmed route-only content and the R12 injection path; the overrides-file live-effect
  claim is a browser-observable behavior (W03-W's job), not exercised in this session.
- CMD and PowerShell panels on Linux show the in-panel unavailability message with no uncaught
  console errors; bash round-trips (REQ-007 W12) — **Met on the reviewed half**: W03-V3 confirmed
  the shared-implementation and refusal-rendering code paths; "no uncaught console errors" is a
  browser-observable claim for W03-W, not exercised here.

## Backlog

`status: active`, `agent: agent-demo-stage` unchanged. `next_action`: W03-A (adversarial review)
and W03-W (browser verification) remain outstanding — both are dispatched by the coordinator, not
this orchestrator, per the pack's own attribution; the gate's item 6 finding (the `_data/`
layout-file scope conflict with the "touches nothing outside `ts/`" checklist wording) is
reported up for the coordinator to resolve, since it traces to `ADR-016`'s documented
architecture rather than a defect in the work; the three `test_demo_terminal.py` pytest failures
are the recorded environmental defect, not phase work remaining.

## Unresolved

- W03-G's item 6 finding: the phase's diff against `dev` touches `_data/workbench/layouts/*.json`
  in addition to `ts/`, required by `ADR-016`'s data-driven `admits` model to make the CMD/
  PowerShell panel options selectable — a gate-wording/architecture mismatch, not a defect,
  reported up rather than resolved unilaterally.
- W03-A (adversarial review) and W03-W (browser verification) have not run this session — both
  are coordinator-dispatched per the pack.
- The three `test_demo_terminal.py` PTY failures are the recurrent host-wide `pyenv` shim
  contention (tracked previously as environmental, e.g. idea `000097` for `phase-wb-02`'s
  identical failures) — not phase-wb-03-specific.
