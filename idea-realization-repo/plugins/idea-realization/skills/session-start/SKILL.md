---
name: session-start
description: Open a working session on one backlog phase — orient, ask before claiming, claim it in the control repository, cut its branch and worktree in the product repository and a paired one in the control repository, and isolate the environment. Use before writing any code or document for a phase, or when someone asks to start, pick up or claim a phase.
---

# Start a session

Run this before writing any code or creating any document. It leaves the session in the state the
concurrency rules assume: one phase claimed on the control repository's integration branch, a
branch and a worktree of its own in the product repository where the code is written, a paired
branch and worktree in the control repository for the session's records, and a known route back
when the work is done.

**Two repositories.** This repository is the **control repository**: ideas, plans, the backlog,
session and review records, agents and rules. The code is built in the **product repository** that
`.idea-realization/product.yaml` names. Start Claude Code in the control repository; the product
worktree is added to the session in step 4. `docs/two-repositories.md` explains the split. A
repository with no `product.yaml` works on one repository: skip every product step below.

## The values this procedure uses

Every command below runs from the control repository's primary checkout root unless it says
otherwise, and every command carries the same option assignments, so the person's saved plugin
options reach the scripts. An option never saved appears as its `${user_config.…}` text; the
scripts treat that as unset and use the documented default.

Read the resolved values once, at the start:

```bash
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
CLAUDE_PLUGIN_OPTION_WORKTREE_DIR='${user_config.worktree_dir}' \
CLAUDE_PLUGIN_OPTION_PRODUCT_ROOT='${user_config.product_root}' \
CLAUDE_PLUGIN_OPTION_PRODUCT_WORKTREE_DIR='${user_config.product_worktree_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/paths.py"

CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/identity.py"

CLAUDE_PLUGIN_OPTION_PRODUCT_ROOT='${user_config.product_root}' \
CLAUDE_PLUGIN_OPTION_PRODUCT_WORKTREE_DIR='${user_config.product_worktree_dir}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/product.py" verify
```

From the first output use `backlog_path` as **the backlog**, `integration_branch` as **the control
integration branch** and `worktree_dir` as **the control worktree directory**. From `identity.py`
use the printed handle as **your handle**. From `product.py verify` use `root` as **the product
checkout**, `integration_branch` as **the product integration branch** and `worktree_dir` as **the
product worktree directory**. Use those exact values everywhere below; never substitute a branch or
directory name from memory or from another repository.

**If `identity.py` or `product.py verify` fails, stop** and report its message. A missing handle
means your git email is not listed under your key in `systems.yaml` `owners`; a refused product
checkout means `product_root` names the wrong repository. Neither is worked around.

The check and the queue, used in several steps:

```bash
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH='${user_config.integration_branch}' \
CLAUDE_PLUGIN_OPTION_PRODUCT_ROOT='${user_config.product_root}' \
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
| Orientation | control primary checkout, on its integration branch | Reads only |
| The claim commit and the catalog regeneration it forces | control primary checkout, on its integration branch | The backlog on the control integration branch is the lock table every developer reads; a claim held anywhere else is invisible and is therefore not a lock |
| The code, its tests, the verification commands | the product worktree | The product repository is where the code lives; tests must not touch a peer's run |
| The session record, checkpoints, review records | the control worktree | Records are reviewed and merged with the phase, never written straight onto the integration branch |

**Neither primary checkout's branch is ever switched.** Make the claim in the control primary
checkout, then move to the worktrees and stay there.

## 1. Orient — run the `backlog` skill

Run the `backlog` skill, naming the phase if one was given. It runs the check, shows the queue,
reads the phase and its plan, and asks what needs deciding. It never claims.

**If the check fails, stop.** Create no branch, no worktree, and claim nothing. Report the failure
and nothing else. The product repository's own tests run in step 5, in the new product worktree,
never in a primary checkout. If they fail there, hand the phase back as an interrupted phase:
return it to queued with an exact `next_action` and remove both worktrees.

## 2. Ask before the claim commit

The claim is a change other developers read as a lock. Ask with the AskUserQuestion tool whether to
claim the phase, recommendation first, and report alongside the question:

- the phase id and its title, and its plan by title;
- its Conflicts column from the queue; if it is not `—`, say so and recommend a different phase,
  because a peer already holds one of its systems or paths;
- whether its deliverables sit inside your own workstream (`workstreams.py show`); a deliverable
  inside another developer's workstream needs that developer's approval recorded on the phase
  (`cross_workstream`) before the check accepts the claim;
- anything that looked wrong during orientation: an acceptance condition nothing can verify, a
  missing deliverable, an undeclared dependency.

Stop until the answer comes back. An unanswered question is not a yes.

**Work with no backlog phase** — a one-off document, a fix asked for directly — has nothing to
claim. Skip steps 2 and 3, name the branches and worktrees after the work (`agent/<slug>`), and say
plainly in the first report that the session is unclaimed and peers hold no lock against it. Never
invent a phase to have something to claim.

## 3. The claim commit — control primary checkout, control integration branch

Only once the answer is yes. Confirm the control primary checkout is on its integration branch
(`git branch --show-current`) — if it is not, stop and report it rather than switching — then
bring it up to date:

```bash
git pull --ff-only
```

In the backlog, edit **only this phase's lines**: `status: active` and
`agent: <your handle>/agent-<name>`, and set the catalog's `updated` to today. Choose the agent name
once, lowercase, and reuse it; one agent holds at most one active phase.

Then regenerate the document catalog, which lists the phases, and run the check:

```bash
CLAUDE_PLUGIN_OPTION_DOCS_ROOT='${user_config.docs_root}' \
CLAUDE_PLUGIN_OPTION_EXEMPT_FILES='${user_config.exempt_files}' \
CLAUDE_PLUGIN_OPTION_BACKLOG_PATH='${user_config.backlog_path}' \
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/cli.py" catalog
```

and the check command above. The check rejects the claim if it overlaps an active peer's systems,
deliverable paths or dependency chain, if `max_active` is reached, or if a deliverable falls inside
another developer's workstream without that developer's recorded approval. **That rejection is the
answer, not an obstacle**: choose a different phase.

Commit the claim and the regenerated catalog together, in one commit that changes nothing else,
and push it. If the push is rejected as non-fast-forward, `git pull --rebase`, re-run the check,
and confirm the claim is still safe: a peer claimed in between, and its systems may now collide.

## 4. Cut the branches and the worktrees

**Product repository**, from its primary checkout on the product integration branch (confirm with
`git -C <product checkout> branch --show-current`; if it is on another branch, stop and report):

```bash
git -C <product checkout> pull --ff-only
git -C <product checkout> worktree add -b agent/<phase-id> \
  <product worktree directory>/<phase-id> <product integration branch>
