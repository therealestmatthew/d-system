---
schema_version: 1
id: doc-adr-document-codes
code: ADR-006
title: Per-kind document codes alongside semantic identifiers
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-governance]
depends_on: [doc-document-code-requirements]
---

# ADR-006: Per-kind document codes alongside semantic identifiers

## Status

Accepted.

## Context

Governed documents carried one identifier, a semantic slug such as `doc-mini-systems`, and their
filenames followed three unrelated conventions at once: `YYYY-MM-DD-topic.md` for plans,
`NNN-topic.md` for ADRs, and bare slugs for architecture. No rule said what number a new document
received, no counter existed per category, and a directory listing did not reveal what a document
was or where it sat in its series.

The gap already bound. `docs/09-backlog/backlog.yaml` listed `004-membership-authority.md` and
`005-projection-publication.md` as deliverables of `phase-rel-04` and `phase-rel-05`, so two ADR
numbers were claimed before either document existed, with nothing to stop a third document taking
them.

## Decision

Every governed document carries a `code` from a series registered for its kind. The code is the
filename prefix, and the register at `docs/08-governance/codes.yaml` holds the series definitions,
reservations and retirements that make allocation deterministic.

**Codes sit alongside `doc-*` identifiers rather than replacing them.** The slug stays the
referential key used by `depends_on`, `parent`, `supersedes` and the backlog's `plan` and `sources`
fields. The code is the catalog number: human-facing, filename-bearing, ordered within its series.

**Allocation reads a register, not just existing documents.** `next(series)` is the highest number
among documents, reservations and retirements, plus one.

**Counter series and dated series both exist.** Plans, ADRs, architecture, requirements, prompts,
operations and governance take counter codes. Sessions and walkthroughs take date-derived codes of
the form `SESS-2026-09-05-01`.

**Child plans take dotted sub-codes** under their parent, and the sub-code and the `parent` field
must imply each other.

**Codes are permanent.** A code is never reused or renumbered once it reaches `dev`. Superseded and
deprecated documents keep theirs; a deleted document's code moves to the retired list.

## Alternatives considered

**Replace `doc-*` ids with codes.** One identity per document, nothing to keep in sync. Rejected
because it rewrites every cross-reference in a 1560-line backlog, four schemas and roughly twenty
documents, for a benefit that is aesthetic rather than functional. The slug also carries meaning a
number cannot: `doc-adr-multi-agent-concurrency` survives a reader who has never seen the register.

**Derive the next code by scanning documents alone, with no register.** Simpler, one less file.
Rejected because the repository already reserves ADR-004 and ADR-005 through backlog deliverables. A
pure maximum scan would hand those numbers to unrelated documents, and a deleted document would free
its number for recycling.

**A global counter for sessions too.** Uniform, one rule with no exceptions. Rejected on the
evidence: `max_active` is 3, every completed phase requires a session record, and 59 open phases
imply at least 59 session documents against 24 in every other category combined. A shared counter
would contend precisely where several agents write at once, and its order could contradict the date
order when branches merge out of sequence.

**Sub-codes as a flat sequence with `parent` alone expressing containment.** Simpler counter.
Rejected because a seven-document plan set then scatters across the series, and the grouping is
invisible in a directory listing — the problem this decision exists to solve.

## Consequences

A directory listing now answers what a document is and where it sits. Allocation is one command, and
its answer is a pure function of committed state, so two agents on the same commit agree.

Two identifiers exist per document. The mapping is one-directional — a code resolves to a document —
and the validator enforces uniqueness on both, but a reader must know which one a given field wants.

Concurrent agents can still collide on a counter code. This is handled by the ADR-003 discipline
rather than a new mechanism: the register on `dev` is the ledger, the governance command is the
check, and the later-integrating agent renumbers. Dated series avoid the contention entirely.

Renaming every governed file moved roughly forty inbound references. That cost is paid once.

## Revisit trigger

Reconsider if a counter collision between concurrent agents happens more than once, which would mean
reservations are not being taken early enough; or if `WALK` remains unused after several
walkthroughs, in which case collapse it into `SESS`.
