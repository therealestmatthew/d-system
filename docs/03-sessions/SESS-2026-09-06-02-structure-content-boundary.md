---
schema_version: 1
id: doc-session-structure-content-boundary
code: SESS-2026-09-06-02
title: Structure/content boundary decision
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-portfolio]
depends_on: [doc-confidentiality-sweep, doc-structure-content-boundary]
---

# Structure/content boundary decision

Executed `phase-priv-01` as `agent-architect`, at the owner's direction, ahead of `phase-cap-02`.
The reason for the reordering: `phase-cap-08` seeds the portfolio through the capture pipeline, so
capture will generate exactly the personal material [PLAN-006](../01-plans/PLAN-006-confidentiality-sweep.md)
exists to keep out of the tracked tree. Settling the boundary first costs one session; discovering it
afterwards costs a history rewrite.

## Outcome

[ADR-009](../04-decisions/ADR-009-structure-content-boundary.md) defines the boundary. Structure is
anything that stays true if every record were replaced; content is anything describing the owner's
actual life or clients. The operative test for an unclear case is **whether the file would still be
correct if a different person adopted the system** — which is what a worked example naming a real
client fails, and how the client identifier reached `ARCH-001` and two brain memories while looking
like documentation.

The ADR also fixes the three things the phase required: the portfolio relocates to
`_private/portfolio/` rather than being gitignored in place, the fresh-clone-stays-green constraint
binds every later phase, and captured content is content by the same definition — which is what
[ADR-007](../04-decisions/ADR-007-capture-routing.md)'s private-by-default rule derives from.

`GOV-001` no longer calls the tracked `_data/` path the source of truth. It now names the *configured
data root*, and carries a data-root section stating both the target state and, explicitly, that the
relocation has not happened yet.

## Code collision

`phase-priv-01` declared `docs/04-decisions/ADR-007-structure-content-boundary.md` as its deliverable.
PLAN-006 stated in prose that ADR-007 was allocated, but never reserved it in `codes.yaml`, so
`--next-code adr` issued ADR-007 to the capture routing decision earlier the same day.

Resolved by the documented rule — the document that integrates first keeps the code. The boundary ADR
became ADR-009; the phase's deliverable path and PLAN-006's prose were corrected in the same change,
and the collision is recorded in
[GOV-003](../08-governance/GOV-003-backlog-decisions.md).

The root cause is worth stating separately from the fix: the allocator behaved correctly, and the
reservation step was skipped. `ADR-004` and `ADR-005` are reserved in `codes.yaml` and did not
collide. A code claimed only in prose is not claimed.

## Verification

```
uv run python -m src.governance
Governance OK: 15 systems, 38 documents, 7 memories, 77 backlog phases

uv run pytest
110 passed, 2 warnings
```

For the second verification step — reading the amended protocol against the ADR for surviving
contradictions — `grep -rn "source of truth"` returns five other matches, all checked:

| Location | Status |
|---|---|
| `GOV-005` | Refers to `codes.yaml`, unrelated |
| `PLAN-006` (two matches) | Describes the tension being resolved; accurate as context |
| `PROMPT-002` | An interview question, now answered; historical |
| `brain/decisions/json-first-duckdb-derived.md` | Currently accurate — the move has not happened |

`CLAUDE.md` and `README.md` describe `_data/` as the tracked source of truth. Both are accurate
today and become wrong at `phase-priv-03`, not before. They were left alone: they sit outside this
phase's declared deliverables, and amending them now would state a relocation that has not occurred.

## Deviation from AGENTS.md

This phase ran in the primary checkout on `dev`, not in a worktree, with the owner's explicit
approval. `AGENTS.md` still states the blanket prohibition; the reasoning and its limits are recorded
in [GOV-003](../08-governance/GOV-003-backlog-decisions.md). Amending `AGENTS.md` itself is not in
this phase's scope.

## Unresolved

- **`brain/decisions/json-first-duckdb-derived.md`, `CLAUDE.md` and `README.md` need amending when the
  portfolio actually moves.** This is `phase-priv-03` work, not a gap here. `phase-priv-02` already
  covers the brain memories for identifier scrubbing.
- **PLAN-006's three open questions stand**: whether the remote should be private regardless, whether
  the fictional portfolio is generated or hand-written, and whether `_public/` holds a sanitized
  export.
- **`README.md` documents `commitment_cadence`**, which [ADR-008](../04-decisions/ADR-008-record-types.md)
  renames. That correction belongs to `phase-cap-02`.
