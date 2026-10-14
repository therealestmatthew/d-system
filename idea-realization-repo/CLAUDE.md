# CLAUDE.md

Orientation for Claude Code in this repository: what it is and where things live.

## Read AGENTS.md first

**[AGENTS.md](AGENTS.md) is the working agreement and governs everything you do here.** This file is
orientation only; where the two ever disagree, AGENTS.md wins.

## Never edit this file or AGENTS.md without explicit approval

**Do not modify `CLAUDE.md` or `AGENTS.md` for any reason without the owner's explicit approval for
that specific change.** There is no exception: not to correct an error, not to record something you
learned, not because a phase seems to cover it, and not as tidy-up alongside other work. If you
believe either file is wrong, quote the passage, propose the replacement wording, and stop.

## Do not assume. Ask.

When something is unclear, unstated or open to more than one reading, ask, using the
AskUserQuestion tool, at the point the work reaches the uncertainty. A question that can wait is
stated as an assumption and the work continues; an assumption that changes what gets built is a
question.

Do not turn a one-time instruction into a standing rule. If a pattern seems worth making
permanent, propose it and let the owner decide.

## Verify before claiming ignorance

If a tool can settle a fact, use it before saying you do not know. Any named model, product,
library, AWS service or version, and anything dated after your knowledge cutoff: search or read
first, answer second.

## When you get something wrong

Say plainly that it is a correction, in one sentence, fix the claim and continue. If the slip came
from a habit that could recur, propose an entry for the anti-pattern procedures
(`docs/governance/GOV-002-anti-pattern-procedures.md`); the owner approves each one.

## How to report

Follow `plugins/idea-realization/docs/reporting.md`: name things before citing their codes, paste
the output that carries information, and do not block on a question that can wait.

## Facts worth knowing before the first command

- This is the **control repository**. Code is built in the **product repository**, reached with
  `--add-dir`; see `plugins/idea-realization/docs/two-repositories.md`.
- Control-repository work lands on `main` only with the owner's approval of each merge. A product
  merge needs a passing gating review.
- Every session works in its own worktree; the primary checkout's branch is never switched.
- `.private/` is confidential and untracked, and holds the deny-list. Nothing from it is ever written
  into a tracked file.
- Every AWS command goes through `tools/aws-sandbox`, never the bare `aws` command. The two
  sandbox IAM roles are the boundary (`aws/README.md`); the hook and permission rules are
  guardrails.

## Project

The idea realization system for the team's hackathon project: an idea is captured, triaged,
grouped, planned, reviewed, broken into one-session phases, built in the product repository,
reviewed by a gating agent and recorded. The plugin under `plugins/idea-realization/` carries the
pipeline's tools, skills and protocol.

| Path | What it holds |
|---|---|
| `AGENTS.md` | The working agreement |
| `ideas/` | The append-only idea log, its rendered view, the priority list and accepted partitions |
| `backlog/backlog.yaml` | Phases, one session each; on `main` it is also the lock table |
| `docs/` | Governed documents: `plans/`, `requirements/`, `decisions/`, `architecture/`, `governance/`, `sessions/`, `prompts/`, plus `codes.yaml`, `systems.yaml`, `workstreams.yaml` and the generated `catalog.md` |
| `docs/reviews/` | Review verdict records |
| `.claude/agents/` | The planner, the review-gate agents and the AWS agents |
| `.claude/settings.json` | Permission rules, including the AWS rules |
| `plugins/idea-realization/` | The plugin: scripts, skills, schemas, templates, protocol documents and its tests |
| `.idea-realization/` | Product-repository settings, install state and schema copies |
| `tools/` | The confidentiality check, the AWS sandbox wrapper, the AWS PreToolUse hook and the git hooks |
| `aws/` | The sandbox's two IAM role policies and their setup page |
| `test/` | Tests for `tools/` |
| `.private/` | Untracked: the deny-list and other per-machine confidential files |
