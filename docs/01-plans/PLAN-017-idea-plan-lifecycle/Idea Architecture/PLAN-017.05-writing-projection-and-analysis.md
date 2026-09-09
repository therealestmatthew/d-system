---
schema_version: 1
id: doc-idea-plan-writing-projection
code: PLAN-017.05
title: Safe writing, projection, rendering and analysis
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-portfolio, sys-projection]
depends_on: [doc-idea-plan-lifecycle-requirements]
parent: doc-idea-plan-lifecycle
---

# Safe writing, projection, rendering and analysis

## What we know

**The write path has a live defect with a permanent consequence in the log.** Idea `000019` was
corrupted by shell command substitution inside a double-quoted argument. The tool's own docstring
(`tools/append_idea.py:20`) already shows the safe form — `--title "..."` with the body on stdin —
but `.claude/commands/idea.md:19` documents `--body "..."`, the form that caused the corruption.
`--title` has no stdin path at all, so a title containing a backtick or `$(` has no safe route in.

The corrupted record stays as it is. It is evidence, and repairing it is explicitly out of scope.

**Replay exists three times and diverges twice.** `tools/append_idea.py:100`,
`tools/rebuild_db.py:176`, `test/test_ideas.py:261`. The test fixture being a fourth copy rather than
a consumer is why the divergence went unnoticed: the test cannot detect a difference it reimplements.

**Two shipped tests are wrong.** `test_ideas.py:276` asserts time-in-state `>= 0` and the second
time axis produces `('triaged', -3600)`. `test_mixed_offsets_compare_as_the_same_instant` returns
`False` on the next status event written against any idea but `000019` — a latent failure
independent of everything proposed here.

**Only one of the six stated metrics is computable today.** Idea density from `created.at` needs
nothing new. Promotion rate, fizzle rate, time-in-state, time-to-resolution and duplication rate are
all blocked on status transitions occurring at all — not on schema richness.

## What we propose

### Make the safe path the only documented path

Give `--title` the same stdin route `--body` already has, and add a file-input form so prose reaches
the writer without passing through a shell at all. Then rewrite `.claude/commands/idea.md` so the
form it shows is the safe one. The command file is what an agent copies; leaving the dangerous form
in the example is the actual bug, and it is a documentation fix as much as a code one.

What this promises is bounded: prose that reaches the writer intact is stored intact. It cannot
recover prose an arbitrary caller's shell already mangled before the tool saw it.

### One replay, imported everywhere

Move replay into `src/` as a single importable function and delete the other three copies. The
writer, the rebuild, the renderer and the tests all consume it. A divergence test between three
implementations is not an acceptable substitute: every status branch is unexercised, so three wrong
implementations would agree and the test would pass.

Validation runs before mutation, in both directions — before an append, and before
`rebuild_db.py:88-90` drops every table in the database.

### Raw and effective stay separately queryable

`idea_events` keeps every line, including amendments, retractions and annotations, at full fidelity.
The folded `ideas` table holds effective current state. Both are projections of the log and neither
replaces it.

Because amendments are timestamped events, "what did we believe on date D" is answered by replaying
to D — the corrected value appears from the amendment's own timestamp forward, never before it. A
correction records when the mistake was noticed; it does not pretend the right answer was always
there.

### Rendering

`docs/00-working/ideas.md` shows effective current state — corrected prose, no per-idea amendment
badge. This follows the owner's decision and is not reopened here. The raw history remains available
through `idea_events`, so nothing is hidden; it is merely not in the summary view.

Agent findings collapse by default. Without that, one triage run over 19 ideas makes the file
unreadable, which would defeat the only view anyone actually opens. Rendering stays deterministic:
same events in, same bytes out, across processes and hash seeds, so `--check` can detect staleness.

### Analysis, scoped to what can be honestly measured

Every reported metric declares its population, its cutoff, its time axis and how missing data is
treated. Where a denominator is zero the metric reports that it is unavailable rather than reporting
zero. Corrections and annotations are not captures and never enter a capture count.

Duplication rate and ideas-per-session are **not delivered**: neither has a definition, and no
session identifier exists on an event to compute the second. The six-metric list came from an
assistant proposal at transcript 714-724, not from the owner; it is carried as a proposal.

## What is open

- Whether the file-input form supersedes stdin or joins it. Recommend both: stdin for pipelines,
  a file for prose an agent has already written to disk.
- The collapse threshold for findings, and whether it is per idea or per render.
- Whether `--check` failing should block a commit or only report. Recommend report until the
  renderer has run in anger a few times.
- Fixing the two broken tests requires synthetic later events. They must be built in a fixture and
  never written to `_data/ideas.jsonl` — the repair must not manufacture history to pass a test.

## What it touches

`tools/append_idea.py`, `tools/rebuild_db.py`, `tools/generate_ideas_md.py`, the new replay module
in `src/`, `test/test_ideas.py`, `.claude/commands/idea.md`, `sql/001_schema.sql`, and the generated
`docs/00-working/ideas.md`. It writes no production idea data.

## How it is verified

`R01`-`R04`, `R08`, `R10`, `R17`. Prose containing backticks, `$(...)`, quotes, newlines and
non-ASCII survives the real CLI in an isolated fixture, with an assertion that no sentinel command
executed. Import tracing proves one replay implementation and one transition table. Negative
fixtures — duplicate creation, unknown idea, mismatched `from`, illegal transition, second revisit —
each leave the log and database unchanged, and a failed first rebuild leaves no data directory
behind. The existing log's byte prefix is unchanged by every test in the suite. Synthetic SQL
results with known durations prove no negative time-in-state and correct denominators.

## Conflicts with other categories

`C04` is the sharpest: the clean folded view is the owner's decision, and the argument that
corrections become invisible in the only artifact anyone reads is answered by raw queryability
rather than by re-asking. `C14` bounds analysis to synthetic transitions until real ones exist.
`C15` limits what can be claimed about history: current metadata cannot reconstruct past plan
states, and the planned history squash means git is not an archival fallback. `C16` and `C20` land
in `PLAN-017.06` and `PLAN-017.01` respectively.
