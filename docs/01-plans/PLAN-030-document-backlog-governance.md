---
schema_version: 1
id: doc-document-backlog-governance
code: PLAN-030
title: Document and backlog governance (P2)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-15'
systems: [sys-governance, sys-backlog]
depends_on: [doc-document-backlog-governance-requirements, doc-governance-protocol, doc-backlog-protocol]
---

# Document and backlog governance (P2)

## Summary

Programme `P2` of the twelve, fifth in the owner's delivery order. Seven ideas across four fine
groups. The contract governing what a governed document is and how the backlog carries it — a
different substrate from `P1`, which is the idea log, and from `P3`, which is agent safety mechanics
rather than document contract.

The governance check already verifies that the corpus is structurally sound. This programme adds the
things structure cannot see: whether a document is the right *kind*, whether it still describes
reality, whether the registries have room, and whether a phase went where it said it would.

| Group | Ideas | What it covers |
|---|---|---|
| `G05` Document contract | `000038`, `000056` | The requirement-vs-plan boundary, and document staleness and retirement |
| `G06` Backlog substrate | `000006`, `000011`, `000037` | Index widths, a reprioritisation recipe, and splitting `backlog.yaml` before it clogs agent context |
| `G07` Phase containment check | `000027` | Nothing diffs a completed phase's actual change set against its declared paths |
| `G08` `_tmpagent` registry | `000023` | A load-bearing mechanism missing from `systems.yaml`'s maturity registry |

