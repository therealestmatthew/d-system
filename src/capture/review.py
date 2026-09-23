"""Review: what the owner sees before deciding — REQ-002 R11/R14, ADR-007 sections 5, 7 and 9.

Review shows the claim, not the record. For every flagged or held staged record it lays out
the raw text, the proposed record, each assumed field with its level, quote and reason, and
anything the record names that does not exist yet. Items are ordered by stakes, highest
first, so the decisions that matter most come first. Clean records are listed by id only:
they promote in bulk with one action, and review effort should scale with ambiguity, not
volume.

Every new tag is shown as an alert, whether it arrives as a held `tag` record or as a tag
named on another record. A new tag category is shown as a proposal only: approving it is a
change to `schemas/tag.schema.json`, which review does not make.

Nothing here writes anything.
"""

from __future__ import annotations

import datetime as dt
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.capture.promote import (
    Paths,
    PromotionError,
    candidate,
    known_identities,
    load_staged,
)
from src.capture.raw import RAW_DIR
from src.capture.routing import stakes_for
from src.capture.structure import KnownIdentities, unresolved_references

#: Higher sorts first.
STAKES_ORDER = {"structural": 3, "high": 2, "medium": 1, "low": 0}


@dataclass(frozen=True)
class AssumedField:
    name: str
    value: Any
    level: str
    quote: str | None
    reason: str | None
    review_flag: bool


@dataclass(frozen=True)
class ReviewItem:
    """One flagged or held staged record, as the owner needs to see it."""

    staged_id: str
    entity_type: str
    route: str
    stakes: str
    raw_text: str | None
    proposed: dict[str, Any]
    assumed: list[AssumedField]
    unresolved: list[str]
    alerts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Review:
    """`clean` promotes as staged; `blocked` is clean by route but would be left staged."""

    items: list[ReviewItem]
    clean: list[str]
    blocked: list[tuple[str, str]] = field(default_factory=list)


def _raw_text(capture_id: str, raw_dir: Path) -> str | None:
    path = raw_dir / f"{capture_id}.json"
    if not path.is_file():
        return None
    content: str = json.loads(path.read_text(encoding="utf-8"))["content"]
    return content


def _assumed(record: Mapping[str, Any]) -> list[AssumedField]:
    entity: Mapping[str, Any] = record.get("entity") or {}
    evidence: Mapping[str, Mapping[str, Any]] = record.get("evidence") or {}
    return [
        AssumedField(
            name=name,
            value=entity.get(name),
            level=ev["level"],
            quote=ev.get("provenance", {}).get("quote"),
            reason=ev.get("reason"),
            review_flag=bool(ev.get("review_flag", False)),
        )
        for name, ev in sorted(evidence.items())
        if ev.get("level") != "explicit"
    ]


def _alerts(record: Mapping[str, Any], unresolved: Iterable[str]) -> list[str]:
    entity: Mapping[str, Any] = record.get("entity") or {}
    entity_type = record["entity_type"]
    alerts = []
    if entity_type == "tag":
        alerts.append(
            f"NEW TAG {entity.get('id')!r} in category {entity.get('category')!r}: stays held; "
            "capture-derived tags go under the private data root (idea 000343)"
        )
    elif entity_type == "tag-category":
        alerts.append(
            f"PROPOSED NEW TAG CATEGORY {entity.get('id') or entity.get('name')!r}: needs a "
            "change to schemas/tag.schema.json and cannot be approved here"
        )
    alerts += [f"NEW TAG {u.split('=', 1)[1]}" for u in unresolved if u.startswith("tags=")]
    return alerts


def _stakes(entity_type: str) -> str:
    try:
        return stakes_for(entity_type)
    except ValueError:
        return "structural"


def build_review(
    paths: Paths | None = None,
    raw_dir: Path | None = None,
    known: KnownIdentities | None = None,
) -> Review:
    """Collect every staged record into a review, highest stakes first."""
    where = paths or Paths()
    raw = raw_dir if raw_dir is not None else RAW_DIR
    identities = known if known is not None else known_identities(where)
    items: list[ReviewItem] = []
    clean: list[str] = []
    blocked: list[tuple[str, str]] = []
    for record in load_staged(where.staging):
        if record.get("route") == "clean":
            # The same check bulk promotion makes, without writing, so review never calls a
            # record ready that promotion would leave staged.
            try:
                candidate(record, {}, where, dt.date.today(), set(), keep_names=False)
            except PromotionError as exc:
                blocked.append((record["id"], str(exc)))
            else:
                clean.append(record["id"])
            continue
        entity: dict[str, Any] = record.get("entity") or {}
        unresolved = unresolved_references(entity, identities)
        items.append(
            ReviewItem(
                staged_id=record["id"],
                entity_type=record["entity_type"],
                route=record["route"],
                stakes=_stakes(record["entity_type"]),
                raw_text=_raw_text(record["capture_id"], raw),
                proposed=entity,
                assumed=_assumed(record),
                unresolved=unresolved,
                alerts=_alerts(record, unresolved),
            )
        )
    # A stable sort: within one stakes level, staging order is kept.
    items.sort(key=lambda item: -STAKES_ORDER[item.stakes])
    return Review(items=items, clean=clean, blocked=blocked)


def format_review(review: Review) -> str:
    """Render a review as plain text for the terminal."""
    lines: list[str] = []
    if review.clean:
        lines.append(f"{len(review.clean)} clean, ready to promote in bulk:")
        lines += [f"  {staged_id}" for staged_id in review.clean]
        lines.append("")
    if review.blocked:
        lines.append(f"{len(review.blocked)} clean but left staged by promotion:")
        lines += [f"  {staged_id}: {reason}" for staged_id, reason in review.blocked]
        lines.append("")
    if not review.items:
        lines.append("Nothing flagged or held.")
    for item in review.items:
        lines.append(f"[{item.route}] {item.staged_id} — {item.entity_type} ({item.stakes} stakes)")
        lines += [f"  ALERT: {alert}" for alert in item.alerts]
        raw = item.raw_text if item.raw_text is not None else "(raw capture not found)"
        lines.append(f"  raw: {raw}")
        lines.append(f"  proposed: {json.dumps(item.proposed, ensure_ascii=False)}")
        for assumed in item.assumed:
            flag = ", flagged" if assumed.review_flag else ""
            lines.append(f"  assumed {assumed.name} = {assumed.value!r} ({assumed.level}{flag})")
            lines.append(f"    quote: {assumed.quote!r}")
            lines.append(f"    reason: {assumed.reason}")
        for reference in item.unresolved:
            lines.append(f"  unresolved: {reference}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
