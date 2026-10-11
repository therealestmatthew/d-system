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
  per-panel `eligible_slots`; they are outside this phase's deliverables. Recorded as idea `000690`
  on 2026-10-09.

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

## Review round 1 (2026-10-09)

Verdicts on `0f043854`, committed unchanged in `b2682aef`: gating `demo-adversary` pass with two
minors, the security stand-in (`demo-adversary-2`) reject with one major, `review-judge` (shadow)
pass.

**Test baseline sign-off.** `tools/check_test_baseline.py` against dev `4cfb05e8` reported one test
that passed in the base and is missing in the branch:
`test.test_workbench_layout_schema::test_panel_with_no_eligible_slot_fails_schema`. Commit
`c487acdf` removed it with the `eligible_slots` field it exercised; it is superseded by
`test_layout_carrying_an_eligibility_list_fails_the_schema` (any `eligible_slots` fails the schema,
per shipped layout) and by `test_panel_with_no_eligible_slot_fails_invariant`, rewritten to the
structural rule. The owner signed off on its removal on 2026-10-09, relayed by the Session Manager.

**Minor F01** (the R12 scan did not cover Python sources): fixed. The scan in
`test_no_source_or_data_file_carries_a_per_panel_or_per_slot_allow_list` now also reads
`src/**/*.py`; a probe file holding `eligible_slots` under `src/workbench/` made it fail, and the
probe was removed.

**Minor F02** (stale `eligible_slots` prose in `brain/concepts/terms-workbench-ui.md` and
`docs/08-governance/GLOSSARY.md`): outside the deliverables; recorded as idea `000690`.

**Major F01, security stand-in** (a symlink under the new `server.fs.allow` directories is
followed). Vite checks `server.fs.allow` by path prefix and does not resolve symlinks. A prototype
on a throwaway root showed the same file served two ways: through `/@fs/<absolute path>`, the
reviewer's case, and through a plain root-relative URL for a symlink under the Vite root. The second
route existed before this phase, since `ts/` is always the root. Fixed in two parts, by owner
ruling of 2026-10-09:

