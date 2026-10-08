---
schema_version: 1
id: doc-workbench-content-fit-contracts-requirements
code: REQ-037
title: Workbench content-fit contracts
kind: requirement
status: draft
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-layout, sys-wb-styles, sys-wb-shared]
depends_on: [doc-workbench-architecture-quality-requirements, doc-workbench-requirements]
---

# Workbench content-fit contracts

## Observed problem and scope

`REQ-011` R09 requires every workbench panel to state what overflows, what scrolls, what truncates
and what reflows, and to have each statement asserted mechanically. `R10` requires that a panel
added without such a statement fails a check. This document is the contract document `R09` points
at, and the two tables below are its machine-readable form: `test/test_workbench_fit_contracts.py`
reads them.

Until now fit was verified by an agent driving a browser against a checklist (`REQ-007` W15 and W18
name the checks) and by the owner noticing. Nothing in `test/` or `ts/src` asserted any of it, so
a panel could ship with no fit behavior stated at all. Five instances show the cost, and each is
mapped to a rule below:

1. the `phase-wb-08` height collapse (idea `000104`): the terminal rendered a few rows tall inside a
   tall slot;
2. the File Browser clip (`REQ-007` W18): a deep tree was cut off with no scrolling;
3. the rotator tooltip cutoff (idea `000130`): the notes strip's `?` bubble is cut by the strip's
   own `overflow: hidden`;
4. the popover height floor (idea `000117`): `Popover.tsx` opens upward into a 142 px bubble while
   hundreds of pixels are free below, leaving a file selector with about two visible entries;
5. the ~98 px chrome offset: slot header, panel header and tab bar sit between the slot body and
   the content, so "content height equals slot height" fails on a correct panel.

In scope: the nine panel types registered in `ts/src/workbench/panelRegistry.tsx`, and the three
floating surfaces (popover, tooltip, file-tree context menu). Out of scope: fixing any defect the
contracts detect. `phase-wbf-06` (rotator variants), `phase-wbf-13` (popover side choice) and
`phase-wbf-14` (tooltip clipping) own the three known ones; the others are listed under "Measured
state" for the owner to schedule. Slot geometry, maximize and the Windows shells are also out of
scope; Windows shell fit is an owner-machine check (`C10`).

## How a contract is read

A contract is a list of **regions**. Each region names a CSS selector inside the panel and one or
more **modes** saying how that region may behave when its content exceeds its box. A region passes
when any one of its `or`-joined modes holds. `optional` marks a region that exists only in some
states (an xterm exists only where the shell is available); an absent optional region is counted as
not applicable and never as a pass.

| Mode | The region must |
|---|---|
| `fill` | On `:root` (the panel box): sit inside its slot body and leave no more than 24 px unfilled on either axis, which is the slot body's own padding. On any other region: be at least `min-h`/`min-w` px, stay inside the panel box, and end within 32 px of the panel's bottom edge. Measured against the panel box, never the slot body, so the chrome offset (instance 5) does not defeat it. |
| `frame` | Be an embedded document that scrolls itself: at least `min-h` px high and inside the panel box. |
| `scroll-y`, `scroll-x` | Be bounded by the panel box, have a computed overflow that scrolls on that axis, and, when its content exceeds its box, actually move when scrolled. |
| `scrollbar` | Be a virtual scrollbar track bounded by the panel box and carrying a slider. For xterm 6, whose scrollback moves through its own scrollbar while the native `.xterm-viewport` reports `overflow: scroll` and never scrolls. |
| `marquee` | Be bounded by the panel box. The declared way for text to move horizontally instead of scrolling (`phase-wbf-06`). |
| `wrap` | Hold its content within its own width, by wrapping or reflowing. |
| `truncate` | Cut text with an ellipsis: `text-overflow: ellipsis` with `white-space: nowrap`. No shipped panel declares this today; it is in the vocabulary so the first panel that truncates declares it rather than clipping. |
| `visible` | Render a box that lies wholly inside the panel box. |

