---
schema_version: 1
id: doc-day-one-prompts
code: OPS-010
title: Day-one prompts
kind: operation
status: draft
owner: repository-owner
created: '2026-10-15'
updated: '2026-10-15'
systems: []
depends_on: []
---

# Day-one prompts

Prompts a developer pastes into Claude Code for the common sessions: the first session on a new
machine, planning, implementing a phase, asking for a review, and release day. Each prompt follows
`CLAUDE.md` and the guides it names; where a prompt and a guide differ, the guide wins. The
one-page command list per mode is in the mode cheat sheets (`OPS-009`).

## How to use these prompts

- Start Claude Code in the **control repository's primary checkout** with the plugin loaded:
  `claude --plugin-dir plugins/idea-realization` (ONBOARDING §3 step 10). Then paste one prompt.
- Text in `<angle brackets>` is yours to fill in before you paste. Each prompt fits one session.
- Where a prompt runs the product's tests, it runs them in the product worktree, as the
  `session-start` skill §5 and the implementing guide (`OPS-003`, step 3.6) state.
- The plugin's skills may be listed as `/idea-realization:<skill>` (for example
  `/idea-realization:start`). Each prompt names the skill, and the agent picks the form this
  machine uses.

---

## 1. First session: set up the machine, then `/start`

Paste this once per machine, on your first day. It does not claim any work.

```text
This is my first session in this team's control repository. I am a new developer, and my handle
will be <handle>.

1. Read CLAUDE.md and ONBOARDING.md in full before doing anything else.
2. Run `uv run python tools/onboard_check.py` and show me its output as printed. For each FIX
   line, take me through the matching step in ONBOARDING.md section 3, one step at a time, in
   order. I run anything that needs a credential or a URL myself. Do not make up a URL, an email,
   an AWS profile name or a deny-list entry; ask me for each one with AskUserQuestion.
3. Never read or write anything under .private/ or ~/.aws/ unless I tell you to. I will save the
   deny-list myself.
4. The only commit you may make today is my `owners` entry in docs/systems.yaml (ONBOARDING
   section 3, step 3), and later my workstream claim in docs/workstreams.yaml (section 4). Each
   goes directly on control `dev`, is pushed at once, and contains nothing else. Show me the diff
   and ask before you commit.
5. Repeat `uv run python tools/onboard_check.py` until it exits 0, and show me the final output.
6. Then run the `start` skill and stop at its mode question.

When something I asked for conflicts with CLAUDE.md, say so and follow CLAUDE.md. If a document is
wrong, quote the passage and tell me. Do not edit CLAUDE.md.
```

## 2. Planning mode

For the person who turns ideas into an approved plan and phases. The planning guide (`OPS-002`)
reserves every gate to the owner. Someone who is not the owner stops at each gate.

```text
Planning session. I am <handle>; the owner is <owner handle>.

1. Run the `start` skill and choose Planning. Read docs/guides/OPS-002-planning-mode.md in full.
   Follow it step by step and ask me before each step.
2. First, I pull: `git pull --rebase origin dev` in the control primary checkout. Do not run the
   pull yourself. Then load what is already decided:
   `uv run plugins/idea-realization/scripts/brain.py load --kind decision`.
3. Today's work: <record these ideas: ... | triage the open ideas | partition the triaged ideas |
   plan accepted track <track> | split approved plan <PLAN-code>>.
4. Run scripts from the control root with IDEA_REALIZATION_ROOT set to it. Dispatch every agent
   by its own name (idea-triage, idea-planner, plan-adversary, phase-splitter, batch-validator).
   Never dispatch a general-purpose agent in place of one.
5. Reserve every document code with the `next-code` skill. Never pick a code by reading a
   directory.
6. Idea commits go directly on control `dev` and are pushed at once. Everything else (partition
   record, requirement, plan, backlog phases, batches, catalog) goes in a control worktree on
   `agent/<handle>-<slug>` and reaches `dev` through a pull request.
7. Stop at each owner gate and tell me what the owner has to decide: accepting the partition,
   approving the plan, ranking next_up, composing a batch and assigning phases. No agent makes
   those decisions, and you do not.
8. Before any commit, `uv run plugins/idea-realization/scripts/check.py` must exit 0. Show me its
   output.
```

## 3. Implementing a phase

For building one phase. The first form starts a new phase; the second resumes one this
developer already claimed.

### 3a. Start a phase

```text
Implementing session. I am <handle>. <Optional: the owner assigned me <phase-id>.>

1. Run the `start` skill and choose Implementing. Read
   docs/guides/OPS-003-implementing-mode.md in full and follow its steps in order.
2. First, I pull: `git pull --rebase origin dev` in both primary checkouts (control and product).
   Do not run the pull yourself.
3. Load context with the `brain` skill for the phase's subject.
4. Run the `backlog` skill. Take the first ready phase in next_up order, preferring one with
   `owner: <handle>`. If the check is red, stop: nothing is claimed on a red backlog.
5. Run the `session-start` skill. It asks before claiming. When it asks, show me the phase's
   scope, acceptance, verification, systems and deliverables, its Conflicts column, and whether
   its deliverables are in my workstream. The claim goes directly on control `dev` and is pushed
   at once.
6. After the claim, tell me the exact `/add-dir <product worktree dir>/<phase-id>` line to run.
   Install the product worktree's own environment and run the product's tests there once,
   before any change. Keep that output.
7. Build only inside the phase's declared systems and deliverables. A path that starts with
   `product:` is in the product worktree. If the work needs a file outside them, stop and tell me.
   Commit small diffs on agent/<phase-id>. Rebase onto origin/dev; never merge dev in.
8. Choose a free port yourself for any dev server.
9. Every AWS command goes through tools/aws-sandbox. Only the aws-deploy agent deploys. Ask
   bedrock-claude-advisor before writing a Bedrock call.
10. Record any new ask as an idea with the `idea` skill. Do not fold it into this phase.
11. When I stop, run the `checkpoint` skill from the control worktree. Paste the product
    verification output into the record yourself: the skill does not cover the product
    repository yet.
```

