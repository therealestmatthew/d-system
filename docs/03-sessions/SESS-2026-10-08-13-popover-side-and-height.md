---
schema_version: 1
id: doc-session-popover-side-and-height
code: SESS-2026-10-08-13
title: Popovers open toward the side with room (phase-wbf-13)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-shared, sys-wb-styles]
depends_on: [doc-workbench-features-defects-requirements]
---

# Popovers open toward the side with room (phase-wbf-13)

## Phase

`phase-wbf-13` (open popovers toward the side with room so the file selector shows its list),
built by `agent-builder-b` under the Session Manager, 2026-10-08, in
`/home/user/d-system-worktrees/phase-wbf-13` on `agent/phase-wbf-13`, cut from the run's integration
branch `ccr-b69b05b4-tdcrux` (standing in for `dev`). Dev servers on API port 8020 and Vite port
5190, both stopped at the end.

## Baseline (measured before any edit)

`python test/test_workbench_fit_contracts.py --live http://localhost:5190 --quick --panel
html-viewer` reproduced the defect: "bubble is 149px high but its content needs 305px, 529px of room
exists on the larger side" (layout-1, 1280x720) and 153 px at 1024x768. Counting fully visible
`.stage-html-viewer__file-option` elements with the HTML Viewer on `_public/engine/trace` (140
files): layout-1 2 entries at both sizes (opened upward into 149 to 153 px), layout-2 7 entries at
both sizes (opened downward, held by the list's own 14rem cap).

## What changed

- `ts/src/stage/Popover.tsx`: new exported `choosePlacement` chooses the side from the room each
  side has for the content (upward kept when the whole content fits there, then downward when it
  fits there, otherwise the larger side; unmeasured content uses the larger side). The height is the
  room on the chosen side up to 60% of the viewport and never more than the room, replacing the
  fixed 120 px floor. The content height is measured on the live bubble with `maxHeight` lifted and
  restored in the same call.
- `ts/src/stage/StagePage.css`: removed the 14rem `max-height` on `.stage-html-viewer__file-list`
  (the measurement showed it limited layout-2 to seven entries), so the popover body is the one
  scroller; the filter box is sticky at the top of that scroller.
- `ts/src/stage/Popover.test.tsx` (new, 12 tests): the side choice, the height clamp, and the
  placement reaching the bubble's inline style in the DOM.
- `docs/00-working/popover-consumer-audit.md` (new): nine consumers by grep, each with its measured
  bubble height at 1280x720 in both layouts before and after, and an outcome (`REQ-012` R26).

## Evidence

- Fully visible file entries after the change: layout-1 12 (1280x720) and 13 (1024x768); layout-2
  12 and 13. Scrolling to the end reaches entry 140; the dismiss control is on screen in all four
  cells.
- The same live command after the change: no popover finding remains. Four findings remain, none from
  the popover: two `tooltip` `not-clipped` findings (phase-wbf-14) and the `wrap` and `silent-clip`
  findings on the HTML Viewer header in layout-2 at 1024x768 (not in this phase's scope).
- `cd ts && npm test`: 96 passed. `npm run build`: built. `npm run lint`: clean.
- `uv run python -m src.governance`: OK. `uv run ruff check src/ test/ tools/`: clean.
  `uv run mypy src/`: no issues in 51 files.
- `uv run pytest`: 1899 passed, 1 skipped, 1 failed when run whole:
  `test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`. It chmods a
  directory to 0o500 and expects a refusal; this sandbox runs as root (uid 0), for which the mode does
  not block creation. It is unrelated to this phase and was run deselected for the rest of the suite
  (1899 passed). Not skipped or edited.

## Unresolved and assumptions

- `choosePlacement` is exported from `Popover.tsx` with an `eslint-disable-next-line
  react-refresh/only-export-components`, because the phase's deliverables name no separate module.
  A `popoverPlacement.ts` would remove the disable; this needs the reviewer's decision.
- Assumption: the upward side stays preferred when the whole content fits there, to keep the
  trigger-near-bottom behaviour of existing consumers. Measured: no other consumer's height changed.
- Layout-2 "Skills (11)" needs 395 px and 360 px is the larger room, so its last entries scroll. Not a
  shared-component fault.
- No decision here awaits ratification.