Two rules apply to every panel without a row. **Page scroll:** the document is never larger than
the viewport (`REQ-006` R02). **Silent clip:** no element inside the panel may have `overflow`
hidden or clip while its content is larger than its box, unless it is inside a region declared as a
scroller, frame, marquee or truncation (or inside xterm, which manages its own surface). This is
what makes the contract complete by default: an overflow nobody declared is a finding.

Floating surfaces use their own modes. `in-viewport`: the bubble lies inside the viewport.
`dismiss-visible`: a popover's dismiss control lies inside the viewport. `not-clipped`: the bubble
lies inside every ancestor that clips its overflow. `text-fits`: a tooltip's text is not cut inside
its bubble. `not-starved`: a popover is at least as tall as the smaller of its content, 60% of the
viewport and the room on its larger side (less 2 px), so it does not open short while room exists.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| C01 | Every panel type registered in `panelRegistry.tsx` has at least one row in the panel contract table, and no row names an unregistered type. | `uv run pytest test/test_workbench_fit_contracts.py`: `test_every_registered_panel_type_has_a_contract` and `test_no_contract_row_names_an_unregistered_panel` pass. Nine types are registered on 2026-10-08. |
| C02 | A panel type registered without a contract row fails the check, and the failure names the type. | `test_undeclared_panel_fails_and_is_named` registers a fake type in a copy of the registry source and removes a real type's rows from the table, and requires `AssertionError` naming each. |
| C03 | Discovery of registered types cannot pass vacuously. The parse is cross-checked three ways: key count equals the `displayName:` count and the `Component:` count in the same block, every layout panel id is registered, and every registered id appears in a layout file (otherwise the live check could never render it). | `test_registry_discovery_cannot_pass_vacuously` and `test_registry_parser_sees_added_and_removed_types`, which add, remove and obscure a key and require the count check to trip. |
| C04 | Every panel type declares how it fills its slot: a `:root` row with mode `fill`. | `test_every_panel_declares_how_it_fills_its_slot`. |
| C05 | Each contract region is asserted in a real browser, for every layout, every registered panel type, every slot the layout makes it eligible for, at 1280x720, 1366x768, 1920x1080 and 1024x768. The run exits non-zero on any violation, on a panel never rendered, on a scroll region that was present but never given content to scroll, and on a surface kind never opened. | `uv run python test/test_workbench_fit_contracts.py --live <url>` against a running workbench. The matrix is read from `_data/workbench/layouts/*.json`; `test_live_matrix_covers_every_registered_panel_in_every_eligible_slot` asserts it. |
| C06 | A panel given content that violates its own contract fails. | `--self-test` injects CSS that breaks one region per panel (a scroller loses its overflow, a fill region collapses, a marquee or visible region is pushed out of its panel) and requires the judge to name the broken region. The judge itself is unit-tested against synthetic measurements of each of the five instances. |
| C07 | The notes strip declares vertical scroll, horizontal scroll and a bounded marquee as alternatives for a long entry, so the rotator variants of `phase-wbf-06` (`REQ-012` R12) are conformant, not violations. | `test_notes_strip_declares_vertical_and_horizontal_scroll_as_alternatives` and `test_notes_strip_marquee_variant_is_declared_and_bounded`. |
| C08 | Every selector in either table names a CSS class that exists in `ts/src`, so a renamed class fails statically rather than leaving a stale row. | `test_contract_selectors_name_classes_that_exist_in_source`. `.xterm` and `.xterm-viewport` are library classes and are exempt by name. |
| C09 | Every floating surface in `ts/src` (a component portaled into `document.body`, or a tooltip bubble) has a row in the floating surface table, and every row points at such a source. | `test_every_floating_surface_in_source_has_a_contract_row`. |
| C10 | The CMD and PowerShell panels' fit on the owner's Windows machine, where the real shells exist, is an owner check, not asserted from Linux. On a host where the shell is unavailable the panel shows its in-panel message (`REQ-007` W12) and the terminal-only regions are `optional`. | Run `--live` on the owner's machine and record the output. Linux evidence does not close this row. |

## Panel contract table

Each row is one region of one panel type. The first table under this heading is the contract the test reads.

