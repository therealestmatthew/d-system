---
schema_version: 1
id: doc-session-entity-contracts
code: SESS-2026-09-06-04
title: Entity contracts for the expanded model
kind: session
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-contracts, sys-portfolio, sys-brain]
depends_on: [doc-capture-build, doc-record-types, doc-capture-routing, doc-capture-requirements]
---

# Entity contracts for the expanded model

Executed `phase-cap-02` as `agent-architect`, the front of `next_up`, in a worktree at
`../d-system-worktrees/phase-cap-02`. Schemas only: no DDL, no loader and no application code
changed, which is one of the phase's acceptance conditions and the reason the contract can be
settled before anything is written against it.

## Outcome

Nine entity shapes exist where five did. `task`, `interaction`, `decision`, `waiting-on` and
`development-event` are new; `commitment` and `project` changed.

`schemas/evidence.schema.json` holds the shared shape. Its root is the per-field evidence map a
**staged** record carries — level plus provenance into the raw capture — and its
`definitions/capture_source` is the much smaller shape that survives promotion into `_data/`: a
capture pointer and the names of the fields that were non-explicit at the time, per
[GOV-003](../08-governance/GOV-003-backlog-decisions.md). Entity schemas reference that definition
by relative `$ref` rather than restating it, so there is one definition of what a record remembers
about its own origin.

The protected-field rule is the part worth stating precisely, because it is the mechanism behind
"zero broken promises" rather than a naming convention. `definitions/protected_field_evidence`
makes a non-explicit value in a protected field a validation failure unless `review_flag` is true.
The protected set is `promised_to`, `due_date`, `decision`, `rationale`, `completed` and
`received` — the last two both being instances of [ADR-007](../04-decisions/ADR-007-capture-routing.md)'s
"completion of anything", one on `commitment` and one on `waiting-on`. The list is published as an
`enum` in the schema so code and tests read it rather than restating it.

## Evidence

- `schemas/evidence.schema.json`, `schemas/task.schema.json`, `schemas/interaction.schema.json`,
  `schemas/decision.schema.json`, `schemas/waiting-on.schema.json`,
  `schemas/development-event.schema.json` — new.
- `schemas/commitment.schema.json` — `project_id` optional, embedded `tasks` array removed.
- `schemas/project.schema.json` — `commitment_cadence` renamed `review_cadence`, `quarterly` added,
  `ongoing` retired.
- `_data/projects/*.json` — 33 files renamed, three reassigned.
- `test/test_schemas.py` — 117 tests.

## Verification

Both commands in the phase's `verification` list, run in the worktree after the rebase onto `dev`:

- `uv run pytest test/test_schemas.py` — 117 passed.
- `uv run python -m src.governance` — exit 0; 15 systems, 42 documents, 7 memories, 78 phases.

Also run, because the phase touches tracked source: `uv run pytest` (227 passed),
`uv run ruff check src/ test/` (clean) and `uv run mypy src/` (clean, 10 files).

The negative assertions were checked to fail for the stated reason rather than incidentally. A
`promised_to` at `inferred` with no flag fails on `required: review_flag` under `promised_to`, and
the same record passes once flagged. `failing_paths` in the test module exists because an
`additionalProperties` error carries no instance path — the offending key lives in the message —
so without recovering the key from the subschema every "names the field" assertion would have
passed vacuously. That was a real defect caught while writing the tests, not a hypothetical.

## Decisions taken in session

**The owner reassigned the three retired cadences.** Two real portfolio projects moved
to `ad-hoc`, one to `weekly`. ADR-008 is explicit that an agent does not pick a
replacement, so these were asked. This satisfies `phase-cap-08`'s cadence scope item early; that
phase's acceptance condition — no project carries a retired value — now holds before it starts.

**The phase was widened twice, both times recorded on `dev` before the work.** First to
`_data/projects`, because renaming the field invalidates every project file and no phase declared
that directory; second to `README.md`, `brain/procedures/add-new-project.md` and `PROMPT-001`,
which still instructed a reader or an agent to write the old field, PROMPT-001 going as far as
offering `ongoing` as a valid choice. The reasoning is in
[GOV-003](../08-governance/GOV-003-backlog-decisions.md).

`schemas/evidence.schema.json` was also added to the deliverable list. The phase's scope called for
a shared evidence shape but the list never named a file for it, and the alternative — repeating the
shape inside all nine entity schemas — is the duplicate bookkeeping the protocol forbids.

## Unresolved

- **`_data/projects` files are validated by a test, not by the loader.** `tools/rebuild_db.py` still
  reads `p.get("commitment_cadence")` and will now write null for every project. That is
  `phase-cap-07`'s work and is deliberately out of scope here, but until it runs the projection
  carries no cadence at all. The next agent to rebuild the database should not read that as data
  loss.
- **`owed_by` on `waiting-on` is not a protected field.** It is the structural mirror of
  `promised_to`, which is protected, and the same argument for not inventing who a promise was made
  to applies to who owes the owner something. ADR-007 fixes the protected set at four things and
  this is not one of them, so it was left alone rather than widened by an agent. Worth deciding
  before `phase-cap-05` scores evidence against it.
- **Corrections have no shape yet.** REQ-002 R15 requires a promoted record to carry dated
  correction entries, and no entity schema has a field for them. This was excluded on purpose: the
  phase's scope says a promoted record carries *only* a capture reference and the assumed-field
  list. `phase-cap-06` owns corrections and will need to add the field to all nine schemas.
- **`capture_id` has no format.** It is constrained only to a non-empty string, because
  `phase-cap-03` owns the raw capture identifier and pre-empting it would settle that decision
  here by accident.
