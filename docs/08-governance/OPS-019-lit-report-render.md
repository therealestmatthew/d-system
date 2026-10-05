---
schema_version: 1
id: doc-ops-lit-report-render
code: OPS-019
title: Render the literature-review campaign report's pages
kind: operation
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-10-05'
systems: [sys-research, sys-html]
depends_on: [doc-governance-operations, doc-literature-review-report-requirements]
---

# Render the literature-review campaign report's pages

## Trigger

Run when a later phase of [PLAN-043](../01-plans/PLAN-043-literature-review-report-page.md) needs
`tools/lit_report_extract.py`'s output turned into HTML — the generator that writes pages to
`_public/` (`phase-lrr-04`), which this module hands its fifteen-page mapping to.

This module is `OPS-017`'s sibling half of the render seam
[REQ-027](../06-requirements/REQ-027-literature-review-report-page.md) R05 requires: the extractor
measures the corpus, and this module turns that measurement into markup without opening
`research/literature-review/` itself. Every count on a rendered page traces back to
`data["counts"]` or to a `data["deliverables"]`/`data["tables"]` entry the extractor already
produced — this module computes none of them.

## Command

**There is no command.** `tools/lit_report_render.py` carries no `argparse` block and is never run
directly; it is a pure rendering library, imported by whichever tool assembles the report. It sits
under `tools/` because that is where it is consumed from — `tools/lit_report_extract.py`, which it
reads output from, and `tools/generate_lit_report.py`, which `phase-lrr-04` will build to write its
output to `_public/`. Writing pages to disk is that later phase's job, not this module's; this
module only turns `data` into strings in memory.

Import path and a worked example against the extractor's own output:

```python
from tools.lit_report_extract import extract
from tools.lit_report_render import render_report

data = extract()
pages = render_report(data)

pages.keys()
# {"index.html", "01_terminology_map.html", ..., "05_critical_collisions.html", ...}
# 15 entries: index.html plus one page per of the 14 deliverables

pages["index.html"][:15]
# "<!DOCTYPE html>"
```

## Expected result

`render_report(data)` returns a `dict[str, str]` — fifteen entries, `index.html` plus one page per
deliverable — mapping a relative output path (e.g. `"05_critical_collisions.html"`) to a complete
HTML document (full `<!DOCTYPE html>` through `</html>`, styles inlined, nothing to fetch). Nothing
is written to disk; that mapping **is** the seam between phases. The three CSV pages are
browsable tables (see "The three CSV deliverables" below); `phase-lrr-04` takes the mapping and
writes each value to its key under `_public/`.

### The public API

- **`render_markdown(text: str) -> str`** — one deliverable's Markdown source rendered to HTML
  through `MarkdownIt("commonmark").enable("table").enable("strikethrough")`, the combination
  verified against all eleven Markdown deliverables, `05` and `06`'s fenced-YAML hard cases
  (`evidence: >`-style YAML block scalars that must stay inside `<pre>`, not leak out as literal
  `- ` text) included.
- **`load_template(name: str) -> str`** — a template's text, by filename alone. A name ending in
  `.css` is read from `templates/styles/`, one ending in `.js` from `templates/scripts/`, and
  anything else from `templates/html/`. See "Behaviours" below for what each strips before
  returning.
- **`fill(template: str, tokens: dict[str, str]) -> str`** — plain `{{TOKEN}}` string substitution,
  strict in both directions. See "fill()'s contract" below.
- **`render_report(data: dict) -> dict[str, str]`** — the full fifteen-page mapping, described
  above. A pure function of `data` (from `tools.lit_report_extract.extract()`) and the on-disk
  `templates/html/lit-report-*.html`, `templates/styles/lit-report.css` and
  `templates/scripts/lit-report-table.js` family.

### The three CSV deliverables

