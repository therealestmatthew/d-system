# Idea realization repository

The control repository for the team's hackathon work. It holds every idea, requirement, plan,
decision, backlog phase, session record and review record, and the agents, skills and governance
that move work through them. The product itself is built in a separate **product repository**; work
in it is planned, claimed, reviewed and recorded here.

New to the team? Start with [ONBOARDING.md](ONBOARDING.md): the first-day checklist, how to claim
work, and where to get help. `uv run python tools/onboard_check.py` checks your machine against it.

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

After cloning, run the plugin's scaffold once. It recreates the gitignored
`.idea-realization/staging/` directory, which `doctor.py` otherwise reports missing; it never
overwrites a file that exists:

```bash
uv run plugins/idea-realization/scripts/scaffold.py --feature all
```

Per machine, never committed:

- **The private-content deny-list**, `.private/deny-list.txt`: one identifier per line (client
  names, account ids, anything that must never reach a tracked file). The pre-commit hook fails any
  commit that contains one. Ask the owner for the team's list.
- **The product repository's local path**, and **the AWS sandbox read profile, deploy profile and
  region**: plugin options or environment variables, listed by
  `uv run plugins/idea-realization/scripts/paths.py`. The AWS values are
  `IDEA_REALIZATION_AWS_READ_PROFILE`, `IDEA_REALIZATION_AWS_DEPLOY_PROFILE` and
  `IDEA_REALIZATION_AWS_REGION`; `aws/README.md` sets up the two roles behind them.

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

The sandbox has two IAM roles (`aws/README.md`): a read-only role, and a deploy role with no IAM,
Organizations, account or billing permissions. They are the boundary together with the **machine
rule**: a machine that runs agents holds no default or ambient AWS credentials, only the two named
sandbox profiles (`uv run python tools/check_aws_machine.py --probe` checks it). Every AWS command goes
through `tools/aws-sandbox`, which runs reads with the read profile and writes with the deploy
profile. A PreToolUse hook refuses AWS commands and SDK use outside the wrapper, and writes from any
agent but `aws-deploy`. Deleting anything prompts a person for approval each time. The hook and
the permission rules match command text: they are guardrails on top of the roles, not a substitute
for them.
