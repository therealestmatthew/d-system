---
schema_version: 1
id: doc-document-backlog-governance
code: PLAN-030
title: Document and backlog governance (P2)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-governance, sys-backlog]
depends_on: []
---

# Document and backlog governance (P2)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-05`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P2` of the twelve, fifth in the owner's delivery order. The contract governing what a
governed document is and how the backlog carries it. A different substrate from `P1`, which is the
idea log, and from `P3`, which is agent safety mechanics rather than document contract.

**7 ideas across 4 fine groups**, from the accepted partition of 2026-09-13. Sizing at partition
time was 4–5 phases; every member is small.

| Group | Ideas | What it covers |
|---|---|---|
| `G05` Document contract | `000038`, `000056` | `000038` fixes the requirement-vs-plan boundary; `000056` governs document staleness and retirement |
| `G06` Backlog substrate | `000006`, `000011`, `000037` | Three capacity questions against one registry — index widths, a reprioritisation recipe, and splitting `backlog.yaml` before it clogs agent context |
| `G07` Phase containment check | `000027` | Nothing diffs a completed phase's actual change set against its declared paths |
| `G08` `_tmpagent` registry | `000023` | A load-bearing mechanism missing from `systems.yaml`'s maturity registry |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P2`.
- **The governance protocol** ([GOV-001](../08-governance/GOV-001-protocol.md)) and **document codes** ([GOV-005](../08-governance/GOV-005-document-codes.md)) — the contract `G05` sharpens.
- **The backlog protocol** ([GOV-002](../08-governance/GOV-002-backlog-protocol.md)) and **accepted decisions** ([GOV-003](../08-governance/GOV-003-backlog-decisions.md)) — the substrate `G06` scales.
- **The `_tmpagent` contract** ([`_tmpagent/AGENTS.md`](../../_tmpagent/AGENTS.md)) and [PLAN-015](PLAN-015-ephemeral-working-plans.md) — what `G08` would register.
- **Idea graph and lifecycle** ([PLAN-029](PLAN-029-idea-graph-lifecycle.md)) — `G05` informs its `G04`.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section, applied to
this programme: requirement, design, real phases under a registered prefix, and pruning
`phase-prog-05` from `next_up` on completion.

## Known facts not to rediscover

- **`G05` was kept out of `P1`'s `G04` deliberately.** `000056`'s own text admits an unresolved
  overlap with `000047`. That is a scope question for the owner to settle, not a reason to merge the
  two groups.
- **`G07` is the nearest existing mechanism to hang `000204` on** — the systemic finding that
  resolved work leaves its idea open.
- **`G08` is near-mechanical**, effectively a registry entry, and sized at trivial.
- **`G06`'s three members are independently shippable** and were grouped for readability, not
  dependency. Roughly one phase each.
- **An existing phase already covers adjacent ground:** `phase-gov-01` (reject backlog deliverables
  claiming an unreserved code) is ready and queued outside this programme. Check it before writing
  a phase that overlaps it.
