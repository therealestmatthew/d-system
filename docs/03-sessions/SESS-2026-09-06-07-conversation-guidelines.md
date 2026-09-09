---
schema_version: 1
id: doc-session-conversation-guidelines
code: SESS-2026-09-06-07
title: Conversation guidelines and the CLAUDE.md import
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance]
depends_on: [doc-governance-protocol, doc-conversation-guidelines]
---

# Conversation guidelines and the CLAUDE.md import

Owner-directed work outside any claimed phase, which is why this record exists — unphased work is
invisible to the backlog otherwise. No phase was claimed and no worktree was used; the change is
documentation only, with no peer claim outstanding, which is the condition
[GOV-003](../08-governance/GOV-003-backlog-decisions.md) allows the primary checkout under.

## What prompted it

The owner said that phase and document codes — `phase-ses-01`, `ADR-007` — carry no meaning without
opening a file, and asked for a better way to talk about them. The naming rule was settled first,
then the question of where a rule about *conversation* belongs, given that `AGENTS.md` governs work
product.

## Outcome

[GOV-006](../08-governance/GOV-006-conversation-guidelines.md) states four rules: name things before
citing their code, show output that carries information, do not block on a question that can wait,
and say plainly when a correction is a correction. It is deliberately short, because it is imported
into every session and therefore costs context on every turn.

`CLAUDE.md` imports it with `@docs/08-governance/GOV-006-conversation-guidelines.md`. `AGENTS.md`
carries a plain link for agents that do not read `CLAUDE.md`.

## Why an import rather than a link

`CLAUDE.md` is loaded automatically; `AGENTS.md` is not. It is read because `CLAUDE.md` instructs an
agent to read it and the agent complies — an act of compliance, not a load. Verified this session:
`CLAUDE.md` was in context without being opened, `AGENTS.md` had to be read.

A work rule tolerates that. It is needed before a phase is claimed, which is minutes in. A rule about
how an agent addresses the owner governs the first sentence, and a two-hop reference would be opened
after several messages had already broken it. The failure mode is not a broken reference; it is a
rule that arrives too late to have applied.

The import stays consistent with `CLAUDE.md`'s own rule that it holds pointers rather than copies:
`GOV-006` remains the only copy, so it stays correct when it changes. This is the first `@` import in
the repository.

## Deviations from AGENTS.md, and a correction to my own advice

The requirement-and-plan-before-code step was skipped. I raised it; the owner judged a plan
disproportionate for a single short document and directed the file be written directly. Recorded
here rather than left for a later reader to infer.

I also proposed folding the conversational rules already in `AGENTS.md` — "Report outcomes honestly.
A failing check is a result to record, not a step to retry until quiet" — into `GOV-006`, and did
not. `AGENTS.md`'s structure is a declared deliverable of `phase-ses-02`, `-03`, `-04` and
`phase-rel-09`; moving text out of it now would collide with work already scoped. `GOV-006` cites
that rule instead of restating it, which avoids the duplication without touching the section.

Two of my own claims were wrong and the owner corrected both. I said the owner's instinct to
reference the document from `CLAUDE.md` rather than `AGENTS.md` was inverted, on the grounds that
`AGENTS.md` has wider cross-vendor reach. That answers a question about reach, not about what is in
context when the first sentence is written — and on that, the owner's original position was right,
as the loading behaviour above confirms. I also framed the context cost of an `@` import as a
drawback, when importing a concise document costs exactly what inlining the same content costs; the
cost is the content, and the mechanism is what buys a single source of truth.

## Verification

- `uv run python -m src.governance` — exit 0; 45 documents.
- `uv run pytest` — 264 passed.

## Unresolved

- **The import is unverified in practice.** It takes effect at the start of the next session; this
  one had already loaded `CLAUDE.md` before the line existed. The first agent to open a session here
  should confirm `GOV-006` arrives in context without reading it, and say so if it does not.
- ~~`phase-gov-01` has no row in the backlog track glossary.~~ Fixed in this session at the owner's
  direction. Adding it surfaced a second stale row: `phase-cap-*` cited only the discovery plan
  (PLAN-007) while its nine current phases come from the build plan (PLAN-009). Corrected in the
  same edit, since leaving a known-wrong row in a navigation table while adding another would send
  a reader to the wrong plan.
- **A personal memory recording this rule was written and then deleted.** Once `CLAUDE.md` imports
  `GOV-006`, a separate memory restating it is duplicate bookkeeping that can drift out of agreement
  with the document.
