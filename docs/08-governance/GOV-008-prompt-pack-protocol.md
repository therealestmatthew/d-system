---
schema_version: 1
id: doc-prompt-pack-protocol
code: GOV-008
title: Prompt-pack planning protocol — the two-session methodology for multi-agent builds
kind: governance
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems: [sys-governance, sys-backlog]
depends_on: []
---

# Prompt-pack planning protocol — the two-session methodology for multi-agent builds

A **prompt pack** is the complete governed artifact set a multi-agent build runs from: a
requirement, decision records, a plan, backlog phases, agent-roster deltas, a delegation pack of
pre-crafted prompts, a coordinator prompt and a kick-off record. This document is the standard
procedure for manufacturing one. It was extracted from the two builds that proved it — the live
demo (`PROMPT-010`..`PROMPT-018`) and the workbench (`PROMPT-020`..`PROMPT-023`) — and its
adoption is recorded in the prompt-pack methodology decision
([ADR-017](../04-decisions/ADR-017-prompt-pack-methodology.md)).

The core split: a **planning session** manufactures the pack; a separate **build session**
spends it. Nothing is authored mid-build — if the planning session did not write it, the build
session does not send it. The word for the artifact set is always *prompt pack*; it is never
called a workbench (that word belongs to the UI product, `REQ-007`).

## The pipeline

Eight stages, each ending at a gate. Owner sign-off at a gate means the stage's artifact is
frozen; later changes go through the same gate again.

### 1. Prompt A — the pre-plan package

A governed prompt document (precedent: the workbench pre-plan package, `PROMPT-020`), planned
**interactively with the owner** — AskUserQuestion batches, one at a time, at the point each
question matters. It carries:

- the owner's **ratified decisions**, marked explicitly as do-not-re-ask;
- the **feature inventory** — the owner's specification, itemized;
- the **open-questions list** the later planning session must resolve with the owner;
- **standing constraints** (governance rules that bind the build) and **deadline context**.

### 2. Prompt B — the pack-factory prompt

A **separate** governed prompt document (precedent: the demo agent factory, `PROMPT-010`),
drafted by executing Prompt A. Its purpose: investigate the repository and write the prompt
pack — the system of prompts and prompt components that function together. Prompt A is the
owner's input; Prompt B is the machine that turns it into artifacts. They are never one
document: the gate between them is real.

### 3. Gate — adversarial review of Prompt B

An adversarial, opinionated agent audits Prompt B against Prompt A and repository reality,
assuming it is broken and hunting for where it fails when executed. Findings are synthesized
into fixes, and the owner signs off on the revised Prompt B before it runs.

### 4. Execute Prompt B — draft the pack files

**First in plan mode; auto execution only after the owner confirms the plan.** The output is
the pack body:

- requirement rows with observable verification methods (browser-verification rows in the
  established validator style where the deliverable has a UI);
- decision records for every boundary the build needs settled;
- a plan with **backlog phases sized one session each**, dependency-ordered, encoded in
  `depends_on` rather than left to judgment;
- agent-roster deltas — extend existing charters where possible; new agents only with cause;
- the **delegation pack**: per-phase sections in the established shape — kickoff (`K`),
  creator/validator pairs (`C*`/`V*`), phase gate (`G`), adversarial review (`A`), browser
  verification (`W`) — each idempotent and dispatchable verbatim;
- the **descope ladder**, ordered for the actual runway.

### 5. Gate — adversarial audit of the pack

A second adversarial agent audits the finished pack files (precedent: the five-finding
workbench pack audit, commit `804c6c7`, which caught a validator-rejected parallel dispatch and
an unverifiable assertion). Findings are synthesized, fixes committed, and the governance check
exits 0 before the pack is called done.

### 6. The coordinator prompt

A governed prompt document (precedent: `PROMPT-014`, `PROMPT-022`): preflight, the phase graph,
the completion gate, integration, close-out. Written **generic and idempotent** — the same
prompt whether the build takes one session or several, so every re-run is a resume. Per-build
owner rulings do not go here; they go in the kick-off record.

### 7. Gate — owner sign-off on the coordinator prompt

