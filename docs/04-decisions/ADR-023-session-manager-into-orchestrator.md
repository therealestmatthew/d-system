---
schema_version: 1
id: doc-adr-session-manager-into-orchestrator
code: ADR-023
title: Carry the Session Manager system into the LangGraph and Agent SDK orchestrator by the split
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-24'
updated: '2026-09-24'
systems: [sys-realization, sys-governance]
depends_on: [doc-adr-langgraph-orchestration, doc-multi-session-coordination-protocol, doc-irs-orchestrator-design, doc-idea-realization-system-requirements]
---

# Carry the Session Manager system into the LangGraph and Agent SDK orchestrator by the split

## Status

Accepted 2026-09-24. The owner approved this text and its merge as `accepted` in the Prompt
Planner session. It records the owner's rulings from the 000347 decision session of 2026-09-24. A
separate session writes the requirement, the plan and the backlog phases from it (owner ruling,
entry 1).

## How rulings are cited

- **Owner ruling (entry n)** means the owner's ruling as the Session Manager recorded it in
  `_working/session-manager/reports/rulings-000347.md`. The entry numbers follow
  `_working/session-manager/reports/decision-pack-000347.md`. `D3-n` means the Scout's decision
  numbering in `_working/session-manager/scout/d3-supervisor-vs-sm-session.md` §6.
- **Proposal** means text from a design document or a session. It is not the owner's ruling. It
  comes from P3 (`_working/overnight-sprint/planning/session-manager-on-langgraph.md`), P4
  (`_working/overnight-sprint/planning/roadmap-to-autonomy.md`) or the Scout's D3 comparison.
- **All of these source files are gitignored.** This ADR is the first tracked record of the rulings.
- **Scope of the rulings.** The owner's rule is that a ruling is one-time unless the owner calls it
  standing (protocol ruling Q10, `_working/session-manager/board.md`:164). Q10 also says a standing
  ruling needs a `GOV-003` entry. None of the rulings below was marked standing, so each is one-time:
  it decides this design and does not become a general rule for other work.

## Context

**The question.** Idea 000334 asks whether the Session Manager system should be injected into,
adapted into, or recreated in the orchestrator built on LangGraph and the Agent SDK (`ADR-018`).
The Session Manager system is the multi-session coordination protocol (`GOV-017`) and its starter
messages (`PROMPT-037`). 000334 also asks two related questions:
- whether the answer differs for each part of the protocol;
- how the daemon's "propose, then observe" claim model (`PLAN-039.01` §6) compares with granted
  turns.

**The routing this ADR supersedes.** An owner ruling of 2026-09-22 is recorded on 000334
(annotation `e18d7d9fb25b4f094`, 2026-09-23T00:50): "Whether to inject, adapt or recreate the Session
Manager system is decided in the later daemon-process phase (phase-irs-16), not before
phase-irs-04." `phase-irs-16` was built to its mechanical scope (lock, signal handling,
start/stop/status). It merged without deciding the question (`SESS-2026-09-23-06`). The owner then
ruled that the question is decided in a new ADR that supersedes that routing (entry 2). This is
that ADR. It supersedes the routing ruling only. `phase-irs-16` stays complete as built. No governed
document is superseded, so the front matter has no `supersedes` field.

**What exists on `dev`.** From the Scout's D3 comparison §2, checked at `2dd56d4`:
- the orchestrator has the tick, `gates.gate_node`, `resume_command`, the gate decisions log and
  `SqliteSaver` checkpoints;
- it has no `unit` graph and no supervisor or router node;
- it has no real dispatcher: `dispatch.py` raises `NotImplementedError`.

## Decision

### 1. The split (000334)

Owner ruling (entry 2), recording P3's recommendation D2 (a):

- **Adapt the coordination rules into the orchestrator.** These are the primary-checkout lock, the
  claim slots, the merge gate, the message contract and the board.
- **Recreate the roles as per-task Agent SDK dispatches.**
- **Inject only during migration.** Interactive sessions and the orchestrator share the one lock
  and gate queue until the migration ends.
- **The owner's merge approval stays human at G4.**

Reason, as the proposal gives it (P3 §3): recreating the coordination rules would put two
coordination systems in charge of one `dev`. That is the "two authorities" failure that `REQ-017`
R16 and `ADR-003` forbid.

### 2. The line between the model and code

**Background.** The owner first left P3's D3 ("is the Session Manager an LLM?") open (entry 3), in
these words: "I think we need to implement both the LLM supervisor node with routing and the
deterministic code." The Scout's D3 comparison was written for this. The owner then ruled on its
decisions D3-1 to D3-9. Those rulings replace P3's D3 options:

- **The line (D3-2).** The model chooses among options that code has already computed as legal.
  Code validates the choice, executes every write and records it. The owner decides at the gates.
- **The router node (D3-3), for now.**
  - It is a router node whose output is restricted to a `Literal` of legal routes.
  - It starts in shadow. It records its proposal next to what actually happened for a number of
    runs. It may route only after its proposals agreed with what happened in a set share of those
    runs.
  - The owner, verbatim: "We're not recreating the wheel". Existing routing solutions are to be
    investigated for integration: idea 000427.
