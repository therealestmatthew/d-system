---
schema_version: 1
id: doc-single-session-orchestration-protocol
code: GOV-022
title: Single-session orchestration protocol — one session, its subagents, and the hand-off to the trunk
kind: governance
status: draft
owner: repository-owner
created: '2026-10-08'
updated: '2026-10-08'
systems: [sys-governance, sys-backlog]
depends_on: [doc-multi-session-coordination-protocol, doc-coordinator-protocol, doc-conversation-guidelines, doc-adr-multi-agent-concurrency]
---

# Single-session orchestration protocol

How one interactive session runs owner-directed work through subagents when it is the **only
session in its checkout**: a claude.ai/code cloud session in its own ephemeral clone, or a local
session that has the repository to itself. It restructures the multi-session coordination protocol
([GOV-017](GOV-017-multi-session-coordination-protocol.md)) for that case.

`GOV-017` exists because several top-level sessions share one machine and one primary checkout on
`dev`, so access to that checkout has to be serialized through a Session Manager, turn messages and
claim slots. A single session has none of those peers. Most of `GOV-017`'s machinery therefore has
nothing to coordinate, and keeping it would spend the session's context on messages no one receives.
What survives is everything that protects the trunk and the review, because those hold whether one
session is running or eight.

The coordinator protocol ([GOV-013](GOV-013-coordinator-protocol.md)) governs how to *design* a
session that drives many units of work through dispatched agents. This document does not repeat it.
It says which of `GOV-013`'s rules bind an ordinary single session that dispatches a handful of
agents, and which belong only to a full coordinator run.

It was written on 2026-10-08, in the second cloud session the owner opened with the same standing
instruction on subagent cost, from that instruction, from the three cloud sessions that ran under
`docs/00-working/cloud-prompts/master-prompt.md` between 2026-09-28 and 2026-10-01, and from
`GOV-017` and `GOV-013`. Where it states a rule that neither of those documents states, the rule is
marked **proposed** and listed under *Open questions* for the owner to confirm or strike. Nothing
here is a standing rule until the owner says so.

## Scope

This protocol applies when all of the following hold:

1. The session is the only session writing in its checkout. A cloud session always is. A local
   session is only when no peer has a worktree on the same machine.
2. The session runs **owner-directed work with no backlog phase**, or a phase the owner names at
   kickoff. It never claims a phase itself: a claim is a commit on `dev` in the primary checkout
   (`AGENTS.md`, "Concurrent agents: claim a phase"), and a cloud session cannot make one.
3. The session's work reaches `dev` only through the merge gate in `GOV-017`, run by the owner or
   by a local Session Manager after the session has pushed its branch.

When several sessions are running at once, `GOV-017` governs and this document does not apply. A
local session that wants this protocol instead of `GOV-017` says so in its first report, so the
owner can refuse.

## What a cloud session is

Facts about the environment, as observed in the cloud sessions this document was written from.
Rules below depend on them.

- **The clone is fresh, isolated and ephemeral.** The repository is cloned when the container starts
  and the container is reclaimed after inactivity. Nothing survives except what is pushed. Gitignored
  state (`_working/`, `data/`, `.venv/`, `_capture/`) dies with the container.
- **The branch is assigned.** The harness gives the session a branch (`claude/<slug>`) or the kickoff
  names one (`agent/cloud-<slug>`). The session develops on that branch and pushes it. It never
  commits to, merges into or pushes `dev`.
- **`_private/` is absent.** The owner's real portfolio is not in the clone, so nothing that needs the
  real data root can run here. `AGENTS.md` forbids reading it in any case.
- **The agent types come from the branch the clone opened on.** On 2026-09-28 a cloud session failed
  to dispatch `partition-adversary` because its clone opened on a branch cut from `main` on
  2026-09-12, before that agent existed (`handoff-planning-protocol.md`, section 4). Check the agent
  type is available before the first dispatch, and read `.claude/agents/<type>.md` from the branch
  you are on, not from memory.
- **The owner may be away.** A cloud session is often started from a phone and read later. Questions
  block until the owner returns; `GOV-006`'s rule that a question which can wait is stated as an
  assumption and surfaced later matters more here than in a terminal session.
- **The worker process can restart mid-session.** On 2026-10-08 this session's worker restarted
  once with no loss, because every result was already in a file. State that lives only in the
  conversation is lost on a restart; state in files is not.
