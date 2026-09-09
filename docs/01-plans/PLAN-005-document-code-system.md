---
schema_version: 1
id: doc-document-codes
code: PLAN-005
title: Deterministic document codes and a documentation management view
kind: plan
status: complete
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-governance, sys-delivery]
depends_on: [doc-document-code-requirements, doc-governance-protocol]
completion_evidence:
- src/governance/codes.py
- schemas/codes.schema.json
- docs/08-governance/codes.yaml
- docs/08-governance/catalog.md
- docs/08-governance/GOV-005-document-codes.md
- docs/04-decisions/ADR-006-document-codes.md
- test/test_codes.py
- docs/03-sessions/SESS-2026-09-05-01-document-code-system.md
---

# Deterministic document codes and a documentation management view

## Context and scope

This repository already governs its documentation: [the protocol](../08-governance/GOV-001-protocol.md)
defines a front-matter contract, `src/governance/__main__.py` validates it, `systems.yaml` is the
component registry, and `backlog.yaml` is the lock table for concurrent agents
([ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md)). The baseline check passes with
14 systems, 23 documents, 7 memories and 53 backlog phases.

What is missing is catalog numbering. There is no per-category counter, no rule for what number a
new document receives, and no way to read a document's series from a directory listing. The
observable requirements and the owner's four accepted decisions are recorded in
[the requirements](../06-requirements/REQ-001-document-code-requirements.md); this plan does not
restate or reopen them.

Included: the code grammar, the register that makes allocation deterministic, validator enforcement,
two new commands, backfilling every existing document, and the governance records. Excluded:
replacing `doc-*` identifiers, changes to `brain/` memories, and any scheduler, service or database.

## The scheme

Two grammars, because two kinds are numbered differently:

- Counter series: `^(PLAN|ADR|ARCH|REQ|PROMPT|OPS|GOV)-[0-9]{3}(\.[0-9]{2})?$`
- Dated series: `^(SESS|WALK)-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}$`

| Series | Kind | Location | Numbering | Sub-codes |
|---|---|---|---|---|
| `PLAN` | plan | `docs/01-plans/`, `plans/` | counter | yes |
| `ADR` | adr | `docs/04-decisions/` | counter | no |
| `ARCH` | architecture | `docs/07-architecture/` | counter | no |
| `REQ` | requirement | `docs/06-requirements/` | counter | no |
| `PROMPT` | prompt | `docs/02-prompts/` | counter | no |
| `OPS` | operation | `docs/08-governance/` | counter | no |
| `GOV` | governance | `docs/08-governance/` | counter | no |
| `SESS` | session | `docs/03-sessions/` | dated | no |
| `WALK` | walkthrough | `docs/03-sessions/` | dated | no |

Allocation is a total function of committed state, so every agent computes the same answer:

- Counter series: `next(series)` = the highest number used by a governed document, a reservation or
  a retirement in that series, plus one.
- Counter sub-codes: `next(parent)` = the highest existing sub-code of that parent, plus one, padded
  to two digits.
- Dated series: `next(date)` = that document's date plus the lowest unused two-digit sequence for
  that date, for example `SESS-2026-09-05-01`.

Sessions and walkthroughs are dated rather than counted for a specific reason. They are the only
kinds written concurrently by several agents — `max_active` is 3, and every completed phase requires
a session record, so the 59 open phases imply at least 59 session documents against the 24 documents
in all other categories combined. A global counter would contend exactly where contention is most
likely, and its order could contradict the date order when agents merge out of sequence. A
date-derived code contends only among agents finishing on the same day, and its order can never
disagree with chronology.

Codes are permanent. A code is never reused and never renumbered once it reaches `dev`; superseded
and deprecated documents keep theirs, and a deleted document's code moves to the retired list.

Concurrency reuses the ADR-003 discipline rather than adding a mechanism. `codes.yaml` on `dev` is
the allocation ledger and `uv run python -m src.governance` is the check. Two agents that both take
`PLAN-006` collide at the second agent's post-rebase run; the later-integrating agent renumbers,
because codes are free before merge and permanent after. An agent that knows it will write a
document reserves its code in the same small commit as its backlog claim — which is what
`phase-rel-04` and `phase-rel-05` already do informally for ADR-004 and ADR-005.

## Work and dependencies

Six phases, each one session, tracked as `phase-doc-*` in
[the backlog](../09-backlog/backlog.yaml). Each leaves the repository check green, matching the
one-concern-per-commit convention.

### Phase 1 — the register and its contract

Create `schemas/codes.schema.json` and `docs/08-governance/codes.yaml`. The register holds only what
cannot be derived — series definitions, reservations and retirements — and deliberately carries no
titles, statuses or owners, so it does not become the duplicate bookkeeping the protocol forbids.

