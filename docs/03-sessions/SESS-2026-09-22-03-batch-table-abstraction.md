---
schema_version: 1
id: doc-session-2026-09-22-batch-tables
code: SESS-2026-09-22-03
title: Abstract the batch table out of the build coordinator and register the orchestration protocol
kind: session
status: active
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-backlog, sys-governance]
depends_on: [doc-build-coordinator, doc-batch-orchestration-protocol, doc-coordinator-protocol]
---

# Batch table abstraction

**Unclaimed, owner-directed session.** No backlog phase was claimed, so peers held no lock against
this work. Branch `agent/batch-tables`, worktree `../d-system-worktrees/batch-tables`.

## What was asked

The owner asked whether a reusable prompt existed for reviewing the open backlog and planning a
batch for parallel or serial execution. One did —
[PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md), the build coordinator — but its batch
table was hard-coded, and had gone stale: batch 1 was built, and two phases
(`phase-gov-05`, `phase-conc-02`) had since been ranked to the head of `next_up` ahead of batch 2.

Rather than run the stale pack, the owner directed that the batch table be abstracted out behind a
schema capturing order, dependencies and what may run in parallel; that the original table be moved
into that form; that the next batch be composed as a new table; and that the coordinator discover
and select a table rather than be told one. Mid-session they added that the mechanism be registered
as a protocol once it landed.

## What was delivered

- **`schemas/batch.schema.json`** — the batch table contract. Grouping, sequencing and parallelism
  only; no phase facts beyond a convenience `title`.
- **Six tables under `docs/09-backlog/batches/`**, with a README. `batch-001` is `complete` (the
  built batch, with a retrospective stage decomposition); `batch-002` is the new seven-phase batch;
  `batch-003`–`006` carry `PROMPT-036`'s original batches 3–6 unchanged in membership.
- **`PROMPT-036` revised** — the hard-coded table replaced by discovery, a deterministic selection
  rule with stated ambiguity cases, stage semantics, and the table's `status` lifecycle. The unit
  run, dispatch templates, hygiene and cost protocols are unchanged.
- **[GOV-016](../08-governance/GOV-016-batch-orchestration-protocol.md)** — the batch orchestration
  protocol. `GOV-013` and `PROMPT-036` gained prose pointers to it.
- **Two ideas captured**: `000316` (the governance check that would validate these tables) and
  `000317` (this protocol, promoted to `GOV-016` in the same session).

## Verification

Preflight on `dev` before starting, both green:
`Governance OK: 35 systems, 308 documents, 29 memories, 293 backlog phases` and `688 passed`.

In the worktree after the work:
`Governance OK: 35 systems, 309 documents, 29 memories, 293 backlog phases` and `688 passed`.

The six compositions were verified by script against `backlog.yaml`: every phase id resolves, every
phase in an unbuilt batch is `queued` and unclaimed, every `depends_on` edge resolves to an earlier
position in the global batch order or to an external phase confirmed `complete`, and every stage
boundary was computed from shared `systems` or prefix-overlapping `deliverables`.

## Two things worth carrying forward

**The prefix collision rule matters.** A first pass computed deliverable collisions by exact set
intersection and reported `phase-conc-02` and `phase-irs-04` disjoint. They are not:
`tools/git-hooks/` sits under `tools/`. Drawn that way, the table would have declared a parallel
stage the claim validator refuses. `GOV-016` records the rule; `000316` would enforce it.

**Collision, not dependency, is what serializes a batch.** `batch-002` is six stages for seven
phases, and only one stage is parallel — because five of the seven declare `sys-governance`. Two of
them have no dependencies at all and still cannot run together.

## One deviation, stated

The owner scoped this session to data and prompt work with no Python, so that `AGENTS.md`'s
requirement-and-plan-before-code gate would not apply. One line of `src/` was nonetheless added:
`docs/09-backlog/batches/README.md` in `__main__.py`'s `EXEMPT` set, exactly parallel to the
existing `docs/09-backlog/README.md` entry. Without it the front-matter scanner rejects the
directory's navigation README. It adds no behavior; the deferred validator remains unbuilt and
unplanned, held in `000316`.

## Not done

`batch-002` was not run. The session's purpose became the mechanism rather than the build, and the
batch is `queued` and selectable for the next coordinator session.
