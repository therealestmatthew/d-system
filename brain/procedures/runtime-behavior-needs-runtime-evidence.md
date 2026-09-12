---
id: mem-proc-runtime-behavior-needs-runtime-evidence
title: Runtime Behavior Needs Runtime Evidence
type: procedure
tags: [agentic-systems, ai-tools, knowledge-base]
source_model: anthropic/claude-fable-5
project: d-system
created: 2026-09-11
updated: 2026-09-11
confidence: high
related: [mem-proc-verify-before-claiming-ignorance]
scope: global
---

## The rule

A gate battery of build, lint, type-check and unit tests proves nothing about whether a page
renders or a session survives an interaction. Any work item whose requirement is **runtime
behavior** — the page loads, a panel fills, a websocket survives a reassignment — must have a
**live check in its loop**, run after each attempt, not only at the phase's end. And the agent
asked to fix runtime behavior must receive **recorded runtime evidence** (measurements taken by
an agent that can observe them), never verify-by-assumption.

## What happened (2026-09-11, phase-wb-09)

Two failures in one phase, same root:

1. **A page-crash blocker survived every scheduled check until the final adversarial gate.** A
   creator with no browser tool introduced an infinite React update loop (a per-render ref
   closure calling setState on every commit). The code validator reviewed the diff and ran
   `npm run build` — clean, because the bug is runtime-only. The mechanical phase gate (build,
   pytest, governance, private-content) — also clean. The stage page rendered **nothing at
   all**, in dev and production builds, and the first check that opened a browser (the
   coordinator's adversarial review) was the first to notice. Every browser-facing acceptance
   item was unverifiable behind it.
2. **A session-kill defect survived two fix attempts** because the creator patched from an
   assumption (React 18 state batching would keep a moved panel alive) instead of from a
   measurement. The instrument that settled it — a websocket open/close lifecycle trace
   correlated with backend logs — existed, but only in the orchestrator's hands, after each
   attempt rather than in front of the next one.

The phase's own pack had already solved this pattern once: phase-wb-08's `W08-M` convention
("measurements are observed by the agent that can observe them, never asserted by one that
cannot") front-loaded live measurements into the creator's dispatch, and that phase's fix landed
first-try. Phase-wb-09's items shipped without an equivalent, and paid two fix cycles plus an
escalation.

## The procedure

- **Pack authoring:** every frontend or runtime-behavior work item gets (a) a cheap browser
  smoke dispatch — page loads on a clean profile, root renders content, no uncaught console
  errors, dev AND production build — runnable after each creator commit, and (b) for stateful
  requirements (sessions, persistence), a named measurement instrument (e.g. websocket
  lifecycle trace) defined in the pack, with the creator prompt required to state the expected
  post-fix trace signature.
- **Fix cycles:** never dispatch a second attempt without attaching the live measurements from
  the first attempt's failure. A creator that cannot observe the runtime states its expected
  measurements and asks for re-verification — same as `W08-M` re-dispatch semantics.
- **Coordinators/orchestrators:** treat "build passes" on frontend work as *compiles*, not
  *works*. If no browser has opened the branch, its runtime claims are unverified — say so in
  reports rather than letting a green mechanical gate imply a working product.

## Why this is durable

The failure mode is structural, not situational: creators without browser tools cannot see
runtime bugs, and every static check is blind to them by construction. Any future phase pairing
a no-browser creator with runtime requirements will reproduce it unless the loop carries live
evidence by design.
