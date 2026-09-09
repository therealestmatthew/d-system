---
schema_version: 1
id: doc-capture-requirements
code: REQ-002
title: Capture and structuring requirements
kind: requirement
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-08'
systems: [sys-capture, sys-contracts, sys-portfolio, sys-projection]
depends_on: [doc-governance-protocol, doc-capture-routing, doc-record-types]
---

# Capture and structuring requirements

Observable requirements for getting information into this system. Each states what must be true and
how to verify it. The decisions behind them are in [ADR-007](../04-decisions/ADR-007-capture-routing.md)
and [ADR-008](../04-decisions/ADR-008-record-types.md); the build order is in
[PLAN-009](../01-plans/PLAN-009-capture-build.md). **R1, R2 and R5 are implemented** (raw-only CLI
and inbox intake, `phase-cap-04`); everything else — structuring, routing, review, promotion and
the entity model — is still proposed only.

## Problem being solved

The portfolio holds 33 projects and 28 tags, and zero people, commitments or tasks. There is no
intake path of any kind. Fourteen phases in the `phase-sig-*` and `phase-syn-*` tracks read
commitment data, so today they would be built and verified against empty tables.

The owner is the sole contributor and stated two priorities in order: **zero broken promises**, then
**nothing went quiet**. Capture completeness is explicitly not expected to reach 100%.

## Accepted decisions

Settled with the owner in the definition session; implementation does not reopen them.

| Decision | Choice |
|---|---|
| Raw text | Immutable, stored before interpretation, referenced by every derived record |
| Channels | Conversational session, inbox directory, CLI quick-capture — one pipeline |
| Confidence | Scored per field, with provenance into the raw capture |
| Protected fields | `promised_to`, `due_date`, decision and rationale, completion — assumable, never silently |
| Routing | clean / flagged / held, on record stakes crossed with evidence level |
| Interruption | Never; ambiguity queues, capture does not block on the owner |
| Write boundary | Staging, promoted into `_data/` by an explicit owner action |
| Privacy | Private by default; only deliberately promoted records are tracked |
| Tags | New tags allowed inside existing categories with an alert; new categories held |
| Entities | Nine types; tasks first-class with optional parents |
| Cadence | `review_cadence` is policy, `last_touched` is derived, `ongoing` retired |

## Requirements

### Capture

**R1 — Raw text survives interpretation.** Every capture is written to the raw store with an
identifier and a timestamp before any structuring runs, and is byte-identical to what was submitted.
*Verify:* submit a capture through each channel; assert the stored raw record matches the input
exactly and predates any derived record.

**R2 — Raw text is never mutated.** No code path edits or deletes a raw capture. A correction to a
derived record leaves its raw source unchanged.
*Verify:* apply a correction to a structured record; assert the referenced raw record's content hash
is unchanged.

**R3 — Every structured record names its source.** A record produced by capture carries a resolvable
reference to the raw capture it derives from.
*Verify:* validation rejects a staged record whose source reference is absent or unresolvable.

**R4 — All three channels converge.** The same text submitted conversationally, through the inbox and
through the CLI produces the same routing decision and the same field-level evidence levels.
*Verify:* submit one fixture through all three channels; assert identical routing and evidence.

**R5 — Quick capture is a single command.** CLI capture of a free-text fragment requires one command
and no arguments beyond the text.
*Verify:* the documented command in `docs/08-governance/OPS-008-capture.md` runs and produces a
raw record.

### Structuring

**R6 — Evidence is recorded per field.** Every agent-filled field carries `explicit`, `inferred` or
`guessed`, plus provenance locating the supporting text in the raw capture.
*Verify:* schema validation rejects a staged record with an agent-filled field lacking either.

**R7 — Protected fields are never silently populated.** `promised_to`, `due_date`, a decision's
existence or rationale, and any completion state are rejected when populated at a non-explicit
evidence level without a review flag.
*Verify:* a fixture whose text omits a deadline, structured into a record with a `due_date` at
`inferred` and no flag, fails validation with the field named.

**R8 — Routing follows the table.** A record's route is exactly `clean` when all fields are explicit
and its type is low or medium stakes; `flagged` when any field is non-explicit or its type is high
stakes; `held` when it would create a new person, project, tag or tag category.
*Verify:* a fixture set covering each cell of the stakes-by-evidence matrix produces the stated route.

**R9 — Capture never blocks.** No capture path waits on owner input to complete. Ambiguity produces a
flagged record, not a prompt.
*Verify:* process an ambiguous inbox fixture non-interactively; assert it completes and yields a
flagged record.

