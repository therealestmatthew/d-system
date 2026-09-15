---
schema_version: 1
id: doc-session-idea-realization-system-architecture
code: SESS-2026-09-15-13
title: Idea realization system architecture and master plan
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-realization, sys-portfolio, sys-backlog, sys-governance]
depends_on: [doc-idea-realization-system]
---

# Idea realization system architecture and master plan

Owner-directed session with no backlog phase — **unclaimed**, branch `agent/irs-architecture`,
worktree `../d-system-worktrees/irs-architecture`. Peers hold no lock against it.

## What the session did

1. **Captured and triaged idea `000247`** (formalize the idea realization system into an
   automated multi-agent pipeline). The triage agent recorded a finding and links to `000046`,
   `000072`, `000078` and `000082`, and moved it to `triaged`. Capture and annotations were
   committed on `dev` per the standing capture path (`d682ddd`, `bef4c85`).
2. **Took eight owner rulings**, all via `AskUserQuestion`, recorded as findings on `000247`:
   LangGraph + Claude Agent SDK; a superseding master plan over P1/P4/P5/`PLAN-025`; five gate
   categories with batched completion review; plan-now-build-after-P1/P4; a repo-native stopgap
   trigger; agents map and the owner ranks; a stage-9 realization check.
3. **Ran an adversarial pass** (the `partition-adversary` agent) against the draft architecture
   before writing any governed document. It returned two blockers and seven majors — the gate
   count broken by `PLAN-025`'s three check-ins and by per-phase `/session-close`; the P4 trio
   mischaracterized; `phase-idg-05` misapplied to phases; orchestrator overlap with
   `phase-agx-09`; the P5 gateway dependency with no interim; `next_up` authority; missing
   stage 7/8 failure paths; `PLAN-025` still `draft`. Every finding was accepted and is
   corrected in the shipped documents.
4. **Wrote the document set**: `ARCH-006` (the system map: nine stages, five gates, authority
   model, hand-off contracts), `REQ-022` (25 observable requirements), `PLAN-039` (the master
   plan: sub-programme table, de-duplication boundaries, thirteen `phase-irs-*` phases),
   `ADR-018` (LangGraph, thin-state/repo-wins rule), a `GOV-003` entry for the re-framing of
   the accepted partition, the `sys-realization` entry in `systems.yaml`, and the thirteen
   phases registered in `backlog.yaml`, none in `next_up`.

## Verification, actual output

- `uv run python -m src.governance` — `Governance OK: 28 systems, 251 documents, 25 memories,
  274 backlog phases`.
- `uv run pytest` — `580 passed, 2 warnings`.
- `tools/check_no_private_content.py` run staged on the `dev` capture commits — OK both times.

Three validator rejections during the work, each fixed rather than bypassed: `status: proposed`
is not a valid system status (now `planned`) nor a valid ADR status (now `draft`), and six
backlog items had single-entry acceptance lists (each now carries two conditions).

## Unresolved

- The documents are drafts awaiting the owner's G3-category review; `PLAN-039`'s phases enter
  `next_up` only by owner ranking.
- `PLAN-025` remains `status: draft`; its acceptance and the `phase-irs-02` gate-consolidation
  amendment both surface at the next partition-related decision.
- The branch is ready for review, not integrated: `git diff dev..agent/irs-architecture`.
