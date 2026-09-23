---
schema_version: 1
id: doc-adr-langgraph-orchestration
code: ADR-018
title: Orchestrate the idea realization pipeline with LangGraph over the Claude Agent SDK
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-22'
systems: [sys-governance, sys-backlog]
depends_on: [doc-idea-realization-system]
---

# Orchestrate the idea realization pipeline with LangGraph over the Claude Agent SDK

## Status

Accepted 2026-09-22. Owner-selected on 2026-09-15 (recorded on idea `000247`); `phase-irs-04`
landed the first working graph -- `src/orchestrator/graphs/intake.py`, a checkpointed,
interruptible LangGraph state graph running end to end under `test/test_orchestrator.py`,
including the checkpoint-loss and killed-process resumption drills this ADR's boundary rule
promises (REQ-022 R16, R17).

## Context

The idea realization system ([ARCH-006](../07-architecture/ARCH-006-idea-realization-system.md))
chains nine stages with five owner gates. The repository is otherwise a pure Anthropic stack
with no LangChain-family dependency. Three orchestration needs exceed what ad-hoc scripting over
the Agent SDK provides cleanly: a run that survives process death and resumes at its stage;
conditional branching between stages driven by stage outcomes; and durable human-interrupt
points that park a run at a gate for hours or days.

## Decision

- **LangGraph** defines the pipeline as a state graph: one node per stage, conditional edges for
  the failure paths, interrupt nodes for gates G2–G5, and a checkpointer for resumability.
- **The Claude Agent SDK** executes every agent a node dispatches. LangGraph never talks to the
  model directly; nodes invoke SDK sessions and read their results.
- Plain LangChain (chains) is not used; the owner's original phrasing named LangChain, and the
  selected target is LangGraph specifically.

## The boundary rule: thin state, repo wins

Graph state carries run identity, the current stage, and references into the repository's
durable records — never copies of their content. `_data/ideas.jsonl`, `backlog.yaml`, governed
documents and the run ledger remain the only sources of truth. When a checkpoint and the
repository disagree, the repository is authoritative and the run re-derives its position.
Checkpoints therefore cover process death only; semantic failures follow the stage failure
paths in `ARCH-006` and are recorded in repository state, not in graph state.

Checkpoint storage lives under gitignored `data/`, alongside the other derived, rebuildable
state, and is disposable by construction: deleting it loses nothing the repository cannot
re-derive.

## Alternatives considered

- **Agent SDK only** — fewest moving parts and the reviewer-recommended default. Rejected by
  the owner in favor of purpose-built graph orchestration; the interrupt/checkpoint machinery
  would otherwise be rebuilt by hand.
- **Plain LangChain** — largely superseded by LangGraph for multi-agent orchestration; not
  chosen.
- **Cron/polling scripts per stage** — no run identity, no resumability, gates become ad-hoc
  files; rejected.

## Consequences

- A new dependency family enters `pyproject.toml`, version-pinned, with the integration surface
  confined to the orchestrator package so nothing else in `src/` imports it.
- The thin-state rule is enforceable in review: any node caching record content into graph
  state is a defect.
- If LangGraph is later removed, the loss is the checkpoint/interrupt machinery, not any
  business state — the repository records were the truth throughout.
