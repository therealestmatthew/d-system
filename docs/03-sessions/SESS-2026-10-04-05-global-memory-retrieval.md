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
