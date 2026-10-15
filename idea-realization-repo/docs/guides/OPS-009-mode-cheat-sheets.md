---
schema_version: 1
id: doc-mode-cheat-sheets
code: OPS-009
title: Mode cheat sheets
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-15'
systems: []
depends_on: []
---

# Mode cheat sheets

One page per mode: the skills, agents and commands in the order they are used, one line each. The
full procedure for each mode is in its guide: planning (`OPS-002`), implementing (`OPS-003`),
validating (`OPS-004`). Where this page and a guide differ, the guide wins. Prompts to paste for each mode are in `OPS-010`.

**Entry point for every mode: `/start`** (long form `/idea-realization:start`). It asks which mode you are in and points to that mode's
first step.

Plugin skills are invoked as `/idea-realization:<skill>`. Agents are dispatched by name, never as a
general-purpose agent. Run scripts from the control repository's root; they find it from git and need no
`IDEA_REALIZATION_ROOT`. If a script resolves the wrong root, set the variable on that one
command (`IDEA_REALIZATION_ROOT=$PWD uv run ...`) and never `export` it: an exported value makes
`uv run pytest` fail (`OPS-001`, section 7; `OPS-008`, "check.py reports files from the wrong
repository").

## Planning

From a captured idea to approved plans, registered phases and validated, assigned batches.

1. `/start`, choose Planning.
2. `uv run plugins/idea-realization/scripts/brain.py load --kind decision` — read what is already decided.
3. `/idea-realization:idea` — record each new idea as given.
4. `/idea-realization:idea-triage <id>` — scout one open idea for related material; moves it to triaged.
5. `/idea-realization:partition-ideas` — group triaged ideas into tracks; stops for the owner at each gate.
6. `/idea-realization:next-code plan` (and `requirement`) — reserve the codes first; never choose one by hand.
7. `idea-planner` agent — drafts the requirement and plan for one accepted track, with the reserved codes.
8. `/idea-realization:plan-check <plan>` — check the plan has the sections it needs.
9. `plan-adversary` agent — attacks the plan at three altitudes (`plugins/idea-realization/docs/plan-review.md`, section 3).
10. `phase-splitter` agent — splits the approved plan into one-session phases with systems, deliverables and dependencies.
11. `batch-validator` agent and `scripts/batch_check.py` — confirm each batch is dependency-closed and collision-free.
12. Owner — orders `next_up` and sets `owner: <handle>` on each phase.
13. `/idea-realization:catalog`, then `uv run plugins/idea-realization/scripts/check.py` — must pass before the commit.

Done when: the plan is approved, its phases are registered, the check passes, and each batch is
validated and assigned.

## Implementing

From a claimed phase to merged code and a completion record.

1. `/start`, choose Implementing.
2. `git pull --rebase origin dev` on control `dev` — always, before any work.
3. `/idea-realization:brain` — load the context the phase needs.
4. `/idea-realization:backlog` — run the check, see the ready queue and its Conflicts column, orient on one phase.
5. `/idea-realization:session-start` — claim the phase (push the claim at once), cut both `agent/<phase-id>` branches and worktrees.
6. `/add-dir <product worktree>` — add the product worktree to the session.
7. Build and test in the product worktree; commit narrow diffs; rebase onto `origin/dev`, never merge it in.
8. `/idea-realization:checkpoint` — record progress as often as useful; it never completes a phase.
9. `bedrock-claude-advisor` agent — model ids, quotas and request shapes for Bedrock calls; read-only.
10. `aws-infra-reviewer` agent — review any infrastructure diff before it is deployed (`OPS-004`).
11. `aws-deploy` agent — deploy the change to the sandbox; the only agent that creates or updates AWS resources.
12. `aws-ops-inspector` agent — read the deployed resources' state and errors.
13. `/idea-realization:brain` — record what the next session should know, as a `lesson` or `decision`, in the control worktree before closing.
14. `/idea-realization:session-close` — verification, gating review, pull requests merged with merge commits, completion record on control `dev`.

Done when: the phase is complete and merged in both repositories, or handed back with an exact
`next_action`.

## Validating

Reviewing plans, branches, infrastructure and spend. Reviewers change nothing.

1. `/start`, choose Validating.
2. `phase-adversary` agent — the gating review of a phase's product diff; `session-close` dispatches it with the phase's acceptance.
3. `validator-code` agent — gating review instead, for a narrow code change judged against one requirement.
4. `review-judge` agent — shadow judge of the same diff, dispatched by a session other than the one that built the phase (`session-close` does not run it); its verdict is recorded and decides nothing.
5. `validator-check` agent — runs the mechanical checks on a branch.
6. `aws-infra-reviewer` agent — reviews every infrastructure diff for security, reliability, cost and fit.
7. `aws-cost-optimizer` agent — daily spend and idle-resource review (`OPS-007`).
8. `plan-adversary` agent — plan reviews at three altitudes (`plugins/idea-realization/docs/plan-review.md`, section 3).
9. Queued-phase review packs — `plugins/idea-realization/docs/plan-review.md`, section 4.
10. Smoke test of each release candidate (`OPS-006`).

Every verdict is recorded under `docs/reviews/` with its `reviewed_commit`; every finding is fixed or
accepted by the workstream's owner, with the disposition recorded.
