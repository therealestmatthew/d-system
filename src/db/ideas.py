"""Single source of truth for replaying `_data/ideas.jsonl`.

Consumed by `tools/append_idea.py` (validates the existing log before appending),
`tools/rebuild_db.py` (folds the log into the `ideas` table) and
`src/db/source_validation.py` (the preflight, before the rebuild drops a table). Three
copies of this used to exist and had already diverged in two behaviours — none of them
checked `event["from"]` against the status the replay had actually reached — which is
why only one may exist now.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "idea.schema.json"
LOG = ROOT / "_data" / "ideas.jsonl"

#: Terminal states carry no outgoing status transition. `discarded` leaves this set only
#: through a `revisited` event, which is what limits reopening to once.
WORKING_STATES = {"open", "triaged", "reviewing"}

#: Fields an `amended` event may correct. `title`/`body` are required on every idea and
#: `text` is required on every annotation, so none of the three can ever be cleared — see
#: `field_shape` in the schema for where that is enforced structurally. `target` is the one
#: clearable field: its only legal shape is `link_retraction`, which always clears (phase-idea-08).
AMENDABLE_FIELDS = ("title", "body", "text", "target")

#: Kinds an annotation may carry. Mirrors schemas/idea.schema.json's `kind` enum.
ANNOTATION_KINDS = ("note", "finding", "assessment")

#: Relationship types a link may carry. Mirrors schemas/idea.schema.json's `type` enum.
LINK_TYPES = ("extends", "supersedes", "relates_to")

#: A link's derived inverse, shown alongside the forward edge when rendering the target idea.
#: `relates_to` is symmetric by construction — its own inverse — so it is not listed here.
INVERSE_LINK_TYPE = {"extends": "extended_by", "supersedes": "superseded_by"}


class IdeaError(Exception):
    """A refusal the caller can act on, printed without a traceback."""


def canonical_bytes(event: dict[str, Any]) -> bytes:
    """A deterministic encoding of an event, independent of key order or whitespace."""
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def identity(event: dict[str, Any]) -> str:
    """The identity an `amends` pointer names: `eid` when present, else a digest of the event.

    The 19 events written before `eid` existed have no way to carry one without rewriting an
    append-only log, so their identity is a pure function of bytes that are already permanent.
    Two events resolving to the same identity — a digest collision for a legacy line, a writer
    bug for a new one — is a fold-time error (`_identity_index`), never a silent merge.
    """
    eid = event.get("eid")
    if eid:
        return str(eid)
    return hashlib.sha256(canonical_bytes(event)).hexdigest()[:16]


def new_eid() -> str:
    """A short, lexicographically sortable identity for a newly written event.

    Nanosecond epoch time, zero-padded to a fixed width: fixed-width zero-padded hex sorts
    identically to the numeric value it encodes, so identities sort in write order without
    parsing them. Collision would require two events on the same process to be built in the
    same nanosecond, which nothing here does.
    """
    return f"e{time.time_ns():016x}"


def _schema() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return data


def legal_transitions() -> set[tuple[str, str]]:
    """Read the transition table out of the schema rather than restating it here.

    Two copies of a rule is one copy and one liability. The schema is where the machine is
    declared, so the writer, the projection and the tests all read the same statement.
    """
    for branch in _schema()["allOf"]:
        if branch.get("if", {}).get("properties", {}).get("event", {}).get("const") != "status":
            continue
        return {
            (option["properties"]["from"]["const"], option["properties"]["to"]["const"])
            for option in branch["then"]["oneOf"]
        }
    raise IdeaError("schemas/idea.schema.json declares no status transitions")


def load_events(log: Path = LOG) -> list[dict[str, Any]]:
    """Every event in order. A missing log is an empty one, not an error."""
    if not log.exists():
        return []
    events: list[dict[str, Any]] = []
    for number, line in enumerate(log.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise IdeaError(f"{log.name} line {number} is not valid JSON: {exc}") from exc
    return events


def _identity_index(events: list[dict[str, Any]]) -> dict[str, tuple[int, dict[str, Any]]]:
    """Map every event's identity to its position and itself, refusing a collision.

    A collision is a digest collision for two legacy lines or a writer bug for two new ones;
    either way it is silently unresolvable which one an `amends` pointer meant, so this fails
    the fold rather than picking one.
    """
    index: dict[str, tuple[int, dict[str, Any]]] = {}
    for position, event in enumerate(events):
        ident = identity(event)
        if ident in index:
            other_position, other_event = index[ident]
            raise IdeaError(
                f"two events resolve to the same identity {ident!r} — idea "
                f"{other_event['idea']!r} at position {other_position} and idea "
                f"{event['idea']!r} at position {position}"
            )
        index[ident] = (position, event)
    return index


def _amendments_by_target(
    events: list[dict[str, Any]], id_index: dict[str, tuple[int, dict[str, Any]]]
) -> dict[str, list[dict[str, Any]]]:
    """Group `amended` events by the identity they target, validating each target.

    A target must exist, must appear earlier in the log than the amendment naming it, and
    must belong to the same idea. All three are refused here — before any append, and before
    the rebuild writes a row — rather than left for whatever later reads `amends` to notice.
    """
    by_target: dict[str, list[dict[str, Any]]] = {}
    for position, event in enumerate(events):
        if event.get("event") != "amended":
            continue
        target = event["amends"]
        if target not in id_index:
            raise IdeaError(
                f"{event['idea']}: amendment targets {target!r}, which is not in the log"
            )
        target_position, target_event = id_index[target]
        if target_position >= position:
            raise IdeaError(
                f"{event['idea']}: amendment targets {target!r}, which does not appear "
                "earlier in the log — an amendment cannot target itself or a later event"
            )
        if target_event["idea"] != event["idea"]:
            raise IdeaError(
                f"{event['idea']}: amendment targets {target!r}, which belongs to idea "
                f"{target_event['idea']!r} — an amendment may only target an event on the "
                "same idea"
            )
        by_target.setdefault(target, []).append(event)
    return by_target


def _effective_fields(
    ident: str,
    id_index: dict[str, tuple[int, dict[str, Any]]],
    by_target: dict[str, list[dict[str, Any]]],
    memo: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """The field_shape each amendable field resolves to, after every amendment targeting it.

    Starts from the event's own contribution (`{"set": True, "value": v}` for whichever of
    `AMENDABLE_FIELDS` it carries), then applies each amendment targeting it in append order,
    recursing first into amendments of amendments so a correction is itself correctable
    (`effective(e)` in PLAN-017.03). Because `_amendments_by_target` already proved every
    target strictly precedes its amendment, this recursion cannot cycle.
    """
    if ident in memo:
        return memo[ident]
    _, event = id_index[ident]
    if event.get("event") == "amended":
        fields = {field: event[field] for field in AMENDABLE_FIELDS if field in event}
    else:
        fields = {
            field: {"set": True, "value": event[field]}
            for field in AMENDABLE_FIELDS
            if field in event
        }
    result = dict(fields)
    for amender in by_target.get(ident, []):
        amender_fields = _effective_fields(identity(amender), id_index, by_target, memo)
        for field, shape in amender_fields.items():
            if shape.get("set"):
                result[field] = shape
    memo[ident] = result
    return result


def _effective_event(
    event: dict[str, Any],
    id_index: dict[str, tuple[int, dict[str, Any]]],
    by_target: dict[str, list[dict[str, Any]]],
    memo: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    """`event`, with any amendable field replaced by what amendments resolved it to."""
    fields = _effective_fields(identity(event), id_index, by_target, memo)
    resolved = dict(event)
    for field, shape in fields.items():
        if shape.get("set"):
            resolved[field] = shape["value"]
    return resolved


def _as_promoted_to(value: str | list[str] | None) -> list[str] | None:
    """Normalise `promoted_to` to a list. A legacy scalar reads as a singleton (phase-idea-08)."""
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    return list(value)


def fold(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Replay events into current state, validating history as it goes.

    A schema checks one line in isolation; this is what checks a line against the ones
    before it. Every rule that needs more than one line lives here: a `created` event is
    unique per idea and precedes everything else about it, a `status` event's `from` equals
    the status this replay has actually reached — the single highest-value check, because
    without it a hand-edited or replayed line can silently rewrite history — the `from -> to`
    pair is in the schema's transition table, and `revisited` fires only from `discarded`
    and at most once. It runs before any append and before the rebuild drops a table.

    `amended` events never advance the machine themselves — they correct what a `created`,
    `status`, `revisited`, `annotated` or `linked` event resolves to (`_effective_event`), so
    only those five kinds are replayed here. `annotated` and `linked` are permitted regardless
    of status, terminal included (`PLAN-017.04`): they extend the record, not the state machine.
    """
    transitions = legal_transitions()
    id_index = _identity_index(events)
    by_target = _amendments_by_target(events, id_index)
    memo: dict[str, dict[str, dict[str, Any]]] = {}
    state: dict[str, dict[str, Any]] = {}
    for raw_event in events:
        if raw_event["event"] == "amended":
            continue
        event = _effective_event(raw_event, id_index, by_target, memo)
        idea = event["idea"]
        kind = event["event"]
        if kind == "created":
            if idea in state:
                raise IdeaError(f"{idea} was already created — a second created event follows it")
            state[idea] = {
                "title": event["title"],
                "body": event["body"],
                "status": "open",
                "created": event["at"],
                "updated": event["at"],
                "revisits": 0,
                "promoted_to": None,
                "annotations": [],
                "links": [],
            }
            continue
        if idea not in state:
            raise IdeaError(f"event for unknown idea {idea} — no created event precedes it")
        current = state[idea]
        if kind == "status":
            source, target = event["from"], event["to"]
            if source != current["status"]:
                raise IdeaError(
                    f"{idea}: status event declares from={source!r} but the replay had "
                    f"already reached {current['status']!r}"
                )
            if (source, target) not in transitions:
                raise IdeaError(f"{idea}: illegal transition {source} -> {target}")
            current["status"] = target
            current["updated"] = event["at"]
            if target == "promoted":
                current["promoted_to"] = _as_promoted_to(event.get("promoted_to"))
        elif kind == "revisited":
            if current["status"] != "discarded":
                raise IdeaError(
                    f"{idea}: revisited but the replay had reached {current['status']!r}, "
                    "not discarded"
                )
            if current["revisits"] >= 1:
                raise IdeaError(f"{idea} was already revisited once — a second revisit follows it")
            current["status"] = "reviewing"
            current["updated"] = event["at"]
            current["revisits"] += 1
        elif kind == "annotated":
            current["annotations"].append({
                "eid": identity(raw_event),
                "author": event["author"],
                "kind": event["kind"],
                "text": event["text"],
                "at": event["at"],
            })
            current["updated"] = event["at"]
        elif kind == "linked":
            target_idea = event.get("target")
            current["links"].append({
                "eid": identity(raw_event),
                "type": event["type"],
                "target": target_idea,
                "retracted": target_idea is None,
                "at": event["at"],
            })
            current["updated"] = event["at"]
    return state


