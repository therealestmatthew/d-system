---
schema_version: 1
id: doc-session-literature-review-report-rendering
code: SESS-2026-09-22-02
title: Template family, stylesheet and rendering module for the campaign report — two rulings implemented, a requirement amended, and a read-only audit that took a document code
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems:
- sys-html
depends_on:
- doc-literature-review-report-page
- doc-literature-review-report-requirements
---

# Template family, stylesheet and rendering module for the campaign report

## Phase

`phase-lrr-02` — Report template family, shell and faithful Markdown rendering, the second phase of
[PLAN-043](../01-plans/PLAN-043-literature-review-report-page.md). Claimed as `agent-lrr` on `dev`;
worked on `agent/phase-lrr-02` in `../d-system-worktrees/phase-lrr-02`.

Run as a coordinated batch under [GOV-003](../08-governance/GOV-003-backlog-decisions.md)'s
2026-09-16 coordinator-completion ruling, with the owner's batch approval standing in for the
per-phase claim gate and the integration ask preserved unchanged.

## What shipped

Six files. Three were declared when the phase was written; three were added by widening the
declaration on `dev`, for reasons recorded under *The declaration was too narrow, twice* below.

| File | What it is |
|---|---|
| `templates/html/lit-report-page.html` | The shell for one deliverable or one table view |
| `templates/html/lit-report-index.html` | The entry page |
| `templates/styles/lit-report.css` | The stylesheet, inlined into every page |
| `tools/lit_report_render.py` | The rendering module |
| `test/test_lit_report_render.py` | Its tests |
| `docs/08-governance/OPS-019-lit-report-render.md` | Its operations document |

Plus amendments to `REQ-027`, `PLAN-043` and `phase-lrr-02`'s own backlog entry, both owner-ruled.

`render_report()` takes `tools/lit_report_extract.py`'s output and returns a mapping of relative
output path to complete HTML document — fifteen entries, 973,278 bytes. That mapping is the seam:
`phase-lrr-03` replaces the three CSV pages' bodies with interactive tables, and `phase-lrr-04`
writes the mapping to disk. Nothing else should need to change.

```
00_search_ledger.html          11,886      07_anti_novelty_case.html          46,273
01_terminology_map.html       272,232      08_surviving_distinctions.html     32,550
02_domain_map.html             88,254      09_reuse_recommendations.html      36,655
03_source_inventory.html       11,839      10_architecture_implications.html  30,809
04_evidence_matrix.html        13,171      11_open_research_questions.html    28,538
05_critical_collisions.html   166,866      12_experiment_proposals.html       26,653
06_hypothesis_tests.html      140,588      13_validated_bibliography.html     54,087
index.html                     12,877
```

## The plan's top risk does not exist

`PLAN-043`'s risks section states that `05` and `06` "carry nested tables inside blockquotes" and
that "a renderer that handles `01`'s prose may not handle `05`". Measured across all eleven Markdown
deliverables before any code was written:

```
$ grep -cE '^[[:space:]]*>.*\|' research/literature-review/[0-9][0-9]_*.md
   0 for all eleven
```

No line anywhere in the corpus carries a blockquote marker and a pipe. `05_critical_collisions.md`
contains **zero** pipe characters and **zero** blockquote lines — it has no tables at all, and is
the file the risk names as the hard case. `06` has 35 blockquote lines and 13 table rows, but they
never overlap.

The real rendering load is volume, not nesting: `01_terminology_map.md` carries 749 table rows
across 74 separate tables.

Filed as idea `000311`, which is open and awaiting a ruling on whether the risk statement is
corrected or struck. The statement was **not** amended in this session — the owner ruled on the
wording defect in `000310` and that ruling is what was applied; generalising it to a second,
unruled defect in the same paragraph would be inventing policy.

## Markdown rendering, settled by measurement

No Python Markdown renderer existed anywhere in the repository. `marked` is a Node dependency in
`ts/package.json`, serving the HTML Viewer's route-side rendering, and is unreachable from a tool
under `tools/`. The owner chose `markdown-it-py` over hand-rolling a renderer or vendoring one.

Verified against the real corpus before the decision was acted on, using
`MarkdownIt("commonmark").enable("table").enable("strikethrough")`:

```
01_terminology_map.md      h2 src= 74 out= 74   tableRows=749  tables=74   stray(h2=0,li=0)
02_domain_map.md           h2 src=  1 out=  1   tableRows= 22  tables= 1   stray(h2=0,li=0)
05_critical_collisions.md  h2 src= 30 out= 30   tableRows=  0  tables= 0   stray(h2=0,li=0)
06_hypothesis_tests.md     h2 src= 12 out= 12   tableRows= 13  tables= 1   stray(h2=0,li=0)
...all eleven...
ALL R02 HEADING/STRAY ASSERTIONS PASS
```

Every `REQ-027` R02 assertion satisfied on the first attempt. That is the phase's first acceptance
condition, met by the library choice rather than by anything written here.