| Panel type | Region | Selector | Mode | Basis |
|---|---|---|---|---|
| `terminal` | Panel box | `:root` | `fill` | The panel fills its slot body (`REQ-007` W15; instance 1) |
| `terminal` | Header controls | `.stage-region__header` | `wrap` | The injection dropdowns and menu reflow or wrap, never run past the panel edge |
| `terminal` | Session tabs | `.stage-terminal-tabbar` | `scroll-x optional` | Many tabs reveal by horizontal scroll (REQ-007 tab-bar rule) |
| `terminal` | Terminal screen | `.xterm` | `fill(min-h=68) optional` | Present only where the shell is available on the host |
| `terminal` | Scrollback | `.xterm .scrollbar.vertical` | `scrollbar optional` | Output longer than the screen scrolls inside the terminal. xterm 6 scrolls through its own virtual scrollbar, so the native `.xterm-viewport` is not the scroller |
| `terminal-cmd` | Panel box | `:root` | `fill` | The panel fills its slot body (`REQ-007` W15; instance 1) |
| `terminal-cmd` | Header controls | `.stage-region__header` | `wrap` | The injection dropdowns and menu reflow or wrap, never run past the panel edge |
| `terminal-cmd` | Session tabs | `.stage-terminal-tabbar` | `scroll-x optional` | Many tabs reveal by horizontal scroll (REQ-007 tab-bar rule) |
| `terminal-cmd` | Terminal screen | `.xterm` | `fill(min-h=68) optional` | Present only where the shell is available on the host |
| `terminal-cmd` | Scrollback | `.xterm .scrollbar.vertical` | `scrollbar optional` | Output longer than the screen scrolls inside the terminal. xterm 6 scrolls through its own virtual scrollbar, so the native `.xterm-viewport` is not the scroller |
| `terminal-powershell` | Panel box | `:root` | `fill` | The panel fills its slot body (`REQ-007` W15; instance 1) |
| `terminal-powershell` | Header controls | `.stage-region__header` | `wrap` | The injection dropdowns and menu reflow or wrap, never run past the panel edge |
| `terminal-powershell` | Session tabs | `.stage-terminal-tabbar` | `scroll-x optional` | Many tabs reveal by horizontal scroll (REQ-007 tab-bar rule) |
| `terminal-powershell` | Terminal screen | `.xterm` | `fill(min-h=68) optional` | Present only where the shell is available on the host |
| `terminal-powershell` | Scrollback | `.xterm .scrollbar.vertical` | `scrollbar optional` | Output longer than the screen scrolls inside the terminal. xterm 6 scrolls through its own virtual scrollbar, so the native `.xterm-viewport` is not the scroller |
| `notes-strip` | Panel box | `:root` | `fill` | The strip fills its slot body |
| `notes-strip` | Active entry | `.stage-notes-strip__current` | `scroll-y or scroll-x or marquee` | A long entry scrolls vertically (shipped) or horizontally (the rotator variant), never clips |
| `notes-strip` | Controls dropdown | `.stage-popover__trigger` | `visible` | The only control stays reachable |
| `notes-strip` | Help tooltip trigger | `.stage-tooltip__trigger` | `visible` | The `?` stays reachable |
| `html-viewer` | Panel box | `:root` | `fill` | The viewer fills its slot body |
| `html-viewer` | Header controls | `.stage-region__header` | `wrap` | Refresh, file selector, directory and mode controls reflow |
| `html-viewer` | Tabs | `.stage-html-viewer__tabbar` | `scroll-x` | Many tabs reveal by horizontal scroll |
| `html-viewer` | Page area | `.stage-html-viewer__content` | `fill(min-h=60)` | The page area is never collapsed to a sliver |
| `html-viewer` | Embedded page | `.stage-overview__iframe` | `frame(min-h=60) optional` | The embedded document scrolls itself; present once a page is chosen |
| `overview` | Panel box | `:root` | `fill` | The panel fills its slot body |
| `overview` | Header controls | `.stage-region__header` | `wrap` | Title, help and toggle reflow |
| `overview` | Embedded page | `.stage-overview__iframe` | `frame(min-h=60) optional` | The embedded document scrolls itself; present once the page is generated |
| `file-browser` | Panel box | `:root` | `fill` | The browser fills its slot body |
| `file-browser` | Header controls | `.stage-region__header` | `wrap` | Preset and directory controls reflow |
| `file-browser` | Filters | `.stage-file-browser__filters` | `wrap` | Search and type filter reflow |
| `file-browser` | Tree | `.stage-file-browser__tree` | `fill(min-h=48)` | At least two entries stay visible |
| `file-browser` | Tree | `.stage-file-browser__tree` | `scroll-y` | A deep tree scrolls inside the panel (REQ-007 W18) |
| `file-browser` | Tree | `.stage-file-browser__tree` | `scroll-x` | A long name scrolls rather than clips |
| `idea-explorer` | Panel box | `:root` | `fill` | The explorer fills its slot body |
| `idea-explorer` | Header controls | `.stage-region__header` | `wrap` | View toggle reflows |
| `idea-explorer` | Filters | `.stage-explorer__filters` | `wrap` | Search and status filter reflow |
| `idea-explorer` | Table | `.stage-explorer__table-wrap` | `fill(min-h=80)` | The header row and two entries stay visible |
| `idea-explorer` | Table | `.stage-explorer__table-wrap` | `scroll-y` | Rows beyond the box scroll inside it |
| `idea-explorer` | Table | `.stage-explorer__table-wrap` | `scroll-x` | Columns beyond the box scroll inside it |
| `backlog-explorer` | Panel box | `:root` | `fill` | The explorer fills its slot body |
| `backlog-explorer` | Header controls | `.stage-region__header` | `wrap` | View toggle reflows |
| `backlog-explorer` | Filters | `.stage-explorer__filters` | `wrap` | Search and status filter reflow |
| `backlog-explorer` | Table | `.stage-explorer__table-wrap` | `fill(min-h=80)` | The header row and two entries stay visible |
| `backlog-explorer` | Table | `.stage-explorer__table-wrap` | `scroll-y` | Rows beyond the box scroll inside it |
| `backlog-explorer` | Table | `.stage-explorer__table-wrap` | `scroll-x` | Columns beyond the box scroll inside it |