```yaml
schema_version: 1
updated: '2026-09-05'
series:
- code: PLAN
  kind: plan
  locations: [docs/01-plans/, plans/]
  numbering: counter
  sub_codes: true
- code: SESS
  kind: session
  locations: [docs/03-sessions/]
  numbering: dated
  sub_codes: false
reserved:
- code: ADR-004
  reason: Membership authority decision; deliverable of phase-rel-04
- code: ADR-005
  reason: Projection publication decision; deliverable of phase-rel-05
retired: []
```

The validator loads and schema-checks the register. The `series` block becomes the single source of
truth for kind, prefix and location, replacing the hardcoded `LOCATIONS` dict at
`src/governance/__main__.py:41`. `code` stays optional in `schemas/document.schema.json` for now, so
the tree remains green before the backfill.

### Phase 2 — allocation and the management view

Add `--next-code <kind> [--parent <doc-id>]`, printing one code and nothing else, and `--catalog`,
the management report: every governed document as Code, Kind, Status, Owner and Path, each plan
joined with its backlog phase rollup and claiming agent, followed by the reserved and retired lists.
The report reuses `readiness()` and the item indexing in `src/governance/backlog.py:175` rather than
re-deriving phase state, so front-matter lifecycle and backlog execution stay single-sourced.

The catalog is written to `docs/08-governance/catalog.md` and committed, so it is readable in the
GitHub web UI without a checkout or a Python environment. CI regenerates it and fails on any
difference, which turns a stale catalog into a build failure rather than silent misinformation.
`.github/workflows/ci.yaml` already runs the governance command on every push and pull request,
so this is one added step. Because `doc-governance-protocol` line 129 currently states that no
generated snapshot is committed, that sentence is amended in phase 6 to permit a derived file
that is mechanically regenerated and drift-checked. The rule's intent — no hand-maintained
duplicate bookkeeping — is preserved, since nobody edits this file.

### Phase 3 — backfill codes into existing documents

Assign a code to every document that exists today, in git creation order per series — the order in
which the documents were first committed, oldest first. Front matter only; no renames, so no link
churn in this phase.

| Code | Document ID |
|---|---|
| PLAN-001 | `doc-agent-memory` |
| PLAN-002 | `doc-mini-systems` |
| PLAN-003 | `doc-html-00-overview` (parent) |
| PLAN-003.01 … .06 | `doc-html-01-build-tooling` … `doc-html-06-verification` |
| PLAN-004 | `doc-reliability-follow-up` |
| PLAN-005 | `doc-document-codes` (this plan) |
| ADR-001 … 003 | `doc-adr-file-based-governance`, `doc-adr-session-backlog`, `doc-adr-multi-agent-concurrency` |
| ARCH-001 … 003 | `doc-tagging`, `doc-system-audit`, `doc-html-adversarial-audit` |
| REQ-001 | `doc-document-code-requirements` |
| PROMPT-001 | `doc-artifact-code-generation` |
| GOV-001 … 004 | `doc-governance-protocol`, `doc-backlog-protocol`, `doc-backlog-decisions`, `doc-backlog-capture` |
| OPS-001 | `doc-governance-operations` |

ADR-004 and ADR-005 remain reserved, not assigned. ADR-006 and GOV-005 are allocated in phase 6.

### Phase 4 — backfill filenames and inbound references

Rename every governed file so the code is its prefix, and update every inbound reference in the same
change, because the validator and `systems.yaml` existence-check these paths.

| From | To |
|---|---|
| `plans/PLAN-001-agent-memory-system.md` | `plans/PLAN-001-agent-memory-system.md` |
| `docs/01-plans/PLAN-002-mini-systems-proposal.md` | `docs/01-plans/PLAN-002-mini-systems-proposal.md` |
| `docs/01-plans/PLAN-003-dynamic-html-generation/PLAN-003-overview.md` | `docs/01-plans/PLAN-003-dynamic-html-generation/PLAN-003-overview.md` |
| `…/01-build-tooling.md` … `…/06-verification.md` | `…/PLAN-003.01-build-tooling.md` … `…/PLAN-003.06-verification.md` |
| `docs/01-plans/PLAN-004-reliability-follow-up.md` | `docs/01-plans/PLAN-004-reliability-follow-up.md` |
| `docs/01-plans/PLAN-005-document-code-system.md` | `docs/01-plans/PLAN-005-document-code-system.md` |
| `docs/04-decisions/00N-<slug>.md` | `docs/04-decisions/ADR-00N-<slug>.md` |
| `docs/07-architecture/ARCH-001-tagging-system.md` | `docs/07-architecture/ARCH-001-tagging-system.md` |
| `docs/07-architecture/ARCH-002-system-audit.md` | `docs/07-architecture/ARCH-002-system-audit.md` |
| `docs/07-architecture/ARCH-003-html-adversarial-audit.md` | `docs/07-architecture/ARCH-003-html-adversarial-audit.md` |
| `docs/06-requirements/REQ-001-document-code-requirements.md` | `docs/06-requirements/REQ-001-document-code-requirements.md` |
| `docs/02-prompts/PROMPT-001-artifact-code-generation-system.md` | `docs/02-prompts/PROMPT-001-artifact-code-generation-system.md` |
| `docs/08-governance/GOV-001-protocol.md` | `docs/08-governance/GOV-001-protocol.md` |
| `docs/08-governance/GOV-002-backlog-protocol.md` | `docs/08-governance/GOV-002-backlog-protocol.md` |
| `docs/08-governance/GOV-003-backlog-decisions.md` | `docs/08-governance/GOV-003-backlog-decisions.md` |
| `docs/08-governance/GOV-004-backlog-capture.md` | `docs/08-governance/GOV-004-backlog-capture.md` |
| `docs/08-governance/OPS-001-operations.md` | `docs/08-governance/OPS-001-operations.md` |

