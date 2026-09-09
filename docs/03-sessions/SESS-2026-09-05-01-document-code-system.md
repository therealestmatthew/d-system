---
schema_version: 1
id: doc-session-document-codes
code: SESS-2026-09-05-01
title: Implement the document code system
kind: session
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-governance, sys-delivery]
depends_on: [doc-document-codes]
---

# Implement the document code system

Delivered all six `phase-doc-*` phases of [PLAN-005](../01-plans/PLAN-005-document-code-system.md)
in one session, as six commits that each left the repository check green.

## Outcomes

| Phase | Outcome |
|---|---|
| phase-doc-01 | Register contract and data; the series block replaced the hardcoded `LOCATIONS` mapping |
| phase-doc-02 | `--next-code` and `--catalog`; catalog committed with a CI drift check |
| phase-doc-03 | Codes backfilled into all 24 documents, front matter only |
| phase-doc-04 | 25 paths renamed, roughly 40 inbound references updated |
| phase-doc-05 | `code` made required; all strict rules enforced; 18 rejection tests added |
| phase-doc-06 | ADR-006 and GOV-005 written; protocol, operations, template and AGENTS.md updated |

## Verification results

```
uv run python -m src.governance
Governance OK: 14 systems, 26 documents, 7 memories, 59 backlog phases

uv run pytest
104 passed

uv run mypy src/
Success: no issues found in 10 source files

uv run ruff check src/governance/ test/
All checks passed!
```

Allocation returned the exact values the plan predicted before any code existed:
`PLAN-006`, `PLAN-003.07`, `ADR-006`, `SESS-2026-09-05-01`.

End-to-end naming check: placing a stub at `ADR-006` validated clean; changing one character of the
filename failed with `filename must start with ADR-006-`. Following the written procedure from the
committed instructions alone allocated `REQ-002`, placed a document from the template and validated
green.

Link integrity after the renames was checked by resolving every relative Markdown link in `docs/`,
`plans/` and the root entry points. None were broken.

## Decisions made during the session

Two questions the plan left open were resolved against the real workflow rather than in advance.

CI **verifies** the catalog rather than regenerating it: it renders into a temporary file and diffs,
so CI keeps no write side effects on the tree and a stale catalog fails with a readable diff.

Filename enforcement was gated behind a `strict` flag rather than applied as soon as codes existed.
Without the gate, adding `code` to front matter would have demanded the renames in the same commit,
collapsing two phases into one unreviewable diff.

## Unresolved

`ruff check src/ test/` still fails on `src/db/connection.py:3` (`UP035`, deprecated
`typing.Generator` import). This is pre-existing and is the declared deliverable of
`phase-rel-01`; it was left untouched because it belongs to another phase's boundary.

`WALK` remains an unused series. Collapse it into `SESS` if the distinction stays unused after the
first few walkthroughs, as ADR-006's revisit trigger states.
