---
id: mem-concept-terms-organizational-schema-system
title: Organizational and Schema-System Terms
type: concept
tags: [knowledge-base, frameworks]
systems: [sys-contracts, sys-portfolio, sys-governance, sys-brain]
source_model: openai/gpt-5
project: d-system
created: 2026-09-17
updated: 2026-09-23
confidence: high
related: [mem-concept-terms-data-and-storage, mem-concept-terms-plans-and-work]
scope: global
---

Definitions from the organizational, engagement, WBS, and governed-schema architecture discussion.

### Company

A first-class organization record. A legal entity, brand, division, or team is represented as its
own company record when it has distinct operational or legal identity. Not a synonym for a person,
engagement, or project.

### Legal entity

An organization with a distinct legally recognized identity. Operational divisions, teams and brands
are not automatically legal entities. Legal identity is modeled separately from display names.

### Prospect

A potential client or counterparty. A prospect can participate in an opportunity before an engagement
exists; the party and pipeline record have separate identities.

### Prospecting

The outreach, qualification, and discovery activity directed at prospects. Prospecting may produce
an opportunity but does not establish an engagement.

### Opportunity

A potential engagement before qualified mutual intent to pursue or authorize work. It is a pipeline
record, distinct from the prospect party and from the later engagement.

### Engagement

The commercial or delivery relationship that officially begins at **qualified mutual intent to
pursue or authorize work, before contract signature**. An engagement may contain projects and
non-project work such as retainers, advisory support, and operational requests.

### Business contract

An agreement or related formal commercial document, including proposals, statements of work,
amendments, renewals, or termination records. Multiple business contracts may belong to one
engagement. It is not a data contract or programming contract.

### Data contract

A machine-readable agreement describing a data object's shape, required properties, validation,
ownership, compatibility, and versioning. It is to be governed by the schema registry (planned, not
yet built), not by the business-contract schema.

### Programming contract

Executable interface expectations such as inputs, outputs, preconditions, postconditions, and
invariants. It may reference a data contract but is not a business contract.

### Template

A reusable, versioned document, process, or delivery pattern. A template is not a contract,
engagement, or instantiated project.

Objects created from a template retain the exact version used. Applying a later template revision
is an explicit action that preserves the original derivation history.

### Document asset

A record describing a business file, its versions, and its storage locations, including PDFs,
signed agreements, and externally hosted documents. The planned `document-asset` schema governs
this metadata; the existing `document` schema governs repository documentation.

### Document link

A typed relationship between an object and a supporting document, recording the relationship's
meaning and provenance.

### External reference

A provider-scoped identifier or URL associated with a target object and validity dates, such as
an external CRM record ID or a document URL.

### Project

A bounded delivery effort organized around an objective, schedule, parties, roles, scope, and
outcomes. A project may participate in multiple engagements.

### Project party

A person or company participating in a project through a dated, role-bearing relationship. The
record may capture a person's representation through a particular affiliation.

### Affiliation

A time-bounded relationship connecting a person to a company, such as employment, contracting, or
advisory association. A person may have multiple simultaneous affiliations.

### Person alias

A typed, time-bounded identity value associated with one person, such as an email address used in a
particular organizational context. Aliases preserve one human identity across changing addresses.

### Work Breakdown Structure (WBS)

A hierarchical decomposition of the complete project scope into progressively smaller elements,
including workstreams, deliverables, and work packages. It is distinct from a schedule, organization
chart, or accounting structure.

### WBS element

One node in a project's WBS hierarchy. Elements have immutable identities, readable versioned codes,
types, scope descriptions, and optional responsibility; work packages are normal task attachment
points.

### Work package

A leaf-level WBS element sufficiently defined for planning, assigning responsibility, estimating,
and linking executable work.

### WBS baseline

An approved representation of WBS scope pinned to a replay position and integrity evidence so later
structural changes can be identified.

### Schema-governed object

A durable object whose identity, properties, lifecycle, provenance, validation, and relationships
are defined by one authoritative schema. Derived projections are not independent authorities.

### Schema mapping

An explicit relationship that maps properties or identities among governed schemas, enabling joins,
analysis, and mathematical processing without relying on duplicated free text.

### Global identity

An immutable, collision-resistant, system-wide identifier allocated by the identity registry. It is
separate from readable domain codes such as six-digit idea identifiers.

### Shared analytical dimension

A semantically compatible property through which different schemas can be analyzed together,
such as effective date. Sharing a dimension does not by itself establish a relationship between
individual records; mappings must define the property's meaning and compatibility.

