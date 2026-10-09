---
schema_version: 1
id: doc-session-schema-owned-slots-structural-eligibility
code: SESS-2026-10-08-20
title: Schema-owned slots, sub-slots and structural eligibility (phase-arch-07)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-09'
systems: [sys-wb-layout, sys-wb-styles, sys-demo-stage, sys-wb-terminal, sys-wb-notes, sys-wb-explorers, sys-wb-viewer, sys-ui]
depends_on: [doc-workbench-architecture-quality-requirements, doc-adr-slot-configuration-schema-model, doc-workbench-requirements, doc-workbench-content-fit-contracts-requirements]
---

# Schema-owned slots, sub-slots and structural eligibility (phase-arch-07)

## Phase

`phase-arch-07` (implement schema-owned slots and sub-slots with structural eligibility), group
`G43` of [`PLAN-028`](../01-plans/PLAN-028-workbench-architecture-quality.md). It builds
[`ADR-031`](../04-decisions/ADR-031-slot-configuration-schema-model.md), accepted by the owner on
2026-10-08, against `REQ-011` `R12` (no per-panel allow-list as the eligibility authority) and `R13`
(one top bar per slot, drawn by the slot). Builder A (`agent-builder-a`) under the Session Manager's
run of 2026-10-08, branch `agent/phase-arch-07`, cut from the run's trunk `ccr-b69b05b4-tdcrux` at
`c281b7f`. The session code is 20 because the allocator returns a taken number from a worktree. An
earlier attempt at this phase was blocked only by the deliverable boundary and left nothing behind;
this one started from the trunk.

The cloud run paused at a checkpoint (`8d1968f`, pushed to `origin/agent/phase-arch-07`) when the
owner's cloud credits ran out. On 2026-10-09 the owner ruled that Session 2 (Builder B) finishes the
phase locally, and the claim's `agent` moved to `agent-builder-b` on `dev` (`4cfb05e8`). The branch
was rebased onto that commit with no conflicts; the run's trunk had by then been merged into `dev`.
The checkpoint's remaining steps (gate, backlog entry, this record, the full live self-test) were
done locally, and the owner ratified the nine items under "Ratification" the same day.

## The defect, reproduced first

The `R13` count test was written and committed before any rendering change
(`ts/src/workbench/oneHeaderPerSlot.test.tsx`, commit `3db0b14`). It renders the stage with each panel
assigned into each slot it can occupy, in both layouts, and counts `header` elements and elements
with `role="banner"` in every slot. On the trunk it failed all 25 cases, each with the same
message shape (`layout-1/secondary holding html-viewer: expected 2 to be 1`), because the slot drew
a bar and the hosted panel drew a second one. That is idea `000101`, and it was not confined to a
multi-panel slot: every slot that held one of the eight panel types with a header counted two.

## What was built

