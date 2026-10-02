---
schema_version: 1
id: doc-session-review-judge-agent-build
code: SESS-2026-10-02-01
title: The reviewer-judge agent type, in shadow — build
kind: session
status: active
owner: repository-owner
created: '2026-10-02'
updated: '2026-10-02'
systems: [sys-governance]
depends_on: [doc-reviewer-contract]
---

# The reviewer-judge agent type, in shadow — build

## Phase

`phase-asr-01` — The reviewer-judge agent type, in shadow, with a test that its tools stay
read-only. Continues `SESS-2026-10-01-06`, which checkpointed the phase before any deliverable was
written.

## Verification

`uv run pytest test/test_agent_tools.py`

```
5 passed, 1 warning
```

`grep -n "session record" .claude/agents/review-judge.md`

```
69:- Never read the builder's session record or report, or anything else the builder wrote about
```

`uv run ruff check src/ test/`

```
All checks passed!
```

`uv run python -m src.governance --catalog`, `uv run python -m src.governance` and
`git diff --exit-code docs/08-governance/catalog.md` run when this record is committed: the catalog
is regenerated in the same commit and the pre-commit hook runs governance.

The full suite in the worktree, after the rebase onto `dev` at `440190c`, gave
`1296 passed, 1 warning`. `uv run mypy src/` gave `Success: no issues found in 47 source files`.

## Acceptance

- `uv run pytest test/test_agent_tools.py` passes on the agent file, and the same assertion fails on
  a fixture copy that adds Bash: **Met**. 5 passed: the real file, fixture copies adding `Bash`,
  `Edit` and `Write`, and a copy with no `tools` field.
- The agent's description says it runs in shadow and does not decide a merge: **Met**. The
  description reads "Runs in shadow until the owner promotes it in GOV-003; its verdict is recorded
  and does not decide a merge."
- `grep -n "session record"` on the agent file returns only the never-do line: **Met**. One match,
  line 69, the first never-do.

## Backlog

`status: active`, `agent: agent-builder-a`. `next_action`: Both deliverables written and verified
(SESS-2026-10-02-01, branch agent/phase-asr-01); awaiting the independent review, then READY to the
Session Manager. The owner ruled on 2026-10-01 that there is no .codex mirror for now. New agent
types appear in running sessions after a delay; check review-judge is listed before its first
dispatch.

## Unresolved

None.
