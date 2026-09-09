# Repository governance

- [Protocol](GOV-001-protocol.md): metadata, ownership, lifecycle, taxonomy and enforcement.
- [Architecture audit](../07-architecture/ARCH-002-system-audit.md): code evidence and plan gaps.
- [Systems registry](systems.yaml): component responsibilities, maturity and dependencies.
- [Operations](OPS-001-operations.md): commands, authoring and failure recovery.
- [Document codes](GOV-005-document-codes.md): series, allocation, reservation and permanence.
- [Code register](codes.yaml): series definitions, reserved and retired codes.
- [Catalog](catalog.md): generated index of every document, its code and its phases.
- [ADR-001](../04-decisions/ADR-001-file-based-governance.md): design rationale.
- [ADR-006](../04-decisions/ADR-006-document-codes.md): why codes sit alongside `doc-*` ids.

Run `uv run python -m src.governance --inventory` for a derived inventory of open plans.

- [Session backlog](../09-backlog/README.md): all open plans split into one-session phases.
- [Accepted choices](GOV-003-backlog-decisions.md): saved questionnaire answers and the selected blend.
- [Backlog workflow](GOV-002-backlog-protocol.md): readiness, coverage, concurrency and session completion.
- [ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md): concurrent agents, worktrees and claims.
