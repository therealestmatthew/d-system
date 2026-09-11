---
schema_version: 1
id: doc-session-rehearsal-refresh
code: SESS-2026-09-11-05
title: Rehearsal refresh (phase-wb-07) checkpoint
kind: session
status: active
owner: repository-owner
created: '2026-09-11'
updated: '2026-09-11'
systems: [sys-demo-stage]
depends_on: [doc-workbench]
---

# Rehearsal refresh (phase-wb-07) checkpoint

## Phase

`phase-wb-07` — Rehearsal refresh: runbook, Windows checks, owner-driven timing.

## Verification

- `uv run python -m src.governance` (orchestrator run, in the worktree, after W07-G):
  ```
  Governance OK: 18 systems, 163 documents, 16 memories, 119 backlog phases
  ```
- `uv run python tools/check_no_private_content.py` with the changes staged (orchestrator
  run, in the worktree, after W07-G):
  ```
  note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
  check_no_private_content: OK (497 tracked files, 0 identifiers checked)
  ```
- Playwright rehearsal pass over the runbook's browser-marked steps (demo-validator-web,
  pack W07-W, dispatched by the coordinator): **PASS, no blocking finding** — every control
  the runbook names in the browser-marked steps exists under that name and behaves as
  described (terminal header dropdown, notes-strip controls, terminal ellipsis menu, the
  four injection dropdowns with counts, the layout-configuration dialog, explorer header
  dropdown and swap, HTML Viewer refresh/file-dropdown/directory controls, parked-skill
  dropdown state, refresh re-fetch confirmed via the iframe's `?v=` bump, terminal echo
  round-trip). A first dispatch was blocked by a stale Playwright browser lock (a leftover
  Chrome from the pass-2 rehearsal holding the shared profile); the owner killed the stale
  process and the re-run completed. Two non-blocking notes: (a) the HTML Viewer has an
  "Embedded"/"Open-in-tab link" toggle documented nowhere in the runbook — recorded as idea
  `000105`; (b) zero-scroll could be mechanically confirmed only at the single available
  window size (1600×1000; the Playwright environment ignores viewport overrides), so
  multi-size scroll verification remains a rehearsal-environment limitation, not a defect.
- Supplementary owner-requested check (same day, coordinator dispatch): the terminal shell
  session **persists across layout switches**. With fresh state and Terminal (bash) resolved
  in both layouts, a marker variable set in Layout 1 survived Layout 1 → 2 → 1
  (`check-persist26030` printed identically after each switch), scrollback stayed intact, no
  new terminal websocket opened (constructor hook recorded zero connections), and the
  "connection closed" message never appeared. Caveat recorded for the owner: per-layout
  stored panel selections mean a layout whose terminal slot resolves to a different panel
  type would remount and end sessions on switch.
- The executed Windows checklist and both dry-runs' recorded times in the runbook:
  not run — owner-machine, owner-driven work; not performed by any agent.
- W07-C1 (demo-creator-docs): rewrote `docs/00-working/demo-runbook.md` and
  `docs/00-working/demo-windows-setup.md` against the final workbench UI (commit `0855033`).
- Talking-points finalization (this orchestrator, its own authored prose per its charter):
  finalized the presenter-facing step copy over the creator's skeleton (commit `7b4f663`),
  then fixed after a runbook gap found by rehearsal pass 1 (commit `110f421`).
- W07-V1 (demo-validator-code), first pass: **FAIL** — one finding: both Dry-Run `/orient`
  rows' narration described the notes strip as "carrying my talking points," reattaching the
  retired "talking points" panel label (REQ-007 W01) to the presenter's scripted narration.
  Fixed directly by this orchestrator (audience-facing prose is its own to write, not a
  creator/validator fix-cycle item) — commit `84001d6`.
- W07-V1, re-validation: **PASS**, no findings. Confirmed the "talking points" phrase no
  longer appears anywhere in either document, the step shape (commands/fallback/timebox)
  holds, timeboxes sum to 15m, Windows checklist covers all five required items, and
  `tools/demo_reset.py`/OPS-013 remain untouched by the diff.
