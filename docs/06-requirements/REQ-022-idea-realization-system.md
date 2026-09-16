---
schema_version: 1
id: doc-idea-realization-system-requirements
code: REQ-022
title: Idea realization system requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-16'
systems: [sys-portfolio, sys-backlog, sys-governance]
depends_on: [doc-idea-realization-system]
---

# Idea realization system requirements

Observable statements for the pipeline mapped in
[ARCH-006](../07-architecture/ARCH-006-idea-realization-system.md). Each row is checkable by the
named method; none asserts that the capability exists today. `PLAN-039` maps every row to at
least one phase.

## Gates and authority

| # | Requirement | Verification |
|---|---|---|
| R01 | The five gate categories (G1 idea approval, G2 track acceptance, G3 plan approval, G4 integration, G5 completion review) exist as defined pause points; no pipeline transition crosses one without a recorded owner decision | Inspect the orchestrator's graph definition; trace one run's ledger entries against its gate decisions |
| R02 | G5 is batchable: the owner can clear a queue of finished phases in one sitting, each still individually closed through `/session-close` | Run a batch of two or more closes; confirm each phase's record and status change |
| R03 | No standing owner-only rule is performed by an agent: `lineage` annotations, `next_up` ranking, integration into `dev`, phase completion, `AGENTS.md`/`CLAUDE.md` edits, `_working/` deletions | Grep role contracts for the reservation; adversarial audit of one full run's writes |
| R04 | Every gate item is decision-ready: it presents the proposal, the adversarial findings, and the evidence, and never requires the owner to read a raw agent transcript | Owner inspection of one queued item per gate category |
| R05 | The dependency-mapping agent writes `depends_on` and `systems` and proposes an ordering; the proposal is ratified, amended or rejected at G3 and the decision is recorded | Trace one plan's mapping from proposal to ratified `next_up` contribution |

## Pipeline behavior

| # | Requirement | Verification |
|---|---|---|
| R06 | An idea appended to the log is dispatched for triage without human action, via the repo-native stopgap until the P5 gateway question is ruled | Append a test idea; observe dispatch and the resulting finding annotation |
| R07 | If dispatch or the triage agent fails, the idea remains `open` and a sweep reconciles and re-dispatches; no idea is lost between `open` and `triaged` | Kill a dispatch mid-run; run the sweep; confirm the idea reaches `triaged` |
| R08 | The partition stage consumes only `triaged` ideas, fires on a stated threshold or on demand, and its proposal passes through an adversarial audit before G2 | Inspect a partition run's inputs and its adversary findings record |
| R09 | Drafted plans are checked against the plan-quality standard before adversarial review; non-conformance returns them to the planner | Submit a deliberately non-conformant draft; observe the return |
| R10 | The three-altitude review procedure exists in writing — whole plan, each phase in isolation, each later-added phase against the standing plan — and runs with whatever adversarial engine is available, recording findings and dispositions | Read the procedure; inspect one review's findings record |
| R11 | A phase-fit procedure exists for splitting an oversized backlog phase, distinct from `phase-idg-05`'s idea decomposition; a split phase re-enters review | Run it against a deliberately oversized phase |
| R12 | Every stage has a written failure path (revise, escalate, park, or dead-letter); no stage's failure leaves a run wedged silently | Read the stage table; force one failure per stage class in a test run |
| R13 | Execution agents work under the `ADR-003` claim and worktree protocol unchanged; validators see the requirement and the diff, never the developer's rationale | Inspect validator dispatch prompts from one run |
| R14 | A unit rejected twice by validation parks as `blocked` with its finding attached and surfaces in the G5 queue | Force a double rejection; inspect the phase state |
| R15 | After integration, a realization check verifies the delivered capability against the originating idea's text and records evidence on the idea; the idea reaches a terminal `delivered` status only through G5 | Trace one idea from merge to `delivered`; confirm the evidence annotation |

## Orchestration and state

| # | Requirement | Verification |
|---|---|---|
| R16 | Graph state is thin: run identity, current stage, and references into durable records; on disagreement the repository wins and the run re-derives by abandoning the thread and re-keying a new one at the re-derived position | Delete or corrupt the checkpoint store in a test run; confirm threads are re-keyed at the position the records prove |
| R17 | A run interrupted at a gate parks durably and resumes in a later process without loss | Kill the orchestrator at a gate; resume; compare state |
| R18 | Every automated transition writes a ledger entry sufficient to reconstruct the run after the fact | Reconstruct one completed run from the ledger alone |
| R19 | The orchestrator consumes claim-protocol recovery procedures from `phase-conc-04`'s deliverables and defines none of its own | Grep the orchestrator for claim-recovery logic; audit against the boundary table in `PLAN-039` |

## Cost, safety and independence

| # | Requirement | Verification |
|---|---|---|
| R20 | Every run carries a token budget; reaching the hard cap parks the run rather than exceeding it | Set a low cap on a test run; observe the park |
| R21 | A kill switch halts all pipeline dispatch, is owner-operable, and takes effect before the next agent dispatch | Trip it during a multi-stage run |
| R22 | The staged confidentiality check runs mechanically inside stage 8 before any push; a failure blocks the push and surfaces the finding | Stage a file with a test identifier; observe the block |
| R23 | Validation independence is grounded in executed evidence (tests, repository checks) rather than persona prompts, and the owner's spot-audit of passed validations is a defined G5 activity with a sampling rule | Read the validator contracts; perform one spot-audit |

## Measurement and learning

| # | Requirement | Verification |
|---|---|---|
| R24 | Automation rate, cycle time and rework rate are computed deterministically from the run ledger and idea log; baselines are recorded before targets are set | Run the metrics tool twice; identical output; baseline document exists |
| R25 | Validator rejections, recurring adversarial findings and realization-check outcomes feed the anti-pattern store, and the plan-quality standard cites that store when revised | Trace one recorded rejection into the store; inspect a standard revision |
