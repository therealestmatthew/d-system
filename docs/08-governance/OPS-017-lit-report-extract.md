---
schema_version: 1
id: doc-ops-lit-report-extract
code: OPS-017
title: Extract the literature-review campaign corpus to structured JSON
kind: operation
status: active
owner: repository-owner
created: '2026-09-21'
updated: '2026-09-21'
systems: [sys-research, sys-html]
depends_on: [doc-governance-operations, doc-literature-review-report-requirements]
---

# Extract the literature-review campaign corpus to structured JSON

## Trigger

Run when a later phase of [PLAN-043](../01-plans/PLAN-043-literature-review-report-page.md) needs
the campaign's fourteen files in a form it can render — the report's template family
(`phase-lrr-02`), its three browsable tables (`phase-lrr-03`), or the generator and drift test
(`phase-lrr-04`). Run it directly when you want to check a figure about the corpus without opening
a 1.6MB CSV.

This tool is the report's only reader of `research/literature-review/`. That is the point of it:
[REQ-027](../06-requirements/REQ-027-literature-review-report-page.md) R05 requires that the
renderer compute nothing, so every count the report shows is measured here and passed downstream
rather than recomputed at render time. A renderer that opens a campaign file itself has bypassed
the contract the drift test depends on.

It reads only `research/literature-review/` and writes only where you point `--out`. It makes no
model or network call and asks the wall clock for nothing, so two runs against an unchanged tree
produce byte-identical bytes.

## Command

```bash
uv run python tools/lit_report_extract.py               # print to stdout
uv run python tools/lit_report_extract.py --out FILE    # write to FILE instead
uv run python tools/lit_report_extract.py --corpus DIR  # read a different corpus directory
```

`--corpus` exists for tests and for checking a copy of the corpus; the report always runs against
the default.

## Expected result

Exit 0 and roughly 4.3MB of JSON, ordered by key throughout. Six top-level sections:

- `deliverables` — the files matching `research/literature-review/[0-9][0-9]_*`, in filename
  order, each with its anchor, byte count and SHA-256. The eleven Markdown deliverables also carry
  their full source text and line count; the three CSVs do not, because they appear under `tables`
  instead. `CLAUDE.md` and `HANDOFF.md` sit in the same directory, fall outside the glob, and are
  correctly absent — they are the campaign's own working instructions, not deliverables.
- `tables` — `ledger`, `inventory` and `matrix`, each as `columns` plus `rows`, where a row is a
  list of strings aligned to `columns`. Cells are never coerced: `04` stays `"04"`.
- `collisions` — the sections of `05_critical_collisions.md`, each joined by slug to its row in
  `04_evidence_matrix.csv`, carrying the matrix's `second_review` prose verbatim alongside a
  derived `second_review_verdict`.
- `hypotheses` — the `H1`–`H11` blocks of `06_hypothesis_tests.md`. `06`'s trailing
  `## Summary table` heading is not one of them.
- `counts` — every figure the report shows, measured from the files.
- `known_defects` — defects found in the corpus and deliberately left in place; see below.

At the time of writing, `counts` reads: 14 deliverables (11 Markdown, 3 CSV); ledger 1200 × 15;
inventory 1154 × 13; matrix 67 × 43; 30 collision sections, 18 `disputed` and 12 `confirmed`; 11
hypothesis blocks. Those figures are recorded here as an orientation for a reader, **not** as
something the tool asserts. The tool measures; if the corpus changes, the numbers change with it,
and `test/test_lit_report_extract.py` recomputes rather than hardcoding them for the same reason.

### Anchors

Every deliverable, collision, hypothesis and table carries an `anchor` — a unique, HTML-id-safe
string a later phase can link to. Collision anchors key on the **slug**, not the section number
(`collision-em-llm-human-inspired-episodic-memory-infinite-context-2024`, not `collision-3`), so
renumbering `05` cannot silently break a link; the slug is also a `source_id` in the matrix, which
makes the anchor a join key for free. Hypothesis anchors key on the `H<n>` token for the same
reason: the descriptive title after the em dash can be rewritten without consequence.

### `second_review_verdict`

The matrix's `second_review` field is prose, not an enum. It opens with a verdict word and
continues into the reviewer's commentary, punctuated four different ways across nine sessions
(`disputed:`, `confirmed,`, `confirmed;`, `disputed --`). The tool derives the verdict from the
leading run of letters and carries the prose through untouched, so REQ-027 R07's "18 of 30
disputed" is assertable without any of the reviewer's reasoning being lost.

A value opening with a word outside `confirmed` / `disputed` / `not_applicable` classifies as
`unrecognised` rather than being guessed at, and an empty cell as `none`. Both appear in
`counts.collision_second_review` at zero when unused, so a future edit to the corpus surfaces as a
visible number rather than a silent miscount.

## Known corpus defects

The tool reports these and does not repair them. `PLAN-043` puts any edit to
`research/literature-review/` out of scope: the report renders the campaign as it stands, and a
repair folded into a rendering tool would hide a tracked defect.

