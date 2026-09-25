---
schema_version: 1
id: doc-idea-node-classification
code: ARCH-005
title: Idea node classification (ontological, epistemic, lifecycle, temporal)
kind: architecture
status: active
owner: repository-owner
created: '2026-09-09'
updated: '2026-09-25'
systems: [sys-contracts, sys-portfolio]
depends_on: [doc-idea-record-system, doc-idea-plan-annotations-links, doc-tagging]
---

# Idea node classification (ontological, epistemic, lifecycle, temporal)

Recorded from the owner's proposal (2026-09-09) as a durable reference for the classifications
themselves. The originating idea is `000061` in `_data/ideas.jsonl` (recorded verbatim per
[ADR-010](../04-decisions/ADR-010-idea-staging.md)); this document is the properly-structured
counterpart the owner asked for once the idea itself was captured.

**Accepted by the owner 2026-09-25.** This version is the vocabulary a classifier, the classification agent
(`phase-idg-02`) and the idea schema (`phase-idg-01`) work against. It was revised from the
2026-09-09 draft by the owner's rulings of 2026-09-24 and 2026-09-25, relayed by the Session Manager:

- record kinds, and only knowledge records carry axis values;
- a fourth axis, temporal validity;
- a value on every axis for every knowledge record, with Not Applicable on the epistemic axis
  replacing a blank;
- the lifecycle axis renamed and widened;
- Axiom reworded to a scoped claim;
- agent types classified as Actor / Agent;
- the tie-break rules below, including E4 (2026-09-25).

**Provenance.** The new values Actor / Agent, Metric / Standard, Not Applicable / Agnostic, Active /
Evergreen and Deprecated / Archived came from Gemini's proposals, which the owner forwarded on
2026-09-24 as the current direction. Record kinds, the temporal axis's evidence and the tie-break
rules came from Ideation's v2 and v3 classification runs over the idea log (452 ideas in v2). Those
runs located where two classifiers disagreed, and each tie-break rule settles one of those
disagreements. The owner ruled on every change.

## Why a classification, not another tag

[ARCH-001](ARCH-001-tagging-system.md) already gives ideas a tagging axis — open-vocabulary,
additive, answers "what is this about." Idea `000018` (tagging and plan-mapping system for ideas)
and `000053` (idea-to-document links) both extend that same additive-metadata model: more tags,
richer link targets.

This taxonomy is a different kind of thing. It defines a **small, closed set of node types**
along independent axes, so that graph traversal can partition on *kind of node* the way a
database partitions on a typed column — not by string-matching an open tag vocabulary. The
motivating query is structural, not topical: "every Strategic Directive resting on an Assumption
rather than an Axiom" is a join across two axes, not a keyword search. A tag vocabulary can grow
to describe this after the fact; a closed type system supports the query by construction.

Four axes are defined, each orthogonal to the others and to tags and links. A knowledge record
carries exactly one value per axis (not one overall "type"); see "Required values" below.

## Record kind (decided first)

Before any axis is assigned, a record is given a kind. Only `knowledge` records carry axis values.

| Kind | Definition |
|---|---|
| **knowledge** | States, asks for, or records something about the domain. |
| **collection** | Exists to group other records, stated in its title or body (an anchor, umbrella or shared parent), or its body is mainly a list of other records. A record that bundles several findings of its own is `knowledge` with `decompose` set, not a collection. |
| **fixture** | Test or rehearsal data with no domain content. |
| **reference** | A pointer to an external source kept for later, with no claim or ask of its own. |

`collection`, `fixture` and `reference` records carry no axis values. They are not missing a
classification. They are records whose job is to group, test or point at other records, not to
state a knowledge claim.

## Axis 1 — Ontological (the record's subject)

What kind of thing the record's subject *is*, independent of how true or how actionable it is. The
subject is the thing the record's observation is about, or that its ask would change.