- **The router's memory (D3-4).** Each routing event gets a fresh model call, briefed from records.
- **The owner's surface (D3-1).**
  - This Session Manager session evolves into the Owner Desk through A1. It hands coordination
    duties to the tick one at a time.
  - It ends as the Owner Desk plus exception judge.
  - It runs `dev` writes under D5 (a) (section 3).
  - D3-1 was first recorded as open, pending a comparison of the Owner Desk and the Session Manager.
    It was then ruled as stated here. This ADR records the later ruling.
- **Daemon events (D3-5), for now.**
  - The Owner Desk session polls or watches the gate queue and `orchestrator status`.
  - A spike runs before A1.
  - An injection hook is parked for investigation: idea 000428.
  - LangSmith is to be looked into: idea 000429.
- **G5 (D3-7).** Completion review is a code check that the acceptance lines are met and the
  records are present. The owner also re-reviews a sample, as `REQ-029` R06 (`phase-dam-01`) sets
  out. G5 is not an owner interrupt on every unit.
- **Worker permission prompts and questions (D3-8).**
  - Until a spike passes, the call is denied and parked as a gate item.
  - After the spike passes, the call is deferred and a gate item is written. The worker's transcript
    resumes with the owner's answer.
- **Removals (D3-9).**
  - Removing a worktree or branch is a gate item after each merge.
  - Code executes it after the owner's decision and after the gitignored-content check.
  - It runs from the primary checkout.

### 3. Who commits to `dev` (P3 D5 = D3-6)

Owner ruling (D3-6):
- **(a) for A1.** The owner triggers each write in the Owner Desk session.
- **(b) for U1.**
  - After a recorded G4 decision, the daemon runs the merge and the completion edit.
  - This requires `REQ-022` R03 to be amended. R03 lists integration into `dev` and phase completion
    among the standing owner-only rules.
  - It also departs from `PLAN-039.01` §6's round-4 rule, "the daemon writes nothing to dev". That
    rule has to be amended to match.
- **Builders keep self-merging until N2.** The owner's Scout ruling O-3 (`board.md`:168) stands:
  builders self-merge until N2, P3's proposed merge-gate nodes, exists.

### 4. P3's design decisions D4 and D6 to D13

Owner rulings:

| P3 | Ruling | Entry |
|---|---|---|
| D4 worker lifetime | (c) Mixed: long-lived meta roles, per-task builders. P3 had recommended (a) | 4 |
| D6 mobile approval surface | The Owner Desk (this session, evolved) on Remote Control now; the workbench page when `phase-irs-13` builds it | 6 |
| D7 how workers ask | Never directly: a decision-ready gate item, then the worker continues or parks. One queue for questions, merges, parks and permissions | 7 |
| D8 Documenter authority | Writes on its own branch through G4. New ADRs stay "proposed" until the owner accepts them. The validator allows an ADR only `draft`, `accepted`, `deprecated` or `superseded`. The owner ruled on 2026-09-24 that a separate `proposed` status be added, for finished ADRs waiting on acceptance: idea 000443 (draft, then proposed, then accepted). Until it lands, Documenter ADRs carry `draft` | 8 |
| D9 context thresholds | Soft 50% (finish and restart), hard 75% (park) | 9 |
| D10 delegated authority | Grant records in a tracked file, evaluated in code at G4 and cited in each decision | 10 |
| D11 first role moved to a dispatch (M4) | Scout | 11 |
| D12 the lease | A lease file under `data/orchestrator/` (staleness by heartbeat), with audit events in the ledger | 12 |
| D13 canonical run ledger | `phase-irs-04`'s `_data/runs.jsonl`. `phase-auto-04` is re-scoped to add its missing fields: model and tool versions, context-pack hash, payload hash | 13 |

### 5. P4's roadmap decisions R1 to R4

Owner rulings:

| P4 | Ruling | Entry |
|---|---|---|
| R1 milestone order | A1 first: an attended unit run on SDK dispatches, on the Session Manager path. Then U1, one unattended night. Then the pipeline | 14 |
| R2 `next_up` | The N-phases and `phase-irs-08` go ahead of the pipeline-stage phases. The owner ranks this reorder, and it is applied when the N-phases are registered | 15 |
| R3 split `sys-realization` | A separate system id for the coordination code (the lease, the merge-gate nodes, the grants), with narrow declared paths | 16 |
| R4 the A1 phase | A small docs-only phase whose systems are disjoint from both lanes on the day, picked from `--ready` | 17 |

### 6. Other rulings the follow-on plan must carry

Two more rulings from the same session fall inside the plan this ADR leads to:
- **000400 inside the plan (entry 28).** Executable acceptance and a diff-scoped mutation node are
  planned inside the LangGraph plan, in the `unit` graph.
- **Idempotency (entry 34).** N2's acceptance requires idempotent merge and completion nodes after
  interrupts. The fix for 000348 goes in N0.

The session's other rulings (entries 18 to 51) are outside this ADR.

## Alternatives considered

These were not chosen. Each is described as its source gives it.

