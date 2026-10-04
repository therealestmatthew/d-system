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

## Review

Independent adversarial review by a fresh `demo-adversary` sub-agent (a demo-track reviewer type,
used here because the roster has no governance-specific adversary), range `dev...HEAD` at
`3c6d2e3`. Its findings, as reported:

- **REQ-015 R14 — Met.** Ran `--inventory` itself: `sys-tmpagent | governance | implemented`
  alongside `sys-backlog` and `sys-portfolio`. Governance OK (44 systems, 425 documents); the new
  entry carries all eight required fields per `schemas/systems.schema.json`.
- **Maturity justified — Met.** Every factual claim in the description verified against
  `_tmpagent/claims.jsonl`: 15 lines spanning 2026-09-14 to 2026-09-22; all five events; four files;
  `p10-track-coordinator.md` removed (line 15); every claimed `(file, kind, ref)` triple has a later
  `released`; lines 13-14 use `agent` not `by`; `grep -rn "claims.jsonl" test/ src/ tools/` returns
  nothing; idea 000564 exists and matches. "Implemented" judged defensible against ADR-012's
  scaffold/implemented distinction and comparable to `sys-brain`, and the entry discloses its own
  weakest point.
- **Reachability — Met.** `_tmpagent/AGENTS.md` is in `paths`; both AGENTS.md passages cited
  exist (Key conventions, lines 123-127; "complete and hand off" step 3, lines 283-284).
- **Minor:** the description quoted the AGENTS.md heading with a hyphen ("Concurrent agents -
  complete and hand off"); the heading uses a colon.
- **Minor:** the ledger facts are a point-in-time snapshot nothing re-derives; a line appended to
  `claims.jsonl` on dev before merge would make "every claim released" false. Same gap as idea
  000564; recheck `claims.jsonl` against dev immediately before merge.
- Scope discipline holds: `systems.yaml` purely additive, plus the session record, the phase's own
  `next_action` line and the regenerated catalog. Catalog regeneration byte-matches.

Disposition: the first minor finding is fixed — the description now cites the section as headed
"complete and hand off", because an unquoted `: ` inside a YAML plain scalar is a parse error,
which is why the hyphen was there. The second is accepted: `_tmpagent/` was checked identical on
dev `451fdea` before READY, and is checked again inside the merge turn.

## Decisions

The owner chose a new `sys-tmpagent` system at `implemented` over `scaffold`, on the evidence that
the full ledger lifecycle has run for real. The description carries the counter-evidence alongside:
the contract is convention-only, and field drift in two ledger lines went unnoticed. That drift was
sent to Ideation instead of being fixed here, because `_tmpagent/claims.jsonl` is append-only and
outside this phase's deliverable; it became idea 000564. `AGENTS.md` itself was not listed as a
path, so the new system does not appear to own a file every phase reads; it is named in the
description instead.

## Corrections

The review's heading fix first reproduced the exact heading with its colon, which broke YAML
parsing of `systems.yaml`; caught by a parse check before commit and reworded.

## Left undone

The completion edit on dev (`status: complete`, `session`, `completion_evidence`, `result`) waits for
the owner-approved merge. A mechanical check of the ledger is idea 000564, not this phase.