### Tag assignment

A governed relationship connecting an object to a tag, with provenance. A shared `tag-assignment`
schema is planned to supply the assignment authority across object types; it does not exist yet (see
`docs/07-architecture/ARCH-008-schema-catalog.md`). Today a project's tags are a plain
`tags` array.

### Effective time and recorded time

Effective time describes when a fact applied in the world; recorded time describes when the system
learned that fact. Preserving both allows a correction entered today to describe a role change
that took effect last month while retaining what was known before the correction.

### Resolved record

The deterministic result of folding immutable original events and their amendments through a
specified event position, following the idea-log pattern. Subsequent amendments can produce a new
current view without erasing the original evidence or earlier resolved views.

### Amendment behavior

The schema-declared method for changing an existing object: fold immutable events and amendments,
or validate a complete replacement record under the same stable identity. History retention is
declared separately; replacement alone does not guarantee historical reconstruction.

### Record multiplicity

Whether a schema permits one or multiple eligible records for a specified business key and context.
It is independent of amendment behavior. One person may hold concurrent roles or repeat a role in
different periods, with each assignment carrying its own identity and effective dates.

### Role assignment occurrence

One dated tenure in a role for a person or party within an organizational or project context.
Returning to the same role creates another occurrence; correcting a tenure's dates amends the
existing occurrence. Context-specific rules govern whether intervals may overlap.

### Conflict resolution event

For event-backed schemas, an explicit decision resolving incompatible amendments while preserving
the conflicting events and the resolution's provenance. Independent amendments may combine;
arrival order alone does not settle semantic conflicts.

### Identity registry

The planned authority for allocating global object identities and recording domain-code aliases,
resolution, supersession, merges and splits. IDs are never reused. Existing document-code allocation
continues to supply human-facing document codes linked to those identities.

### Schema registry

The planned foundational register of data contracts, versions, ownership, compatibility, mappings,
validation and migrations. Each schema declares amendment behavior, history retention and record
multiplicity. Object identities are managed by the separate identity registry.

### Provisional party

A durable unresolved identity record holding captured names, provenance, confidence and review
state. It may later resolve to a person or company while retaining its earlier evidence.

### Party reference (PartyRef)

A shared typed reference to a person, company or provisional party, with affiliation context when
representation is known. It must validate its target and mutually exclusive alternatives.

### Opportunity party and engagement party

Separate dated participation records for an opportunity or engagement, carrying role,
representation and provenance. Multiple people or companies can participate in each context.

### Company relationship

A directed, typed relationship between organizational identities with effective dates and
provenance, such as ownership, control, organizational hierarchy or succession.

### Role definition

A reusable or project-specific specification of participation responsibilities, permitted party
types, required status, cardinality and overlap rules. Project type, scale and complexity guide
the set of roles without hard-coding one global staffing pattern.

### Workstream

A grouping of related project scope within the WBS. Workstream membership alone does not define
execution order or a dependency.

### Deliverable

A defined output or result of work. A WBS may organize scope around deliverables, distinct from
the executable tasks used to produce them.

### Control account

An optional WBS management grouping for monitoring scope and associated performance. Its detailed
use and allowed position in this system remain design decisions.

### WBS code and WBS change

A WBS code is a readable, versioned hierarchical label for an element with a stable internal ID.
A WBS change is an immutable event recording a structural or scope amendment from which current
WBS state can be reconstructed. Moves may explicitly change codes while preserving prior labels.

### Work dependency

A directed temporal or technical dependency between typed work endpoints, such as tasks,
commitments, WBS elements or projects. Its type and provenance are governed independently of
the WBS parent-child hierarchy.

### Engagement-project and engagement-contract

Explicit relationship records connecting engagements to projects or business contracts. Both
relationships are many-to-many; a master agreement may cover several engagements.

### Event envelope and domain payload

Shared event metadata records identity, actor, effective/recorded times and amendment references;
a typed, versioned domain payload specifies the operation. The reusable envelope need not be a
separately stored object. Exact fields remain part of the event-contract design.

### Master data management (MDM)

Management of authoritative identities and shared data through quality rules, stewardship,
resolution, provenance and lifecycle controls. The full MDM system and its dedicated stewardship
agent are parked ideas; current identity governance establishes a foundation for them.

### Idea classification axes

Ontological classification describes what an idea concerns or is; epistemic classification
describes its knowledge/evidence standing; temporal classification describes its time-related
context. These axes are distinct from workflow state. Their exact values, links, tags and
transition rules remain the subject of idea 000268.