## Two owner rulings, implemented

### 05's stale preamble is annotated, never corrected (idea `000309`)

`05_critical_collisions.md`'s preamble says the file covers "24 rows"; it holds 30 sections. The
owner ruled on 2026-09-22 that the prose renders verbatim and the rendered output carries an
editorial note. `research/literature-review/` is untouched, per `PLAN-043`'s out-of-scope rule.

Rendered, with the count read from `data["counts"]["collision_sections"]` rather than a literal:

> This file's own preamble states 24 rows. The measured collision-section count is **30**, read
> from `04_evidence_matrix.csv`'s `critical_collision: yes` rows. The source file is not corrected;
> this note records the discrepancy.

Verified present on `05` and on no other page. The ruling is deliberately narrow — one note for one
known defect. A general contradiction-detection pass over deliverable prose was considered and
declined as an unspecified feature that would widen `phase-lrr-04` past its scope.

### The duplicate-rate trend's third figure is cited, not measured

`REQ-027` R06 requires the entry page to show the falling duplicate-discovery rate as
20.0% → 15.0% → 6.4–7.7%, and its verification required those figures to "match the values in the
source deliverables". They cannot all do so. Measured:

```
20.0% and 15.0%   present in six deliverables (06, 07, 09, 10, 11, 12)
6.4% / 7.7%       present in NO deliverable
```

The only `6.4` occurrences in the corpus are citations of a theorem number (`Thm 6.4`) in three
deliverables — a false positive that has to be excluded by hand. The third measurement point is
recorded only in `SESS-2026-09-19-08` and `SESS-2026-09-20-02`, outside the corpus the extractor
reads, and `data["counts"]` carries no duplicate-rate field at all.

The owner ruled on 2026-09-22 that the figure is **kept** — the falling trend is the campaign's
actual finding and R06's purpose, saturation approached but explicitly not demonstrated, depends on
all three points — on condition its provenance is visible to a reader. Implemented as:

- `REQ-027` R06 gains a *Where the duplicate-rate figures come from* section recording this as a
  stated exception to R05, naming the two session records, and amending R06's verification to
  require the citation.
- `_render_framing()` emits a `.lr-provenance` line saying in plain words that 6.4–7.7% is not from
  the deliverables, naming both session records, and calling it cited rather than measured.
- `test_the_uncorroborated_duplicate_rate_figure_carries_its_provenance` pins the condition, and
  independently asserts that 20.0% and 15.0% really are in the corpus while 6.4–7.7% is not.
- The extractor was **not** widened. Its corpus remains `research/literature-review/` alone.

## The declaration was too narrow, twice

`AGENTS.md` requires an agent to stay inside its phase's declared `systems` and `deliverables`, and
where the work genuinely needs a file outside them, to update the declaration on `dev` and re-run
the validator so peers see the wider lock before continuing. That happened twice here, each as its
own commit on `dev`.

1. **Nothing rendered.** The phase's acceptance requires assertions against rendered output —
   heading counts, table elements, reachability — while declaring only two template files. Added
   `tools/lit_report_render.py`, `test/test_lit_report_render.py` and
   `templates/html/lit-report-index.html`. The generator assembly and the writes to `_public/` stay
   in `phase-lrr-04`, which already declares them.
2. **The renderer needed an operations document.** `test/test_tool_docs.py` requires every file
   under `tools/` to be paired with an `OPS-*` document, and the full suite was red on two tests
   until one existed. `AGENTS.md`'s rule is unconditional, so this was required work. Added
   `docs/08-governance/OPS-019-lit-report-render.md`.

The second is worth noting as a design question rather than just a gap: `lit_report_render.py` is a
pure library with no CLI, and the repository's convention treats everything under `tools/` as
operator-invocable. Its operations document says plainly that there is no command and why. If a
later phase wants a cleaner boundary, the module belongs under `src/`; that was not changed here
because the extractor and the generator are both genuinely tools and keeping the family together
was judged the smaller surprise.

## An adversarial review permanently consumed a document code

`--next-code operation` returned `OPS-019` where `OPS-018` was expected. The reservation store
explains it:

```
$ cat .git/code-reservations/OPS-018
{"at": 1790080020.373468, "code": "OPS-018", "holder": "dev @ /code/d-system"}
```

That timestamp is 08:27 on 2026-09-22, which is when the **read-only adversarial review of
`phase-lrr-01`** ran `uv run python -m src.governance --next-code operation` to evidence its finding
that `phase-lrr-04`'s declared deliverable path named a consumed code. The command reserves rather
than reports, so gathering the evidence consumed the very resource the finding was about.

**The reservation was released by hand once the mechanism was actually read.** Two claims made
earlier in this session were wrong and are corrected here rather than left standing:

- `OPS-018` was **not** permanently lost. `src/governance/reservations.py` gives every reservation
  a fourteen-day TTL, pruned by the next allocation, so an abandoned code returns on its own.
