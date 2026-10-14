# CLAUDE.md

Orientation for Claude Code in this repository: what the project is and where things live.

<!-- Rendered from the idea-realization plugin's template. Replace the Project section with this
repository's own purpose and layout, and keep this file to pointers, instructions an agent needs
before anything else, and the few facts worth duplicating. -->

## Read AGENTS.md first

**[AGENTS.md](AGENTS.md) is the working agreement and governs everything you do here.** This file is
orientation only; where the two ever disagree, AGENTS.md wins.

## Never edit this file or AGENTS.md without explicit approval

**Do not modify `CLAUDE.md` or `AGENTS.md` for any reason without the owner's explicit approval for
that specific change.** If you believe either is wrong, quote the passage, propose the
replacement, and stop.

## Facts worth knowing before the first command

- Work lands on `{{integration_branch}}`, and only with the owner's approval of each merge.
- Every session works in its own worktree under `{{worktree_dir}}`; the primary checkout's branch is
  never switched.
- `{{confidential_dir}}` is confidential and untracked; nothing from it is ever written into a
  tracked file.
- `{{data_root}}` holds this repository's data; anything generated from it is regenerated, never
  edited.

## Ask, do not assume

Use the AskUserQuestion tool for anything unclear, at the point the work reaches it. Do not turn a
one-time instruction into a standing rule. When a tool can settle a fact, use it before saying you
cannot know it.

## Project

<!-- What this repository is, and a table of its directories and what each holds. The plugin's
repository-layout reference describes the directories its features create. -->
