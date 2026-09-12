---
id: mem-proc-hook-blocked-writes-hand-off-a-candidate
title: When a Hook Blocks the Write, Hand Off a Candidate and a Prompt — Never Route Around It
type: procedure
tags: [knowledge-base, agentic-systems, ai-tools]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-12
updated: 2026-09-12
confidence: high
related: [mem-proc-ask-through-the-tool, mem-proc-check-that-cannot-fail]
scope: project
---

## The situation

The owner approves a specific change to `AGENTS.md` or `CLAUDE.md`. You have the approval the
standing rule requires, you know exactly what the wording should be — and the write fails. A
pre-tool hook denies `Edit` on those paths, and `Bash` denies any command naming them. The approval
is real; the tool is still blocked.

The same shape appears for any path a hook protects. The block is not a judgement about this
change's merit. It is a guard that cannot read approvals, which is precisely what makes it a guard.

## Why the obvious responses are wrong

- **Retrying the same call.** A denial is a decision, not a transient failure.
- **Finding another tool that reaches the same path.** `Bash` with `cp`, `sed`, a heredoc, a Python
  one-liner — each is an attempt to defeat a control the owner installed deliberately. If one
  succeeded, the guard would be worthless, and you would have proven it so on a file that governs
  every future agent.
- **Reporting only the block and stopping.** The owner approved a change and receives nothing they
  can act on. The block is an obstacle to your write, not to the work.
- **Silently narrowing the change** to something the hook permits. That ships a different change
  than the one approved.

## What to do

1. **Say the write is blocked, in one sentence.** Name the tool and the path. Do not editorialise
   about the hook.
2. **Produce the complete candidate file, not a diff or a description.** Build it by writing the
   current file out verbatim and changing only what the approval covers, then diff the candidate
   against the real file and confirm the output contains *only* the approved changes. A candidate
   assembled from memory drifts in whitespace and wording nobody asked about, and the reviewer
   cannot tell those from the real edit.
3. **Write the executing agent a prompt that forbids authorship.** It performs a byte-for-byte copy
   and the verification. State plainly: do not rewrite, reformat, re-wrap or improve the candidate;
   if something in it looks wrong, stop and report rather than fix. Include the approval's scope and
   the reason a copy is being used instead of an edit.
4. **Give it the verification commands and their expected output** — the diff printing nothing,
   `git diff --stat` naming that file and no other, the governance run exiting 0 — and tell it to
   paste the real output.
5. **Tell it not to commit.** The change lands in the working tree for the owner. In a repository
   with several live worktrees, also tell it never to stash or revert working-tree changes it did
   not make.
6. **Verify the result yourself** before reporting success. Run the diff against your candidate. The
   executing agent reporting "done" is its claim; the diff exiting 0 is the evidence.

## Worked example (2026-09-12)

`AGENTS.md` carried two contradictions: a "claim a phase" paragraph still saying "ask the owner
before pushing" while citing the section commit `6374071` had corrected to the opposite, and a
hand-off step telling an agent to integrate onto `dev` whenever `dev` was clean, against the
standing rule that the merge is the owner's call. Both were stale halves of earlier corrections.

The owner approved the replacement wording. Every write path to the file was hooked. The session
produced two scratchpad files — the complete revised `AGENTS.md`, and a Codex prompt pinning the
change to a `cp` with four verification commands — and the owner ran it. The result came back
"Only AGENTS.md is modified. It remains unstaged and uncommitted", and `diff` against the candidate
exited 0, which is what made the report checkable rather than trusted.

The handoff cost one turn. Routing around the hook would have cost the guard.
