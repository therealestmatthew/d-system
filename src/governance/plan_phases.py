"""Plan-versus-registered check: plans and backlog phases must name each other (REQ-028 R09).

Two directions with different reach (PLAN-045 D8). A phase registered with `plan: <id>` must be
named by id somewhere in that plan's text, but only for plans created on or after 2026-09-22:
older plans predate the rule and 25 of them would fail. A `phase-...` id named in any plan's text
must be registered in the backlog, for every plan.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping
from datetime import date
from typing import Any

# The first plan date the named-phase direction applies to (PLAN-045 D8, GOV-010's scope).
CUTOFF = date(2026, 9, 22)
# The backlog schema's phase id pattern, bounded so `phase-abc-123` is not read as `phase-abc-12`.
PHASE_ID = re.compile(r"\bphase-[a-z]+-[0-9]{2}\b")


def named_phases(text: str) -> set[str]:
    """Every phase id written anywhere in a plan's text."""
    return set(PHASE_ID.findall(text))


def inspect_plan_phases(
    documents: Mapping[str, Mapping[str, Any]],
    items: Iterable[Mapping[str, Any]],
    read_text: Callable[[str], str],
) -> tuple[list[str], dict[str, int]]:
    """Return errors for both directions, and the counts that show what was checked."""
    # audit() gives every real document its path. A record without one has no text to read: only
    # tests that build the documents mapping by hand produce it, and they are not plans to check.
    plans = {
        key: meta
        for key, meta in documents.items()
        if meta.get("kind") == "plan" and "path" in meta
    }
    phases = list(items)
    registered = {item["id"] for item in phases}
    named = {key: named_phases(read_text(meta["path"])) for key, meta in plans.items()}
    recent = {
        key for key, meta in plans.items() if date.fromisoformat(str(meta["created"])) >= CUTOFF
    }
    errors: list[str] = []
    checked = 0
    for item in phases:
        plan = item.get("plan")
        if plan not in recent:
            continue
        checked += 1
        if item["id"] not in named[plan]:
            errors.append(
                f"{plans[plan]['path']}: registered phase {item['id']} is not named in its plan "
                f"{plan}"
            )
    mentions = 0
    for key, ids in named.items():
        mentions += len(ids)
        for phase_id in sorted(ids - registered):
            errors.append(f"{plans[key]['path']}: names unregistered phase {phase_id}")
    counts = {
        "plans": len(plans),
        "recent_plans": len(recent),
        "registered_phases_checked": checked,
        "phase_ids_named": mentions,
    }
    return sorted(errors), counts