- Agent-driven rehearsal pass 1 (W07-R, `demo-validator-web`): completed and recorded in the
  runbook (commit `47a81d3`). Three findings, one addressed (the `/orient` step now
  instructs starting a `claude` session before `/idea`); two left as noted, non-blocking
  observations (the `_parked` skill entry rendering in the dropdown; the ~85s `/orient`
  measurement against its 1m timebox, attributed to cold-start latency rather than the
  live-segment's on-stage time).
- Agent-driven rehearsal pass 2 (W07-R): two dispatches by this orchestrator were each
  truncated by their turn limit mid-investigation before delivering a final report, with no
  `SendMessage` tool available in this orchestrator's toolset to resume a truncated agent.
  Reported up as a blocking finding. The coordinator then dispatched pass 2 itself, resumed
  the truncated agent past its cutoff, and delivered the complete report. Recorded in the
  runbook (commits `b799a53`, `a96443b`): /orient took ~232s against its 1m timebox (a
  blocking finding inside the step, not just a timing overage — see below); /idea used the
  pre-seeded fallback as designed; /idea-triage completed one idea's triage in ~115s only
  after the dispatching agent intervened to stop broader scope; the overview-skill rebuild
  and test steps passed well under their timeboxes.
- Four findings from pass 2, all recorded in the runbook's Rehearsal Findings list:
  (4) the terminal slot's panel picker and non-guaranteed default panel were undocumented —
  a Linux rehearsal host defaulted to a non-functional CMD panel; **fixed** as a runbook gap
  (the `/orient` step and Workbench UI Reference now document the picker and instruct
  confirming a working panel first, commit `a96443b`); (5) `/idea-triage` triages the whole
  open backlog rather than just the captured idea and resists `Escape` (only `Ctrl-C`
  stops it) — a real mismatch with the runbook's single-idea narrative and 2-minute
  timebox; **fixed** within the runbook's own scope (the step's narration and timebox now
  state the real behavior and give an explicit `Ctrl-C` fallback, commit `a96443b`) since
  the underlying command's behavior is not this phase's deliverable to change; (6) the
  terminal panel renders clipped to ~85px (`.xterm` container `height: 0` against a child
  `.xterm-screen` height of 372.99) — a real CSS/layout sizing bug that would hide almost
  all live output; this is a code defect outside this phase's deliverables (application
  code, not the runbook/checklist) and is **not fixed here** — recorded instead as idea
  `000104` (commit `b799a53`), flagged prominently: this would wreck the live demo if
  unaddressed; (7) repeat of pass 1's already-noted cosmetic `_parked` dropdown entry, no
  new action.
- Pass 2's side effects on the idea log (idea `000087` annotated and moved `open` → `triaged`
  via the sanctioned `append_idea.py` calls, as the intended result of exercising
  `/idea-triage`) and this orchestrator's own idea `000104` write are committed, with
  `docs/00-working/ideas.md` and `_public/overview/index.html` regenerated alongside per the
  drift test (commit `b799a53`).
- W07-G (phase gate, `demo-validator-check`), first dispatch: **RED** on item 6 only — the
  validator used a two-dot `git diff dev --name-only`, which picked up `dev`'s own
  independent commits (made directly on `dev` in the primary checkout, not on this branch —
  a session-record file, catalog and backlog updates) as if they were part of this branch's
  diff. Items 1-5 passed clean. Re-dispatched with a note to use the merge-base-relative
  `git diff dev...HEAD` instead (the same triple-dot form `W07-V1` already used) and to
  treat the rehearsal's sanctioned idea-log/regenerated-view side effects as expected,
  since the checklist item itself does not specify diff notation and the pack's prompt was
  not altered. Re-check: **PASS on all six items** — governance OK; private-content OK
  staged; both deliverables present and updated; runbook timeboxes sum to exactly 15m in
  both Dry-Run tables; `tools/demo_reset.py`/OPS-013 untouched; the merge-base diff against
  `dev` touches only the two deliverables plus the three sanctioned rehearsal-side-effect
  paths (`_data/ideas.jsonl`, `docs/00-working/ideas.md`, `_public/overview/index.html`).

