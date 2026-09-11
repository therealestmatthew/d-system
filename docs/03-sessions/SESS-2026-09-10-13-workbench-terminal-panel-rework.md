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

W03-W (browser verification, coordinator-dispatched) — **PASS on all six items** with measured
evidence: (1) only the two menu controls exist; a live `seq`-loop survived collapse/re-expand
(tick counter matched wall time) and was still ticking at the drop confirmation, its child
process gone from `ps` within 2 seconds of confirming; (2) drop-in-place — outer panel bbox
byte-identical before/after (`716.9 × 778.4`), all four dropdowns carrying real `disabled`
(click timed out as "not enabled", focus refused), restore round-tripped `echo`; (3) enumeration
matched the filesystem exactly (3 skills, 11 agents, 23 prompts), one injection per category
exact and un-executed with Enter then executing; the overrides live-edit (relabel, replace,
hide) took effect on refresh with zero rebuild, verified in API and UI; the fix confirmed
behaviorally — one malformed entry dropped only itself (3→2 skills) with no console errors;
(4) bash round-trips; CMD and PowerShell each render the in-panel unavailable message naming
the shell; (5) flag-off degradation correct — labeled disabled dropdowns, the ADR-013 absent
message, no uncaught exceptions — with a recorded cosmetic caveat: four network-404 resource
logs from the app probing the designed-absent workbench routes (idea `000100`); (6) zero
scroll (`{x:0, y:0}`) and no overlapping regions at all four sizes.

At close, re-run by the coordinator on dev after integration (`72506f4`, completion `1d81d08`):
`uv run python -m src.governance` — exit 0; staged `check_no_private_content.py` — `OK (486
tracked files, 31 identifiers checked)`.

## Acceptance

- No standalone collapse or page-level drop control renders; both live in the ellipsis menu with
  sessions surviving collapse and confirmation guarding drop (REQ-007 W02) — **Met**: confirmed
  by W03-V1's grep and mount-state review.
- Dropped state shows the info page inside unchanged panel bounds with all four injection
  dropdowns visible, disabled and unclickable; restore returns a working terminal (REQ-007 W03)
  — **Met**: W03-W measured identical panel bounds before/after drop, click and keyboard both
  refused on every dropdown, and a working round-trip after restore.
- Each category injects its exact agreed text un-executed; an overrides-file relabel,
  replacement and hide take effect with no rebuild (REQ-007 W04) — **Met**: W03-W verified all
  three per category (exact text, un-executed, Enter executes) and the live overrides edit
  effective on refresh with no rebuild; the W03-A fix confirmed behaviorally (one malformed
  entry drops only itself).
- CMD and PowerShell panels on Linux show the in-panel unavailability message with no uncaught
  console errors; bash round-trips (REQ-007 W12) — **Met**: W03-W measured both in-panel
  messages naming the shell, bash round-trips, and no uncaught exceptions (the only console
  entries anywhere were flag-off network-404 resource logs, recorded as cosmetic under idea
  `000100`).

## Backlog

`status: complete`, `agent: agent-demo-stage` retained as the record of who did the work.
`next_action` is the "None — phase complete" close note. `completion_evidence` names the nine
shipped files plus this session record. `result` records the full arc: first-pass items, the
gate with its two rulings (environmental pytest; the ADR-016 deliverables widening), the W03-A
major and its fix, W03-W's six measured passes with the flag-off caveat, the orchestrator's
self-reported process deviation, and the fast-forward integration at `72506f4` (completion
commit `1d81d08`). `phase-wb-03` removed from `next_up`.

## Unresolved

- The three `test_demo_terminal.py` PTY failures remain the recurrent host-wide pyenv shim
  contention (ideas `000097`, `000099` — the latter annotated with the evidence clearing the
  suspected wb-01 commit). Host-level fix is the owner's.
- Flag-off console 404 noise is cosmetic, tracked as idea `000100`.
- Owner-side commands pending: `git push origin dev`, and worktree/branch cleanup for the three
  merged phases (`phase-wb-01`, `phase-wb-02`, `phase-wb-03`).

## Review

Independent sub-agent review at close (fresh agent, range `f62611e..1d81d08`, its own reruns).
Findings pasted:

