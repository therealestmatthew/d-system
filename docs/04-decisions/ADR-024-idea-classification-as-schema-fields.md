---
schema_version: 1
id: doc-adr-idea-classification-as-schema-fields
code: ADR-024
title: Idea classification lands as fields on the idea schema, not a separate graph layer
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-contracts, sys-portfolio]
depends_on: [doc-idea-node-classification, doc-idea-graph-lifecycle, doc-idea-graph-lifecycle-requirements]
---

# Idea classification lands as fields on the idea schema, not a separate graph layer

## Status

Accepted. This records the owner's scope-fork ruling, made in
[PLAN-029](../01-plans/PLAN-029-idea-graph-lifecycle.md) decision 1 (2026-09-15), which names this
record as the one decision in that plan that needs an ADR. `phase-idg-01` wrote it before changing
the schema, so the schema follows from the ruling rather than the ruling being reconstructed from
the schema.

## Context

[ARCH-005](../07-architecture/ARCH-005-idea-node-classification.md) defines a closed classification
for idea records: a record kind, and for knowledge records one value on each of four axes
(ontological, epistemic, lifecycle, temporal). It left open where that classification lives, and
named two candidates:

1. **Fields on `schemas/idea.schema.json`**, carried by events in `_data/ideas.jsonl` and derived
   by `src/db/ideas.py`'s `fold()` like every other idea property.
2. **A separate typed-node graph layer** in which ideas, memories (`brain/`, `docs/05-memories/`)
   and governed documents all become nodes, with the classification as a property of the node
   rather than of the idea record (ideas `000060`, `000032`).

The second is the more general design. It does not exist: it depends on the retrieval and memory
work in `P6` ([PLAN-033](../01-plans/PLAN-033-retrieval-knowledge-infrastructure.md)), none of
which has started.

## Decision

**The classification is fields on the idea schema.** It is written by a new `classified` event
through the sanctioned writer, `tools/append_idea.py`, and folded by `fold()`. No separate graph
layer is built.

The shape that follows, as `phase-idg-01` landed it:

- **A `classified` event** carries `record_kind` and, on a knowledge record, `ontological`,
  `epistemic`, `lifecycle` and `temporal`, each a closed lowercase snake_case enum with one token
  per ARCH-005 type. It also carries `reasons` and `confidence` (0 to 1), each keyed per axis,
  `lifecycle_remedy` (only when `lifecycle` is `retrospective_insight`), `decompose`,
  `tie_breaks` (the ARCH-005 rule ids applied) and `author`. `author` and the event's `at` are the
  provenance. A `collection`, `fixture` or `reference` record carries none of the axis fields.
- **The latest `classified` event wins.** A reclassification is another event, never an edit,
  so the history of how an idea was classified is kept.
- **Classification is an event rather than fields on `created`**, because `created` lines are
  permanent and the corpus already holds hundreds of ideas. Backfilling them is an append
  (REQ-014 R07, PLAN-029 decision 4), which only a separate event allows.

The same change adds the rest of the ARCH-005 bundle (PLAN-029 decision 3): the `component_of`
link type, the owner-only `lineage` annotation kind, and `target_code`, a link target naming a
governed document code instead of an idea. It also adds the terminal statuses `delivered`,
`resolved` and `absorbed`, and makes `promoted` non-terminal (GOV-003, 2026-09-22 ruling).

## Alternatives rejected

- **A typed-node graph layer now.** It would block every `G01` idea, and everything in `P1` that
  depends on them, behind an unbuilt substrate. At roughly 460 ideas the traversal queries ARCH-005
  wants ("every Strategic Directive resting on a Hypothesis") are joins over two closed enums, which
  the DuckDB derived layer expresses without a graph library.
- **Tags.** ARCH-001's tags are open-vocabulary and additive. A classification written as tag values
  cannot be validated as a closed set, and REQ-014 R01 requires that a classification written as a
  tag be rejected.

## Consequences

**The migration cost, stated plainly.** If `P6` later builds the graph layer, these fields become a
migration rather than a design already fitted to it. The migration is a read of every idea's
latest `classified` event into the new node store. It is bounded by the size of the log and needs
no rewrite of `_data/ideas.jsonl`, because the events remain the record. The blockage the
alternative would cause is not bounded, which is why the cost is accepted.

Other consequences:

- The classification is validated by the schema and the writer like every other idea field, and
  coverage is countable from `fold()` alone (REQ-014 R03).
- Consumers that read the idea log directly, rather than through `fold()`, see `classified` events
  they do not understand. The DuckDB projection (`tools/rebuild_db.py`) stores their common columns
  and drops the classification fields until it is extended.
- An idea record, a memory and a document remain different kinds of thing with no shared node
  type. A query across all three waits for `P6`.
