---
schema_version: 1
id: doc-session-lit-report-tables
code: SESS-2026-10-05-05
title: The three browsable literature-review tables, including the 43-column matrix
kind: session
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-html]
depends_on: [doc-literature-review-report-page]
---

# The three browsable literature-review tables, including the 43-column matrix

## Phase

`phase-lrr-03`: The three browsable tables, including the 43-column matrix. It turns the
literature-review report's three CSV pages from `phase-lrr-02`'s placeholders into tables that
can be sorted and filtered, with column choice on the matrix (`REQ-027` R03, R08, R10;
`PLAN-043`). Run overnight on 2026-10-05 as Session 5 (Batch Runner, `agent-batch-runner`). The
Session Manager assigned it, and the owner pre-approved the assignment. Builder A had stalled on
it and released it.

## Verification

`uv run python -m src.governance`

```text
Governance OK: 45 systems, 442 documents, 37 memories, 347 backlog phases
```

`uv run pytest` (worktree, at `9db88f1`)

```text
1521 passed, 1 skipped, 1 warning
```

`uv run pytest -q test/test_lit_report_render.py`

```text
60 passed, 1 warning
```

`uv run ruff check src/ test/ tools/lit_report_render.py` and `uv run mypy src/`

```text
All checks passed!
Success: no issues found in 48 source files
```

`uv run python tools/generate_tool_docs.py --check`

```text
27 tool document(s) current
```

`REQ-027` R11 requires the private-content check to run with the real `_private/portfolio/`. The
worktree has none, so `tools/check_no_private_content.py`'s functions were run directly: the
identifiers came from the primary checkout's portfolio, and the check covered this worktree's
tracked and staged files.

```text
tracked+staged files: 1326 identifiers: 31 violations: 0
```

**Browser verification.** It was driven by the `demo-validator-web` agent. That agent had no
Playwright MCP tools here, so it used headless Chrome over the DevTools protocol, the fallback
the Session Manager named. Pages were rendered from `9db88f1` with `render_report(extract())`.
The validator computed its filter counts from the CSVs with Python's `csv` module, not from the
page, and typed them as real keystrokes.

| Check | Ledger | Inventory | Matrix |
|---|---|---|---|
| Rendered rows | 1200 | 1154 | 67 |
| Sorted column (ascending, then descending) | `date` | `year` | `component_overlap_score` (shown by default) |
| Row order changed both ways, row count unchanged | yes | yes | yes |
| Filter term, rows expected from the CSV, rows shown | `NELL`: 10, 10 | `dissertation`: 11, 11 | `QOC`: 5, 5 |

- Matrix column toggle: `architecture_overlap_score` turned off hid 67 of 67 cells. At 1280px
  the page body stayed at `scrollWidth` 1265 = `clientWidth` 1265, before and after.
- Default matrix subset (9 of 43 columns): no horizontal page scroll at 1280px or at 1920px.
- Ledger filter timing, from the page's own `performance.now()` span around the filter handler
  (owner ruling, 2026-09-30):
  - one keystroke on the full ledger: handler 0.50ms, to the next frame 35.10ms;
  - the final keystroke of `NELL`: handler 1.40ms, to the next frame 6.90ms;
  - the validator's own in-page measure, from keystroke to the changed row count: 37.4ms and
    12.6ms.

  All are under R10's 500ms, so the ledger rows were not virtualised.
- Machine: Intel Core i7-1185G7 @ 3.00GHz, 8 cores; Google Chrome 153.0.8010.36.
- Every table page made one request, the page's own `file://` URL, and logged no console error
  or exception. Only the three table pages contain `<script`; the 11 Markdown pages and
  `index.html` contain none.

The session's own earlier headless-Chrome run agreed: ledger handler 2-7ms, filter counts 100,
36 and 1 for other terms, and no page-body overflow at 700px or 1280px.

## Acceptance

- Sorting a named column ascending then descending changes row order and leaves row count
  unchanged, on all three tables: Met. See the validator's table above.
- Filtering by a term present in exactly n rows leaves exactly n rows, on all three tables: Met.
  The expected counts were computed from the CSVs, not from the page.
- Toggling a matrix column off removes its cells and the page body still does not scroll
  horizontally at 1280px: Met. 67 of 67 cells were hidden, and 1265 = 1265.
- Rendered row counts equal 1200, 1154 and 67, and a ledger filter keystroke updates rows in under
  500ms, measured and recorded: Met. The test
  `test_table_pages_render_every_row_and_column_of_the_extracted_table` checks the counts. The
  measurements and the machine are recorded above.

## Backlog

`status: active`, `agent: agent-batch-runner`. `next_action`: all acceptance met; reviewed and
browser-verified; awaiting the owner's merge approval through the Session Manager.
`completion_evidence`: the seven deliverables and this record.

## Unresolved

None. Both open items are settled by the owner's sign-off below.

## Owner sign-off, 2026-10-05

The phase was parked overnight for two decisions that only the owner can make. On the morning of
2026-10-05 the Session Manager relayed the owner's rulings, and the owner confirmed them directly in
this session. The question asked was: "For the literature-review tables (phase-lrr-03): do you sign
off the two retired placeholder tests (test_csv_pages_carry_the_phase_lrr_03_handoff_marker_and_md_pages_do_not,
test_csv_placeholder_counts_match_the_extracted_table) and accept {{INLINE_SCRIPT}} carrying the
whole <script> element?" The owner answered:

