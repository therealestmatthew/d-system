---
schema_version: 1
id: doc-implementing-mode
code: OPS-003
title: Implementing mode
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-15'
systems: []
depends_on: []
---

# Implementing mode

How one developer's agent takes one queued phase from the backlog to merged code and a completion
record. The procedures are the `session-start`, `checkpoint` and `session-close` skills; this guide
gives their order, what each leaves behind, and where the AWS agents fit. Git and GitHub mechanics
are in the branching and CI guide (`OPS-001`); claims, review and merge for a team are in the team
workflow (`OPS-005`); the one-page command list is in the mode cheat sheets (`OPS-009`).

## The two repositories

The **control repository** (this one) holds the backlog, plans, session and review records. The
**product repository** holds the code; its remote is set per machine as `product_remote` in the
untracked `.idea-realization/local.yaml`. A session has a
worktree in each, both on a branch named `agent/<phase-id>`
(`plugins/idea-realization/docs/two-repositories.md`).

| What | Where |
|---|---|
| The claim commit and the completion commit | Control primary checkout, directly on control `dev`, pushed at once |
| Code, tests, verification commands | Product worktree, `<product worktree dir>/<phase-id>` |
| Session record, checkpoints, review verdict records | Control worktree, `<worktree dir>/<phase-id>` |

Neither primary checkout ever leaves `dev`.

## The steps

### 1. Start

Run `/idea-realization:start` and choose Implementing. In the control primary checkout,
`git pull --rebase origin dev`
before anything else, and load the context the phase needs with the `brain` skill.

### 2. Choose a phase: `backlog` skill

`/idea-realization:backlog` runs the check, shows the ready queue with its Conflicts column, and
orients on one phase without claiming it. Take the first ready phase in `next_up` order, preferring
one assigned to you (`owner: <handle>`). If the check fails, stop: nothing is claimed on a red
backlog.

### 3. Claim and set up: `session-start` skill

`/idea-realization:session-start` does, in order:

1. Pulls origin `dev` in the control primary checkout.
2. Asks before claiming, reporting the phase, its conflicts, whether its deliverables sit in your
   workstream, and anything that looked wrong.
3. On a yes, edits only this phase's lines (`status: active`, `agent: <handle>/agent-<name>`),
   regenerates the catalog, runs the check, commits directly on control `dev` and **pushes at
   once**. The check refuses a claim that overlaps an active phase's systems, deliverable paths or
   dependency chain, that exceeds `max_active`, or that falls inside another developer's workstream
   without their recorded approval. It warns, and does not refuse, when the phase's `owner:` is a
   different developer: ask that developer before going on. A rejected push means a peer pushed
   first: `git pull --rebase`, re-run the check, push again if the claim is still safe.
4. Cuts `agent/<phase-id>` from `origin/dev` in both repositories, each in its own worktree outside
   the repository.
5. Asks you to add the product worktree to the session with
   `/add-dir <product worktree dir>/<phase-id>` (or start the next session with
   `claude --add-dir <product worktree dir>/<phase-id>` from the control worktree).
6. Has you install the product worktree's own environment and run the product's tests once before
   any change, keeping the output.

**Output:** an active phase pushed on control `dev`, two worktrees, a baseline test run.

### 4. Build in the product worktree

- Stay inside the phase's `systems` and `deliverables`. A deliverable written `product:<path>` is a
  path in the product worktree. If the work needs a file outside them, stop, and widen the
  declaration on control `dev` first so peers see the wider lock.
- Commit narrow diffs on `agent/<phase-id>`. Rebase onto `origin/dev` whenever a peer integrates;
  never merge `dev` in.
- Push your own `agent/<phase-id>` branches whenever you like; that needs no approval.
- Build against merged interfaces and mocks, never against a peer's unmerged branch (`OPS-005`,
  section 2).
- Pick a free port explicitly for any dev server.
- Record new asks as ideas with the `idea` skill; do not fold them into the phase.

### 5. Record progress: `checkpoint` skill

`/idea-realization:checkpoint` writes the session record in the control worktree: the phase, the
verification output, an acceptance verdict per condition, the backlog fields, and what is
unresolved. It is safe to repeat and never marks a phase complete.

**Current limitation: the checkpoint skill is still written for one repository.** It edits and runs
verification only in the working tree it is run from, and does not record the product branch's
state. Its two-repository version is the queued phase **Checkpoint skill for two repositories**
(`phase-boot-14`), whose acceptance is that a checkpoint records both branches' tips. Until it lands:

- run `checkpoint` from the control worktree;
- run the phase's product verification commands in the product worktree yourself, so the
  `## Verification` section holds their real output, not a summary;
