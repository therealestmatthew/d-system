---
schema_version: 1
id: doc-session-green-dev-ci-before-grants
code: SESS-2026-09-24-03
title: Green dev CI before each primary-checkout grant
kind: session
status: active
owner: repository-owner
created: '2026-09-24'
updated: '2026-09-25'
systems: [sys-governance, sys-gov-docs]
depends_on: [doc-deterministic-guards]
---

# Green dev CI before each primary-checkout grant

## Phase

`phase-grd-02` — Green dev CI before each primary-checkout grant.

## Verification

Run in the worktree `../d-system-worktrees/phase-grd-02` on `agent/phase-grd-02`.

```text
$ uv run pytest test/test_check_dev_ci.py
27 passed, 1 warning
```

```text
$ uv run python tools/check_dev_ci.py
green: CI succeeded for 2dd56d4: https://github.com/therealestmatthew/d-system/actions/runs/35986703694
exit 0
```

The live run against `dev`'s head (the grd-02 claim commit). Exit 1 against the real `gh`, on a
commit from the six-day red period (review finding 8):

```text
$ uv run python tools/check_dev_ci.py --commit 024443c
red: CI failure for 024443c: https://github.com/therealestmatthew/d-system/actions/runs/35876027675
exit 1
```

```text
$ uv run python -m src.governance --catalog
347 documents — adr: 19, architecture: 11, governance: 16, operation: 22, plan: 61, prompt: 38, requirement: 30, session: 150.
$ uv run python -m src.governance
Governance OK: 35 systems, 347 documents, 32 memories, 304 backlog phases
$ git diff --exit-code docs/08-governance/catalog.md
exit 0
$ uv run ruff check src/ test/ tools/check_dev_ci.py
All checks passed!
$ uv run mypy src/ tools/check_dev_ci.py
Success: no issues found in 47 source files
```

Full suite, not in the verification list but run for the merge gate:

```text
$ uv run pytest
1096 passed, 1 skipped, 1 warning
```

The counts above were taken before this record existed; adding it changes the document count by
one.

## Acceptance

- Unit tests over recorded `gh run list` JSON for the five cases — **Met.** `test_success_at_head_exits_0`,
  `test_failure_at_head_exits_1_naming_the_run`, `test_in_progress_exits_2`,
  `test_run_only_for_an_older_commit_exits_2` and `test_gh_error_exits_2` pass; every payload was
  recorded live on 2026-09-24 (the test module's docstring names the command).
- Run against the live repository, the tool's output is recorded in the session record — **Met.**
  `## Verification` above: exit 0 at `dev`'s head, and exit 1 with the run URL for `024443c`.
- The `GOV-017` and `PROMPT-037` diffs show the grant rule and the meaning of exit 2 — **Met.**
  `GOV-017`'s lock section gains the push-before-`TURN DONE` rule and the green-CI grant rule with
  exits 0, 1 and 2; `PROMPT-037` contract item 1 gains the push step and the same rule in short
  form. `REQ-028` R06 is amended to the rulings.

## Backlog

`status: active`. `next_action`: all acceptance met in the worktree; the independent `/session-close`
review was launched and had not returned at the 2026-09-25 reset; re-run it, fix or accept its
findings, then send READY and wait for the owner's merge approval. `session`, `completion_evidence`
and `result` are recorded as interim evidence.

## Unresolved

- Sessions already running hold the old `PROMPT-037` item 1 text. Whether the Session Manager
  re-sends the amended item or uses it only after a `/clear` is its operating choice (review, out of
  scope).
- The independent review launched on 2026-09-24 did not return before the reset. It must be re-run.