- **The environment is empty until synced.** `uv sync --extra dev` runs before any governance
  command, test or generator, as `AGENTS.md`'s worktree setup requires. It takes about a minute and
  runs in the background while orientation continues.

## The roles collapse into one session

`GOV-017`'s roster exists to split work that cannot share a checkout. In a single session every role
is either the session itself or a subagent it dispatches.

| `GOV-017` role | Single-session equivalent |
|---|---|
| Session Manager | The session. It sequences, dispatches, verifies and reports. There is no lock to hold and no slot to allocate |
| Builder A, Builder B, Standby Builder | Creator subagents the session dispatches, or the session itself for a small change. One branch, the assigned one, carries all of it |
| Batch Runner | Not present. A batch run under `PROMPT-036` is a coordinator run and follows `GOV-013` and `PROMPT-036`, not this document |
| Scout | Read-only research agents (`Explore`, or `general-purpose` with a read-only brief) dispatched in parallel at the open |
| Ideation | The session records ideas itself on its branch through `tools/append_idea.py` (see *Ideas*) |
| Prompt Planner | Not present. A prompt the session writes is a governed `PROMPT` document on its branch like any other deliverable |
| Owner Terminal | The owner, or the local Session Manager, at the merge gate. Pushing `dev` and deleting `origin` branches stay owner-only commands and never happen from the cloud |

## What is dropped, and why

Each of these is `GOV-017` machinery that only serializes access to a shared checkout. A single
session drops it.

- **The primary-checkout lock and the `TURN?` / `GRANTED` / `TURN DONE` messages.** There is no
  primary checkout in the clone, and no one to grant a turn. The clone's single checkout is the
  session's working tree.
