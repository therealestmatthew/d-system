---
schema_version: 1
id: doc-organizational-and-wbs-data-model
code: ARCH-007
title: Organizational identity, project parties, engagements and WBS data model
kind: architecture
status: draft
owner: repository-owner
created: '2026-09-17'
updated: '2026-09-17'
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
files, and represent unresolved names without pretending they are canonical identities. Each
relationship has exactly one role and has start/end dates, so responsibility changes are historical
rather than overwrites.

Roles are data-driven rather than one universal enum. A reusable role catalog supplies common roles;
each project may define additional roles with descriptions, required/optional status, and expected
quantity. Optional project `scale` and `complexity` metadata can guide which roles apply, but their
controlled vocabulary and consumers must be defined before they become validation inputs. Existing
`project.stakeholders` and `person.projects` fields are migration inputs, not long-term parallel
authorities.

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
engagement by itself. The governed plan must choose whether an engagement begins at a qualified
opportunity, a mutual intent/authorization point, contract signature, or another recorded event.
Pre-engagement prospect activity belongs to sales or interaction records and may later be linked to
the engagement without changing its start date.

`Contract` will be a separate schema for agreements, amendments, statements of work, and their
parties, dates, status, and references. `Template` will be a separate schema for reusable document,
process, or delivery patterns; a template is not a contract or an engagement and may be versioned
and instantiated by either. Their exact legal, commercial, and content boundaries remain plan
decisions.

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
a validated party reference or an unresolved captured name, never an ambiguous mixture. Unresolved
names remain text until identity is confirmed. Person-specific semantics are preserved where a
company cannot meaningfully act as the subject.

## Source and projection boundary

The JSON and Markdown source records remain authoritative. New entity directories and schemas will
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

New contracts are expected for `company`, `company-relationship`, `affiliation`, `person-alias`,
`project-party`, `role-definition`, `engagement`, `engagement-project`, `contract`, `template`,
`glossary-term`, `wbs-element`, and
`wbs-change` (with baseline metadata placement still to be decided). Existing project, person,
commitment, task, waiting-on, interaction, decision, and development-event contracts will be
updated in dependent phases.

## Explicit non-goals

- Building the MDM system or MDM stewardship agent in this effort.
- Implementing a full corporate registry, tax/address master, or contract repository.
- Making WBS codes a substitute for task IDs, schedules, or financial accounting structures.
- Retaining duplicated project/person relationship fields as independent authorities.

## Open decisions for the governed plan

- Exact company kinds, statuses, legal identifier/jurisdiction rules, and external identifier shapes.
- Alias uniqueness, normalization, shared values, conflict handling, and privacy rules.
- The canonical polymorphic party-reference shape and its cross-file/database validation rules.
- Temporal convention: inclusive/exclusive bounds, open-ended intervals, overlap rules, and assertion timestamps.
- Role-definition versioning, assignment overlap/cardinality rules, and warning versus blocking validation.
- Engagement versus engagement-party semantics and date/status propagation.
- Engagement start trigger and lifecycle boundary relative to prospecting, qualification,
  authorization, and contract signing.
- Contract and template scope, versioning, party links, and their relationship to engagements.
- The schema registry/governance model for every durable object, including schema versioning,
  mappings, derived projections, and validation ownership.
- Glossary-term structure and its lineage links to schemas, decisions, plans, and implementation.
- The WBS change fold, code/version rules, structural invariants, atomic writer convention, and baseline pinning.
- Which existing records may reference companies and how unresolved counterparties are represented.
- Migration fixtures, precedence/count checks, ambiguity output, and backward compatibility requirements.
