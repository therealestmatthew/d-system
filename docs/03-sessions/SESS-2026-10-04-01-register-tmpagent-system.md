---
schema_version: 1
id: doc-session-register-tmpagent-system
code: SESS-2026-10-04-01
title: Register _tmpagent in the systems maturity registry
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-governance]
depends_on: [doc-document-backlog-governance]
---

# Register _tmpagent in the systems maturity registry

## Phase

`phase-dgov-07` — Register _tmpagent in the systems maturity registry.

## Verification

`uv run python -m src.governance --inventory` (rows for the new entry and two named peers):

```
| System | Domain | Maturity | Owner |
| sys-backlog | governance | implemented | repository-owner |
| sys-portfolio | data | implemented | repository-owner |
| sys-tmpagent | governance | implemented | repository-owner |
```

`uv run python -m src.governance`:

```
Governance OK: 44 systems, 424 documents, 36 memories, 347 backlog phases
```

## Acceptance

- REQ-015 R14 — `Met`. `--inventory` lists `sys-tmpagent` with maturity `implemented`, next to
  `sys-backlog` and `sys-portfolio` (see Verification).
- Maturity justified against the mechanism's actual state — `Met`. The entry's description gives the
  ledger facts behind `implemented`: 15 lines from 2026-09-14 to 2026-09-22, all five events used
  across four files, one file removed, every claim released. It also states that the contract is
  convention-only, and names the drift nothing caught (lines 13-14 of `claims.jsonl` use `agent`
  instead of the required `by`).
- AGENTS.md's `_tmpagent` section and `_tmpagent/AGENTS.md` reachable from the entry — `Met`.
  `_tmpagent/AGENTS.md` is a registered path; the description names AGENTS.md's Key conventions
  passage and its "complete and hand off" step 3, the two places AGENTS.md covers `_tmpagent`.

## Backlog

`status: active`, `agent: agent-builder-b`. `next_action`: every acceptance condition met on
`agent/phase-dgov-07`; awaiting the owner-approved merge, after which the completion edit is made
on dev.

## Unresolved

None.
