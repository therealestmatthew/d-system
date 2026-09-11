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
onto `dev` at `0ab5aa4`):

- `cd ts && npm run build` — `tsc -b && vite build` succeeds, `✓ 44 modules transformed`, `✓
  built in 1.03s` (the chunk-size-over-500kB note is Vite's informational warning, not an
  error).
- `uv run python -m src.governance` — exit 0, `Governance OK: 18 systems, 155 documents, 16
  memories, 119 backlog phases`.
- `uv run python tools/check_no_private_content.py` with all changes staged (`git add -A`
  first; nothing to stage, the worktree was already clean post-rebase) — `check_no_private_content:
  OK (471 tracked files, 0 identifiers checked)`.
- Adversarial review (pack W02-A) — not yet dispatched; the coordinator's responsibility per the
  phase's verification list, not this orchestrator's.
- Playwright browser verification (pack W02-W) — not yet dispatched; same as above.

Work-item validators: W02-V1 (layout engine) passed with no findings — layouts load from
`_data/workbench/layouts/` data files with no hardcoded geometry in components, both shipped
layouts carry `schema_version`, stable ids, fractional geometry and default assignments; the
slot-header dropdown and plain-header cases are both implemented; the configuration surface is
limited to layout choice and slot assignment; the single namespaced versioned localStorage key
falls back to defaults silently on mismatch; zero-scroll is structural (fixed page height,
`overflow: hidden` down the box chain) in both layouts. W02-V2 (notes strip) passed with no
findings — the strip is display-only, carries no title or "talking points" string, has the
tooltip at its far left, holds every control (cycling, timed advance, file picker) in one
dropdown fed by the `phase-wb-01` listing route rather than a hardcoded list or client-side
walk, persists the chosen file under the shared ADR-016 key via merge-on-write, and the old
panel's standalone controls and stale placeholder comment are gone. `npm run build` and a
case-insensitive `grep` for "talking points" (no hits) both confirmed by the validator and
reproduced independently by this orchestrator.

The phase gate (W02-G) was dispatched twice: the first run's transcript truncated mid-check
(never treated as a result — not retried from scratch, re-dispatched instead per the
resume-don't-restart rule). The second run recorded a full pass: governance exit 0; staged
private-content check OK (471 tracked files, 0 identifiers); both phase deliverables present;
`npm run build` exit 0; `uv run pytest` — `534 passed, 3 failed`, the three failures being the
known host-wide pyenv shim rehash contention in `test_demo_terminal.py`
(`test_posix_adapter_reports_alive_then_not_alive`,
`test_resize_text_frame_applies_to_pty_window_size`,
`test_two_concurrent_websocket_sessions_are_independent_shells`) — an environmental defect, not
a phase finding; and the diff against `dev` touches only `ts/` and `_data/workbench/layouts/`.

A blocking finding was raised and resolved mid-session: `W02-C2`'s deletion of
`ts/src/stage/TalkingPointsRegion.tsx` (the sanctioned outcome of its dispatch) broke
governance's completion-evidence check because `phase-demo-02` (already complete, integrated)
listed that file as evidence. The coordinator resolved it on `dev` by retiring that one
evidence line (its other eight evidence files stand), recorded under GOV-003 in commit
`0ab5aa4`. The worktree was rebased onto that commit and governance now passes.

## Acceptance

- Switching layouts moves the terminal region per each layout's geometry, panel reassignment
  renders in the chosen slot, and both survive reload; a cleared store yields layout-1 defaults
  (REQ-007 W05) — **Not met yet**: implemented and code-reviewed clean (W02-V1), but this
  condition requires the rendered-browser check (W02-W), which has not run.
- A multi-panel slot's header dropdown lists and swaps its panels; a single-panel slot renders a
  plain header (REQ-007 W06) — **Not met yet**: same basis — code-reviewed clean, not yet
  browser-verified.
- The notes strip is display-only with all controls in its dropdown, the file picker switches
  and persists the notes file, and the tooltip sits far left (REQ-007 W01) — **Not met yet**:
  same basis — code-reviewed clean (W02-V2), not yet browser-verified.
- Zero page scroll and no overlapping regions in both layouts at all four sizes — **Not met
  yet**: structural CSS confirmed by W02-V1 (fixed height, `overflow: hidden` chain), but the
  actual four-size, two-layout measurement is W02-W's job and has not run.

## Backlog

`status: active`, `agent: agent-demo-stage`. `next_action`: dispatch the coordinator-owned
`W02-A` (adversarial review) and `W02-W` (Playwright browser verification) — both outside this
orchestrator's dispatch list per `PROMPT-021`'s W02 kickoff — then, contingent on their results,
close the session. No `completion_evidence` or `result` recorded yet; the phase remains open
with real interim progress (two work items committed and validated, the phase gate green) but no
completion claim.

## Unresolved

- `W02-A` and `W02-W` have not run. Per the phase's own verification list these are part of the
  GOV-003 completion gate and belong to the coordinator, not this orchestrator, to dispatch.
- The three `test_demo_terminal.py` PTY failures are the recurrent host-wide pyenv shim
  contention already tracked under idea `000097` (per `phase-wb-01`'s session record) — not a
  new or phase-specific defect.
- Not integrated, not pushed, not marked complete — per this orchestrator's standing
  restrictions and pending the coordinator's `W02-A`/`W02-W` dispatch and the owner's approval.
