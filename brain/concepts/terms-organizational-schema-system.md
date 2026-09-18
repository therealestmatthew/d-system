---
id: mem-concept-terms-organizational-schema-system
title: Organizational and Schema-System Terms
type: concept
tags: [knowledge-base, frameworks]
systems: [sys-contracts, sys-portfolio, sys-governance, sys-brain]
source_model: openai/gpt-5
project: d-system
created: 2026-09-17
updated: 2026-09-17
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

An organization recognized as a distinct legal person or business unit for legal, contractual, or
financial purposes. A legal entity is a kind of company, not merely an alias for a company with a
different name.

### Prospect

A potential client or counterparty before an opportunity is established. Not itself an engagement.

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
ownership, compatibility, and versioning. It is governed by the schema registry, not by the
business-contract schema.

### Programming contract

Executable interface expectations such as inputs, outputs, preconditions, postconditions, and
invariants. It may reference a data contract but is not a business contract.

### Template

A reusable, versioned document, process, or delivery pattern. A template is not a contract,
engagement, or instantiated project.

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
