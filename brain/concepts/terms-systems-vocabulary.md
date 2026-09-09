---
id: mem-concept-terms-systems-vocabulary
title: Systems
type: concept
tags: []
systems: [sys-governance]
source_model: anthropic/claude-sonnet-5
project: d-system
created: 2026-09-07
updated: 2026-09-07
confidence: high
related: [mem-concept-mini-systems]
scope: global
---

Grouped definitions per [PROMPT-004](../../docs/02-prompts/PROMPT-004-terminology-and-architecture.md).

### System

One entry in `docs/08-governance/systems.yaml` — an independently-changeable capability with an
owner, domain, status, dependency list and description. Not a second project portfolio and not a
duplicate of the plan that proposed it — a planned system's `paths` may point at a design document
rather than code. See `docs/08-governance/GOV-001-protocol.md`.

### Subsystem

The informal name for a system when discussing it in relation to the whole repository. Not a separate
tier in `systems.yaml` — there is no subsystem layer below `system`; scoping a query to one subsystem
is done through the memory `systems` field, not through `brain/` folder nesting, which contributes
nothing to retrieval filtering. See `docs/01-plans/PLAN-012-terminology-system.md`.

### Domain

The `domain` field grouping systems by category — `data`, `memory`, `application`, `delivery`,
`governance`. Not a second dependency hierarchy — it is a classification axis for reading the
registry, unrelated to `depends_on`.

### System status

The `status` field on a system entry — `implemented`, `scaffold`, `planned`, or `retired`. Not tied to
its plan's own status: a plan being `approved` or `active` does not make its system `implemented`,
only actual code and observed verification does. See `docs/08-governance/GOV-001-protocol.md`.
