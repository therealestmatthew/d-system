---
schema_version: 1
id: doc-session-workbench-layout-notes-strip
code: SESS-2026-09-10-12
title: Demo stage orchestration — layout engine and notes strip (phase-wb-02)
kind: session
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-ui]
depends_on: [doc-workbench, doc-prompt-workbench-delegation-pack]
---

# Demo stage orchestration — layout engine and notes strip (phase-wb-02)

## Phase

`phase-wb-02` — Layout engine and notes strip: the ADR-016 slot model, the two shipped layouts,
the slot-header dropdown, the layout-configuration surface, and the notes strip replacing the
talking-points panel.

## Verification

Run in the worktree (`/code/d-system-worktrees/phase-wb-02`, branch `agent/phase-wb-02`, rebased
onto `dev` at `9cc8fd8`, the deliverables-widening commit):

- `cd ts && npm run build` — `tsc -b && vite build` succeeds, `✓ 45 modules transformed`, `✓
  built in 1.03s` (the chunk-size-over-500kB note is Vite's informational warning, not an
  error).
- `uv run python -m src.governance` — exit 0, `Governance OK: 18 systems, 156 documents, 16
  memories, 119 backlog phases`.
- `uv run python tools/check_no_private_content.py` with all changes staged (`git add -A`
  first) — `check_no_private_content: OK (473 tracked files, 0 identifiers checked)`.
- Adversarial review (pack W02-A) — dispatched by the coordinator; reported no blocker, two
  MAJORs and two minors (see below). Both majors fixed and re-validated; minor 3 (the
  ADR-016 layout-schema test) recorded by the coordinator as idea `000098`, no action from this
  orchestrator; minor 4 (declaration widening) resolved directly (see Backlog).
- Playwright browser verification (pack W02-W) — dispatched by the coordinator; **passed every
  reachable check with measured evidence**: zero-scroll (`scrollHeight <= viewport`) and
  pairwise non-intersection at 1280x720, 1366x768, 1920x1080 and 1024x768 in BOTH layouts
  (8/8, screenshots kept); layout switch moved the terminal bounding box per geometry, reload
  restored it, clearing the storage key restored layout-1 defaults; the notes strip passed its
  full battery (no title, controls in one dropdown, cycling, far-left tooltip hover/collapse,
  file choice persisting across reload); no uncaught application console errors. Two
  sub-checks — the W06 multi-panel dropdown swap and panel reassignment — were **not
  exercisable**: every slot in the shipped layouts resolves to at most one implemented panel (the explorer slot to zero)
  until phase-wb-04..06 register theirs; those phases' browser gates cover both paths.
- Coordinator-dispatched targeted browser re-check after the fix commit (`38f56b3`): the
  picker's rendered option list was exactly `["talking-points.json"]` while the raw listing
  route still returned both JSON files (the incompatible `demo-commands.json` filtered by the
  content probe); cycling, reload persistence, the layout switch/reload/clear-storage
  round-trip (bounding boxes byte-identical across reload), and the shared single storage key
  all confirmed; the only console error across the session was the benign favicon 404.
- At close, on dev after integration (`aeea6db`), re-run by the coordinator:
  `cd ts && npm run build` — `✓ built in 1.12s`; `uv run python -m src.governance` — exit 0;
  `uv run python tools/check_no_private_content.py` with changes staged — `OK (473 tracked
  files, 31 identifiers checked)`.

Work-item validators, first pass: W02-V1 (layout engine) passed with no findings. W02-V2 (notes
strip) passed with no findings. The phase gate (W02-G) was dispatched twice — the first
transcript truncated mid-check and was never treated as a result (re-dispatched, not retried
from scratch); the second run recorded a full pass: governance exit 0; staged private-content
check OK; both deliverables present; `npm run build` exit 0; `uv run pytest` — `534 passed, 3
failed`, the three failures being the known host-wide pyenv shim rehash contention in
`test_demo_terminal.py` (`test_posix_adapter_reports_alive_then_not_alive`,
`test_resize_text_frame_applies_to_pty_window_size`,
`test_two_concurrent_websocket_sessions_are_independent_shells`) — an environmental defect, not
a phase finding; diff against `dev` touched only `ts/` and `_data/workbench/layouts/`.

A blocking finding was raised and resolved mid-session: `W02-C2`'s deletion of
`ts/src/stage/TalkingPointsRegion.tsx` (the sanctioned outcome of its dispatch) broke
governance's completion-evidence check because `phase-demo-02` (already complete, integrated)
listed that file as evidence. The coordinator resolved it on `dev` by retiring that one
evidence line (its other eight evidence files stand), recorded under GOV-003 in commit
`0ab5aa4`.

