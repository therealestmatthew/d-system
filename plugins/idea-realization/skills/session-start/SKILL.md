---
name: session-start
description: Open a working session on one backlog phase — orient, ask before claiming, claim it on the integration branch, cut its branch and worktree, and isolate the environment. Use before writing any code or document for a phase, or when someone asks to start, pick up or claim a phase.
---

# Start a session

Run this before writing any code or creating any document. It leaves the session in the state the
concurrency rules assume: one phase claimed on the integration branch, a branch and a worktree of
its own, and a known route back when the work is done.

## The values this procedure uses

Every command below runs from the repository's primary checkout root unless it says otherwise, and
every backlog command carries the same option assignments, so the person's saved plugin options
reach the scripts. An option never saved appears as its `${user_config.…}` text; the scripts treat
that as unset and use the documented default.

Read the resolved values once, at the start:

```bash
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
CLAUDE_PLUGIN_OPTION_WORKTREE_DIR='${user_config.worktree_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/paths.py"
```

From its output, use `backlog_path` as **the backlog**, `integration_branch` as **the integration
branch**, and `worktree_dir` as **the worktree directory**. Use those exact values everywhere below;
never substitute a branch or directory name from memory or from another repository.

The check and the queue, used in several steps:

```bash
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/check.py"

CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" ready
```

## Where each step happens

| Step | Where | Why there |
|---|---|---|
| Orientation | primary checkout, on the integration branch | Reads only |
| The claim commit and the catalog regeneration it forces | primary checkout, on the integration branch | The backlog on the integration branch is the lock table every peer reads; a claim held anywhere else is invisible and is therefore not a lock |
| Everything else — the work, verification, checkpoints, the session record | the worktree | Tests, rebuilds and servers must not touch a peer's run |

**The primary checkout's branch is never switched.** Make the claim there, then move to the
worktree and stay there.

## 1. Orient — run the `backlog` skill

Run the `backlog` skill, naming the phase if one was given. It runs the check and the repository's
own tests, shows the queue, reads the phase and its plan, and asks what needs deciding. It never
claims.

**If the check or the tests fail, stop.** Create no branch, no worktree, and claim nothing. Report
the failure and nothing else.

## 2. Ask before the claim commit

The claim is a change peers read as a lock. Ask with the AskUserQuestion tool whether to claim the
phase, recommendation first, and report alongside the question:

- the phase id and its title, and its plan by title;
- its Conflicts column from the queue; if it is not `—`, say so and recommend a different phase,
  because a peer already holds one of its systems or paths;
- anything that looked wrong during orientation: an acceptance condition nothing can verify, a
  missing deliverable, an undeclared dependency.

Stop until the answer comes back. An unanswered question is not a yes.

**Work with no backlog phase** — a one-off document, a fix asked for directly — has nothing to
claim. Skip steps 2 and 3, name the branch and worktree after the work (`agent/<slug>`), and say
plainly in the first report that the session is unclaimed and peers hold no lock against it. Never
invent a phase to have something to claim.

## 3. The claim commit — primary checkout, integration branch

Only once the answer is yes. Confirm the primary checkout is on the integration branch
(`git branch --show-current`) — if it is not, stop and report it rather than switching — then
bring it up to date:

```bash
git pull --ff-only
```

In the backlog, edit **only this phase's lines**: `status: active` and `agent: agent-<name>`, and
set the catalog's `updated` to today. Choose the agent id once, lowercase `agent-<name>`, and reuse
it; one agent holds at most one active phase.

Then regenerate the document catalog, which lists the phases, and run the check:

```bash
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" catalog
```

and the check command above. The check rejects the claim if it overlaps an active peer's systems,
deliverable paths or dependency chain, or if `max_active` is reached. **That rejection is the
answer, not an obstacle**: choose a different phase.

Commit the claim and the regenerated catalog together, in one commit that changes nothing else,
and push it. If the push is rejected as non-fast-forward, `git pull --rebase`, re-run the check,
and confirm the claim is still safe: a peer claimed in between, and its systems may now collide.

