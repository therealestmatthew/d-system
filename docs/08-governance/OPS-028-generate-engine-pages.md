---
schema_version: 1
id: doc-ops-generate-engine-pages
code: OPS-028
title: Regenerate the idea realization engine pages
kind: operation
status: active
owner: repository-owner
created: '2026-10-01'
updated: '2026-10-03'
systems: [sys-html]
depends_on: [doc-governance-operations, doc-engine-pages-house-style-requirements]
---

# Regenerate the idea realization engine pages

## Trigger

Run when an up-to-date snapshot of the engine's state is wanted: before sharing the pages, after
a batch of merges, or after a planning session changes plans, phases or batch tables. The pages under
`_public/engine/` are committed snapshots
([REQ-036](../06-requirements/REQ-036-engine-pages-house-style.md) R08). Nothing regenerates
them automatically, and no CI check fails when they fall behind their inputs. The owner ruled
this on 2026-09-30, because the idea log changes many times a day.

## Command

```bash
uv run python tools/generate_engine_pages.py              # write _public/engine/
uv run python tools/generate_engine_pages.py --out DIR    # write somewhere else, e.g. to review
```

Commit the regenerated pages with a message naming the source commit the stamp shows.

## Expected result

One line per page written. Today that is three pages:

```text
wrote _public/engine/index.html
wrote _public/engine/ideas.html
wrote _public/engine/backlog.html
```

| Page | File | Requirements | Built by |
|---|---|---|---|
| Pipeline overview | `index.html` | `REQ-036` R14 | `phase-des-09` |
| Idea funnel and ledger | `ideas.html` | `REQ-036` R15, R16 | `phase-des-10` |
| Backlog and batch graph | `backlog.html` | `REQ-036` R21-R23 | `phase-des-12` |

`REQ-036` R07-R13 apply to every page. The per-idea trace pages (R19, R20) are not built yet;
`phase-des-11` adds them.

The inputs are all tracked: the idea log through `fold()`, `backlog.yaml`, the batch tables under
`docs/09-backlog/batches/`, plan front matter, the house family templates, and the source commit
and its date from git.

Each page states its source commit and that commit's date in the header, never the time the tool
ran, so two runs on one commit produce identical bytes. If any input has uncommitted changes when
the tool runs, the header also says "Inputs had uncommitted changes when generated". Commit first
when the snapshot is meant to be shared.

The pages are built from the house family (`OPS-027`) with both stylesheets inlined. The only
external request is the Google Fonts stylesheet, and the pages contain no script.

## What the pipeline overview counts

Each figure is shown with its source beside it. A stage whose work leaves no structured record
shows "not recorded" rather than an estimate (`REQ-036` R11).

| Stage | Count | Source |
|---|---|---|
| 1 Capture | ideas captured, all statuses | `fold()` |
| 2 Triage | ideas with status `open` | `fold()` |
| 3 Partition | triaged ideas with no `promoted_to` and no phase naming them | `fold()`, the backlog `ideas` field |
| 4 Planning | plans whose front matter reads `draft`, the same set as the G3 queue | plan front matter |
| 5 Adversarial review | not recorded | reviews are prose in session records |
| 6 Phase-fit check | not recorded | no structured record |
| 7 Dependency mapping | queued phases (ready or waiting) | `backlog.yaml`, `src.governance.backlog.readiness` |
| 8 Execution | `active` phases | `backlog.yaml` |
| 9 Realization check | ideas with status `delivered` | `fold()` |

The gates follow `REQ-036` R14's table. G1 shows ideas captured, because nothing waits there. G2
is the stage-3 set. G3 lists the draft plans, which are also the stage-4 count: plan front matter
does not record whether a draft is still being written, under review or waiting for approval, and
the page says so rather than splitting them by guesswork. G4 and G5 share one queue, the active phases,
because integration is fast-forward-only and the completion edit follows the merge in the same
turn. When no backlog phase carries the `ideas` field, G2 falls back to `promoted_to` alone and
the page says phase links are not recorded.