W02-A (adversarial review) then reported, verbatim: MAJOR 1 — the ADR-016 "one namespaced key"
was two independently tracked version numbers (`useWorkbenchLayouts.ts` derived the storage
key's schema version dynamically from the fetched layout files; `NotesStripRegion.tsx` imported
a hardcoded `WORKBENCH_SCHEMA_VERSION` constant), coinciding only while both were 1. MAJOR 2 —
the notes-file picker listed every `.json` the listing route returned, including incompatible
files like `demo-commands.json`, a reachable error state. Fixed in one dispatch to
`demo-creator-web` (fix cycle 1/2 against each of `W02-C1` and `W02-C2`), committed narrowly as
`38f56b3`: a new `schemaVersionContext.ts` module makes `useWorkbenchLayouts`'s resolved schema
version the single source the layout engine and the notes strip both read (the hardcoded
constant removed from `types.ts` entirely), and the notes-file picker now probes each listed
candidate against `isNotesFile` before offering it, still sourced exclusively from the
phase-wb-01 listing route. `cd ts && npm run build` after the fix: `✓ 45 modules transformed`,
`✓ built in 1.05s`/`1.04s` (reproduced independently by this orchestrator and by both
re-validators). W02-V1 and W02-V2 were re-dispatched verbatim against the post-fix, post-rebase
diff and both returned **PASS, no findings** — confirming closure of both majors and no
regression in either work item's original obligations. Minor 4 (`ts/vite.config.ts` gained the
`serveWorkbenchLayouts` plugin but the phase's declared deliverables didn't name it) was handled
directly per `AGENTS.md`'s declaration-widening rule: one small commit on `dev` (`9cc8fd8`)
adding `ts/vite.config.ts` to `phase-wb-02`'s `deliverables`, governance confirmed green before
and after.

## Acceptance

- Switching layouts moves the terminal region per each layout's geometry, panel reassignment
  renders in the chosen slot, and both survive reload; a cleared store yields layout-1 defaults
  (REQ-007 W05) — **Met, with one sub-check deferred**: W02-W measured the layout switch
  (bounding box `(12, 54.6, 716.9x778.4)` → `(12, 361.4, 1241x471.6)`), reload restoration and
  the clear-storage fallback; the panel-reassignment render is not exercisable while every
  slot ships exactly one implemented panel, and is covered by phase-wb-04..06's browser gates
  (recorded in the phase result).
- A multi-panel slot's header dropdown lists and swaps its panels; a single-panel slot renders a
  plain header (REQ-007 W06) — **Met on the reachable half, swap deferred**: W02-W confirmed
  zero multi-panel slots render a dropdown today (`.stage-workbench-slot--multi` count 0) and
  single-panel slots render plain headers; the swap itself first becomes exercisable when
  phase-wb-04..06 register panels, whose gates assert it (W06-W explicitly).
- The notes strip is display-only with all controls in its dropdown, the file picker switches
  and persists the notes file, and the tooltip sits far left (REQ-007 W01) — **Met**: W02-W's
  full battery plus the post-fix targeted re-check (picker filtered to notes-shaped files,
  choice persisted across reload under the single ADR-016 key).
- Zero page scroll and no overlapping regions in both layouts at all four sizes — **Met**:
  W02-W measured `scrollHeight <= viewport` and pairwise non-intersection at all four sizes in
  both layouts, 8/8 with screenshots.

## Backlog

`status: complete`, `agent: agent-demo-stage` retained as the record of who did the work.
`next_action` is the "None — phase complete" close note. `completion_evidence` names the nine
`ts/` files, the two layout JSON files and this session record. `result` records the full arc:
items, gate, blocking finding, W02-A majors and their one-dispatch fix, re-validation, W02-W's
measured pass with the two deferred sub-checks, the targeted re-check, and the fast-forward
integration at `622c558` under PROMPT-023 delta 1 (completion commit `aeea6db`).
`phase-wb-02` removed from `next_up` in the completion commit.

## Unresolved

- The W06 multi-panel dropdown swap and the panel-reassignment render remain unverified in a
  browser — structurally unexercisable until phase-wb-04..06 register their panels (every slot ships at most one
  implemented panel today, the explorer slot zero); their gates (W06-W explicitly) assert
  both. Recorded in the phase result so the deferral cannot silently drop.
- The three `test_demo_terminal.py` PTY failures are the recurrent host-wide pyenv shim
  contention tracked under idea `000097` — environmental, not phase-specific.
- The ADR-016 layout-schema test is unbuilt, tracked as idea `000098`.
- Owner-side commands pending: `git push origin dev`, and worktree/branch cleanup for the
  merged `phase-wb-01` and `phase-wb-02` — classifier-blocked for the coordinator.

## Review

Independent sub-agent review at close (fresh agent, range `bc52e82..aeea6db`, its own reruns).
Findings condition by condition, pasted:

