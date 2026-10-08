---
schema_version: 1
id: doc-session-tooltip-bottom-clip
code: SESS-2026-10-08-18
title: Stop the notes strip tooltip being cut off at the panel bottom (phase-wbf-14)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-shared, sys-wb-styles]
depends_on: [doc-workbench-features-defects-requirements]
---

# Stop the notes strip tooltip being cut off at the panel bottom (phase-wbf-14)

## Phase

`phase-wbf-14` (stop the notes strip tooltip being cut off at the panel bottom), group of
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md). Batch runner
(`agent-batch-runner`) under the Session Manager's pre-approved run of 2026-10-08. Branch
`agent/phase-wbf-14`, cut from the run's integration branch `ccr-b69b05b4-tdcrux`. Idea `000130`
(the rotator help tooltip is cut off at the bottom of its panel). The session code is the one the
Session Manager assigned; `--next-code session` in this worktree returned 17.

## Measurement before the change

The idea guessed the cause was the shared popover. It is not: the `?` is `Tooltip.tsx`, whose bubble
was `position: absolute; top: 130%` inside `.stage-region`, which sets `overflow: hidden`. Measured
with `test/test_workbench_fit_contracts.py --live http://localhost:5200 --quick` on this branch
before any edit (the tooltip `not-clipped` findings; the other 30 findings in that run belong to
other phases):

```
layout-1/tooltip 'tooltip About the notes strip' 1280x720: not-clipped: bubble box 240x113 at (760,106), bottom 219, right 1000 is cut by ancestor section.stage-region.stage-notes-strip box 521x28 at (750,81), bottom 109, right 1271
layout-1/tooltip 'tooltip About the notes strip' 1024x768: not-clipped: bubble box 240x113 at (611,109), bottom 222, right 851 is cut by ancestor section.stage-region.stage-notes-strip box 415x32 at (600,81), bottom 114, right 1015
```

The bubble's bottom (219 and 222) is about 110 px below the strip's bottom (109 and 114), so
nearly all of it was clipped. Total before: 32 findings.

## Outcome

`ts/src/stage/Tooltip.tsx`: the bubble is rendered through `createPortal` into `document.body`, as
`Popover.tsx` does. `reposition()` reads the trigger's live bounding box, measures the bubble's
width and natural height (with `maxHeight` lifted for the measurement), chooses the side and height
with `choosePlacement` imported from `Popover.tsx`, and clamps the left edge to the viewport with the
same 8 px margin. It runs on open and on window resize and scroll while open. Hover and focus open it;
pointer leave and blur close it (REQ-006 R03). The portaled bubble remains a React descendant of the
wrapper, so React's mouseenter/mouseleave treat moving from the trigger onto the bubble as staying
inside. The class names `stage-tooltip__bubble` and `role="tooltip"` are unchanged, which the fit
check and the contract's floating-surface scan rely on.

`ts/src/stage/StagePage.css`: `.stage-tooltip__bubble` is `position: fixed`, `z-index: 1000`
(matching the popover) and `overflow-y: auto`, so text stays reachable by scrolling in the bubble
when the viewport leaves less room than the text needs. The notes strip's font size and text
capacity are unchanged.

`ts/src/stage/Tooltip.test.tsx` (new): 11 tests with the trigger's box and the bubble's size mocked.
Placement: the bubble is a child of `document.body` and not of `.stage-region`; opens below a trigger
near the top; opens above one near the bottom; shifts left to keep its right edge inside the
viewport; keeps off the left edge; limits its height to the room when the text is taller; places
again on resize. Collapse: closed by default; opens on enter and closes on leave; stays open while
the pointer is over the bubble and closes on leaving it; opens on focus and closes on blur.

## Evidence

Fit check after the change, same command: tooltip `not-clipped` findings gone, total 32 to 30,
tooltips measured 8, floating surfaces unchanged (`popover` 54, `context-menu` 4).

Playwright hover on every tooltip trigger present (notes strip, terminal, overview) at 1280x720 and
1024x768, layout-1, layout-2 and layout-2 with the overview panel in the main slot: 14 triggers, all
with the bubble box inside the viewport, scroll width and height equal to client width and height
(text fully visible), the bubble still open with the pointer over it, gone after the pointer moved
to (2, 2), and document scroll extents zero (REQ-006 R02). The notes strip bubble is now at
(760,114)-(1000,211) at 1280x720 in layout-1. The script is not committed (a scratch file).

## Unresolved

- The overview panel is only reachable in layout-2's main slot, and the fit check does not assign it
  there, so its tooltip is covered by the Playwright run above and not by the fit check's cells.
- The idea also asks whether the notes strip's font size and text capacity should be reconsidered.
  That is a design decision for the owner and is not changed here. `phase-wbf-06` changes how the
  strip handles long entries on a sibling branch. Open question for the owner: after `phase-wbf-06`
  merges, is the strip's size acceptable?
- `test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused` fails in this
  environment because the run is root (idea `000604`). Recorded, not retried or skipped.

## Assumptions and ratification

- I used `choosePlacement` from `Popover.tsx` unchanged, which prefers the upward side when the whole
  text fits there. A tooltip near the bottom of the viewport therefore opens above its trigger. No
  existing row says which side a tooltip should prefer. Awaiting the owner's confirmation if a
  below-first preference is wanted.
- `Tooltip.tsx` now imports from `Popover.tsx`, so the two share one placement rule.
