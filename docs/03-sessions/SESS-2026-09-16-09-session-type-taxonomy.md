---
schema_version: 1
id: doc-session-session-type-taxonomy
code: SESS-2026-09-16-09
title: Session type taxonomy defined with per-type context contracts
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-governance]
depends_on: [doc-session-lifecycle, doc-build-coordinator]
---

# Session type taxonomy defined with per-type context contracts

Third phase of [PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md) batch 1, built by
dispatched agents under the coordinator (`agent-build`), executing **phase-ses-01** — define the
session type taxonomy and per-type context — from the session lifecycle plan (`PLAN-008`).

## Outcome

Two governed documents: the session type taxonomy requirements (`REQ-023`), stating each type's
must-read / may-skip / must-produce / must-never obligations as observable conditions with
verification methods and listing the universal rules once as non-negotiable; and the session type
declaration and lifecycle decision (`ADR-020`), resolving the plan's open questions —
brainstorming records ideas through `append_idea.py` rather than a governed artifact; a mid-flight
type change binds from the point of change and is recorded in the session record's Decisions
section; the type is inferred from the claimed phase by default with owner declaration as
override. Per the owner's ruling at the batch open, the already-shipped checkpoint skill
(`phase-ses-03`) and session-close command (`phase-ses-05`) were treated as fixed constraints the
taxonomy describes.

## Evidence

- `uv run python -m src.governance`: OK (31 systems, 267 documents, 278 phases), re-run by the
  coordinator directly.
- Independent validator: pass on all three acceptance conditions plus the scope's two decision
  questions, citing no contradiction with checkpoint, session-close, GOV-003's coordinator entry,
  AGENTS.md or GOV-006.
- Adversarial review: two major findings (both documents citing mechanisms that do not exist — a
  checkpoint note field, a `/session-start` type inference) and two minors. Fixed in one cycle
  (`48184f1`): the mid-flight record now cites session-close's real Decisions section; type
  inference is an obligation on the opening session, verifiable from the session record, with the
  `/session-start` wiring named as future work. Fixes spot-verified by the coordinator.

## Unresolved

- Future work named in ADR-020's consequences: wiring type inference into `/session-start` (an
  owner-only command edit, out of this phase's deliverables).

Full evidence trail in `_working/build-b1/phase-ses-01.md` (gitignored).
