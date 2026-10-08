---
schema_version: 1
id: doc-session-html-viewer-toggle-runbook
code: SESS-2026-10-08-04
title: Document the HTML Viewer Embedded/Open-in-tab toggle in the runbook (phase-wbf-18)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-demo-stage]
depends_on: [doc-workbench-features-defects, doc-workbench-features-defects-requirements]
---

# Document the HTML Viewer Embedded/Open-in-tab toggle in the runbook (phase-wbf-18)

## Phase

`phase-wbf-18` (document the HTML Viewer's Embedded/Open-in-tab header toggle in the demo runbook),
built by `agent-standby` (Session 3 - Standby Builder) as a subagent of the Session Manager's
`ASSIGN`, run 2026-10-08. Worked in `/home/user/d-system-worktrees/phase-wbf-18` on
`agent/phase-wbf-18`, cut from the run's integration branch `ccr-b69b05b4-tdcrux`, which stands in
for `dev`. Documentation only; no code changed. The work answers idea `000105` (the runbook does not
document the toggle) and requirement `R31` in `REQ-012`.

## What changed

- `docs/00-working/demo-runbook.md` (ungoverned, per `ADR-010`): the HTML Viewer entry now names the
  header toggle, gives its two labels, says what each state shows, how to switch back, that the
  setting is one for the whole panel and is not saved across a reload, and that the link appears
  only once a page is selected and found. It records the ladder-number mismatch described below.
  Neither the runbook's Descope Ladder nor the control's label is changed.
- `docs/09-backlog/backlog.yaml`: `phase-wbf-18` gains `session`, `completion_evidence` and `result`.
  Its `status` stays `active`.
- `docs/08-governance/catalog.md`: regenerated for this session record and the phase entry.

## Description checked against the code

Read from `ts/src/stage/HtmlViewerRegion.tsx`, the trunk's copy (last changed 2026-10-05):

- The state is one boolean, `useState(true)` (line 144). Nothing writes it to `localStorage`, so a
  reload resets it to Embedded. The tabs are persisted; this setting is not.
- The button (lines 398-405) has `aria-pressed={!embedded}` and the label `Embedded` when embedded,
  `Open-in-tab link (rung 3)` otherwise. The label shows the current mode; a click switches to the
  other.
- Embedded renders an iframe (`sandbox=""`). Open-in-tab renders the anchor "Open page in a new
  tab ↗" with `target="_blank"` (lines 470-498).
- The placeholder branches (no tab, no selection, checking, error, missing) come before the
  embed/link branch, so they show in either mode.

`phase-wbf-01` is `queued`, so no header change has landed since 2026-10-08 and the entry needed no
re-read against a changed header.

## Ladder mismatch (recorded, not resolved)

- The control's label says "rung 3". `PLAN-021` (`docs/01-plans/PLAN-021-live-demo.md`) rung 3 is
  "Embedded overview panel becomes an open-in-tab link", which matches the control.
- The runbook's own Descope Ladder (`docs/00-working/demo-runbook.md` line 17) lists the same
  fallback as rung 7.
- The runbook entry names both numbers and states the mismatch. Which numbering the owner wants, and
  whether the label should change, is the owner's decision.

## Verification (run in the worktree)

- `grep -n "Open-in-tab" docs/00-working/demo-runbook.md` printed two lines: line 254 (the HTML
  Viewer entry, the existing list item) and line 256 (the new toggle paragraph inside that entry).
- `uv run python -m src.governance` exit 0: `Governance OK: 45 systems, 459 documents, 37 memories, 354 backlog phases`.
- `uv run pytest -q -x test/test_governance*.py test/test_codes.py`: `106 passed, 1 warning in 31.25s`.
- `uv run ruff check src/ test/ tools/`: `All checks passed!`.
- The pre-commit hook ran on the runbook commit and passed (`check_no_private_content: OK`).

## Not done, and why

- Not run: the full `uv run pytest`, `uv run mypy src/` and `cd ts && npm test`. The dispatch named
  the governance tests, ruff and the governance check as sufficient for a documentation-only change,
  and `ts/` was not touched. Full pytest and mypy were not run against this branch.
- Not done: `REQ-012` R31 asks for the toggle to be clicked in a running viewer. No browser or dev
  server was used, per the dispatch. The acceptance condition for the phase, checked by reading the
  labels and link text in the code, is met. The R31 click check remains for a person to run.

## Assumptions

- The reset-on-reload behaviour is read from the code. It was not observed in a running viewer.
- The runbook entry describes the toggle but does not recommend a rung number. Both numbers appear
  as they stand.

## Awaiting ratification

- Which ladder numbering is correct, and whether the control's label should match the runbook's
  ladder. The idea offered two options: document the toggle (done here) or hide it behind the demo
  flag. The second was not chosen and stays with the owner.
- Idea `000105` status is not changed here. Its status is the owner's to move.

## Attribution

The phase contract named the co-author as Claude Fable 5.1. The commit carries Claude Haiku 5.5,
the model that did the work, per the session's attribution instruction. This is a mismatch to
confirm with the Session Manager.
