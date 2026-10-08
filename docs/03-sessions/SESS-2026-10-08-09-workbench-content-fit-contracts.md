---
schema_version: 1
id: doc-session-workbench-content-fit-contracts
code: SESS-2026-10-08-09
title: Workbench content-fit contracts and their mechanised check (phase-arch-05)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-layout, sys-wb-styles, sys-wb-shared]
depends_on: [doc-workbench-content-fit-contracts-requirements, doc-workbench-architecture-quality-requirements]
---

# Workbench content-fit contracts and their mechanised check (phase-arch-05)

## Phase

`phase-arch-05` (per-panel content-fit contracts and their mechanised checks), claimed by
`agent-batch-runner` (Session 5 - Batch Runner) under the Session Manager's `ASSIGN`, run
2026-10-08. Worked in `/home/user/d-system-worktrees/phase-arch-05` on `agent/phase-arch-05`, cut from
the run's integration branch `ccr-b69b05b4-tdcrux`, which stands in for `dev`. Dev servers on API
port 8013 and Vite port 5183, both stopped at the end.

## What changed

- `docs/06-requirements/REQ-037-workbench-content-fit-contracts.md` (new requirement): the mode
  vocabulary, ten observable rows (`C01`-`C10`), the panel contract table (nine registered panel
  types, 45 region rows), the floating surface contract table (popover, tooltip, file-tree context
  menu), a mapping of the five known instances to rules, the discovery method, the measured state and
  the boundaries. The two tables are what the test parses.
- `test/test_workbench_fit_contracts.py` (new): 31 pytest tests (static half) and a live runner
  (`--live <url> [--self-test] [--quick] [--layout] [--panel] [--dump]`) that drives Chromium through
  Playwright for Node.
- `docs/08-governance/catalog.md`: regenerated.
- `docs/09-backlog/backlog.yaml`: this phase's `session`, `completion_evidence` and `result` only.

REQ-011 was not edited. R09 says "read the contract document"; REQ-037 declares `depends_on` on
REQ-011 and says it is that document.

## Evidence

- Static half: `uv run pytest test/test_workbench_fit_contracts.py` passes 31 tests.
  `test_undeclared_panel_fails_and_is_named` adds a fake panel type to a copy of the registry source
  and removes `file-browser`'s rows from the parsed table, and requires an `AssertionError` that
  names `fake-panel` and `file-browser` (REQ-011 R10).
  `test_registry_parser_sees_added_and_removed_types` adds, removes and obscures a registry key and
  requires the three-way count check to trip (`C03`).
- Live half, full matrix (100 panel cells, 132 floating-surface measurements, 2 layouts, 9 panel
  types, every eligible slot, four sizes), final run:
  `rules pass=489 fail=35 n/a=0; scroll regions exercised in 7 of 7 pairs; 43 finding(s)`, exit 1.
  The findings, all real, are tabulated in REQ-037 "Measured state": the rotator tooltip cut by the
  notes strip (instance 3) and the popover height floor (instance 4) both reproduce; the notes strip
  entry is not bounded by its strip in layout 1; the notes strip dropdown trigger overruns the strip
  by 1-6 px; and the terminal, HTML Viewer and File Browser headers do not wrap in narrow slots.
  Instances 1 (height collapse) and 2 (File Browser clip) do not reproduce.
- Self-test: one violation injected per panel type; the judge named the broken region for all nine
  (eight at layout 1, `overview`, which only layout 2 can show, at layout 2).
- Panel root gap to slot body was at most 19 px on both axes in every cell, inside the 24 px
  tolerance; the smallest measured region heights were 57 (tree), 93 (tables), 84 (xterm), 83
  (viewer page area and frame) and 150 (overview frame).

## Verification and gate results

| Command | Result |
|---|---|
| `uv run pytest` | 1 failed, 1692 passed, 1 skipped. The failure is `test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused` (`DID NOT RAISE Refused`): the session runs as uid 0, which can write to a directory with mode 0555, so the test's premise does not hold here. It does not touch this phase's files; it was not run on the base commit. |
| `cd ts && npm run build` | built in 1.73s (chunk-size warning only) |
| `uv run python -m src.governance` | `Governance OK: 45 systems, 460 documents, 37 memories, 354 backlog phases`, plus three non-blocking dev-relative status-regression warnings on `phase-wbf-04`, `-07`, `-18`, none mine |
| `uv run ruff check src/ test/ tools/` | `All checks passed!` |
| `uv run mypy src/` | `Success: no issues found in 50 source files` |
| `cd ts && npm test` | 3 files, 10 tests passed |

## Acceptance

- REQ-011 R09, one contract per shipped panel type and the suite fails when a panel is given content
  violating its own contract: met for the first half (nine types, `C01`) and for the second as
  `--self-test` plus the judge's unit tests; the second half is a command, not part of
  `uv run pytest` (see below).
- REQ-011 R10, an undeclared panel fails a check and is named by it: met
  (`test_undeclared_panel_fails_and_is_named`, in `uv run pytest`).

## Assumptions and decisions

- **New requirement document rather than rows in REQ-011.** REQ-011 is the programme document and
  its rows are programme-level; per-region contract rows belong in a document that other phases
  amend as their panels change. Assumed, not asked.
- **Live half is a command, not a pytest test.** Playwright is not a Python dependency and `uv.lock`
  and `pyproject.toml` are outside this phase's deliverables. A pytest test that skipped without a
  browser would pass vacuously. Whether to add Playwright to the dev dependencies and start both
  servers from a fixture is a decision for the owner.
- **Discovery by parsing `panelRegistry.tsx`**, not a generated manifest; the vacuity guards are in
  REQ-037 "How panel types are discovered".
- **Numeric floors and tolerances** (48, 80, 68, 60 px; 24 px and 32 px fill tolerances; 15% popover
  starvation tolerance) are my judgment, set below measured values; REQ-037 says so.
- **The live command exits 1 today** because the defects it found are real and unfixed. I did not
  weaken a rule to make it pass.
- **Commit trailer.** The contract names `Claude Fable 5.1` in the trailer; the harness's attribution
  reminder names `Claude Sonnet 5.5`, which is the model that did the work, so the commit uses that.

## Awaiting ratification

None: no ADR was written and no decision was recorded as binding. The three choices above are
the owner's to overturn.

## Unresolved

- The live check is not in the pytest gate (see above).
- The CMD and PowerShell panels' fit and scrollback are owner-machine checks: on Linux they mount an
  xterm showing "is not available on this host", so their scrollback was not exercised. Not run.
- Four findings belong to no queued phase: the notes strip dropdown trigger overrun and the three
  header-wrap findings (terminal, HTML Viewer, File Browser). They are in the final report's `IDEA`
  lines for Ideation to record; this session did not record them.
