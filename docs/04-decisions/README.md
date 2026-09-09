# Architecture Decision Records (ADRs)

Documents non-obvious design decisions so future contributors understand the why. Template:

```
# ADR-NNN: Title

## Status
Accepted | Deprecated | Superseded by ADR-NNN

## Context
What situation forced a decision?

## Decision
What was decided?

## Consequences
What are the trade-offs?
```

New ADRs also need front matter from the [governance protocol](../08-governance/GOV-001-protocol.md).
Use lowercase metadata statuses (`draft`, `accepted`, `deprecated`, `superseded`);
metadata is authoritative if a historical body uses a display label.

- [ADR-001: File-based governance](ADR-001-file-based-governance.md)
- [ADR-002: One-session backlog phases](ADR-002-session-backlog.md)
- [ADR-003: Worktree-isolated concurrent agents](ADR-003-multi-agent-concurrency.md)
- [ADR-006: Per-kind document codes](ADR-006-document-codes.md)
