# Role contracts

The contracts for the roles that take an idea through triage, planning, review, building,
validation and realization. Each role has one contract: what it receives, what it produces, and
what it never does. The never-do list is the binding half.

- Capturing an idea is the owner's work, done in conversation through the `idea` skill. It is not
  an agent role and has no contract.
- Where a role has an agent definition, the contract is the authority and the definition is
  changed to match it.

## 1. Owner-reserved decisions

No contract grants an agent an owner-reserved decision. The reserved decisions are:

- idea approval and `lineage` annotations;
- partition acceptance;
- plan approval (the plan-approval gate);
- ranking `next_up` and all cross-track priority (`backlog-protocol.md`, section 4);
- integration onto the integration branch (`protocol.md`, section 12);
- edits to the agent instruction files (`protocol.md`, section 3);
- anything in the confidential directory (`protocol.md`, section 10).

Phase completion is not a role's decision: it follows the three completion conditions of
`backlog-protocol.md` section 10.

Every "proposes" in a contract names a proposal waiting for the owner's gate, never the decision
itself. A role never describes its own output as accepted, approved or ratified.

An agent may write the following, always leaving an audit trail: finding annotations and the status
moves the idea writer permits it; draft documents; `depends_on` and `systems` on phases within an
approved plan; commits on its own branch.

## 2. The evidence rule

A validator's verdict rests on tests and repository checks it ran in the worktree, with their real
output captured. It never rests on asserted confidence or on what the code "should" do. A claim
with no command behind it is not evidence. Every agent in the pipeline is the same underlying
model, so a validator that judges by impression shares the developer's blind spots.

## 3. Roles

### Triage

Carried by the `idea-triage` skill and its agent (`agents/idea-triage.md`).

- **Receives:** one open idea's id, title and body, read through the idea writer's `show`; the
  configured search list; the literal read and write commands.
- **Produces:** one finding annotation naming related plans, phases, documents and overlapping
  ideas, and asserting no decision about them. The dispatching skill moves the idea from open to
  triaged only after it has verified the finding.
- **Never:** concludes decline or merge; writes a link, only a `PROPOSED LINK:` line; promotes,
  only a `PROPOSED PROMOTION:` line; runs a writer command other than `annotate`; invents a
  relationship it has not verified by reading the target.

### Partition

Carried by the `partition-ideas` skill, its partition pack (`partition-pack.md`) and its analyst
and adversary agents.

- **Receives:** ideas at `triaged`, the partition pack and its corpus, and the request that starts
  the sweep.
- **Produces:** a proposed partition record of tracks and their member ideas. Each track's
  new-plan-or-amendment ruling is the owner's, recorded when the owner makes it. The record stays a
  proposal until the owner accepts it at the partition-acceptance gate.
- **Never:** accepts its own partition; treats agreement between proposal and adversary as the
  owner's acceptance; proceeds past a gate without the owner's answer.

### Planner

Any session that writes a plan. Supported by `protocol.md` section 4, the plan and requirement
templates, and the `plan-check` and `next-code` skills.

- **Receives:** an accepted track or the owner's request; triage's findings and links for the
  member ideas, so the draft does not duplicate coverage triage already established; the plan
  quality standard (`plan-review.md`).
- **Produces:** a requirement and plan pair that meets the plan quality standard, with phases
  decomposed to one outcome and one session when drafted.
- **Never:** approves the plan; moves an idea to `promoted`; leaves a phase table undecomposed for
  a later stage to split.

### Adversary

Runs the review in `plan-review.md` with the dispatch prompt in `adversary-prompt.md`.

- **Receives:** a requirement and plan pair, and the review procedure.
- **Produces:** findings in its reply. Every finding reaches the review record and receives a
  disposition, including `accepted-no-change`. None is silently dropped.
- **Never:** approves the plan; authors the fix beyond naming the smallest change; skips the
  later-added altitude because the first two came back clean; writes a disposition.

### Phase-fit

Splits phases that do not fit one session (`backlog-protocol.md`, section 14).

- **Receives:** the plan and its dispositioned review record; the phase-splitting rule. Splitting a
  phase is a different act on a different object from decomposing an idea.
- **Produces:** the final phase set, each phase within one session. A split phase goes back to
  review at the phase altitude before mapping.
- **Never:** decomposes an idea; skips re-review after a split.

### Mapper

Validated by the check (`check.py`).

- **Receives:** the final phase set.
- **Produces:** phases carrying `depends_on` and `systems` that pass the check, and a proposed
  `next_up` order that stays a proposal until the owner ratifies, amends or rejects it at the
  plan-approval gate.
- **Never:** ranks `next_up` or sets cross-track priority; registers a phase the check rejects
  without revising first; proceeds after a second rejection without escalating to the owner with
  the check output attached.

### Developer

Carried by the `session-start`, `checkpoint` and `session-close` skills.

- **Receives:** one claimed phase, in its own worktree.
- **Produces:** a branch whose diff meets the phase's acceptance, ready for independent review.
- **Never:** integrates its own branch; completes a phase on its own judgement; writes a
  confidential identifier into a tracked file; edits the agent instruction files; touches the
  confidential directory.

### Validator

The independent review in the `session-close` skill, and any validator a repository adds.

- **Receives:** the requirement or the phase's acceptance, and the diff.
- **Produces:** a pass or fail verdict under the evidence rule, with findings and the verbatim
  output of every verification command it ran.
- **Never:** accepts the developer's rationale as evidence; edits the diff or fixes a finding;
  marks a phase complete; merges; substitutes "this looks correct" for a check it ran.

### Realization

Any agent that checks a delivered capability against the idea that asked for it, through the idea
writer.

- **Receives:** an integrated branch, its verification output, the completed phase, and the
  originating idea's text, read through the writer's `show`.
- **Produces:** evidence as finding annotations, and a proposal, carrying the evidence, that the
  idea close as `delivered` with its `closes_with` pointer (`vocabulary.md`, Statuses). The owner
  ratifies proposals in batch.
- **Never:** writes the terminal status itself; closes an idea silently when the capability cannot
  be verified against the idea's text; it records a finding the owner sees instead.
