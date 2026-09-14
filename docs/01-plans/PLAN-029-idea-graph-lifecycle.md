---
schema_version: 1
id: doc-idea-graph-lifecycle
code: PLAN-029
title: Idea graph and lifecycle (P1)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-portfolio, sys-projection, sys-governance]
depends_on: []
---

# Idea graph and lifecycle (P1)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-04`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P1` of the twelve, fourth in the owner's delivery order. Every member changes,
agentifies, or reports on the append-only idea log and the schema it folds through.

**19 ideas across 4 fine groups**, from the accepted partition of 2026-09-13. Sizing at partition
time was 10–13 phases if built in full, with `G03` the most shovel-ready.

| Group | Ideas | What it covers |
|---|---|---|
| `G01` `ARCH-005` schema bundle | `000018`, `000053`, `000061`, `000062`, `000063`, `000064`, `000065` | Tagging, doc-code link targets, the three-axis classification, its agent, the withdrawn forking link resolved into a lineage annotation, and the decomposition procedure |
| `G02` Idea-system agents | `000048`, `000055`, `000127` | `000048` and `000127` are the same ask six days apart — move `/idea`'s write into a subagent returning only the id; `000055` maintains the link graph those writes create |
| `G03` Idea and backlog reporting | `000008`, `000010`, `000042`, `000050`, `000070`, `000071` | `000050` is the umbrella parenting `000010`; `000008` supplies the metrics it renders; `000042` is the same instinct over two logs |
| `G04` Idea-to-plan drafting | `000046`, `000047`, `000049` | `000046` names `000047` its own prerequisite; `000049` surfaced from triaging `000046` and blocks its design |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P1`.
- **Idea node classification** ([ARCH-005](../07-architecture/ARCH-005-idea-node-classification.md)) — the owner's own document, which already bundled `G01`'s seven ideas as one governed unit.
- **Idea record system** ([PLAN-016](PLAN-016-idea-record-system.md)) and the **idea/plan lifecycle** ([PLAN-017](PLAN-017-idea-plan-lifecycle)) — the existing substrate.
- **Idea staging** ([ADR-010](../04-decisions/ADR-010-idea-staging.md)) — the record-as-given rule and the staging boundary.
- **Document and backlog governance** ([PLAN-030](PLAN-030-document-backlog-governance.md)) — `G05`'s requirement-vs-plan rule informs `G04`.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section, applied to
this programme: requirement, design, real phases under a registered prefix, and pruning
`phase-prog-04` from `next_up` on completion.

## Known facts not to rediscover

- **`G01` is not internally separable by design.** `ARCH-005` names exactly those seven ideas as
  one unit; splitting them re-opens a decision the owner already made. It needs a governing
  requirement and plan that do not yet exist.
- **`G03` is largely delivered in part.** `000071` is already prototyped and `000070` largely done.
  Verify what exists before sizing.
- **`G04` was contested 2–2** among the analysts and was ruled on the one-directional dependency,
  not by counting. Read the partition's disagreement table before revisiting it.
- **`000072`'s planner bullet duplicates `000046`.** `000072` lives in `P4` (`G16`); only the
  control analyst caught the duplication. The partition recommends striking the bullet rather than
  building the same thing twice.
- **`G02`'s `000055` depends on `G01`**; the rest of `G02` does not.
