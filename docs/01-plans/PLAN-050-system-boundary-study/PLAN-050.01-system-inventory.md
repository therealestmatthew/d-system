---
schema_version: 1
id: doc-system-boundary-study-system-inventory
code: PLAN-050.01
title: System boundary study — system ownership and interface inventory
kind: plan
status: draft
owner: repository-owner
created: '2026-09-26'
updated: '2026-09-26'
systems: [sys-gov-docs]
depends_on: [doc-system-boundary-study, doc-system-boundary-study-requirements]
parent: doc-system-boundary-study
---

# System ownership and interface inventory

## Context and scope

`phase-bnd-01` establishes the evidence base for the boundary study. It inventories every system
in `systems.yaml`, including those outside the three target concerns, without altering the registry
or reading private content.

## Approach

Use one explicit disposition per registered system: personal-productivity core, idea-realization
core, workbench core, cross-cutting framework, shared foundation, adjacent, incubating, legacy, or
retired. Record source authority, writers, readers, interfaces, evidence, and unknowns. Unknown is
an evidence state, not a disposition.

## Work and dependencies

Record the baseline revision, read the registry and named tracked paths, write the inventory and
current-boundary map, then check that every registry entry appears exactly once. This is the first
phase and has no prerequisite phase.

## Requirement coverage

R01 and R02 are delivered directly; R07 is met by the baseline and evidence citations.

## Acceptance and verification

The inventory covers the whole registry and the map labels each proposed crossing and at least one
negative ownership rule per boundary. Run governance, compare the inventory with `systems.yaml` at
the recorded revision, and run `git diff --check`.

## Out of scope

Changing `systems.yaml`, deciding an extraction, or auditing private data.

## Open questions

None. Any ambiguous classification is recorded as an unknown for the synthesis phase.
