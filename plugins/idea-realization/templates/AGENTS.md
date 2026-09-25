# AGENTS.md

The working agreement for every agent in this repository, human-directed or autonomous.
Framework-specific orientation files, such as `CLAUDE.md`, say what the project is and where things
live; this file governs how you work. Where the two disagree, this file wins.

<!-- Rendered from the idea-realization plugin's template. It carries only rules that hold in any
repository. Add this repository's own sections by hand below the last one: its stack, how to run
its tests and checks, its conventions, and anything it adds to these rules. -->

## Never edit this file or CLAUDE.md without explicit approval

**No agent modifies `AGENTS.md` or `CLAUDE.md` for any reason without the owner's explicit approval
for that specific change.** There is no exception: not to fix something you are certain is wrong,
not to record something you learned this session, not because a phase's scope appears to cover it,
and not as tidy-up alongside a change you were asked to make.

These two files are the instructions every agent reads before doing anything. An agent that edits
them rewrites its own governing rules and every later agent's, and the edit outlives the session
that made it, usually unreviewed because it arrives inside a diff about something else.

**If you believe either file is wrong, out of date or missing something: say so and stop.** Quote
the passage, propose exact replacement wording, and let the owner decide.

## Do not assume, and do not invent rules

- When something is unclear, unstated or open to more than one reading, ask. Ask at the point the
  work reaches the uncertainty, not at the end. A question that can wait is stated as an
  assumption, and the work continues; an assumption that changes what gets built is a question.
- Do not turn a one-time instruction into a standing rule. If a pattern seems worth making
  permanent, propose it and let the owner decide.
- If a tool can settle a fact, use it before saying you do not know.
- When the owner corrects you and is right, say so in one sentence and move on.

## Plan before implementing

For any non-trivial change, write a requirement document (observable statements with verification
methods) and a plan document before writing implementation code. Approval of one plan is not
permission to skip the documents for the next piece of work.

## Confidentiality and publishing

- `{{confidential_dir}}` holds confidential material and is never tracked. Never read or write
  there unless the owner directs you to.
- **Never write a confidential identifier into a tracked file**: not in code, a document, a commit
  message, or a session record describing the identifiers.
- **Pushing your own branch needs no approval.** Backing up your own work is not publishing.
- **Ask before integrating a branch into `{{integration_branch}}`.** The merge that lands work on
  the trunk is the owner's call; a green branch is ready to integrate, not cleared to.

## Generated files

`{{data_root}}` holds this repository's data. A file generated from it, or from any other source,
is never edited by hand: change the source and regenerate. A generated file is committed only when
a check regenerates it and fails on any difference.

## Work in a worktree

**Every session works in its own worktree, and the primary checkout's branch is never switched.**
Each session's worktree lives under `{{worktree_dir}}`, outside the repository, on its own branch.

## Working rules

- Prefer narrow diffs: one concern per commit.
- Report outcomes honestly. A failing check is a result to record, not a step to retry until
  quiet.
