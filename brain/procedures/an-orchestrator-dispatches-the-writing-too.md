---
id: mem-proc-an-orchestrator-dispatches-the-writing-too
title: An Orchestrator Dispatches the Writing Too
type: procedure
tags: [agentic-systems, ai-tools]
project: d-system
created: 2026-10-08
updated: 2026-10-08
confidence: high
related: [mem-proc-summarize-before-you-dispatch, mem-proc-scope-dispatches-to-the-turn-budget]
scope: global
---

## The rule

An orchestrating session that has dispatched research agents does not then write the deliverables
itself. It dispatches creator agents, with the returned research as their brief. The session's own
tools write only commits and verification output.

The orchestrator reads its tracker, the summaries agents return, and command output. Agents read the
source files and write the deliverables (`GOV-013`, "Context discipline is the coordinator's whole job").

## What happened (2026-10-08, cloud session on one branch)

A cloud session on branch `claude/productivity-system-templates-ie1x8d` was asked to orchestrate four
pieces of work, using Haiku subagents by default. It dispatched two read-only research agents, which
was correct. It then wrote the deliverables itself: the governance document `GOV-022` (about 360
lines), the guide page `_public/portfolio-guide.html` (about 760 lines), two scripts, and sixteen idea
files. The owner corrected it: "function as orchestrator only, primarily to keep your context clean and
properly utilize subagents."

The returned research should have briefed creator agents, not become files the session wrote. The
owner ruled the same day that `GOV-022` carries this rule ("The session writes no deliverable").

## The tell

The slip is happening when either of these is true:

- The session is composing a file longer than the brief that would produce it.
- The session is re-reading source files that an agent has already summarised.

When either appears, stop writing. Write a brief for a creator agent and dispatch it.

## The procedure

- **Brief each deliverable.** The brief names the deliverable, the research it builds on, and the
  path the creator writes to. Pass a source file by path only when the creator must read it in full
  (see `mem-proc-summarize-before-you-dispatch`).
- **One creator per deliverable.** Each creator writes its own file and returns a bounded report: a
  verdict and the path. `GOV-013` caps returns at fifteen lines.
- **Corrections go back to the creator** as a new dispatch, not as an edit by the session.
- **A stopped creator is resumed, not replaced.** An agent that stops with no file written is
  truncated. Resume it; do not take over its file.

## Why this is model-agnostic and durable

The rule names no tool and no model. It applies to any session that dispatches agents and also holds
a write tool. The slip comes from a habit: the research is already in context, so finishing the file
looks cheaper than writing a brief. Each file written in the session adds its full text to that context.