## Floating surface contract table

A floating surface is drawn outside its trigger's box and is measured only while open. Each row names the source file that creates it; `C09` fails when a source exists with no row.

| Surface | Source | Selector | Mode | Basis |
|---|---|---|---|---|
| `popover` | `ts/src/stage/Popover.tsx` | `.stage-popover__bubble` | `in-viewport` | The bubble stays on screen |
| `popover` | `ts/src/stage/Popover.tsx` | `.stage-popover__bubble` | `dismiss-visible` | The dismiss control stays on screen (`REQ-012` R25) |
| `popover` | `ts/src/stage/Popover.tsx` | `.stage-popover__bubble` | `not-starved` | Opens at the height its content and the larger side allow, within 15% (idea `000117`, `phase-wbf-13`; instance 4) |
| `tooltip` | `ts/src/stage/Tooltip.tsx` | `.stage-tooltip__bubble` | `in-viewport` | On screen |
| `tooltip` | `ts/src/stage/Tooltip.tsx` | `.stage-tooltip__bubble` | `not-clipped` | Not cut by an overflow-hidden ancestor (idea `000130`, `phase-wbf-14`; instance 3) |
| `tooltip` | `ts/src/stage/Tooltip.tsx` | `.stage-tooltip__bubble` | `text-fits` | The whole tooltip text is visible (`REQ-012` R27) |
| `context-menu` | `ts/src/stage/FileTreeContextMenu.tsx` | `.stage-file-tree-menu` | `in-viewport` | On screen |

## The five known instances