## 4. Cut the branch and the worktree

Still in the primary checkout, on the up-to-date integration branch:

```bash
git worktree add -b agent/<phase-id> <worktree directory>/<phase-id> <integration branch>
```

- The branch is always `agent/<phase-id>`, and the worktree is always
  `<worktree directory>/<phase-id>`. The worktree directory sits beside the repository, never
  inside it, so no test or scanner walks a second copy of the tree.
- Confirm with `git worktree list` and report the path. Every later step happens there.

## 5. Isolate the environment

Ignored directories — virtual environments, databases, `node_modules` — do not travel between
worktrees. Create the worktree's own; never link a peer's. If the work runs a server, choose a free
port explicitly rather than assuming the default one is free.

Ignored content also never travels through a merge. Anything written to an ignored path in the
worktree must be copied out by hand before the worktree is removed.

## 6. While the session runs

- Stay inside the phase's declared `systems` and `deliverables`. If the work genuinely needs a
  file outside them, stop: narrow the change, or widen the phase's declarations on the integration
  branch and re-run the check so peers see the wider lock before continuing.
- In the backlog, touch only this phase's lines and the catalog's `updated`.
- Commit narrow diffs, one concern per commit, on this branch only.
- **Rebase onto the integration branch, never merge it in**, whenever a peer integrates, not only
  at the end.
- Pushing `agent/<phase-id>` needs no approval; backing up your own work is not publishing.
- Record progress with the `checkpoint` skill as often as useful. It never marks a phase complete.

## 7. Hand off — finish, then ask before integrating

In the worktree, in this order:

1. Run every command in the phase's `verification` list and keep the real output. A failing check
   is a result to record, not a step to retry until quiet.
2. Write the session record with the `checkpoint` skill.
3. `git rebase <integration branch>`, then re-run the check and the repository's tests. **This run,
   after the rebase and against peers' merged work, decides whether the branch may integrate.** If
   it fails, fix it on the branch.
4. Confirm the primary checkout is clean: `git -C <primary checkout> status --short` shows nothing.
   Never stash a peer's uncommitted work and never force an integration around it; uncommitted
   changes there are someone's work in progress, to be reported and waited on.
5. **Ask the owner before merging into the integration branch.** A green branch on a clean
   integration branch is ready to integrate, not cleared to. Without a yes, leave the branch
   unmerged and report that it is ready for review with `git diff <integration branch>..agent/<phase-id>`.

Marking the phase complete is not part of this procedure. The `session-close` skill does that, and
only under its three conditions.

## 8. Integrate and clean up — only on the owner's yes

From the primary checkout:

```bash
git merge --ff-only agent/<phase-id>
git worktree remove <worktree directory>/<phase-id>
git branch -d agent/<phase-id>
```

Copy any ignored content out of the worktree before removing it. If the merge is not a
fast-forward, the integration branch moved since the rebase: rebase again and re-run the check;
never resolve it with a merge commit that skips the green run.

### If the rebase conflicts

- **A backlog conflict is normal** — two agents edited different phases in one file. Keep both
  sides: the peer's phases verbatim, your own phase's edits, `updated` set to today. Never resolve
  this file wholesale with `--ours` or `--theirs`; either silently deletes a peer's work.
- **A generated file conflicts** — the catalog: regenerate it rather than merging it by hand.
- **A duplicate document code** means a peer took the same number. Whoever integrates second
  allocates again, renames the file and updates every reference.
- **A conflict in source code means the declared systems or deliverables were wrong.** Stop, do not
  force it, and report it; the phases' declarations need fixing before either completes.
- When resolving a collision needs an actual choice, record the decision and its reason in the
  decisions document the backlog's `decision_record` names, in the same change.

## What this skill never does

- It never marks a phase complete.
- It never merges into the integration branch without the owner saying so in this session.
- It never switches the primary checkout away from the integration branch.
