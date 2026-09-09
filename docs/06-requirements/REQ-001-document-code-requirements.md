---
schema_version: 1
id: doc-document-code-requirements
code: REQ-001
title: Document code assignment requirements
kind: requirement
status: active
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-governance]
depends_on: [doc-governance-protocol]
---

# Document code assignment requirements

Observable requirements for a deterministic per-category document code scheme. Each
requirement states what must be true and how to verify it. These requirements are the
agreed contract; [the implementation plan](../01-plans/PLAN-005-document-code-system.md)
describes how and when they are met. Nothing here is implemented yet.

## Problem being solved

Governed documents currently carry only a semantic identifier (`id: doc-mini-systems`) and
their filenames follow three unrelated conventions at once: `YYYY-MM-DD-topic.md` for plans,
`NNN-topic.md` for ADRs, and bare slugs for architecture. No rule says what number a new
document receives, no counter exists per category, and a directory listing does not reveal
where a document sits in its series.

The gap already has a concrete consequence: `docs/09-backlog/backlog.yaml` reserves
`docs/04-decisions/ADR-004-membership-authority.md` and `ADR-005-projection-publication.md` as phase
deliverables. Two ADR numbers are claimed by backlog phases before either document exists,
with nothing preventing a third document from taking them.

## Accepted decisions

These four choices were made by the owner and are not reopened by implementation.

| Decision | Choice |
|---|---|
| Identity | Add a `code` field; keep `id: doc-*` as the referential key used by `depends_on`, `parent`, `supersedes` and backlog `plan`/`sources` |
| Filenames | Rename files so the code is the filename prefix, enforced by the validator |
| Coverage | All nine document kinds get a series |
| Multi-file plans | Child plans take dotted sub-codes under their parent |
| Session numbering | Sessions and walkthroughs take date-derived codes, not a global counter |
| Catalog | The catalog is committed as a generated file and kept current by a CI drift check |

## Requirements

### R1 — Every governed document carries a code

Every Markdown file validated under `docs/` has a `code` field. Two grammars exist,
because two kinds are numbered differently:

- Counter series: `^(PLAN|ADR|ARCH|REQ|PROMPT|OPS|GOV)-[0-9]{3}(\.[0-9]{2})?$`
- Dated series: `^(SESS|WALK)-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}$`

Sessions and walkthroughs use the dated form because they are the only kinds written concurrently
by several agents and the only kinds whose volume tracks phase completions rather than deliberate
authoring. A global counter would contend precisely where contention is most likely.

*Verification:* `uv run python -m src.governance` exits 0 and reports the full document count;
removing `code` from any one document produces an error naming that file.

### R2 — Codes are unique

No two governed documents share a code.

*Verification:* a fixture with two documents holding the same code fails with a duplicate-code
error naming both paths.

### R3 — The series matches the kind

A document's series prefix is the one registered for its `kind`, and the file sits under one of
that series' registered locations.

*Verification:* an `adr` document carrying a `PLAN-` code fails; an ADR placed outside
`docs/04-decisions/` fails.

### R4 — Allocation is deterministic

For a counter series, the next free code is a pure function of committed repository state: the
highest number used by a governed document, a reservation, or a retirement, plus one. For a dated
series, the code is the document's date plus the next unused sequence number within that date, so
agents working on different days never contend and agents working the same day contend only with
each other. Two agents computing the next code from the same commit obtain the same answer.

*Verification:* `uv run python -m src.governance --next-code <kind>` prints one code and
nothing else; running it twice against an unchanged tree prints the same value.

### R5 — Codes can be reserved before their document exists

A code may be claimed in the register before the document is written, and the counter skips it.
This preserves the existing ADR-004 and ADR-005 claims made by `phase-rel-04` and `phase-rel-05`.

*Verification:* with ADR-004 and ADR-005 reserved, `--next-code adr` skips both; using a reserved
code for an unrelated document fails until the reservation is removed in the same change.

### R6 — Codes are permanent

A code is never reused and never renumbered once it is on `dev`. Superseded and deprecated
documents keep their codes. A deleted document's code moves to the register's retired list.

*Verification:* a retired code reused by a new document fails validation.

### R7 — Filenames agree with codes

A document's filename begins with its code. A multi-file plan folder is named for the parent code
and contains only that parent's code and its sub-codes.

*Verification:* renaming a governed file so its prefix no longer matches its `code` fails with an
error naming the file and the expected prefix.

### R8 — Sub-codes and parentage are mutually consistent

A dotted sub-code implies a `parent`, its stem equals the parent's code, and a plan declaring a
`parent` carries a sub-code of that parent.

*Verification:* a sub-code without `parent` fails; a sub-code whose stem is not the parent's code
fails; a child plan with a top-level code fails.

### R9 — Concurrent allocation collisions are caught, not silently merged

Two agents that independently take the same code produce a validation error when the second
integrates, using the existing lock-check discipline rather than a new mechanism.

*Verification:* a fixture holding two documents with the same code fails the same command that
gates a backlog claim.

### R10 — One report shows what exists and what is in progress

A single command lists every governed document with its code, kind, lifecycle status and owner,
joined with its backlog phase state, plus the reserved and retired codes.

*Verification:* `uv run python -m src.governance --catalog` renders a deterministic Markdown
report covering every document and reflects a phase status change on the next run.

### R11 — Existing documents are backfilled

Every document that exists before this work carries a code, and every file rename is accompanied
by an update to every inbound reference in the same change.

*Verification:* after the backfill, `uv run python -m src.governance` exits 0, `systems.yaml` path
checks pass, and no repository Markdown link resolves to a renamed path.

### R12 — The catalog is committed and cannot go stale

The catalog is committed as a generated file so it is readable without a checkout or a Python
environment. It is never hand-edited, and CI regenerates it and fails on any difference, so a
stale catalog is a build failure rather than silent misinformation.

*Verification:* CI regenerates the file and `git diff --exit-code` reports no change; editing the
committed file by hand, or changing a document without regenerating, turns the build red.

## Out of scope

Codes do not replace `doc-*` identifiers, do not change the memory schema under `brain/`, and do
not introduce a scheduler, service or database. Portfolio entities in `_data/` keep their own
identifier namespace.