- **Two data files and their JSON Schemas.** `_data/workbench/slot-schemas.json` (the element-type
  vocabulary, two frames, `standard` stacked and `compact` inline, and one entry per role) and
  `_data/workbench/panel-elements.json` (each panel type's body kind and ordered bar elements), with
  `schemas/workbench-slot-schemas.schema.json` and `schemas/workbench-panel-elements.schema.json`.
  A frame is a tree of depth two (frame, group, leaf); the group is the top bar and the schema
  rejects a group nested in a group.
- **The matcher, written twice.** `ts/src/workbench/slotMatcher.ts` (pure functions, the browser's
  copy) and `src/workbench/slot_matcher.py` (the Python gate's copy) implement one rule: the role's
  body admits the panel's body kind, and every bar element routes to the first panel-filled bar
  sub-slot that admits its type and still has room. Each file points at the other.
  `_data/workbench/matcher-cases.json` holds hand-written expected answers (all 36 shipped
  panel-and-role pairs and 17 synthetic cases) that `test/test_workbench_slot_matcher.py` and
  `ts/src/workbench/slotMatcher.test.tsx` are both held to. The negative bar-capacity case is a
  `ticker` panel with `["help", "choice", "choice"]` refused for `strip` in both implementations.
- **The frame renderer.** `Slot.tsx` draws one `<header>` and one body from the role's frame. The
  `identity` sub-slot carries the hosted panel's name (or the switcher), `help` and `controls` carry
  what the panel supplies, and `frame_actions` is declared and drawn empty for `phase-arch-17`.
  The `strip` role's `compact` frame is `inline`: the header generates no box and its help and
  controls places share the row with the body, which keeps the strip one thin row.
- **The typed wrapper.** `BarElement` (`ts/src/workbench/BarElement.tsx`) wraps each control a panel
  wants in the bar. It portals the children into the sub-slot of the hosting slot's frame that
  admits the type, through a `SlotFrameContext` that `StagePage.tsx` provides per hosted panel. The
  children stay in the panel's React tree, so a refresh button still sees the viewer's active tab.
  A type the frame has no place for throws during render, and the existing per-panel error boundary
  shows it in the slot. Outside any slot (a panel rendered alone in a test) the children draw in
  place. A reassignment replaces the context value, so the elements move to the new slot and the
  panel does not remount.
- **The six panel files** (`TerminalRegion`, `HtmlViewerRegion`, `OverviewRegion`,
  `FileBrowserRegion`, `ExplorerRegion`, `NotesStripRegion`) lost their `<header>` and now render
  their controls inside `BarElement`s. Their roots are `<section class="stage-panel ...">`, which
  fill the slot body and draw no border. `PANEL_REGISTRY` entries gain
  `elements: panelElements['<id>']`; `displayName:` and `Component:` are unchanged, so `C03`'s parse
  stays green.
- **`eligible_slots` removed, version 4.** Both layout files drop the field and declare
  `schema_version: 4`; the layout JSON Schema now rejects `eligible_slots`. The browser key carries
  the version, so version-3 state is never read, and no migration code was written (`ADR-031`
  decision 10, open item 10 ruled permanent). `useWorkbenchLayouts.ts` and
  `LayoutConfigDialog.tsx` compute eligibility from the matcher on every call; no list of eligible
  slots is kept anywhere. A slot whose frame has no `identity` (so no switcher) refuses a second
  panel, in both the stored-state validation and `setPanelSlot`.
- **`REQ-007` W01, W16 and `REQ-037` amended**, rows kept (see "Amended wording").
- **`ts/vite.config.ts`** allows the dev server to serve `_data/workbench/` (and nothing else
  outside `ts/`) so the two data files can be imported.

## Measured capacities

Each `BarElement` a panel renders is one place in the bar; a group such as the three injection
dropdowns declares `places`. Counted from the nine panels' source:

| Panel type | Body kind | Bar elements (in order) | Places used |
|---|---|---|---|
| `terminal`, `terminal-cmd`, `terminal-powershell` | `terminal-screen` | help; Commands, Skills, Prompts, Agents (choices); the `...` menu (choice) | help 1, controls 5 |
| `html-viewer` | `document-frame` | last-modified badge (status); Refresh (action); file picker, directory picker (choices); embed toggle | controls 5 |
| `overview` | `document-frame` | help; embed toggle | help 1, controls 1 |
| `file-browser` | `tree` | preset select, directory picker (choices) | controls 2 |
| `idea-explorer`, `backlog-explorer` | `table` | view toggle (two buttons) | controls 2 |
| `notes-strip` | `ticker` | help; the controls dropdown (choice) | help 1, controls 1 |

`standard` is `help` 1 and `controls` 5, the measured maximum (the terminal and the viewer both use
5); `compact` is `help` 1 and `controls` 1, which is what the strip uses. No capacity excludes an
assignment `REQ-007` W16 ships. As `ADR-031` predicted, 16 of the 17 panel-in-layout rows match W16
and `overview` in layout 2 is now also eligible for `secondary`.

## Evidence

- **Header count, jsdom** (`ts/src/workbench/oneHeaderPerSlot.test.tsx`, a standing test): all 26
  panel-in-slot cases pass; the 25 that failed on the trunk now pass, plus the new
  `overview`-in-`secondary` case.
- **Header count, a real browser at 1280x720** (Playwright, headless Chromium, Vite 5208 and API
  8038): `node header-count.cjs pairs.json http://localhost:5208` printed `26 cells, 0 failing`, each
  line showing `headers per slot {"secondary":1,"strip":1,"primary":1,"explorer":1}` (layout 2 in
  its own order). The pairs came from the Python matcher, so the browser exercised the same
  eligibility the code uses. The script was a scratch file and is not committed; the command above is the
  record.
- **A reassignment keeps the shell.** In layout 2, `echo MARK-$((6*7))` was typed into bash in the
  `secondary` slot, then `Configure layout` moved Terminal (bash) to `Main` with its confirmation.
  After the move the marker was still in the terminal's rows, the WebSocket count was unchanged
  (3 before and after, the other two being Vite's), the terminal's host sat in `primary`, and each
  slot still counted one header.
- **Content-fit contracts, live, `--quick`** (1280x720 and 1024x768, both layouts):
  `uv run python test/test_workbench_fit_contracts.py --live http://localhost:5208 --quick` printed
  `52 panel cells; floating surfaces measured {'context-menu': 4, 'popover': 54, 'tooltip': 8};
  rules pass=260 fail=0 ...; 0 finding(s)` and exited 0. That is two of the four required sizes. The
  full four-size matrix was not run, as instructed.
- **Differential self-test** (`self_test` of the same module, run directly): `self_test(...)` against the same server judged every candidate cell unbroken first, then injected one
  violation per panel into a region that passed unbroken at 1280x720 and printed `caught` for all
  nine panel types (the three terminals' and the viewer's tab bars given `overflow:hidden`, the notes
  strip's entry moved out, the File Browser tree and both explorer tables collapsed to 12 px, the
  overview frame moved out), with no `UNPROVEN` and no `NOT CAUGHT`. The differential choice picks the
  first breakable region, so it did not pick the new bar rows; those were broken by hand in a second
  run (`.stage-slot__controls .stage-popover__trigger` and `.stage-slot__help .stage-tooltip__trigger`
  moved out of the strip's slot, 1280x720, layout 1), and the judge reported a `visible` finding on
  each, which shows the frame-scoped selector, its CSS scope and its frame bound all work.
- **Content-fit contracts, live, full matrix with the self-test** (local, 2026-10-09, after the
  rebase; Vite 5791 and API 8731, both with `D_SYSTEM_DEMO_TERMINAL=1`):
  `uv run python test/test_workbench_fit_contracts.py --live http://localhost:5791 --self-test`
  printed `104 panel cells; floating surfaces measured {'context-menu': 8, 'popover': 108,
  'tooltip': 16}; rules pass=520 fail=0 n/a(optional region absent)=0; scroll regions exercised in 7
  of 7 (panel, region) pairs; shell unavailable on this host, scrollback not exercised
  (owner-machine, C10): ['terminal-cmd', 'terminal-powershell']; 0 finding(s)` and exited 0. The
  self-test printed `unbroken region passed` and `caught` for all nine panel types. This covers all
  four required sizes; REQ-037's measured state of 2026-10-08 recorded 489 pass and 35 fail on the
  trunk before this run's fix phases.
- **Zero page scroll** held in the screenshots taken at 1280x720 and 1024x768 in both layouts
  (`scrollWidth` x `scrollHeight` equal to the viewport in all four).

## Amended wording

The three amendments are this session's wording; the owner ratified them on 2026-10-09 (item 8
below).

- **`REQ-007` W01** (row id kept): the `?` is the strip's one `help` bar element and the dropdown its
  one `controls` bar element, placed by the slot's `compact` inline frame, so the strip is still one
  thin row; the verification adds that the strip's slot holds exactly one header.
- **`REQ-007` W16** (row id kept): no eligibility list in the layout files; a panel type is eligible
  for a slot when the role's body admits its body kind and the frame has room for its bar elements,
  computed from the two data files; the shipped eligibility is restated (Overview now eligible for
  both slots where declared); the layout files are at version 4; the verification names the
  matcher test, the no-allow-list check and the `eligible_slots` schema rejection. The earlier
  "Eligibility moves from the slot to the panel" note carries an amendment pointer.
- **`REQ-037`**: every `Header controls` row becomes `Bar controls` on `.stage-slot__controls`; the
  notes strip's controls-dropdown and help-tooltip rows move to
  `.stage-slot__controls .stage-popover__trigger` and `.stage-slot__help .stage-tooltip__trigger`;
  a "Bar regions" paragraph states that such a row is searched for in the slot frame and judged
  against the frame's box; `C03` and `C05` are restated; instance 5, the `phase-wbf-02` sentence and
  the measured-state section are updated, and the old header findings are kept as the record of
  what was measured then, with a re-baseline note.
  `test/test_workbench_fit_contracts.py` implements the frame scope (`FRAME_SCOPE_MARKER`,
  `is_frame_scoped`, a `frame` rectangle in the measurement) and builds its live matrix from the
  Python matcher.

## Ratification

These are this session's choices where `ADR-031` left the call to the phase, proposed in the
pre-approved run of 2026-10-08. The owner ratified all nine as built on 2026-10-09, relayed by the
Session Manager to Session 2 (Builder B), which finished the phase locally.

1. **Capacities per frame.** `standard`: `help` 1, `controls` 5. `compact`: `help` 1, `controls` 1.
   They equal the measured maximum, so a panel with a sixth control on a standard slot is refused
   until the schema is edited.
2. **Imported, not fetched.** The two data files are imported into the bundle
   (`PANEL_REGISTRY` refers to them synchronously, and the matcher must answer before the layouts
   load). The cost is that editing one reaches a running page through the dev server's module
   reload, not a plain refresh, unlike the layout files. `ts/vite.config.ts` gains
   `server.fs.allow: [ts/, _data/workbench/]` so the dev server can serve them; the directory, not
   the repository root, keeps `_private/` unreachable through `/@fs/`.
3. **The wrapper API.** `<BarElement type="action|choice|toggle|help|status" places={n}>`. Every
   `BarElement` a panel has is rendered all the time, with any condition inside it, because
   elements land in a sub-slot in the order they first mount. `places` states how many bar places a
   group of controls takes (the terminal's three injection dropdowns, the explorers' two-button
   view toggle), because the files that render those groups (`InjectionDropdowns.tsx`,
   `TerminalMenu.tsx`) are outside this phase's deliverables. The `declared bar elements` test in
   `BarElement.test.tsx` holds the count of rendered places to at most the declared count per type.
4. **A fifth bar element type, `status`.** `ADR-031` lists `help`, `action`, `choice` and `toggle`.
   The HTML Viewer's last-modified badge (`REQ-012` R03, shipped by `phase-wbf-02`) is read-only
   text in the header, and `REQ-012` R03 says the header shows it. None of the four types fits, so
   `status` is added to the vocabulary and to the `controls` sub-slot's `admits`. The alternative
   is to move the badge into the viewer's body, which changes where the owner sees it.
5. **Routing at render time is by type, in declaration order; the matcher's routing also counts
   capacity.** The two agree on every shipped frame because `help` and `controls` admit disjoint
   types. A future frame with overlapping `admits` would need the wrapper to take the element's
   position in the declared list; nothing ships that today.
6. **The frame's identity is the hosted panel's name**, as `ADR-031` decision 1 says, so a slot
   with one panel now shows `HTML Viewer` where it showed the slot's display name `Main`. The slot
   display name still names the section's accessible label and the switcher's popover title.
7. **Bar layout.** Controls sit right-aligned in the bar and wrap onto further rows when they do not
   fit, instead of being clipped. The terminal's `...` menu no longer pins itself to the far
   right on its own; it is the last control in the right-aligned group.
8. **The amended wording** of `REQ-007` W01 and W16 and the `REQ-037` rows, above.
9. **The one-header test counts in jsdom** (a standing vitest test) and the browser count is
   recorded evidence, not a gate, because Playwright is not a dev dependency (the same position
   `REQ-037` takes). A pytest source check (`test_no_panel_source_draws_a_top_bar`) backs it.

## Not done, and why

- The terminal's own collapse flag and `stage-region--terminal-collapsed` class remain in
  `TerminalRegion.tsx`; moving them to a slot frame action is `phase-arch-17`.
- The hard-coded shell ids in `useWorkbenchLayouts.ts` (`SHELL_HOME_SLOT_ID`, the bash and
  PowerShell panel ids) are unchanged and keep `REQ-007` W17's PowerShell default on Windows;
  `phase-arch-08` converts them.
- `frame_actions` is declared in the `standard` frame and drawn empty. Nothing fills it yet.
- Body-kind content floors are not in `slot-schemas.json`; `phase-arch-09` builds that table.
- CMD, PowerShell and Windows checks are owner-machine, not run. The CMD and PowerShell panels'
  scrollback regions were not exercised here either (the shells are unavailable on Linux); `C10`.
- `brain/concepts/terms-workbench-ui.md` and `docs/08-governance/GLOSSARY.md` still describe a
  per-panel `eligible_slots`; they are outside this phase's deliverables. Sent to Ideation as an
  idea on 2026-10-09; Ideation is holding it until the next free id.

## Gate checks

Run locally on 2026-10-09 in `../d-system-worktrees/phase-arch-07`, after the rebase onto `4cfb05e8`:

- `uv run python -m src.governance`: `Governance OK: 45 systems, 478 documents, 37 memories, 357
  backlog phases`. `--catalog` regenerates with no diff.
- `uv run pytest`: `2175 passed, 1 warning in 906.66s`. The two failures the cloud checkpoint
  recorded (`test_control_characters_reach_the_shell` under load and
  `test_an_unwritable_worktree_parent_is_refused` as uid 0) both pass on this machine.
- `uv run ruff check src/ test/ tools/`: `All checks passed!`
- `uv run mypy src/`: `Success: no issues found in 54 source files`
- `cd ts && npm test`: `Test Files 18 passed (18)`, `Tests 277 passed (277)`, including
  `LayoutConfigDialog.test.tsx`, which the checkpoint had not run.
- `cd ts && npm run build`: built (chunk-size warning only). `npm run typecheck` and `npm run lint`
  exit 0.

The cloud checkpoint's last full run, before the final commit, was `2 failed, 2167 passed, 1 skipped
in 374.98s`, with the two failures named above.
