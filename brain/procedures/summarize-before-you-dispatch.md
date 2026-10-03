---
id: mem-proc-summarize-before-you-dispatch
title: Summarize Before You Dispatch
type: procedure
tags: [agentic-systems, ai-tools, prompt-engineering]
source_model: anthropic/claude-opus-5-5
project: d-system
created: 2026-10-03
updated: 2026-10-03
confidence: high
related: [mem-proc-scope-dispatches-to-the-turn-budget]
scope: global
---

## The rule

Before dispatching an agent with a file or a body of results, check whether the agent needs the
full content for its analysis. If it does not, summarize first, then pass only the summaries.
The summary can come from the main context, from another agent, or from a script that extracts
the fields that matter. Pass a file in full only when the analysis depends on its full text.

(Owner's direction, 2026-10-03: "it should always be checked if the agent needs the full context
of a file for analysis or if the file can be summarized either by the main context or another
agent first and then provide just the summaries.")

## What happened (2026-10-01 to 2026-10-03, release-export analysis)

A workflow analysed 37 removable bundles of dev data, with one analysis, one empirical proof and
one adversarial challenge per bundle. Each later stage received the earlier stages' full JSON
inline in its prompt. The final design agent was written to receive all 37 specs in one prompt,
about 1.3 MB. The owner's weekly budget was nearly spent, so the design was not run that way.

A script then cut the input to the fields the design needs: about 93 KB for the six bundles the
owner had named, plus a 27 KB index of the other 31. That is about a tenth of the original, and
the script cost no model tokens.

## The procedure

- **Before every dispatch, ask:** does this agent need the whole file, or only what the file says
  about its question? Most synthesis, design and review steps need only the second.
- **Prefer the cheapest summarizer that is good enough:**
  1. a script that extracts named fields from structured data (JSON, YAML): no model tokens;
  2. the main context, when it already holds the material;
  3. a summarizer agent, when the material is prose and too large for the main context.
- **Pass paths, not content,** for files the agent must read in full. It then reads only what it
  needs and nothing is pasted twice.
- **Measure what you inline.** Check the byte size of any prompt that embeds data. If it is more
  than a few tens of kilobytes, stop and summarize.
- **In multi-stage workflows,** give each stage the fields the next stage uses, not the previous
  stage's whole return value.
