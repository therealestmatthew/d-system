---
schema_version: 1
id: doc-blocked-downstream-projections
code: PLAN-034
title: Blocked downstream projections (P7)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-projection, sys-portfolio, sys-signals]
depends_on: []
---

# Blocked downstream projections (P7)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-09`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P7` of the twelve, ninth in the owner's delivery order. Each member needs infrastructure
that does not exist, and `000022` is the root fact behind most of it. The partition records this
programme as **not yet sizeable**, and independent of everything else in the corpus.

**4 ideas across 2 fine groups**, from the accepted partition of 2026-09-13.

| Group | Ideas | What it covers |
|---|---|---|
| `G31` Portfolio data gap | `000022` | Two of four core entities hold zero records. Is that tooling friction, or no current need? |
| `G32` Temporal, scenario and calibration | `000033`, `000034`, `000036` | Three views over projections that do not yet exist — history snapshots, what-if simulation, and whether advice helped |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P7`, including the decline tiers where the control analyst nominated all three of `G32`.
- **The structure/content boundary** ([ADR-009](../04-decisions/ADR-009-structure-content-boundary.md)) — why the tracked `_data/` is fictional and the real portfolio lives at `_private/portfolio/`, which bears directly on how `G31` is even measured.
- **The mini-systems proposal** ([PLAN-002](PLAN-002-mini-systems-proposal.md)) — the `phase-sig-*` and `phase-syn-*` signal and synthesis lines these views would consume.
- **Idea record system** ([PLAN-016](PLAN-016-idea-record-system.md)) — `000033` needs `phase-idea-07`'s fold.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section — but see the
first known fact below. Finalizing this programme may reasonably conclude that `G32` stays dormant
and only `G31` gets phases.

## Known facts not to rediscover

- **`G31` is a question for the owner, not a build.** It is sized at under one phase to resolve, and
  resolving it is what determines whether `G32` has any subject matter at all. Answer it before
  writing a requirement for anything downstream.
- **`G31` gates `G32`** — entirely, not partially.
- **All three of `G32` were nominated for decline** by the control analyst. That nomination has not
  been ruled on; it is a live option, not a settled outcome.
- **Each `G32` member is blocked by something different:** `000033` on `phase-idea-07`'s fold,
  `000034` on portfolio signals and `G31`, and `000036` on recommendations existing at all.
- **Measuring the data gap needs care about the data root.** The tracked `_data/` is a fictional
  example set by design, so a count taken there says nothing about the owner's real portfolio. See
  `ADR-009` and `GOV-001`'s data-root section.
