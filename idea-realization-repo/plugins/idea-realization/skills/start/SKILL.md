---
name: start
description: Begin a working session by choosing a mode — Planning, Implementing or Validating — then load that mode's guide and name the first command to run. Use at the start of every session, when the session banner says to run /start, or when someone asks what to do first or which mode to work in.
---

# Start: pick a mode

The entry point for every session. It shows the resolved configuration, reminds the person to
bring the integration branch up to date, asks which mode they are working in, loads that mode's
guide and names the first command. **It changes no file, claims nothing and runs no git command
that changes a branch.** Claiming belongs to the `session-start` skill.

Run from the control repository's root. Every command carries the person's saved options; an
option never saved appears as its `${user_config.…}` text and the script uses the documented
default.

## 1. Show the configuration

```bash
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
CLAUDE_PLUGIN_OPTION_PRODUCT_ROOT='${user_config.product_root}' \
CLAUDE_PLUGIN_OPTION_HANDLE='${user_config.handle}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/session_banner.py"
```

Report the lines as printed. A line that reads `(unavailable: …)` is a setup gap, not a reason to
stop: name it in one sentence (an unresolved handle means the person's git email is not in the
`owners` map of `<docs_root>/systems.yaml`; a missing `project.yaml` means the shared project
configuration was never scaffolded) and continue.

## 2. Remind: pull the integration branch first

State this to the person before the menu, in these words or close to them:

> Before any work, update the integration branch in the **primary checkout** of the control
> repository (the first entry of `git worktree list`), and in the product checkout if this
> repository drives one: `git pull --rebase origin <integration branch>` (the branch the banner
> printed). `--rebase` keeps an unpushed bookkeeping commit on top instead of merging.
> Push right after any claim or other bookkeeping commit.

Do not run the pull yourself. It can merge into a checkout someone else's session is using; the
person runs it, or asks you to. You may show where the primary checkout stands, which changes
nothing:

```bash
git -C "$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -n 1)" status --short --branch
```

## 3. Ask the mode

Use the AskUserQuestion tool, never prose: one question, "Which mode is this session in?", with
three options. Put no content in the option previews; the descriptions below are the whole text.

- **Planning** — from captured ideas to approved plans, registered phases and validated, assigned
  batches.
- **Implementing** — claim one phase, build it in the product worktree, verify it and merge it.
- **Validating** — review a plan, a peer's ready branch, infrastructure or spend; reviewers change
  nothing.

If the person already named the mode when invoking this skill, skip the question.

## 4. Load the mode's guide

Each mode has one guide under `<docs_root>/guides/` (`docs/guides/` by default), named by the
mode, whatever its document code:

| Mode | Guide file | Front-matter `id` |
|---|---|---|
| Planning | `<docs_root>/guides/*-planning-mode.md` | `doc-planning-mode` |
| Implementing | `<docs_root>/guides/*-implementing-mode.md` | `doc-implementing-mode` |
| Validating | `<docs_root>/guides/*-validating-mode.md` | `doc-validating-mode` |

Find the file with the Glob tool and read it in full. If no file matches, say so in one sentence
and continue with step 5 from the defaults below; if more than one matches, list them and ask which
to use. Do not summarise the whole guide back to the person: tell them what the mode ends with, as
the guide states it, and move on.

## 5. Name the first command

Name the first command the guide gives for the mode, exactly as the guide writes it. Where the
guide is missing or names none, use these:

| Mode | First command | Then |
|---|---|---|
| Planning | `/idea-realization:idea` to record each new idea as given | `/idea-realization:idea-triage`, then `/idea-realization:partition-ideas` |
| Implementing | `/idea-realization:backlog` to check the repository and see the ready queue | `/idea-realization:session-start` on the phase the person chooses |
| Validating | `/idea-realization:backlog` to see the active phases | follow the validating guide's procedure for the chosen review; a review of a peer's branch is advice and never replaces the gating review, which belongs to the session that holds the phase |

Say the command, say in one sentence what it does, and ask whether to run it now. Stop there.
