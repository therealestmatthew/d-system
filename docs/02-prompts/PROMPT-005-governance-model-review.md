---
schema_version: 1
id: doc-governance-model-prompt
code: PROMPT-005
title: Investigate whether governance is a system, a kind, or both
kind: prompt
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-contracts]
depends_on: [doc-governance-protocol]
---

# Investigate whether governance is a system, a kind, or both

## How to use this

Open a fresh session in this repository and say:

> Read `docs/02-prompts/PROMPT-005-governance-model-review.md` and follow it.

This is a **narrow investigation**, not a build session. It ends with **one ADR** and, if that ADR
changes anything, backlog phases to carry it out. It should not end with a new schema written
speculatively.

Run it after [PROMPT-004](PROMPT-004-terminology-and-architecture.md), which supplies the vocabulary
and the architecture picture this question needs.

## The question

Governance currently exists in two forms at once, and nobody has decided whether that is right:

- **As a document kind.** `governance` and `operation` are both registered in
  `docs/08-governance/`, producing `GOV-*` and `OPS-*` series.
- **As a system.** `sys-governance` is an entry in `systems.yaml` like any other subsystem.

The owner's framing is worth testing directly: *maybe governance is simply a type of system, and
everything governance-related is contained within it.* If that holds, some of the current structure
is redundant. If it does not, the reason it does not is worth writing down.

## What is already known

These were established on 2026-09-06 as a starting point. **Re-read the front matter before relying
on them** — an earlier version of this table omitted `GOV-003` and misdescribed `GOV-002`.

**Governance documents already scope to subsystems.** The `systems` field carries it today:

| Document | `systems` |
|---|---|
| `GOV-001-protocol` | `[sys-governance]` |
| `GOV-002-backlog-protocol` | `[sys-backlog, sys-governance]` |
| `GOV-003-backlog-decisions` | `[sys-backlog, sys-projection, sys-html, sys-memory-agents]` |
| `GOV-004-backlog-capture` | `[sys-backlog]` |
| `GOV-005-document-codes` | `[sys-governance]` |
| `OPS-001-operations` | `[sys-governance, sys-delivery]` |

So the distinction is **already representable and already used** — but it is not a clean partition.
`GOV-002` carries both scopes and `GOV-003` carries four systems and no governance scope at all. Any
proposal to add structure must explain what the field does not capture, and must handle `GOV-003`.

## The questions to answer

1. **Is `governance` a kind, a system, or both — and does the overlap cost anything?** State what
   breaks if either representation is removed. If nothing breaks, remove one.

2. **What do governance documents need that plans and ADRs do not?** This is the field question. One
   candidate is already identified: **nothing currently distinguishes a rule the governance check
   mechanically enforces from a rule that is convention only.** A reader cannot tell whether
   violating `GOV-002` fails a check or merely disappoints someone. Decide whether that gap is worth
   a field, and if so whether it belongs on all documents or only governance ones.

3. **Why do `governance` and `operation` both exist?** Both live in `docs/08-governance/`. Find a real
   `OPS-*` document and a real `GOV-*` document and state what would have been lost had they been
   filed as the same kind. If nothing, merge them.

4. **Should subsystems carry their own operating rules?** The owner raised that individual systems —
   and tools — may need governance of their own. Test it against a concrete case: does `sys-backlog`
   need rules that are not already in `GOV-002` and `GOV-004`? Answer from the real documents, not in
   principle.

5. **Does `systems.yaml` want a `governed_by` field?** If subsystem governance is real, the link may
   belong on the system rather than being discoverable only by searching document front matter.
   Decide, and say what query it makes possible that is impossible today.

## Constraints

- **Do not write a schema this session.** If one is needed, the ADR says so and a phase builds it.
  Three scope-creep corrections on 2026-09-06 came from building structure ahead of demonstrated
  need.
- **Bias toward removal.** The default answer to "should we add a field" is no, unless a question
  someone actually asked cannot be answered without it.
- **Every claim cites a real document.** This repository has enough governance to check arguments
  against, so arguments from principle are not needed.

## What to produce

- **One ADR** answering all five questions, including the ones answered "leave it alone" — those get
  re-litigated otherwise.
- **Backlog phases** for any change the ADR decides on.
- **Terms for the glossary** if the investigation sharpens any definition — governance vocabulary
  belongs in the same generated glossary as everything else, per
  [PLAN-012](../01-plans/PLAN-012-terminology-system.md).