Dates leave filenames; `created` already carries them. Future sessions keep a date inside the slug
(`SESS-001-2026-09-05-topic.md`) because chronology is their primary axis.

Reference sites to update in the same commit: `docs/08-governance/systems.yaml` lines 95, 109, 120
and 130; `docs/09-backlog/backlog.yaml` `deliverables` lists plus the prose at line 605 and the path
at line 1017, with the ADR-004 and ADR-005 deliverable paths becoming `ADR-004-…` and `ADR-005-…`;
`docs/09-backlog/README.md`; each category README; `doc-system-audit` lines 77–79 and 122;
`doc-html-adversarial-audit` evidence links; `doc-governance-protocol` lines 42 and 53;
`docs/08-governance/README.md`; `doc-backlog-capture`; `AGENTS.md`; `CLAUDE.md` line 128; and
`README.md` lines 155 and 159.

### Phase 5 — enforcement

Make `code` required in `schemas/document.schema.json`, accepting both the counter and dated
grammars, and enable the remaining checks: uniqueness,
series-matches-kind, location, filename prefix, plan-folder naming, sub-code and parent consistency
in both directions, reserved codes usable only by the document whose reservation is removed in the
same change, and retired codes never reusable. A dated code's embedded date must equal the
document's `created` date, so the code cannot drift from the chronology it encodes. Delete the
`LOCATIONS` constant. Add `test/test_codes.py`
covering the rejection paths, since silent acceptance is the real risk here.

### Phase 6 — record the decision and the operating rules

Allocate ADR-006 for the decision record — why codes sit alongside `doc-*` ids rather than replacing
them, why a register rather than a pure maximum scan, and why child plans take sub-codes — and
GOV-005 for the code-assignment protocol. Amend `doc-governance-protocol` line 129, which currently
forbids committing any generated snapshot, so that it permits a derived file kept current by a CI
drift check while still forbidding hand-maintained lists. Update the same document with a Code
column in the taxonomy table, the code-prefixed naming rule and the `code` field row; `doc-governance-operations`
with the two new commands and their diagnostics; `templates/governance/document.md` with a `code`
placeholder; and `AGENTS.md` with the allocation step and the duplicate-code collision case.

## Acceptance and verification

Each phase carries its own acceptance conditions in the backlog. For the program as a whole:

```bash
uv run python -m src.governance
uv run python -m src.governance --catalog
uv run python -m src.governance --inventory
uv run python -m src.governance --ready
uv run pytest
uv run ruff check src/ test/ && uv run mypy src/
```

Allocation is the user-facing contract, so assert exact strings:

```bash
uv run python -m src.governance --next-code plan                                # PLAN-006
uv run python -m src.governance --next-code plan --parent doc-html-00-overview  # PLAN-003.07
uv run python -m src.governance --next-code adr                                 # ADR-007
uv run python -m src.governance --next-code session                             # SESS-001
```

End-to-end confirmation that the scheme works for a genuinely new document: run `--next-code adr`,
create a stub at the returned code with a matching filename, run the validator and expect green,
then change one character of the filename and expect a specific error naming the file and the
expected prefix.

When each phase completes, record actual command output in a dated session document and list
existing files in the phase's `completion_evidence`. A phase is not complete because its files were
written; it is complete when its acceptance conditions were observed to hold.

## Result

All six phases were delivered in one session and recorded in
[SESS-2026-09-05-01](../03-sessions/SESS-2026-09-05-01-document-code-system.md). Final state:
26 governed documents each carrying a code, 104 tests passing, and allocation returning the
exact values this plan predicted before any code existed.

## Open questions

The two questions this plan originally carried are resolved and recorded in the requirements:
sessions and walkthroughs use date-derived codes rather than a global counter, and the catalog is
committed with a CI drift check. What remains genuinely open:

- Whether `WALK` needs to be a separate series at all. Walkthroughs share a directory, a date-based
  grammar and a purpose with sessions; the only thing separating them is the `kind` field. Decide
  after the first few walkthroughs exist, and collapse the series if the distinction stays unused.
- Whether CI should regenerate the catalog and fail on a diff, or fail and require the author to
  regenerate. The first is friendlier; the second keeps CI free of write side effects. Settle this
  in phase 2 against the actual workflow rather than in advance.
