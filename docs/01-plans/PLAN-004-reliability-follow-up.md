---
schema_version: 1
id: doc-reliability-follow-up
code: PLAN-004
title: Source integrity and projection reliability follow-up
kind: plan
status: approved
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-contracts, sys-projection, sys-retrieval, sys-delivery]
depends_on: [doc-system-audit]
---

> Delivery is approved in phases. The [accepted user choices](../08-governance/GOV-003-backlog-decisions.md) resolve conflicting details below; the [session backlog](../09-backlog/README.md) tracks execution and completion. This document is a design source, not evidence of implementation.

# Source integrity and projection reliability follow-up

## Outcome and scope

Make invalid source data fail before it can damage a usable projection, and document/test retrieval behavior. This is proposed follow-up to the architectural audit, not an implementation claim. Page generation, memory agents and SQL portfolio signals stay in their own plans.

## Ordered work and acceptance

| Step | Change | Acceptance evidence required |
|---|---|---|
| 1 | Repair the existing `typing.Generator` lint issue | Existing `uv run ruff check src/ test/` passes |
| 2 | Validate all JSON and memory sources before destructive SQL; check relationships and global task IDs | Invalid date, unknown tag/person/project, duplicate task ID and malformed memory tests return source diagnostics without altering the prior DB |
| 3 | Decide transaction or temporary-build/publication strategy in an ADR | Failed mid-load rebuild leaves the old projection queryable; repeated successful rebuilds preserve expected rows; connection cleanup verified |
| 4 | Resolve project membership authority and database path consistency | Conflicting membership and alternate-working-directory tests demonstrate the accepted semantics |
| 5 | Define global-memory and `--all` semantics | Tests cover repository-scoped/global/project memories, multi-tag conjunction, and more than 10 entries |
| 6 | Expand CI coverage to loader/retrieval tooling after correcting their baseline issues | Focused tests and agreed lint/type scope pass without writing the repository database |

## Dependencies and review

Steps 2–3 form one reliability outcome but can be separate reviewable changes. Step 4 needs a data contract decision before changing source shapes. Steps 1 and 5 can proceed independently. Update schemas first for any entity change, followed by SQL and models where applicable. Run data tests in temporary databases. Mark this plan complete only after implementation and test paths are recorded in `completion_evidence` with actual results.

## Open decisions

- Which projection publication approach fits local readers and filesystem behavior?
- Is `scope: global` the retrieval authority, or is repository-scoped context a separate class?
- Which side of project/person membership is canonical?
