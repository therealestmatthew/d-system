---
schema_version: 1
id: doc-session-session-start-step2-exceptions
code: SESS-2026-10-05-09
title: Name the two standing claim-approval exceptions in /session-start step 2
kind: session
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-governance, sys-backlog]
depends_on: []
---

# Name the two standing claim-approval exceptions in /session-start step 2

## Phase

Unclaimed: owner-directed work with no backlog phase. Idea `000591` (/session-start step 2 should
not stall on claim approval in a run the owner has pre-approved). Assigned by the Session Manager
as Session 1 - Builder A, following the plan at
`_working/session-manager/session-start-step2-plan.md`, option B.

## What changed

- `.claude/commands/session-start.md` step 2 names the two standing exceptions to the question
  before a claim: a batch run under `PROMPT-036`, and a run the owner has pre-approved under a
  Session Manager (`GOV-003`, 2026-10-05). The second applies only when the `ASSIGN` or the run's
  coordination contract names the owner's pre-approval.
- `GOV-003`'s 2026-10-05 entry gains one line saying the command now names this exception and the
  batch-run one.
- The plugin copies under `plugins/idea-realization/` are unchanged.

## Owner decisions

- Before the session (relayed by the Session Manager): option B; keep the pre-approval condition;
  this repository only; build it this run.
- In this session: approved the step 2 wording as proposed, and approved adding the `GOV-003` note.
- After review (relayed by the Session Manager, ruled in its session): remove the sentence
  "Record which exception you relied on in the session record."; keep the `max_active`/Conflicts
  sentence as is.

## Review

Coordinator-dispatched review of `6163861`. Unclaimed, so there are no verdict records; the Session
Manager keeps the raw replies under
`_working/session-manager/verdict-evidence/fix-session-start-step2/`.

- demo-adversary (gating): pass-with-findings. Shadow review-judge: pass-with-findings.
- Finding (minor, gating; shadow flagged the same): step 2's added sentence "Record which exception
  you relied on in the session record." was a standing rule found in none of the `000591` ruling,
  `GOV-003`, `GOV-017` or `PROMPT-036`/`PROMPT-037`. Fixed by removing it, per the owner's ruling.

## Verification

Run in `/code/d-system-worktrees/fix-session-start-step2` on `agent/fix-session-start-step2`,
branched from dev `a553a91`. On `6163861`:

`uv run python -m src.governance`

```
Governance OK: 45 systems, 451 documents, 37 memories, 347 backlog phases
```

`uv run ruff check src/ test/ tools/`: `All checks passed!` `uv run mypy src/`:
`Success: no issues found in 49 source files`.

`uv run pytest`

```
1638 passed, 1 warning in 193.21s (0:03:13)
```

Private-content check: the worktree run reports 0 identifiers checked, because `_private/portfolio/`
is absent there. Matching the changed files against the primary checkout's identifiers found 0
matches against 31 identifiers.

## Unresolved

None.