- Releasing it by hand was **not** an improper touch of governed state. `--release-code` exists for
  precisely this case, and `GOV-005`'s *Releasing* section names it: "Release one by hand when you
  allocated a code and decided not to write it."

```
$ uv run python -m src.governance --release-code OPS-018
released OPS-018
```

`OPS-019` stands as the renderer's code; renumbering it back would have been churn for nothing. The
real cost was one code held for a few hours. The correct code was still taken from the allocator,
as `GOV-005` requires — never by reading a directory.

The hazard is structural even though this instance was cheap: an auditing agent with only read and
run access can still mutate shared governance state, because a read-only *intent* does not make
`--next-code` a read-only *command*. There is no way to ask what the next code would be without
taking it, which also makes any audit that checks non-idempotent — run twice, it answers `OPS-018`
then `OPS-019`, so the check alters what it is checking.

The adversarial review of this phase was explicitly instructed not to run it, which protects only
the runs someone remembers to protect. The durable fixes worth considering are a read-only query
(`--peek-code`, or `--next-code --dry-run`) that reports without reserving, and moving the
prohibition into the auditor agent definitions rather than into each dispatch prompt. Neither was
built here; both are outside this phase.

`phase-lrr-04`'s declared path is now wrong by two codes rather than one — it names
`OPS-017-generate-lit-report.md`, `OPS-017` went to the extractor's document and `OPS-019` to the
renderer's. Tracked as idea `000312`, which is open.

## Verification

The phase's `verification` list, run in the worktree, with real output.

```
$ uv run python -m src.governance
Governance OK: 35 systems, 308 documents, 28 memories, 292 backlog phases

$ uv run pytest
737 passed, 2 warnings in 56.04s
```

737 is 688 before this session plus the 49 new rendering tests. Also run, though not in the phase's
list:

```
$ uv run ruff check tools/lit_report_render.py test/test_lit_report_render.py
All checks passed!

$ uv run mypy tools/lit_report_render.py
Success: no issues found in 1 source file

$ uv run pytest test/test_tool_docs.py -q
7 passed
```

Output checked directly rather than only through the suite: no double-escaped HTML entities, no
off-origin `src` or `href`, no unsubstituted `{{TOKEN}}`, the editorial note present on `05` alone.

### A pre-existing lint condition, not this phase's

```
$ uv run ruff check tools/ test/
Found 11 errors.
```

All eleven are in `test/test_governance.py`, `test/test_idea_dispatch.py` and
`tools/idea_dispatch.py`, and all predate this branch. The four files this phase touches pass
clean. They have gone unseen because `AGENTS.md`'s lint command is
`uv run ruff check src/ test/` — `tools/` is not in it, and `src/` is, so a defect under `tools/`
is invisible to the documented check. Not repaired here: out of scope, and repairing a peer's files
inside a rendering phase is exactly what `PLAN-043` warns against.

### The private-content check

```
$ uv run python tools/check_no_private_content.py     # with changes staged
note: _private/portfolio/ not found — content check skipped (path check still ran)
check_no_private_content: OK (772 tracked files, 0 identifiers checked)
```

The path half ran over all 772 tracked files and passed; the content half did not, because
`_private/` is gitignored and never reaches a worktree. Not in this phase's verification list —
`REQ-027` R11 and `phase-lrr-04`'s acceptance are where the with-`_private/` run is required. Run
from the primary checkout after integration it reports `31 identifiers checked`, which is the half
that matters actually running.

## A concurrent writer on the trunk

Another session ran an idea-triage workflow on `dev` during this one, committing at 11:36 and 11:39
around this session's own 11:38 commit. It caused one transient failure of
`test_the_committed_markdown_matches_regenerated_output` that did not reproduce and was initially
misattributed here to a mistake of this session's own.

The adversarial review of `phase-lrr-01` flagged the concurrent writer correctly and was told it was
wrong. It was not. Recorded because the correction matters more than the slip: an agent reporting an
unexplained modification to shared state is doing its job, and the reflex to explain it away as
one's own edit is the thing to distrust.

Both peer commits touch only `_data/ideas.jsonl` and `docs/00-working/ideas.md`, so neither collides
with this phase's deliverables.

## Open, and not this phase's to close

- Idea `000311` — `PLAN-043`'s nested-tables-in-blockquotes risk is false. Awaiting a ruling on
  correcting or striking it.
- Idea `000312` — `phase-lrr-04`'s declared OPS path names a consumed code, now wrong by two.
- The `--next-code` hazard above, which nothing durable records.
- `phase-lrr-03` makes the three CSV placeholder pages interactive; `phase-lrr-04` assembles the
  generator, resolves cross-links and adds the drift test.

## State at hand-off

- Branch `agent/phase-lrr-02`, one work commit on top of the claim and two declaration-widening
  commits taken on `dev`.
- Both verification commands green.
- No `_tmpagent/` claim was opened this session, so there is none to release.
- The phase is left `status: active`. Completion requires the independent adversarial review's
  findings to be fixed or accepted, and the owner's approval to integrate.