- `refuseSymlinkEscapes` in `ts/vite.config.ts`, first in `plugins` and attached directly in
  `configureServer`, so it runs before Vite's own middlewares. It realpaths the file a request names
  (the `/@fs/` path, or the path under the root or its `public/` directory) and returns 403 when
  the real path lies outside the allow-list. `server.fs.allow` and the guard take one shared list,
  `devServerAllow`, and the config's comments now say the allow-list alone does not stop a symlink.
  `ts/vite.config.test.ts` (a Vitest test in Node, added to `ts/vitest.config.ts`'s include list)
  builds a tree with outside-pointing symlinks and runs a real Vite dev server over it. Without the
  guard, both routes return 200 with the outside file, which reproduces the hole. With it, four
  escape URLs (including a `%2E%2E` variant) return 403, and allowed files are still served. With
  the guard's refusal disabled, the blocking test fails.
- `test_no_tracked_symlink_under_the_dev_server_allow_list` in
  `test/test_workbench_slot_matcher.py` fails on any `git ls-files` mode-120000 entry under `ts/`
  or `_data/workbench/`; a symlink staged only in the index made it fail. Today there are none,
  and all 23 symlinks under `ts/node_modules` point inside `ts/`.
- Live check against this worktree's own dev server, with temporary untracked symlinks under
  `_data/workbench/` and `ts/` pointing at a scratch file: both returned 403, and `/`,
  `/src/main.tsx`, `slot-schemas.json` and `panel-elements.json` returned 200. The symlinks were
  removed afterwards.

The owner widened the deliverables to name `ts/vite.config.test.ts` and `ts/vitest.config.ts` and
ruled that the guard covers root-relative URLs as well as `/@fs/`.

## Review round 2 (2026-10-09)

On `5fe933fa` the functional gating review passed with no findings. The security stand-in
rejected with one blocker: `/workbench-layouts/<name>` served a symlink under
`_data/workbench/layouts/` that pointed outside, because that route checked containment textually
and the guard did not map its prefix. An audit of every file-serving route in `ts/vite.config.ts`
found the same gap in all three; each was reproduced live against this worktree's dev server with
`D_SYSTEM_DEMO_TERMINAL=1` and a temporary untracked symlink, and each returned 200 with the
target's content:

- `/workbench-layouts/` (the blocker): textual check only.
- `/generated-overview/`, which serves `_public/`: textual check only. `_public/` is outside the
  dev server's allow-list, so the guard cannot map it; the route must check itself.
- `/workbench-file/`, which serves any non-ignored repository file: it resolved symlinks against
  the repository root, but ran `git check-ignore` and the `.git` segment check on the requested
  path only, so a symlink in a tracked directory to an ignored file (`_private/` or `_working/`)
  was served.

Fixed at both layers. The guard takes a map of this config's own route prefixes to their
directories and checks `/workbench-layouts/` through it. `realPathWithin` is a new helper, and
`/workbench-layouts/` and `/generated-overview/` now refuse with 403 a file whose real path leaves
their directory. `/workbench-file/` runs the `.git` check and `git check-ignore` on the resolved
repository-relative path as well as the requested one. A `.git` target gets 403; an ignored target
gets 404, as an ignored file already did. The three route plugins take their directory or root as
a parameter, defaulting to the old constants, so the test can point them at a scratch tree.
`realRepoRoot` moved into the route.

`ts/vite.config.test.ts` gains four cases, seven in all:
- A route with only a textual check serves the symlinked layout (the reproduction), and the guard's
  prefix mapping refuses it.
- `/workbench-layouts/` refuses its symlink and serves a real layout.
- `/generated-overview/` refuses its symlink and serves a real page.
- `/workbench-file/` over a scratch git repository: 404 for a symlink to an ignored file, 403 for
  one into `.git/`, and the real file served.

With the three route checks disabled, those three tests fail; restored, 7 of 7 pass. The live
re-check on the worktree's dev server gave 404, 403 and 403 for the three symlinks, and 200 for
`layout-1.json`, `README.md`, the generated overview page and `/`. The temporary symlinks and the
scratch file were removed.

The reviewer's major finding, that the check-then-serve sequence is not atomic, went to the owner,
who ruled on 2026-10-09 that it is fixed in this phase (round 3 below).

## Review round 3: the check-then-serve race (2026-10-09)

The round 2 verdict records are committed unchanged in `bb003e90`. They are the functional gating
pass, the security reject (F01 the layouts route, F02 the race) and the shadow pass with one
minor. That minor, the Python allow-list scan reading `src/` only, is fixed: the scan now reads
`tools/` as well, and a probe file under `tools/` made it fail. `test/` stays out of the scan,
because tests name the fields to assert they are gone.

**The race leaked, not only crashed.** A probe ran a real Vite 6 dev server, plus a child process
renaming a regular file and an outside-pointing symlink over one name (about 9,000 swaps a
second), while 16 requests ran at a time for 2.8 s. Under the round 2 code, responses carrying the
outside file numbered 312 on `/workbench-layouts/`, 682 on `/race.txt` (`ts/public/`) and 925 on
`/@fs/`. Every run also logged two or three uncaught exceptions, which would have ended a real dev
server.

**The fix: one descriptor, opened then checked, is the only thing read.**
- `openChecked` opens the name, then checks the open file. On Linux it reads the real path from
  `/proc/self/fd/N`. Elsewhere it requires `lstat(realpath(name))` to be a regular file with the
  descriptor's device and inode, compared as bigints. The real path must lie inside the allowed
  directories.
- The result is `'absent'`, `'changed'` (a rename replaced the opened file), `'forbidden'`, or the
  descriptor. A changed name is retried up to five times and is never handed on to code that would
  open the name again.
- Bytes come only from that descriptor: `streamChecked`, which has an error handler and closes the
  descriptor on end, failure or client abort, and `readChecked`.
- The three config routes serve this way, and the `/workbench-file/` checks and Markdown render
  use the descriptor and its real path.

**Vite's own paths.** The guard now serves, from the checked descriptor, every GET or HEAD that
Vite would send as the file stands: a non-module extension, any query but `?import`. A `load` hook
(`enforce: 'pre'`) gives the transform pipeline source modules and `?raw` imports from a checked
descriptor, outside `node_modules`. A second middleware, registered after Vite's single-page
fallback, serves `.html` pages through `server.transformIndexHtml` from a checked descriptor. The
uncaught exceptions came from Vite's file watcher (chokidar's `readlink` `EINVAL` on the flipping
name), not from serving: with the watcher off there were none. The guard now listens for watcher
`error` events and logs them.

