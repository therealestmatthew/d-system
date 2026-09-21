---
schema_version: 1
id: doc-session-literature-review-corpus-extraction
code: SESS-2026-09-21-04
title: Deterministic extraction of the literature-review campaign corpus — the extractor, its determinism carriers and the corpus defects it surfaced
kind: session
status: active
owner: repository-owner
created: '2026-09-21'
updated: '2026-09-21'
systems:
- sys-research
- sys-html
depends_on:
- doc-literature-review-report-page
- doc-literature-review-report-requirements
---

# Deterministic extraction of the literature-review campaign corpus

## Phase

`phase-lrr-01` — Deterministic extraction of the campaign corpus, the first phase of
[PLAN-043](../01-plans/PLAN-043-literature-review-report-page.md) and the first reader of
`research/literature-review/` the report will have. Claimed as `agent-lrr` on `dev` in `c47b7b2`;
worked on `agent/phase-lrr-01` in `../d-system-worktrees/phase-lrr-01`.

## What shipped

`tools/lit_report_extract.py` reads `research/literature-review/` and emits the structured form
`phase-lrr-02` through `phase-lrr-04` will render. It writes no HTML and touches nothing under
`_public/`, which is the phase's scope boundary. Its operations document is
[OPS-017](../08-governance/OPS-017-lit-report-extract.md); its tests are
`test/test_lit_report_extract.py`.

The precedent followed is `tools/overview_metrics.py` and `tools/overview_inventory.py`, not
`tools/generate_overview.py`. `PLAN-043` points at `generate_overview.py`, but that tool is the
renderer and belongs to `phase-lrr-02`; this phase is the extractor, which is what the two
`overview_*` tools already are — same `render()`/`--out` shape, same "asks the wall clock for
nothing" contract, and `OPS-011`/`OPS-012` as the shape of the document.

### The three design questions, settled before implementing

The phase was handed over with three questions deliberately left open. All three were put to the
owner before any code was written, and all three were settled as recommended.

1. **Parse depth.** The extractor captures block boundaries and hands raw Markdown to
   `phase-lrr-02`; it does not parse inside a collision or hypothesis block. `REQ-027` R02 makes
   faithful Markdown rendering `phase-lrr-02`'s job, and parsing inside here would have built half
   a Markdown renderer in the extractor and the other half again downstream — against exactly the
   nested-tables-inside-blockquotes cases `PLAN-043` names as the hard ones.
2. **Fixture for `phase-lrr-02`.** None. `lrr-02` calls the real extractor. `PLAN-043` had already
   reached this conclusion in its own words — "a fixture that drifts from the real extractor costs
   more than the sequencing saves" — and it keeps this phase to the two deliverables the backlog
   declares.
3. **`second_review`.** A derived `second_review_verdict` alongside the verbatim prose. The field
   is prose opening with a verdict word, punctuated four different ways across nine sessions
   (`disputed:`, `confirmed,`, `confirmed;`, `disputed --`). Deriving the verdict makes `REQ-027`
   R07's count assertable; keeping the prose keeps the reviewer's reasoning. A word outside the
   vocabulary classifies as `unrecognised` rather than being guessed, and appears in `counts` at
   zero when unused, so a future corpus edit surfaces as a visible number rather than a silent
   miscount.

A fourth question was raised in the same batch and answered: `AGENTS.md` requires an `OPS-*`
document alongside any new tool, but this phase's declared deliverables list only the tool and its
test. The owner directed that it be written now. See *Consequence for `phase-lrr-04`* below.

### Determinism, and its three carriers

`REQ-027` R05 requires byte-identical output across runs. Three things carry that, and each has
its own test rather than being covered only by a happy-path comparison:

- **`sorted()` over `Path.glob()`.** Glob order is the filesystem's, not the tool's. This is the
  one risk the `overview_*` precedent never had to handle, and on a filesystem that already yields
  sorted names a happy-path test passes without the `sorted()` call. The test therefore monkey-
  patches `Path.glob` to yield its results reversed, so the assertion can actually fail.
- **`json.dumps(..., sort_keys=True)`**, with every list built in a defined order.
- **CSV cells left as strings.** Round-tripping a numeric-looking cell through `float()` rewrites
  `04` as `4.0` — a silent edit to source data, not a formatting choice.

A fourth test asserts the source contains no `datetime.now`, `time.time`, `date.today` or `utcnow`.
The byte-identical tests would catch a timestamp only if two runs landed in different seconds,
which is a race; asserting the clock is never consulted is the deterministic form of the same
check.

### Anchors

Every deliverable, collision, hypothesis and table carries a unique, HTML-id-safe `anchor`.
Collision anchors key on the **slug**, not the section number — `collision-em-llm-human-inspired-
episodic-memory-infinite-context-2024`, not `collision-3` — so renumbering `05` cannot silently
break a link, and because the slug is also a `source_id` in `04_evidence_matrix.csv`, the anchor
is a join key to the matrix for free. `phase-lrr-04`'s cross-links are the thing that needs it.
Hypothesis anchors key on the `H<n>` token for the same reason: the descriptive title after the em
dash can be rewritten without consequence.

The slug-to-matrix relationship is asserted as a bijection, set-equal in both directions, so a slug
present on one side only cannot hide behind a matching count. It holds: all 30.

## Measured results

