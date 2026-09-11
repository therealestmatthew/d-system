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
- Playwright browser verification (pack W02-W) — not yet dispatched; the coordinator's
  responsibility per the phase's verification list, not this orchestrator's.

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
  (REQ-007 W05) — **Not met yet**: implemented and code-reviewed clean (W02-V1, re-confirmed
  post-fix), but this condition requires the rendered-browser check (W02-W), which has not run.
- A multi-panel slot's header dropdown lists and swaps its panels; a single-panel slot renders a
  plain header (REQ-007 W06) — **Not met yet**: same basis — code-reviewed clean, not yet
  browser-verified.
- The notes strip is display-only with all controls in its dropdown, the file picker switches
  and persists the notes file, and the tooltip sits far left (REQ-007 W01) — **Not met yet**:
  same basis — code-reviewed clean (W02-V2, re-confirmed post-fix, including the MAJOR-2 picker
  filter), not yet browser-verified.
- Zero page scroll and no overlapping regions in both layouts at all four sizes — **Not met
  yet**: structural CSS confirmed by W02-V1 (fixed height, `overflow: hidden` chain), but the
  actual four-size, two-layout measurement is W02-W's job and has not run.

## Backlog

`status: active`, `agent: agent-demo-stage`. `next_action`: both W02-A majors fixed and
re-validated clean; dispatch the coordinator-owned `W02-W` (Playwright browser verification) —
outside this orchestrator's dispatch list per `PROMPT-021`'s W02 kickoff — then, contingent on
its result, close the session. `deliverables` widened on `dev` (`9cc8fd8`) to add
`ts/vite.config.ts` per W02-A minor 4. `completion_evidence` (interim, real files existing now,
not a completion claim) extended with `ts/src/workbench/schemaVersionContext.ts` and
`ts/vite.config.ts`. `result` updated to record the fix cycle and re-validation.

## Unresolved

- `W02-W` (Playwright browser verification) has not run. Per the phase's own verification list
  this is part of the GOV-003 completion gate and belongs to the coordinator, not this
  orchestrator, to dispatch.
- The three `test_demo_terminal.py` PTY failures are the recurrent host-wide pyenv shim
  contention already tracked under idea `000097` (per `phase-wb-01`'s session record) — not a
  new or phase-specific defect.
- W02-A minor 3 (the ADR-016 layout-schema test is unbuilt and untracked) is recorded as idea
  `000098` by the coordinator — no action pending from this orchestrator.
- Not integrated, not pushed (beyond the one sanctioned minor-4 commit on `dev`), not marked
  complete — per this orchestrator's standing restrictions and pending the coordinator's `W02-W`
  dispatch and the owner's approval.