- **Scope containment**: "The phase's four own commits touch only `ts/src/stage/*`,
  `ts/src/workbench/panelRegistry.tsx`, `ts/public/demo-commands.json`, and the two
  `_data/workbench/layouts/*.json` files (admits-line change only, exactly matching the
  ADR-016 widening ruling). Nothing outside the declared deliverables; no `test/` or `src/`
  file touched, which confirms the attribution of the three `test_demo_terminal.py` PTY
  failures to the pre-existing host pyenv defect without a rerun."
- **Condition 1 (W02) — HOLDS.** "Controls only in `TerminalMenu.tsx` (the sole home;
  in-bubble confirm before `onConfirmDrop` fires). Sessions survive collapse structurally:
  `TerminalRegion.tsx:495-505` always mounts every `TerminalSession`; collapse flips only a
  CSS class and the `visible` prop."
- **Condition 2 (W03) — HOLDS.** "Dropped state swaps only the body div inside the same
  section/header structure; the disabled mechanism is a real HTML attribute (`Popover.tsx:163`)
  plus force-close-on-disable. W03-W's bbox/click-refusal measurements are consistent with
  this code."
- **Condition 3 (W04) — HOLDS.** "`sendToActiveSession(injection, false)` with send-time
  `\r\n` stripping — un-executed by construction; entries come solely from the runtime fetch,
  so an overrides edit needs a refresh, never a rebuild. The W03-A fix is real in merged code:
  shape-only top-level check, per-category `.filter`, no whole-payload `.every` gate anywhere;
  `CONTROL_CHARACTER_PATTERN` intact in both dropdown components."
- **Condition 4 (W12) — HOLDS.** "All three panel ids share one `TerminalRegion` via two thin
  wrappers — no duplicated terminal component. The refusal is shape-parsed and rendered as the
  backend's own shell-naming message in-panel, never thrown."
- **Reruns**: build ✓, governance exit 0, staged private-content check byte-identical to the
  record's close line. `demo-commands.json` strings absent from `ts/src` (zero grep matches);
  the startup-race fix present.
- **Discrepancies: none material.** Two notes, neither a record error: the governance document
  count moved 158→160 from later coordinator/peer commits (the record attributes its number to
  the earlier run correctly), and the record's close edits were staged-but-uncommitted at
  review time, as expected mid-close.
- **Verdict (verbatim)**: "all four acceptance conditions hold; the record's claims are
  supported by the diff and reruns. No blocker to marking the phase complete."

## Decisions

- The gate's item-6 scope red ("diff touches nothing outside ts/") was ruled a checklist-wording
  lag, not a violation: ADR-016 deliberately puts a slot's `admits` list in layout data, so
  registering the shell panels required editing the two layout JSON files. The coordinator
  widened the phase's declared deliverables (`6a63f67`) per AGENTS.md's declaration-widening
  rule — the second phase in a row where the pack's file-scope wording lagged the ratified
  architecture (wb-02's `vite.config.ts` was the first).
- W03-W's item-5 caveat (four network-404 console resource logs with the flag off) was ruled
  within the requirement's intent — degradation is correct, no uncaught exceptions — and the
  cosmetic noise recorded as idea `000100` rather than spent as a fix cycle.
- A peer session's mid-build report suspecting a wb-01 commit for the PTY test failures was
  answered with timeline evidence rather than a code change: the failures pre-dated that
  commit's merge, and the suite ran 46/46 green with the commit in place the moment the pyenv
  lock was removed. The evidence went into idea `000099` as a finding annotation; no
  `src/demo/posix.py` change was made.
- Session-limit interruptions (the orchestrator and one gate dispatch died mid-run when the
  API session limit hit) were handled by resuming the same agents with verified repository
  state, never re-running from scratch — the pack's idempotency held.

## Corrections

- The orchestrator dispatched W03-V3 before committing W03-C3's work, against the explicit
  commit-before-validate instruction; it flagged the deviation itself, the validator assessed
  the real worktree state, and the commit followed immediately — no rework needed, recorded as
  a process error.
- The W03-G gate's first dispatch was cut off by the session limit before any result and was
  correctly discarded and re-dispatched, not treated as a verdict.

## Left undone

- The Windows halves of W12 (CMD/PowerShell round-trips on the owner's machine) belong to
  phase-wb-07's owner-machine conditions, as the pack defines.
- The host-level pyenv fix, the dev push, and the three merged worktree cleanups — owner's
  hands, listed above.
- Phases wb-04 through wb-07: the coordinator session pauses here by the owner's direction;
  the handoff file `_working/coordinator-handoff.md` carries the resume state, and the next
  coordinator session continues at phase-wb-04 (W04-K, demo-orch-data).