Every figure below was measured by the tool at run time, not restated from the backlog. The test
suite recomputes them from the files rather than comparing against literals, so the suite does not
go red the day the corpus changes for a reason unrelated to the extractor.

```
deliverables            14   (11 markdown, 3 csv)
ledger     1200 rows ×  15 columns
inventory  1154 rows ×  13 columns
matrix       67 rows ×  43 columns
collision_sections      30   (18 disputed, 12 confirmed, 0 unrecognised)
hypothesis_blocks       11   (H1–H11)
```

These match `phase-lrr-01`'s acceptance and `REQ-027`'s recorded figures exactly. `CLAUDE.md` and
`HANDOFF.md` live in the same directory, fall outside the `[0-9][0-9]_*` glob, and are correctly
absent from the deliverable set — asserted, rather than left to chance.

## Verification

The phase's `verification` list, run in the worktree, with real output.

```
$ uv run python -m src.governance
Governance OK: 35 systems, 306 documents, 28 memories, 292 backlog phases

$ uv run pytest
686 passed, 2 warnings in 52.04s
```

686 is 651 before this session plus the 35 new tests. Also run, though not in the phase's list:

```
$ uv run ruff check tools/lit_report_extract.py test/test_lit_report_extract.py
All checks passed!

$ uv run mypy tools/lit_report_extract.py
Success: no issues found in 1 source file

$ uv run python tools/lit_report_extract.py --out a.json
$ uv run python tools/lit_report_extract.py --out b.json
$ cmp a.json b.json          # byte-identical, 4,314,428 bytes
```

`ruff format --check` reports 33 files would be reformatted against 33 already formatted, so
`ruff format` is not this repository's convention and was not applied. `ruff check` and `mypy` are
what `AGENTS.md` names, and both are clean.

### The private-content check, honestly

```
$ uv run python tools/check_no_private_content.py       # with the changes staged
note: _private/portfolio/ not found — content check skipped (path check still ran)
check_no_private_content: OK (765 tracked files, 0 identifiers checked)
```

The path half ran over all 765 tracked files and passed; **the content half did not run**, because
`_private/portfolio/` is gitignored and therefore does not exist in a worktree. This is not a
failure and it is not in `phase-lrr-01`'s verification list — `REQ-027` R11 and `phase-lrr-04`'s
acceptance are where the with-`_private/` run is required, and that run has to happen somewhere
the real portfolio is present. Recorded here so nobody later reads this session's green line as
the content half having passed.

## Corpus defects surfaced, and deliberately not repaired

`PLAN-043` puts any edit to `research/literature-review/` out of scope. The tool reports these
under `known_defects` and leaves them alone; the two below were known going in.

- **Two duplicate `source_id` rows in the inventory** — `memtx-transactional-belief-commit-2026`
  and `semantically-seeded-graph-propagated-impact-analysis-vision-2026`. Both rows survive
  extraction and `inventory.row_count` counts both. Idea `000308`.
- **The inventory's `status` field understates deep-read coverage by 16.** Also idea `000308`.
  Worth recording how this was confirmed: a first measurement here gave **17**, counting inventory
  *rows* with a matrix row and a status other than `deep_read`. Idea `000308`'s own predicate —
  distinct `source_id`s present in the matrix and not marked `deep_read` — gives **16**, and
  reproduces exactly. The two differ by one because one of the duplicated ids above is among them.
  The figure is only meaningful with its predicate attached, which is why `OPS-017` states the
  predicate and not just the number. `000308` records that this drift had already been written
  down twice at two different wrong figures; this is the third way to get it wrong, and the idea's
  own rule is the one that holds.

Two further defects were found during this phase and are **not** yet tracked as ideas:

- **`05_critical_collisions.md`'s preamble says "24 rows"** where the file holds 30 sections. The
  prose is stale; `counts.collision_sections` is measured and disagrees with it. The report will
  render the prose as written, so a reader of the rendered `05` will see a figure its own file
  contradicts.
- **`01`–`13` is eleven Markdown deliverables, not thirteen.** `03_source_inventory.csv` and
  `04_evidence_matrix.csv` are CSVs. `PLAN-043` and `phase-lrr-02`'s scope both say "all thirteen
  Markdown deliverables", and `REQ-027` R02 and `phase-lrr-02`'s acceptance are written as "for
  each of `01`–`13`". As written, that acceptance cannot hold: a CSV has no `## ` headings to
  count and no Markdown tables to assert. The counts are unaffected — 14 deliverables, 11 Markdown,
  3 CSV, all measured — but `phase-lrr-02`'s acceptance needs rewording before it is worked, or the
  phase will fail a check that was never satisfiable.

## Consequence for `phase-lrr-04`

`--next-code operation` allocated **OPS-017** to this phase's document,
`OPS-017-lit-report-extract.md`. `phase-lrr-04` declares
`docs/08-governance/OPS-017-generate-lit-report.md` as a deliverable, so that path is now taken and
the generator's document will need the next code instead. Flagged rather than fixed:
`AGENTS.md` permits touching only this session's own phase line in `backlog.yaml`, so
`phase-lrr-04`'s deliverable path is the owner's to update.

## State at hand-off

- Branch `agent/phase-lrr-01`, one work commit (`47def0d`) on top of the claim (`c47b7b2`).
- Both verification commands green after the post-rebase run.
- No `_tmpagent/` claim was opened this session, so there is none to release.
- The phase is left `status: active`. Marking it complete is `/session-close`'s, after its
  independent review.
