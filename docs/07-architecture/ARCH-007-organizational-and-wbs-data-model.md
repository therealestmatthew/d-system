---
schema_version: 1
id: doc-organizational-and-wbs-data-model
code: ARCH-007
title: Organizational identity, project parties, engagements and WBS data model
kind: architecture
status: draft
owner: repository-owner
created: '2026-09-17'
updated: '2026-09-18'
systems: [sys-contracts, sys-portfolio, sys-capture, sys-governance]
depends_on: [doc-architecture-overview, doc-structure-content-boundary]
---

# Organizational identity, project parties, engagements and WBS data model

This is a high-level architecture proposal from the 2026-09-17 schema-design discussion. It
describes the intended shape and boundaries; it does not claim that the schemas, loader, database,
or migrations exist.

## Design objective

Represent organizations, people, organizational capacity, commercial engagements, project roles,
and project scope without conflating legal identity, human identity, delivery responsibility, or
execution tasks. Preserve historical relationships when people change roles, companies change
legal form, or project scope changes.

## Identity model

Each legal or operational organization is a distinct `Company` record, with an explicit kind that
distinguishes legal entities from brands, divisions, and teams. A holding company, client,
consulting company, and spun-off legal entity therefore have separate stable IDs. A separate
`CompanyRelationship` record expresses directed parent/subsidiary, holding/spin-off,
successor/predecessor, client/vendor, and similar relationships with dates, notes, cycle rules,
and succession semantics.

`Person` remains the canonical individual identity. An `Affiliation` connects a person to a
company and carries organizational role, title, start/end dates, status, and notes. A person may
have several simultaneous or historical affiliations.

`PersonAlias` records typed identity values—especially email addresses—rather than embedding a
string list in `Person`. An alias may reference an affiliation, carry validity dates and current or
primary state, and resolve multiple organizational addresses to one person.

Aliases carry normalized values, organizational context, provenance, and review state. Shared or
reused addresses are permitted subject to explicit validation rules; matching an email alone must
not merge people. Normalization algorithms and primary-status scope remain implementation decisions.

```text
Person
  └── Affiliation ── Company
          └── PersonAlias
```

This model treats legal entities as separate records and keeps MDM automation and a dedicated MDM
stewardship agent out of the current build. It does not defer identity governance entirely: the MVP
needs immutable IDs, explicit unresolved/confirmed/rejected/superseded states, manual merge/split
records, provenance, confidence, and explicit owner approval. The future MDM initiative may automate
or centralize that stewardship; this work establishes the contracts it would later govern.

## Project participation and roles

Projects are connected to people and companies through `ProjectParty` records. A project party may
identify a company, a person, or a person acting through a specific affiliation. The canonical
`PartyRef` shape must make those alternatives mutually exclusive, validate every target across
files, and reference a first-class provisional party when identity is unresolved rather than
pretending a captured name is canonical. Each
relationship has exactly one role and has start/end dates, so responsibility changes are historical
rather than overwrites.

Roles are data-driven rather than one universal enum. A reusable role catalog supplies common roles;
each project may define additional roles with descriptions, required/optional status, and expected
quantity. Optional project `scale` and `complexity` metadata can guide which roles apply, but their
controlled vocabulary and consumers must be defined before they become validation inputs. Existing
`project.stakeholders` and `person.projects` fields are migration inputs, not long-term parallel
authorities.

Role rules are configurable by project type and project, including allowed party types,
required/optional status, cardinality, and assignment overlap. During migration the new relationship
records become authoritative; legacy stakeholder and person-project fields are generated for a
temporary compatibility period, measured for usage, and retired in an explicit later phase.

```text
Project ──< ProjectParty >── Person
                    └────── Company
                    └────── Affiliation (when representation is known)
Project ──< ProjectRoleDefinition ──< ProjectParty
```

The same party can have multiple roles on one project, represented by multiple relationship
records. This supports delivery companies, clients, sponsors, vendors, partners, advisors, and
project-specific roles.

## Commercial engagement model

An `Engagement` represents the broader commercial relationship, assignment, statement of work, or
contract context. It may connect companies, people, dates, status, and optional contract/SOW
references. Engagements and projects have a many-to-many relationship with relationship-level dates
and notes, allowing amendments, multiple SOWs, and projects spanning legal entities. An engagement
may also contain non-project work such as retainers, advisory support, and operational requests;
the eventual work-item contract will distinguish those from bounded projects.

An engagement is not a replacement for a project: it answers “under what commercial relationship is
this work being delivered?” while the project answers “what outcome is being pursued?”

The lifecycle boundary is intentionally explicit: a prospect or sales conversation is not an
engagement by itself. An engagement officially begins at **qualified mutual intent to pursue or
authorize work, before contract signature**. Pre-engagement prospect activity belongs to sales or
interaction records and may later be linked to the engagement without changing its start date. This
definition is the source wording for the future glossary term `Engagement`.

`BusinessContract` will be a separate schema for agreements, amendments, statements of work, and
their parties, dates, status, and references. It is distinct from a `DataContract` (the
machine-readable agreement governed by `schema-registry`) and a `ProgrammingContract` (executable
interface expectations and invariants). `Template` will be a separate schema for reusable document,
process, or delivery patterns; a template is not a contract or an engagement and may be versioned
and instantiated by either. Their exact legal, commercial, and content boundaries remain plan
decisions.

Business file metadata, versions, and locations belong to `document-asset`; repository documentation
continues to use the existing `document` contract. Template instances retain their originating
template version, and later revisions are applied explicitly with derivation history preserved.
Tasks and commitments may reference engagements directly with no project required, supporting
non-project advisory and retainer work through the existing execution objects.

