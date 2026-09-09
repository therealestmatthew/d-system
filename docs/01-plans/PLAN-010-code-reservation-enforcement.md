---
schema_version: 1
id: doc-code-reservation-enforcement
code: PLAN-010
title: Enforce document code reservations mechanically
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-backlog]
depends_on: [doc-governance-protocol, doc-document-codes]
---

# Enforce document code reservations mechanically

## Context and scope

On 2026-09-06 two phases claimed `ADR-007`. `PLAN-006` stated in prose that the code was allocated to
the structure/content boundary, but never recorded it under `reserved` in `codes.yaml`, so
`--next-code adr` correctly issued `ADR-007` to an unrelated decision hours before the boundary ADR
was written. The collision and its resolution are recorded in
[GOV-003](../08-governance/GOV-003-backlog-decisions.md).

The rule was never missing. [GOV-005](../08-governance/GOV-005-document-codes.md) already says to
reserve a code when a backlog phase names it as a deliverable, and
[REQ-001](../06-requirements/REQ-001-document-code-requirements.md) states that codes are permanent. What is
missing is any check that notices when the rule is skipped — so a code claimed only in prose looks
identical to one properly reserved, until the allocator hands it to someone else.

`ADR-004` and `ADR-005` are correctly reserved and did not collide, which is the evidence that the
mechanism works when used. This plan makes using it non-optional.

Out of scope: changing how codes are allocated, renumbering anything already merged, and the
permanence rule itself. None of those failed.

## Work

### Phase 1 — reject unreserved code claims (`phase-gov-01`)

Extend the governance validator so that every backlog `deliverables` entry whose filename matches a
governed code pattern is checked against two sources: the set of existing governed documents, and the
`reserved` list in `codes.yaml`. A deliverable naming a code that is neither an existing document nor
a reservation fails the check, naming the phase, the code and the file.

The failure message must say what to do — reserve the code in `codes.yaml` with the claiming phase —
because the rule's whole failure mode is that skipping it looks like nothing happened.

Two cases must not fail. A phase whose deliverable is an already-written document is legitimate; so is
a deliverable path that carries no code at all, such as `AGENTS.md` or `docs/09-backlog/backlog.yaml`.

## Acceptance and verification

```bash
uv run python -m src.governance
uv run pytest
```

A fixture backlog claiming an unreserved code must fail with the phase and code named. The current
repository must continue to pass unchanged: `phase-rel-04` and `phase-rel-05` name `ADR-004` and
`ADR-005`, which are reserved, and `phase-priv-01` now names `ADR-009`, which exists.

## Open questions

Whether the same check should cover codes named in plan *prose* rather than only in backlog
deliverables. That is what actually happened here — `PLAN-006`'s claim was in a sentence, not in a
deliverable path. Scanning prose for code-shaped strings would catch it, and would also fire on every
legitimate cross-reference to an existing document. Deferred: implement the deliverables check first
and see whether prose claims recur once the mechanical path is enforced.