- **Condition 1 (W05) — holds with recorded deferral.** "The two layout files place the
  terminal in genuinely different geometry, consistent with the record's measured bounding
  boxes (tall-narrow → wide-short). Persistence and cleared-store fallback are implemented in
  `storage.ts` (versioned key, `loadStoredState` returning null on any mismatch → defaults)
  and `useWorkbenchLayouts.ts:52-53`. The panel-reassignment deferral is factually justified."
- **Condition 2 (W06) — holds with recorded deferral.** "`Slot.tsx:32-57` implements all
  three cases (zero implemented → placeholder with plain header; one → panel rendered
  directly; two-plus → `stage-workbench-slot--multi` dropdown header). No slot reaches the
  multi-panel branch, so the swap is structurally unexercisable — the deferral is accurate in
  substance."
- **Condition 3 (W01) — holds.** "The strip surface renders only the current entry; all
  controls live inside the single Popover dropdown; the Tooltip is the first child of the row,
  i.e. far left. The picker probes each listing-route candidate's content against `isNotesFile`
  before offering it — exactly the W02-A MAJOR 2 fix. Persistence goes through the versioned
  ADR-016 key with merge-on-write."
- **Condition 4 — holds per W02-W's recorded measurements** (8/8); "nothing in the merged
  CSS/grid code contradicts it, and the grid `areas` definitions in both layout files are
  non-overlapping by construction."
- **Verification reruns**: build, governance and the staged private-content check all
  reproduced the record's close-time outputs exactly. **W02-A fix verified in merged code**:
  `schemaVersionContext.ts` exists, `StagePage.tsx` sole provider, `NotesStripRegion.tsx`
  consumes it; `grep -rn WORKBENCH_SCHEMA_VERSION ts/src/` — zero hits; `TalkingPointsRegion`
  — zero hits including CSS; "talking points" survives only in comments and the data-filename
  constant, no UI copy. Backlog claims all match; `aeea6db` is an ancestor of HEAD.
- **One minor wording inaccuracy, no substantive discrepancy**: the record said "every slot
  ... resolves to exactly one implemented panel"; the explorer slot resolves to zero.
  "Zero and one implemented panels both make the multi-panel swap and reassignment
  unexercisable... not close-blocking." — Accepted; corrected to "at most one (the explorer
  slot to zero)" in this record.
- **Verdict (verbatim)**: "all four acceptance conditions hold (1 and 2 with the recorded,
  factually accurate deferral); close is supportable."

## Decisions

- The mid-session governance collision (W02-C2's sanctioned deletion of the old
  talking-points panel breaking `phase-demo-02`'s pinned completion evidence) was resolved by
  the coordinator with a new general rule recorded in GOV-003: a completed phase's evidence
  line retires when a later phase's sanctioned scope deletes the file, in the same diff as
  the GOV-003 note, never silently. The orchestrator's choice to stop and report rather than
  edit a closed phase's record was the correct reading of its mandate.
- Both W02-A majors were fixed in a single dispatch because they touched the same two files —
  counted as fix cycle 1 of 2 against each affected work item, keeping the cap accounting
  honest rather than laundering two fixes into one budget slot.
- The W06 multi-panel sub-checks were ruled deferred-not-failed: the mechanism is built and
  code-reviewed, no shipped slot can exercise it until phase-wb-04..06 register panels, and
  those phases' browser gates assert exactly those paths. Recorded in the phase result so the
  deferral survives scrutiny in six months.
- Minor 4 (undeclared `ts/vite.config.ts`) was resolved by widening the phase's declarations
  on dev per AGENTS.md rather than reverting a necessary change to fit stale paperwork.

## Corrections

- The W02-G gate's first dispatch truncated mid-run and was correctly discarded rather than
  treated as a verdict; the second dispatch recorded the full pass. No repository-content
  mistakes required fixing this session — the fix cycle addressed reviewer findings, not
  regressions of previously-passing claims.
- Stale dev servers from an earlier test run were masking the layouts middleware when W02-W
  arrived; the validator diagnosed the staleness (process older than `vite.config.ts`'s
  mtime), killed and restarted per its dispatch commands, and correctly attributed the
  symptom to the environment rather than the checked-in code.

## Left undone

- The browser-rendered proof of the multi-panel dropdown swap and panel reassignment — waits
  on phase-wb-04..06's panels by structural necessity, asserted by their gates.
- The ADR-016 layout-schema test (idea `000098`) and the failure/anti-pattern tracking system
  (idea `000097`) — both parked for the owner's prioritization.
- The dev push and merged-branch cleanup — owner commands, listed above.
- Phases wb-03 through wb-07 continue in the coordinator session; phase-wb-03 was claimed and
  its orchestrator dispatched while this record was being closed.
