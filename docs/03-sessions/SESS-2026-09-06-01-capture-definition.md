---
schema_version: 1
id: doc-session-capture-definition
code: SESS-2026-09-06-01
title: Capture and structuring definition session
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-capture, sys-contracts, sys-portfolio, sys-projection]
depends_on: [doc-capture-system, doc-capture-system-prompt]
---

# Capture and structuring definition session

Executed `phase-cap-01` against
[PROMPT-002](../02-prompts/PROMPT-002-capture-and-structuring-system.md), claimed as
`agent-architect`. The session interviewed the owner in five batches and produced governed documents
and backlog phases. No implementation code was written and no prototype was built.

## Correction made before the interview

The concurrency protocol was written against a `main` branch that does not exist in this repository;
`dev` is the trunk. Every trunk reference in `AGENTS.md`, `GOV-001`, `GOV-002`, `OPS-001`, `ADR-003`,
`ADR-006`, `REQ-001` and `PLAN-005` was corrected, and `dev` was added to the CI trigger.

The same pass removed the remote-dependent steps from those command sequences. `AGENTS.md` forbids
adding a remote until `phase-priv-05` completes, so `git fetch origin`, `git pull` and `git push`
could not have run as written; they are now marked as steps that apply once a remote exists. `main`
is recorded as reserved for future tagged releases.

## What the owner decided

Fifteen decisions, recorded in full in [ADR-007](../04-decisions/ADR-007-capture-routing.md) and
[ADR-008](../04-decisions/ADR-008-record-types.md). The ones that shaped everything else:

- **Ad hoc now, scheduled later.** All four output moments are wanted eventually; nothing schedules
  itself yet.
- **Priorities in order:** zero broken promises, then nothing went quiet. Capture completeness is
  explicitly not expected to reach 100%.
- **Never interrupt capture.** Ambiguity is flagged and queued, never asked about in the moment,
  because a question in the moment is friction that ends capture.
- **Assume, but never silently.** Four protected fields may be inferred from context; an unflagged
  non-explicit value in one of them is a validation failure.
- **Staging is the write boundary**, and capture is private by default. The owner's test for what may
  be tracked: it benefits the application, rather than encoding personal prioritisation.

Three answers changed the shape of the work rather than confirming it:

1. **The entity model was insufficient.** "Who said what and when", "what did we decide and why",
   "what is owed to me" and personal-development metrics had no home. Four record types were added.
2. **Tasks need optional parents.** The owner asked for free-floating tasks, tasks under a project,
   and tasks under a commitment. A task is currently an array element inside commitment JSON, so a
   parentless task had nowhere to live at all — tasks become a first-class entity. Zero tasks exist,
   so the change is free now and gets more expensive weekly.
3. **`ongoing` is not a cadence.** The owner identified that it describes activity status, which
   `project.status` already carries. It is retired; three projects need reassignment, and no agent
   picks a value for them.

## Deliverables

| Document | Content |
|---|---|
| [ADR-007](../04-decisions/ADR-007-capture-routing.md) | Routing, provenance and the staging boundary |
| [ADR-008](../04-decisions/ADR-008-record-types.md) | Nine record types, optional parents, cadence semantics |
| [REQ-002](../06-requirements/REQ-002-capture-requirements.md) | 25 observable requirements with verification methods |
| [PLAN-009](../01-plans/PLAN-009-capture-build.md) | Eight build phases in dependency order |
| `docs/09-backlog/backlog.yaml` | `phase-cap-02` through `phase-cap-09` |
| `docs/08-governance/systems.yaml` | `sys-capture` registered, status `planned` |

## Verification

```
uv run python -m src.governance
Governance OK: 15 systems, 36 documents, 7 memories, 77 backlog phases

uv run python -m src.governance --backlog
77 phases; every phase has a one-session budget.
active: 1, complete: 7, deferred: 5, ready: 5, waiting: 59

uv run pytest
110 passed, 2 warnings
```

Both of the phase's verification commands pass. The test suite was run because the branch-reference
correction touched `.github/workflows/ci.yaml`; it is unchanged by the documentation work.

## Deviation from AGENTS.md

This phase ran in the primary checkout on `dev`, not in a worktree, with the owner's explicit
approval. `AGENTS.md` still states the blanket prohibition; the reasoning and its limits are recorded
in [GOV-003](../08-governance/GOV-003-backlog-decisions.md). Amending `AGENTS.md` itself is not in
this phase's scope.

## Unresolved

- **Durable off-disk storage.** Postgres, Supabase and Firebase were raised. Deferred by owner
  decision; revisit once sustained captured data exists that would hurt to lose. Recorded in REQ-002;
  no phase scheduled.
- **Scheduled prompting.** Wanted eventually; revisit once the review loop is in daily use.
- **Three projects hold a retired cadence value.** Resolved by the owner during `phase-cap-02` and
  `phase-cap-08`; both phases carry the flag.
- **`phase-sig-03` gains a second source.** `waiting_on` records would make the Accountability Ledger
  two-sided. This is a scope change to an existing phase and was not absorbed silently;
  `phase-cap-09` puts it to the owner.
- **Whether the fourteen blocked phases should depend on `phase-cap-08`.** PLAN-009 states the
  mapping, but their `depends_on` lists were not rewired — that would change the readiness of
  fourteen phases and is the owner's call.
