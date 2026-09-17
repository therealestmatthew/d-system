---
schema_version: 1
id: doc-claude-code-dependency
code: ADR-021
title: This repository needs an agent runner, not Claude Code specifically
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-17'
updated: '2026-09-17'
systems: [sys-delivery, sys-governance]
depends_on: [doc-agent-surface-audit, doc-portable-agent-workflows]
---

# This repository needs an agent runner, not Claude Code specifically

## Context

Idea `000069` asked whether this repository still needs Claude Code specifically once `PLAN-020`
(`doc-portable-agent-workflows`) makes `.claude/` generated output, or whether it needs *an* agent
runner with Claude Code as one interchangeable option. `phase-agx-02`'s audit
([GOV-015](../08-governance/GOV-015-agent-surface-audit.md)) was the work that reads every file
under `.claude/` and judges it, and the plan (`PLAN-031`) rules that this question is decided in the
same sitting rather than in a phase of its own, because asking it separately would mean reading all
of `.claude/` twice.

Idea `000069`'s own verification bar: "the question is answered when there is a written decision (an
ADR) naming what is kept, what is dropped, and which capabilities have no equivalent elsewhere — not
when someone deletes a directory." This document is that decision. `REQ-016` R05 requires the ruling
to be decided rather than deferred, and to state what would change the answer.

Two pieces of evidence make this decidable now rather than premature, which the idea itself flagged
as a live risk ("the honest answer today may be 'revisit when phase-port-01 and its siblings are
complete'"):

1. **`phase-port-02` already shipped Codex equivalents for 7 of the repository's substantive
   governed workflows**, confirmed tracked by `git ls-files` during the audit:
   `.codex/agents/idea-triage.toml` and `.agents/skills/{backlog, checkpoint, idea, idea-triage,
   log-anti-patterns, orient}/SKILL.md`, generated from the same `agent-workflows/*.md` sources that
   generate the `.claude/` versions. Portability is not a future question for the workflows that
   actually run this repository day to day; it is already built and in the tree.
2. **A real Codex session was run against this repository** to establish what it can actually do
   rather than inferring it (`docs/00-working/codex-capability-probe-response.md`). Its claims are
   tagged `[demonstrated]`, `[documented]`, or `[uncertain]` by Codex itself; this decision treats
   only `[demonstrated]` and `[documented]` claims as evidence, per the audit's instruction to weigh
   the probe rather than restate it.

## Decision

**This repository needs an agent runner, not Claude Code specifically.** Claude Code remains the
repository's actual, current runner — nothing here directs a migration — but that is because it
carries the deepest existing investment (the demo kit; most of `.claude/` is hand-authored, not
generated), not because the repository's governed operation is structurally bound to it.

### What is kept — genuinely Claude-Code-specific, by deliberate choice

- **The entire demo kit**: every `demo-*` agent, `demo-cmd-*` command, `demo-skill-*` skill, and the
  `.claude/prompts/rung-*` and `anti-pattern-gallery.md` presenter scripts. These are built to be
  shown live inside a Claude Code session, using Claude-Code-specific mechanisms — the
  `AskUserQuestion` tool's recommended-option affordance, the `Agent` tool's named sub-agent roster.
  No attempt was made to port them, and none is needed: their entire purpose is presentational for
  this harness in front of a live audience, which is a one-time, deliberate choice rather than
  evidence that the repository's *ongoing* operation depends on Claude Code. If the demo kit ever
  stopped being a one-time presentational artifact and became part of ongoing operation, this
  boundary would need to be redrawn — see the triggers below.
- **Exact numeric turn-budget enforcement.** `maxTurns` on every Claude agent definition, and any
  future exact-context-percentage protocol `phase-agx-01` (`000077`'s truncation-cap work) produces,
  has no Codex equivalent today. Codex enforces no per-agent turn or token budget natively — the
  probe states this as `[documented]`, and `.codex/agents/idea-triage.toml`'s own comment already
  records that Codex cannot enforce Claude's 30-turn cap.

### What is dropped, or has no clean equivalent, if Codex were used instead

- **`/session-close`'s status as a registered, host-native slash command.** Codex can read and
  follow `.claude/commands/session-close.md` as a plain authorized procedure, but it is not
  registered as a Codex command — there is no native equivalent of "a command a person types, which
  is why an agent cannot reach the completion decision." The owner-only guard this protects survives
  as **policy** (an authorization requirement Codex's developer instructions can state and Codex can
  honor), not as a mechanism enforced by the harness itself the way a Claude slash command is.
- **Exact-percentage context-budget stopping.** Codex exposes no remaining-context counter at all
  (`[documented]`), so a protocol written around a numeric threshold ("stop at 10% context
  remaining") cannot be followed literally under Codex; it needs milestone-based handoffs instead.
- **Five-way concurrent sub-agent fan-out.** Codex's concurrency limit is four agents total including
  the coordinator (`[documented]`), so at most three workers run alongside it. Any design that
  assumes five parallel workers — none currently exists in this repository's governed protocols, but
  the constraint is worth stating because `GOV-006`'s batch guidance says "up to four" questions,
  close enough to this boundary to be worth naming — breaks under Codex without redesign.

### What was verified as already working, and is therefore not a gap

- Context-isolated sub-agents, nested dispatch, and per-dispatch model selection — all
  `[demonstrated]`.
- Resuming both a *completed* and, notably, an *interrupted* agent with context intact —
  `[demonstrated]`. This satisfies `GOV-013`'s resume-never-re-run rule directly and is a genuine
  capability, not merely a documented claim.
- `AGENTS.md` auto-injected at session start, without the agent needing to discover the file itself
  — `[documented]`, and independently `[demonstrated]` when the probe session then read the file
  directly on request.

## What would change this answer

This decision reverses — back toward "Claude Code stays exclusively" — if any of the following
happens:

1. **A live attempt, not a probe, to run this repository's actual worktree-and-claim protocol under
   Codex** — after fixing `.codex/config.toml`'s sandbox roots to grant the mandated sibling-worktree
   path — **still fails** on approval-escalation gates for ordinary git operations (commits, branch
   creation, worktree creation) that the protocol requires to run without a human approving each one.
   The probe's own sandbox findings here are `[documented]`, not `[demonstrated]`; nobody has actually
   tried this yet.
2. **A governed protocol is written that genuinely depends on exactly four simultaneous structured
   choices, or on an exact context-remaining percentage**, in a way that milestone-based batching-to-
   three cannot satisfy. None exists today.
3. **The demo kit stops being a one-time presentational artifact** and the owner decides its
   mechanisms (the live interview pattern, the adversarial-panel synthesis) need to run unattended or
   under a different runner as part of ongoing operation, rather than in front of a live audience
   inside a Claude Code session.

## Consequences

- `PLAN-020`'s portability work is validated rather than merely aspirational: the seven workflows it
  already generates for both hosts are the evidence this decision rests on, and any future workflow
  added to `agent-workflows/workflows.yaml` should continue to target both hosts by default.
- The demo kit under `.claude/` (agents, commands, skills, prompts) is explicitly *not* subject to
  future porting work under this decision — it is scoped out by design, not overlooked.
- `phase-agx-01`'s truncation-cap work should record, alongside its own findings, that any signal it
  proposes must be understood as Claude-Code-only unless a Codex-side equivalent is separately
  established; this decision does not do that work for it.
- No change to `AGENTS.md` or `CLAUDE.md` is made or implied by this decision. Both already state the
  working agreement in framework-agnostic terms; nothing here contradicts that.
