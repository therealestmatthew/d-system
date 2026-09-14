---
schema_version: 1
id: doc-workbench-architecture-quality
code: PLAN-028
title: Workbench architecture and quality (P10)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: []
---

# Workbench architecture and quality (P10)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-03`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P10` of the twelve, **second in the owner's delivery order**. Audits and architecture of
the workbench itself, as against `P11`'s discrete features — the same product, a different kind of
work.

It was moved ahead of `P11` on 2026-09-14, on the owner's ruling. `G40`'s container-vs-content
vocabulary is cited as a prerequisite by six ideas, four of them in `P11`, so planning the features
first would have meant naming things twice. The plan codes were already permanent by then, which is
why `PLAN-028` sits after `PLAN-027` while running before it; `next_up` is the authority on order.

**13 ideas across 8 fine groups**, from the accepted partition of 2026-09-13. Sizing at partition
time was 12–15 phases, with `G43` alone approaching a full architecture revision.

| Group | Ideas | What it covers |
|---|---|---|
| `G40` Vocabulary | `000124` | Settles container-vs-content naming before more work names things wrong |
| `G41` Duplication and structure audits | `000115`, `000116` | Two-way cross-reference: an abstraction extracted in one is often the refactor proposed in the other |
| `G42` Content-fit methodology | `000134` | Per-panel visibility contracts and mechanised checks |
| `G43` Slot/panel architecture | `000133`, `000135`, `000141` | `000141` generalises `000135` structurally and would prevent the double-header defect by construction; `000133` revisits geometry on the same model |
| `G44` Sub-app packaging | `000144` | How a sub-app plugs into a slot |
| `G45` Ports/process app | `000142`, `000143` | Explore the lifecycle, then build the tool — raised together against the same port-conflict incidents |
| `G46` Performance and cache invalidation | `000114`, `000121` | `000121` sharpens `000114`'s invalidation requirement with a dated failure: a stale overview page during demo prep |
| `G47` Terminal persistence audit | `000113` | Session survival and latency across all three shells |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P10`.
- **Workbench requirements** ([REQ-007](../06-requirements/REQ-007-workbench.md)) and the **workbench plan** ([PLAN-022](PLAN-022-workbench.md)).
- **Workbench layout persistence** ([ADR-016](../04-decisions/ADR-016-workbench-layout-persistence.md)) — the model `G43` would revise.
- **Workbench features and defects** ([PLAN-027](PLAN-027-workbench-features-defects.md)) — the sibling programme on the same product; `G40` is a prerequisite for its renaming work.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section, applied to
this programme: requirement, design, real phases under a registered prefix, and pruning
`phase-prog-03` from `next_up` on completion.

## Known facts not to rediscover

- **`G40` comes first and is cited as a prerequisite by six ideas** — `000115`, `000116`, `000133`,
  `000135`, `000141` and `000144`. It is a documentation deliverable completable alone, in about one
  phase. It is the reason this programme was moved ahead of `P11`, so it should be the first
  implementation phase this plan produces, not a later one.
- **`G40` gates `G43` and `G44`** by those ideas' own text, not by an inference drawn here.
- **`G46` measures before it changes anything** — `000114` is the measurement, `000121` the
  refinement, and they are not separable.
- **`G47` cannot be fully verified on Linux.** Some checks need the owner's Windows machine.
- **`G44` is dual-natured.** Its concrete half rides `G45`, its general half needs `G40` and `G43`.
  It was kept whole because the idea is one entry, not because the work is one piece.
- **`G45` is fully standalone** and was named a *candidate* first sub-app for `G44`, not a
  requirement of it.