```

**Control repository**, from its primary checkout on the up-to-date control integration branch:

```bash
git worktree add -b agent/<phase-id> <control worktree directory>/<phase-id> <control integration branch>
```

- Both branches are `agent/<phase-id>`, one in each repository. Both worktree directories sit
  beside their repositories, never inside them, so no test or scanner walks a second copy.
- Add the product worktree to this session: ask the person to type
  `/add-dir <product worktree directory>/<phase-id>`, or start the next session with
  `claude --add-dir <product worktree directory>/<phase-id>` from the control worktree.
- Confirm with `git worktree list` in each repository and report both paths.

## 5. Isolate the environment and run the product tests

Ignored directories — virtual environments, databases, `node_modules` — do not travel between
worktrees. Create the product worktree's own; never link a peer's. If the work runs a server,
choose a free port explicitly rather than assuming the default one is free. Run the product
repository's own tests once in the product worktree before changing anything, and keep the output:
a failure that was there before you started is not yours to discover at the end.

Ignored content also never travels through a merge. Anything written to an ignored path in either
worktree must be copied out by hand before the worktree is removed.

## 6. While the session runs

- Stay inside the phase's declared `systems` and `deliverables`. A deliverable written
  `product:<path>` is a path in the product worktree; one with no prefix is in the control
  worktree. If the work genuinely needs a file outside them, stop: narrow the change, or widen the
  phase's declarations on the control integration branch and re-run the check so peers see the
  wider lock before continuing.
- In the backlog, touch only this phase's lines and the catalog's `updated`.
- Commit narrow diffs, one concern per commit, each on its own repository's `agent/<phase-id>`.
- **Rebase onto each integration branch, never merge it in**, whenever a peer integrates, not only
  at the end.
- Pushing either `agent/<phase-id>` needs no approval; backing up your own work is not publishing.
- Record progress with the `checkpoint` skill as often as useful. It writes in the control worktree
  and never marks a phase complete.

## 7. Hand off — run the `session-close` skill

When the work is done, run `session-close`. It runs the verification, rebases both branches, has an
independent reviewer judge the product diff against the phase, and merges only on a passing review.
This skill never merges.

### If a rebase conflicts

- **A backlog conflict is normal** — two agents edited different phases in one file. Keep both
  sides: the peer's phases verbatim, your own phase's edits, `updated` set to today. Never resolve
  this file wholesale with `--ours` or `--theirs`; either silently deletes a peer's work.
- **A generated file conflicts** — the catalog: regenerate it rather than merging it by hand.
- **A duplicate document code** means a peer took the same number. Whoever integrates second
  allocates again, renames the file and updates every reference.
- **A conflict in product source code means the declared systems, deliverables or workstream paths
  were wrong.** Stop, do not force it, and report it; the declarations need fixing before either
  phase completes.
- When resolving a collision needs an actual choice, record the decision and its reason in the
  decisions document the backlog's `decision_record` names, in the same change.

## What this skill never does

- It never marks a phase complete and never merges.
- It never claims a phase whose deliverables fall inside another developer's workstream without
  that developer's recorded approval.
- It never acts on a product checkout that `product.py verify` refuses.
- It never switches either primary checkout away from its integration branch.
