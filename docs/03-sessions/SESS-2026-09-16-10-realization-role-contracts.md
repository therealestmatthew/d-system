---
schema_version: 1
id: doc-session-realization-role-contracts
code: SESS-2026-09-16-10
title: Pipeline role contracts written for the realization system
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization]
depends_on: [doc-idea-realization-system-plan, doc-idea-realization-system-requirements, doc-idea-realization-system, doc-irs-orchestrator-design, doc-build-coordinator]
---

# Pipeline role contracts written for the realization system

Fourth phase of [PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md) batch 1, built by
dispatched agents under the coordinator (`agent-build`), executing **phase-irs-03** — write the
pipeline role contracts — from the idea realization system plan (`PLAN-039`), its requirements
(`REQ-022`), the architecture (`ARCH-006`) and the orchestrator design (`PLAN-039.01`).

## Outcome

The realization role contracts (`GOV-014`) cover all nine pipeline roles from ARCH-006's stage
table — triage, partition, planner, adversary, phase-fit, mapper, developer, validator,
realization — each with inputs, outputs, a binding never-do list, and a per-dispatch token-budget
ceiling. The owner-reserved list is encoded verbatim from ARCH-006's authority model. The
validator contract carries the evidence rule (executed tests and repository checks, never persona
assertions) and the G5 spot-audit sampling rule. The two existing agent definitions whose roles
appear in the nine were updated: `idea-triage` (through its canonical body in `agent-workflows/`,
regenerating its Codex adapter) and `partition-adversary`. No new stub agent files.

## Evidence

- `uv run python -m src.governance`: OK. `generate_agent_workflows.py --check`: 14 adapters
  current. Both re-run by the coordinator.
- Independent validator: pass on all four acceptance conditions (R03 audited per reserved action;
  hand-offs traced to ARCH-006's table; R13 and R23 verbatim).
- Adversarial review: two minors — an unsourced hand-off addition in the Partition contract,
  fixed in one cycle (`a920c02`) and verified gone; and the generator-chain ripple into
  `agent-workflows/` and `.codex/`, accepted as forced by `phase-port-02` having made the
  idea-triage adapter generated after this phase's deliverables were declared.

## Decisions surfaced to the owner

- GOV-014 carries two defaults no source document supplies, labeled in the document as unsourced
  and owner-revisable: a 300,000-token per-dispatch ceiling for every role, and a 1-in-10 random
  G5 spot-audit sampling rate (with twice-rejected work always audited). The owner accepted both
  at the integration gate; revising either is a one-line GOV-014 edit.

Full evidence trail in `_working/build-b1/phase-irs-03.md` (gitignored).