### 3b. Resume a claimed phase

```text
Resume <phase-id>. I claimed it earlier; it is active with my agent id.

1. Run the `start` skill and choose Implementing. I pull `dev` in both primary checkouts first.
2. Do not claim again. Read the phase in backlog/backlog.yaml on control `dev`, then its latest
   session record in the control worktree <worktree dir>/<phase-id>, and its next_action.
3. Check that both agent/<phase-id> worktrees exist and say where each branch tip is
   (`git -C <path> log -1 --oneline`). If one is missing, stop and tell me. Do not recreate it
   from memory.
4. Add the product worktree with /add-dir. Rebase both branches onto origin/dev and rerun the
   product's tests in the product worktree before changing anything.
5. Then continue from step 7 of the start-a-phase prompt.
```

## 4. Asking for a review

There is no `review` skill (`OPS-004`, "Reviewing a peer's ready branch"). Your own phase's gating
review runs inside `session-close`. A review of a peer's branch is done by hand and does not
replace their gating review.

### 4a. Close your own phase (the gating review)

```text
Close <phase-id>.

1. Run the phase's verification list first: each command in the product worktree, except those
   that start with `control:`, which run in the control worktree. Show me the real output. A
   failing check is a result; report it, do not retry it until it passes.
2. If any acceptance condition does not hold, stop. Run the `checkpoint` skill and tell me what
   remains.
3. If every condition holds, run the `session-close` skill. Its gating review uses a fresh
   phase-adversary agent (or validator-code for a narrow change against one requirement), never a
   general-purpose agent and never a fork of this session. Give the reviewer the brief the skill
   specifies and none of my explanations.
4. Show me the verdict's first line and every finding. Fix each finding or ask me to accept it.
   After a fix, the new HEAD gets a fresh review. Two rejects on the same finding: stop and tell me.
5. Merge only on a pass, with merge commits, control first and then product once `verify` passes.
   Confirm that the product merge commit's second parent is the reviewed commit. Then write the
   completion commit on control `dev` and push it.
6. Record what the next session should know with the `brain` skill.
7. Never commit with --no-verify. A failing hook is a finding to fix or report.
```

### 4b. Review a peer's pushed branch

```text
Validating session. Review <peer handle>'s branch for <phase-id>. This review is advice for the
peer and does not replace their gating review in session-close.

1. Run the `start` skill and choose Validating. Read docs/guides/OPS-004-validating-mode.md,
   section "Reviewing a peer's ready branch", and follow its six steps.
2. `git fetch origin` in each primary checkout and confirm that origin/agent/<phase-id> exists. If
   it does not, stop and tell me.
3. Create detached review worktrees outside the repositories, at the pushed commit, so the peer's
   branch never moves. Install the product worktree's own environment there.
4. Dispatch a fresh phase-adversary agent with the phase's scope, acceptance, verification and
   deliverables from control `dev`, both review worktree paths with the range origin/dev...HEAD,
   and the requirement and plan paths. Give it nothing the peer wrote to explain the work.
5. Show me the full reply with the reviewed commit, so I can send it to the peer. Commit nothing
   on the peer's branch.
6. Change nothing you review.
7. When I confirm, remove both review worktrees with `git worktree remove`.
```

## 5. Release day

Demo 2026-11-05, freeze 2026-11-03 (`OPS-006`). Only the owner merges into `main` and creates
tags. Each prompt below states which role uses it. The release developer and the validator should
be different people.

### 5a. Release developer: release candidate and deploy

```text
Release session. I am the release developer for demo-rc-<n>. Read
docs/guides/OPS-006-demo-day-runbook.md in full and follow it.

1. In both repositories, in that order (control, then product), prepare the release pull request
   from dev to main with the command in OPS-006, "Release candidate", step 1. Show me the command
   and the body before you run it. In the product repository, wait for `verify` with
   `gh pr checks <number> --watch`.
2. Stop there. The owner merges the release pull requests and creates the demo-rc-<n> tags. Do
   not merge into main, and do not create, move or push a tag.
3. After the owner tags, check the machine: `uv run python tools/check_aws_machine.py --probe`
   must print OK, then run `tools/aws-sandbox whoami`.
4. Check out the tag in a separate detached product worktree (OPS-006, "Local deployment",
   step 2). Do not use any working branch.
5. Dispatch the aws-deploy agent with the worktree path, the tag, the product's deploy command and
   the smoke test's first check as its verification. It shows a diff or change set before it
   applies anything. Before any prompt to delete appears, tell me exactly what will be deleted. A
   refused prompt means stop.
6. Keep the deploy report, with what was created or updated and the verification output, where
   the owner asks.
```

### 5b. Validator: smoke test

```text
Validating session. Smoke test demo-rc-<n> (or demo-final) as deployed. I am the validator, not
the person who deployed it.

1. Read docs/guides/OPS-006-demo-day-runbook.md, sections "Smoke test" and "On the day".
2. Run each check of the written smoke test in the product repository, in order. Record pass or
   fail for each check with its real output or a screenshot.
3. Dispatch the aws-ops-inspector agent to read the deployed resources' state and recent errors,
   and add its output to the record.
4. Change nothing on the deployed stack. A failed check becomes a fix: record it as an idea with
   the `idea` skill, and the owner registers a phase for it.
```
