---
schema_version: 1
id: doc-session-workbench-terminal-panel-rework
code: SESS-2026-09-10-13
title: Demo stage orchestration — terminal panel rework, injection dropdowns, shells (phase-wb-03)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-11'
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
twice onto `dev` as it advanced — most recently onto `6a63f67`):

- `cd ts && npm run build` — `tsc -b && vite build` succeeds, `✓ 47 modules transformed`, built
  in ~1.0-1.2s across every rerun including the post-fix rerun (the chunk-size-over-500kB note is
  Vite's informational warning, not an error).
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
  first) — `check_no_private_content: OK (484-485 tracked files, 0 identifiers checked)`.

Work-item creator/validator cycles:

- W03-C1 (ellipsis menu, drop-in-place, injection deactivation, websocket startup-race fix),
  committed `0c36034` (pre-rebase `b7d4f3d`). W03-V1 — **PASS, no findings**: no standalone
  collapse or page-level drop control remains anywhere in `ts/src`; drop renders the info page
  inside unchanged panel bounds; confirmation guards on drop and tab close intact; sessions
  survive collapse (components stay mounted, only a CSS class and `visible` prop change); the
  Commands dropdown carries a real `disabled` attribute (not styling-only) while dropped; the
  startup-race fix guards socket handlers with a `disposed` flag and defers closing a
  still-`CONNECTING` socket rather than swallowing errors.
- W03-C2 (Skills/Prompts/Agents injection dropdowns; real `demo-commands.json` entries),
  committed `d3b9553` (pre-rebase `f0d024d`). W03-V2 first pass — **PASS, no findings**
  (subsequently superseded by W03-A's finding below, on the same code W03-V2 had reviewed): all
  three dropdowns render only content fetched from phase-wb-01's
  `/api/v1/workbench/injection-sources` route (no hardcoded skill/agent/prompt names — grep
  confirmed); injection reuses the R12 path (`sendToActiveSession(injection, false)`, no
  trailing newline, active tab's websocket only); dropdowns disable with drop state and degrade
  cleanly (404) when the route is absent; `demo-commands.json`'s placeholder entries are
  replaced with the real orient/idea/idea-triage/overview commands from
  `docs/00-working/demo-runbook.md`, and none of the four command/label strings appear anywhere
  in `ts/src` (grepped individually, zero matches).
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
limit before producing any checklist result (discarded, not treated as a verdict). The second
dispatch, run after the first rebase onto `dev` (`b044b1a`), recorded governance PASS, staged
private-content PASS, deliverables present PASS, `npm run build` PASS, no
collapse/drop/command-string remnants PASS, `uv run pytest` **FAIL as reported** (the same three
known `pyenv`-contention failures), and "diff touches nothing outside `ts/`" **FAIL as
reported**: `_data/workbench/layouts/layout-1.json` and `layout-2.json` were also modified. That
item-6 finding was reported up rather than resolved unilaterally, since `ADR-016` (workbench
layout persistence) makes a slot's `admits` list layout data, not component code, with no
`ts/`-only way to satisfy REQ-007 W12 under that design. The coordinator resolved it by widening
`phase-wb-03`'s declared deliverables to include `_data/workbench/layouts/` (commit `6a63f67`,
"W03-G item-6 ruling") — **closed**.

W03-A (adversarial review, coordinator-dispatched) then reported one MAJOR, no blocker, against
W03-C2: `InjectionDropdowns.tsx`'s `isInjectionSources` validated the *whole*
`/api/v1/workbench/injection-sources` response with `.every(isInjectionSourceEntry)` per
category, so one malformed entry in any single category (e.g. an embedded control character from
a supported operator's edit of `_data/workbench/injection-overrides.json`) set one shared
`loadState` to `'error'` and blanked **all three** dropdowns behind "Could not load the list,"
hiding every valid entry across every category — reproduced end-to-end against the live route.
Fix cycle 1 of 2 against W03-C2, dispatched to `demo-creator-web` with the finding verbatim and
the constraint that both load-bearing defense layers (the `CONTROL_CHARACTER_PATTERN` load-time
rejection and the send-time newline stripping in `TerminalRegion`/`TerminalSession`) stay
unweakened. Fix committed narrowly (`196410b`, only `InjectionDropdowns.tsx` touched): the
whole-payload gate (`isInjectionSources`) is replaced by a shape-only check
(`isInjectionSourcesShape` — are `skills`/`agents`/`prompts` present and arrays?) plus a
per-category `.filter(isInjectionSourceEntry)`, so one bad entry now drops only itself from its
own category; `loadState` becomes `'error'` only for a genuinely malformed top-level payload.
`cd ts && npm run build` after the fix: `✓ 47 modules transformed`, `✓ built in 1.19s`/`1.08s`/
`1.24s` (reproduced independently by the creator, the re-validator and this orchestrator).
W03-V2 was re-dispatched verbatim against the post-fix diff and returned **PASS, no findings** —
confirming closure of the MAJOR and no regression in W03-C2's original R12/W04 obligations
(route-only content, active-tab un-executed injection, disable/degrade semantics, and no
`demo-commands.json` string leaking into `ts/src`, all re-confirmed).

## Acceptance

- No standalone collapse or page-level drop control renders; both live in the ellipsis menu with
  sessions surviving collapse and confirmation guarding drop (REQ-007 W02) — **Met**: confirmed
  by W03-V1's grep and mount-state review.
- Dropped state shows the info page inside unchanged panel bounds with all four injection
  dropdowns visible, disabled and unclickable; restore returns a working terminal (REQ-007 W03)
  — **Met for the mechanism reviewed** (the Commands dropdown, real `disabled` attribute
  confirmed by W03-V1; the Skills/Prompts/Agents dropdowns share the identical `Popover`
  `disabled` mechanism, re-confirmed post-fix by W03-V2), but this remains code-reviewed, not
  browser-measured — W03-W (browser verification, coordinator-dispatched, not run in this
  session) is the measurement of record for the rendered claim.
- Each category injects its exact agreed text un-executed; an overrides-file relabel,
  replacement and hide take effect with no rebuild (REQ-007 W04) — **Met on the reviewed half,
  and now resilient to a malformed override entry**: W03-V2 (both passes) confirmed route-only
  content and the R12 injection path; W03-A's MAJOR and its fix specifically hardened the
  overrides-file path against one bad entry hiding the other 36+ valid ones; the overrides-file
  live-effect claim itself is a browser-observable behavior (W03-W's job), not exercised in this
  session.
- CMD and PowerShell panels on Linux show the in-panel unavailability message with no uncaught
  console errors; bash round-trips (REQ-007 W12) — **Met on the reviewed half**: W03-V3 confirmed
  the shared-implementation and refusal-rendering code paths; "no uncaught console errors" is a
  browser-observable claim for W03-W, not exercised here.

## Backlog

`status: active`, `agent: agent-demo-stage` unchanged. `next_action`: W03-A's one MAJOR is fixed
and re-validated clean (fix cycle 1 of 2 used, 1 remaining if a further finding surfaces); the
gate's item-6 scope finding is closed by the coordinator's deliverables-widening ruling
(`6a63f67`); W03-W (browser verification) remains outstanding, coordinator-dispatched; the three
`test_demo_terminal.py` pytest failures are the recorded environmental defect, not phase work
remaining.

## Unresolved

- W03-W (browser verification) has not run this session — coordinator-dispatched per the pack.
- The three `test_demo_terminal.py` PTY failures are the recurrent host-wide `pyenv` shim
  contention (tracked previously as environmental, e.g. idea `000097` for `phase-wb-02`'s
  identical failures) — not phase-wb-03-specific.