- when you hand off, make sure the product `agent/<phase-id>` branch is pushed and that
  `next_action` says what remains in the product repository.

### 6. AWS work, when the phase has any

All AWS access goes through `tools/aws-sandbox` with the two sandbox profiles; no machine holds a
`default` profile or ambient credentials. Check the machine once with
`uv run python tools/check_aws_machine.py --probe` and `tools/aws-sandbox whoami`.

| Need | Agent | What it does |
|---|---|---|
| Calling Claude through Amazon Bedrock | `bedrock-claude-advisor` | Read-only. Which models and inference profiles the sandbox can call in its region, request shapes, quotas, prompt caching, streaming and tool use, checked against the account and current documentation. Ask before writing Bedrock calls, not after. |
| Reviewing an infrastructure diff before it is deployed | `aws-infra-reviewer` | Read-only. Ranked findings on IAM scope, exposure, encryption, secrets, tags, alarms and idle cost (`OPS-004`). |
| Deploying the change to the sandbox | `aws-deploy` | The only agent that creates or updates AWS resources. Runs on your machine with the deploy role, states its plan, shows a diff or change set before applying, asks a person to approve every deletion, and reads back what it changed. Deploy is local only; no CI workflow deploys (`OPS-001`). |
| Checking what is running and why it is not | `aws-ops-inspector` | Read-only. Health, logs, alarms and recent errors, with the real output. |

Tag every resource with `project` and `owner` (`OPS-007`, "Tags"). Keep the deploy report and the
inspector's output in the session record: they are evidence for acceptance conditions about the
deployed system.

### 7. Verify

Run every command in the phase's `verification` list and keep the real output. A command runs in
the product worktree unless it starts with `control:`, which runs in the control worktree. A failing
check is a result to record, not a step to retry until it passes. `session-close` runs the
verification again after rebasing, and that run is the one the review judges.

### 8. Close: `session-close` skill

`/idea-realization:session-close` is the only procedure that marks a phase complete. It:

1. Runs the checkpoint steps against the current state.
2. Rebases both branches onto `origin/dev`, runs the verification and the control check.
3. Runs the **gating review**: a fresh `phase-adversary` agent (or `validator-code` for a narrow code
   change against one requirement) judges the product diff against the phase's acceptance. The
   review and the shadow `review-judge` are described in validating mode (`OPS-004`).
4. Records the verdict under `docs/reviews/` in the control worktree, with `reviewed_commit` set to
   the product `HEAD` that was judged. Every finding is fixed (with a fresh review of the new
   `HEAD`) or accepted by the developer who owns the workstream. Two rejects on the same finding:
   stop and report to the owner.
5. On a passing verdict, pushes both branches, opens a pull request to `dev` in each repository,
   merges the control pull request, waits for the product's required check `verify`, then merges
   the product pull request. Both are **merge commits**, pinned with `--match-head-commit`. The
   passing gating review is the approval for both merges; no separate approval is asked for.
6. Confirms the product merge commit's second parent equals `reviewed_commit` and that the merge is
   on product `dev`.
7. Writes the **completion commit directly on control `dev`**: `status: complete`, `session`,
   `completion_evidence`, `product_merge: <merge commit>`, `result`, the phase removed from
   `next_up`, the catalog regenerated, the check run, `git pull --rebase`, then push. If the push
   fails after the product merged, retry; never revert the product merge. The phase stays `active`
   until this commit lands.
8. Removes both worktrees and both local branches, copying out any ignored content first.

A repository with no `origin`, or a local-path one, uses a local `git merge --no-ff` instead; a
hosted `origin` that `gh` cannot reach stops the close rather than merging locally. The skill says
which path applied. Commands for each step and the failure cases are in `OPS-001`, section 4, and
`OPS-008`.

Before you run `session-close`, record what the next session should know with the `brain` skill,
as a `lesson` or a `decision`, in the control worktree. The entry and `brain/index.md` are committed
on `agent/<phase-id>` and reach `dev` in the control pull request.

## How implementing mode ends

A session ends in one of two states:

- **Complete and merged.** The gating review passed, both pull requests merged with merge commits,
  the second-parent check held, and the completion commit is on control `dev`.
- **Released with a `next_action`.** Any condition is unmet: verification is red, the review
  rejected, or the work is unfinished. Run `checkpoint`. If someone will continue, the phase stays
  `active`; if nobody is continuing it, return it to `queued`, clear `agent`, `session`,
  `completion_evidence` and `result` in the same edit, and write a `next_action` that names exactly
  what remains, including anything the review found. Push both feature branches so no work exists
  only on one machine. Closing honestly incomplete is a correct outcome.
