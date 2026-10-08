---
schema_version: 1
id: doc-session-terminal-persistence-audit
code: SESS-2026-10-08-17
title: Terminal persistence and performance audit across three shells (phase-arch-16)
kind: session
status: active
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-wb-terminal, sys-demo-stage]
depends_on: [doc-workbench-architecture-quality-requirements, doc-workbench-terminal-decision]
---

# Terminal persistence and performance audit across three shells (phase-arch-16)

## Phase

`phase-arch-16` (terminal persistence and performance audit across three shells), a phase of
[`PLAN-028`](../01-plans/PLAN-028-workbench-architecture-quality.md), answering `REQ-011` R23 and R24
and building on idea `000107` (terminal session lost on layout switch when the stored visible panel
differs between layouts). Claimed by `agent-builder-b` (Session 2, Builder B) under the Session
Manager's pre-approved run of 2026-10-08. Worked in `/home/user/d-system-worktrees/phase-arch-16` on
`agent/phase-arch-16`, cut from the run's integration branch `ccr-b69b05b4-tdcrux`. The session code
`SESS-2026-10-08-17` was assigned by the Session Manager; `--next-code session` in this worktree
returned 14 at the start (taken on sibling branches) and 18 later.

## Awaiting ratification

Nothing in this phase is a decision record, but the audit makes judgments the owner has not seen:

- **D1.** Whether a shell ending on a visible-panel switch (finding F1) or on a layout switch with a
  differing stored panel (F2) is an intended outcome. The audit judges the ending a designed
  consequence and the missing warning a gap, by analogy with `REQ-007` W16. Not ruled.
- **D2.** "Re-assignment" in R23 means moving a panel with the configuration dialog; the slot-header
  switcher is a visible-panel switch.
- **D3.** Intent and communication for CMD and PowerShell are judged from documents and shared code
  and are labelled so; they are not observations of those shells.
- **D4.** Both the development server and a production build were measured.
- **D5.** The 300-second idle close is reported although it is not one of the five events.

## Outcome

One working document, [`docs/00-working/terminal-persistence-audit.md`](../00-working/terminal-persistence-audit.md)
(ungoverned, `ADR-010`), containing:

- The three-shell by five-event matrix, one table per shell, each cell with survival, intent and
  communication. The bash cells are measured on Linux; the CMD and PowerShell survival cells say
  "owner-machine, not run" and point to a numbered procedure.
- The five measurements for bash on Linux, with commands and numbers: connect latency, echo latency,
  resize behavior, scrollback handling, behavior at the six-session cap.
- Twelve findings (F1 to F12), an explicit list of ten owner-machine checks (O1 to O10) with what to
  do and what to look for and a result sheet, and a list of what was not covered.
- The standalone measurement script and the in-page recorder, so the numbers can be reproduced.

Headline results (all bash, Linux, loopback):

| Event or measure | Result |
|---|---|
| Layout switch, same shell shown in both layouts | survives (same pid and marker, 0 new websockets in the production build) |
| Layout switch, destination layout's stored visible panel differs | ends, no message (the residual of `000107`) |
| Visible-panel switch | ends every tab (3 to 0 server sessions), no message |
| Re-assignment | moved panel survives; the displaced panel ends after a stated confirmation |
| Collapse / drop / restore | collapse survives; drop ends all after confirmation; restore starts as many fresh sessions as there were tabs |
| Page reload | ends all, no notice; layout and panel choices persist |
| Connect latency | socket open 3.2 ms and prompt 17.5 ms median direct; new tab in the page 35 ms (production) or 61 ms (development) |
| Echo latency | 1.8 ms median at the socket; 28 ms keydown to rendered text in the page |
| Resize | pty size equals the xterm grid at 8 of 8 layout and size combinations; 40 resize frames for 41 viewport steps; shell sees the new size 33 to 40 ms after a viewport change |
| Scrollback | 1000 lines on the client (xterm default), 256 KiB ring on the server for the API only |
| Six-session cap | 7th refused in 6.6 ms with code 4001 and the server's reason; in the development server 2 of 4 new tabs were refused at five live sessions (production build: 0 of 4) |
| Idle | a session with no keystrokes is closed by the server at 300.0 s with code 1006 |

