---
schema_version: 1
id: doc-idea-realization-system-plan
code: PLAN-039
title: Idea realization system master plan
kind: plan
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-portfolio, sys-backlog, sys-governance]
depends_on: [doc-idea-realization-system, doc-idea-realization-system-requirements, doc-idea-graph-lifecycle, doc-agent-engineering-delegation, doc-autonomous-agent-operations, doc-repeatable-idea-partition]
---

# Idea realization system master plan

The umbrella plan for idea `000247`. It re-frames four existing programmes as sub-programmes of
one pipeline — the idea graph and lifecycle programme (`PLAN-029`, P1), agent engineering and
delegation (`PLAN-031`, P4), autonomous agent operations (`PLAN-032`, P5) and the repeatable
idea partition (`PLAN-025`) — and holds only the glue those programmes do not build. The
architecture is [ARCH-006](../07-architecture/ARCH-006-idea-realization-system.md); the
requirements are [REQ-022](../06-requirements/REQ-022-idea-realization-system.md); the
orchestration decision is [ADR-018](../04-decisions/ADR-018-langgraph-orchestration.md). The
re-framing itself is recorded in `GOV-003`, because it touches the accepted partition of
2026-09-13.

**Re-framing changes no sub-programme phase.** Their codes, scopes and orderings stand; this
plan adds dependency edges *into* them and builds around them. Sequencing follows the owner's
2026-09-15 ruling: plan now, build the glue as its foundations land, with the stopgap trigger
(`phase-irs-01`) the one piece ruled buildable immediately.

## What each sub-programme supplies

| Sub-programme | Supplies to the pipeline | Status caveat |
|---|---|---|
| `PLAN-029` (P1) | The idea schema bundle (`phase-idg-01`), the plan-quality standard (`phase-idg-10`), the promoted-draft location (`phase-idg-11`), the planner agent (`phase-idg-12`), idea-level decomposition (`phase-idg-05`) | Active |
| `PLAN-031` (P4) | The delegation-scoping methodology, the expander/minimalist/arbiter engine (`phase-agx-11`/`-12`), the anti-pattern store (`phase-agx-03`), claim-protocol recovery (`phase-agx-09`) | Active |
| `PLAN-032` (P5) | The capability/approval broker (`phase-auto-02`), the run ledger, the supervised worker (`phase-auto-05`), the trigger gateway (`phase-auto-03`) — each conditional on the `phase-auto-01` design ruling, which may descope any of them | Active; the most speculative sub-programme, and this plan carries fallbacks for it |
| `PLAN-025` | The partition workflow, prompt pack and corpus selection | **Still `status: draft`**; it must be accepted, and `phase-irs-02` amends its gate structure — both surface at the next G2-category decision |

## De-duplication boundaries

The adversarial pass of 2026-09-15 found the draft architecture double-counting or misapplying
existing work in four places. These boundaries are the corrections, and reviewers should hold
phases to them.

| This plan builds | The sub-programme owns | The line |
|---|---|---|
| Run-level recovery: which stage a run is in, resuming it, parking it | `phase-agx-09`: claim-protocol recovery — stale claims, orphaned worktrees, unwritten findings — for any agent | The orchestrator consumes `phase-agx-09`'s procedures and defines none of its own (`REQ-022` R19) |
| The phase-fit procedure: splitting an oversized **backlog phase** | `phase-idg-05`: decomposing a compound **idea** on the log | Different object, different artifact; neither invokes the other. Stage 4's minimum-scope duty (`phase-idg-12`) is the planner getting it right; stage 6 is the independent check that it did |
| The three-altitude review **procedure** and its findings record | `phase-agx-11`/`-12`: the deliberation **engine** — domain-agnostic breadth/minimalism/arbitration | The procedure runs with a single-adversary engine until the trio ships, then adopts it unchanged in procedure |
| The stopgap dispatch: append → triage agent, plus the reconciling sweep | `phase-auto-03`: the general external trigger gateway, if `phase-auto-01` rules it built | The stopgap is interim by declaration; migration or permanence is decided by the `phase-auto-01` ruling, not by this plan |
| The execution harness's dispatch loop | `phase-auto-05`: the supervised worker host | If the worker is descoped, the fallback is plain Agent SDK dispatch under the unchanged `ADR-003` claim protocol — slower, equally safe |