- **Claim slots and `ASSIGN`.** The session claims nothing. If the owner names a backlog phase at
  kickoff, the claim commit on `dev` is made by the owner or the local Session Manager, in the
  primary checkout, before or after the cloud session runs; the cloud session says in its first
  report that it runs unclaimed and that peers hold no lock against it (`AGENTS.md`, "Owner-directed
  work with no backlog phase").
- **`ListAgents`, `/rename` and the registered-name check.** There are no peer sessions to address.
- **The board under `_working/session-manager/`.** It is gitignored and would die with the
  container. The session's durable state is its branch: committed files and a tracked hand-off
  file (see *State and resumption*).
- **`REBASE` notices and the `dev`-moved rule.** `dev` moves while the cloud session runs, but the
  session does not rebase a pushed branch (see *Git on the assigned branch*). The gate rebases.
- **The green-`dev` grant rule (`tools/check_dev_ci.py`).** It gates grants of the lock, and there
  is no lock. The gate still runs it before the merge, as `GOV-017` requires.

## What stays, unchanged

These `GOV-017` and `AGENTS.md` rules protect the trunk or the review, not the shared checkout. They
bind a single session exactly as written.

1. **Never write to `dev`.** No commit, merge, rebase of `dev`, or push of `dev`. The owner's
   approval for a merge is given at the gate, after the branch is pushed (`AGENTS.md`,
   "Confidentiality and publishing"; `GOV-017`, "The merge gate").
2. **Never commit with `--no-verify`.** A failing pre-commit hook stops the session. It fixes the
   cause or reports the check and its message (owner ruling, 2026-09-23, recorded in `GOV-003`).
3. **One `pytest` run at a time in the checkout**, and `git diff --exit-code
   docs/08-governance/catalog.md` before every commit that is not meant to change the catalog. A
   commit that does change it regenerates it with `uv run python -m src.governance --catalog`
   (`GOV-017`, "The primary-checkout lock", last two items; `phase-grd-01`).
4. **Never write a confidential identifier into a tracked file**, and run
   `tools/check_no_private_content.py` with the changes staged (`AGENTS.md`).
5. **Allocate every document code with `--next-code`**, never by reading a directory (`GOV-005`).
   See *Code allocation from a clone* for the collision this leaves open.
6. **The five gate checks** run in the checkout before the hand-off, and their real output goes in
   the hand-off: `uv run python -m src.governance`, `uv run pytest`, `uv run ruff check src/ test/
   tools/`, `uv run mypy src/`, `cd ts && npm test`. The baseline is zero findings on each.
   `uv run python tools/check_diff_patterns.py origin/dev..HEAD` runs with them (`OPS-032`).
7. **The review brief contains nothing the builder wrote** beyond the diff, the requirement text and
   the commands (`GOV-017`, "Build reviews", "The brief"; `GOV-013`, "Verification discipline"). Not
   the session record, not commit messages, not the session's own account of what it did or why.
8. **Report as `GOV-006` requires**: name things then cite them, paste the output that carries
   information, ask only when the answer changes what gets built, capture new asks as ideas at once.

## Subagents

The session dispatches agents the way `GOV-013` describes a coordinator dispatching, scaled down.
`GOV-013`'s full apparatus (a tracker as memory, a dispatch template per unit, a descope ladder) is
for a run of many units. A session that dispatches two to six agents needs these rules and no more.

### Model tiers

**Proposed, from the owner's instruction of 2026-10-08, repeated from the previous cloud session:**

- **Haiku is the default for every subagent.** Research sweeps, inventories, file digests,
  mechanical checks and cited-fact extraction all run on Haiku.
- **Sonnet only where Haiku is clearly not fit**: design judgment, adversarial review, synthesis
  that has to weigh alternatives. The dispatch states in one line why Haiku was not fit.
- **Opus is not used.** The one exception is an extreme reason the session names to the owner
  before dispatching, and records in the hand-off.

This is stricter than `GOV-013`'s "Sonnet is the standard model for judgment work". The owner
stated it as the rule for this session and the one before; whether it is standing is Open question 1.

### Dispatch kinds

| Kind | Agent type | Model | Brief carries | Returns |
|---|---|---|---|---|
| Reconnaissance | `Explore` | Haiku | The files to read and the questions to answer; "cite file and line"; "write nothing" | Cited facts, bounded (a word cap in the brief) |
| Creator | `general-purpose` or a creator type from `.claude/agents/` | Haiku; Sonnet if the work is design | The unit's definition, the files it may touch, the verification commands | The paths written and the command output |
| Validator | `demo-validator-code`, `demo-validator-check` | Haiku for mechanical gates; Sonnet for a diff review | The diff, the requirement text, the commands. Never the creator's rationale | Pass or fail per check, with output |
| Adversary | `partition-adversary`, `demo-adversary` | Sonnet | The artefact, the governing documents, the fidelity checks. Nothing the writer wrote about it | Findings with severity |
| Resolver | `general-purpose` | Haiku | The blocker, the evidence, the governing text | What is actually true, and the options |

### Dispatch rules

- **Independent dispatches go out in one turn**, so they run in parallel and the session keeps
  working. A dispatch whose input is another's output waits for it.
- **The session does not duplicate an agent's work.** Once a sweep is dispatched the session reads
  its result, not the same files.
- **Every brief is the agent's whole input.** It names the goal, the files, what is already ruled
  out, the output shape and the cap. An agent that has to guess the task re-pays the reading bill.
- **Bound every return.** A word or line cap in the brief, and the detail in a file under the
  session's scratch directory when it exceeds the cap.
- **A truncated agent is resumed, never restarted** (`GOV-013`, "Context discipline"). An agent that
  stops with no file written is truncated, not finished.
- **The session runs verification itself and keeps the real output.** An agent's report that a
  command passed is a claim, not evidence (`GOV-013`, "Verification discipline").
- **Fix cycles are capped at two per unit.** What survives them is reported, not looped on
  (`GOV-013`, "Cost protocols").
- **A blocker goes to a resolver agent before it goes to the owner** (`GOV-013`). A question only
  the owner can answer goes to the owner at once, through `AskUserQuestion`, batched with any other
  question that is ready.

## Questions to the owner

- **Orient first, then ask once.** Read `AGENTS.md`, `GOV-006`, this document and the files the
  task names before asking anything. Then put every question whose answer changes what gets built
  in one `AskUserQuestion` call, recommendation first in each, as `GOV-013`'s "Questions at the
  open" requires and as the owner asked for on 2026-10-08.
- **State the tasks before the questions.** The owner's kickoff may carry several asks in one
  message. List them back, numbered, with the planned steps, so a dropped ask is visible before the
  work starts.
- **Drafts go in the message text, never in a question preview** (owner instruction in the cloud
  kickoff of 2026-09-28).
- **While the owner is away, state the assumption and continue** for anything that can wait.
  Surface every assumption in the hand-off, ranked by how much a different answer would change.

## Reviews in a single session

`GOV-017`'s assurance rule is that a build review is dispatched by the coordinator, never by the
session that built the phase (`REQ-030` R03). A single session is both. Two cases:

1. **The session dispatched creators and did not write the work itself.** It is the coordinator for
   that work, exactly as `GOV-017` says of a `PROMPT-036` run outside the protocol, and dispatches
   the review under the brief rule.
2. **The session wrote the work itself.** The 2026-09-28 cloud session did this and dispatched its
   own adversary with a brief that carried the artefact, the governing documents and the owner's
   rulings, and nothing the session had written about its reasoning, after committing and pushing
   the work (`handoff-planning-protocol.md`, section 4). The hand-off names the review as
   self-dispatched. The local Session Manager may re-run the review at the gate.

Whether case 2 satisfies `REQ-030` R03 or is a departure the owner must rule on is Open question 2.
Until the owner rules, the session follows case 2 and says in the hand-off that it did.

A review is dispatched **after** the work is committed and pushed, so a worker restart during the
review loses nothing, and so the reviewer reads the committed diff rather than a working tree.

## Git on the assigned branch

- **Develop on the assigned branch only.** Create it if the harness did not. Never switch the clone
  to `dev`.
- **Commit narrow and early, and push after each unit.** A push of the session's own branch needs no
  approval (`AGENTS.md`). An unpushed commit is lost when the container is reclaimed.
- **Do not rebase, reset or force-push a branch that has been pushed** (cloud kickoff of
  2026-09-28: "Never recreate, reset or force-push your branch"). If `dev` has moved, say so in the
  hand-off; the gate rebases the branch before the merge (`GOV-017`, "The merge gate", step 4).
  Before the first push, `git rebase origin/dev` is fine and preferred.
- **Fetch `origin/dev` before allocating a code or recording an idea**, so the allocation sees the
  latest trunk (see the next two sections).
- **No pull request** unless the owner asks for one. `dev` is the integration branch and the merge
  is the owner's call.

## Code allocation from a clone

`--next-code` reserves the code it hands out against every worktree **on the same machine**
(`GOV-005`). A cloud clone is a different machine. A code allocated in the cloud can collide with one
allocated locally the same day.

- Allocate as late as the work allows, after `git fetch origin` so `origin/dev`'s codes are seen.
- List every allocated code in the hand-off, with the command that allocated it, so the gate checks
  each is still free on current `dev` (the 2026-09-28 hand-off did this for `GOV-021`).
- A collision found at the gate is resolved as `AGENTS.md` says: the branch integrating second
  renumbers.

## Ideas

`GOV-006` requires that a new ask the owner names outside the current work is recorded as an idea at
once. Under `GOV-017` a single Ideation session is the only writer of `_data/ideas.jsonl`, so ids
never collide. A cloud session has no Ideation to send to.

**Proposed:** the session records ideas on its own branch through `tools/append_idea.py` (the only
sanctioned writer, `OPS-005`), one idea per distinct ask, after `git fetch origin`. The ids it
takes are the next sequential ids on its branch and can collide with ids recorded on `dev` while
the session runs. The hand-off lists every id recorded. `_data/ideas.jsonl` is append-only, so a
collision surfaces as a rebase conflict at the gate, and the gate re-records the colliding ideas
through the same writer on `dev` and notes the renumbering. Whether this is acceptable or whether
cloud sessions should instead hand ideas to the owner as text is Open question 3.

## State and resumption

- **State lives in files on the branch, not in the conversation.** Results an agent returns are
  written to a file before they are used. Decisions the owner makes are written into the deliverable
  or the hand-off as soon as they are made.
- **The hand-off file is tracked.** `_working/` is gitignored and would die with the container. The
  three cloud sessions wrote `docs/00-working/cloud-prompts/handoff-<slug>.md`, ungoverned under
  `ADR-010`, and that is the pattern: a Markdown file in `docs/00-working/`, named for the branch,
  committed and pushed with the final gate output.
- **A restarted worker re-reads the branch and the hand-off**, checks `git status` and `git log`,
  and continues. It does not redo work whose result is already committed.

## The hand-off

The hand-off replaces `READY`. It is a tracked file on the branch and the session's final report to
the owner. It carries, in this order:

1. The unclaimed statement, the branch and its tip, and whether `origin/dev` moved since the branch
   was cut.
2. What changed, file by file, with the commits.
3. Every code allocated with `--next-code`, and every idea id recorded.
4. The review: agent type, model, what the brief contained and what it did not, each finding with
   its disposition.
5. The gate output: the tail of each of the five checks and the diff-pattern check, pasted, not
   summarised. A failure is pasted as a failure.
6. Assumptions made while the owner was away, ranked by what a different answer would change.
7. Open questions for the owner, and anything left undone and why.
8. Spend posture: agents dispatched, with model and kind; any escalation above Haiku and its reason.

After the push, the owner or the local Session Manager runs `GOV-017`'s merge gate on the branch:
the review runner or the five checks in a detached worktree, the code check, the dirty-integration
check, the fast-forward and the push of `dev`. The cloud session's part ends at the push.

## Kickoff

The owner pastes this into a fresh cloud session, after the task text:

```text
Kickoff: you are running owner-directed, unclaimed work in a cloud clone of this repository under
GOV-022 (docs/08-governance/GOV-022-single-session-orchestration-protocol.md). Read AGENTS.md,
GOV-006 and GOV-022 first. Run `uv sync --extra dev` in the background while you orient. List the
tasks I gave you, numbered, with your planned steps; then ask every question whose answer changes
what gets built in one AskUserQuestion call, drafts in the message text and never in previews;
then work. Subagents run on Haiku unless you say in the dispatch why Haiku is not fit; Sonnet is
the ceiling; no Opus. Develop on the assigned branch, commit narrow, push often, never touch dev.
Finish with the hand-off file GOV-022 describes, committed and pushed with the gate output.
```

## Departures from AGENTS.md

Each of these is a reading of `AGENTS.md` that a cloud session cannot avoid, stated here so an agent
reading `AGENTS.md` mid-session does not conclude the session is misbehaving (`GOV-013`, "Name every
deviation"). None is an owner ruling yet; each is an open question below.

1. **The clone is the worktree.** `AGENTS.md` says every session works in a worktree under
   `../d-system-worktrees/<id>` and the primary checkout's branch is never switched. A cloud clone
   has no primary checkout to protect and no peer to isolate from; its single checkout is already
   the isolation the rule exists to provide. The three cloud sessions worked in the clone on their
   `agent/cloud-*` branches under the owner's kickoff. (Open question 4.)
2. **No claim commit.** `AGENTS.md`'s claim protocol needs a commit on `dev` in the primary checkout.
   Owner-directed work has nothing to claim, as `AGENTS.md` already says; a named phase would be
   claimed by the local side. (Open question 5.)
3. **Hand-off instead of in-session integration.** `AGENTS.md` steps 6 to 9 have the session rebase,
   ask the owner and fast-forward `dev` itself. A cloud session stops at the push, and the gate
   does the rest. This is `GOV-017`'s own departure 4 (relayed merge approval) applied to a session
   that is not present at the merge.

## Open questions

1. **Is the Haiku-default model rule standing?** The owner stated it in two consecutive cloud
   sessions. `GOV-013` says Sonnet is standard for judgment work. If standing, it needs a `GOV-003`
   entry and `GOV-013`'s "Cost protocols" should cite it; if one-time, *Model tiers* above becomes a
   description of what those two sessions did.
2. **Does a self-dispatched review satisfy `REQ-030` R03** when the session wrote the work itself
   and the brief carries nothing it wrote about the work, or must the gate always re-review such a
   branch?
3. **Idea recording from a clone**: record on the branch with possible id collision resolved at the
   gate, or hand ideas to the owner as text for Ideation to record?
4. **The clone as worktree**: confirm departure 1 as a standing ruling for cloud sessions, with a
   `GOV-003` entry, or require a worktree inside the clone.
5. **Named phases in a cloud session**: when the owner names a backlog phase at kickoff, who makes
   the claim commit on `dev`, and when?
6. **Status of this document.** It is `draft`. The owner decides whether it becomes `active`, and
   whether `GOV-017` and `PROMPT-037` should point to it for the single-session case.
