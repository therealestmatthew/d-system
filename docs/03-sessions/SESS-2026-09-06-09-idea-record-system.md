---
schema_version: 1
id: doc-session-2026-09-06-09
code: SESS-2026-09-06-09
title: Build the idea record system
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-portfolio, sys-projection, sys-governance, sys-contracts]
depends_on: [doc-idea-record-system, doc-idea-staging]
---

# Build the idea record system

## What happened

`phase-idea-01` delivered the idea record system: `docs/00-working/ideas.md` stopped being a
hand-maintained markdown list and became a generated view over `_data/ideas.jsonl`, an append-only
event log with a schema, a sanctioned writer, a DuckDB projection and an enforcement test.

Four defects in the phase were found while orienting and corrected before any code was written. The
owner decided each through the question tool.

## Decisions taken during the session

### The migration override was replaced, not guarded

`PLAN-016` specified an `--at` override on `tools/append_idea.py`, gated behind a migration flag,
recorded in the event and covered by a test asserting ordinary invocation could not reach it.

The owner proposed the alternative that was adopted: a separate `tools/backfill_ideas.py`, run once
and then deleted, with `append_idea.py` never gaining a timestamp argument at all. A guard proves the
lock holds but leaves the door — the argument would sit in the shipped interface permanently, one
flag away from anyone reading `--help`. Deleting the migrator leaves no door, and the assertion about
the writer becomes structural (*the option does not exist*) rather than behavioural (*the guard held
on the inputs tried*).

Two conditions made this a closed door rather than a moved one, and both are in the delivered work:
the migrator imported its event construction from `append_idea.py` rather than reimplementing it, and
its deletion is an acceptance condition rather than an intention. The tool is gone rather than
archived — `phase-priv-05` squashes this repository before any remote exists, so history is not a
place anything survives. What it did is recorded in `PLAN-016`, and `_data/ideas.jsonl` is the
result.

`PLAN-016` was amended to record the supersession rather than left contradicting the code.


### Three phase defects were corrected before claiming

- **The phase said ten entries; there were thirteen.** `PLAN-016` already carried the correction
  ("every entry created before the writer exists"), so the phase text was the stale copy. Migrating
  ten would have silently stranded three.
- **"Expose it as a custom tool" had no deliverable and no acceptance condition**, so the phase could
  have passed with the bullet unbuilt. Now `.claude/commands/idea.md`, with a test.
- **The ADR-010 amendment had no acceptance condition.** Governance does not detect an ADR
  contradicting reality.

## Outcomes

- `schemas/idea.schema.json` states the status machine once. `tools/append_idea.py` and the tests
  read the transition table out of it rather than restating it.
- All thirteen entries migrated with their original timestamps, verified against the markdown before
  the migrator was deleted. Every body round-tripped byte-identically; only the header changed.
- `idea_events` is retained in full and the DDL says why, so the constraint travels with the code.
  Point-in-time reconstruction is tested: eight ideas existed at `2026-09-06T15:00:00-04:00`.
- The source preflight now validates every line of the log, including ordering — an event with no
  preceding `created` cannot be folded into any state, and a per-line schema cannot see that.

## Evidence

    uv run pytest                     285 passed, 2 warnings in 1.77s   (19 new)
    uv run python -m src.governance   Governance OK: 16 systems, 56 documents, 8 memories, 88 phases
    uv run python tools/rebuild_db.py ideas: 13 rows, idea_events: 13 rows

The append-only test was verified by mutation rather than assertion: altering a committed line in
`_data/ideas.jsonl` fails `test_no_committed_line_in_the_log_is_ever_altered` and the generated-view
test with it. It checks against `git show HEAD:_data/ideas.jsonl` rather than a recorded digest,
because a digest has to be updated on every append, and a check that is routinely updated is a check
that will eventually be updated over a real change.

## Corrections and unresolved items

**`dev` was left red by the claim commit.** `--catalog` prints rather than writes, and the
regeneration run was redirected to `/dev/null`, so `docs/08-governance/catalog.md` went stale while
`test_committed_catalog_matches_regenerated_output` failed on `dev` for three commits. Fixed with the
ADR-010 amendment and green on integration. The mistake was assuming a documented "regenerate" step wrote a
file without checking that it did.

**`date-time` format validation is inert repository-wide.** `jsonschema` only checks the `date-time`
format when `rfc3339-validator` is installed, and it is not a dependency — so `format: "date-time"`
currently validates nothing anywhere in `schemas/`. `schemas/idea.schema.json` therefore enforces its
timestamps with a `pattern` as well, and keeps the keyword as the declaration. This confirms the
premise of **`phase-rel-11`** (*make the contract tests and the source preflight agree about dates*)
and gives it a concrete first action: add the dependency. It was left alone as that phase's work
rather than taken here.

**Both new tables were unreadable from Python, and the tests missed it.** DuckDB returns a
`TIMESTAMP WITH TIME ZONE` through `pytz`, which was not a dependency, so any query returning
`idea_events.occurred_at` or `ideas.created` raised instead of yielding a row — while `count()`,
`sum()` and `date_diff()` over the same column kept working. The two projection tests written here
only aggregated, so they passed against tables no caller could read. Found while checking an
unrelated question about mixed UTC offsets; nothing had hit it because nothing reads these tables
yet. Fixed by adding `pytz` to the runtime dependencies, plus a test that fetches a row rather than
aggregating over one, verified to fail in a `pytz`-free environment.

The lesson is narrower than "test more": verifying that a *query* runs is not verifying that a
*result* can be read, and an aggregate hides the difference.

**A pre-existing lint failure sits outside the documented gate.** `uv run ruff check tools/` fails on
`tools/load_context.py:101` (`F541`, f-string without placeholders). The documented command in
`AGENTS.md` is `ruff check src/ test/`, which passes, so `tools/` has never been linted — every
script there is unchecked. Pre-existing on `dev` and untouched here. **Already recorded** in
[GOV-003](../08-governance/GOV-003-backlog-decisions.md) and owned by `phase-rel-09`, which covers
both the F541 and widening the documented command — it was reported in session as a fresh finding
before that record was checked.