## Acceptance

- The runbook describes the workbench UI only, with per-step commands, fallbacks and
  timeboxes summing inside 15 minutes (REQ-007 W13) — **Met**: W07-V1 passed clean on
  re-validation and W07-G independently confirmed the 15m sum in both Dry-Run tables.
- The R06 smoke check and both shell round-trips are recorded as passing on the
  presentation machine — **Not met**: owner-machine, owner-driven work not yet performed by
  the owner. Cannot be performed by an agent.
- Both owner-driven dry-runs complete within 15 minutes with every step inside its timebox,
  per-step times recorded — the REQ-006 R09 conditions deferred from phase-demo-05 are
  closed, not re-deferred — **Not met**: owner-driven work not yet performed. The
  agent-driven mechanics-check passes (pack W07-R) are explicitly distinct from these and
  do not close R09 per the runbook's own labeling; both passes are now recorded, but they
  are mechanics checks, not the owner's own timed dry-runs.

## Backlog

- `status: active`, `agent: agent-demo-content`.
- `next_action`: All agent-executable work for this orchestrator's charter is done — W07-C1,
  talking points, W07-V1 (clean on re-validation), both agent-driven rehearsal passes
  (recorded, with runbook gaps from pass 2 fixed and the one code defect routed to idea
  `000104` rather than fixed here), and W07-G (green on re-check with the correct
  merge-base diff). What remains is entirely owner-machine, owner-driven: the REQ-006 R06
  terminal smoke check, the CMD and PowerShell round-trips (REQ-007 W12's Windows half),
  and both owner-driven timed dry-runs closing REQ-006 R09's deferred conditions — none of
  which can be performed by an agent. The phase cannot close until the owner performs and
  records these.
- `result`: see `backlog.yaml`'s `result` field for this phase, mirrored from the same
  facts recorded above.

## Unresolved

- The owner-machine, owner-driven items (REQ-006 R06 terminal smoke check, the CMD and
  PowerShell round-trips of REQ-007 W12, and both owner-driven timed dry-runs closing
  REQ-006 R09) remain entirely outstanding. None of these can be performed by an agent;
  they close only on the owner's own recorded results in the runbook and Windows checklist.
- Idea `000104` (terminal panel clipped to ~85px, a real layout sizing bug found during
  pass 2) is flagged prominently for the owner: it would wreck the live demo if
  unaddressed, and is outside this phase's deliverables to fix.
- Idea `000105` (the HTML Viewer's Embedded/Open-in-tab toggle is documented nowhere in the
  runbook) is recorded on the phase branch for the owner — a small runbook follow-up or a
  flag-gated control, to be reconciled with the layout-assignment redesign.
- Two follow-up fixes are staged for a fresh session in
  `docs/00-working/handoff-workbench-layout-and-terminal-fixes.md` (owner-directed,
  2026-09-11): the idea `000104` terminal truncation fix first, then a layout-assignment
  redesign; that session is under way and edits `REQ-007`/`PLAN-022`/`backlog.yaml` in the
  primary checkout, which is why this checkpoint deliberately did not touch
  `backlog.yaml` — the phase's `next_action` there still predates the W07-W result, and
  this record is the current source for it.
- Process hazard observed this checkpoint, for the owner: sequential idea ids collide
  across branches. Dev's log tip was `000101` while the un-merged `agent/phase-wb-07`
  branch already carried `000102`–`000104`, so an append on dev minted a second, different
  `000102` (caught before commit, reverted, re-appended at the branch tip as `000105`).
  Until the branch merges, `_data/ideas.jsonl` must only be appended to on
  `agent/phase-wb-07`.