| Type | Definition |
|---|---|
| **Concept / Mental Model** | A theoretical construct, principle, paradigm or classification (e.g. "Observability," "Systems Thinking"). Acts as a gravitational center other nodes cluster around. |
| **Artifact / Entity** | A concrete output or entity: a file, schema, tool, system, dataset or commit. |
| **Process / Workflow** | A sequence of steps: how something is done, who does what, in what order. |
| **Event** | A distinct occurrence in time, as the subject itself. |
| **Actor / Agent** | Who acts: a human role, stakeholder group or autonomous agent, with its remit and authority. Agent types (`.claude/agents/*.md`) are Actor / Agent, not Artifact. |
| **Metric / Standard** | A quantitative measure or threshold that governs something: an SLA, KPI, benchmark, budget or cap. |

## Axis 2 — Epistemic (the truth status of what the record asserts)

How much what the record asserts can currently be trusted or relied upon.

| Type | Definition |
|---|---|
| **Axiom / Ground Truth** | A claim accepted as verified within its stated scope. |
| **Hypothesis / Assumption** | An untested theory, prediction or premise that needs validation before it is safe to build code or infrastructure on top of it. |
| **Anti-Pattern / Falsified Concept** | A disproven theory, failed approach or known dead end. Retained deliberately — an explicit record of what doesn't work prevents cyclical mistakes and marks the boundary of the system, rather than being discarded once disproven. |
| **Not Applicable / Agnostic** | The record asserts no verifiable truth claim: an ask, a proposal, an instruction, a question, or a named thing with nothing claimed about it. |

Axiom was first defined as "a verified, immutable fact". It now names a claim verified within a
scope, because most verified claims in the idea log hold at a point in time. When the claim held is
recorded on the temporal axis, not the epistemic one. A defect verified at a commit and fixed later
was never falsified: it stays an Axiom, and its temporal value records that it was true as of then.

## Axis 3 — Lifecycle

Where the record sits in its evolution: the arc from raw thought to executed and reviewed work, and
also records that stay in force outside that arc or whose subject has been retired.

| Type | Definition |
|---|---|
| **Generative Seed** | A raw or developing idea, before owner commitment. |
| **Strategic Directive** | A committed goal or plan that sets a direction. |
| **Operational Task** | One executable action with a clear done-state. |
| **Retrospective Insight** | A post-execution observation: a gap, technical debt, or newly realized context. |
| **Active / Evergreen** | A standing record in force outside execution: a policy, principle, master data or reference kept current. |
| **Deprecated / Archived** | The record's **subject** has been retired or superseded, and the record is kept for audit. This is not the idea record's own disposition (see "Dispositions are not axis values"). |

**Lifecycle remedy.** When the lifecycle value is Retrospective Insight, the record also carries a
`lifecycle_remedy`: Operational Task when the record names one concrete fix, or Generative Seed when
the remedy is left open. It marks how the record could be split, not a second lifecycle value, and it
is absent on every other lifecycle value.

## Axis 4 — Temporal validity

Whether what the record states is bound to a time. Required on every knowledge record.

| Type | Definition |
|---|---|
| **As-of** | True of a point or interval: a state at a commit, a count on a date, a condition later work changes. A later change makes it untrue without falsifying it. |
| **Standing** | True or relevant without a time bound: a principle, a want, a standing rule. |

The axis records only whether the record is time-bound. The interval itself (when it was observed,
until when it holds) is data a schema may carry; a classifier cannot supply it.

## Required values

- Every `knowledge` record has one value on each of the four axes. The epistemic axis may be Not
  Applicable / Agnostic. No axis is blank.
- `collection`, `fixture` and `reference` records have no axis values.
- A reason is kept for each axis value.

## Dispositions are not axis values

Discarding and superseding are dispositions of the idea record, independent of every axis. In the
owner's words (2026-09-24), an idea is discarded when it has "no value to what we are trying to
build", and superseded when "we propose a better or more detailed idea that explains more
effectively". Whether an idea is held true, or later revised as not valid, is a separate question
from whether it is discarded or superseded. A discarded or superseded record keeps its own axis
values, including its lifecycle value. Deprecated / Archived describes the record's subject, not
the record.

