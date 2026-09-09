# Documentation

Start with the [current architecture audit](07-architecture/ARCH-002-system-audit.md)
and [governance protocol](08-governance/GOV-001-protocol.md).

- [Plans](01-plans/README.md) describe intended work; check their front-matter status.
- [Decisions](04-decisions/README.md) record architectural rationale.
- [Shared memory](../brain/index.md) holds cross-session context.
- [Governance operations](08-governance/OPS-001-operations.md) explain validation and inventory.

Run `uv run python -m src.governance --inventory` for current components and open plans.

[Session backlog](09-backlog/README.md) captures every open plan as bounded phases.
Use `uv run python -m src.governance --ready` to find eligible work before starting a session.
