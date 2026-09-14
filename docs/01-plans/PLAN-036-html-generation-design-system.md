---
schema_version: 1
id: doc-html-generation-design-system
code: PLAN-036
title: HTML generation and design system (P9)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-html]
depends_on: []
---

# HTML generation and design system (P9)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-11`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P9` of the twelve, eleventh in the owner's delivery order. The template, component and
palette layer of the generation pipeline, and its relationship to plans written before the
workbench existed. Its consumer is generated report pages, which is what separates it from `P10`
and `P11`, whose consumer is an interactive panel app.

**6 ideas across 3 fine groups**, from the accepted partition of 2026-09-13. Sizing at partition
time was 5–6 phases, mostly gated on `PLAN-003`.

| Group | Ideas | What it covers |
|---|---|---|
| `G37` Libraries and designer agent | `000083`, `000084`, `000085`, `000092` | Three cross-linked asset layers feeding one pipeline, plus the agent that would populate all three by scanning shipped pages |
| `G38` Governance atlas page | `000093` | A content deliverable from the existing atlas family |
| `G39` HTML-gen plan reconciliation | `000123` | Dispositions each old `phase-html-*` requirement as accomplished, open, superseded or retired |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P9`.
- **The HTML generation overview** ([PLAN-003](PLAN-003-dynamic-html-generation/PLAN-003-overview.md)) and its six child plans — what `G39` reconciles and what `G37` is gated on.
- **The HTML adversarial audit** ([ARCH-003](../07-architecture/ARCH-003-html-adversarial-audit.md)) — prior findings against this pipeline.
- **`templates/html/` and `templates/styles/`** — the existing template families, including the atlas family `G38` draws on.
- **Idea graph and lifecycle** ([PLAN-029](PLAN-029-idea-graph-lifecycle.md)) — its `G03` reporting work builds on the *existing* generation framework, not on this programme's new libraries. That boundary was tested by two analysts and is the one place these two programmes could be confused.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section, applied to
this programme: requirement, design, real phases under a registered prefix, and pruning
`phase-prog-11` from `next_up` on completion.

## Known facts not to rediscover

- **`G39` should precede detailed scoping of `G37`.** It is independent research that produces
  `G37`'s scope, and it is roughly one phase. Doing it second wastes the scoping work.
- **`G37` is blocked on `PLAN-003`**, but evaluation can start now: the atlas family is an existing
  manual precedent to evaluate against.
- **`G38` was already deferred once by the owner.** Check that ruling before re-queueing it.
- **`G38` does not depend on `G37`.** It depends on the atlas family that already exists, not on
  `G37`'s automation.
- **The `phase-html-*` line predates the workbench.** `G39` exists precisely because some of those
  requirements may now be accomplished, superseded or retired, and nobody has dispositioned them.