## Tie-break rules

A classifier, and the `phase-idg-02` agent, applies these rules when more than one value seems to
fit. Order: record kind is decided first; L3 is applied before L1; E4 overrides E1.

**Ontological.**

- **O1, Artifact vs Process.** Editing a file, schema, code or data is Artifact. Changing steps,
  their order or who performs them is Process, even when the steps live in a file. If the title
  names both, pick the thing the record's observation measures or counts. If nothing is measured,
  Process.
- **O2, Actor vs Artifact.** An agent type and its remit or definition are Actor / Agent. Tooling
  that generates, indexes or lists agent files is Artifact.
- **O3, Metric vs Artifact or Process.** Metric / Standard only when the number or threshold is the
  subject. The tool that computes it, or the step that checks it, is Artifact or Process.
- **O4, Event.** An incident that evidences a lasting defect is evidence, not the subject. Classify
  the defective thing.
- **O5, Actor vs Process.** Adding, removing or re-scoping a role is Actor / Agent. Changing an
  existing role's steps is Process.
- **O6, a bundle of unrelated findings.** The record is `knowledge` with `decompose` set. Its
  ontological value is the value its parts share, otherwise the value of the first finding named in
  the title.

**Epistemic.**

- **E1, the record's point.** Classify what the record asks or asserts as its point, using the title
  as the proxy. A defect, count or fact in the title is Axiom. An imperative, proposal or question is
  Not Applicable.
- **E2, a verified symptom with a guessed cause.** Axiom; the reason names the guessed part.
- **E3, scope and time.** An Axiom verified at a point in time stays an Axiom, and the temporal axis
  carries its time bound. A fixed defect was never falsified.
- **E4, an Insight asserts its observation** (owner ruling, 2026-09-25). If the lifecycle value is
  Retrospective Insight, the epistemic value is Axiom, or Hypothesis when the observation itself is
  hedged. E4 overrides E1.

**Lifecycle.**

