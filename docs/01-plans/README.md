# Plans

Implementation plans for upcoming features and systems. Name files descriptively: `YYYY-MM-DD-topic.md`.

Use the [document template](../../templates/governance/document.md) and
[governance protocol](../08-governance/GOV-001-protocol.md). Multi-file plans use a `parent`
reference to their overview. New plans start as drafts; existing root `plans/` paths
remain for compatibility. Run `uv run python -m src.governance --inventory` to list open plans.

Every open plan must be covered by the [session backlog](../09-backlog/README.md).
Add or update its phases before implementation; validate with `uv run python -m src.governance`.

- [Document code system](PLAN-005-document-code-system.md): deterministic document codes, allocation commands and the backfill of existing documents.
- [Confidentiality sweep](PLAN-006-confidentiality-sweep.md): separate structure from portfolio content before the first remote push.
- [Capture and structuring system](PLAN-007-capture-and-structuring-system.md): discovery plan; its first phase runs the definition session.
- [Session lifecycle protocols](PLAN-008-session-lifecycle-protocols.md): what each session type loads at open, and what every session owes at close.
- [Idea priority queue](PLAN-019-idea-priority-queue.md): an ordered next_up list for open ideas, sitting beside the append-only idea log rather than inside it.
