"""The decision inbox's sanctioned read and write path: `_data/gate-decisions.jsonl`.

The idea log's discipline, scaled down to one gate resumption (PLAN-039.01 section 7):
append-only JSONL, a schema (`schemas/gate-decision.schema.json`), one sanctioned writer.
`tools/append_decision.py` is a thin CLI over `decide()`; `tick.py`'s `advance()` calls
`latest_for_gate()` to find a decision waiting to resume an interrupted gate. The repository
artifact a decision produces remains the durable truth; this file only requests a resumption.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "gate-decision.schema.json"
LOG = ROOT / "_data" / "gate-decisions.jsonl"


class DecisionError(Exception):
    """A refusal the caller can act on."""


def _schema() -> dict[str, Any]:
    schema: dict[str, Any] = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return schema


def _validator() -> Draft7Validator:
    return Draft7Validator(_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)


def validate(event: dict[str, Any]) -> None:
    errors = sorted(_validator().iter_errors(event), key=lambda e: list(e.absolute_path))
    if errors:
        detail = "; ".join(
            f"{'.'.join(str(p) for p in e.absolute_path) or 'event'}: {e.message}"
            for e in errors
        )
        raise DecisionError(f"refusing to append an invalid decision — {detail}")


def now() -> str:
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def load_decisions(log: Path = LOG) -> list[dict[str, Any]]:
    """Every recorded decision, in file order. An empty or absent log is zero decisions."""
    if not log.exists():
        return []
    decisions = []
    for lineno, line in enumerate(log.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            decisions.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise DecisionError(f"{log}:{lineno}: malformed JSON line") from exc
    return decisions


def for_gate(run_id: str, gate: str, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every decision recorded for one run's gate, oldest `decision_seq` first."""
    return [d for d in decisions if d["run_id"] == run_id and d["gate"] == gate]


def latest_for_gate(
    run_id: str, gate: str, decisions: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """The most recent decision for `(run_id, gate)`, or None if the gate has none yet."""
    matching = for_gate(run_id, gate, decisions)
    return matching[-1] if matching else None


def append(event: dict[str, Any], log: Path = LOG) -> None:
    validate(event)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def decide(
    run_id: str,
    gate: str,
    decision: str,
    decided_by: str,
    notes: str | None = None,
    decision_seq: int | None = None,
    log: Path = LOG,
) -> dict[str, Any]:
    """Record `decision` for `(run_id, gate)`.

    `decision_seq` is computed automatically. Passing an explicit value that does not match
    the next expected sequence is refused — the dedup key catching a second decision for a
    gate not yet reached again since its last one.
    """
    existing = load_decisions(log)
    expected_seq = len(for_gate(run_id, gate, existing)) + 1
    if decision_seq is not None and decision_seq != expected_seq:
        raise DecisionError(
            f"refusing decision_seq={decision_seq} for ({run_id!r}, {gate!r}) — "
            f"the next expected sequence is {expected_seq}. A gate already decided once "
            "is not decided again until it is reached a second time."
        )
    event: dict[str, Any] = {
        "run_id": run_id,
        "gate": gate,
        "decision": decision,
        "decision_seq": expected_seq,
        "at": now(),
        "decided_by": decided_by,
    }
    if notes is not None:
        event["notes"] = notes
    append(event, log)
    return event
