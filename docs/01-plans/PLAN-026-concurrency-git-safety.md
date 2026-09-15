---
schema_version: 1
id: doc-concurrency-git-safety
code: PLAN-026
title: Concurrency, git safety and enforcement (P3)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-15'
systems: [sys-governance, sys-backlog, sys-delivery]
depends_on: [doc-concurrency-git-safety-requirements, doc-adr-multi-agent-concurrency]
---

# Concurrency, git safety and enforcement (P3)

## Summary

Programme `P3` of the twelve, first in the owner's delivery order. Ten ideas across five fine groups,
from the accepted partition of 2026-09-13. Every member hardens how concurrent agents share one
repository without destroying each other's work.

`ADR-003` already decided the model — `backlog.yaml` on `dev` as the lock table, the governance check
as the lock check, one worktree per agent. This programme does not revise that model. It makes the
model fail safely, because every rule that currently protects a peer's work is a sentence an agent
has to remember, and the four recorded failures in [REQ-013](../06-requirements/REQ-013-concurrency-git-safety.md)
are all cases of an agent not remembering one.

| Group | Ideas | What it covers |
|---|---|---|
| `G09` Claim and clobber hardening | `000025`, `000041` | An abandoned claim with no recovery path, and a `git stash` that destroyed a peer's uncommitted work |
| `G10` Branch protection and PR gate | `000066` | Branch topology, GitHub settings, CI-as-gate, and the multi-agent pull-request protocol |
| `G11` Version control and backup | `000021`, `000058`, `000059` | `000058` is the umbrella, `000059` its git slice, `000021` the concrete gap for gitignored `_private/` |
| `G12` Harness enforcement | `000012`, `000014`, `000051` | Where enforcement belongs — hooks, settings, tests or prose |
| `G13` `AGENTS.md` push-rule rewrite | `000091` | Two hunks in one file, replacement text already approved and recorded twice |