def link_diagnostics(state: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """Fold-time diagnostics, keyed by the idea each is reported against (per-idea, `PLAN-017.04`).

    Never raises: a cycle or a stale supersession is a modelling mistake worth surfacing, not a
    reason to refuse the append that revealed it (`ADR-010`'s capture-always-wins principle,
    extended to links). Two checks: an `extends` cycle is flagged against every idea on it, and
    a `supersedes` edge whose target is not `discarded` is flagged against the idea asserting it.
    """
    diagnostics: dict[str, list[str]] = {}

    def flag(idea: str, message: str) -> None:
        diagnostics.setdefault(idea, []).append(message)

    graph: dict[str, list[str]] = {
        idea: [
            link["target"] for link in entry["links"]
            if link["type"] == "extends" and not link["retracted"]
        ]
        for idea, entry in state.items()
    }
    WHITE, GRAY, BLACK = 0, 1, 2
    color = dict.fromkeys(graph, WHITE)

    def visit(node: str, stack: list[str]) -> None:
        color[node] = GRAY
        stack.append(node)
        for target in graph.get(node, []):
            if target not in color:
                continue
            if color[target] == WHITE:
                visit(target, stack)
            elif color[target] == GRAY:
                cycle = stack[stack.index(target):] + [target]
                message = "extends cycle: " + " -> ".join(cycle)
                for member in cycle[:-1]:
                    flag(member, message)
        stack.pop()
        color[node] = BLACK

    for idea in graph:
        if color[idea] == WHITE:
            visit(idea, [])

    for idea, entry in state.items():
        for link in entry["links"]:
            if link["retracted"] or link["type"] != "supersedes":
                continue
            target_entry = state.get(link["target"])
            if target_entry is not None and target_entry["status"] != "discarded":
                flag(
                    idea,
                    f"{idea} marks {link['target']} as superseded, but {link['target']} is "
                    f"{target_entry['status']!r}, not discarded",
                )

    return diagnostics