**Measured after the fix**, same probe, ten paths: `/workbench-layouts/`, `/generated-overview/`,
`/workbench-file/`, `/race.txt`, `/@fs/`, a `.ts` module, `?raw`, `?t=`, `.json?import` with a
JSON-valid secret, and `index.html`. Every one gave 0 responses with the outside content, 0
uncaught exceptions, and a server still answering. `?inline` on an SVG also gave 0, but the guard
does not cover it by design.

**What remains uncovered** (corrected in round 4 below). Every request that names a file is
checked, so a symlink or hard link leading outside is refused (403) on every route, including
under `node_modules` and on every import query. Two kinds of request are checked and then read
again by name, so they are not protected against a swap between the check and the read:
- source modules under `node_modules`, which the `load` hook passes through;
- import queries other than `?raw` (`?inline`, `?worker`, `?url`), which the plugins that own them
  read.
On macOS and Windows there is a further gap: a directory component of the real path swapped to a
symlink between `realpath` and `lstat`. Linux reads the descriptor's own path and has no such gap.

**The test.** `ts/vite.config.test.ts` gains a race case. For eight routes it builds a fresh tree
and server, runs the toggler for 1.2 s with 16 requests in flight, and asserts that no response
contains the secret, that the toggler made more than 50 swaps, that the server still answers, and
that no uncaught exception was recorded. It passed 5 runs out of 5, about 12 s for the whole file.
Its sensitivity was measured by mutation:
- Restoring the round 2 guard behaviour (check once, then hand every request on) failed 3 runs out
  of 3, on `/race.txt`.
- Making `/workbench-layouts/` reopen its name instead of streaming the checked descriptor failed 2
  runs out of 3.

The test is bounded and probabilistic: it can miss a regression, but it cannot fail against a
correct guard.

**Regression check on the real app**: with the worktree's backend and dev server, the live REQ-037
check `--quick` printed `52 panel cells ... rules pass=260 fail=0 ... 0 finding(s)` and exited 0.
The same check with `--self-test` exited 0 and caught all nine injected violations. JSON imports,
`?import`, modules and plain JSON gave the same responses with and without the guard.

## Review round 4: hard links (2026-10-09)

On `91580253` the security stand-in returned pass with findings. Its live attack confirmed the
race fix: the race test fails against `ca00beda`, and a toggler with 400 requests got nothing out,
with the server up and file descriptors flat. One major remained, by owner ruling of 2026-10-09: a
hard link inside a served directory to an outside file was served on every route. The reviewer
reproduced it through `ts/public/`, through `/@fs/` on `_data/workbench/` and through
`/workbench-file/` on `docs/`. A hard link is a second name for the same file, so the opened file's
`/proc/self/fd` path and its inode both look like an inside file.

Fixed in `openOnce`: a regular file whose `fstat` link count is above 1 is refused with 403.
Files under the root's own `node_modules` are exempt, because package managers hard-link packages
there. The first version matched a `node_modules` segment anywhere in the real path; round 5 below
anchors it.

No tracked file in this worktree or the primary checkout has a link count above 1, and no file of
any kind under `ts/` (outside `node_modules`), `_data/workbench/` or `_public/` has one, so the
rule refuses nothing the workbench serves today. On the worktree's dev server, `/`,
`src/main.tsx`, a `.ts` module, `slot-schemas.json?import`, `layout-1.json`, `README.md` through
`/workbench-file/`, the generated overview page and `/@vite/client` all returned 200.

`ts/vite.config.test.ts` gains two cases, ten in all:
- Seven URLs naming a hard link to an outside file, across Vite's public and `/@fs/` paths,
  root-relative, `?raw` and the three config routes, all return 403 without the content. With the
  link-count check removed, that test fails.
- A hard-linked file under `node_modules` is still served.

The minor finding, that the comment in `vite.config.ts` overclaimed what is not covered, is fixed:
the comment now says that every file-naming request is checked, and names the two kinds of
request that are read again by name after the check.

**Functional gating on `91580253`: pass with findings, one major.** The race test's toggler child
was stopped and awaited only when a case succeeded. A case that failed an assertion, or a test run
that was killed, left it running with no deadline. The reviewer found two such togglers at 82% CPU,
about 47 minutes old, with their `/tmp/vite-fs-guard-*` trees, and removed them. They came from
this session's own mutation runs, in which the race assertion failed inside the loop before the
stop step. The same runs also left 70 probe trees (`/tmp/race-*`, `/tmp/jp-*`) from the scratch
probe; those were removed as well.

