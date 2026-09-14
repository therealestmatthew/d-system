---
id: mem-proc-document-observed-symptoms
title: Document the Symptom You Observed, Not the One You Inferred
type: procedure
tags: [agentic-systems, ai-tools, knowledge-base]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-14
updated: 2026-09-14
confidence: high
related: [mem-proc-runtime-behavior-needs-runtime-evidence, mem-proc-check-that-cannot-fail, mem-proc-verify-before-claiming-ignorance]
scope: global
---

## The rule

When you write down what a failure **looks like** — in a README, a runbook, a troubleshooting
section, an error-message table — open the code that produces that appearance and read it. A
symptom description is a factual claim about a rendered surface. It is not an inference you are
entitled to draw from a correct diagnosis of the cause.

Diagnosing the cause and describing the symptom are two separate claims with two separate
evidence requirements. Getting the first right does not license the second.

## Worked example (2026-09-13)

The owner could not start the demo app. The diagnosis was correct and was verified in the source:
the frontend process was missing two environment variables, so the dev-server proxy fell back to a
port where an unrelated service was listening, and every API call returned 404.

The documentation written from that diagnosis said the failure shows up as **"empty
Commands/Skills/Prompts/Agents dropdowns"**. That sentence came from the owner's own words
("none of the prompts or skills are visible") plus the observed 404. No component file was opened.
An independent reviewer opened them:

- The dropdowns are not empty. The terminal-unavailable state disables them, so they render as
  greyed-out buttons labelled `(terminal absent)` and cannot be opened at all.
- One of the four named dropdowns was not proxy-fed at all. It reads a static JSON asset and goes
  dark for an unrelated reason, so listing it alongside the others implied a shared cause that did
  not exist.

A presenter matching that text against the screen would have seen something that did not match,
while holding a document that told them what to expect. The wrong-symptom text is worse than no
text: it invites the reader to reject a correct diagnosis because the described appearance is
absent.

## The tell

The slip has a recognisable shape: the user reports a *perception* ("nothing is visible", "it's
blank", "the list is empty"), you confirm a *cause* at a layer below it (a 404, a missing
variable), and you then write the user's perception into a document as if it were the verified
symptom. The user's words are a report from one glance at one state, not a specification of what
the UI does. They are the starting point of the investigation, not its output.

## The procedure

- Before writing a symptom into a document, find the code path that renders it. Grep the literal
  string the document will quote; read the branch that produces it.
- Quote the exact user-visible text — the real label, the real message — rather than paraphrasing
  it. A reader matching a paraphrase against a screen cannot tell a mismatch from a typo.
- When several symptoms are listed as one cause's effects, check each one's source separately.
  Symptoms that appear together are not necessarily caused together.
- If the code cannot be read or run, say what was observed and by whom ("the owner reported ...")
  instead of promoting it to a verified symptom.

## Why this is model-agnostic

Any agent that diagnoses from logs, status codes and user reports has everything it needs to be
confident about the cause and nothing it needs to be right about the appearance. The pull toward
writing the vivid, user-supplied wording is strongest exactly when the diagnosis was hard and
correct — which is when the documentation is most likely to be trusted and least likely to be
re-checked.
