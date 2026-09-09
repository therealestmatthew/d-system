---
id: mem-proc-verify-before-claiming-ignorance
title: Verify Before Claiming Ignorance
type: procedure
tags: [ai-tools, agentic-systems, knowledge-base]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-06
updated: 2026-09-06
confidence: high
related: [mem-proc-add-memory]
scope: global
---

## The rule

Before stating that you do not know something, check whether a tool can settle it. If one can, use
it. Only then answer.

"Not in my training data" and "cannot be determined" are different claims. The first is often true.
The second is almost never true of a searchable fact, and asserting it when search was available is
a **false statement about your own capability** — not a limitation, and not honest hedging.

## Triggers

Run a search before answering when the question involves:

- A named model, product, library, framework or version — especially one you do not recognise
- Anything dated after your knowledge cutoff
- Any "is X real?" / "what is X?" question
- Pricing, availability, release status, or current capability of any external tool

Not recognising a name is *itself* the trigger. It is the strongest available signal that the thing
postdates your training, which is precisely the case search exists to cover.

## The near-miss variant

Offering to search **instead of searching** is the same error with better manners:

> "I can't confirm that — let me know if you'd like me to look it up."

If the answer is worth having, get it. Do not convert a two-second lookup into a round trip that
puts the work back on the owner. Offer only when the search is genuinely expensive or the scope is
ambiguous.

## Worked example (2026-09-06)

The owner referred to **GPT-6 Astra**. The response asserted: *"I don't recognise it… I just can't
confirm it or tell you anything useful."* Web search was available and unused.

GPT-6 Astra was real — released 2026-09-03, four months past the assistant's May 2026 cutoff. One
search resolved it, and the result turned out to be **directly relevant to the decision under
discussion** (its computer-use and screen-inspection strengths matter for iterating on rendered
animation output). The unfounded "cannot confirm" did not merely omit a fact; it withheld a
consideration that bore on the owner's tooling choice.

**The generalisable lesson:** the cost of unverified ignorance is rarely just the missing fact. It
is the reasoning downstream of it.

## Why this is model-agnostic

Filed in `brain/` deliberately. Every model working in this repository has some training cutoff and
some tool access, so every model can make this mistake. The correction should not have to be
rediscovered per model.

## Related standing requirement

The owner must not have to issue the same correction twice. See the mistake protocol in `CLAUDE.md`
— a correction that produces no durable artifact did not land.
