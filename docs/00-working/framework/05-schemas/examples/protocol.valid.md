---
code: GOV-002
title: "Claiming a backlog phase"
kind: protocol
status: active
created: 2026-09-12
---

# Claiming a backlog phase

## Trigger

An agent has been assigned a backlog phase and has not yet written any file for it.

## Steps

1. On an up-to-date integration branch, run the governance check and the test suite. Stop if
   either fails.
2. Ask the owner to approve the claim.
3. Set the phase's status to active and record your agent id, regenerate the catalog, and run the
   governance check again.
4. Commit those changes alone on the integration branch and push.
5. Create `agent/<phase-id>` and its worktree, and do all further work there.

## Exit criteria

The phase shows `status: active` with your agent id on the integration branch, the governance
check exits 0, and `git worktree list` shows the new worktree on `agent/<phase-id>`.

## Failure handling

If the governance check rejects the claim for overlapping a peer's systems or paths, do not retry;
choose a different phase. If the push is rejected as non-fast-forward, pull with rebase, re-run the
check, and confirm the claim is still safe before pushing again.
