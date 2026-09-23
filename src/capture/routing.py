"""The clean / flagged / held routing table — ADR-007 section 5, REQ-002 R8/R10.

Stakes are a property of the record type. The route is the whole policy:

- **held** — the record is itself a new durable identity (person, project, tag, tag
  category), or it references one that does not exist yet. An identity call the agent may
  not make, so this outranks everything else.
- **flagged** — any field is inferred or guessed, or the type is high stakes.
- **clean** — every field explicit and the type low or medium stakes.

Reversibility and channel are deliberately absent: staging already guarantees the first,
and the second changes only when the owner sees a flag, never whether one is raised.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

Route = Literal["clean", "flagged", "held"]
Stakes = Literal["low", "medium", "high", "structural"]

#: ADR-007's stakes table, keyed by staged `entity_type`. `note` is the raw-note tier: a
#: capture kept as a note with no richer type. A new tag is structural whatever its
#: category — the owner ruled on 2026-09-22 that this phase holds every new tag, leaving
#: REQ-002 R11's alert-and-create path for review (phase-cap-06).
STAKES: dict[str, Stakes] = {
    "note": "low",
    "task": "low",
    "commitment": "medium",
    "interaction": "medium",
    "waiting-on": "medium",
    "development-event": "medium",
    "decision": "high",
    "person": "structural",
    "project": "structural",
    "tag": "structural",
    "tag-category": "structural",
}


class RoutingError(ValueError):
    """A record could not be routed because its type is not in the stakes table."""


def stakes_for(entity_type: str) -> Stakes:
    try:
        return STAKES[entity_type]
    except KeyError:
        raise RoutingError(
            f"unknown entity_type {entity_type!r}; expected one of {sorted(STAKES)}"
        ) from None


def route_for(
    entity_type: str, levels: Iterable[str], unresolved_references: bool = False
) -> Route:
    """Return the route for a record of `entity_type` whose fields carry `levels`.

    `unresolved_references` is true when a field names a person, project or tag that does
    not exist — REQ-002 R10 holds the item rather than creating the identity.
    """
    stakes = stakes_for(entity_type)
    if stakes == "structural" or unresolved_references:
        return "held"
    if stakes == "high" or any(level != "explicit" for level in levels):
        return "flagged"
    return "clean"
