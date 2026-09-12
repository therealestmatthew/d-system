---
id: mem-proc-scope-dispatches-to-the-turn-budget
title: Scope Dispatches to the Turn Budget
type: procedure
tags: [agentic-systems, ai-tools, knowledge-base]
source_model: anthropic/claude-fable-5
project: d-system
created: 2026-09-11
updated: 2026-09-11
confidence: high
related: [mem-proc-runtime-behavior-needs-runtime-evidence]
scope: global
---

## The rule

An agent dispatch is sized wrong when completing it takes more tool calls than one turn allows.
Scope every dispatch so its expected tool-call count fits comfortably inside a single turn, and
when a dispatch must be large, structure it so a truncation loses nothing: evidence recorded as
it is gathered, no long deferred final report, explicit "you will be resumed — never restart
completed checks" framing.

## What happened (2026-09-11, workbench fix build)

Browser-heavy dispatches truncated **seven times across two phases**: the wb-08 diagnosis twice
for the orchestrator (which had no resume tool and burned both dispatches entirely — a blocking
finding), then once more for the coordinator; the wb-08 adversarial review once; the wb-09
browser verification twice (60+ then 130+ tool calls before its report); the escalated creator
once. Every truncation cost a coordinator intervention, and the orchestrator-level ones cost
whole dispatches, because the resume capability lived only at the coordinator.

The pattern behind all of them: pack prompts that bundle a full measurement matrix (three
panels × two layouts × four sizes, plus persistence, plus fallback seeding, plus screenshots)
into one dispatch, with the report due only at the end — maximum work before the first byte of
durable output.

## The procedure

- **Authoring dispatches:** estimate the tool-call cost. A browser matrix multiplies fast
  (panels × layouts × sizes × assertions); split by concern (one dispatch per matrix axis or
  per requirement row) rather than by agent role when the product exceeds roughly half a turn
  budget.
- **Front-load durability:** instruct agents to record results as they go (numbered items,
  pass/fail as measured) so a truncation preserves everything; forbid saving the report to the
  end on large dispatches.
- **Resume, never re-run:** a truncated agent is resumed with its context intact (idea 000077).
  Ensure every orchestrator that dispatches subagents either holds a resume-capable tool or has
  an explicit escalation path to someone who does — an orchestrator without one loses the whole
  dispatch on truncation, as happened twice before the coordinator took over.
- **Tell the agent it will be resumed** in the dispatch itself ("if cut off you will be
  resumed — never restart completed checks"), so the resumed turn continues instead of
  re-verifying from scratch.

## Why this is durable

Turn budgets are a permanent property of dispatched agents, and verification matrices only grow
as the product grows. Any pack authored without a tool-call estimate will reproduce the
truncation cascade; the cost scales with exactly the complexity growth the project intends.
