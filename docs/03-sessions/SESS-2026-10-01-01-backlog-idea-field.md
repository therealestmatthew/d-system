---
schema_version: 1
id: doc-session-backlog-idea-field
code: SESS-2026-10-01-01
title: Give backlog phases a structured idea field and backfill it (phase-des-08)
kind: session
status: active
owner: repository-owner
created: '2026-10-01'
updated: '2026-10-01'
systems: [sys-backlog]
depends_on: [doc-html-generation-design-system]
---

# Give backlog phases a structured idea field and backfill it (phase-des-08)

## Phase

`phase-des-08` — Give backlog phases a structured idea field and backfill it. Run by Session 5 -
Batch Runner as agent `agent-coord`, claimed at 3a4e87e with the owner's approval, on branch
`agent/phase-des-08`.

## Verification

Run in the worktree on 5014690, rebased onto dev 458ab36.

`uv run pytest`

```
1198 passed, 1 warning in 163.36s (0:02:43)
```

`uv run python -m src.governance`

```
Governance OK: 43 systems, 409 documents, 34 memories, 347 backlog phases
```

`uv run mypy src/`

```
Success: no issues found in 46 source files
```

Also run: `uv run ruff check src/ test/` gave `All checks passed!`, and
`uv run python -m src.governance --check-ideas` gave
`Idea field check: 100 phases name 167 ideas; 0 phases differ (0 missing, 0 extra)` with exit 0.

## Acceptance

- REQ-036 R17 holds (a fixture phase with a made-up id fails the validator naming it, and the
  committed backlog passes): Met. `test_ideas_field_rejects_an_id_the_idea_log_does_not_contain`
  asserts the exact error `phase-demo-01: ideas names 999999, which is not in _data/ideas.jsonl`,
  and the committed backlog, which now carries the field on 100 phases, passes governance above.
- REQ-036 R18 holds (the backfill's check mode reports no missing and no extra ids): Met.
  `--check-ideas` above reports 0 missing and 0 extra. `test_repository_idea_field_matches_its_backfill`
  asserts the same on every test run.

## Backlog

`status: active`, `agent: agent-coord`. `next_action`: built and verified; independent review of
the branch against REQ-036 R17 and R18, then READY to the Session Manager and the owner's merge
approval.

## Unresolved

- The backfill was run on dev 458ab36. Any later edit to a phase's scope, acceptance or next_action
  that names an idea id, merged before this branch, needs `--backfill-ideas` re-run after the rebase.
  The default governance run does not enforce the derived match; only `--check-ideas` reports it.
