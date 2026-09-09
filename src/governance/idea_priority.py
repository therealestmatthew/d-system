"""Validation for docs/00-working/ideas-priority.yaml — no database or state mutations.

The append-only idea log (_data/ideas.jsonl, schemas/idea.schema.json) has no ordering
concept, only status. This is the equivalent of backlog.yaml's next_up for ideas: a plain
ordered list living beside the log, not a new event type inside it.
"""

from __future__ import annotations

from datetime import date
from typing import Any

#: An idea already past scouting has nothing left for this queue to order.
QUEUEABLE_STATES = {"open", "triaged"}


def inspect_idea_priority(
    catalog: dict[str, Any], ideas: dict[str, dict[str, Any]], today: date | None = None
) -> list[str]:
    """Errors in the priority file given the current folded state of the idea log."""
    errors: list[str] = []
    today = today or date.today()

    if date.fromisoformat(catalog["updated"]) > today:
        errors.append("ideas-priority.yaml: updated is in the future")

    for idea in catalog["next_up"]:
        if idea not in ideas:
            errors.append(f"ideas-priority.yaml: next_up names unknown idea {idea}")
            continue
        status = ideas[idea]["status"]
        if status not in QUEUEABLE_STATES:
            errors.append(
                f"ideas-priority.yaml: {idea} is {status}, not open or triaged — remove it "
                "from next_up"
            )
    return errors
