---
schema_version: 1
id: doc-schema-catalog
code: ARCH-008
title: Schema catalog and governed object register
kind: architecture
status: draft
owner: repository-owner
created: '2026-09-17'
updated: '2026-09-17'
systems: [sys-contracts, sys-portfolio, sys-capture, sys-governance]
depends_on: [doc-organizational-and-wbs-data-model, doc-architecture-overview]
---

# Schema catalog and governed object register

This is the repository's schema log. It distinguishes contracts that exist today from contracts
planned by the organizational, engagement, identity, and WBS architecture. A planned entry is not
an implemented capability.

## Governing rule

Every durable object has one authoritative schema defining its identity, properties, lifecycle,
provenance, validation, and permitted relationships. Mappings among governed objects create the
structured data used for analysis and mathematical processing. Derived projections must identify
their source schema and deterministic rebuild rule. The foundational `schema-registry` will make
this catalog machine-readable and will manage schema versions, compatibility, ownership, mappings,
and migrations before the new domain schemas are implemented.

## Existing schema contracts

| Schema | Current role |
|---|---|
| `backlog` | Governed phase queue, statuses, dependencies, acceptance, and verification |
| `capture` | Immutable raw capture records before interpretation |
| `codes` | Governed document-code series, reservations, and retirements |
| `commitment` | Promises and obligations with dates, status, and participants |
| `decision` | Recorded decisions with rationale, status, and evidence |
| `development-event` | Development history and implementation events |
| `document` | Governed Markdown document metadata and lifecycle |
| `evidence` | Provenance and source references attached to records |
| `idea` | Append-only idea lifecycle events and classification fields |
| `idea-priority` | Ordered priority overlay for open or triaged ideas |
| `interaction` | Recorded interactions and their participants/context |
| `memory` | Durable brain memories and their metadata |
| `person` | Canonical individual identities and current portfolio relationships |
| `project` | Bounded work records and project-level metadata |
| `staged-record` | Interpreted capture awaiting promotion or rejection |
| `systems` | System/component responsibilities, paths, and maturity |
| `tag` | Shared controlled taxonomy values |
| `task` | Executable work linked to projects or commitments |
| `waiting-on` | External dependencies and pending responses |
| `workbench-layout` | Workbench panel placement and layout configuration |

## Planned schema contracts

| Schema | Intended authority | Status |
|---|---|---|
| `identity-registry` | System-wide opaque IDs, domain-code mappings, aliases, supersession, merges, and splits | Planned |
| `schema-registry` | Machine-readable schema definitions, versions, ownership, mappings, compatibility, and migrations | Foundational planned |
| `schema-mapping` | Version-aware mappings between schema properties, identities, and transformations | Foundational planned |
| `tag-assignment` | Shared object-to-tag relationships with provenance | Planned |
| `provisional-party` | Unresolved party identity with captured names, provenance, confidence, and resolution lifecycle | Planned |
| `company` | Legal entities and operational organizations, including brands, divisions, and teams | Planned |
| `company-relationship` | Directed, typed, time-bounded relationships among companies | Planned |
| `affiliation` | A person's time-bounded relationship to a company | Planned |
| `person-alias` | Typed, time-bounded identity values such as email addresses | Planned |
| `project-party` | Person/company participation in a project, with representation context and role | Planned |
| `role-definition` | Reusable and project-specific role rules, cardinality, and requirements | Planned |
| `opportunity` | Potential engagement before qualified mutual intent | Planned |
| `opportunity-party` | Opportunity participant roles, dates, representation, provenance, and cardinality | Planned |
| `engagement` | Commercial or delivery relationship beginning at qualified mutual intent; may include project and non-project work | Planned |
| `engagement-party` | Engagement participant roles, dates, representation, provenance, and cardinality | Planned |
| `engagement-project` | Explicit dated participation of a project in one or more engagements | Planned |
| `business-contract` | Legal and commercial agreements, proposals, statements of work, amendments, renewals, and termination records | Planned |
| `engagement-contract` | Explicit many-to-many links between engagements and business contracts | Planned |
| `document-link` | Typed links from objects to supporting documents with provenance | Planned |
| `document-asset` | Business file metadata, versions, and storage locations, including signed agreements and externally hosted documents | Planned |
| `external-reference` | Provider-scoped external identifiers or URLs, target object, and validity dates | Planned |
| `template` | Reusable versioned document, process, or delivery patterns | Planned |
| `glossary-term` | Structured vocabulary terms, definitions, synonyms, distinctions, and lineage | Planned |
| `wbs-element` | Hierarchical project scope nodes, work packages, codes, and responsibility | Planned |
| `wbs-change` | Append-only WBS structural changes, replay order, provenance, and baseline support | Planned |
| `wbs-baseline` | Approved WBS scope with identity, replay anchor or snapshot hash, approval, and supersession history | Planned |
| `work-dependency` | Directed temporal and technical dependencies among typed work endpoints, with dependency type and provenance | Planned |

