---
schema_version: 1
id: doc-session-dev-lint-and-type-fixes
code: SESS-2026-09-23-04
title: Fixing dev's ruff findings and the broker's mypy error
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-api, sys-governance]
depends_on: []
---

# Fixing dev's ruff findings and the broker's mypy error

## Phase

Unclaimed: owner-directed work with no backlog phase, relayed by the Session Manager on 2026-09-23.
Peers held no lock against it. Branch `agent/fix-dev-lint`, worktree
`../d-system-worktrees/fix-dev-lint`.

## What changed

`dev` failed `uv run ruff check src/ test/` with 16 findings and `uv run mypy src/` with one error.

- **ruff, auto-fixed (10):** `datetime.timezone.utc` became `datetime.UTC` in `src/broker/` and
  `test/test_broker.py`. The two are the same object on Python 3.11 and later. `Iterable` is now
  imported from `collections.abc`, and quoted annotations lost their quotes. `--unsafe-fixes` was
  not used.
- **ruff, by hand (6):** five E501 lines wrapped, in `src/governance/__main__.py`,
  `test/test_governance.py` and `test/test_idea_dispatch.py`. One unused `idea_id` assignment
  removed in `test/test_idea_dispatch.py`, keeping the call that creates the idea.
- **mypy (1):** `src/broker/__main__.py` assigned the stdin payload's `capability` field, typed
  `object`, to `str | None`. It is now narrowed with `isinstance`. This changes one behaviour, and
  the owner chose it over a `cast`: a truthy `capability` field that is not a string now fails
  closed as `malformed-payload` (exit 2). Before, it was passed to `enforcement.check()` and allowed
  under the permissive default. String input, a falsy field, and `--capability` behave as before.
  `test_cli_check_fails_closed_on_non_string_capability` covers the new path.

## Verification

Run in the worktree after rebasing onto `dev` at `d34850a`.

```
$ uv run ruff check src/ test/
All checks passed!

$ uv run mypy src/
Success: no issues found in 32 source files

$ uv run python -m src.governance
Governance OK: 35 systems, 327 documents, 30 memories, 293 backlog phases

$ uv run pytest
873 passed, 2 warnings
```