| # | Instance | Rule that makes it detectable | Judge test (synthetic measurement) | Live result, 2026-10-08 |
|---|---|---|---|---|
| 1 | `phase-wb-08` height collapse (`000104`) | `:root` `fill` on every panel; `.xterm` `fill(min-h=68)` | `test_judge_flags_a_height_collapse` | Not reproduced. Every panel box filled its slot body in all 100 cells, and the xterm met its floor. |
| 2 | File Browser clip (`REQ-007` W18) | `.stage-file-browser__tree` `scroll-y`, `scroll-x`, `fill(min-h=48)` | `test_judge_flags_the_file_browser_clip_w18` | Not reproduced. The tree scrolls inside its box in all 8 cells, and its content exceeded the box in each, so the rule was exercised. |
| 3 | Rotator tooltip cutoff (`000130`, `phase-wbf-14`) | tooltip `not-clipped` | `test_tooltip_judge_flags_the_rotator_cutoff_000130` | **Reproduced** in layout 1 at all four sizes: the 240x113 bubble is cut by the 28-32 px notes strip. Layout 2's strip is 220-350 px high and does not clip it. |
| 4 | Popover height floor (`000117`, `phase-wbf-13`) | popover `not-starved`, `in-viewport`, `dismiss-visible` | `test_popover_judge_flags_the_height_floor_000117` | **Reproduced** in layout 1 at all four sizes: the HTML Viewer file selector, given a directory of 140 files, opens a 149-191 px bubble when it needs 305 px and 529-846 px is free on the larger side. The dismiss control and viewport rules held. |
| 5 | The ~98 px chrome offset | every non-root `fill` is anchored on the panel box, not the slot body | `test_chrome_offset_does_not_make_a_correct_panel_fail` | By construction. The fixture carries a 98 px gap between slot body and xterm and conforms; a slot-height proxy would fail it. |

## How panel types are discovered

`PANEL_REGISTRY` in `ts/src/workbench/panelRegistry.tsx` is the one registration point, so the test
parses that object literal as source text rather than relying on a generated manifest. A manifest
would be a second list that could drift from the first, and a build step the test would have to
trust. The parse takes the keys that open at the literal's own indent. It cannot silently find
nothing or the wrong things, because `C03` makes the test fail unless three independent counts
agree (keys, `displayName:` entries and `Component:` entries in the same block), every panel id in
the layout files is registered, and every registered id appears in a layout. The last condition
matters for the live half: a type no layout places can never be rendered, so it could never be
measured. The test also proves the parser itself by adding, removing and obscuring a key in a copy
of the source.

Floating surfaces are discovered the same way, by scanning `ts/src` for a `createPortal(...)` into
`document.body` or a `role="tooltip"` bubble, and require a row in the second table.

## Running the live check

Start the backend and the Vite dev server on ports of your own (never 8000 or 5173), both with
`D_SYSTEM_DEMO_TERMINAL=1` so the workbench routes and the file route exist, and with
`VITE_API_TARGET` pointing the dev server at the backend. Then:

```bash
uv run python test/test_workbench_fit_contracts.py --live http://localhost:<vite-port> --self-test
```

`--quick` keeps 1280x720 and 1024x768 only, `--layout` and `--panel` narrow the matrix, and
`--dump <path>` writes the raw measurements. The full matrix takes about eight minutes. It needs
Node and Playwright for Node (found in `ts/node_modules`, in the global `npm root`, or at the path
in `FIT_PLAYWRIGHT_MODULE`) and a Chromium that Playwright can launch. The tracked directory
`_public/engine/trace` must hold more than twenty `.html` or `.svg` files: it is seeded into the
HTML Viewer so its file selector popover has a long list, and `test_stress_directory_gives_the_file_selector_a_long_list` fails if it stops doing so.

## Measured state, 2026-10-08

Run against the stock workbench (`uv run python test/test_workbench_fit_contracts.py --live <url>
--self-test`): 100 panel cells (2 layouts, 9 panel types, every eligible slot, 4 sizes), 132
floating-surface measurements (108 popovers, 16 tooltips, 8 context menus). Rules passed 489 and
failed 35. The run exits 1. Instances 3 and 4 above are the two floating-surface violations, and the
notes strip's unbounded entry is the defect `phase-wbf-06` addresses. The other four rows below match
no queued phase's title or scope in `backlog.yaml`, so they are listed for the owner to schedule
rather than fixed here. `phase-wbf-02` will add a last-modified badge to the HTML Viewer header,
which the header's `wrap` row will measure.