## Implementation phases

Thirteen phases under `phase-irs-*`, registered in the backlog. None enters `next_up`; per the
owner's ruling this track does not jump the queue, and its ordering ratification is itself a G3
decision when the time comes.

| Phase | Title | Depends on | Requirements |
|---|---|---|---|
| `phase-irs-01` | Stopgap triage dispatch on append, with the reconciling sweep | — | R06, R07 |
| `phase-irs-02` | Consolidate `PLAN-025`'s check-ins into Gate 2 and record the amendment | `phase-part-03` | R01, R08 |
| `phase-irs-03` | Write the pipeline role contracts | — | R03, R13, R23 |
| `phase-irs-04` | LangGraph orchestrator skeleton: graph, checkpointer, interrupt gates, thin-state rule | `phase-irs-03` | R16–R19, R08 |
| `phase-irs-05` | Phase-fit procedure and agent | `phase-idg-10` | R11 |
| `phase-irs-06` | Three-altitude review procedure with the interim adversarial engine | `phase-idg-10` | R09, R10 |
| `phase-irs-07` | Dependency-mapping agent and the G3 ratification flow | `phase-idg-12` | R05 |
| `phase-irs-08` | Execution loop harness: developer/validator dispatch, double-rejection parking, mechanical confidentiality gate | `phase-irs-04`, `phase-auto-02` | R13, R14, R22 |
| `phase-irs-09` | Terminal `delivered` status and the realization check | `phase-idg-01` | R15 |
| `phase-irs-10` | Learning loop: wire rejections, findings and realization outcomes into the anti-pattern store | `phase-agx-03`, `phase-irs-09` | R25 |
| `phase-irs-11` | Run budgets, hard caps and the kill switch | `phase-irs-04` | R20, R21 |
| `phase-irs-12` | End-to-end trace, forced-failure drill and metrics baselines | `phase-irs-05`–`08` | R12, R24 |
| `phase-irs-13` | Gate queue and decision-ready presentation, including batched completion review | `phase-irs-04` | R02, R04 |

Requirement coverage: every `REQ-022` row maps to a phase above except R09's planner half
(owned by `phase-idg-12` and only *checked* here by `phase-irs-06`) and R08's partition workflow
half (owned by `PLAN-025`, amended by `phase-irs-02`). Every phase carries at least one row.

## Execution order

The genuinely parallel front at the start is `phase-irs-01` and `phase-irs-03` — neither
depends on anything, and the stopgap is the owner-ruled immediate build. The critical path runs
`03 → 04 → 08 → 12`, with `04` unblocking three phases (`08`, `11`, `13`). Everything else
gates on the sub-programmes: `05`/`06` on the plan-quality standard, `07` on the planner, `09`
on the schema bundle, `10` on the anti-pattern store, `08` on the broker — the broker-first
inversion `PLAN-032` itself made. If `phase-auto-01` descopes a P5 component, the named
fallback in the boundary table applies and the dependent phase's `depends_on` is amended at
that time, on `dev`, as an ordinary backlog edit.

## Verification discipline for this plan

Each design document in this system passes the six checks the owner accepted on 2026-09-15
before its G3 approval: a trace-through of one real idea end to end; the manual-touch inventory
mapped to automated/gated/out-of-scope; the authority audit of every agent write; failure-path
enumeration with no blank cells; the measurable-target check; and an adversarial pass at the
document's own altitude. The first adversarial pass ran against the draft of `ARCH-006` and its
findings shaped the stage table, the gate model and the de-duplication boundaries above.
