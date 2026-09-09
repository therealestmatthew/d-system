---
schema_version: 1
id: doc-adr-session-backlog
code: ADR-002
title: 'ADR-002: One-session phases in a file-backed backlog'
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-backlog, sys-governance]
depends_on: [doc-adr-file-based-governance]
---

# ADR-002: One-session phases in a file-backed backlog

## Context

The user requested that every open plan be captured before implementation and that every backlog item be one session-sized plan phase. Existing plan documents range from single proposals to a seven-file HTML design. Their lifecycle metadata does not describe executable increments, prerequisites or session handoffs. The saved answers and follow-up clarification settle constraints that supersede conflicting details in earlier proposals.

## Decision

Keep broad design in existing governed plan documents and execution state in `docs/09-backlog/backlog.yaml`, with one strict-schema item per phase. Require bounded scope, acceptance checks, verification, expected deliverables, one-session budget and source-plan links. Derive readiness and coverage instead of storing a separate ordered queue. Permit one active phase for the current maintainer workflow.

Extend the existing governance CLI and CI check to require this catalog, reject unresolved dependencies/cycles and uncovered open plans, and require evidence plus a session record for completion. Preserve deliberately deferred work in the catalog with explicit release conditions. Add an accepted-choice record linking the user's raw answers, which remain unmodified under an exact scanner exemption.

This extends ADR-001's file-based approach. Backlog metadata is not business data and requires no DuckDB table, DDL migration or application Pydantic model. JSON Schema is defined first, followed by the development validator and tests.

## Alternatives

| Alternative | Tradeoff |
|---|---|
| Only checkboxes in each large plan | Simple locally, but shared dependencies, global readiness and missed plans are difficult to detect |
| One Markdown file per phase with full document metadata | Duplicates parent-plan metadata and adds dozens of navigation files before implementation |
| External issue tracker | Adds another authority and account/service dependency for a single-maintainer repository |
| Store ready/blocked state solely by hand | Readiness drifts whenever a dependency changes |

## Consequences

The YAML catalog is longer than a summary board but each item has enough context to start a session. Readable boards are generated on demand. Semantic coverage and session sizing still require review; the validator checks structure, not effort estimates or engineering truth. One-active-phase enforcement can be revisited when the user explicitly adopts multiple simultaneous work streams; [ADR-003](ADR-003-multi-agent-concurrency.md) does exactly that and amends only this clause. Current work captures and validates the backlog; it does not implement the queued product phases.