## Work Breakdown Structure

Each project may have a tree of `WBSElement` records. An element is any node: root, workstream,
deliverable, work package, or (if needed) control account. Summary nodes organize scope; leaf work
packages are the normal attachment point for executable tasks.

Each element has an immutable internal ID, a versioned dotted WBS code, one parent at most, type,
scope/deliverable description, lifecycle fields, and an optional responsible `ProjectParty`.
Element IDs are authoritative. Codes are readable labels whose history is retained; a move may
change a code and descendant codes only through an explicit change event, and a retired code is not
silently reused. WBS elements are not schedules: temporal or technical dependencies remain separate
from the hierarchy.

Tasks and commitments may reference a WBS element. A task remains an independent execution record;
the WBS does not replace it. A commitment may reference a work package when the promise is scoped
that specifically.

The current WBS is a deterministic projection of append-only `WBSChange` records, not a second
independent authority. Change events have immutable IDs, actor, effective timestamp, sequence/order,
and enough payload to replay the tree. Baselines pin an event sequence, content hash, or immutable
snapshot so the approved scope is provable. The fold rejects divergence between current state and
history. This follows the PMI principles that a WBS should represent the complete project scope,
decompose it into useful levels of detail, assign clear responsibility, and support baseline/change
control; it remains distinct from an organization chart, schedule, or financial breakdown.

```text
Project
  └── 1.0 Root outcome
       ├── 1.1 Workstream
       │    └── 1.1.1 Work package ──< Task
       └── 1.2 Deliverable ──────────< Commitment
```

## Counterparty generalization

Where the meaning permits, commitments, waiting-on records, interactions, and decisions should use
the same structured person/company `PartyRef` rather than person-only fields. A record must use either
a validated party reference or a first-class provisional party reference, never an ambiguous mixture.
Provisional parties retain captured names, provenance, confidence, and review state until resolved,
merged, or rejected. Person-specific semantics are preserved where a
company cannot meaningfully act as the subject.

## Source and projection boundary

For schemas choosing event history, historical corrections follow the immutable idea-log pattern:
original events plus targeted
amendments fold deterministically into the current resolved record. Both effective time and
recorded time are retained so late corrections preserve what applied and what was known. This
decision establishes correction semantics; the per-schema event storage design remains planning
work. The owner's 2026-09-18 clarification also permits full-record replacement on amendment,
without event chaining, under a declared per-schema history-retention policy. Each schema specifies
record multiplicity independently: recurring or concurrent role assignments are distinct dated
records with separate identities, while corrections amend the affected assignment. Role/context
rules determine valid overlaps. See ARCH-008's amendment and multiplicity policies.
Shared analytical dimensions are cataloged separately from explicit record relationships.
Cross-object tags use authoritative `tag-assignment` records with provenance.

The registered JSON, JSONL, YAML, and Markdown source records remain authoritative. New entity directories and schemas will
be validated by the source preflight, then projected into DuckDB by the rebuild process. Join and
history tables will represent relationships and append-only changes. Cross-record resolution rules
(for example, whether a referenced company or affiliation exists) belong in source validation and
loader checks, with database integrity checks where practical, not in an isolated JSON Schema.
Updates to current WBS state and its event history must be atomic at the writer/commit boundary;
rebuild rejects a current/history mismatch.

The long-term knowledge-system rule is that every durable object has an authoritative schema. A
schema defines the object's identity, properties, lifecycle, validation, provenance, and allowed
relationships; mappings among governed objects create analyzable data. Derived projections may
exist, but their source schema and rebuild rule must be explicit. A structured `GlossaryTerm`
schema will govern vocabulary entries, including definitions, synonyms, related terms,
authoritative schema references, distinctions, lifecycle state, and lineage links. The glossary
remains conceptual and relational rather than becoming a field-by-field manual.

## Planned schema families

The current schema log is [ARCH-008](ARCH-008-schema-catalog.md). It includes the accepted
`engagement-contract` many-to-many relationship, typed `document-link` records with provenance,
and provider-scoped `external-reference` records with validity dates.

New contracts are expected for `identity-registry`, `company`, `company-relationship`, `affiliation`,
`person-alias`, `project-party`, `role-definition`, `opportunity`, `engagement`,
`engagement-project`, `business-contract`, `template`, `glossary-term`, `wbs-element`, and
`wbs-change`, and `wbs-baseline`. Separate `opportunity-party` and `engagement-party` schemas
hold participant relationships; `work-dependency` holds temporal and technical dependency links.
The foundational `schema-registry` and `schema-mapping` govern these data contracts, with
`provisional-party` providing durable unresolved identities. Existing project, person,
commitment, task, waiting-on, interaction, decision, and development-event contracts will be
updated in dependent phases.

## Explicit non-goals

- Building the MDM system or MDM stewardship agent in this effort.
- Implementing a full corporate registry, tax/address master, or contract repository.
- Making WBS codes a substitute for task IDs, schedules, or financial accounting structures.
- Retaining duplicated project/person relationship fields as independent authorities.

## Decision reconciliation and remaining work

[ARCH-010](ARCH-010-schema-decision-reconciliation.md) records accepted decisions, superseded
alternatives, idea lineage, and genuinely unresolved design work. ARCH-008 is the current schema
log. Earlier open questions about engagement start, half-open dates, provisional parties, template
version pinning, registry separation, and migration compatibility are settled there.

WBS source requested by the owner: [PMI, Work Breakdown Structure basic principles](https://www.pmi.org/learning/library/work-breakdown-structure-basic-principles-4883).
