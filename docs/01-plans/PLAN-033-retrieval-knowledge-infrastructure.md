---
schema_version: 1
id: doc-retrieval-knowledge-infrastructure
code: PLAN-033
title: Retrieval and knowledge infrastructure (P6)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-retrieval, sys-memory-agents, sys-brain]
depends_on: []
---

# Retrieval and knowledge infrastructure (P6)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-08`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P6` of the twelve, eighth in the owner's delivery order. How the system finds and judges
its own accumulated knowledge — distinct from `P1`, which is the idea graph's shape rather than
search over it.

**9 ideas across 5 fine groups**, from the accepted partition of 2026-09-13. Mostly design work
rather than code, sized at roughly one session per sub-question surveyed.

| Group | Ideas | What it covers |
|---|---|---|
| `G25` Ordering and deterministic search | `000002`, `000040` | `000002` is named by `000040` as its conceptual parent; `000040` is the deterministic layer, explicitly not the vector work |
| `G26` Vector retrieval | `000004` | Vector/RAG tooling and the `phase-mem` line it gates |
| `G27` Code-graph retrieval | `000005` | GitNexus evaluated against this repository's code |
| `G28` Documentation companion set | `000043`, `000044`, `000045` | `000045`'s body names the other two as companion ideas, deliberately split so one decision — structured front matter, graph, or vector for the documentation corpus — is made from all three surveys together |
| `G29` Memory lifecycle and provenance | `000032`, `000060` | Staleness, contradiction and confidence over memory content, with `000032`'s lineage graph as its trust layer |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P6`.
- **The agent memory system** ([PLAN-001](PLAN-001-agent-memory-system.md)) — the `phase-mem-*` line this programme gates and is gated by.
- **File-based governance** ([ADR-001](../04-decisions/ADR-001-file-based-governance.md)) — `000043` proposes reversing it, so it must be revisited first.
- **Agent engineering and delegation** ([PLAN-031](PLAN-031-agent-engineering-delegation.md)) — `000081` in its `G14` would consume `G25`'s query contract without sharing its deliverable.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section, applied to
this programme: requirement, design, real phases under a registered prefix, and pruning
`phase-prog-08` from `next_up` on completion.

## Known facts not to rediscover

- **The whole programme is gated on evidence nothing currently collects.** It needs a recorded
  retrieval failure, and `G25` is what would supply it. Until then every other group is
  speculative.
- **`G25` would unblock work outside this programme** — `phase-mem-15`, `-16`, `-18` and `-19` wait
  on the failure evidence it produces.
- **`G28` must be kept whole.** Audit 2 caught the synthesis step silently splitting `000045` out on
  mechanism grounds; it was restored on the idea's own self-description. Do not re-split it.
- **`000043` reverses `ADR-001`.** That decision needs revisiting before `G28` can be scoped.
- **`G27` needs no design work** — it resolves by installing a tool and evaluating it. Roughly one
  phase.
- **`G26` and `G28` are complementary, not substitutes**, and `000045` is not part of `G26`.