Fixed in `ts/vite.config.test.ts`. Every race case runs its toggler through `withToggler`, which
kills it with `SIGKILL` and waits for it in a `finally`, and each case's tree is removed in its
own `finally`. The toggler script exits at its own deadline (10 s by default) and as soon as its
parent is gone, when its stdin pipe ends or its parent process id changes. Three new cases, 13 in
all:
- a failing body leaves no live toggler;
- a toggler that is never stopped ends at its deadline;
- killing the process that started a toggler, a stand-in for a test worker, ends the toggler
  within 5 s.

Checked by hand as well. A race case failing under the round 2 mutation left no toggler and no
tree. Killing Vitest with `SIGKILL` mid-race ended its toggler within 3 s, but left that case's
tree, since no cleanup code runs after `SIGKILL`; it was removed by hand. The file passed 3 runs
out of 3.

## Review round 5 (2026-10-09)

On `6e29c8d0` the security stand-in rejected with one blocker. The `node_modules` exemption was
a regex matching that segment anywhere in the real path, so any directory named `node_modules`
reopened the hard-link hole. The reviewer reproduced it with `data/node_modules/evil/hard.txt`
and `ts/src/node_modules/evil/hard.txt`, both hard links to an outside file, served with 200
through `/@fs/` and through a root-relative URL. `serveRepositoryFiles`, rooted at the whole
repository, was the broadest case.

Fixed by anchoring the exemption. `openChecked` takes an explicit list of resolved package
directories in which a hard-linked file may be served:
- The guard passes only `realpath(<root>/node_modules)`, that is `ts/node_modules`.
- The three config routes pass none, so `/workbench-file/` refuses every hard-linked file.
- The `load` hook leaves to Vite only modules inside that same directory, compared both textually
  and resolved, instead of any path with the segment.

The hard-link test now also requests `data/node_modules/evil/hard.txt` and
`src/node_modules/evil/hard.txt`, through `/@fs/` and root-relative, and
`/workbench-file/node_modules/evil/hard.txt`; all are 403. A hard-linked file under the root's own
`node_modules` is still served through both `/node_modules/...` and `/@fs/`. With the old
free-floating regex put back, the test fails on the reviewer's case
(`/@fs/.../data/node_modules/evil/hard.txt: expected 200 to be 403`). The comments in
`vite.config.ts` say which `node_modules` is meant.

Waiting on the owner, not acted on: the reviewer's major finding that import queries other than
`?raw` still leak under a race. `/data/race.svg?import&url` leaked the secret in 122 of 544
requests. This is the residual the comment and this record already name.

## Review round 7: the import-query race (2026-10-10)

Records committed unchanged in `0f4078bd`:
- `demo-adversary-5`: functional pass. F01, the orphan toggler, was fixed in `3f8af063`.
- `demo-adversary-6`: security pass. F01 (hard links) and F02 (the comment) are fixed.
- `review-judge-3`: shadow reject, three findings.
  - F01, that `vite.config.test.ts` never runs, is not applicable. The judge read dev's
    `vitest.config.ts`; on this branch the include list names the file, and the runner's 19 test
    files are the 18 under `src/` plus this one.
  - F02, that the non-Linux fallback's check window is narrower than the `/proc/self/fd` path, is
    accepted as it stands. It fails closed on a device or inode mismatch, and "What remains
    uncovered" above names it.
  - F03 is the import-query race fixed below.
- `demo-adversary-7`: round 5 security reject. F01 (the free-floating `node_modules` regex) was
  fixed in `d2a3e4be`. F02 is the import-query race.

**The race.** Owner ruling of 2026-10-10: fix it in this phase. The reviewer's case,
`/data/race.svg?import&url` raced against a toggler, leaked 122 of 544 requests at `6e29c8d0`.
Vite's source (6.4) shows two paths that read an asset by its name:
- A `?raw`, `?url` or `?inline` request, or an SVG one, first passes `checkServingAccess`. For a
  URL that no module has imported yet, that check falls back to Vite's static server, which sends
  the file raw. This is the reviewer's case.
- From a module, the transform pipeline's asset plugin reads the file to build the module, for
  example to inline a small SVG as a data URL.

Worker sources (`?worker_file`) were read by name as well, because the `load` hook skipped every id
with a query.

