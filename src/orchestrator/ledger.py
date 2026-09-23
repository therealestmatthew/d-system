"""The run ledger's sanctioned read and write path: `_data/runs.jsonl`.

The run ledger is the idea log's own pattern applied to runs (PLAN-039.01 section 5):
append-only JSONL, one JSON Schema (`schemas/run.schema.json`), one sanctioned writer.
`tools/append_run.py` is a thin CLI over the functions below; `tick.py` calls them directly
so a tick's own writes go through the identical validation path a human's manual correction
would. `identity()`/`new_eid()` mirror `src/db/ideas.py`'s so a run's events resolve to a
stable identity whether or not future work ever needs to amend one.

REQ-022 R18: `reconstruct()` is the whole answer to "one run is reconstructible from ledger
entries alone" -- it reads nothing but the events passed to it, never a checkpoint.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "run.schema.json"
LOG = ROOT / "_data" / "runs.jsonl"

#: `abandoned` and `terminal` close a run for natural-key idempotency purposes. `parked` is
#: deliberately not terminal: the run is waiting, not done (PLAN-039.01 section 8's
#: budget-park case), so a natural key with only a `parked` run stays taken.
CLOSING_EVENTS = frozenset({"terminal", "abandoned"})


class LedgerError(Exception):
    """A refusal the caller can act on, printed without a traceback."""


def canonical_bytes(event: dict[str, Any]) -> bytes:
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def identity(event: dict[str, Any]) -> str:
    eid = event.get("eid")
    if eid:
        return str(eid)
    return hashlib.sha256(canonical_bytes(event)).hexdigest()[:16]


def new_eid() -> str:
    """A short, sortable identity for a newly written event. Mirrors `src/db/ideas.py`."""
    return f"e{time.time_ns():016x}"


def now() -> str:
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _validator() -> Draft7Validator:
    return Draft7Validator(_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)


def validate(event: dict[str, Any]) -> None:
    errors = sorted(_validator().iter_errors(event), key=lambda e: list(e.absolute_path))
    if errors:
        detail = "; ".join(
            f"{'.'.join(str(p) for p in e.absolute_path) or 'event'}: {e.message}"
            for e in errors
        )
        raise LedgerError(f"refusing to append an invalid event — {detail}")


def load_events(log: Path = LOG) -> list[dict[str, Any]]:
    """Every event in `log`, in file order. An empty or absent log is zero events."""
    if not log.exists():
        return []
    events = []
    for lineno, line in enumerate(log.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise LedgerError(f"{log}:{lineno}: malformed JSON line") from exc
    return events


def append(event: dict[str, Any], log: Path = LOG) -> None:
    """Validate, then append one line. Nothing already in the file is read or rewritten."""
    validate(event)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def by_run(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group events by `run_id`, preserving file order within each run."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        grouped.setdefault(event["run_id"], []).append(event)
    return grouped


def reconstruct(run_events: list[dict[str, Any]]) -> dict[str, Any]:
    """Rebuild one run's summary from its own events alone -- no checkpoint, ever (R18)."""
    if not run_events or run_events[0]["event"] != "started":
        raise LedgerError("a run's events must begin with 'started'")
    started = run_events[0]
    summary: dict[str, Any] = {
        "run_id": started["run_id"],
        "kind": started["kind"],
        "natural_key": started["natural_key"],
        "refs": dict(started["refs"]),
        "positions": [],
        "dispatches": [],
        "gates": [],
        "decisions": [],
        "status": "active",
        "outcome": None,
        "reason": None,
    }
    for event in run_events[1:]:
        kind = event["event"]
        if kind == "position":
            summary["positions"].append(event["position"])
        elif kind == "dispatched":
            summary["dispatches"].append(
                {"role": event["role"], "budget_cap": event["budget_cap"], "result": None}
            )
        elif kind == "dispatch_result":
            if summary["dispatches"]:
                summary["dispatches"][-1]["result"] = {
                    "outcome": event["outcome"],
                    "usage": event["usage"],
                }
        elif kind == "gate_reached":
            summary["gates"].append(event["gate"])
        elif kind == "gate_decided":
            summary["decisions"].append({"gate": event["gate"], "decision": event["decision"]})
        elif kind == "parked":
            summary["status"] = "parked"
            summary["reason"] = event["reason"]
        elif kind == "abandoned":
            summary["status"] = "abandoned"
            summary["reason"] = event["reason"]
        elif kind == "terminal":
            summary["status"] = "terminal"
            summary["outcome"] = event["outcome"]
            summary["positions"].append(event["position"])
        else:
            raise LedgerError(f"unknown ledger event {kind!r}")
    return summary


def fold(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Every run's summary, keyed by `run_id`. See `reconstruct()` for one run's shape."""
    return {run_id: reconstruct(run_events) for run_id, run_events in by_run(events).items()}


def active_natural_keys(events: list[dict[str, Any]]) -> set[str]:
    """Natural keys with a non-terminal run already open (PLAN-039.01 section 4)."""
    summaries = fold(events)
    return {
        summary["natural_key"]
        for summary in summaries.values()
        if summary["status"] not in ("terminal", "abandoned")
    }


def start(kind: str, natural_key: str, refs: dict[str, str], log: Path = LOG) -> dict[str, Any]:
    """Open a new run under `natural_key`. Refused if a non-terminal one already exists.

    This is the whole idempotency guarantee PLAN-039.01 section 4 asks for: reconcile calls
    this once per idea/phase/etc. it believes needs a run, and a duplicate call — two ticks
    racing, or the same tick re-deriving twice — is refused rather than silently accepted.
    """
    events = load_events(log)
    if natural_key in active_natural_keys(events):
        raise LedgerError(
            f"a non-terminal run already exists under natural key {natural_key!r} — "
            "reconcile is idempotent by design; this is refused rather than double-started"
        )
    run_id = f"run-{new_eid()}"
    event = {
        "run_id": run_id,
        "kind": kind,
        "event": "started",
        "at": now(),
        "eid": new_eid(),
        "natural_key": natural_key,
        "refs": refs,
    }
    append(event, log)
    return event


def _kind_of(run_id: str, events: list[dict[str, Any]]) -> str:
    for event in events:
        if event["run_id"] == run_id:
            return str(event["kind"])
    raise LedgerError(f"no run {run_id!r} in the ledger")


def record(run_id: str, event_name: str, log: Path = LOG, **fields: Any) -> dict[str, Any]:
    """Append a non-`started` event for an already-open run. `kind` is read from the ledger."""
    events = load_events(log)
    event = {
        "run_id": run_id,
        "kind": _kind_of(run_id, events),
        "event": event_name,
        "at": now(),
        "eid": new_eid(),
        **fields,
    }
    append(event, log)
    return event
