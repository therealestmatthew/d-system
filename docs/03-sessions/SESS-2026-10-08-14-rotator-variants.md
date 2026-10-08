---
schema_version: 1
id: doc-session-rotator-variants
code: SESS-2026-10-08-14
title: Rotator variants - scrolling text and image entries (phase-wbf-06)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-ui]
depends_on: [doc-workbench-features-defects-requirements]
---

# Rotator variants - scrolling text and image entries (phase-wbf-06)

## Phase

`phase-wbf-06` (rotator variants: horizontally scrolling text and image entries), group `G50` of
[`PLAN-027`](../01-plans/PLAN-027-workbench-features-defects.md). Standby Builder (`agent-standby`)
under the Session Manager's pre-approved run of 2026-10-08. Branch `agent/phase-wbf-06`, cut from the
run's integration branch `ccr-b69b05b4-tdcrux`.

## Outcome

The notes strip (`ts/src/stage/NotesStripRegion.tsx`) now rotates one list of entries that is a union
of two kinds, and a long text entry no longer clips. The single-click and dropdown behaviour is
unchanged (the same controls, the same picker, the same persisted file choice).

- **Entry model.** `NotesEntry` is `text` or `image`. A notes file carries `points` (text, as before)
  or `imageDirectory` (a repository-relative directory), parsed by `parseNotesFile`. Image entries are
  the files of that directory, listed through the workbench listing route and served through Vite's
  `/workbench-file/` route, so image rotation needs `D_SYSTEM_DEMO_TERMINAL=1` on both servers. This
  follows `PLAN-027` decision 5: images come from a directory, with no edge to the bookmark phases.
- **Variant selection (R12).** A text entry is shown wrapped, as today, when that fits the entry box.
  When it does not, it becomes one line (line breaks become `  ·  `) that scrolls right to left: hold
  1 s, travel at 60 px/s until the line's end is in view, hold 1 s, repeat. The motion is a
  transform animation on the line, so the entry box is never taller than the strip and nothing is cut
  off for a reader who waits. A line that fits the box when flattened does not move.
- **Pause (R12).** Hovering over the entry or giving it keyboard focus pauses the scroll; leaving or
  blurring resumes it. The entry is a tab stop only while it scrolls. With reduced motion requested
  nothing animates and the box scrolls horizontally by hand.
- **Rotation within and between entries (R13).** The timed advance moves on only when the entry has
  been shown for the full 6 s interval, its scroll has finished one pass, and the pointer and focus
  are not on it. With the timed advance on, a scrolling entry plays one pass; with it off, it
  repeats. The dropdown's Previous and Next apply at once. The rule is written on the component's
  doc comment and in `advanceIfDue`.
- **Image sizing (R14).** An image fills the entry box (the strip's height less its padding, and the
  width between the `?` and the dropdown), scaled to sit entirely inside it with its proportions kept
  (`object-fit: contain`): letterboxed, never cropped, stretched or overflowing. An image that fails
  to load shows its name instead.
- **Mixing ruling (R14).** One rotation is all text or all images. A file that lists `points` and
  names an `imageDirectory` is rejected with a message, before the directory is read. Reasons: it is
  the reversible choice (allowing mixing later relaxes a check; allowing it now and forbidding it
  later would orphan files authors had written), and mixing needs a rule nobody has stated, namely
  where the directory's images fall among the points.

## Decisions awaiting ratification

**All proposed; awaiting the owner's ratification (pre-approved run, 2026-10-08).**

1. The mixing ruling above (no mixing).
2. The image sizing rule above (`contain` in the entry box, scaled up as well as down).
3. The pause interaction (hover or keyboard focus on the entry) and the rotation rule above.
4. The notes-file shape: `imageDirectory` as an optional key beside `points`. Nothing else in the
   file format changed.

## Assumptions

- Plain text means "wrapped, as today", so a four-line entry in layout 2's tall strip is still shown
  wrapped; only an entry that does not fit becomes the scrolling line.
- Scroll speed (60 px/s) and the 1 s end holds are my choice. The owner has not ruled on them.
- The font-size half of idea `000130` (and `000613`) has no ruling and was not decided here. The
  strip's font size and line height are unchanged.
