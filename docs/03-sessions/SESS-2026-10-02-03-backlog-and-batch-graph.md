---
schema_version: 1
id: doc-session-backlog-and-batch-graph
code: SESS-2026-10-02-03
title: Backlog and batch graph page
kind: session
status: active
owner: repository-owner
created: '2026-10-02'
updated: '2026-10-02'
systems: [sys-html]
depends_on: [doc-html-generation-design-system]
---

# Backlog and batch graph page

## Phase

`phase-des-12`: build the backlog and batch graph page.

## Verification

Run in the worktree after the rebase onto `dev` `82c17e4`, at `80779a1`.

```text
$ uv run pytest
1320 passed, 1 warning in 311.12s (0:05:11)
$ uv run python -m src.governance
Governance OK: 43 systems, 421 documents, 34 memories, 347 backlog phases
$ uv run python -m src.governance --check-ideas
Idea field check: 100 phases name 168 ideas; 0 phases differ (0 missing, 0 extra)
$ uv run python tools/check_no_private_content.py
check_no_private_content: OK (1130 tracked files, 0 identifiers checked)
$ uv run ruff check src/ test/
All checks passed!
$ uv run mypy src/
Success: no issues found in 47 source files
```

The worktree has no `_private/portfolio/`, so the check above loads 0 identifiers. Every tracked
file in the worktree, `_public/engine/backlog.html` included, was scanned with the primary
checkout's identifiers through the check's own `confidential_identifiers()` and `check_content()`:
31 identifiers over 1130 tracked files, 0 hits.

## Acceptance

- REQ-036 R21 holds — **Met.** `test_every_phase_appears_once_with_the_governance_state` compares
  every row's state with `src.governance.backlog.readiness`, called by the test itself, and
  `test_state_counts_sum_to_every_phase` checks the counts. The page shows 347 phases: active 2,
  ready 80, waiting 109, blocked 1, deferred 17, complete 137, cancelled 1.
- REQ-036 R22 holds — **Met.** `test_each_batch_matches_its_yaml` compares each of the seven batch
  tables' stages and phases, in order, with its YAML, and checks every phase and listed external
  dependency is drawn. `test_every_in_graph_dependency_is_drawn_as_an_edge` checks the edges: 54
  across the seven graphs. `test_the_graphs_are_static_svg` checks the graphs are inline SVG with
  no script and no event handler. The page was loaded in headless Chrome with
  `--disable-javascript`: `--dump-dom` shows all 7 graphs and 54 edges, and screenshots show the
  graphs rendered and legible in light mode (whole page) and dark mode (`batch-005`, the largest).
- REQ-036 R23 holds — **Met.** `test_every_waiting_phase_lists_its_unmet_dependencies` checks all
  109 waiting phases list exactly their non-complete dependencies with each one's state.
  `test_every_blocked_or_deferred_phase_shows_both_fields` checks the 18 blocked or deferred
  phases. `test_a_missing_field_reads_not_recorded` covers a phase missing a field.
- REQ-036 R07 to R13 still hold — **Met.** The determinism, stamp, committed-page, colour-literal,
  house-family, fold-only and no-script tests run over all three pages and pass. R13 passes on the
  scan above.

## Backlog

`phase-des-12`: `status: active`, `agent: agent-standby-3`, `session: doc-session-backlog-and-batch-graph`.

## Review

Independent review by a fresh `demo-adversary` sub-agent over `d40d4f5..2d88bff`. It ran the
verification commands in the worktree (`1319 passed`; governance, ruff and mypy clean; the
primary-identifier scan, 31 identifiers, 0 hits) and reported, condition by condition:

1. **R21 — Met.** A standalone recount gave the same seven state counts and 347 phases. The test
   calls the same `readiness()` the generator calls, as R21's method and the phase scope require,
   so it cannot catch a bug inside `readiness()` itself.
2. **R22 — Met.** No edge is dropped: every dependency target of a member is drawn. Marker ids are
   per batch, so seven inline graphs do not collide. Every CSS variable the graph uses is defined in
   both modes of `house.css`. Per-table edge counts 1, 6, 0, 8, 4, 12, 23 sum to 54. It loaded the
   page with JavaScript disabled through `--dump-dom`.
3. **R23 — Met.** No `depends_on` id in the backlog is dangling.
4. **R07-R13 — Met** over all three pages.

Containment: every changed file is a declared deliverable or the session record, the phase's own
`session` field, and the regenerated catalog. All figures in this record reproduced.

Findings: no blockers, no majors.

- **Minor:** the generator docstring and `OPS-028` do not name the batch tables as an input.
  **Accepted** as out of scope: `OPS-028` is not a deliverable of this phase. Recorded as idea
  `000554`.
- **Note:** the branch that draws an arrow between boxes in one column has no live data to exercise
  it. **Accepted:** no batch table has such an edge today.
- **Note:** `batch-007` (sequence 5) is listed before `batch-005` (sequence 6). **Accepted:** the
  page orders by sequence, as intended.

After the review, the script-disabled screenshots showed arrows that skip a stage striking through
the phase ids of the boxes between them. Fixed in `ba68dca`: arrows are drawn before boxes, and
`test_arrows_are_drawn_beneath_the_boxes` checks it. Such an arrow now passes behind the boxes in
between, so in `batch-005` an arrow to stage 3 or 4 can look as if it leaves a stage 2 box. The
text is legible; the routing is left as it is.

## Decisions

Owner rulings in this session, 2026-10-02, given through AskUserQuestion:

- The claim, for `agent-standby-3`, granted by the Session Manager (claim commit `d40d4f5`).
- The layout: one graph per batch table, plus a table of every phase with its state. The page
  states the choice. 347 phases with 270 edges among the 209 unfinished ones do not fit one legible
  graph; the seven batch tables hold 1 to 7 phases each.

Agent's own choices:

- A graph's columns are its stages in order, with an "External" column first. External holds the
  table's `external_depends_on` plus any other `depends_on` target of a member, so no edge is
  dropped. An external dependency the table does not list reads "not listed in the table".
- Every arrow is one backlog `depends_on` edge, not the table's `after` field, because the phase
  scope says to draw `depends_on`.
- A cancelled phase shows its `blocked_reason` and `resume_when` the same way, and a missing field
  reads "not recorded" (R11).
- Graph colours are CSS rules over house tokens, added to the page's inline styles, so the
  colour-literal test covers the SVG too.

## Corrections

- The first full run gave `3 failed, 1316 passed`: `test_committed_catalog_matches_regenerated_output`,
  `test_catalog_flag_writes_committed_file` and `test_ideas_priority_yaml_is_governance_clean`, all
  "catalog.md differs from the rendered catalog". This record was on disk but not yet committed, and
  the catalog had not been regenerated for it. Fixed by committing the record with the regenerated
  catalog in `21982bc`; the run above is after that.
- The first edge test failed because `data-edge` carried a raw `>`. The generator now escapes the
  whole attribute value.

## Unresolved

- `OPS-028` still says one page exists and names R07-R14, and the generator's docstring does not
  mention the batch tables as an input. `OPS-028`'s reference section is generated from that
  docstring, and `OPS-028` is outside this phase's deliverables, so neither was changed. Recorded as
  idea `000554`.