**The fix.** The guard never leaves an asset query (`?raw`, `?url`, `?inline`) or an asset
`?import` to Vite, except under the root's own `node_modules`, which is unchanged.
- From a module (an `import` parameter, or `Sec-Fetch-Dest: script`), the request goes straight to
  `server.transformRequest`, skipping the serving-access fallback.
- Fetched directly, it gets the file's bytes from the checked descriptor, as Vite's static server
  would send them.

The `load` hook now answers, from the checked descriptor:
- `?raw`: the text, as before.
- `?url`, and a plain import of an asset type: the URL. The file is checked but not read, and
  fetching the URL goes through the guard's static path.
- `?inline`: CSS text, which Vite's CSS plugin compiles, or a base64 data URL for anything else.
- `?worker_file`: the worker source.
- `?direct` and `?used` CSS: the text.

`?worker` and `?sharedworker`, including `?worker&inline` in dev, stay with Vite's worker plugin,
whose module only names the worker URL. No query type had to be refused.

**What changes for the app.** A module importing each query type was compared with and without
the guard:
- The worker wrappers, the worker source, CSS, CSS `?inline`, `?raw` and JSON are identical.
- A small SVG imported plainly or with `?url` now exports its URL, where Vite inlined it as a
  data URL.
- An `?inline` SVG is base64 rather than percent-encoded.

**Measured.** The race test now has 20 cases, using `withToggler`, 1.2 s each and 16 requests in
flight. The new cases are the reviewer's direct `?import&url`, plus `?import&url`, `?import&inline`,
`?import&raw` and a plain `?import` of an SVG from a module; CSS `?inline` from a module and
directly, CSS `?url` and `?raw`; and `?worker`, `?worker&inline` and `?worker_file`.

Against `vite.config.ts` as it stood at `d2a3e4be`, every asset and worker query case leaked:

| Request | Leaked |
|---|---|
| `?import&url`, direct | 146 of 1,040 |
| `?import&url`, from a module | 145 of 992 |
| `?import&inline` | 208 of 1,088 |
| `?import&raw` | 218 of 1,168 |
| plain SVG `?import` | 217 of 1,072 |
| CSS `?inline`, from a module | 182 of 1,040 |
| CSS `?inline`, direct | 196 of 1,104 |
| CSS `?url` | 187 of 1,088 |
| CSS `?raw` | 214 of 1,200 |
| `?worker&inline` | 232 of 1,200 |
| `?worker_file` | 226 of 1,200 |

