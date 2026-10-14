# Idea realization repository

The control repository for the team's hackathon work. It holds every idea, requirement, plan,
decision, backlog phase, session record and review record, and the agents, skills and governance
that move work through them. The product itself is built in a separate **product repository**; work
in it is planned, claimed, reviewed and recorded here.

## The pipeline

An idea moves through nine stages. Each gate marked *owner* is a decision only the owner makes.

| Stage | What happens | Gate |
|---|---|---|
| 1. Capture | An idea is recorded in the idea log (`idea` skill) | |
| 2. Triage | An agent records related plans, phases and ideas on it (`idea-triage`) | |
| 3. Partition | Triaged ideas are grouped into tracks (`partition-ideas`) | owner accepts the partition |
| 4. Plan | A requirement and plan are drafted per track (`idea-planner` agent) | |
| 5. Review | The plan is reviewed adversarially (`plugins/idea-realization/docs/plan-review.md`) | owner approves the plan |
| 6. Phase | The plan's phases enter `backlog/backlog.yaml`, one session each | owner orders `next_up` |
| 7. Build | A developer claims a phase and builds it in a product worktree (`session-start`) | |
| 8. Gating review | `phase-adversary` reviews the diff; `review-judge` runs in shadow (`session-close`) | a passing gating verdict |
| 9. Merge and record | The product branch merges, the control records merge, the phase is completed | |

The protocol behind each stage is in `plugins/idea-realization/docs/`. How the control and product
repositories divide the work is in `plugins/idea-realization/docs/two-repositories.md`, and how five
developers share it is in `plugins/idea-realization/docs/workstreams.md`.

## Quickstart

```bash
uv sync --extra dev
git config core.hooksPath tools/git-hooks             # pre-commit: private-content check + repository check
uv run pytest                                         # repository and plugin tests
uv run plugins/idea-realization/scripts/check.py      # ideas, backlog, documents, catalog
uv run plugins/idea-realization/scripts/doctor.py     # every scaffolded file unchanged
```

Per machine, never committed:

- **The private-content deny-list**, `.private/deny-list.txt`: one identifier per line (client
  names, account ids, anything that must never reach a tracked file). The pre-commit hook fails any
  commit that contains one. Ask the owner for the team's list.
- **The product repository's local path**, and **the AWS sandbox profile and region**: plugin options
  or environment variables, listed by `uv run plugins/idea-realization/scripts/paths.py`. The AWS
  values are `IDEA_REALIZATION_AWS_PROFILE` and `IDEA_REALIZATION_AWS_REGION`. The profile must be a
  named sandbox profile, never `default`.

Start a Claude Code session in this repository, with the plugin loaded and the product worktree
reachable:

```bash
claude --plugin-dir plugins/idea-realization --add-dir <path to your product worktree>
```

## Agents

| Agent | Role |
|---|---|
| `idea-planner` | Drafts a requirement and plan pair from an accepted track |
| `phase-adversary` | Gating reviewer of a phase's diff |
| `validator-code` | Judges a diff against its requirement and runs the verification commands |
| `validator-check` | Runs the mechanical gates and reports each result |
| `review-judge` | Shadow judge without a shell, beside the gating reviewer |
| `aws-deploy` | The only agent that creates or updates AWS resources |
| `aws-infra-reviewer` | Read-only review of infrastructure code and live resources |
| `aws-ops-inspector` | Read-only health, logs and alarms |
| `bedrock-claude-advisor` | Read-only advice on calling Claude through Amazon Bedrock |
| `aws-cost-optimizer` | Read-only cost and idle-resource report |

The triage and partition agents ship with the plugin.

## AWS safety

Every AWS command goes through `tools/aws-sandbox`, which uses only the configured sandbox profile
and region. Reads run freely. Only `aws-deploy` creates or updates. Deleting anything, and any
change to IAM, Organizations, account or billing settings, prompts a person for approval each time
(`.claude/settings.json`). These rules match command text: they are guardrails for agents, and the
sandbox account's own permissions are the real boundary.
