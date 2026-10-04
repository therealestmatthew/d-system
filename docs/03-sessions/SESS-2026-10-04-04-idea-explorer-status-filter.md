---
schema_version: 1
id: doc-session-idea-explorer-status-filter
code: SESS-2026-10-04-04
title: List every schema idea status in the Idea Explorer filter
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-ui]
depends_on: []
---

# List every schema idea status in the Idea Explorer filter

## Phase

Unclaimed — owner-directed work, no backlog phase. `fix-idea-explorer-statuses` — make the Idea
Explorer's status filter cover every status in the idea schema's enum, with a test that asserts
coverage (idea 000556, assigned by the Session Manager with the owner's approval).

The work ran on `agent/fix-idea-explorer-statuses` and merged onto `dev` as `2e34704` before this
record was written. It is recorded afterwards, on the `phase-des-11` branch, at the owner's
direction.

## Verification

Run in the worktree after rebasing onto `dev` `d0e3304`, at `2e34704`:

`uv run python -m src.governance`

```text
Governance OK: 43 systems, 424 documents, 36 memories, 347 backlog phases
```

`uv run pytest`

```text
1403 passed, 1 skipped, 1 warning
```

`uv run python tools/check_no_private_content.py`

```text
check_no_private_content: OK (1140 tracked files, 0 identifiers checked)
```

The worktree cannot see `_private/portfolio/`, so that run read no identifiers. The Session
Manager's gate on `2e34704` ran the check with 31 identifiers and reported both changed files
clean. The diff contains only status names and a test.

The Session Manager's instruction also named these checks:

`uv run ruff check src/ test/`

```text
All checks passed!
```

`uv run mypy src/`

```text
Success: no issues found in 47 source files
```

`cd ts && npm run build`

```text
✓ built
```

## Acceptance

Self-declared from the owner's instruction; no backlog acceptance list exists for this session.

- The Idea Explorer's status filter lists every status in `schemas/idea.schema.json`'s
  `definitions.status` enum: Met. `STATUSES` in `ts/src/stage/IdeaExplorerRegion.tsx` holds the
  nine statuses in the enum's order. Before the fix it held five; `delivered`, `resolved`,
  `absorbed` and `set_aside` were missing.
- A test asserts that coverage: Met. `ts/` has no test runner, so the owner chose a pytest that
  reads the array from the `.tsx` source,
  `test_idea_explorer_status_filter_covers_every_schema_status` in `test/test_workbench_api.py`. It
  failed, naming the status, when `set_aside` was removed from the array.
- 000556's idea status is left unchanged: Met. Ideation moves it later.

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of backlog.yaml was changed.

## Unresolved

None.

## Review

A `demo-adversary` agent reviewed commit `69975e3` (later rebased to `2e34704`). Its report,
condition by condition:

- Verdict: PASS. No blocker, major or minor findings.
- The `STATUSES` list matches the schema enum exactly, in order, with no typos, extras or
  omissions.
- The test's regex was run against mutated copies of the source. A missing, extra or misspelled
  status failed. A double-quoted array failed loudly, because the pattern matches single quotes
  only. A type annotation or a renamed constant failed with "STATUSES array not found". An
  `as const` suffix still passed, correctly. A reordered list failed, because the comparison is
  list equality, which is stricter than the instruction required but not a defect.
- `ExplorerRegion.tsx` filters by plain string equality. The idea route's `_idea_row` returns
  `fold()`'s raw status strings, so the four new filter values match real rows.
- The diff touches exactly the two files named. `npm run build` succeeds.
- Report only, out of scope: `BacklogExplorerRegion.tsx`'s `STATUSES` already matches
  `schemas/backlog.schema.json`'s enum; it has no such gap.

## Decisions

The owner chose how to test a TypeScript constant in a frontend with no test runner. The choices
were a pytest that reads the `.tsx` source, no test with the gap reported, or adding vitest. The
owner chose the pytest. It is the first test in the suite that reads TypeScript source.

The owner approved the merge in the session that did the work, after the Session Manager's
GRANTED. The worktree and branch were removed with the owner's approval.

## Corrections

The first test draft had a line over the 100-character limit; ruff caught it and it was wrapped
before the commit. The session record itself was not written at the time. The owner directed that
it be written afterwards, here.

## Left undone

Nothing in scope. 000556's status change goes through Ideation.