`00_search_ledger.csv` (1,200 × 15), `03_source_inventory.csv` (1,154 × 13) and
`04_evidence_matrix.csv` (67 × 43) each render as a table view (`REQ-027` R03, `phase-lrr-03`).
`_render_table()` fills `templates/html/lit-report-table.html` with every row of the extractor's
`data["tables"][key]`, escaped and in CSV order, so each page carries its own data and nothing is
fetched (`PLAN-043`'s inlining decision; the ledger page is about 1.8MB). The shown figures are
`row_count` and `columns`, not a recount.

`templates/scripts/lit-report-table.js` is inlined into those three pages only, as a complete
`<script>` element in the page shell's `{{INLINE_SCRIPT}}` token; the token is empty on every
deliverable page and the entry page has no such token, so neither carries a script tag (owner
ruling, 2026-09-30). The script:

- sorts by any column from its header button, ascending then descending (`aria-sort` marks the
  state). A column sorts numerically when every non-empty cell is a number, otherwise as text;
  empty cells stay last and ties keep the CSV order;
- filters by free text, case-insensitively, over every column including hidden ones. A term
  cannot match across a cell boundary. The status line reports the rows left;
- on the matrix, shows and hides columns from a checkbox per column. The nine columns in
  `MATRIX_DEFAULT_COLUMNS` (`source_id`, `source_type`, `research_domain`,
  `hypotheses_challenged`, the two overlap scores, `critical_collision`,
  `interpretation_confidence`, `access_limitation`) start visible; the 34 prose columns start
  hidden. A default name missing from the matrix raises `ValueError`;
- measures each filter run with `performance.now()` around the handler and stores it on the view
  as `data-lr-filter-ms`, with the time to the next frame as `data-lr-filter-frame-ms` (`REQ-027`
  R10, owner ruling 2026-09-30).

Without script the full table still reads. `_breakable()` adds a `<wbr>` after each underscore and
semicolon in headers and cells, so values such as `H2;H7;H9` and `architecture_overlap_score` can
wrap. It adds no text, so a cell's `textContent` is the CSV value.

### Behaviours a reader would otherwise trip on

Both are already in the code; verify them there rather than assuming from the names.

**(a) `load_template()` strips each HTML template's leading `<!-- token contract -->` doc comment.**
`templates/html/lit-report-page.html` and `lit-report-index.html` each open with a long HTML
comment that documents every `{{TOKEN}}` the template declares, naming each one literally in
braces — following `tools/generate_overview.py`'s precedent for the same reason: a naive global
`{{TOKEN}}` substitution over the *whole* template text would also match those documentation
mentions and corrupt the comment with substituted content. `load_template()` strips exactly that
leading comment (`re.DOTALL`, `count=1`) before the text is ever handed to `fill()`, so the comment
never reaches the substitution step at all.

**(b) The stylesheet's `/* */` comments are stripped when inlined.** `templates/styles/lit-report.css`
is read as a substitution *value* (`{{INLINE_STYLES}}`), never filled itself, so `load_template()`
strips every `/* ... */` block from it before returning. Two reasons, both in the code's own
comments: page weight — the CSS is inlined into all fifteen pages, so every byte of comment is paid
fifteen times over — and false positives, since the stylesheet's own header comment names literal
strings like `<table>` and `lr-editorial-note` as documentation, which would otherwise make a
naive scan of a rendered page look like it contains a table or an editorial note regardless of the
page's actual content.

**(c) The table script's leading `/* */` comment is stripped, and `</script` is refused.**
`templates/scripts/lit-report-table.js` is inlined as a value the same way. Only its leading
comment is stripped, because a regex cannot tell a later `/*` from one inside a JavaScript string.
`load_template()` raises `ValueError` if the script contains `</script`, which would end the
inline element early.

### `fill()`'s contract

`fill()` raises `ValueError` in both directions, comparing the set of `{{TOKEN}}` names the
template declares (found by regex before any substitution runs) against the set of keys
`tokens` supplies:

- a key supplied that the template does not declare (`unknown`) — a token the template writer
  renamed or dropped, caught immediately rather than silently doing nothing;
- a `{{TOKEN}}` the template declares that no key was supplied for (`unfilled`) — a token the
  caller forgot to fill.

Both checks compare placeholder *names*, never by re-scanning the substituted output for a stray
`{{`. A substituted value is free to contain literal `{{...}}` text of its own — the CSS's header
comment mentions `{{INLINE_STYLES}}` as documentation before it is stripped — without that being
mistaken for an unfilled placeholder in the template itself.

### The editorial note on `05_critical_collisions.md`

`05`'s own preamble states the file covers "24 rows"; the measured section count is 30
(`data["counts"]["collision_sections"]`). The owner ruled on 2026-09-22: the rendered `05` page
carries one editorial note (`_editorial_note_05()`, tagged `lr-editorial-note`) stating the
measured figure and that the source's own preamble disagrees with it — read from
`data["counts"]["collision_sections"]`, never a literal. The source file itself is never corrected;
`research/literature-review/` is read-only to this module and to the whole report build.

That ruling is deliberately narrow. It authorizes one note for this one known defect, not a general
contradiction-detection pass over the corpus — a broader pass was considered and declined. No other
deliverable gets an automatic consistency check against its own prose.

### Determinism

`render_report()` asks the wall clock for nothing and makes no model or network call. Iteration
over `data["tables"]` (a dict) is always `sorted()`, for the same reason
`tools/lit_report_extract.py`'s own docstring gives: dict iteration order is Python's, not the
corpus's, and sorting removes even that dependency. Two calls against the same `data` produce
byte-identical strings.

## Known limitation — the duplicate-discovery-rate trend is a hardcoded literal

`REQ-027` R06 requires the entry page to state the campaign's falling duplicate-discovery rate as a
trend: "20.0% → 15.0% → 6.4–7.7%". Verified against the corpus on 2026-09-22: 20.0% and 15.0%
appear across six deliverables in `research/literature-review/`, but 6.4–7.7% appears **nowhere**
in that directory. It is recorded only in two files under `docs/03-sessions/`, outside the corpus
`tools/lit_report_extract.py` reads, and `data["counts"]` carries no duplicate-rate field of any
kind — there is nothing for this module to read that third figure from.

`_render_framing()` therefore renders that sentence as a fixed string, quoted from `REQ-027` R06's
own text rather than measured. This is a documented exception to R05's "the renderer computes
nothing" — the module docstring and `_render_framing()`'s own docstring both call it out — and it
is a real limitation in the sense that the figure is not tied to `data["counts"]` the way every
other number on the page is, and nothing this module or the extractor reads can verify it at render
time.

**Ruled by the owner on 2026-09-22.** The figure is kept rather than dropped: the falling trend is
the campaign's actual finding, and R06's purpose — saturation approached but explicitly not
demonstrated — depends on all three points. `REQ-027` R06 now records this as a stated exception to
R05 and names the two session records as the third point's source. The condition attached to the
ruling is that the provenance is visible to a reader, so `_render_framing()` emits a
`.lr-provenance` line naming `SESS-2026-09-19-08` and `SESS-2026-09-20-02` and saying in plain words
that this figure is cited rather than measured.
`test_the_uncorroborated_duplicate_rate_figure_carries_its_provenance` pins that condition, and
also asserts that 20.0% and 15.0% genuinely are in the corpus while 6.4-7.7% is not. The extractor
was deliberately **not** widened to read session records; its corpus remains
`research/literature-review/` alone.

## Failure and recovery

`render_report()` raises rather than producing a partially-filled page. It never writes to
`research/literature-review/` or anywhere else, so a failed call leaves nothing to clean up.

| Failure | Cause | Fix |
|---|---|---|
| `FileNotFoundError` from `load_template()` | `templates/html/lit-report-page.html`, `lit-report-index.html`, `lit-report-table.html`, `templates/styles/lit-report.css` or `templates/scripts/lit-report-table.js` is missing or renamed | Restore the template family; `render_report()` reads those five exact filenames |
| `ValueError: load_template(): lit-report-table.js contains '</script' ...` | An edit to the script added the closing-tag text, for example inside a string | Split the string (`"<" + "/script>"`) or remove it; the script must not end its own element |
| `ValueError: default column(s) not in the table: ...` | `MATRIX_DEFAULT_COLUMNS` names a column `04_evidence_matrix.csv` no longer has | Update `MATRIX_DEFAULT_COLUMNS` to the matrix's current header |
| `ValueError: fill(): token(s) not present in template: ...` | A caller (or a future edit to `render_report()`) supplies a token key the template no longer declares | Align the template's `{{TOKEN}}` names with the keys `render_report()` builds, or vice versa |
| `ValueError: fill(): unfilled token(s) remain: ...` | The template declares a `{{TOKEN}}` no value was supplied for | Add the missing key to the `tokens` dict passed to `fill()` |
| `KeyError` on `data["deliverables"]`, `data["tables"]`, or `data["counts"]` | `data` did not come from `tools.lit_report_extract.extract()`, or came from a stale/hand-edited copy | Pass `extract()`'s live output; do not hand-construct or cache `data` across a corpus change |
| `KeyError` in `table_by_filename[entry["filename"]]` | A CSV deliverable's filename in `data["deliverables"]` has no matching entry in `data["tables"]` | This indicates `extract()`'s own output is inconsistent; investigate there, not here |

<!-- generated:tool-reference:start -->

### Reference: `tools/lit_report_render.py`

Render the literature-review campaign report's pages — `REQ-027` `phase-lrr-02`, `phase-lrr-03`.

This module renders. It writes nothing to `_public/` and assembles no CLI — `phase-lrr-04` owns
both. It consumes `tools/lit_report_extract.extract()`'s output (see that module's docstring for
the shape) and returns a mapping of relative output path to complete HTML document; writing that
mapping to disk is `phase-lrr-04`'s job.