| Finding | Where | Measured |
|---|---|---|
| Notes strip entry is not bounded by its panel (`scroll-y or scroll-x or marquee`) | layout 1, all four sizes | The 4-line default entry is 71-106 px high in a strip 28-57 px high, so the strip's `overflow: hidden` cuts it. The entry declares `overflow-y: auto` but is not height-limited, so it never scrolls. This is the defect `phase-wbf-06` addresses; the contract already accepts its horizontal variant. |
| Notes strip controls dropdown partly outside the strip (`visible`) | layout 1, 1280x720, 1366x768, 1024x768 | The 26x27 px trigger overruns the strip's bottom edge by 1-6 px. |
| Terminal header does not wrap (`wrap`) | `terminal` in the primary slot: layout 1 at 1280x720 and 1024x768, layout 2 at 1280x720 and 1024x768; `terminal-cmd` the same; `terminal-powershell` also at 1366x768 | The header's injection controls are 410 px wide (437 px for PowerShell) in a 393 px box, down to 307 px, and are cut off. |
| HTML Viewer header does not wrap (`wrap`) | layout 2, primary slot, 1024x768 | 377 px of controls in a 307 px box. |
| File Browser header does not wrap (`wrap`) | layout 2, explorer slot, 1024x768 | 349 px of controls in a 307 px box. |

Each `wrap` finding is accompanied by a `silent-clip` finding on the panel root, which is the same
defect seen from the other side: the root's `overflow: hidden` is hiding the controls.

Not exercised, and said so rather than counted as a pass: the CMD and PowerShell scrollback.
`terminal-cmd` and `terminal-powershell` mount an xterm that shows "is not available on this host"
on Linux, so no output exists to scroll. The run reports both by name; the owner's Windows machine
closes them (`C10`).

The self-test injected one violation into each of the nine panel types' own contracts at 1280x720,
and the judge named the broken region in every case: the three terminals' tab bar and the HTML
Viewer tab bar given `overflow: hidden`, the notes strip entry and the overview frame moved out of
their panels, and the File Browser tree and both explorer tables collapsed to 12 px. The overview
exists only in layout 2, so it was broken there and the other eight in layout 1.

## Boundaries and unresolved

**The live half is not part of `uv run pytest`.** It needs a running workbench, Chromium and Node
Playwright, none of which the Python dependencies provide. A pytest test that passed when they were
absent would be the vacuous pass `R10` forbids, and one that failed would break the suite on any
machine without a browser. Running it from pytest would need Playwright added to the dev
dependencies and a fixture that starts both servers; both are outside this phase's declared files,
so that choice is the owner's. Until then, `C05` and `C06` are verified by the command in each row,
and `C01` to `C04` and `C07` to `C09` by `uv run pytest`.

**The live run exits non-zero today.** The defects above are real, so the command cannot gate
anything until `phase-wbf-06`, `phase-wbf-13`, `phase-wbf-14` and the header-wrap findings are fixed.
Each fixing phase should rerun it and amend this document in the same change: when `phase-wbf-06`
lands it should name the moving element in the notes strip row if it is not
`.stage-notes-strip__current`, and a marquee that translates its content must stay bounded by the
strip to conform.

**The numeric floors are judgments.** `min-h=48` for the File Browser tree (two entries), `80` for
an explorer table (header row and two entries), `68` for the xterm (four rows) and `60` for the
HTML Viewer page area and frames were set below what the shipped layouts achieve (the smallest
measured heights were 57 for the tree, 93 for the tables, 84 for the xterm, 83 for the viewer's page
area and frame, and 150 for the overview frame) and from how little content makes a region usable.
They are the owner's to tighten. The 24 px and 32 px fill tolerances are the measured slot-body padding and a
chrome allowance; the 15% starvation tolerance is described in the test's constants.

**Nothing is fixed here.** The contracts make `phase-wbf-13` and `phase-wbf-14` verifiable by command;
they do not change `Popover.tsx` or `Tooltip.tsx`.
