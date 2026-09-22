---
id: mem-proc-pipe-discards-the-exit-code
title: A Pipe Discards The Exit Code You Were Guarding On
type: procedure
tags: [agentic-systems, ai-tools, automation]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-22
updated: 2026-09-22
confidence: high
related: [mem-proc-check-that-cannot-fail, mem-proc-recompute-a-delegated-measurement]
scope: global
---

## The rule

A shell pipeline's exit status is its **last** command's. So the moment you pipe a command through
`tail`, `head`, `grep`, `sed` or anything else to trim its output, you have replaced that command's
exit code with the trimmer's — and the trimmer almost always succeeds.

**Never put a pipe on the left-hand side of `&&` when the right-hand side depends on the left
having succeeded.** The `&&` still runs, because it is reading the pipe's status, not the command's.
The guard is gone and nothing says so.

This matters most in exactly the place it is easiest to do: a chain that verifies, then acts.

```bash
# BROKEN — tail exits 0, so the destructive step runs even when the merge fails
git merge --ff-only agent/branch 2>&1 | tail -3 && git worktree remove ../wt

# BROKEN — the validator can print ERROR and exit 1; the commit lands anyway
uv run python -m src.governance 2>&1 | tail -5 && git commit -m "..."
```

Three ways out, in order of preference:

1. **Do not pipe the guard.** Run the command that must succeed on its own line, unpiped, and let
   its status stand. Trim the output of the things whose status you do not depend on.
2. **`set -e` at the top of the block**, so any failing command aborts it. Combine with keeping
   guards unpiped — `set -e` alone does not rescue a pipeline, because the pipeline genuinely
   succeeded.
3. **Check `${PIPESTATUS[0]}`** when you truly need both the trimmed output and the real status.
   Correct, but easy to forget and easy to misread; prefer 1.

When output volume is the reason you reached for the pipe, redirect instead of trimming: send it to
a file and read what you need afterwards. Volume is a display problem and status is a control-flow
problem, and solving the first must not silently solve away the second.

## The worked example

**2026-09-22, `phase-lrr-02`.** The hand-off ran:

```bash
git -C /code/d-system merge --ff-only agent/phase-lrr-02 2>&1|tail -3 \
  && git -C /code/d-system worktree remove /code/d-system-worktrees/phase-lrr-02 \
  && git -C /code/d-system branch -d agent/phase-lrr-02
```

A peer had moved the trunk between the rebase and the merge, so the merge failed with
`fatal: Not possible to fast-forward, aborting.` — and `tail` exited 0, so the chain continued.
`git worktree remove` then succeeded and destroyed the worktree along with its gitignored `.venv`,
which had to be rebuilt. The branch survived only by luck: `git branch -d` refuses a branch that is
not fully merged, and that refusal — not the intended guard — is what prevented the work being
deleted.

The same defect had already fired earlier the same day, and was missed:

```bash
uv run python -m src.governance 2>&1|tail -5 && git add ... && git commit ...
```

The validator printed `ERROR backlog:items.133: 'next_action' is a required property` and exited
non-zero. The commit landed anyway, carrying a backlog entry that failed validation. It was caught
only because the error text happened to be visible in the trimmed output and was read by a human
eye, not because any check stopped it.

Both instances share one shape: **the command whose failure mattered was the one that got piped**,
precisely because it was the noisy one.

## Why this is model-agnostic

Nothing here is about a particular model, harness, or tool. It is a property of POSIX shells: the
pipeline's status is the last stage's, and `&&` reads the pipeline. Any agent that composes shell
commands and trims output for readability will reach for the same construction and get the same
silent failure.

It generalises past the shell, too. The underlying error is letting a presentation concern — this
output is too long — quietly alter a control-flow decision. Whenever a step that formats, truncates
or summarises sits between a check and the action that check protects, ask what happened to the
signal. See [a check that cannot fail is not a check](a-check-that-cannot-fail-is-not-a-check.md):
a guard whose failure path has been routed around is the same defect wearing different clothes.
