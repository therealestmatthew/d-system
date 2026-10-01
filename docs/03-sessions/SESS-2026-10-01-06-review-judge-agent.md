---
schema_version: 1
id: doc-session-review-judge-agent
code: SESS-2026-10-01-06
title: The reviewer-judge agent type, in shadow
kind: session
status: active
owner: repository-owner
created: '2026-10-01'
updated: '2026-10-01'
systems: [sys-governance]
depends_on: [doc-reviewer-contract]
---

# The reviewer-judge agent type, in shadow

## Phase

`phase-asr-01` — The reviewer-judge agent type, in shadow, with a test that its tools stay
read-only.

## Verification

Checkpoint taken at the owner's wind-down, before any deliverable was written. The worktree's
preflight `uv run pytest` gave `1265 passed, 1 warning`.

`uv run pytest test/test_agent_tools.py`

```
ERROR: file or directory not found: test/test_agent_tools.py
```

`grep -n "session record" .claude/agents/review-judge.md`

```
ugrep: warning: .claude/agents/review-judge.md: No such file or directory
```

`uv run ruff check src/ test/`

```
All checks passed!
```

`uv run python -m src.governance --catalog`, `uv run python -m src.governance` and
`git diff --exit-code docs/08-governance/catalog.md` are run when this record is committed. The
pre-commit hook runs governance, and the catalog is regenerated in the same commit.

## Acceptance

- `test/test_agent_tools.py` passes on the agent file and fails on a fixture copy that adds Bash:
  **Not met**. Neither file exists yet.
- The agent's description says it runs in shadow and does not decide a merge: **Not met**. The
  agent file does not exist yet.
- `grep -n "session record"` on the agent file returns only the never-do line: **Not met**. The
  agent file does not exist yet.

## Backlog

`status: active`, `agent: agent-builder-a`. `next_action`: Checkpointed at the 2026-10-01
wind-down before any deliverable was written. Next, write `.claude/agents/review-judge.md` from
`partition-analyst.md` with tools exactly Read, Grep and Glob, then `test/test_agent_tools.py`
with its Bash-adding fixture. The owner ruled on 2026-10-01 that there is no `.codex` mirror for
now.

## Unresolved

None.
