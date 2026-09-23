---
id: mem-proc-verify-a-cause-before-you-report-it
title: Verify a Cause Before You Report It
type: procedure
tags: [agentic-systems, ai-tools, knowledge-base]
source_model: anthropic/claude-opus-5-5
project: d-system
created: 2026-09-23
updated: 2026-09-23
confidence: high
related: [mem-proc-document-observed-symptoms, mem-proc-runtime-behavior-needs-runtime-evidence, mem-proc-verify-before-claiming-ignorance]
scope: global
---

## The rule

When you tell someone why something happened, whether the owner, a coordinating session or a
session record, state as fact only the cause you have checked. If the check is cheap, run it
before you send the message. If you cannot run it yet, write the cause as a hypothesis and name the
check that would settle it.

A cause reported as fact changes what other people do. They reassign a fix, ask for a restart, or
stop looking. That is the reason it needs the same evidence as a test result.

## Worked example (2026-09-23, phase-part-03)

The same session made this slip twice.

1. **An inferred cause stated as observed.** After a rebase, two catalog tests failed. The branch
   did not touch the backlog or the catalog, and dev's newest commit had changed the backlog
   without regenerating the catalog. The session's merge request to the Session Manager said "The
   same two tests fail on dev without my changes." It had not run them on dev. The claim was true:
   a throwaway worktree at dev's tip then gave `2 failed, 59 passed`. But the claim went out first,
   and the session had to send a second message to say it was now verified.
2. **One observation generalised into a rule of the platform.** Right after a new agent type was
   merged, one dispatch to it failed with "Agent type ... not found". The session reported that the
   tool loads agent types only at session start, sent BLOCKED, and asked for a restart. A few
   minutes later the harness listed the new type as available in the same session. The failure was
   real, but the stated cause was wrong: the type was picked up after a delay. A restart had been
   asked for on the strength of that claim.

In both cases the evidence was one step away. The first needed a test run in a throwaway
worktree. The second needed a wait and a second attempt, or a documentation lookup.

## The tell

You have one observation, and a sentence forms that explains it in general terms: "X fails because
Y", "the tool only does Z when ...". Ask yourself which part of that sentence you saw and which part
you inferred. The inferred part is a hypothesis until it is checked.

## The procedure

- Before sending a cause, write down the check that would show it. If the check is cheap, run it
  first and quote its output in the message.
- If you cannot run it yet, label the cause: "likely", "not yet verified", "the check is ...".
- A single failed attempt shows that it failed once. Before reporting a limitation of a tool,
  retry after a short wait, or read the tool's documentation.
- If you have already sent an unverified cause, send the verification or the correction as soon as
  you have it, and say plainly which one it is.

## Why this is model-agnostic

Any agent that reports to other agents or to a person turns an observation into an explanation.
Doing that before the check is a habit of the reporting step, not of any one model or tool. The
entry names no model's tools.