- `minHeight: 1.4em` on the entry box (an inline style, because the stylesheet is outside the
  deliverable) keeps one line, or a small image, at 18 px in layout 1's 13 px padded row. Without it
  `REQ-037` reports the entry as collapsed (below its 16 px floor).

## Evidence

- Fit contract before (`python test/test_workbench_fit_contracts.py --live http://localhost:5191
  --quick --panel notes-strip`, API 8021, Vite 5191): `rules pass=12 fail=6 ... 10 finding(s)`, with
  the active entry reported as `box 441x71 ... not bounded by its panel`.
- Fit contract after: `rules pass=14 fail=4 ... 8 finding(s)`. The active-entry row is clean in both
  sizes; the notes-strip findings left are the dropdown trigger overrunning the strip (`000628`,
  not fixed here, as instructed), the strip's own `silent-clip`, which comes from that same trigger
  (`scroll 519x33 in a 519x26 box`; the trigger is the only content that low), and the tooltip and
  file-picker bubbles (`phase-wbf-14` and `000117`).
- Playwright check on ports 8021 / 5191 (a scratch script, not committed; the notes file and the
  strip's contents were served per scenario by intercepting `/talking-points.json`): 20 checks, all
  pass. A long entry becomes the ticker, no vertical clip (`sh=18 ch=18`), zero page scroll
  (`1280x720` in `1280x720`), the transform moves between samples and is negative (right to left);
  hover pauses and leaving resumes; focus pauses and blur resumes; the scroll repeats with the timed
  advance off; a short entry stays plain; a four-line entry stays wrapped in layout 2. Rotation with
  the timed advance on, entries short / long / short: changes at 0 s, 6.0 s, 15.4 s, 21.5 s, so the
  long entry (travel 441 px, pass 9.35 s) was kept until its pass ended, not rotated at 6 s; a
  hovered entry was not rotated for 8 s and rotated once released. Images from `_public/images`
  (six SVGs): the first loads at `437x18` in layout 1 and `329x205` in layout 2, inside its box and
  the strip, `object-fit: contain`, rotating through three on the 6 s cadence. A mixed file shows
  the rejection message. Reduced motion shows no animation and `overflow-x: auto`.
- `cd ts && npm run build`: `built in 2.79s`. `uv run python -m src.governance`: `Governance OK: 45
  systems, 468 documents, 37 memories, 354 backlog phases`.
- Vitest, `ts/src/stage/NotesStripRegion.test.tsx` (21 tests): the entry model through the rendered
  component, variant selection against stubbed measurements, hover and focus pause, the four R13
  conditions with fake timers, image listing and sizing, the mixing ruling, the unavailable and empty
  directory messages. Removing the scroll condition or the hold condition from `advanceIfDue` makes
  one test fail each, checked by hand. `cd ts && npm test`: `Test Files 9 passed (9)`, `Tests 110
  passed (110)`.
- Gates: `uv run pytest`: `1 failed, 1901 passed, 1 skipped`; the failure is
  `test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`, which expects a
  permission error that root does not get (environmental, the same one recorded for `phase-wbf-07`).
  `uv run ruff check src/ test/ tools/`: `All checks passed!`. `uv run mypy src/`: `Success: no issues
  found in 51 source files`. `cd ts && npm run lint`: no output (clean).

## Unresolved

- `ts/src/stage/NotesStripRegion.test.tsx` is outside the declared deliverable
  (`ts/src/stage/NotesStripRegion.tsx` only). The deliverable needs widening by that file, which the
  Session Manager applies on the trunk at completion. The ESLint rule `react-refresh/only-export-components`
  forbids exporting the pure entry-model functions from the component file, so the test goes through
  the component.
- `REQ-037`'s live-run paragraph says phase-wbf-06 should name the moving element in the notes strip
  row if it is not `.stage-notes-strip__current`. It is that element's inner line (`[data-notes-part="track"]`),
  and the row's selector is unchanged, so no amendment to the row is needed; the paragraph's "unbounded
  entry" defect is fixed and could be struck. `REQ-037` is outside this phase's deliverables.
- In layout 1 the strip's padded row is 13 px, so an image there is an 18 px thumbnail. The rule works
  at any strip height (329x205 in layout 2); the strip's height is the limit. That is the geometry
  question of idea `000133`, not decided here.
- A running ticker needs `Element.animate`; without it (an old browser) a long entry would be cut,
  not scrolled. Every browser the demo uses has it.