**R10 — New identities are not created unaided.** Processing a capture naming an unknown person,
project or tag creates no such record; the reference is retained as text and the item is held.
*Verify:* process a fixture naming an unknown person; assert `_data/people/` and staging contain no
new person record and the item's route is `held`.

**R11 — New tags alert, new categories block.** A new tag inside one of the six existing categories is
created with an alert in review; a tag requiring a new category is held.
*Verify:* two fixtures, one per case, produce an alerted tag and a held item respectively.

### Review and promotion

**R12 — Nothing reaches `_data/` without an owner action.** No capture path writes to `_data/`.
*Verify:* run every capture path against a fixture tree; assert `_data/` is byte-identical afterward.

**R13 — Clean items promote in bulk.** One owner action promotes all clean staged records, and
promotes no flagged or held record.
*Verify:* stage a mixed batch, run bulk promotion, assert only clean records moved.

**R14 — Review shows the claim, not the record.** For each flagged item, review displays the raw text,
the proposed record, each assumed field and the reason for the assumption, ordered by stakes.
*Verify:* inspect review output for a mixed batch; assert every flagged field appears with its
provenance and that high-stakes items sort first.

**R15 — Corrections are dated and preserved.** Correcting a promoted record appends a dated correction
entry naming the field, the previous value and the new one.
*Verify:* correct a record; assert the correction entry exists and the prior value is still readable.

### Privacy

**R16 — Raw and staging are untracked.** The raw store and the staging area are gitignored, and a
clean checkout after a capture run shows no new tracked files.
*Verify:* run a capture, then `git status --porcelain`; assert no untracked-but-unignored or staged
paths from capture.

**R17 — Promotion is the only path into tracked data.** A record enters version control only through
the promotion step.
*Verify:* the leak check from `phase-priv-04` passes against a tree containing captured content.

### Entity model

**R18 — Tasks exist without parents.** A task validates and loads with neither `commitment_id` nor
`project_id`, with one, or with both.
*Verify:* four task fixtures covering each combination validate and appear in the `tasks` table.

**R19 — Parentless records stay visible.** A view lists every task, commitment and other record with
no project association.
*Verify:* the unfiled query returns exactly the parentless fixtures.

**R20 — The four new types round-trip.** Interaction, decision, waiting-on and development-event
records validate against their schemas, load into their tables, and survive a rebuild unchanged.
*Verify:* fixtures for each type; rebuild; compare loaded rows to source JSON.

**R21 — Staleness is computed, not stored.** `last_touched` exists only in the projection, derived as
the latest activity across a project's interactions, commitments, tasks and decisions. No `_data/`
file contains it.
*Verify:* grep `_data/` for the field; assert absent. Add an interaction to a fixture project;
rebuild; assert `last_touched` advances.

**R22 — `review_cadence` defines the staleness threshold.** A project whose `last_touched` is older
than its cadence appears in the stale set; one inside its cadence does not.
*Verify:* fixtures on both sides of each cadence boundary produce the expected membership.

**R23 — `ongoing` is rejected.** `review_cadence: ongoing` fails schema validation.
*Verify:* a fixture using it fails with the field named.

**R24 — `last_reviewed` stays independent.** Activity on a project advances `last_touched` and leaves
`last_reviewed` unchanged.
*Verify:* add an interaction to a fixture project; rebuild; assert only `last_touched` moved.

### Downstream unblocking

**R25 — The signal and synthesis tracks have data.** After the seeding phase, `commitments`,
`interactions` and `tasks` are non-empty, so `phase-sig-02` through `phase-sig-06` and
`phase-syn-01` through `phase-syn-04` can be verified against real rows.
*Verify:* row counts are non-zero after a rebuild, recorded in the seeding phase's session record.

## Open questions

**Durable storage and backup.** The captured record will become the most valuable and least
replaceable content in the repository, and it lives on one local disk. Postgres, Supabase and
Firebase were all raised. *Deferred by owner decision; revisit once capture is real* — that is, once
sustained captured data exists that would genuinely hurt to lose. No phase is scheduled.

**Scheduled prompting.** The owner wants morning, end-of-day, weekly and pre-call outputs eventually,
but capture is ad hoc for now and nothing schedules itself. *Revisit once the review loop is in daily
use*; until then the session lifecycle work in `phase-ses-*` is the nearer path.

**Three projects hold a retired cadence.** They cannot be reassigned by an agent. *Resolved by the
owner during the schema phase; the phase carries the flag.*
