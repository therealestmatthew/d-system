---
schema_version: 1
id: doc-prompt-demo-guardrails
code: PROMPT-016
title: Demo pack — guardrails, budgets and escalation
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems:
- sys-governance
depends_on:
- doc-prompt-demo-build-orchestration
---

# Demo pack — guardrails, budgets and escalation

Child of the build orchestration prompt ([PROMPT-014](PROMPT-014-demo-build-orchestration.md)).
Binding on the coordinator and every agent it dispatches.

## Time and the descope ladder

The build budget is 6–8 hours of wall clock. At every phase boundary the coordinator compares
elapsed time against plan. When behind, it executes the next rung of the ladder **on its own
authority** and reports the cut — it does not negotiate first, because the ladder was agreed with
the owner in advance:

1. Overview charts become tables (drop chart rendering, keep the numbers).
2. The talking-points rotator loses transitions — static text, manual cycling.
3. The embedded overview panel becomes an open-in-new-tab link.
4. The embedded terminal is cut; the rehearsed side-by-side real terminal is the demo.

The live pipeline story — idea → triage → plan → agents build the skill → test — survives every
rung and is never cut.

## Loop and spend limits

- Creator→validator: at most **two** fix cycles per work item, then the orchestrator judges, then
  it reports up. A third quiet retry is forbidden.
- **Opus escalation, once**: the coordinator may re-run exactly one failed work item on opus, only
  after two failed sonnet attempts with validator findings attached, and must report it. There is
  no second escalation; the second failure of that kind goes to the owner.
- Two phases exhausting their loop caps is a stop-and-report signal for the whole build, not a
  reason to push on.
- Truncated agent output: resume the agent, never re-run (idea `000077`).

## Safety fences

- The permission fences in `.claude/settings.json` (from the factory session) stay in place; if a
  fence blocks something an agent legitimately needs, that is an owner question, not a reason to
  remove the fence.
- The terminal route exists only behind `D_SYSTEM_DEMO_TERMINAL=1`, binds to 127.0.0.1, and is
  never registered unconditionally. Its ADR is the contract.
- Ports 8010/5180 only. Never assume 8000/5173.
- Never push `--force`; never rewrite pushed history; pushing `agent/*` branches is free,
  integration into `dev` is owner-approved.
- Validator blindness: validators receive diff + requirement + commands, never creator rationale.

## When to ask the owner

Ask (AskUserQuestion) only when the answer changes what gets built and the pack does not already
answer it: integration approvals, a rung-4 descope (report rungs 1–3, ask before 4 — it changes
the demo's shape), a blocked fence, a missing delegation prompt, or a conflict with the peer.
Everything else: state the assumption, keep working, surface it in the close-out report.
