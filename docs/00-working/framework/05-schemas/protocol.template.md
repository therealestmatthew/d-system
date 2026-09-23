---
code: GOV-NNN
title: "Short name of the procedure"
kind: protocol
status: draft
created: YYYY-MM-DD
---

# [Procedure Name]

<!--
A protocol document states what to do, in order, when a named situation arises. It does not
argue for a rule — that is a governance document (governance.template.md). If a step needs a
justification longer than a sentence, put the justification in a governance document and cite it.

Checked by protocol.schema.json via check_schemas.py: the front matter above and the four
level-2 headings below are required, spelled exactly as written. The schema checks that the
headings exist; it does not check that the Steps section is a numbered list, so write it as one.
-->

## Trigger

<!-- The condition that starts this procedure. Someone reading it must be able to tell whether
they are in that situation right now. -->

Example: An agent has been assigned a backlog phase and has not yet written any file for it.

## Steps

<!-- A numbered list, in the order performed. One action per step. Say where each step happens
when more than one location is involved. -->

1. Run the repository checks on the integration branch and stop if either fails.
2. Ask the owner to approve the claim.
3. Commit the claim on the integration branch, with nothing else in the commit.
4. Create the branch and its worktree, and do all further work there.

## Exit criteria

<!-- How someone confirms the procedure finished correctly. Each criterion should be checkable
by a command or by reading a named file. -->

Example: The phase shows `status: active` with your agent id on the integration branch, and
`git worktree list` shows the new worktree on its own branch.

## Failure handling

<!-- What to do when a step fails: which failures stop the procedure, which are retried, and
what state to leave behind. -->

Example: If the claim is rejected for overlapping a peer's paths, do not retry it; choose a
different phase. If the push is rejected as non-fast-forward, pull with rebase, re-run the
checks, and confirm the claim is still safe before pushing again.
