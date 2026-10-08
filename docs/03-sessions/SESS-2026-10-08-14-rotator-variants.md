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
  are not on it. With the timed advance on (and more than one entry to rotate to), a scrolling entry plays one
  pass; otherwise it repeats. The dropdown's Previous and Next apply at once. The rule is written on the component's
  doc comment and in `advanceIfDue`.
- **Image sizing (R14).** Image entries are meant for a strip at least 100 px tall (N = 100, a
  judgement from what was measured: 205 px in layout 2, 18 px in layout 1; the owner may change it).
  An image fills the entry box (the strip's height less its padding, and the
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
- The 100 px figure for image strips is mine, from the two heights measured; the owner has not ruled.
- `minHeight: 1.4em` on the entry box (an inline style, because the stylesheet is outside the
  deliverable) keeps one line, or a small image, at 18 px in layout 1's 13 px padded row. Without it
  `REQ-037` reports the entry as collapsed (below its 16 px floor).

## Evidence

- Fit contract before (`python test/test_workbench_fit_contracts.py --live http://localhost:5191
  --quick --panel notes-strip`, API 8021, Vite 5191): `rules pass=12 fail=6 ... 10 finding(s)`, with
  the active entry reported as `box 441x71 ... not bounded by its panel`.
- Fit contract after (also rerun after the fix round, same result): `rules pass=14 fail=4 ...
  8 finding(s)`, exit 1. The active-entry row is clean in both sizes. The four finding kinds left
  are not this phase's, and each has an owner:
  1. dropdown trigger partly outside the strip (`box 26x27 ... bottom 115` vs panel bottom 109):
     idea `000628`, not fixed here as instructed;
  2. `silent-clip` on `section.stage-notes-strip` (`scroll 519x33 in a 519x26 box`): follows from the
     trigger (the trigger is the only content that low), so it clears with `000628`;
  3. the help tooltip cut by the strip (`bubble box 240x113`): idea `000130`, `phase-wbf-14`;
  4. the HTML Viewer file-selector popover `not-starved` (`bubble is 149px high but its content
     needs 305px`): idea `000117`, `phase-wbf-13`.
  `REQ-037` is not amended (outside this phase's deliverables); the moving element is the line
  inside `.stage-notes-strip__current`, `[data-notes-part="track"]`, and amending the notes-strip row
  to name it is requested as an idea in the hand-off.
- Playwright check on ports 8021 / 5191 (a scratch script, not committed; the notes file and the
  strip's contents were served per scenario by intercepting `/talking-points.json`): 21 results, all
  pass (rerun after the fix round). A long entry becomes the ticker, no vertical clip (`sh=18 ch=18`), zero page scroll
  (`1280x720` in `1280x720`), the transform moves between samples and is negative (right to left);
  hover pauses and leaving resumes; focus pauses and blur resumes; the scroll repeats with the timed
  advance off; a short entry stays plain; a four-line entry stays wrapped in layout 2. Rotation with
  the timed advance on, entries short / long / short: changes at 0 s, 6.0 s, 15.4 s, 21.5 s, so the
  long entry (travel 441 px, pass 9.35 s) was kept until its pass ended, not rotated at 6 s; a
  hovered entry was not rotated for 8 s and rotated once released. Images from `_public/images`
  (six SVGs): the first loads at `437x18` in layout 1 and `329x205` in layout 2, inside its box and
  the strip, `object-fit: contain`, rotating through three on the 6 s cadence. A mixed file shows
  the rejection message. A lone long entry kept looping after timed advance was switched on for a longer file (still
  running after 11 s, repeating). Reduced motion, run with classic scrollbars shown, shows no
  animation, `overflow-x: auto`, and an 18 px box with no scrollbar height (`offsetHeight` 18,
  `clientHeight` 18).
- `cd ts && npm run build`: `built in 2.79s`. `uv run python -m src.governance`: `Governance OK: 45
  systems, 468 documents, 37 memories, 354 backlog phases`.
- Vitest, `ts/src/stage/NotesStripRegion.test.tsx` (27 tests): the entry model through the rendered
  component, variant selection against stubbed measurements, hover and focus pause, the four R13
  conditions with fake timers, image listing and sizing, the mixing ruling, the unavailable and empty
  directory messages. Removing the scroll condition or the hold condition from `advanceIfDue` makes
  one test fail each, checked by hand. `cd ts && npm test`: `Test Files 9 passed (9)`, `Tests 116
  passed (116)` after the fix round.
- Gates: `uv run pytest`: `1 failed, 1903 passed, 1 skipped`; the failure is
  `test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`, which expects a
  permission error that root does not get (environmental, the same one recorded for `phase-wbf-07`).
  `uv run ruff check src/ test/ tools/`: `All checks passed!`. `uv run mypy src/`: `Success: no issues
  found in 51 source files`. `cd ts && npm run lint`: no output (clean).

## Fix round (after the gating adversary and the shadow judge)

Both verdict records are in `docs/08-governance/reviews/verdicts/` (adversary PASS, 2 major and 4
minor; judge REJECT, 1 major and 3 minor), copied unedited. Fixed in commit 1107cd9:

- **Adversary F01 / judge F04 (single-entry loop).** `loop` is now `!(autoAdvance && entryCount >=
  2)`. The control is disabled below two entries but keeps its setting, so a lone long entry no
  longer parks at its tail. Test: enable the timed advance on a three-entry file, switch to a
  one-entry file, assert the animation repeats.
- **Judge F01 (double step).** The entry's unmount cleanup released the hold *and* called
  `advanceIfDue`, which stepped again when the interval had already elapsed mid-scroll. The
  cleanup now only clears the hold. Test: elapse the interval mid-scroll, click Next then
  Previous, assert one step each.
- **Adversary F02 (reduced motion).** Chose the hidden-scrollbar fallback, not the wrapped vertical
  one: `overflow-x: auto; scrollbar-width: none` on the reduced-motion box. A visible 15 px
  scrollbar left a 3 px line in the 18 px box; the wrapped box would have needed the entry to grow,
  which layout 1's strip cannot hold. The line still scrolls by wheel, drag, touch and arrow keys (the
  entry is a tab stop). Checked in Chromium with classic scrollbars shown. Test: the inline style and
  tab stop. A `::-webkit-scrollbar` rule is not needed: no class is used and `scrollbar-width` is
  supported by every browser the demo uses.
- **Judge F03.** An unbroken word wider than the box also selects the ticker
  (`measurer.scrollWidth`). Test added.
- **Adversary F05.** The measurement copy is now a sibling of the entry box (its font copied onto
  it when measured), so the entry's `textContent` is its own text only; messages (loading, missing,
  rejected file) are a separate `NoticeView` that does not scroll, with the full text in `title`.
  Consequence: a long message is cut in layout 1's strip, where before this round it scrolled.
- **Adversary F03, F04.** Residue recorded as four kinds with owners (above). The image strip
  height is stated in the sizing rule (100 px).
- **Adversary F06 (note only).** `ENTRY_BOX_STYLE` sets `overflow: hidden` inline, which overrides
  `.stage-notes-strip__current { overflow-y: auto }` in `StagePage.css`. A later edit to that CSS
  rule has no effect on entries; the stylesheet is outside this phase's deliverables, so this is for
  a later CSS pass.
- **Judge F02.** The live fit run was done and is recorded above (command, counts, before and
  after). `REQ-037` is not edited.
- **Judge F04 (mixing ruling in a code comment only).** Left for the owner: the ruling is on the
  ratification list above; recording it in a governed document waits for that.

## Unresolved

- `ts/src/stage/NotesStripRegion.test.tsx` is outside the declared deliverable
  (`ts/src/stage/NotesStripRegion.tsx` only). The deliverable needs widening by that file, which the
  Session Manager applies on the trunk at completion. The ESLint rule `react-refresh/only-export-components`
  forbids exporting the pure entry-model functions from the component file, so the test goes through
  the component.
- `REQ-037`'s live-run paragraph says phase-wbf-06 should name the moving element in the notes strip
  row if it is not `.stage-notes-strip__current`. The moving element is its inner line
  (`[data-notes-part="track"]`), so the row should name it, and the "unbounded entry" defect can be
  struck. `REQ-037` is outside this phase's deliverables and was not edited; an amendment is
  requested in the hand-off.
- In layout 1 the strip's padded row is 13 px, so an image there is an 18 px thumbnail. The rule works
  at any strip height (329x205 in layout 2); the strip's height is the limit. That is the geometry
  question of idea `000133`, not decided here.
- A running ticker needs `Element.animate`; without it (an old browser) a long entry would be cut,
  not scrolled. Every browser the demo uses has it.
