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
| `company` | Legal entities and operational organizations, including brands, divisions, and teams | Planned |
| `company-relationship` | Directed, typed, time-bounded relationships among companies | Planned |
| `affiliation` | A person's time-bounded relationship to a company | Planned |
| `person-alias` | Typed, time-bounded identity values such as email addresses | Planned |
| `project-party` | Person/company participation in a project, with representation context and role | Planned |
| `role-definition` | Reusable and project-specific role rules, cardinality, and requirements | Planned |
| `opportunity` | Potential engagement before qualified mutual intent | Planned |
| `engagement` | Commercial or delivery relationship beginning at qualified mutual intent; may include project and non-project work | Planned |
| `engagement-project` | Explicit dated participation of a project in one or more engagements | Planned |
| `business-contract` | Legal and commercial agreements, proposals, statements of work, amendments, renewals, and termination records | Planned |
| `template` | Reusable versioned document, process, or delivery patterns | Planned |
| `glossary-term` | Structured vocabulary terms, definitions, synonyms, distinctions, and lineage | Planned |
| `wbs-element` | Hierarchical project scope nodes, work packages, codes, and responsibility | Planned |
| `wbs-change` | Append-only WBS structural changes, replay order, provenance, and baseline support | Planned |

## Confirmed relationship rules

- An opportunity precedes an engagement; prospecting is activity, not the engagement itself.
- An engagement begins at **qualified mutual intent to pursue or authorize work, before contract
  signature**.
- An engagement may contain projects and non-project work such as retainers, advisory support, and
  operational requests.
- An engagement may have multiple typed contracts and related documents.
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
- Time-bounded relationships use half-open intervals `[starts_on, ends_on)`.
- Unresolved parties are first-class provisional records with provenance, confidence, and review
  status.
- WBS current state is a validated projection of append-only change events; baselines pin a
  replay position and integrity evidence.
- The schema registry is separate from the identity registry and is implemented as a foundational
  capability before the new domain schemas.
- Schema mappings are separate durable objects with their own identity, lifecycle, compatibility,
  validation status, and lineage.

## Implementation boundary

The catalog records design intent only. Each planned schema requires a governed requirement and plan,
source contract, representative data, cross-record validation, projection/DDL work where needed,
and migration evidence before it can be marked implemented.