## What the idea funnel and ledger shows

Every idea in `fold()` appears once in the ledger, with its id, title, status, created date and
the four `ARCH-005` axis values. The funnel counts ideas per status, and the counts sum to the
`fold()` total (`REQ-036` R15). Each axis shows its distribution, and an idea with no
classification counts as "unclassified" (R16). An idea with no `promoted_to` and no phase naming
it in its `ideas` field reads "no recorded plan".

## What the backlog and batch graph shows

Every phase in `backlog.yaml` appears with its state. Ready and waiting are computed by
`src.governance.backlog.readiness`, the same function `--ready` uses (`REQ-036` R21). A waiting
phase lists its unmet dependencies by id and state, and a blocked or deferred phase shows its
`blocked_reason` and `resume_when` (R23).

Each batch table under `docs/09-backlog/batches/` appears in sequence order with its stages,
their phases and their states, drawn as a static SVG graph of `depends_on` edges (R22). Any
dependency of a batch member that is outside the batch is drawn as external, whether or not the
table's `external_depends_on` lists it, so no edge is dropped.

## Failure and recovery

- **`subprocess.CalledProcessError` from git.** The tool was run outside a git checkout, or git
  is not on `PATH`. Run it from the repository.
- **`IdeaError` from `fold()`.** The idea log itself is invalid. `uv run python -m src.governance`
  names the bad event. Fix the log through its sanctioned writer, not by hand.
- **`ValueError: unfilled {{NAME}}`.** The house page template's token contract and this tool's
  `_page()` call have drifted apart. Make them agree.
- **A count looks wrong.** On the overview, each stage and gate is defined once, in `STAGES` and
  `GATES` in the tool, and the page prints that definition beside the number. The ledger's
  figures come from `ledger_data()` and the backlog page's from `backlog_data()`. `test/test_engine_pages.py`
  recomputes every figure independently. Run it before assuming the page is wrong.

<!-- generated:tool-reference:start -->

### Reference: `tools/generate_engine_pages.py`

Generate the idea realization engine's pages into `_public/engine/` — `REQ-036`.

The engine (`ARCH-006`) carries an idea from capture to delivered work through nine stages and
five owner gates. These pages show where everything stands, as committed snapshots built from the
house family (`templates/html/house-page.html`, `templates/styles/house*.css`, `OPS-027`). Three
pages exist, one per entry in `PAGES` below:

- `index.html`, the pipeline overview (R14);
- `ideas.html`, the idea funnel and ledger (R15, R16);
- `backlog.html`, the backlog and batch graph (R21-R23).

R07-R13 apply to all three. The per-idea trace pages (R19, R20) are not built yet.

Inputs, all tracked: the idea log through `fold()` (never parsed here directly, R10), the backlog
(`docs/09-backlog/backlog.yaml`), the batch tables under `docs/09-backlog/batches/`, plan front
matter under `docs/01-plans/`, the house family templates, and two facts from git, the commit the
inputs were read at and that commit's date.

Determinism (R07, R08). Every page is a pure function of those inputs. The stamp is the source
commit and the commit's own date, never the time the generator ran, so two runs on one commit give
identical bytes. When an input has uncommitted changes the stamp says so, because the commit alone
would then misdescribe what was read. Pages are committed snapshots: nothing in CI compares them
with a fresh run, by the owner's ruling of 2026-09-30, since the idea log moves many times a day.

Every number on a page names its source, and where no record exists the page says "not recorded"
and names what is missing instead of estimating (R11). The derivation of each stage count and
gate queue is in `STAGES` and `GATES` below and is printed on the page beside the number.

    uv run python tools/generate_engine_pages.py                 # write _public/engine/
    uv run python tools/generate_engine_pages.py --out DIR       # write somewhere else

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--out` | output directory |  |  |  |

Exit codes found in source: 0.

<!-- generated:tool-reference:end -->