- **L3, Directive vs Evergreen (applied before L1).** A standing rule ("every", "always", "from now
  on", "must" applied to all future cases) is Active / Evergreen. "Build X" is a Strategic Directive.
- **L1, Seed vs Directive.** Strategic Directive requires evidence of owner commitment in the record:
  a ruling, a promotion, "we will", "must", "non-negotiable", or a relayed owner imperative to
  produce a named deliverable. An imperative to investigate or explore is not commitment.
- **L2, Seed vs Task.** Operational Task is one action with a checkable done-state and no open
  choice. If the record lists options or questions, it is a Generative Seed.
- **L4, an observation with a remedy.** The lifecycle value is Retrospective Insight, and
  `lifecycle_remedy` is Operational Task or Generative Seed.
- **L5, Deprecated.** Only when the record's subject is retired or superseded. A record about
  something stale that is still in use is a Retrospective Insight.

**The `decompose` marker.** A knowledge record that bundles several unrelated findings of its own
is marked `decompose: true` (O6). It is still classified as one record. The marker flags it for the
decomposition procedure (`000065`) rather than splitting it at classification time.

## What this unlocks

Separating node class from subject tag is what makes the traversal queries the taxonomy is for
possible at all: isolating a subgraph of every `Strategic Directive` whose supporting links land
on `Hypothesis`/`Assumption` nodes rather than `Axiom` nodes surfaces structural risk in a plan
before any code is written against it. That query is a filter on two closed enums; it is not
expressible as a tag search without first inventing tags that duplicate the taxonomy.

## Composition and abstraction (resolved 2026-09-09)

Discussing this taxonomy surfaced a related but separate question — how ideas compose into
larger ones — resolved with the owner and recorded here because it changes what "atomic" and
"compound" mean for this taxonomy's purposes:

- **Atomic and compound are not a fourth axis, and not node types at all.** They are structural
  *positions*, derivable from the graph rather than hand-classified: whether anything asserts
  `component_of` into a node. A node with nothing composed into it reads as atomic; one with
  edges composed into it reads as compound — at whatever level of the graph you're looking.
- **Composition runs bottom-up, never top-down.** A "compound idea" that started as a brainstorm
  dump of several unrelated thoughts is not decomposed by forking it apart — that dump was never
  one real node. A genuine compound (an emergent system where the whole does something none of
  its parts do alone) is *constructed*: specific atomic ideas are explicitly asserted to
  function together via a new link type, `component_of` (atomic idea → the compound it
  functions within), many-to-many by design — one atomic idea can be a real component of more
  than one distinct emergent system.
- **`extends` is unaffected and keeps doing real work one level up.** Once a compound exists as
  an emergent whole, it is itself a node with its own irreducible meaning and can `extends` a
  still-more-abstract idea — the same `component_of` → `extends` pattern repeats fractally
  rather than there being two fixed buckets.
- **Provenance of thought is not provenance of meaning.** An earlier version of this discussion
  proposed a `forked_from` link type recording which compound idea an atomic fragment was pulled
  out of. That was dropped: it records how the owner arrived at an idea, not how ideas currently
  relate, so it doesn't belong in the relationship graph at all. It is instead proposed as a new
  annotation kind (`000064`) — queryable, but structurally inert, same as `note`/`assessment`
  today.
- **Open tension, left unresolved**: an `Axiom`/`Ground Truth` is meant to be indivisible, yet it
  seems plausible for an axiom-level idea to itself be composed of several atomic ideas
  functioning together — the same fractal pattern as a `Concept`. Whether that contradicts the
  epistemic axis's intent, or epistemic status and compositional structure are simply
  independent and can co-occur, is unresolved pending real examples.

See `000063`'s `assessment` annotation for the full resolution, `000064` (lineage annotation
kind) and `000065` (a decomposition procedure for compound ideas that don't hold together as one
node) for the ideas this produced.

## Open questions

Deliberately unresolved here — this document defines the vocabulary, not the implementation:

- **Does every idea need a value on every axis?** Resolved by the owner on 2026-09-24. Every
  knowledge record has one value on each of the four axes, and the epistemic axis may be Not
  Applicable / Agnostic. Records that are not knowledge records carry a record kind instead of axis
  values. A reason is kept for each axis value. See "Required values".
- **Where does this live?** Three new fields on `schemas/idea.schema.json`, a separate typed-node
  system that ideas participate in alongside a new memory/document graph (see `000060`, `000032`),
  or the seed of a distinct knowledge-graph layer that ideas are only one source feeding.
  *Superseded by [PLAN-029](../01-plans/PLAN-029-idea-graph-lifecycle.md) decision 1: fields on the
  idea schema, not a separate graph layer.*
- **Who assigns it, and when?** The owner has proposed a dedicated classification agent whose
  only job is interpreting an idea's essence into these axes — explicitly not tagging,
  not relationship-building. That agent does not exist yet; this document defines what it would
  classify against.
- **Backfill.** 61 ideas already exist unclassified as of this document's creation. A schema
  change here is not schema-forward-only unless the taxonomy is allowed to be silently absent on
  everything written before it, which weakens exactly the partition queries motivating this work.
- **Interaction with retrieval.** Whether node type becomes a first-class filter/facet once
  `000004`/`000005`/`000043`/`000044`/`000045`'s vector/graph retrieval work lands, or stays a
  property only the idea system itself reasons about.
- **Query surface.** Whether a graph-processing library (NetworkX was named as an example) is the
  intended way to run these traversal queries, or whether the existing DuckDB derived layer
  (`tools/rebuild_db.py`) can express the same joins over relational tables adequately at this
  corpus size.

