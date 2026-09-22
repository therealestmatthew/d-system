---
schema_version: 1
id: doc-literature-review-report-requirements
code: REQ-027
title: Literature-review campaign report page requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-20'
updated: '2026-09-22'
systems: [sys-html, sys-research]
depends_on: [doc-lit-campaign, doc-html-generation-design-system-requirements]
---

# Literature-review campaign report page requirements

Observable requirements for a generated, navigable HTML report over the adversarial D-System
literature-review campaign ([PLAN-023](../01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md)),
built by [PLAN-043](../01-plans/PLAN-043-literature-review-report-page.md).

The campaign ran nine sessions and produced fourteen files that exist only as Markdown and CSV in
`research/literature-review/`. Nothing renders them. The owner directed a **full navigable campaign
report** on 2026-09-20: every deliverable rendered and cross-linked, plus the ledger and matrix as
browsable tables.

## What exists, measured

```
$ python3 - <<'PY'  # row/column counts
ledger     rows= 1200 cols=15
inventory  rows= 1154 cols=13
matrix     rows=   67 cols=43
PY

$ du -ch research/literature-review/*.md | tail -1
752K	total
$ du -ch research/literature-review/*.csv | tail -1
2.7M	total
```

Fourteen files: `00_search_ledger.csv` plus `01`–`13`. The four largest Markdown deliverables are
`05_critical_collisions.md` (1,972 lines, 30 collision sections), `06_hypothesis_tests.md` (1,583
lines, 11 hypothesis blocks), `01_terminology_map.md` (1,305 lines) and `02_domain_map.md` (1,026
lines).

## Scope boundary

`phase-des-*` supplies page assets and states that whether a given report page exists is a ruling,
not an asset decision. The specific ruling it points at (`phase-idg-08`) governs the
ideas-and-backlog page from idea `000042`, a different page. **This page's existence is the owner's
direct 2026-09-20 direction**, recorded here rather than inferred from that boundary.

This document does not amend `REQ-021` and does not disposition any `phase-html-*` phase.

## R01 — Every deliverable is reachable

The generated report reaches all fourteen files. From the entry page, each of `01`–`13` is
reachable in at most two clicks, and the ledger is reachable directly.

**Verification**: parse the generated HTML; assert fourteen distinct deliverable targets exist, and
that the set of rendered deliverable ids equals the set of files matching
`research/literature-review/[0-9][0-9]_*` on disk. A file added to that directory and not reachable
fails this requirement.

## R02 — Markdown deliverables render as structured HTML

Headings, ordered and unordered lists, tables, fenced code blocks, inline code, blockquotes and
links each render as the corresponding HTML element rather than as literal Markdown text.

**Verification**: for each of the **eleven Markdown deliverables** — `01`–`13` excluding
`03_source_inventory.csv` and `04_evidence_matrix.csv`, which R03 covers as browsable tables —
assert the rendered output contains no line beginning with `## ` or `- ` outside a `<pre>` block,
and that every Markdown table in the source produced a `<table>`. Count `<h2>` elements against
`^## ` occurrences in the source and assert equality.

The range `01`–`13` names thirteen files, but only eleven of them are Markdown. The assertions
above have no meaning against a CSV, which carries no headings and no Markdown tables. R01's and
R03's uses of the same range are unaffected: R01 counts reachability across all fourteen
deliverables, CSVs included, and R03 covers the three CSVs directly.

## R03 — The three CSVs are browsable tables

The ledger (1,200 × 15), the inventory (1,154 × 13) and the matrix (67 × 43) each render as a table
the reader can **sort by any column** and **filter by free text**. The matrix, at 43 columns,
additionally supports choosing which columns are visible, with a default subset that fits a 1280px
viewport without horizontal scrolling of the page itself.

**Verification**: browser-driven. Sort a named column ascending and descending and assert row order
changes and row count does not. Type a term present in exactly *n* rows and assert *n* rows remain.
Toggle a matrix column off and assert its cells are gone and the page body still does not scroll
horizontally. Row counts rendered must equal the CSV row counts above.

## R04 — Cross-references resolve as links

A `source_id` named in a deliverable links to that source's inventory and matrix rows. A hypothesis
id (`H1`–`H11`) named anywhere links to its block in `06`. A deliverable that cites another
deliverable by number links to it.

**Verification**: extract every `source_id`-shaped and `H<n>`-shaped token from the rendered pages;
assert each either resolves to an existing in-page anchor or is explicitly listed as a known
non-target. Assert zero dangling internal links across the whole report.

## R05 — Generated and deterministic, never hand-authored