Partition-time sizing at programme level was 4–5 phases. This plan lands **seven**, and the
discrepancy is with the partition's own arithmetic rather than with this plan — see
[Sizing](#sizing-against-the-partition).

## The chosen design

### 1. `000056` and `000047` do not merge, and the boundary is a dependency

This is the design question the phase's scope names, and `000056`'s own body leaves it open: whether
documentation governance overlaps `000047`'s plan-quality audit closely enough to merge. **Ruled:
they do not merge, and `000056`'s work consumes `000047`'s output rather than restating it.**

They fail differently. `000047` asks whether a document is *well written* — which sections earn their
place, what tone works. `000056` asks whether a document is *still true*. A beautifully structured
plan describing a system that was refactored last week passes every test `000047` could set and is
exactly what `000056` exists to catch. Merging them would produce one standard answering two
unrelated questions, and in practice the easier one would crowd out the harder.

There is a real shared surface, and `R05` is what keeps it from becoming duplication: the staleness
mechanism must consume the plan-quality standard for plans rather than define a second one.

**This creates a cross-programme dependency.** `000047` is no longer an unowned idea — `phase-prog-04`
sized it as `phase-idg-10` in `P1`. So `phase-dgov-02` depends on a phase in another programme. That
is recorded in its `depends_on` rather than left to a reader to notice, and it is the reason `P1`
should run before `P2` even though the queue orders them the other way.

### 2. Staleness is defined against what a document describes, never against its age

`R04` forbids the obvious implementation. A date-based rule is trivial to build and would flag
`ADR-003`, one of the oldest documents in the corpus and entirely current, while missing a document
written last week describing a route renamed since.

The signal has to be the relationship between a document and its subject: a named file that no longer
exists, a command whose flags changed, a system whose responsibilities moved in `systems.yaml`. That
is harder, and it is the only version worth building. `CLAUDE.md`'s own record of the no-remote rule —
correct when written, false the moment `phase-priv-05` pushed, stale in two files until someone went
looking — is the case this mechanism exists for.

### 3. The requirement rule is applied to the corpus before it is enforced

`R01` writes the rule, `R02` classifies the existing corpus against it, and `R03` enforces it on new
plans only. The ordering is deliberate and the sequence matters: enforcing first would turn `dev` red
on 14-plus existing plans that predate the rule, which is a way of discovering that the rule is too
strict by breaking the trunk.

Grandfathering is recorded as a list rather than a blanket exemption, so the backlog of unpaired
plans is visible and finite rather than forgotten.

### 4. The backlog split is measured, not just performed

`000037` proposes moving completed and cancelled phases to `backlog-archive.yaml`. `R08` is the safety
half — ids and evidence byte-identical, `GOV-002`'s preservation rule satisfied, because this is a
location change and not a deletion. `R09` is the point: the working file must get materially smaller,
stated as a measurement.

Both are needed because the failure mode is a split that satisfies the letter of `GOV-002` and leaves
the working file the same size, having moved the problem rather than solved it.

### 5. The containment check reports and never blocks

`000027` wants a phase's actual diff compared against its declared paths. **Ruled: it reports, and a
person judges.** `R13` requires the output to distinguish a declaration that was too narrow from work
that genuinely strayed — and only a person can tell those apart, because the first is a paperwork
defect and the second is a protocol violation.

The check also must not write to `backlog.yaml` or reopen a completed phase. A check that
automatically reopens phases on a heuristic would, on this corpus, reopen every `phase-prog-*` phase
immediately.

**`R12` predicts its own first result**, which is unusual in a requirement and deliberate here. The
containment rule has only ever been enforced by agents choosing to follow it, and one violation class
is already known: every `phase-prog-*` phase rewrites `backlog.yaml` without declaring it, including
the three that produced this plan. A first run reporting zero findings across 70-plus completed
phases would contradict evidence already in hand, and should be read as a broken check rather than a
clean corpus.

### 6. `G07` is sequenced behind `phase-gov-01`, which the scope required checking

The phase's acceptance requires stating the overlap with `phase-gov-01`, a ready phase queued outside
this programme. **Checked: the functions are distinct, the files are not.**

`phase-gov-01` rejects a backlog *deliverable whose filename carries an unreserved code* — a pre-hoc
check on declarations, before work starts. `G07`'s check diffs a *completed phase's actual change set*
against those declarations — post-hoc, on what happened. Neither subsumes the other.

But both declare `src/governance/backlog.py` and `test/test_backlog.py`, so they collide and cannot
run concurrently. `phase-dgov-06` therefore declares `depends_on: [phase-gov-01]`. They were not
merged: `phase-gov-01` belongs to `PLAN-010` and is already queued and ready, and pulling a ready
phase out of another plan into this programme to avoid a sequencing edge trades a small ordering
constraint for a governance tangle.

### 7. `G08` gets its own phase, and it is honestly under-sized

`000023` is one entry in `systems.yaml` plus a justified maturity level. The partition calls it
trivial and it is. It gets `phase-dgov-07` anyway rather than being folded into a neighbour, because
the candidates for folding — the index audit, the containment check — are unrelated work, and
bundling unrelated trivia produces a phase that cannot be reviewed as a unit.

Stated plainly so nobody sizes a session around it: **this is well under one session, and whoever
claims an adjacent governance phase should take it in the same sitting.** Its `next_action` says so.

### Which of these need a decision record

**None of the seven.** Each is recorded where the reader meets it: decisions 1 and 5 in `REQ-015`'s
rows and in the phases' scopes, 2 and 3 in the mechanism each phase builds, 4 in `R08`/`R09`, 6 in the
`depends_on` edge itself, 7 in `phase-dgov-07`'s `next_action`. No decision here chooses between two
architectures with a live alternative, which is the case an ADR exists to preserve — contrast
`P1`'s scope fork, which does and gets one.

## Implementation phases

Seven phases under `phase-dgov-*`, registered in [the backlog index](../09-backlog/README.md).

| Phase | Title | Group | Depends on |
|---|---|---|---|
| `phase-dgov-01` | Rule when a requirement is mandatory, classify the corpus, enforce forward | `G05` | — |
| `phase-dgov-02` | Define document staleness and the retirement path | `G05` | `phase-idg-10` |
| `phase-dgov-03` | Audit every index width against a stated horizon and widen what is short | `G06` | — |
| `phase-dgov-04` | Split completed phases into a backlog archive, and measure the saving | `G06` | — |
| `phase-dgov-05` | Write the backlog review and re-prioritisation procedure | `G06` | — |
| `phase-dgov-06` | Diff a completed phase's change set against its declared paths | `G07` | `phase-gov-01` |
| `phase-dgov-07` | Register `_tmpagent` in the systems maturity registry | `G08` | — |

### Sizing against the partition

The partition states `P2` at **4–5 phases** at programme level, and then states its groups at 2, 1
each × 3, `<1`, and trivial — which sums to **5–6 phases plus two fragments**. The programme-level
figure contradicts its own group table, and this plan follows the group table, landing at seven.

The one genuine departure from the group table is `G05`, sized at 2 and delivered at 2, but with
`000038` carrying three separable obligations (write the rule, classify the corpus, enforce forward)
that are kept in one phase because a rule that has not been applied to the corpus is untested, and
enforcement without the grandfather list breaks the trunk. The three are one piece of work.

## Execution order and real concurrency

All seven declare `sys-governance` and five declare `sys-backlog`, so the programme's internal ceiling
is **one agent at a time**. As with `P3`, this is not a defect to engineer around: the subject matter
*is* the governance corpus, and the corpus is one surface.

**Three phases contend on `src/governance/` and `test/test_backlog.py`, not two.** Decision 6 audits
the `phase-dgov-06`/`phase-gov-01` pair because their deliverables are identical, but
`phase-dgov-04`'s `src/governance/` and `test/test_backlog.py` collide with both — `src/governance/`
is a prefix of `src/governance/backlog.py`, and the repository's own `path_conflict()` returns true
for that pair. Measured, not inferred.

No `depends_on` edge is added for it. The edge on `phase-dgov-06` exists because that phase is
*functionally* sequenced behind `phase-gov-01` — it extends the same check — whereas `phase-dgov-04`
merely touches the same files and has no ordering requirement against either. The collision is
therefore real but inert: the programme is already serialised by `sys-governance`, and
`concurrency_errors` rejects a bad concurrent claim regardless of whether this plan predicted it.
Recorded here because decision 6 established the methodology of auditing file-level collisions and
stating them, and applying that to one pair and not the other would leave the next reader assuming
`phase-dgov-04` is safe to run beside `phase-gov-01`.

Two dependencies reach outside the programme, which matters more than the internal ordering:

- `phase-dgov-02` waits on `phase-idg-10` in `P1`. **`P1` should therefore run before `P2`**, even
  though the queue orders `phase-prog-05` ahead of much of `P1`'s work.
- `phase-dgov-06` waits on `phase-gov-01` in `PLAN-010`, which is ready now and blocked by nothing.

`phase-gov-01` is the cheapest unblocking move in the whole programme: it is ready, it is small, and
it releases the containment check. A coordinator should take it before opening `P2`.

## Requirement coverage

Every row of `REQ-015` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 A rule for when a requirement is mandatory | `phase-dgov-01` |
| R02 The corpus classified against the rule | `phase-dgov-01` |
| R03 Governance rejects a new unpaired plan | `phase-dgov-01` |
| R04 Staleness and retirement defined against subject, not age | `phase-dgov-02` |
| R05 The boundary against plan quality, stated | `phase-dgov-02` |
| R06 Every index audited against a horizon | `phase-dgov-03` |
| R07 Narrow indexes widened without renumbering | `phase-dgov-03` |
| R08 Completed phases moved, evidence preserved exactly | `phase-dgov-04` |
| R09 The working file measurably smaller | `phase-dgov-04` |
| R10 A review and re-prioritisation procedure | `phase-dgov-05` |
| R11 The procedure is reachable as what it claims to be | `phase-dgov-05` |
| R12 Actual change sets diffed against declarations | `phase-dgov-06` |
| R13 The check reports and never blocks | `phase-dgov-06` |
| R14 `_tmpagent` in the maturity registry | `phase-dgov-07` |

## Key references

- **The requirement** — [REQ-015](../06-requirements/REQ-015-document-backlog-governance.md).
- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P2`.
- **The governance protocol** ([GOV-001](../08-governance/GOV-001-protocol.md)) and **document codes** ([GOV-005](../08-governance/GOV-005-document-codes.md)) — the contract `G05` sharpens, and the rule that forbids renumbering.
- **The backlog protocol** ([GOV-002](../08-governance/GOV-002-backlog-protocol.md)) and **accepted decisions** ([GOV-003](../08-governance/GOV-003-backlog-decisions.md)) — the substrate `G06` scales, including the preservation rule `R08` must satisfy.
- **The `_tmpagent` contract** ([`_tmpagent/AGENTS.md`](../../_tmpagent/AGENTS.md)) and [PLAN-015](PLAN-015-ephemeral-working-plans.md) — what `G08` registers.
- **Idea graph and lifecycle** ([PLAN-029](PLAN-029-idea-graph-lifecycle.md)) — `phase-idg-10` is the standard `phase-dgov-02` consumes.

## Known facts not to rediscover

- **`G05` was kept out of `P1`'s `G04` deliberately**, and decision 1 above settles the overlap
  `000056` left open rather than carrying it forward again.
- **`G07` is the nearest existing mechanism to hang `000204` on** — the systemic finding that resolved
  work leaves its idea open. `000204` is not a member of this programme, and `phase-dgov-06` does not
  close it; the connection is that a containment check is the kind of post-hoc sweep that could later
  carry an idea-status check beside it.
- **`G08` is near-mechanical** and is under-sized for a session by design. Batch it.
- **`G06`'s three members are independently shippable** and were grouped for readability, not
  dependency. They are three phases with no edges between them.
- **`phase-gov-01` overlaps `G07` on files, not on function**, and the ruling is decision 6. Check it
  before writing anything in `src/governance/backlog.py`.
- **The index audit's asymmetry is the reason to do it early.** Widening a pattern is cheap;
  renumbering an issued code is forbidden by `GOV-005`. Being wrong in one direction costs nothing
  and in the other costs a migration that cannot legally be performed.
