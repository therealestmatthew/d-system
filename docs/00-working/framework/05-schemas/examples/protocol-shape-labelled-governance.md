---
code: GOV-002
title: "Removing a finished worktree"
kind: governance
status: active
created: 2026-09-12
---

# Removing a finished worktree

## Trigger

A phase's branch has been merged into the integration branch, and the owner has approved removing
its worktree.

## Steps

1. Copy any untracked or ignored files the work produced out of the worktree; a merge never
   carries them.
2. From the primary checkout, confirm the merge: `git branch --merged dev` lists the branch.
3. Run `git worktree remove <path>` from the primary checkout with the worktree's absolute path,
   never from inside the worktree.
4. Delete the branch with `git branch -d agent/<phase-id>`.

## Exit criteria

`git worktree list` no longer shows the path, and `git branch --list agent/<phase-id>` prints
nothing.

## Failure handling

If `git worktree remove` refuses because the worktree has uncommitted changes, stop and report them
to the owner; do not pass `--force`. If `git branch -d` refuses because the branch is not merged,
the merge did not happen: leave the branch in place and report it.
