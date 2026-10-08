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
- `test/test_workbench_fit_contracts.py` (new): 50 pytest tests (static half, after review fixes) and a live runner
  (`--live <url> [--self-test] [--quick] [--layout] [--panel] [--dump]`) that drives Chromium through
  Playwright for Node.
- `docs/08-governance/catalog.md`: regenerated.
- `docs/09-backlog/backlog.yaml`: this phase's `session`, `completion_evidence` and `result` only.

REQ-011 was not edited. R09 says "read the contract document"; REQ-037 declares `depends_on` on
REQ-011 and says it is that document.

## Evidence

- Static half: `uv run pytest test/test_workbench_fit_contracts.py` passes 50 tests (31 at the first handoff).
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
- Self-test (differential, after the review fixes): see "Review" below; all nine panel types caught
  with an unbroken baseline that passed.
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
  browser would pass vacuously. The Session Manager ruled, under the owner's pre-approval, that
  `R09`'s "suite" closes for this phase on the documented `--live` command. That ruling is proposed,
  **awaiting the owner's ratification (pre-approved run, 2026-10-08)**; it is recorded in REQ-037
  "Boundaries and unresolved". Gating the command (Playwright as a dev dependency plus a server
  fixture, or a CI job) remains a follow-up idea.
- **Discovery by parsing `panelRegistry.tsx`**, not a generated manifest; the vacuity guards are in
  REQ-037 "How panel types are discovered".
- **Numeric floors and tolerances** (48, 80, 68, 60 px; 24 px and 32 px fill tolerances; 15% popover
  starvation tolerance) are my judgment, set below measured values; REQ-037 says so.
- **The live command exits 1 today** because the defects it found are real and unfixed. I did not
  weaken a rule to make it pass.
- **Commit trailer.** The contract names `Claude Fable 5.1` in the trailer; the harness's attribution
  reminder names `Claude Sonnet 5.5`, which is the model that did the work, so the commit uses that.

## Awaiting ratification

- `R09`'s "suite" closing on the documented `--live` command for this phase: awaiting the owner's
  ratification (pre-approved run, 2026-10-08).

No ADR was written. The other choices above are the owner's to overturn.

## Unresolved

- The live check is not in the pytest gate (see above).
- The CMD and PowerShell panels' fit and scrollback are owner-machine checks: on Linux they mount an
  xterm showing "is not available on this host", so their scrollback was not exercised. Not run.
- Four findings belong to no queued phase: the notes strip dropdown trigger overrun and the three
  header-wrap findings (terminal, HTML Viewer, File Browser). They are in the final report's `IDEA`
  lines for Ideation to record; this session did not record them.

## Review

Verdict records, copied unchanged into `docs/08-governance/reviews/verdicts/`:
`2026-10-08-phase-arch-05-demo-adversary.json` (gating, pass with 3 major and 5 minor) and
`2026-10-08-phase-arch-05-review-judge.json` (shadow, non-gating, reject with 2 major and 4 minor).

