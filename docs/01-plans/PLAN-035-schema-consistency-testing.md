---
schema_version: 1
id: doc-schema-consistency-testing
code: PLAN-035
title: Schema consistency and testing (P8)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-contracts, sys-delivery]
depends_on: []
---

# Schema consistency and testing (P8)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-10`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P8` of the twelve, tenth in the owner's delivery order. Making drift between schema,
DDL, fixtures and CI mechanically impossible. Distinct from `P2`, which is document hygiene; this
is code and contract hygiene.

**8 ideas across 4 fine groups**, from the accepted partition of 2026-09-13. Sizing at partition
time was 4–5 phases.

| Group | Ideas | What it covers |
|---|---|---|
| `G33` Schema/DDL drift and contract compiler | `000024`, `000035`, `000052` | `000052` is the umbrella, `000024` the concrete four-entity drift, `000035` the general compiler proposed to fix it |
| `G34` Testing strategy | `000001`, `000026`, `000057` | `000057` names both other members; `000026` adds the missing `ts/` lint and test gate; `000001` governs HTML-generation fixtures |
| `G35` Overview drift test | `000106` | One pytest mirroring `test_ideas.py`'s committed-output pattern for `_public/overview/index.html` |
| `G36` Layout-schema test **[RESOLVED]** | `000098` | **Already shipped** — schema and 21 passing tests exist. Carried for completeness; no work remains |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P8`.
- **`schemas/` and `sql/001_schema.sql`** — the two artifacts `G33` would stop from drifting apart, plus `tools/rebuild_db.py` which unpacks between them.
- **The reliability follow-up** ([PLAN-004](PLAN-004-reliability-follow-up.md)) — `phase-rel-01` restored the baseline Python lint gate; `000026` is the `ts/` half that is still missing.
- **The HTML generation overview** ([PLAN-003](PLAN-003-dynamic-html-generation/PLAN-003-overview.md)) — `000001` is dormant until this builds.
- **`test/test_ideas.py`** — the committed-output test pattern `G35` would copy.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section, applied to
this programme: requirement, design, real phases under a registered prefix, and pruning
`phase-prog-10` from `next_up` on completion.

## Known facts not to rediscover

- **`G33` was unanimous across all four analysts**, but its scope is not settled: decide whether
  `000024`'s concrete drift fix or `000035`'s general compiler is being committed to **before**
  sizing anything. They are different amounts of work for the same symptom.
- **`G36` is already shipped.** Schema and 21 passing tests exist. Do not re-plan it.
- **`000026` is actionable today** — the `ts/` lint and test gate needs nothing that does not exist.
- **`000001` is dormant** until `PLAN-003` builds, so it should not hold up the rest of `G34`.
- **`G35` is under one phase** and was placed here on its own `relates_to` link to `000057`.
- **A related gap found on 2026-09-14, not in this programme:** `tools/build_idea_corpus.py` shipped
  with no tests at all. That is covered by `phase-part-02` under
  [PLAN-025](PLAN-025-repeatable-idea-partition.md), not here — but it is the same class of defect
  this programme exists to prevent.
