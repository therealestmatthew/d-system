---
schema_version: 1
id: doc-prompt-pack-methodology
code: ADR-017
title: The two-session prompt-pack methodology is the standard for multi-agent builds
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-governance, sys-backlog]
depends_on: [doc-prompt-pack-protocol]
---

# The two-session prompt-pack methodology is the standard for multi-agent builds

## Decision

Multi-agent builds in this repository follow the prompt-pack planning protocol
([GOV-008](../08-governance/GOV-008-prompt-pack-protocol.md)): a planning session manufactures
a governed **prompt pack** — requirement, decisions, plan, backlog phases, roster deltas,
delegation pack, coordinator prompt, kick-off record — through the eight-stage pipeline with
its adversarial gates, and a separate build session spends the pack via verbatim dispatch.
The owner ratified this on 2026-09-10.

## Context

The pattern was used twice before it was named: the live demo build (factory `PROMPT-010`,
pack `PROMPT-018`, coordinator `PROMPT-014`) and the workbench build (pre-plan package
`PROMPT-020`, pack `PROMPT-021`, coordinator `PROMPT-022`, kick-off record `PROMPT-023`).
Both runs delivered on schedule with the two-fix-cycle cap and the `GOV-003` completion gate,
and both adversarial audit stages caught real defects before execution — the workbench pack
audit alone surfaced five (commit `804c6c7`), including a dispatch plan the claim validator
would have rejected mid-build. `PROMPT-010` had already observed the shape was reusable; this
record makes it the standard rather than a precedent to rediscover.

## Terms fixed by this decision

- The artifact set is a **prompt pack**, never a "workbench" — that word belongs to the UI
  product (`REQ-007`).
- **Prompt A** (the pre-plan package) and **Prompt B** (the pack-factory prompt) are separate
  governed documents; the adversarial review + synthesis + owner sign-off gate between B's
  drafting and B's execution is mandatory.
- The final artifacts are the **coordinator prompt** (generic, idempotent, governed), the
  **kick-off record** (per-build owner deltas and starting state, governed, wins over the
  coordinator prompt where they differ), and the **kick-off paragraph** (the single pasteable
  paragraph delivered in chat — the only untracked artifact; its durable copy is the kick-off
  record's final section).

## Consequences

- Future builds do not re-derive the procedure; deviations from `GOV-008` are per-build deltas
  recorded in the kick-off record, not silent judgment calls.
- The standing rules travel with the protocol: selective injection, agent hygiene, the cost
  policy (haiku for mechanical gates, Sonnet standard, opus at most one documented escalation),
  the up-front gate check-in question, and owner-only descope.
- The demo-era prompt documents remain active as precedent and as live children of their packs;
  nothing is superseded.
