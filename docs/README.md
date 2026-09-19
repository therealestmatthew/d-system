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

## Parked: the portable framework drafts

Draft templates and agent specifications for generalizing this repository's
multi-developer agentic workflow into a portable framework live at
[`00-working/framework/`](00-working/framework/README.md), **not** at `docs/framework/`.

They were staged under `docs/00-working/` because their front matter is
placeholder text (`PLAN-NNN`, `YYYY-MM-DD`) that can never satisfy the governed
document schema. `docs/00-working/` is exempt from those rules by
[ADR-010](04-decisions/ADR-010-idea-staging.md); anywhere else under `docs/`
they make the governance check fail.

The work they belong to is captured as ideas `000269`-`000281`, anchored on
`000281` (portable starter kit). Nothing there has earned a code yet.