Adversarial review at this gate is **optional and run only if the owner specifically requests
it** — the pack audit in stage 5 already covered the substance.

### 8. The kick-off record, then the kick-off paragraph

The **kick-off record** is a governed prompt document (precedent: `PROMPT-023`) carrying:

- the owner's **per-build ratified deltas** — integration cadence, descope authority, any
  special lanes (the workbench build's bounded enhancement lane is the model) — gathered via
  AskUserQuestion with recommendations before writing;
- the **pinned starting state** (queue state, peer claims, deadline);
- the precedence rule: **where the kick-off record and the coordinator prompt differ, the
  kick-off record wins**;
- the **kick-off paragraph** as its final section.

The **kick-off paragraph** is the single paragraph referencing everything, delivered **in
chat** so the owner can paste it into the fresh terminal without hunting for files. It is the
one artifact that is never governed and never tracked — its durable copy lives inside the
kick-off record; the chat delivery is a convenience copy.

## Standing rules for every pack

### Selective injection

Context is loaded when the step that needs it begins, never up front. Short parent documents
defer to children; the coordinator prompt defers the phase protocol and guardrails; the
delegation pack is dispatched verbatim one section at a time. Nothing front-loads the full pack
into any agent's opening context.

### Agent hygiene

- The coordinator claims nothing, writes no code, authors no prompts, and never does a worker's
  job. A missing prompt is a blocking finding for the owner, never something to improvise.
- One worktree per phase with fixed ports; claim budgets and path locks are checked
  **numerically** before claiming — the conflicts column says nothing about the budget.
- Peers' claims and fenced paths are never touched; `AGENTS.md`/`CLAUDE.md` are never edited.
- Validators receive the diff, the requirement text and the verification commands — never the
  creator's rationale.
- Commit before validate; truncated agents are resumed, not re-run; an orchestrator's assertion
  is verified against real output before anyone acts on it.

### Cost protocols

- Haiku for mechanical gates. **Sonnet is the standard model for judgment work.** Opus is never
  pre-assigned and is used at most as a single documented escalation per build, only when
  absolutely necessary.
- At most two fix cycles per work item; what survives them is reported, not looped on.
- Close-out reports spend posture: loop counts, any escalation, wall-clock against the runway.

### Gate check-in policy

Prompt A's open-questions list **always asks the owner up front** whether the build session
should stop at gates for check-in or push through to close-out; the answer is recorded in the
kick-off record, not assumed. Whatever the answer, a **critical issue** — a design or
functionality impact prohibitively expensive to defer — first gets a dual review: an
adversarial, opinionated agent challenges the finding and attempts a solution. The build pauses
for the owner only if the issue survives that review unresolved. A failing check is a result to
record, never a step to retry until quiet.

### Descope

The pack drafts the descope ladder for emergencies, but no rung is taken without the owner's
explicit direction unless the kick-off record grants a stated exception.

## Template appendix — required sections per artifact

**Prompt A (pre-plan package)**: ratified decisions (do-not-re-ask) · feature inventory ·
what the planning session must produce, in order · open questions for the owner · standing
constraints · deadline context · the prompt block that drafts Prompt B.

**Prompt B (pack-factory prompt)**: role statement and hard scope limits (documents only) ·
preflight (governance green, peer claims) · the pack artifacts to produce, in order, with the
document codes drawn from `--next-code` · the open-questions protocol (AskUserQuestion, batched,
at the point each matters) · stop condition (pack exists, governance 0, owner has the review
summary).

**Delegation-pack phase section**: `K` kickoff (claim, worktree, ports, item order) · `C*`
creators and `V*` validators in pairs · `G` phase gate (verification commands, real output) ·
`A` adversarial review · `W` browser verification where the phase has a UI.

**Coordinator prompt**: coordinator-only role statement · preflight (governance, budget check,
clean checkout, tooling smoke) · phase graph with dispatch order and the locks that force it ·
completion gate and integration terms · close-out (checkpoint, spend posture, resume state).

**Kick-off record**: starting state · owner-ratified deltas with the precedence rule · the
kick-off paragraph.