> "Yes to both"

- `tools/check_test_baseline.py`'s nonzero result is signed off for exactly these two tests:
  - `test.test_lit_report_render::test_csv_pages_carry_the_phase_lrr_03_handoff_marker_and_md_pages_do_not`
  - `test.test_lit_report_render::test_csv_placeholder_counts_match_the_extracted_table`
- `{{INLINE_SCRIPT}}` carrying the whole `<script>` element, empty on deliverable pages, is
  accepted as the reading of the 2026-09-30 ruling. The overnight assumption becomes the owner's
  decision.

The overnight baseline result, kept as evidence. The base is `8979a09`; the branch was at
`6ccce8f`.

```text
2 tests passed in the base and are missing or skipped in the branch:
  missing  test.test_lit_report_render::test_csv_pages_carry_the_phase_lrr_03_handoff_marker_and_md_pages_do_not
  missing  test.test_lit_report_render::test_csv_placeholder_counts_match_the_extracted_table
```

Both were removed on purpose. They asserted `phase-lrr-02`'s placeholder body, and their checks
carry over to `test_table_pages_render_every_row_and_column_of_the_extracted_table` and
`test_no_placeholder_body_remains_on_any_page`.

## Review

The reviewer was a fresh `demo-adversary` sub-agent. It reviewed `dev...HEAD` at `9db88f1` and
was given the phase's scope, acceptance, verification and deliverables, and no session record.
It ran out of turns once and was asked to report what it had established. Its findings, in
substance:

- All six scope bullets Met. All four acceptance conditions Met for the ledger and the matrix,
  which it drove in headless Chrome. It did not drive the inventory itself, relying on the shared
  code path and the unit tests; the validator's run covered it.
- Its live filter timing on the ledger was 19-24ms.
- No blocking or should-fix findings. It tried and failed to break:
  - escaping (cells holding `<script>`, `{{INLINE_SCRIPT}}`, `&`, quotes) — nothing executed,
    and cell `textContent` matched the CSV byte for byte through the `<wbr>` hints;
  - double substitution in `fill()`;
  - the `</script` guard;
  - Markdown-page tables, which still compute `display: block`;
  - containment — no undeclared changes;
  - R05 — the renderer computes no corpus figure.
- Note: hyphenated `source_id` values get no `<wbr>`, but `overflow-wrap: break-word` wraps them,
  and the page body does not scroll.
- Note: `{{INLINE_SCRIPT}}` carries the whole `<script>` element, while `{{INLINE_STYLES}}` sits
  inside a literal `<style>` tag. It judged this the only reading that leaves deliverable pages
  with no script tag at all, and asked for a one-line owner confirmation rather than calling it
  a defect.
- Not checked by it: tie-sort and numeric-detection edge cases beyond reading the code; the full
  suite, which the session ran.

No finding required a code change.

## Decisions

- OVERNIGHT ASSUMPTION: `{{INLINE_SCRIPT}}` carries the whole `<script>` element and is empty on
  deliverable pages, so those pages have no script tag. The alternative, a literal
  `<script>{{INLINE_SCRIPT}}</script>` in the shell, would leave an empty script element on every
  Markdown page. That would contradict the scope's "left empty on deliverable pages" and the
  page shell's former guarantee.
- OVERNIGHT ASSUMPTION: the matrix opens with its nine short columns showing: `source_id`,
  `source_type`, `research_domain`, `hypotheses_challenged`, both overlap scores,
  `critical_collision`, `interpretation_confidence` and `access_limitation`. The 34 prose
  columns start hidden. Neither the phase nor `REQ-027` names the set, and the Session Manager's
  scout recommended reading it from the CSV header. With these nine, the table fits its 977px box
  at 1280px with no scroll of its own.
- OVERNIGHT ASSUMPTION: the filter searches every column, hidden ones included, and cannot match
  across a cell boundary. A column sorts numerically when every non-empty cell is a number;
  empty cells sort last, and ties keep the CSV order.
- OVERNIGHT ASSUMPTION: the browser check used headless Chrome, because the validator agent had
  no Playwright MCP tools. The Session Manager named this fallback in advance.
- The rows are rendered server-side as HTML rather than shipped as JSON for script to build.
  The table reads without script, the row count is the extractor's by construction, and the
  ledger page is about 1.8MB.
- `_breakable()` adds `<wbr>` after `_` and `;` in headers and cells. Values such as `H2;H7;H9`
  and `preprint_version` otherwise held whole columns wide, and kept the matrix's default view
  wider than its box.
- In the narrow layout (720px or less), `.lr__main` gets full width. Without it, the stacked
  layout sized the main column to the whole table and the page body scrolled sideways. This was
  found during the session's own check at 700px.

## Corrections

- The first `_breakable()` escaped the text before inserting `<wbr>` after semicolons, which also
  split the semicolon closing an entity (`&lt;` became `&lt;<wbr>`). The existing escaping test
  caught it. The text is now split before it is escaped, and a test pins the entity cases.
- The first CSS used `overflow-wrap: anywhere` with a 4rem cell minimum. The browser then
  squeezed every ledger column toward 4rem and broke words mid-word. `break-word`, with a 5rem
  minimum, fixed it. Three further rounds (wrapping headers, `<wbr>` in cells, 0.45rem cell
  padding) brought the matrix's default view from 1331px to its 977px box.

## Left undone

Nothing in scope. Writing the pages to `_public/` and the drift test belong to `phase-lrr-04`.
