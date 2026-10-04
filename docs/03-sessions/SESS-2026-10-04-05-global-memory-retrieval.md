---
schema_version: 1
id: doc-session-global-memory-retrieval
code: SESS-2026-10-04-05
title: Correct global-memory and all-results retrieval
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-retrieval]
depends_on: [doc-reliability-follow-up]
---

# Correct global-memory and all-results retrieval

## Phase

`phase-rel-08` — Correct global-memory and all-results retrieval.

## Verification

The phase's one verification entry is prose: "Run focused context-query and CLI tests on a temporary
memory database." Done by running the focused suite, which seeds a temporary DuckDB from the shipped
DDL and drives both `load()` and `main()`:

`uv run pytest -q test/test_load_context.py test/test_tool_docs.py`

```
29 passed, 1 warning
```

The same new tests run against dev's `tools/load_context.py` (pre-change): `14 failed, 8 passed`,
so they exercise the change and do not pass by default.

Against the real brain projection, `--project example-project -n 100` returned 0 memories before the
change and 30 after; `--all` returns all 36; `--all -n 4` returns 4.

## Acceptance

- A project query includes global and matching project entries but excludes unrelated
  project/session entries — `Met`.
  `test_project_query_includes_globals_and_own_entries_only`,
  `test_project_query_excludes_unrelated_project_and_session_entries`,
  `test_repository_scoped_globals_reach_every_project` and
  `test_d_system_project_query_adds_its_project_scoped_entry` pass.
- A corpus larger than ten entries verifies --all, explicit limits, tag conjunction and stable
  ordering — `Met`. The 13-memory corpus (`test_corpus_is_larger_than_the_default_limit`) backs
  the `--all`, limit, tag, ordering and CLI tests, all passing.

## Backlog

`status: active`, `agent: agent-builder-b`. `next_action`: every acceptance condition met on
`agent/phase-rel-08`; awaiting the owner-approved merge, then the completion edit on dev.

## Unresolved

None.

## Review

Independent adversarial review by a fresh `demo-adversary` sub-agent (a demo-track reviewer type,
used because the roster has no retrieval- or governance-specific adversary), range `dev...HEAD` at
`8948b36`. Its findings, as reported:

- **Project query includes global and own entries, excludes unrelated ones — Met.** The clause
  `(project_id = ? OR scope = 'global')` is a faithful reading of GOV-003's ruling. Scope is never
  NULL: `sql/001_schema.sql` defaults it to `'global'` and `tools/rebuild_db.py` inserts
  `mem.get("scope", "global")`. Real DB: `--project example-project -n 100` returns 0 on dev's
  tool and 30 on the branch. The corpus covers the cases real data cannot: `s-null` (session, no
  project) is now excluded, where the old `project_id IS NULL` clause included it.
- **Corpus larger than ten verifies --all, limits, tag conjunction and stable ordering — Met.**
  13 rows; the hand-written `ORDER` was recomputed independently and matches. Focused suite
  `29 passed`; the new tests against dev's tool `14 failed, 8 passed`, so they test the change. The
  `id` tie-break is load-bearing (`g-tie-a`/`g-tie-b`). `--all` unbounded and `--limit` capping it
  verified through `load()`, the CLI and the real DB (36 and 4).
- Other checks: ruff and mypy clean on both files; `generate_tool_docs.py` reports 0 updated, so
  OPS-003's block is exact and its narrative matches the code; catalog regenerates byte-identical;
  the diff touches only the declared deliverables plus the session record, the phase's own
  `next_action` and the catalog; `int(limit)` hardens programmatic callers; the only other importer
  (`research/evidence/review_probes.py`) does not rely on the old default.
- **Informational:** a session memory carrying the queried project (`s-alpha` for `alpha`) is
  included. GOV-003 does not address it; "unrelated" reads naturally as other projects, and the
  pre-change behaviour included own-project entries regardless of scope.
- **Pre-existing, not introduced:** `--limit -1` crashes with a raw `duckdb.BinderException`
  traceback, identically on dev. Outside this phase's scope.

Disposition: both accepted. The own-project session case keeps pre-change behaviour and fits the
acceptance wording. The negative-limit crash was sent to Ideation as a separate idea rather than
fixed here, because input validation is not in this phase's scope.

## Decisions

The owner approved adding OPS-003 to the phase's deliverables at claim time, because changing the
`--limit` default from 10 to `None` (needed to tell an explicit `--limit` from the default) changes
the generated reference block. The scope rule follows GOV-003's existing ruling: `scope` is the
authority, so a global memory is included whatever project it carries. `--all` still ignores the
other filters; the phase changed only its limit. An `id` tie-break was added to the ordering because
the acceptance asks for stable ordering and ties on confidence and date were otherwise unordered.
The pre-existing mypy error in the tool (`params` unannotated) was fixed because the file is a
deliverable and the fix is one line.

## Corrections

The focused test file was run twice while the preflight full suite was still running in the same
worktree, against the Session Manager's contract item 10 (one pytest run at a time per worktree).
The catalog was not affected, and because code changed mid-run, that run was not counted as the
baseline: a clean full run on the committed branch gave 1427 passed, 1 skipped (1410 baseline plus
17 new tests).

## Left undone

The completion edit on dev waits for the owner-approved merge. Rejecting non-positive `--limit`
values cleanly is a separate idea.