Partition-time sizing was 6–8 phases. This plan lands **nine**, and the delta is explained under
[Sizing against the partition](#sizing-against-the-partition).

## The chosen design

Five decisions. Each settles a question the partition left open, and each is stated as a choice with
its cost rather than as the only option.

### 1. Staleness is reported; release stays a human act

`000025` leaves open whether an abandoned claim should be released by a check or by the owner. **It is
reported by a check and released by a human.**

A claim is a statement that work is in progress. The evidence a check can gather — a branch with no
recent commit, a worktree directory that is gone — is evidence about the *artifacts*, never about the
agent. An agent thinking for forty minutes and an agent that died an hour ago produce identical
signals, and the cost of the two errors is not symmetric: a false "still live" wastes a peer's time,
while a false "abandoned" hands a second agent a phase someone is actively writing, which is the
`000041` incident with extra steps.

So `--ready` grows a stale-claim column and names the signal that fired; the report is an input to a
decision, not the decision. The recovery procedure is written, authorised, and performed by a person.
`R03` makes the absence of an automatic path an asserted property rather than a convention: a grep
finding code that writes `status: queued` over a peer's claim is a defect.

The cost accepted: a dead claim blocks its systems until someone looks at the report. That is the
right cost while `max_active` is 3 and the owner reads the queue daily. It stops being right if this
repository ever runs unattended agents at volume, and `R02` therefore requires the definition to say
what staleness does not prove, so the next reader does not mistake the signal for a verdict.

### 2. The guard sits at integration, not at `git stash`

`000041` asks whether the fix for the clobbering incident is procedural or mechanical. **Mechanical,
and placed at the integration step rather than on the destructive command.**

The instinct is to forbid `git stash`. That fails twice. Git has no stash hook, so the rule would be
unenforceable prose — exactly what this programme exists to replace. And the rule would be wrong:
stashing your own work in your own worktree is ordinary and safe. What is never safe is *landing work
on the trunk across someone else's uncommitted changes*, and that is a single, hookable moment.

So the guard refuses the integration while the primary checkout is dirty, and names the dirty paths.
`R04` adds that the refusal must not be satisfiable by stashing — otherwise the guard teaches the
precise behaviour that caused the incident.

This has already been exercised: on 2026-09-15 a session found three of a peer's files uncommitted in
the primary checkout, waited for the peer to commit, and claimed afterwards. That was a person-shaped
decision made from `AGENTS.md` prose. `phase-conc-02` is what makes it a mechanism.

### 3. Only `dev`-to-`main` is gated; `agent/*` keeps integrating directly

`000066` asks whether each agent opens a pull request from `agent/<phase-id>` into `dev`, or whether
agents integrate onto `dev` and only `dev`-to-`main` is gated. **The latter.**

The claim model in `ADR-003` assumes merges are synchronous: an agent claims, works, integrates, and
releases, and the lock is held for exactly that span. A pull request per agent branch breaks the
assumption — the request sits open across sessions, the claim has to stay open behind it or the lock
table lies, and `max_active` becomes a throttle on review latency rather than on concurrent work.
That is a worse problem than the one the gate solves, and it is `000025`'s abandoned-claim failure
made routine rather than exceptional.

`main` is the published surface and the place the confidentiality history actually bites, so that is
where the gate earns its cost. `R08` makes `tools/check_no_private_content.py` a required check on
it — a pull request is exactly where a file that was untracked until now becomes visible, which is
the sweep session's finding.

The cost accepted: work reaches `dev` without review. That is already true today, and the gate does
not claim to change it.

### 4. The backup posture is decided, and a decision to accept the risk counts

`000021`, `000058` and `000059` between them ask what "version controlled" should mean for state git
cannot hold. **The programme's obligation is a recorded posture, not a particular mechanism.**

`_private/portfolio/` is permanently gitignored by `ADR-009`, deliberately, so no remote will ever
cover it. The honest options are an encrypted off-machine copy, a second local disk, or writing down
that the risk is accepted and what is lost with the disk. `R11` treats all three as satisfying;
what it refuses is the current state, which is that the question is open and nobody has chosen.

`R12` is the row that stops this becoming theatre: if a mechanism is chosen, it is verified by
restoring from it and diffing, never by confirming the backup command exited zero. Untested backups
are the standard way this class of work fails.

`000059`'s git-tooling slice is absorbed into `G09`'s and `G10`'s phases rather than given its own.
Its content — worktree conventions, commit hygiene, hooks, the concurrent-agent git-safety concerns —
is either already written in `AGENTS.md` or is the subject of another group here. A separate phase
would restate them.

### 5. The enforcement question is answered once, as a rule, then applied

`000051` was created to parent `000012` and `000014`, and all three ask where enforcement belongs.
**The deliverable is a placement rule with stated inputs, applied to the rules already in force.**

Answering the three ideas case by case would produce three defensible placements and no way to place
the fourth rule. The rule is the reusable artifact; the placements are its test. `R13` therefore
requires it to be applied to at least the governance check, catalog staleness, the private-content
gate and `_private/` reads — rules that exist today — rather than stated in the abstract.

`R15` carries the tension `000014` names and `PLAN-008` records: hooks live in `.claude/`, and
`AGENTS.md` is written for any agent. The resolution is not to refuse harness-specific enforcement —
that would forfeit the only mechanism available at the moment of action — but to state the non-Claude
equivalent for each hook, so the gap is a known quantity rather than a surprise.

`000012` (skip the test preflight when the tree is provably clean) is **recorded as unblocked but not
sized for implementation.** Its own body gates it on a remote with CI, which now exists; but its value
is a function of suite runtime, and the suite runs 580 tests in about a minute. It gets a stated
disposition in the placement rule's phase and no implementation phase of its own. Building a
provenance check to save sixty seconds is work the programme cannot justify today.

### Which of these need a decision record

The phase's scope requires ruling on this rather than leaving it to be inferred. **Two of the five
decisions need a governed decision record; three do not, and neither ruling creates a new document in
this phase.**

- **Decision 3 (branch topology) amends `ADR-003` rather than superseding it.** `ADR-003` decided
  worktree-isolated agents over a disjoint backlog, and its claim model is what decision 3 reasons
  from. Adding a gate on `dev`-to-`main` does not overturn that model; it bounds where the trunk
  ends. `phase-conc-06` declares `ADR-003` among its deliverables and carries the amendment. A new
  ADR would leave two live documents describing one branch model, which is `R10`'s defect.
- **Decision 4 (the backup posture) needs a new ADR**, because there is no existing decision record
  about durability of non-git state, and `ADR-009` addresses only where the portfolio lives.
  `phase-conc-07` declares `docs/04-decisions/` for exactly this.
- **Decisions 1, 2 and 5 need none.** Each is a design choice whose reasoning belongs with the
  mechanism it governs, and each has a phase that records it where a reader will meet it:
  `phase-conc-04` writes the recovery decision into `GOV-003` alongside the incidents that motivated
  it, `phase-conc-02` records the guard's placement in `OPS-001`, and `phase-conc-08`'s placement
  rule is itself the record. Minting an ADR for a choice already written into the governing document
  adds a second place for it to drift.

### The `G13` exception: one phase no agent may execute

`000091`'s replacement text for `AGENTS.md` is already approved and recorded verbatim on the idea. The
change is two hunks in one file. It is nonetheless **owner-executed**, for two independent reasons:
`.claude/settings.json` hard-denies `Edit(AGENTS.md)` and `Write(AGENTS.md)`, and deny rules override
approvals at the tool level; and `AGENTS.md`'s own standing rule forbids any agent editing it under
any circumstance, which the settings deny merely enforces.

`phase-conc-09` therefore names the owner as the executor in its scope, and its acceptance is written
so that an agent can verify the result without being able to produce it. It is listed last not because
it is least valuable — it lands at the moment an agent finishes a phase and has to decide what to do
with its branch — but because nothing else in the programme waits on it.

## Implementation phases

Nine phases under `phase-conc-*`, registered in [the backlog index](../09-backlog/README.md).

| Phase | Title | Group | Depends on |
|---|---|---|---|
| `phase-conc-01` | Define the stale-claim signal and report it in `--ready` | `G09` | — |
| `phase-conc-02` | Refuse integration over a dirty primary checkout | `G09` | — |
| `phase-conc-03` | Make document-code allocation collision-proof across concurrent sessions | `G09` | — |
| `phase-conc-04` | Write the claim-recovery procedure and record it in `GOV-003` | `G09` | `01` |
| `phase-conc-05` | Decide and apply branch protection on `main`, with the settings record | `G10` | — |
| `phase-conc-06` | Rewrite the multi-agent protocol for the pull-request gate and reconcile the corpus | `G10` | `05` |
| `phase-conc-07` | Decide the backup posture for non-git state and verify it by restoring | `G11` | — |
| `phase-conc-08` | Write the enforcement-placement rule, apply it, and audit `.claude/` settings | `G12` | — |
| `phase-conc-09` | Owner-executed: apply the approved `AGENTS.md` push-rule rewrite | `G13` | `06` |

### Why `phase-conc-03` sits in `G09`

The session-code collision is the second half of the `000041` incident and is usually read as
incidental to it. It is not: both halves are the same failure, which is that a shared resource is
allocated by inspecting state that has not merged yet. `--next-code` reads committed state, so two
worktrees allocating before either merges get the same number. `AGENTS.md` already documents the
workaround — reserve the code in `codes.yaml` alongside the backlog claim — which is a convention
protecting against a mechanism defect, and therefore the thing this programme converts.

### Sizing against the partition

Partition-time sizing for `P3` was **6–8 phases** against 10 ideas. This plan lands **nine**, and the
delta is two stated choices rather than scope growth.

- `G09` was sized at 1–2 and is **four** here. The group carries three mechanically distinct
  deliverables — a report column, an integration guard, an allocator change — plus the written
  procedure that the first of them feeds. Each is a different file and a different failure mode;
  bundling them would produce one phase that cannot be reviewed as a unit.
- `G11` was sized at 2–3 and is **one**, because decision 4 rules `000059` into the `G09`/`G10`
  phases rather than giving it its own, and because `R11` permits a recorded acceptance of the risk
  as a complete answer. If the owner chooses a mechanism rather than accepting the risk, this phase
  splits and the plan is amended to say so.

`G10` lands at two against a 3–4 range, `G12` at one against two, and `G13` at one against its
sub-phase estimate. `G10` and `G12` are each smaller than estimated for the same reason: the partition
sized them before the stale blockers were struck down, when each carried an investigation phase that
the correction removed.

## Execution order and real concurrency

Measured by declared systems and deliverable paths, not read off the dependency graph.

Every phase here declares `sys-governance`, and seven of the nine name a file under
`docs/08-governance/`. A shared system is a collision, so **the realistic ceiling for this programme
is one agent at a time**, with two exceptions: `phase-conc-03` (which lands in `src/governance/` and
`docs/08-governance/GOV-005-document-codes.md`) and `phase-conc-07` (which lands in a new decision
record) can each run beside a peer in another programme, though not beside each other if `GOV-003` is
the venue for both records.

This is not a defect to engineer around. `P3`'s subject matter is the governance corpus itself, and
the corpus is one surface. A coordinator should run this programme serially and spend its concurrency
budget on `P6`, `P8` or `P9`, which touch disjoint systems.

The critical path is three deep: `phase-conc-05` → `phase-conc-06` → `phase-conc-09`.

## Requirement coverage

Every row of `REQ-013` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 Stale claims reported as a distinct state | `phase-conc-01` |
| R02 Staleness defined evaluably, and its limits stated | `phase-conc-01` |
| R03 Release is authorised and never automatic | `phase-conc-01`, `phase-conc-04` |
| R04 Integration refused over a dirty primary checkout | `phase-conc-02` |
| R05 Document codes cannot be allocated twice concurrently | `phase-conc-03` |
| R06 `main` rejects direct pushes; a failing check blocks merge | `phase-conc-05` |
| R07 Every branch-protection setting carries a judgement | `phase-conc-05` |
| R08 The private-content check is required, and reports a real count | `phase-conc-05` |
| R09 The protocol states what a claim means under the gate | `phase-conc-06` |
| R10 No document describes a branch model not in force | `phase-conc-06` |
| R11 The backup posture is recorded, with what it does not cover | `phase-conc-07` |
| R12 A chosen mechanism is verified by restoring | `phase-conc-07` |
| R13 An enforcement-placement rule exists and is applied | `phase-conc-08` |
| R14 `.claude/` settings audited permission by permission | `phase-conc-08` |
| R15 Harness-specific enforcement states its non-Claude equivalent | `phase-conc-08` |
| R16 The `AGENTS.md` push rule reads as rule-plus-exception | `phase-conc-09` |

## Key references

- **The requirement** — [REQ-013](../06-requirements/REQ-013-concurrency-git-safety.md).
- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P3`, for the six-field record and the independence argument against `P4`.
- **The handoff** — [`docs/00-working/handoff-idea-partition-and-triage.md`](../00-working/handoff-idea-partition-and-triage.md), which names convention-without-enforcement as one of the two families dominating the backlog and identifies it as this programme.
- **Multi-agent concurrency** ([ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md)) — the accepted claim-and-lock model this programme hardens rather than revises.
- **Accepted backlog decisions** ([GOV-003](../08-governance/GOV-003-backlog-decisions.md)) — carries the incidents that withdrew the documentation-only worktree exception on 2026-09-12, and is the venue for `phase-conc-04`'s recovery procedure.
- **`AGENTS.md`** — the three *Concurrent agents* sections are the rule this programme enforces mechanically rather than in prose.

## Known facts not to rediscover

- **`G10` is no longer blocked.** The repository being public was the named workaround for the 403
  that stalled it; two analysts carried the stale blocker forward.
- **`G12`'s "blocked pending remote/CI" note is stale.** Both now exist.
- **`G13` is blocked by the owner's own tooling**, not by design: `.claude/settings.json` denies
  `Edit(AGENTS.md)`. It needs the owner to apply the approved text by hand or lift the rule. No
  agent may edit `AGENTS.md` regardless — see that file's own standing rule. The exact replacement
  text for both hunks is recorded verbatim in a finding annotation on `000091`, deliberately, so it
  survives independently of the plan file at `~/.claude/plans/`, which is outside the repository and
  outside backup.
- **`G09` should land after `G10`'s document rewrite**, because both touch the same `AGENTS.md`
  passages. This plan does not follow that ordering, and the reason is stated: `phase-conc-01`
  through `-03` are code and report changes that touch no `AGENTS.md` prose, so only
  `phase-conc-04`'s written procedure is affected, and it depends on `phase-conc-01` rather than on
  `G10`. The partition's precedence note was written before the group was split into mechanism and
  procedure.
- **`000027` (phase containment) sits in `P2`, not here**, and is the nearest existing mechanism to
  hang `000204` on.
- **The private-content check runs weaker in a worktree** — `0 identifiers checked` against `31` in
  the primary checkout, because `_private/portfolio/` is absent there. `R08` asserts this as a
  standing check rather than leaving it as folklore.
