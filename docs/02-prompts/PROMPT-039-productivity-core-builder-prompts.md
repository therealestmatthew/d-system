---
schema_version: 1
id: doc-prompt-productivity-core-builder-prompts
code: PROMPT-039
title: Productivity core builder prompts — portfolio seeding and the specification phases
kind: prompt
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-portfolio, sys-capture]
depends_on: [doc-productivity-core-enhancements, doc-multi-session-coordination-protocol, doc-build-coordinator]
---

# Productivity core builder prompts

Two prompts for phases in [PLAN-044](../01-plans/PLAN-044-productivity-core-enhancements.md) that
need more than `/session-start` and the phase's own lines. Every other `PLAN-044` phase is an
ordinary build phase: a Builder runs it through `/session-start` on `ASSIGN`, and the Batch Runner
runs it through `PROMPT-036` in `batch-007` or `batch-008`.

Both prompts are pasted by the owner into a Builder session after the Session Manager sends
`ASSIGN`, and after Prompt Planner has sent `PROMPT-FOR` so the Session Manager can check the prompt
against that session's role and slot ([GOV-017](../08-governance/GOV-017-multi-session-coordination-protocol.md)).

## Seeding the portfolio (`phase-cap-08`)

The owner takes part in this session: the captures are their own working notes.

```text
You are building phase-cap-08 (seed the portfolio through the capture pipeline). Read the phase in
docs/09-backlog/backlog.yaml and its entry in GOV-003 before starting.

1. Run /session-start for phase-cap-08. Claim only inside a granted turn (TURN? claim phase-cap-08).
   Tests never run in the primary checkout: run the preflight pytest in your worktree.
2. The real records go to the primary checkout's private root. Set
   D_SYSTEM_DATA_ROOT=/code/d-system/_private/portfolio on each capture, promotion, rebuild and
   governance command. Never export it, and never use a relative path: a relative path resolves
   inside the worktree and promotion would create a root there that worktree removal deletes.
   Run uv run pytest and the leak check with it unset.
3. Ask me for the working period to capture. Take the notes I give you through intake,
   structuring, review and promotion. Promotion is my action at each step: show me what is staged
   and wait for my decision. Do not author records by hand.
4. Do not read _private/portfolio/ beyond what the pipeline itself reads. Write only row counts in
   the session record, never names or record content, and read the record for project and person
   names before you commit it. In the worktree the leak check cannot check content (000150).
5. Before removing the worktree, copy _capture/ back into /code/d-system/_capture/ and confirm the
   raw and promoted entry counts match.
6. Run /session-close up to its independent review, then send READY to the Session Manager.
```

## Specification phases (`phase-pc-03` to `phase-pc-09`)

The same text for each, with the phase id filled in. These phases build nothing.

```text
You are running <phase-id>, a specification phase from PLAN-044. It writes documents and backlog
phases only; it builds no code. Read the phase in docs/09-backlog/backlog.yaml, PLAN-044, and the
idea it names through src.db.ideas.fold(), including its triage findings.

1. Run /session-start for the phase. Claim only inside a granted turn. Tests never run in the
   primary checkout.
2. List the design questions the phase names and any you find while reading. Put them to me in
   batches with AskUserQuestion, each with a recommendation. Do not settle a question that changes
   what gets built by assumption.
3. Write the requirement with observable statements and a verification method for each row.
   Allocate codes with uv run python -m src.governance --next-code <kind>.
4. Add session-sized build phases, each with scope, acceptance, verification, systems and
   deliverables. Map every requirement row to at least one phase. Register any new prefix in
   docs/09-backlog/README.md. Record my answers in GOV-003.
5. For phase-pc-07 to phase-pc-09: record each ARCH-010 gate's decision in ARCH-010's Remaining work
   table. phase-pc-09 also writes the organisational model's requirement and plan and runs the
   adversarial review ARCH-010 names.
6. Run /session-close up to its independent review, then send READY to the Session Manager.
```
