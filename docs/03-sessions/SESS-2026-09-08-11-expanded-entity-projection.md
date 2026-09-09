---
schema_version: 1
id: doc-session-expanded-entity-projection
code: SESS-2026-09-08-11
title: Project the expanded entity model into DuckDB
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-projection]
depends_on: [doc-capture-build]
---

# Project the expanded entity model into DuckDB

## Phase

`phase-cap-07` — Project the expanded entity model into DuckDB.

## Verification

`uv run pytest test/test_rebuild.py`:

```
14 passed, 2 warnings
```

`uv run python tools/rebuild_db.py`:

```
Rebuilt: data/d_system.duckdb
  projects: 34 rows
  people: 0 rows
  tags: 28 rows
  commitments: 0 rows
  tasks: 0 rows
  interactions: 0 rows
  decisions: 0 rows
  waiting_on: 0 rows
  development_events: 0 rows
  memories: 13 rows
  ideas: 45 rows
  idea_events: 46 rows
```

Also run, beyond the phase's own list: `uv run pytest` — 386 passed, 2 warnings. `uv run python -m
src.governance` — exit 0. `uv run ruff check src/ test/` — one pre-existing failure in
`src/governance/__main__.py` (unsorted import block), confirmed on `dev` before this branch and
untouched by this change; `uv run ruff check tools/rebuild_db.py` — clean (not in the documented
gate, checked anyway since this phase rewrote the file). `uv run mypy src/` — clean, 15 files.

## Acceptance

- Fixtures for each new type load and survive a rebuild unchanged — Met.
  `test_new_type_fixture_survives_a_rebuild_unchanged` (parametrized over interaction, decision,
  waiting-on, development-event) is in the 14 passed above.
- A task loads with neither parent, with either, and with both — Met.
  `test_task_loads_with_any_combination_of_parents` covers all four combinations.
- `last_touched` exists only in the projection and advances when an interaction is added — Met.
  `test_last_touched_not_present_in_any_source_file` confirms no schema declares the field;
  `test_last_touched_advances_when_an_interaction_is_added` confirms the view moves from
  `2026-09-01` (a commitment) to `2026-09-15` (a later interaction) across a rebuild.
- `last_reviewed` is unchanged by activity — Met. `test_last_reviewed_is_unchanged_by_activity`
  adds an interaction and confirms `projects.last_reviewed` stays `2026-08-01`.
- The unfiled view returns exactly the parentless fixtures (REQ-002 R19) — Met.
  `test_unfiled_view_returns_exactly_the_parentless_fixtures` builds two filed and two unfiled
  fixtures (a commitment and a task each) and asserts the view returns exactly the two unfiled
  ones.

## Backlog

`phase-cap-07`: `status: active`, `agent: agent-cap07`. `next_action`: all five acceptance
conditions are met and verification has been run in this worktree; ready for `/session-close`.

## Unresolved

None on this phase.

## Review

Independent sub-agent review, given the phase's scope/acceptance/verification (including the note
that the fifth acceptance condition was a deliberate correction added during orientation, not
scope creep), REQ-002's R18/R19/R20/R21/R24, the commit range `the commit “Claim phase-cap-07 for agent-cap07”..HEAD`, and this session
record, with instructions to rerun everything itself rather than trust the record. Reported
verbatim:

> Status remains `active`, not yet `complete` — correctly deferred to session-close, consistent
> with expectations for this review. Everything checks out cleanly.
>
> **Condition 1 — Fixtures for each new type load and survive a rebuild unchanged.** Holds.
> `test_new_type_fixture_survives_a_rebuild_unchanged` is parametrized over
> interaction/decision/waiting-on/development-event; all 4 variants pass in the observed `14
> passed` run of `uv run pytest test/test_rebuild.py`. `sql/001_schema.sql` (lines defining
> `interactions`, `decisions`, `waiting_on`, `development_events`) match the corresponding JSON
> schemas' property sets field-for-field; the schema-only `capture` property is omitted from all
> four tables, consistent with the pre-existing (unrelated to this phase) omission of `capture`
> from `commitments`.
>
> **Condition 2 — A task loads with neither parent, with either, and with both.** Holds.
> `test_task_loads_with_any_combination_of_parents` is parametrized over exactly the four
> combinations (`neither`, `commitment-only`, `project-only`, `both`) and all pass.
> `sql/001_schema.sql` confirms `tasks.commitment_id` and `tasks.project_id` both lost `NOT NULL`;
> `commitments.project_id` also lost `NOT NULL`.
>
> **Condition 3 — `last_touched` exists only in the projection and advances when an interaction is
> added.** Holds, and is genuinely a derived view, not a stored column: `sql/003_capture_views.sql`
> defines `project_last_touched` as `SELECT project_id, MAX(activity_date) ... GROUP BY project_id`
> over a `UNION ALL` of interactions/commitments/tasks/decisions — there is no `INSERT`/`UPDATE`
> into it anywhere in `tools/rebuild_db.py`. `test_last_touched_advances_when_an_interaction_is_added`
> rebuilds once with only a commitment (`last_touched` = `2026-09-01`), then rebuilds again after
> adding an interaction dated later (`2026-09-15`) and asserts the value moved — a real before/after
> check across two rebuilds, not a static assertion. `test_last_touched_not_present_in_any_source_file`
> checks all schemas lack the field; since every schema has `additionalProperties: false` and
> `validate_sources()` gates every rebuild, this is a valid, arguably stronger proxy for "no
> `_data/` file contains it" than a literal grep would be.
>
> **Condition 4 — `last_reviewed` is unchanged by activity.** Holds.
> `test_last_reviewed_is_unchanged_by_activity` adds an interaction and asserts
> `projects.last_reviewed` (a stored column, untouched by the rebuild logic for interactions) stays
> `2026-08-01`. Confirmed `rebuild_db.py`'s project-insert path only reads `p["last_reviewed"]`
> from the project's own JSON, never derives it.
>
> **Condition 5 — The unfiled view returns exactly the parentless fixtures (REQ-002 R19).** Holds
> and is non-vacuous. `sql/003_capture_views.sql`'s `unfiled` view unions all six entity tables
> filtered on `project_id IS NULL`. The test builds two entity types (commitment, task) each with
> one filed and one unfiled fixture, and asserts the result is exactly `[("commitment","c-2"),
> ("task","t-2")]` — a real filter check across multiple types, not an empty-result trivial pass.
>
> **Verification reruns:** `uv run pytest test/test_rebuild.py` → `14 passed, 2 warnings`. `uv run
> python tools/rebuild_db.py` → succeeds against the real repo (rows are 0 for
> people/commitments/tasks/interactions/decisions/waiting_on/development_events because `_data/`
> currently has no real fixtures for those types beyond `.gitkeep` — pre-existing state, not a
> regression). `uv run pytest` (full suite) → `386 passed, 2 warnings`. `uv run python -m
> src.governance` → `Governance OK: 16 systems, 99 documents, 13 memories, 101 backlog phases`.
>
> **Other checks.** Confirmed via diff that the old embedded-task loop (`for i, t in
> enumerate(c.get("tasks", []))`) is entirely gone from `tools/rebuild_db.py`, replaced by a
> `_glob(data / "tasks", "*.json")` loop. `project_last_touched`'s activity union correctly
> excludes `waiting_on`, matching R21's literal wording — the session record calls this out
> explicitly and it is accurate, not an oversight. No discrepancies found between the session
> record's claims and the actual diff/rerun results — all five acceptance conditions genuinely
> hold.

No discrepancy stood.

## Decisions

- Orienting on `phase-cap-07`, found scope item 4 ("add the unfiled view for parentless records")
  had no corresponding acceptance condition, even though `REQ-002` (this phase's own source
  document) defines exactly this as R19 with its own stated verification method. Asked the owner,
  who chose to add R19's acceptance condition before implementation rather than proceed with the
  gap. Done before any code was written.
- Chose `phase-cap-07` over the still-front-of-queue `phase-idea-02` (see the prior session's
  decision to skip it — unchanged this session) and over the other `next_up` phases, since it was
  next in queue order once `phase-idea-02` was set aside.

## Corrections

None this session. (The correction recorded in the prior session, about `rfc3339-validator` not
being needed for `phase-rel-11`, belongs to that session's record, not this one.)

## Left undone

Nothing on `phase-cap-07` itself — all five acceptance conditions hold per both the checkpoint
rerun and the independent review. Noted but out of scope:

- The primary checkout has accumulated several new untracked files
  (`docs/00-working/gemini-knowledge-retrieval-*.md`, `split_report.py`) that neither this session
  nor the prior one created, suggesting a separate concurrent session is actively working in the
  same checkout. Left untouched; worth the owner's attention if unexpected.
- `phase-idea-02` still carries the stale `next_action` noted in the prior session's close — not
  corrected here either, since the owner has twice chosen to skip rather than fix it.

## Notable implementation choices

- `tools/rebuild_db.py`'s `rebuild()` now takes an optional `root: Path | None` parameter (default
  the real repository root), and `_parse_memory()` takes `root` explicitly instead of reading a
  module-level constant. Neither function had a way to point at a temporary tree before, and
  without it `test/test_rebuild.py` would have had no way to exercise a rebuild without mutating
  the real `_data/`/`data/`. `validate_sources()` already took a `root` parameter for the same
  reason, so this makes the two consistent rather than introducing a new pattern.
- `last_touched` is a SQL view (`project_last_touched` in `sql/003_capture_views.sql`), not a
  stored column populated after the fact, so it structurally cannot drift from the rows it
  summarizes — there is no update statement to forget to run.
- Views are dropped before tables on every rebuild (`VIEWS_DROP_ORDER`, executed first): DuckDB
  refuses `DROP TABLE` while a view still references it.
- `waiting-on` is excluded from `last_touched`'s activity sources, matching REQ-002 R21's own list
  ("interactions, commitments, tasks and decisions") — not an oversight.
- `tasks.sort_order` is kept in the schema (default `0`, always inserted as `0`) rather than
  removed, since nothing in scope asked for its removal and nothing currently reads it; it lost its
  only source of meaning (array position within a commitment) but removing an unused column wasn't
  part of this phase's scope.
- `_data/tasks/.gitkeep` tracks the new empty directory, following the existing `_working/.gitkeep`
  precedent in this repository rather than inventing a new convention.