The `?worker` wrapper leaked nothing, because it reads nothing. With the fix, all 20 cases had 0
leaks, in about 22,000 requests. Run against the old file, the committed test fails on the
reviewer's case (`/data/race.svg?import&url: expected '<svg>SECRET</svg>' not to contain
'SECRET'`).

**Regression check on the real app**, on the worktree's backend and dev server: the live REQ-037
check `--quick` printed `52 panel cells ... rules pass=260 fail=0 ... 0 finding(s)` and exited 0.
The dev server log had no errors.

## Review round 8 (2026-10-10)

On `59121c16` the security stand-in rejected with two blockers, both within the existing rulings.

**Blocker 1: a symlinked `node_modules`.** The hard-link exemption was `realpath(<root>/node_modules)`,
so if that name was a symlink to a directory inside the allow-list (a decoy in `ts/`), hard links
there were served: `/node_modules/leak.txt` and `/decoy/leak.txt` both returned the secret.

Fixed: the exemption applies only while `<root>/node_modules` is a real directory (`lstat`, not a
symlink). It is then the resolved root joined with `node_modules`, so the last component is never
resolved through. If the name is a symlink, nothing is exempt. The `load` hook's pass-through uses
the same test.

A new case makes `<root>/node_modules` a symlink to a decoy holding a hard link to the secret. It
requests both names, root-relative and through `/@fs/`, and all four get 403. Against the
`59121c16` config it fails.

**Blocker 2: `load` protected an enumerated list.** Any other query fell through to Vite's
fallback, which reads the file by name. Under a race, `GET /data/swap.ts?foo=bar` with
`Sec-Fetch-Dest: script` served the swapped secret module, transformed.

Fixed by design. For every file inside the allow-list and outside the root's own `node_modules`,
`load` now answers from the checked descriptor whatever the query:
- `?raw`, `?url` and `?inline` as before;
- otherwise the file's text, which is what Vite's fallback would have read;
- for an asset type, its URL.

A file in scope that cannot be opened is refused with an error rather than handed back. Otherwise
a dangling symlink could be retargeted between the check and Vite's read.

The one exception is `?html-proxy`. Vite's HTML plugin supplies that content from its own
in-memory copy of an inline `<script>`, not from the file; the app's `index.html` has none.
`?worker` and `?sharedworker` now also get the file's text, which Vite's worker plugin discards in
dev in favour of a wrapper that names the worker URL.

Three race cases with a query no plugin claims were added: `race.ts?foo=bar` and
`race.css?foo=bar` from a module, and `race.svg?import&foo=bar`. Against the `59121c16` config the
test fails on the first: `/data/race.ts?foo=bar: expected 'export const x = "SECRET"; …' not to
contain 'SECRET'`.

**Major: the two worker-wrapper cases.** `?worker` and `?worker&inline` cannot fail in dev, because
the wrapper never contains the file's bytes. They are now labelled in the test as not evidence of
protection, kept only to show the wrapper is still served while the name flips. `?worker_file` is
the case that reads a worker's source. So of the 23 race cases, 21 can detect a leak.

**A regression caught by the live check before commit.** The first version of the default-protect
`load` treated every absolute-looking id as a file. `@vitejs/plugin-react`'s virtual module
`/@react-refresh` therefore failed with "could not be opened": the dev server logged 23 errors and
the live REQ-037 check exited 1. The vitest suite did not catch it, because its servers run no
plugin with such an id.

Fixed by scoping the hook: a path is in scope only if it lies inside the allow-list, as named or
resolved. Anything else is left to the plugin that owns it, or to Vite's own `server.fs.allow`. A
new case, "leaves a virtual module with an absolute-looking id to the plugin that owns it", runs
a stand-in plugin with a `/@virtual-thing` id; without the scope check that test fails. The
vitest file now has 15 cases.

**Functional review of `59121c16`: one blocker and one major.**

*Blocker: the guard ran in `vite build`.* Its `load` answered an asset import with the dev-server
URL, so a build compiled `import logo from './logo.svg'` to `"/src/logo.svg"` and emitted no asset.
The app imports no assets today, so nothing shipped broken, but the defect was latent.

Fixed: the plugin is `apply: 'serve'`. A new case runs a real `vite.build()` with the guard
installed, on a fixture whose module imports an SVG both plainly and with `?url`, with
`assetsInlineLimit: 0`. It asserts `dist/assets/logo-*.svg` exists and that the built JavaScript
references `/assets/logo-…` and never `/src/logo.svg`. Without `apply: 'serve'` it fails ("assets:
index-….js: expected undefined to be defined").

*Major: killing the top-level test run left its pool worker racing.* The toggler watched only its
direct parent, the Vitest worker. When the top-level `vitest` (or `npx`) was killed, the worker
survived, orphaned, and went on starting new race cases.

Fixed: the worker reads its ancestors from `/proc` on Linux: its parent, the top-level `vitest`,
`npm exec`, and so on up to init. On other platforms only the direct parent is known. The worker
passes that list to each toggler. Both the toggler and the race loop stop as soon as any ancestor
is gone, counting a zombie as gone. The race loop then throws "the test run was killed", and its
`finally` blocks kill the toggler and remove the tree.

A new case kills a stand-in top-level process whose stand-in worker survives, and the toggler
still ends within 5 s. By hand, `kill -9` of the real `npm exec vitest` about 6 s into the race
test ended the toggler within 1 s. The orphaned worker failed the case with "Error: the test run
was killed" and the run ended, leaving no Vitest or toggler process and no tree.

The guarantee as built: on Linux, the race stops when any ancestor of the test worker ends;
elsewhere, when the worker's direct parent does. The vitest file now has 17 cases.

**Records for `59121c16`**, committed unchanged in `e44c4797`:
- functional reject, whose blocker and major are fixed above;
- security reject, whose two blockers and major are fixed above;
- review-judge shadow pass with one minor, which is accepted.

The minor says a bare direct `?worker` fetch is untested. A direct `?worker` request is a
JavaScript request, so Vite transforms it into the same wrapper as the module case, and in dev
that wrapper only names the worker's URL. A race case for it could not fail, like the two
`?worker` cases already labelled as non-evidence. The worker's own bytes are covered by the
`?worker_file` case.