Nothing under `src/`, `ts/` or `test/` was changed.

## Evidence

Verification commands from the phase entry, run in the worktree:

- `uv run python -m src.governance`: `Governance OK: 45 systems, 471 documents, 37 memories, 354
  backlog phases` (the final run is in the gate table below).
- `uv run pytest`: see the gate table below.

Measurement evidence is inside the audit document, with the step list for every event. Servers
(backend on 8029, frontend on 5199) were started for the measurements and stopped before finishing,
each by `kill <pid>` of its own pid.

### Gate results

| Command | Result |
|---|---|
| `uv run python -m src.governance` | `Governance OK: 45 systems, 472 documents, 37 memories, 354 backlog phases` (plus the non-blocking dev-relative warning that `phase-wbf-15` is `complete` on the trunk and `active` here, which is not this phase's) |
| `uv run pytest` | `1 failed, 2063 passed, 1 skipped, 1 warning in 378.18s`. The one failure is `test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused`, the known environment failure when the suite runs as root (idea `000604`): recorded, not retried, not skipped |
| `uv run ruff check src/ test/ tools/` | `All checks passed!` |
| `uv run mypy src/` | `Success: no issues found in 52 source files` |
| `cd ts && npm test` | `Tests  108 passed (108)` (run although nothing under `ts/` changed, because `ts/node_modules` is present) |

An earlier full `uv run pytest` run, made before this record and the regenerated catalog were in
place, also failed `test/test_ideas.py::test_ideas_priority_yaml_is_governance_clean` with "catalog.md:
differs from the rendered catalog". That was the stale catalog; it passed after
`uv run python -m src.governance --catalog`. An earlier run with `-x` stopped at the known failure
after 1555 passed and was not a full run.

## Acceptance

- **`REQ-011` R23 (three-shell by five-event matrix with survival, intent and communication in every
  cell): met in the form the requirement's own note allows.** All fifteen cells carry the three
  parts. The ten CMD and PowerShell survival entries are not results: each says "owner-machine, not
  run" and names the procedure (O1 to O5). Their intent entries are judged from documents and their
  communication entries are code reading, both labelled. `REQ-011` states that R23 and R24 cannot be
  fully verified on Linux.
- **`REQ-011` R24 (five measurements reported, owner-machine checks listed explicitly): met.** The
  five measurements are reported for bash with commands and numbers; O6 to O10 list the same five
  for CMD and PowerShell; section 8 of the audit is the explicit list. No CMD or PowerShell figure is
  claimed.

## Not run

- Anything on Windows: CMD and PowerShell results for all five events and all five measurements.
- macOS.
- A session surviving a backend restart; unprovoked drops other than the 300-second idle close.

## Assumptions

- The `nohup` launch of the first backend made shells ignore `SIGHUP`, which made the first reload
  experiment wrong. It was detected from `/proc/<pid>/status`, the result discarded, and the
  experiment re-run under `setsid -f`. Every other experiment does not depend on `SIGHUP`
  (server-side session list and pid comparison).
- Event experiments were run on both builds; the development server's doubled mount changes
  websocket counts and cap behavior, so both are reported where they differ (D4).
- The three throughput runs and the small samples (n=3 for new-tab connect, n=6 for switcher and
  layout timings, n=1 for reload at the cap) are stated as such in the audit. They show an order of
  magnitude and an ordering, not a distribution.
- The `StrictMode` explanation of the false refusals at five live sessions is inferred from the
  doubled mount and the 0 of 4 production-build result; the ordering of the server's slot release
  and the second socket's arrival was not traced.
- The audit baseline is the shipped `schema_version` 3 build. `ADR-031` (proposed) changes panel
  identity; the matrix should be re-run after `phase-arch-08`.

## Unresolved

- D1 to D5 above.
- The twelve findings are not recorded as ideas by this session; the Session Manager's final report
  carries them as `IDEA` lines for the idea log.
- The audit's Playwright scripts are not committed (the phase's only deliverable is the document).
  A committed regression test for the matrix is an idea, not part of this phase.

## Review

No independent review has run on this record. Review is dispatched by the Session Manager.
