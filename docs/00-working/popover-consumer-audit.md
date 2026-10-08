# Popover consumer audit (phase-wbf-13)

Measured on 2026-10-08 against `ts/src/stage/Popover.tsx` before and after the placement change
(`REQ-012` R25 and R26; the file selector defect is idea 000108, the shared-floor warning is idea
000117). Method: `python test/test_workbench_fit_contracts.py --live http://localhost:5190 --quick
--panel html-viewer --dump <file>` against the stock layouts `layout-1` and `layout-2` with the HTML
Viewer pointed at `_public/engine/trace` (140 compatible files). The command opens every enabled
popover trigger on the page at 1280x720 and 1024x768 and records the bubble box. Only the 1280x720
column is listed here; 1024x768 differs by a few pixels where the cap (60% of the viewport) applies.

Consumers found by `grep -rl "from '.*Popover'" ts/src`: nine, the nine the phase names.

| Consumer (trigger label) | layout-1: before -> after | layout-2: before -> after | Outcome |
|---|---|---|---|
| `HtmlViewerRegion` ("Choose a file") | 149 px, opened upward at y=0, 2 entries -> 432 px, opened downward, 12 entries | 307 px, 7 entries -> 432 px, 12 entries | Fixed by the shared change plus the list cap removal in `StagePage.css`. Scrolls inside to the last of 140 entries; dismiss control on screen. |
| `DirectoryPickerDialog` ("Change directory...", HTML Viewer) | 138 px -> 138 px (up) | 138 px -> 138 px (down) | Content fully shown; unchanged. |
| `DirectoryPickerDialog` ("Change directory...", File Browser) | 304 px -> 304 px (up) | 304 px -> 304 px (down) | Content fully shown; unchanged. |
| `LayoutConfigDialog` ("Configure layout") | 389 px -> 389 px | 431 px -> 431 px | Content fully shown; opens downward as before. |
| `Slot` ("Terminal (bash)", "HTML Viewer", "File Browser" panel choosers) | 109 px -> 109 px | 77 to 109 px -> same | Content fully shown; unchanged. |
| `CommandPanel` ("Commands (4)") | 229 px -> 229 px | 229 px -> 229 px | Content fully shown; unchanged. |
| `InjectionDropdowns` ("Skills (11)") | 397 px -> 397 px | 360 px -> 360 px | layout-1 content fully shown. layout-2: content needs 395 px and 360 px is the room on the larger side, so the last entries scroll inside the bubble. Cannot be larger; the viewport has no more room on either side. |
| `InjectionDropdowns` ("Prompts (43)", "Agents (16)") | 432 px -> 432 px | 360 px -> 360 px | Content needs 555 to 1909 px; scrolls inside the bubble at the 60% cap (layout-1) or the room above (layout-2). |
| `TerminalMenu` ("...") | 111 px -> 111 px | 111 px -> 111 px | Content fully shown; unchanged. |
| `TerminalRegion` (close session "x") | 128 px -> 128 px | 128 px -> 128 px | Content fully shown; unchanged. |
| `NotesStripRegion` ("v", notes controls) | 164 px -> 164 px | 164 px -> 164 px | Content fully shown; unchanged. |

## Baseline of the defect, from the file selector measurement

Fully visible `.stage-html-viewer__file-option` elements with the popup open (before -> after):

| Layout | 1280x720 | 1024x768 |
|---|---|---|
| layout-1 | 2 -> 12 | 2 -> 13 |
| layout-2 | 7 -> 12 | 7 -> 13 |

Before, layout-1 opened upward into 149 to 153 px because the space above (149 px) reached the 120
px threshold, although 529 to 558 px were free below. layout-2 opened downward (101 px above, under
the threshold) but the list's own 14rem cap held it to seven entries.

## Findings that are not the shared component's

- `layout-2` at 1024x768: the HTML Viewer panel header content is 377 px wide in a 307 px box
  (`wrap` and `silent-clip` findings from the live check). This is the region header, not the
  popover, and is unchanged by this phase.
- The notes strip tooltip is cut by its region (`not-clipped` finding). That is `Tooltip.tsx`,
  owned by phase-wbf-14.
