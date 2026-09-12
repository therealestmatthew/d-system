---
schema_version: 1
id: doc-ops-build-idea-corpus
code: OPS-015
title: Build the idea-batching analyst corpora
kind: operation
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems: [sys-portfolio, sys-backlog]
depends_on: [doc-governance-operations]
---

# Build the idea-batching analyst corpora

## Trigger

Run at the start of the idea-batching build session, as step 2 of the delegation pack's
kickoff ([PROMPT-032](../02-prompts/PROMPT-032-idea-batching-delegation-pack.md)), before any
analyst is dispatched. Re-run it whenever the idea log or the demo fast lane's exclusion file
moves and the corpus needs rebuilding.

Also useful on its own with `--stats`, which reports what the corpus *would* contain without
writing anything — the cheapest way to answer "how many ideas are actually in the batch right
now".

## Command

```bash
uv run python tools/build_idea_corpus.py                 # build, drawing and recording a seed
uv run python tools/build_idea_corpus.py --seed 1234     # reproduce an earlier run exactly
uv run python tools/build_idea_corpus.py --stats         # report only, write nothing
```

## Expected result

Four corpus files and a manifest in `_working/idea-corpus/`, which is gitignored — the corpora
are analyst input, not a tracked artifact.

The four files hold the **same ideas**. They differ in exactly two controlled ways, and both
variations live in the files rather than in the analysts' prompts, so no analyst can infer that
its input differs from anyone else's:

| File | Content | Order |
|---|---|---|
| `corpus-R1.md` | title, body, links, findings | id ascending |
| `corpus-R2.md` | title, body, links, findings | id descending |
| `corpus-R3.md` | title, body, links, findings | shuffled under the recorded seed |
| `corpus-R4.md` | title, body, links | id ascending |

`corpus-R4.md` is the bias control. Nearly every triaged idea carries a finding written by one
agent charter, so a grouping the control reproduces *without* findings is not inherited framing.
Its file must never mention findings anywhere — not in an entry, not in the header — because a
control that can tell it is a control is not one. Ideas whose own body text happens to use the
word are not a leak; a `### Findings` section, a `LAYERED EVIDENCE` marker or an author byline
would be.

`manifest.json` records what the analysts actually received: corpus size, the shuffle seed, the
ids the fast lane excluded, the ids it recorded but returned, the layered-evidence set, and the
per-author finding counts. **The build session reads this file rather than assuming a count.**

## What the corpus is

The `triaged` ideas, minus every id the demo fast lane's exclusion file
(`docs/00-working/demo-fast-lane-exclusions.yaml`) records with disposition `queued` or `fixed`.

`promoted`, `discarded` and `open` ideas are all outside the corpus. `open` is excluded by the
same status filter rather than by a special case: the corpus is what has been triaged, and an
idea captured after the sweep begins simply is not in it.

An idea the fast lane recorded as **`dropped`** stays *in* the corpus. That is the point of
recording disposition rather than bare membership — an idea the fast lane considered and did not
ship returns to the batching corpus rather than falling between the two lanes
([PROMPT-025](../02-prompts/PROMPT-025-idea-batching-pre-plan-package.md) decision 14).

A **missing exclusion file is not an error**: it means an empty exclusion set. The fast lane and
the batching pack are deliberately independent, and the pack must be runnable before the fast
lane has finished.

"Findings" means every annotation with `kind == "finding"`, **any author**, in chronological
order. `fold()` returns annotations as a flat list mixing `note`, `finding` and `assessment`
kinds from several authors, so the tool filters by kind rather than assuming one tidy triage
finding per idea. Ideas carrying more than one finding are flagged; the set is **computed, never
hard-coded**, because the log is append-only and the set changes — it was eight across the raw
135 and is seven across the 129-idea corpus, because `000107` left with the fast lane.

## Failure and recovery

Exits 1 if no triaged ideas are selected at all, which means the status filter or the exclusion
file is wrong — check `--stats` before rebuilding.

If a number looks wrong, the defect is almost always in the event log or the exclusion file
rather than in this script. Fix the log through `tools/append_idea.py`
([OPS-005](OPS-005-append-idea.md)) and the exclusion file by hand; never edit a corpus file, as
it is regenerated.

To reproduce a previous run exactly, pass the `shuffle_seed` from that run's `manifest.json` to
`--seed`. Without it a fresh seed is drawn, and `corpus-R3.md`'s ordering will differ.

<!-- generated:tool-reference:start -->

### Reference: `tools/build_idea_corpus.py`

Assemble the idea-batching analyst corpora from the folded idea log.

Builds one corpus file per analyst for the idea-batching build (PROMPT-032), plus a
manifest recording what the analysts actually received. The corpus is the `triaged`
ideas minus every id the demo fast lane consumed, so it is smaller than the log and
changes whenever either moves — which is why the build session reads the manifest
rather than assuming a number.

Four analysts read the same ideas under two controlled variations, and the variations
live in the FILES rather than in the prompts, so no analyst can infer that its input
differs from anyone else's:

    corpus-R1.md   title, body, links, findings   id ascending
    corpus-R2.md   title, body, links, findings   id descending
    corpus-R3.md   title, body, links, findings   shuffled under the recorded seed
    corpus-R4.md   title, body, links             id ascending   <- the control

R4 is the bias control: nearly every triaged idea carries a finding written by one agent
charter, so a grouping R4 reproduces without findings is not inherited framing. Its file
is built by the same code path with findings withheld.

"Findings" means every annotation with kind == "finding", ANY author, in chronological
order. fold() returns annotations as a flat, unfiltered list mixing note, finding and
assessment kinds from several authors, so this filters by kind rather than trusting a
single-author assumption. Ideas carrying more than one finding are flagged in the corpus
as layered and possibly contradictory evidence; the set is computed, never hard-coded,
because the log is append-only and the set grows.

    uv run python tools/build_idea_corpus.py                    # build, random seed
    uv run python tools/build_idea_corpus.py --seed 1234        # reproduce a run
    uv run python tools/build_idea_corpus.py --stats            # report only, write nothing

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--seed` | shuffle seed for R3; a random one is drawn and recorded if omitted |  |  |  |
| `--out` | output directory (default: _working/idea-corpus) |  |  |  |
| `--exclusions` | fast-lane exclusion file; a missing file means an empty exclusion set |  |  |  |
| `--stats` | report the corpus facts and write nothing |  |  |  |

Exit codes found in source: 0, 1.

<!-- generated:tool-reference:end -->
