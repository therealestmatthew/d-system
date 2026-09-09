---
schema_version: 1
id: doc-session-source-preflight
code: SESS-2026-09-06-05
title: Source preflight before rebuild
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-contracts, sys-projection]
depends_on: [doc-reliability-follow-up, doc-backlog-decisions]
---

# Source preflight before rebuild

Executed `phase-rel-02` as `agent-architect`, the front of `next_up` after `phase-cap-02`
integrated, in a worktree at `../d-system-worktrees/phase-rel-02`.

## Outcome

`src/db/source_validation.py` validates every `_data/` JSON file and every `brain/` entry's front
matter against the schemas in `schemas/`, and returns a list of `SourceError(path, field, message)`.
`tools/rebuild_db.py` calls it as the first statement of `rebuild()` — before `mkdir`, before
`duckdb.connect`, and well before the eight `DROP TABLE` statements. On failure it prints every
problem and exits 1 without touching the filesystem.

That ordering is the whole point. The rebuild drops all eight tables and then inserts, so a file
that failed partway through used to leave an empty database in place of a working one. Validation
is also complete rather than fail-fast: someone repairing source files wants the full list, not one
error per run.

Two behaviours worth naming because they are easy to lose in a later edit:

- **Missing entity directories are not errors.** `_data/tasks/`, `_data/interactions/` and the rest
  do not exist until capture creates them, so the preflight skips a directory it does not find.
- **`brain/index.md` is excluded.** It is a hand-written table of contents, not a memory, and the
  loader has always skipped it.

## Verification

- `uv run pytest test/test_source_validation.py` — 37 passed.
- `uv run pytest` — 264 passed.
- `uv run ruff check src/ test/` — clean. `uv run mypy src/` — clean, 11 files.
- `uv run python -m src.governance` — exit 0.
- `uv run python tools/rebuild_db.py` — 33 projects, 28 tags, 7 memories.

Acceptance was checked against the real tree, not only fixtures. With `last_reviewed` set to
`2026-13-45` and `review_cadence` set to `ongoing` in one project file, the rebuild printed both
problems with file and field and exited 1, and the existing database still held its 33 project rows
afterwards. With a front-matter-less Markdown file added under `brain/`, it reported
`missing YAML front matter` and exited 1. Both files were then restored.

## What the preflight found on first run

**Every brain entry failed.** `created: 2026-09-05` unquoted is resolved by PyYAML to a
`datetime.date`, and `schemas/memory.schema.json` declares a string. All seven entries failed on
`created` and `updated`.

This is a serialization difference, not bad data, so it is fixed in the validator rather than by
rewriting seven files to quote their dates: `_normalize_yaml_dates` renders date objects back to
ISO strings before validation. The conversion cannot hide a bad date — YAML only produces a date
object for something it already parsed as one, so `2026-13-45` stays a string and still fails the
format check. Both spellings are covered by tests so a future edit cannot quietly drop one.

**A leap-year assertion of mine was wrong**, and the checker caught it: 2026-02-29 is not a day.
The case was kept as a rejection test, since it is exactly what a regex-shaped date check waves
through.

## Change made outside the phase's stated scope

`tools/rebuild_db.py` read `p.get("commitment_cadence")`, which `phase-cap-02` had just renamed.
Left alone, the loader would have written null cadence for all 33 projects while reporting a
successful rebuild — the silent-loss failure this phase exists to prevent, introduced by the phase
before it. The read is now `review_cadence`. The DuckDB *column* is still named
`commitment_cadence` and renaming it is `phase-cap-07`'s work; the insert is positional, so the
values land correctly in the meantime. Verified: 33 rows carry a cadence and none is null.

## Unresolved

- **`test/test_schemas.py` does not enable the format checker.** The preflight does, so a bad date
  fails the rebuild but passes the contract tests. Nothing is wrong today, but the two disagree
  about what a valid date is and the next person to add a date field will meet whichever they hit
  first.
- **`tools/load_context.py` fails `ruff check tools/`.** A pre-existing F541 unrelated to this
  phase. The documented lint gate is `ruff check src/ test/`, which passes; `tools/` has never been
  in it. Not fixed here because the file belongs to `phase-priv-02`.
- **The preflight is not wired into anything but `rebuild_db.py`.** The FastAPI app reads the
  database, not the source tree, so nothing else needs it yet. A capture pipeline writing to
  `_data/` should call `validate_sources` before it writes, and `phase-cap-06` is where that
  decision lands.