## Confirmed relationship rules

- An opportunity precedes an engagement; prospecting is activity, not the engagement itself.
- An engagement begins at **qualified mutual intent to pursue or authorize work, before contract
  signature**.
- An engagement may contain projects and non-project work such as retainers, advisory support, and
  operational requests.
- Existing tasks and commitments may link directly to engagements, with projects optional, to
  represent non-project work. This decision does not introduce a separate service-request schema.
- An engagement may have multiple typed contracts and related documents.
- A business contract may cover multiple engagements; `engagement-contract` records the
  many-to-many relationship, including master agreements spanning engagements.
- Supporting-document relationships are separate `document-link` records with relationship type
  and provenance. Business files use `document-asset` for metadata, versions, and locations;
  the existing `document` schema continues to govern repository documentation.
- Objects instantiated from templates retain the exact template version used. Later template
  revisions are applied explicitly, preserving the original derivation history.
- External identifiers and URLs are separate `external-reference` records carrying provider,
  value, target object, and validity dates.
- `business-contract` means literal legal/commercial paperwork. `data-contract` means a
  machine-readable schema agreement, and `programming-contract` means executable interface
  expectations; neither is the business-contract object.
- Engagements and projects are many-to-many through an explicit participation record.
- Existing IDs remain usable as aliases while the identity registry introduces stable prefixed
  opaque IDs. Six-digit idea codes remain idea-domain codes, not the global identity.
- Existing document codes such as PLAN, ADR, ARCH, and REQ remain human-facing domain codes; each
  governed document also receives a global identity linked through the identity registry.
- Human-readable domain codes are assigned only to object types that people routinely reference;
  other durable objects use their global identity alone.
- The initial domain-code set is documents, ideas, projects, engagements, and WBS elements.
  Companies, people, opportunities, contracts, templates, affiliations, aliases, roles, mappings,
  and events initially use global IDs only.
- Opportunities use role-bearing links to multiple people and companies, including unresolved
  provisional parties, rather than a single prospect/contact pair or free-text participants.
- Opportunities use an explicit staged lifecycle with transition history, including identified,
  qualifying, discovery, proposal, qualified_mutual_intent, won, lost, abandoned, and converted
  states (final vocabulary remains a plan decision).
- One opportunity may convert to multiple engagements through explicit conversion links recording
  dates, reasons, and confidence.
- Time-bounded relationships use half-open intervals `[starts_on, ends_on)`.
- Unresolved parties are first-class provisional records with provenance, confidence, and review
  status.
- WBS current state is a validated projection of append-only change events; baselines pin a
  replay position and integrity evidence.
- The schema registry is separate from the identity registry and is implemented as a foundational
  capability before the new domain schemas.
- Schema mappings are separate durable objects with their own identity, lifecycle, compatibility,
  validation status, and lineage.
- Opportunity and engagement participation each have a separate role-bearing junction schema:
  `opportunity-party` and `engagement-party`.
- Each WBS baseline is a separate durable object carrying approval and supersession history.
- Temporal and technical dependencies are first-class `work-dependency` objects connecting typed
  endpoints such as tasks, commitments, WBS elements, and projects.
- Breaking schema changes require explicit new versions, migrations, compatibility notes, and
  old-to-new data validation. Domain stewards propose and validate changes; the repository owner
  approves their architectural and governance impact.

## Shared dimensions and historical corrections

- Shared analytical dimensions and explicit record relationships are distinct link categories.
  A shared date, status, or other property is analytical metadata, not evidence that two records
  are directly related. Mappings must state semantic compatibility before permitting analysis.
- Tags attach through shared `tag-assignment` records identifying the target object, tag, and
  provenance. Existing embedded tag arrays require migration or derived compatibility views;
  they must not become a second authoritative assignment source.
- Historical corrections preserve both effective time (when the fact applied) and recorded time
  (when the system learned it). Original events and amendments remain immutable, following the
  idea event-log pattern; a deterministic fold produces the current resolved record.
- The resolved record is current as of a specified event position, not permanently final. Later
  amendments produce a new resolved view while retaining the earlier evidence. Event ordering,
  amendment targeting, and conflict rules must make replay reproducible, including corrections
  recorded after their effective date.

## Implementation boundary

The catalog records design intent only. Each planned schema requires a governed requirement and plan,
source contract, representative data, cross-record validation, projection/DDL work where needed,
and migration evidence before it can be marked implemented.
