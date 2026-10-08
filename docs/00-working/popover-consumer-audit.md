# Popover consumer audit (phase-wbf-13)

Measured on 2026-10-08 against `ts/src/stage/Popover.tsx` before and after the placement change
(`REQ-012` R25 and R26; the file selector defect is idea 000108, the shared-floor warning is idea
000117). Method: `python test/test_workbench_fit_contracts.py --live http://localhost:5190 --quick
--panel html-viewer --dump <file>` against the stock layouts `layout-1` and `layout-2` with the HTML
Viewer pointed at `_public/engine/trace` (140 compatible files). The command opens every enabled
popover trigger on the page at 1280x720 and 1024x768 and records the bubble box.

Consumers found by `grep -rl "from '.*Popover'" ts/src`: nine consumers (the new test file also matches the grep).

Bubble height in px, written `1280x720 / 1024x768`; `a -> b` means before -> after the change, a
single number means unchanged.

| Consumer (trigger label) | layout-1 | layout-2 | Outcome |
|---|---|---|---|
| `HtmlViewerRegion` ("Choose a file") | 149 -> 432 / 153 -> 461 | 307 -> 432 / 307 -> 461 | Fixed by the shared change plus the list cap removal in `StagePage.css`. Scrolls inside to the last of 140 entries with a real mouse wheel; dismiss control on screen. |
| `DirectoryPickerDialog` ("Change directory...", HTML Viewer) | 138 / 138 | 138 / 138 | Content fully shown; unchanged. |
| `DirectoryPickerDialog` ("Change directory...", File Browser) | 304 / 304 | 304 / 304 | Content fully shown; unchanged. |
| `LayoutConfigDialog` ("Configure layout") | 389 / 389 | 431 / 431 | Content fully shown; opens downward as before. |
| `Slot` ("Terminal (bash)" chooser) | 109 / 109 | 109 / 109 | Content fully shown; unchanged. |
| `Slot` ("HTML Viewer" chooser) | not in layout | 77 / 77 | Content fully shown; unchanged. |
| `Slot` ("File Browser" chooser) | 109 / 109 | 109 / 109 | Content fully shown; unchanged. |
| `CommandPanel` ("Commands (4)") | 229 / 229 | 229 / 229 | Content fully shown; unchanged. |
| `InjectionDropdowns` ("Skills (11)") | 397 / 397 | 360 -> 352 / 379 -> 371 | layout-1 content fully shown. layout-2: content needs 395 px and 352 to 371 px is the room on the larger side, so the last entries scroll inside the bubble. Cannot be larger; the viewport has no more room on either side. |
| `InjectionDropdowns` ("Prompts (43)") | 432 / 461 | 360 -> 352 / 379 -> 371 | Content needs 1909 px; scrolls inside the bubble at the 60% cap (layout-1) or the room above (layout-2). Unchanged. |
| `InjectionDropdowns` ("Agents (16)") | 432 / 461 | 360 -> 352 / 379 -> 371 | Content needs 555 px; scrolls inside as above. Unchanged. |
| `TerminalMenu` ("...") | 111 / 111 | 111 / 111 | Content fully shown; unchanged. |
| `TerminalRegion` (close session "x") | 128 / 128 | 128 / 128 | Content fully shown; unchanged. |
| `NotesStripRegion` ("v", notes controls) | 164 / 164 | 164 / 164 | Content fully shown; unchanged. |

In layout-2 the three dropdown lists lose 8 px to the second viewport margin (a bubble limited by
the room now ends 8 px above the viewport edge instead of touching it).

Scrolling bodies (Prompts, Agents, layout-2 Skills, the file list) keep their scroll position while
being scrolled: the shared component no longer remeasures on a scroll inside the bubble.

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