| Finding | Disposition |
|---|---|
| ADV F01 / JUDGE F03 (major): the notes strip entry passes a bounded clip | Fixed. `marquee` now needs a box of at least 16x16, no vertical overflow and, when content is wider than the box, measured motion (a running horizontal-motion animation, or a transform or scroll offset that differs between two samples 350 ms apart). `scroll-x` and `scroll-y` fail when the other axis is clipped. Marquee subtrees are exempt from `silent-clip` only in a cell where motion was measured. Judge tests: bounded clip (hidden, 90 px in a 20 px box) fails; a horizontal scroller that clips vertically fails; a non-moving marquee fails; a legal horizontal scroll and a legal animated marquee (animation, or changed transform) pass. |
| ADV F02 (major): C08 substring match misses a rename | Fixed. Classes are matched as whole tokens inside string literals of `.tsx` sources after comments are removed (small scanner, `scan_ts`). `test_renaming_a_class_in_source_is_detected` renames `stage-file-browser__tree` in a copy of the source text and requires the row reported stale. |
| ADV F03 / JUDGE F01 (major): no gate runs the live half | Ruled by the Session Manager: `R09`'s "suite" closes on the documented `--live` command for this phase. Recorded in REQ-037 "Boundaries and unresolved" and above, awaiting the owner's ratification (pre-approved run, 2026-10-08). The follow-up stays an idea. Evidence of real runs is below. |
| ADV F04 / JUDGE F02: the self-test is non-differential | Fixed. The self-test judges every candidate cell unbroken, picks per panel a cell and region that passed unbroken, and counts a break caught only when a finding appears on that region. A panel with no clean candidate prints `UNPROVEN` by name and fails the run. The notes strip is now proven on its help trigger, not the entry region that already fails. REQ-037's self-test claims were rewritten to match. |
| ADV F05: parser bypassed by non-literal registration | Fixed. Lines at the literal's indent must open a `key: {` entry (a spread or call is refused), and any other assignment to `PANEL_REGISTRY` (subscript, property, `Object.assign`, `defineProperty`) is refused. Tests cover the factory-call, spread, subscript, `Object.assign` and property probes, plus a check that comments and reads are not mistaken for mutations. |
| ADV F06: C02 overstated its test | Fixed so C02 is true. `test_undeclared_panel_fails_and_is_named` now builds the fake type in a mutated copy of `REGISTRY_SOURCE`, reads it back through `checked_panel_types`, and asserts the failure names it. |
| ADV F07 / JUDGE F05: mypy errors and a dead docstring | Fixed. The reused `key` is renamed, the bool is cast, the docstring moved. `uv run mypy test/test_workbench_fit_contracts.py` reports `Success: no issues found in 1 source file`. |
| ADV F08: no minimum size on scroll, marquee, visible, wrap | Fixed. Default floor 16 px (a scrollbar track 4 px wide by 16 high), overridable with `min-h` and `min-w`, and `wrap` now fails when the wrapped header is taller than, or ends below, its panel. Judge tests for each. The live run raised no new finding from these checks. |
| JUDGE F04: the fill test iterated the contract | Fixed. It iterates `checked_panel_types(REGISTRY_SOURCE)`. |
| JUDGE F06: `uv run pytest` exits 1 on an unrelated test | Accepted, not mine. `test_an_unwritable_worktree_parent_is_refused` fails because the session runs as uid 0. Same disclosure as above. |

### Evidence after the review fixes

`uv run python test/test_workbench_fit_contracts.py --live http://localhost:5183 --quick` (API 8013,
Vite 5183, both stopped afterwards), tail:

```
50 panel cells; floating surfaces measured {'context-menu': 4, 'popover': 54, 'tooltip': 8}; rules pass=239 fail=28 n/a(optional region absent)=0; scroll regions exercised in 7 of 7 (panel, region) pairs; shell unavailable on this host, scrollback not exercised (owner-machine, C10): ['terminal-cmd', 'terminal-powershell']; 32 finding(s)
exit=1
```

`--live ... --self-test` (full matrix: 100 panel cells, 132 floating measurements,
`pass=489 fail=35`, 43 findings), self-test tail:

```
self-test terminal (layout-1@secondary): unbroken region passed, injected .stage-terminal-tabbar overflow:hidden: caught
self-test terminal-cmd (layout-1@secondary): unbroken region passed, injected .stage-terminal-tabbar overflow:hidden: caught
self-test terminal-powershell (layout-1@secondary): unbroken region passed, injected .stage-terminal-tabbar overflow:hidden: caught
self-test html-viewer (layout-1@secondary): unbroken region passed, injected .stage-html-viewer__tabbar overflow:hidden: caught
self-test notes-strip (layout-1@strip): unbroken region passed, injected .stage-tooltip__trigger moved out: caught
self-test file-browser (layout-1@explorer): unbroken region passed, injected .stage-file-browser__tree height:12px: caught
self-test idea-explorer (layout-1@explorer): unbroken region passed, injected .stage-explorer__table-wrap height:12px: caught
self-test backlog-explorer (layout-1@explorer): unbroken region passed, injected .stage-explorer__table-wrap height:12px: caught
self-test overview (layout-2@primary): unbroken region passed, injected .stage-overview__iframe moved out: caught
```