- **Two duplicate `source_id` rows in the inventory** — `memtx-transactional-belief-commit-2026`
  and `semantically-seeded-graph-propagated-impact-analysis-vision-2026`. Both rows survive
  extraction, `inventory.row_count` counts both, and the ids are listed under
  `known_defects.duplicate_inventory_source_ids`. Tracked as idea `000308`.
- **The inventory's `status` field understates deep-read coverage by 16.** Idea `000308`'s
  predicate is the one that reproduces: of the 67 distinct `source_id`s in the matrix, 16 are not
  marked `deep_read` in the inventory, against 51 that are. Counting inventory *rows* instead gives
  17, because one of the duplicated ids above is among them — which is why the predicate is stated
  here and not just the number. The field is carried through as written; nothing in this tool reads
  it.
- **`05`'s preamble says "24 rows"** where the file holds 30 sections. Prose inside a deliverable
  is rendered as written; `counts.collision_sections` is measured and disagrees with it.

`known_defects.unmatched_collision_slugs` is the one that should stay empty. A slug appearing there
means a section of `05` no longer has a matrix row to join to, which would break `phase-lrr-04`'s
cross-links — investigate rather than render around it.

## Failure and recovery

Every failure prints `error: <what>` to stderr and exits 1, with no traceback. The tool never
writes to the corpus, so a failed run leaves nothing to clean up.

| Message | Cause | Fix |
|---|---|---|
| `corpus directory not found` | `--corpus` points somewhere that is not a directory | Correct the path, or drop the flag to use the default |
| `no files match [0-9][0-9]_*` | The directory exists but holds no deliverables | Check you are pointing at `research/literature-review/` |
| `expected CSV deliverable(s) missing` | One of the three CSVs is absent or renamed | Restore it; the report's tables are defined against those three filenames |
| `expected Markdown deliverable missing` | `05_critical_collisions.md` or `06_hypothesis_tests.md` is absent | Restore it |
| `... row(s) do not match the N-column header` | A CSV is ragged — a quoting or escaping error, usually from hand-editing | Fix the named line in the CSV. The tool refuses rather than emitting a misaligned table |
| `anchor ids are not unique` | Two sections derive the same anchor — typically a duplicated slug in `05` | Report it as a corpus defect; do not work around it in the tool |

<!-- generated:tool-reference:start -->

### Reference: `tools/lit_report_extract.py`

Structured JSON over the adversarial literature-review campaign — `REQ-027` R05's extractor.

The campaign ([PLAN-023](../docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md))
left fourteen files in `research/literature-review/` and nothing that renders them. This tool reads
those files and emits the structured form the report's later phases render; it writes no HTML and
touches nothing under `_public/`.

Every number it emits is measured from the files at run time. No count is restated from prose, and
no figure is recomputed downstream — that split is what `REQ-027` R05 means by "the generator
computes nothing", and it is what makes `phase-lrr-04`'s drift test meaningful.

The tool makes no model or network call and asks the wall clock for nothing: the output is a pure
function of the fourteen files, so two runs against an unchanged tree produce byte-identical bytes.
Three things carry that guarantee, and each has its own test:

- `Path.glob()` has no guaranteed order across platforms or filesystems, so every glob result is
  passed through `sorted()` before anything reads it.
- Every dict is emitted through `json.dumps(..., sort_keys=True)` and every list is built in a
  defined order.
- CSV cells stay strings. Round-tripping a numeric-looking cell through `float()` would rewrite
  `04` as `4.0` and `1e5` as `100000.0`, which is a silent edit to the corpus.

What comes out, per `phase-lrr-01`'s scope:

- `deliverables` — the fourteen files matching `[0-9][0-9]_*`, each with its anchor, its byte count
  and digest, and, for the thirteen Markdown files, the full source text for `phase-lrr-02` to
  render. `CLAUDE.md` and `HANDOFF.md` sit in the same directory and fall outside that glob; they
  are the campaign's own working instructions, not deliverables.
- `tables` — the three CSVs as `columns` plus `rows` (a list of row lists, aligned to `columns`).
- `collisions` — the 30 sections of `05_critical_collisions.md`, each joined to its matrix row.
- `hypotheses` — the 11 `H1`-`H11` blocks of `06_hypothesis_tests.md`.
- `counts` — every figure the report needs, measured here so no renderer computes one.

Anchors are keyed on the **slug**, not the section number. `05`'s headings read `## 3. <slug>`, and
that slug is a `source_id` in `04_evidence_matrix.csv`, so keying on it survives a renumbering of
the file and doubles as the join key to the matrix. Hypothesis anchors key on the `H<n>` token for
the same reason: the descriptive title after the em dash can be rewritten without breaking a link.

    uv run python tools/lit_report_extract.py               # print to stdout
    uv run python tools/lit_report_extract.py --out FILE    # write to FILE instead

This tool never writes to `research/literature-review/`. Defects it surfaces in the corpus are
findings to report, not repairs to make — see `PLAN-043`'s out-of-scope section.

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--out` | write the JSON here instead of stdout |  |  |  |
| `--corpus` |  |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