Fifteen entries come out of `render_report()`: `index.html` plus one page per deliverable
(fourteen — eleven Markdown, three CSV). Each CSV page is a browsable table view (`REQ-027` R03,
`phase-lrr-03`): `_render_table()` writes every row into the page as HTML from the extractor's
`tables` entry, so the table's data travels inline in its own page and nothing is fetched
(`PLAN-043`'s inlining decision). `templates/scripts/lit-report-table.js` is inlined into those
three pages only, through the page shell's `{{INLINE_SCRIPT}}`, and adds sorting, free-text
filtering and, on the matrix, column visibility. Deliverable pages and the entry page carry no
script (owner ruling, 2026-09-30).

Determinism (`REQ-027` R05). `render_report()` is a pure function of its `data` argument and the
on-disk template family under `templates/html/` and `templates/styles/` — no wall clock, no
random input, no model or network call. Two calls against the same `data` produce identical
strings, and iteration over `data["tables"]` (a dict) is always `sorted()` for the same reason
`tools/lit_report_extract.py`'s own docstring gives: dict iteration order is Python's, not the
corpus's, but sorting removes even that dependency.

The renderer computes no corpus figures of its own (R05's "the renderer never computes"). Every
count on the page — collision sections, disputed/confirmed review counts, table row/column
counts, deliverable counts — is read from `data["counts"]` or from a `data["tables"]`/
`data["deliverables"]` entry the extractor already measured; nothing here re-derives a number
from the source text. The one deliberate exception is the entry-page `{{FRAMING}}` block's fixed
epistemic-posture prose (the "first research memo" statement and the duplicate-discovery-rate
trend): those are quoted verbatim from `research/literature-review/CLAUDE.md` and from `REQ-027`
R06's own text, not measured by `tools/lit_report_extract.py`, because the extractor's `counts`
carries no duplicate-rate figure at all and the campaign's third measurement point (`phase-lit-09`,
6.4-7.7%) is recorded only in `docs/03-sessions/`, outside `research/literature-review/` and so
outside the extractor's corpus. The owner ruled on 2026-09-22 that the figure is kept rather than
dropped, because the falling trend is the campaign's actual finding and R06's point depends on all
three points — on condition that the page says plainly where it comes from. `REQ-027` R06 now
records this as a stated exception to R05, and `_render_framing()` emits a visible provenance line
naming the two session records. Nothing on the page presents this figure as measured.

The 2026-09-22 owner ruling on `05_critical_collisions.md`'s stale preamble ("24 rows" against a
measured 30 `collision_sections`) is implemented narrowly: the prose renders verbatim like every
other deliverable, and `_editorial_note_05()` adds one `{{EDITORIAL_NOTES}}` note stating the
measured count — read from `data["counts"]["collision_sections"]`, never a literal — and that the
file's own preamble states a different figure. `research/literature-review/` is read-only; nothing
here writes there.

Markdown deliverables render through `markdown-it-py`'s CommonMark preset with `table` and
`strikethrough` enabled — the combination verified against all eleven Markdown deliverables,
including `05` and `06`'s YAML-block hard cases (05/06 carry `evidence: >`-style YAML fenced code
that must stay inside `<pre>`, not leak out as literal `- ` text).

    from tools.lit_report_render import render_report
    from tools.lit_report_extract import extract
    pages = render_report(extract())   # {"index.html": "<!DOCTYPE html>...", "05_..." : ...}

No CLI arguments.

<!-- generated:tool-reference:end -->
