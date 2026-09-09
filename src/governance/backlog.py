"""Backlog consistency and derived session queues; no database or state mutations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from datetime import date
from graphlib import CycleError, TopologicalSorter
from itertools import combinations
from pathlib import PurePosixPath
from typing import Any

OPEN_PLANS = {"draft", "approved", "active"}
# States that legitimately hold a worktree; every other state must release its claim.
CLAIMED_STATES = {"active", "blocked", "complete"}


def path_conflict(left: str, right: str) -> bool:
    """True when two declared paths are equal or one contains the other."""
    first, second = PurePosixPath(left).parts, PurePosixPath(right).parts
    return first[: len(second)] == second or second[: len(first)] == first


def dependency_closure(key: str, items: dict[str, Any]) -> set[str]:
    """Transitive prerequisites of one phase; terminates even on a cyclic graph."""
    seen: set[str] = set()
    stack = list(items[key]["depends_on"])
    while stack:
        node = stack.pop()
        if node in seen or node not in items:
            continue
        seen.add(node)
        stack.extend(items[node]["depends_on"])
    return seen


def collisions(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    """Reasons two phases cannot be worked simultaneously; empty means they are disjoint."""
    shared = sorted(set(left["systems"]) & set(right["systems"]))
    reasons = [f"share system {system}" for system in shared]
    reasons += [
        f"share deliverable path {path}"
        for path in sorted(
            {
                max(first, second, key=len)
                for first in left["deliverables"]
                for second in right["deliverables"]
                if path_conflict(first, second)
            }
        )
    ]
    return reasons


def concurrency_errors(items: dict[str, Any], active: list[str], max_active: int) -> list[str]:
    """Allow several active phases only while their work areas cannot overlap."""
    errors = []
    if len(active) > max_active:
        errors.append(
            f"backlog: at most {max_active} phases may be active at once; {len(active)} found"
        )
    for agent, count in sorted(Counter(items[key].get("agent", "") for key in active).items()):
        if not agent:
            if max_active > 1:
                errors.append("backlog: every concurrent active phase requires an agent claim")
        elif count > 1:
            errors.append(f"backlog: agent {agent} holds {count} active phases; claim only one")
    for left, right in combinations(active, 2):
        errors += [
            f"{left}/{right}: concurrent phases {reason}"
            for reason in collisions(items[left], items[right])
        ]
        if right in dependency_closure(left, items) or left in dependency_closure(right, items):
            errors.append(f"{left}/{right}: concurrent phases are dependency-linked")
    return errors


def claim_conflicts(item: dict[str, Any], items: dict[str, Any]) -> list[str]:
    """Active phases that a candidate phase would collide with if claimed now."""
    return sorted(
        key
        for key, other in items.items()
        if other["status"] == "active" and key != item["id"] and collisions(item, other)
    )


def inspect_backlog(
    catalog: dict[str, Any],
    documents: dict[str, Any],
    systems: set[str],
    owners: set[str],
    check_file: Callable[[str], bool],
    today: date,
) -> list[str]:
    """Check a schema-validated catalog against source documents and local evidence."""
    errors = []
    items = {item["id"]: item for item in catalog["items"]}
    if len(items) != len(catalog["items"]):
        errors.append("backlog: duplicate phase ID")
    if date.fromisoformat(catalog["updated"]) > today:
        errors.append("backlog: updated cannot be in the future")
    queue = catalog.get("next_up", [])
    for position, key in enumerate(queue):
        if key not in items:
            errors.append(f"next_up[{position}]: unknown phase {key}")
        elif items[key]["status"] in {"complete", "cancelled"}:
            errors.append(f"next_up[{position}]: {key} is {items[key]['status']}; remove it")
    decision = documents.get(catalog["decision_record"])
    if not decision or decision["kind"] not in {"governance", "adr"}:
        errors.append("backlog: decision_record must reference governance or an ADR")
    covered: set[str] = set()
    active = []
    for key, item in items.items():
        if item["owner"] not in owners:
            errors.append(f"{key}: unknown owner {item['owner']}")
        for system in item["systems"]:
            if system not in systems:
                errors.append(f"{key}: unknown system {system}")
        plan = documents.get(item["plan"])
        if not plan or plan["kind"] != "plan":
            errors.append(f"{key}: primary plan must reference a plan document")
        for source in [item["plan"], *item["sources"]]:
            if source not in documents:
                errors.append(f"{key}: unknown source document {source}")
            elif documents[source]["kind"] == "plan":
                if item["status"] != "cancelled":
                    covered.add(source)
                if documents[source]["status"] in {"complete", "deprecated", "superseded"}:
                    if item["status"] not in {"complete", "cancelled"}:
                        errors.append(f"{key}: unfinished work belongs to closed plan {source}")
        for dependency in item["depends_on"]:
            if dependency not in items or dependency == key:
                errors.append(f"{key}: unresolved or self dependency {dependency}")
            elif item["status"] in {"active", "complete"}:
                if items[dependency]["status"] != "complete":
                    errors.append(f"{key}: prerequisite {dependency} is not complete")
        if item["status"] == "active":
            active.append(key)
        if item.get("agent") and item["status"] not in CLAIMED_STATES:
            errors.append(f"{key}: {item['status']} phase must release its agent claim")
        if item["status"] in {"blocked", "deferred", "cancelled"}:
            if not item.get("blocked_reason", "").strip():
                errors.append(f"{key}: {item['status']} requires blocked_reason")
        if item["status"] in {"blocked", "deferred"}:
            if not item.get("resume_when", "").strip():
                errors.append(f"{key}: {item['status']} requires resume_when")
        if item.get("session"):
            session = documents.get(item["session"])
            if not session or session["kind"] not in {"session", "walkthrough"}:
                errors.append(f"{key}: session must reference a session or walkthrough")
        if item["status"] == "complete":
            if not item.get("session") or not item.get("completion_evidence"):
                errors.append(f"{key}: complete phase requires session and completion_evidence")
            if not item.get("result", "").strip():
                errors.append(f"{key}: complete phase requires actual verification result")
        elif item["status"] not in CLAIMED_STATES and (
            item.get("completion_evidence") or item.get("result")
        ):
            # A checkpoint may record real interim evidence while a claim is held (active/blocked);
            # only a released phase (queued/deferred/cancelled) has no claim left to justify it.
            errors.append(
                f"{key}: completion evidence/results require an active, blocked or complete phase"
            )
        try:
            for path in item["deliverables"]:
                check_file(path)  # Validate public path, but planned files need not exist yet.
            for path in item.get("completion_evidence", []):
                if not check_file(path):
                    errors.append(f"{key}: missing completion evidence {path}")
        except ValueError as exc:
            errors.append(f"{key}: {exc}")
    errors.extend(concurrency_errors(items, sorted(active), catalog.get("max_active", 1)))
    try:
        tuple(
            TopologicalSorter(
                {key: item["depends_on"] for key, item in items.items()}
            ).static_order()
        )
    except CycleError:
        errors.append("backlog: phase dependency cycle")
    for key, document in documents.items():
        if document["kind"] == "plan" and document["status"] in OPEN_PLANS and key not in covered:
            errors.append(f"backlog: open plan has no non-cancelled phase: {key}")
    return sorted(errors)


def queue_order(
    items: dict[str, Any], next_up: list[str]
) -> list[dict[str, Any]]:
    """Promoted phases first, in the order listed; everything else by priority then ID."""
    promoted = [items[key] for key in next_up if key in items]
    names = set(next_up)
    rest = sorted(
        (item for key, item in items.items() if key not in names),
        key=lambda item: (item["priority"], item["id"]),
    )
    return promoted + rest


def readiness(item: dict[str, Any], items: dict[str, Any]) -> str:
    if item["status"] != "queued":
        return str(item["status"])
    if all(items[dependency]["status"] == "complete" for dependency in item["depends_on"]):
        return "ready"
    return "waiting"


def render_backlog(
    catalog: dict[str, Any], documents: dict[str, Any], ready_only: bool = False
) -> str:
    """Render deterministic Markdown. The YAML catalog remains the only editable state."""
    items = {item["id"]: item for item in catalog["items"]}
    next_up = catalog.get("next_up", [])
    ordered = queue_order(items, next_up)
    counts = Counter(readiness(item, items) for item in ordered)

    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    max_active = catalog.get("max_active", 1)
    claimed = [item for item in ordered if item["status"] == "active"]
    lines = [
        "# Session backlog",
        "",
        f"{len(items)} phases; every phase has a one-session budget.",
        ", ".join(f"{state}: {count}" for state, count in sorted(counts.items())),
        "",
        f"Active claims: {len(claimed)} of {max_active} allowed.",
        "",
        "| Claimed phase | Agent | Locked systems |",
        "|---|---|---|",
    ]
    for item in claimed:
        agent = item.get("agent", "unclaimed")
        lines.append(f"| {item['id']} | {agent} | {', '.join(item['systems'])} |")
    if not claimed:
        lines.append("| — | — | — |")
    if next_up:
        lines += [
            "",
            f"Queued to the front: {', '.join(next_up)}.",
        ]
    lines += [
        "",
        "| Phase | Outcome | Queue | Priority | State | Prerequisites | Conflicts |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in ordered:
        state = readiness(item, items)
        if ready_only and state != "ready":
            continue
        dependencies = ", ".join(item["depends_on"]) or "—"
        conflicts = ", ".join(claim_conflicts(item, items)) or "—"
        rank = next_up.index(item["id"]) + 1 if item["id"] in next_up else None
        lines.append(
            f"| {item['id']} | {cell(item['title'])} | {rank or '—'} | {item['priority']} | "
            f"{state} | {dependencies} | {conflicts} |"
        )
    if ready_only:
        return "\n".join(lines)
    lines += ["", "## Source plan coverage", "", "| Plan | Status | Phases |", "|---|---|---|"]
    for key, document in sorted(documents.items()):
        if document["kind"] != "plan":
            continue
        phases = [
            item["id"]
            for item in ordered
            if key in [item["plan"], *item["sources"]] and item["status"] != "cancelled"
        ]
        lines.append(f"| {key} | {document['status']} | {', '.join(phases) or '—'} |")
    lines += ["", "## Phase details"]
    for item in ordered:
        lines += [
            "",
            f"### {item['id']}: {item['title']}",
            "",
            f"State: {readiness(item, items)}. Owner: {item['owner']}. Plan: {item['plan']}.",
            f"Next action: {item['next_action']}",
        ]
        if item.get("agent"):
            lines += [f"Claimed by: {item['agent']} on branch agent/{item['id']}"]
        if item.get("blocked_reason"):
            lines += [f"Reason: {item['blocked_reason']}"]
        if item.get("resume_when"):
            lines += [f"Resume when: {item['resume_when']}"]
        for field, title in (
            ("scope", "Scope"),
            ("acceptance", "Acceptance"),
            ("verification", "Verification"),
            ("deliverables", "Deliverables"),
        ):
            lines += ["", f"**{title}**", "", *[f"- {value}" for value in item[field]]]
        if item.get("result"):
            lines += ["", f"Result: {item['result']}"]
    return "\n".join(lines)
