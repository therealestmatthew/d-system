---
schema_version: 1
id: doc-session-r02-r04-open-and-tmpagent-cleanup
code: SESS-2026-09-22-13
title: Recording REQ-017 R02 and R04 as open, and removing the stale v1 P10 coordinator
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-governance]
depends_on: [doc-autonomous-agent-operations, doc-autonomous-agent-operations-requirements, doc-broker-first-autonomous-operations]
---

# Recording REQ-017 R02 and R04 as open, and removing the stale v1 P10 coordinator

## Phase

Unclaimed: owner-directed work with no backlog phase, relayed by the Session Manager on 2026-09-22.
Peers held no lock against it. Branch `agent/fix-000326-and-tmpagent`, worktree
`../d-system-worktrees/fix-000326-and-tmpagent`.

## What changed

1. **000326** (PLAN-032's coverage table still maps R02 and R04 to `phase-auto-02`). `ADR-022`
   records both as open because the broker ships permissive-default and the capability taxonomy
   is deferred. `PLAN-032`'s requirement coverage table now marks R02 and R04 open with a
   citation to `ADR-022`, and its opening sentence no longer claims every row maps to a phase.
   `REQ-017`'s qualification paragraph under "What each requirement is not" now states that the
   permissive shape was chosen, so R02 and R04 are open. The requirement rows themselves are
   unchanged. Both documents' `updated` dates are bumped. The catalog regenerated with no change.
2. **`_tmpagent/p10-track-coordinator.md` removed.** The Session Manager asked for a `released`
   line. `_tmpagent/AGENTS.md` defines `released` as the close of a claim, addressed by
   `(file, kind, ref)`, and this file was never claimed. Its last event was `activated` on
   2026-09-14, and `p10-track-coordinator-v2.md` superseded it 21 minutes later. The owner chose the
   contract's own route when asked: the file is deleted and a `removed` line carries the reason
   "stale activation released on the owner's instruction, 2026-09-22". Two tracked files still
   name it in plain text as history: the v2 file's opening line and
   `SESS-2026-09-14-12`. Neither is a link.

## Verification

Run in the worktree after rebasing onto `dev` at `271d614`.

```
$ uv run python -m src.governance
Governance OK: 35 systems, 326 documents, 30 memories, 293 backlog phases

$ uv run pytest
871 passed, 1 skipped, 2 warnings

$ uv run python tools/check_no_private_content.py   (staged)
check_no_private_content: OK
```

## Unresolved

- `PLAN-032` decision 1 still describes the broker's two possible shapes as a choice yet to be made.
  It is not wrong, since it describes the choice `phase-auto-01` faced, and this session left it alone
  to keep the change to what 000326 asked for.
