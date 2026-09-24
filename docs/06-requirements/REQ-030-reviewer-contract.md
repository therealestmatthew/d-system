---
schema_version: 1
id: doc-reviewer-contract-requirements
code: REQ-030
title: Reviewer contract requirements — independent, rationale-free build review by a judge without a shell, dispatched by the coordinator, with every verdict recorded
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-24'
updated: '2026-09-24'
systems: [sys-gov-docs, sys-governance]
depends_on: [doc-realization-role-contracts, doc-multi-session-coordination-protocol, doc-backlog-decisions]
---

# Reviewer contract requirements

Observable statements for the reviewer contract: step 2 of the Scout's staged path and row R24 of
its revised partition. The plan that delivers them is
[PLAN-047](../01-plans/PLAN-047-reviewer-contract.md).

## Observed problem and scope

Each failure is recorded in the repository or in a report the owner ruled on:

1. **The builder dispatches its own reviewer and hands it the rationale.** `/session-close` step 3
   tells the session being closed to launch the review sub-agent and give it "the session record's
   current path and content" (`.claude/commands/session-close.md`, step 3). The Validator contract
   says a validator sees "exactly the requirement text and the diff. Never the developer's
   rationale" (`GOV-014`, Validator, Inputs). The Scout's partition adversary rated this a blocker
   (`_working/session-manager/scout/orchestration-3-architecture.md`, section D.6, F1).
2. **Build-review dispatches name a general-purpose agent.** `PROMPT-036`'s dispatch templates say
   every dispatch "names the `general-purpose` charter" (`docs/02-prompts/PROMPT-036-build-coordinator.md`,
   "Dispatch templates"), including the validator and adversary. The owner ruled on 2026-09-23 that
   reviews backing a merge come from a dedicated validator or adversary type, never general-purpose.
   Idea `000241` records a general-purpose reviewer that told its caller to ignore part of its own
   output.
3. **Every reviewer type can run any command.** `demo-adversary`, `demo-validator-code`,
   `demo-validator-check` and `partition-adversary` all declare `tools: Read, Grep, Glob, Bash`
   (`.claude/agents/`), so "changes nothing" holds by instruction only. `partition-analyst` shows
   that a type without `Bash` works here: it declares `tools: Read, Grep, Glob`.
4. **No build-review verdict is recorded.** Review outcomes live in session records and `READY`
   messages. Nothing records which reviewer type and model passed a phase, whether the owner later
   overturned it, or whether a defect it passed reached `dev` (idea `000215`; Builder A's mapping of
   the owner's design, section 4, "Verdict ledger").
5. **The spot-audit is not practised.** The owner spot-audit in `GOV-014` appears in no session
   record of 2026-09-22 or 2026-09-23 (Scout report `orchestration-1-evidence.md`, control 28). The
   owner replaced it on 2026-09-23 with sampled independent re-review, 1 in 10 plus every
   once-rejected unit (applied to the documents by `phase-dam-01`), but nothing draws the sample.

The owner's rulings of 2026-09-23 that set this scope, as the Session Manager's board records them:
"O-5 judge without Bash + fixed command runner"; "O-6 coordinator dispatches assurance (out of
P3:164)"; "Q7 record verdicts now, new reviewer types start in shadow"; "session-close reviewer gets
no session record"; "re-review 1 in 10 + every once-rejected"; and "Q7/Q9 -> second docs phase
after reviewer contract", with Q9 being "security review plan-time (GOV-010) + diff-time at READY
for auth/network/secrets/deps".

## Observable requirements and verification

| ID | Required observable behaviour | Verification |
|---|---|---|
| R01 | A reviewer-judge agent type exists whose declared tools are exactly `Read, Grep, Glob`: no `Bash`, `Edit` or `Write` | Read its front matter; a fixture copy that adds `Bash` fails the phase's check on the agent file |
| R02 | A command runner executes, at a named commit in a detached worktree, exactly the phase's `verification` commands and the four gate checks, and nothing its caller supplies beyond the phase id and the commit. It writes each command's output to an evidence file and prints a manifest of command, exit code, file path and sha256 | Fixtures: a phase whose commands run (manifest lists each with its exit code); a failing command (recorded with its exit code, not retried); an unknown phase id (refused); an extra command argument (refused). The detached worktree is removed afterwards |
| R03 | `GOV-014` states the assurance dispatch rule: every build review is dispatched and briefed by the coordinator (the Session Manager today), never by the session that built the phase. The brief holds the phase's `scope`, `acceptance` and `verification`, the commit range and the runner's manifest, and nothing the builder wrote | Read `GOV-014`; the rule names what the brief may and may not contain |
| R04 | `/session-close` step 3, `PROMPT-036` (step 6 and its validator and adversary templates) and `GOV-017`'s merge gate follow R03. A building session asks the coordinator for its review instead of dispatching one; the review templates name a dedicated reviewer type; `GOV-017` defines the request and verdict messages | `grep -n "general-purpose"` in `PROMPT-036` returns no reviewer template line; `/session-close` step 3 lists no builder-written input; `GOV-017`'s message table has the two new messages |
| R05 | Every build-review verdict is recorded in a schema-validated record: reviewer type, the sha256 of its agent definition, model, phase, reviewed commit, verdict, findings, whether it gated or ran in shadow, and a list of later outcomes (owner overturned it; a defect it passed was found on `dev`; a sampled re-review result) | Schema tests: a valid record passes; one without `model` fails; one with an outcome appended passes |
| R06 | The reviewer-judge type runs in shadow: its verdicts are recorded with `gating: false` and do not decide a merge, and promotion to gating is an owner decision recorded in `GOV-003` | Read `GOV-014` and `GOV-017`; the first recorded judge verdict carries `gating: false` |
| R07 | A sampler draws, from the verdict records since the last sampling, one in ten passed build reviews by a recorded seed, plus every phase that was rejected once before it passed. A sampled phase is re-reviewed by a dedicated type other than the one that passed it, and the result is appended as an outcome | Fixtures: the same seed gives the same sample; a once-rejected phase is always in it; the re-reviewer type differs from the original |
| R08 | `GOV-010` requires a plan to name the threat surfaces it touches (authentication, network exposure, secrets, dependencies), and `GOV-017`'s `READY` carries a diff-time security review for a phase that touches one of them | Read both passages |
| R09 | `GOV-003` records the owner's rulings O-5, O-6 and Q7 as standing, each dated and quoted | Read the entries |

## What each requirement is not

- **R01 does not retire the existing reviewer types.** `demo-adversary` and the others keep gating
  while the judge runs in shadow (R06).
- **R02 is not a general command runner.** It runs only commands the backlog already declares for
  the phase, plus the four gate checks.
- **R03 does not change who approves a merge.** G4 stays the owner's on every merge.
- **R05 is not a model-comparison study.** Recording the model is the prerequisite the owner named
  for cross-model review ("O-8 cross-model review after ledger records model, in shadow"); that
  review is not built here.
- **R07 does not replace the owner's G5 judgement.** The sample and its results go to the owner.
- **R08 does not build a security scanner.** It names where a security review happens and what
  triggers it.