- **Inject everything** (000334's "inject"; P3 D2 (b)). The orchestrator talks to a live Session
  Manager session. P3 §3 says this keeps the session as the single point of failure and memory.
- **Recreate everything** (P3 D2 (c)). A separate orchestrator protocol, with `GOV-017` kept for
  interactive sessions only. P3 §3 says this puts two coordination systems in charge of one `dev`.
- **Adapt everything, including the roles as long-lived sessions** (Ideation's option 2 for entry
  2). The decision pack says this brings 000340's context problem back, in code.
- **No model in routing** (P3 D3 (a), the Scout's D3-2 (c)). This was P3's recommendation. The owner
  asked for a router alongside the deterministic code instead (entry 3; D3-2, D3-3).
- **The model routes freely between graph nodes, with code checking only safety rules** (D3-2 (b)).
- **A separate Owner Desk with no Session Manager session, or a web page with no model in the
  approval path** (D3-1 (b), (c)). The web page stays the later surface under D6.
- **A `langgraph-supervisor` agent.** The Scout's report §7.1 cites the documentation saying the
  package is deprecated. A router is a single classification step, which is what D3-3 chose.

The options not chosen for sections 3 to 5, as the decision pack lists them:

| Decision | Not chosen |
|---|---|
| D5 who commits | (c) an LLM worker runs the git commands under a narrow allow rule |
| D4 worker lifetime | (a) one fresh SDK session per task; (b) a long-lived session per role, resumed by id |
| D6 mobile surface | (b) the workbench page only, waiting for it; (c) notifications plus artifact pages |
| D7 worker questions | (b) workers block and wait; (c) separate queues for merges and for questions |
| D8 Documenter | (a) proposes only; (c) writes directly to `dev` |
| D9 thresholds | (b) soft 60%, hard 85%; (c) measure and report only |
| D10 delegated authority | (b) a gitignored authority file per night; (c) no delegation |
| D11 first dispatch | (b) Documenter; (c) Builder, through `phase-irs-08`, skipping M4 |
| D12 the lease | (b) ledger events only; (c) kept in Session Manager messages |
| D13 run ledger | (b) `phase-auto-04` builds the general ledger; (c) keep both |
| R1 milestones | (b) the pipeline first; (c) both at once, split across lanes |
| R2 `next_up` | (b) interleave N-phases after each batch; (c) append them at the end |
| R3 `sys-realization` | (b) keep one serial lane; (c) decide after A1 |
| R4 the A1 phase | (b) a code phase; (c) a phase in the realization lane |

## Consequences

- **What the follow-on session produces.** It writes the requirement, the plan and the phases
  (entry 1). By P4, that is probably a child plan of `PLAN-039` next to `PLAN-039.01`. The GOV-018
  three-altitude review and the partition-before-planning rule apply to it before G3.
- **Amendments this ADR requires but does not make:**
  - `REQ-022` R03, before D5 (b) can apply at U1;
  - `PLAN-039.01` §6's "the daemon writes nothing to dev", to match D5 (b);
  - P3's `unit` graph, which shows a G5 interrupt (P3 §4.2) and must become a code check under D3-7;
  - `GOV-017`, as the migration stages land (P3's proposed N10).
- **The coordination code gets its own system id** (R3). The phases it covers then no longer
  serialise behind every `sys-realization` pipeline phase. The id and its paths are for the
  follow-on plan to propose. `systems.yaml` is not changed here.
- **Two models of the Session Manager coexist until A1:**
  - the evolving Owner Desk session, which runs `dev` writes under D5 (a);
  - the tick, which takes over coordination duties one at a time.
  They share one lock and one gate queue (entry 2, "inject only during migration").
- **The router adds a model call to routing.** It is bounded by D3-2: it chooses only among legal
  options, code rejects anything else, and every write is code's. Until the shadow period ends it
  routes nothing.
- **Parameters left open:**
  - D3-3's number of shadow runs and its required share of agreement;
  - the grant-file location under D10;
  - D3-5's polling interval.
  None of these was ruled. The follow-on plan must ask the owner for each.
- **A possible conflict, not resolved here.** The owner deferred Scout ruling O-1, the overall
  structure, until A1 (`board.md`:168). The decision pack's last paragraph reports that the sources
  do not say whether that deferral limits what this ADR settles. This ADR records what the owner
  ruled on 2026-09-24 and does not decide that question.

## Open follow-ups

Ideas recorded in or around this session (all `triaged`):
- 000427: investigate existing routing solutions to integrate (D3-3).
- 000428: an injection hook that pushes new gate items into the Owner Desk session (D3-5).
- 000429: look into LangSmith (D3-5).
- 000430: second-provider models as planners and in ideation, not only as reviewers.
- 000431: whether LangGraph needs an API key.
- 000432: other providers' models per role, configurable by provider availability and environment.

## Revisit when

- 000427 finds an existing routing solution that fits. D3-3 is ruled "for now".
- The daemon-events spike before A1 fails, or 000428 finds a working injection hook. D3-5 is ruled
  "for now".
- The router's shadow period ends. It either reaches the agreement share and may route, or it does
  not.
- A1 completes. The deferred O-1 ruling and D5 (b) for U1 come due.