The report is produced by a tool under `tools/`, from the files in `research/literature-review/`.
Running it twice against an unchanged repository produces byte-identical output. No figure on the
page is computed by the renderer: counts come from the source files.

**Verification**: run the generator twice, `diff` the outputs, assert empty. Assert the generator
consults no wall clock in its output path (the `generate_overview.py` precedent: any generated-at
label derives from source data, not `datetime.now()`). A committed-output drift test in `test/`
fails when the checked-in page does not match a fresh regeneration.

## R06 — The campaign's epistemic posture is stated, not softened

The report states on its entry page that this is a **first research memo, not a final novelty
claim**, and that **saturation was measured and explicitly not demonstrated** — the falling
duplicate rate (20.0% → 15.0% → 6.4–7.7%) shown as the trend it is. No page asserts the saturation
stop condition holds, and no page contains the verdict `NOVEL`.

This is not presentation preference. `PROMPT-031`'s check-in ruling 8 forbids asserting saturation,
ruling 9 makes measured-not-demonstrated the closing posture, and `PROMPT-030` forbids any
close-out claiming final novelty. A report that renders the deliverables faithfully but drops their
hedging misrepresents the campaign.

### Where the duplicate-rate figures come from

The first two points, **20.0%** and **15.0%**, appear verbatim in five campaign deliverables. The
third, **6.4–7.7%**, does **not** appear anywhere in `research/literature-review/` — it is recorded
only in the campaign's session records, [`SESS-2026-09-19-08`](../03-sessions/SESS-2026-09-19-08-literature-review-pass-3c.md)
and [`SESS-2026-09-20-02`](../03-sessions/SESS-2026-09-20-02-literature-review-pass-4-close.md),
which sit outside the corpus the extractor reads.

This is a **stated exception to R05**, ruled by the owner on 2026-09-22. The trend is the
campaign's actual finding and R06's purpose depends on all three points, so the figure is kept
rather than dropped. The report carries it as a **cited literal** whose provenance is visible on
the page, and the extractor is not widened to read session records. Nothing on the page may present
this figure as measured from a deliverable.

**Verification**: assert the entry page contains the memo statement and the saturation statement.
Grep the full generated output for `NOVEL` and assert every occurrence sits inside a statement that
it is unavailable. Assert that **20.0%** and **15.0%** match the values in the source deliverables
rather than being recomputed, and that the page's **6.4–7.7%** is accompanied by a visible citation
naming the session records as its source.

## R07 — The disputed share of the evidence is visible

Where a critical collision's `second_review` is `disputed`, the rendered collision shows that, and
the report states the count: 18 of 30 standing flags are recorded `disputed`, and under check-in
ruling 1 no score or flag was changed. The reader must not be able to read the collision count as
30 settled findings.

**Verification**: assert the rendered collision list marks 18 rows disputed and 12 confirmed
against `04_evidence_matrix.csv`, and that the entry page carries the count.

## R08 — Self-contained and offline

The report opens from the filesystem with no network access and no build step. All CSS and
JavaScript are local; no CDN, no remote font, no external image.

**Verification**: grep the generated output for `http://` and `https://` in `src`, `href` on
stylesheets, and fetch targets; assert none point off-origin except citation links in deliverable
prose, which are content. Open the page with the network disabled and assert R03's interactions
still work.

## R09 — Design-system conformance

The report uses the existing template and style families under `templates/html/` and
`templates/styles/` rather than introducing a parallel look, and is legible in both light and dark
rendering.

**Verification**: assert the generated page references a stylesheet under `templates/styles/`.
Browser-driven contrast check on body text and table text in both schemes.

## R10 — The large tables stay usable

The 1,200-row ledger renders and remains interactive: sorting or filtering it completes without the
page becoming unresponsive.

**Verification**: browser-driven. Measure time from a filter keystroke to updated rows on the
ledger table; assert under 500ms on the development machine. Assert the page does not load all
three CSVs eagerly if that is what it takes to meet the bound — the mechanism is the build's
choice, the bound is the requirement.

## R11 — The gates pass

`uv run python -m src.governance` exits 0. `uv run python tools/check_no_private_content.py`
passes **with the changes staged and the real `_private/portfolio/` present**, so the content half
actually runs rather than being skipped.

**Verification**: the two commands, with real output recorded.

## Out of scope

- Amending any campaign deliverable. The report renders `research/literature-review/`; it never
  writes there.
- Re-running any campaign measurement. Figures are copied from the deliverables.
- Publishing anywhere outside `_public/`.
- The ideas-and-backlog page (`000042`), which is `phase-idg-08`'s ruling.
