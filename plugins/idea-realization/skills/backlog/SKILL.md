---
name: backlog
description: Check the repository, show the top of the phase queue with readiness and conflicts, and orient on one phase without claiming it. Use when asked what to work on next, to show the backlog or the ready queue, or before starting a session.
---

# Backlog

Checks the repository, shows the top of the queue, and orients on one phase. **It never claims.**
Setting `status: active` or an `agent` on any phase is forbidden in this skill; claiming belongs to
the `session-start` skill, after the owner answers.

It runs one script, `cli.py ready`, after the check. Every command carries the person's saved
options; an option never saved appears as its `${user_config.…}` text and the scripts use the
documented default. Run from the repository root.

## 1. Check — stop if the repository is not green

```bash
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/check.py"
```

Then the repository's own test command, if it has one. Report the real output. **If either fails,
stop**: report the failure and nothing else. Do not orient and do not offer to continue past it. A
failure found before any edit is a fix; the same failure found three edits in is tangled with
yours.

## 2. Show the top of the queue

```bash
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" ready
```

Add `--all` for every phase with its details. The report lists `next_up` first, then priority and
id, with each phase's state, prerequisites and the active phases it would collide with, and a
stale-claim signal beside each active claim.

Present the **top five ready phases** in queue order, one row each: the phase's **title** first with
its id as the handle, its priority and whether it is in `next_up`, its plan by title, and its
`next_action` verbatim. Fewer than five? Show what there is and say how many.

**Recommend the first**, and say in a sentence why it is first: its `next_up` position, its
priority, or that everything ahead is blocked. If it looks wrong against what the owner said they
want, say so; the queue records earlier intent.

**If nothing is ready**, everything is blocked, complete or deferred: report which, naming the
blockers, and say that the backlog needs re-prioritising. Do not invent a prioritisation process
and do not un-defer phases to manufacture work.

## 3. Orient on the chosen phase

If a phase was named, use it; the owner has already decided. Read, in order:

1. the phase in the backlog — scope, acceptance, verification, deliverables, `depends_on`;
2. the plan its `plan` field names;
3. the repository's working agreement, if it has one;
4. only when they bear on this phase: its `sources` that the plan does not restate, the systems
   registry entries it changes, and any governed document it amends.

Do not read session records to orient; their carried-forward content belongs in phases.

## 4. Summarise

- **What the phase wants**, in your own words;
- **the first concrete action**, from `next_action`;
- **what done means** — each acceptance condition and how it will actually be checked;
- **anything that looks wrong**: an acceptance condition no verification can observe, a
  deliverable the scope needs but the list lacks, an undeclared dependency. Say it now.

## 5. Ask, in batches

Every question goes through the AskUserQuestion tool, never prose: up to four per batch, one batch
at a time, recommendation first and marked `(Recommended)`. Ask now, before work starts. Do not ask
what the phase, the plan or the working agreement already answers, and do not pad a batch.

## 6. Stop

Ask whether to start the phase, and stop there. To start it, the owner runs the `session-start`
skill, which asks again before its claim commit. This skill changes no file.