## Recommended build order (2026-09-09)

*Superseded by [PLAN-029](../01-plans/PLAN-029-idea-graph-lifecycle.md), whose phase table and
execution order now govern this sequencing; this section is kept as the owner's 2026-09-09 assessment.*

The owner's assessment of sequencing across every idea this document touches, given as of a
65-idea corpus. Not a commitment — no REQ or PLAN exists yet (see item 2) — but the order this
work would go in once one does.

1. **Resolve the scope fork first.** Is this a handful of new fields/enum values on the existing
   `schemas/idea.schema.json`, or the seed of a separate graph layer that ideas, memories
   (`brain/`, `docs/05-memories/`), and documents all become nodes within (see `000060`,
   `000032`)? Still open. Everything below is scoped differently depending on the answer.
2. **Write the governing REQ/PLAN**, turning this document plus `000061`–`000065`, `000053` and
   `000018` into an accepted requirement and implementation plan, per this repo's
   plan-before-code rule. The gate before any schema change lands.
3. **Ship the schema additions as one bundled phase**: the `component_of` link type, the
   `lineage` annotation kind, the classification fields themselves, and `000053`'s
   document-code link targets. All touch `schemas/idea.schema.json`, `src/db/ideas.py`'s
   `fold()`, and `tools/append_idea.py` together — bundling avoids re-touching the same files
   across four separate phases.
4. **Backfill the existing corpus.** The taxonomy's value is entirely coverage-dependent — the
   partition queries it exists for (e.g. every `Strategic Directive` resting on an `Assumption`)
   can't run on an unclassified majority. Shipping the schema without backfilling defers the
   payoff indefinitely.
5. **Build the classification agent (`000062`)** — the mechanism for #4, and for every idea
   captured after it.
6. **Build the connection-builder agent (`000055`)**, extended to own `component_of`
   maintenance and tagging as already scoped in its own body. Depends on #3; works alongside #5.
7. **Tagging system (`000018`)** — PLAN-017 deferred this pending "60 captured ideas or a
   recorded failed retrieval." The corpus crossed 60 during this same design conversation; the
   deferral condition is no longer speculative. Can run in parallel with #5/#6 — additive
   metadata, not structural.
8. **`000053`'s document-code link targets** — bundled into #3 for convenience, but genuinely
   independent: a different axis (link *target* shape) from node classification or link *type*,
   so it isn't blocked by the rest of #3 if sequencing needs to split.
9. **Decomposition procedure (`000065`)** — write once `component_of` exists and there's a real
   backlog worth decomposing. `000004` ("three related ideas recorded together... the overlap is
   the useful information") already reads like a live candidate compound idea to test the
   procedure against.
10. **The unrelated umbrella ideas from the prior triage session** (`000054` observability,
    `000056` documentation governance, `000057` testing strategy, `000058`/`000059` version
    control and git, `000060` memory and context management) — real, already-triaged gaps, but
    orthogonal to this design thread. Lowest priority only in sequencing, not in importance.

## Related

- `000061` — the idea this document was written from (ontological/epistemic/lifecycle taxonomy)
- `000018` — tagging and plan-mapping system for ideas (the additive-metadata sibling this
  taxonomy is deliberately not another instance of)
- `000053` — idea-to-document links (the other pending schema extension to the idea system)
- `000055` — a connection-builder agent for the full idea corpus (relationship/tag maintenance;
  contrast with the pure-classification agent proposed above, which does neither)
- `000062` — a pure classification agent (contrast with `000055`, which does neither
  classification nor tagging)
- `000063` — the composition/abstraction relationship model resolved above (`component_of`
  added, `forked_from` dropped as a link type)
- `000064` — a lineage annotation kind, replacing `forked_from`
- `000065` — a decomposition procedure for compound ideas that don't hold together as one node
- `000032`, `000060` — provenance and memory-lifecycle ideas that already gesture at a graph
  layer broader than the idea log alone
