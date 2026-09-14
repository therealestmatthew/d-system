---
schema_version: 1
id: doc-autonomous-agent-operations
code: PLAN-032
title: Autonomous agent operations (P5)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-governance, sys-api]
depends_on: []
---

# Autonomous agent operations (P5)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-07`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P5` of the twelve, seventh in the owner's delivery order. All five members assume the
system operating with no chat session open. It is the most speculative programme in the set, sized
at 10+ phases if built in full.

**5 ideas in 1 fine group**, from the accepted partition of 2026-09-13.

| Group | Ideas | What it covers |
|---|---|---|
| `G24` Gateway, ledger, worker, broker, librarian | `000020`, `000028`, `000029`, `000030`, `000031` | Deliberately decomposed from one proposal so each could be evaluated alone. `000030` has no purpose until `000028` and `000029` exist; `000031` gates unattended running; `000020` links to both `000028` and `000031` |

Internal order is `000028` → `000029` → `000030`, with `000031` required before anything runs
unsupervised.

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P5`.
- **Agent engineering and delegation** ([PLAN-031](PLAN-031-agent-engineering-delegation.md)) — `G21`'s shared-state model is the lighter alternative to `000020`.
- **Retrieval and knowledge infrastructure** ([PLAN-033](PLAN-033-retrieval-knowledge-infrastructure.md)) — `000020`'s librarian half overlaps this ground.
- **Multi-agent concurrency** ([ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md)) — the claim model any unattended worker must honour.
- **`AGENTS.md`** — the standing rule that an agent never marks a phase complete, which constrains what `000031` can be allowed to authorise.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section, applied to
this programme: requirement, design, real phases under a registered prefix, and pruning
`phase-prog-07` from `next_up` on completion.

## Known facts not to rediscover

- **This is the strongest signal in the partition.** All four analysts placed these five in one
  programme, the control included — which means the grouping cannot be inherited framing from the
  triage findings. Do not re-litigate the membership.
- **The fine-level granularity is disputed, the membership is not.** Two analysts subdivided the
  five per component. That is a granularity difference, and the partition records it as such.
- **`000020` is a decline candidate.** The control analyst nominated declining it in favour of
  `000128` (`P4`'s `G21`), because its librarian half overlaps both `P6`'s retrieval ground and a
  lighter existing mechanism. Settle that before planning around it.
- **`000031` is a gate, not a feature.** Nothing in this programme should run unsupervised before it
  exists.
- **Speculative does not mean cheap.** The partition sized this at 4 phases plus design for the
  group, and 10+ if every component is built.
