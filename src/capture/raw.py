"""The only writer for `_capture/raw/` — REQ-002 R1/R2, ADR-007 section 1.

Every capture is stored verbatim, with an identifier and a timestamp, before any
interpretation runs. Nothing here edits or deletes a raw record once written; a rejected
capture costs nothing because rejection happens before the write, never after.

Both intake channels in scope for this phase go through `write_raw_capture`: the CLI
(`tools/capture.py`) calls it directly with the typed or piped text, and `scan_inbox`
calls it once per file dropped in `_capture/inbox/`. Structuring, evidence and routing are
phase-cap-05's job — nothing here reads a capture for meaning.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "_capture" / "raw"
INBOX_DIR = ROOT / "_capture" / "inbox"
INBOX_PROCESSED_SUBDIR = "processed"
SCHEMA = ROOT / "schemas" / "capture.schema.json"


class CaptureError(Exception):
    """A capture was refused before it reached the raw store."""


def _validator() -> Draft7Validator:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    # No format_checker: the schema's own note says `pattern` carries enforcement
    # until phase-rel-11 turns on the date-time format checker (test_capture_contracts.py
    # validates the same way).
    return Draft7Validator(schema)


def _iso_utc(at: dt.datetime) -> str:
    return at.astimezone(dt.UTC).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _new_id(at: dt.datetime) -> str:
    stamp = at.astimezone(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"raw-{stamp}-{os.urandom(3).hex()}"


def _validate(record: dict[str, Any]) -> None:
    errors = sorted(_validator().iter_errors(record), key=lambda e: list(e.absolute_path))
    if errors:
        detail = "; ".join(
            f"{'.'.join(str(p) for p in e.absolute_path) or 'record'}: {e.message}"
            for e in errors
        )
        raise CaptureError(f"refusing to write an invalid raw capture — {detail}")


def write_raw_capture(
    content: str,
    channel: str,
    source_path: str | None = None,
    raw_dir: Path = RAW_DIR,
) -> dict[str, Any]:
    """Validate and write one raw capture record verbatim. Returns the record written."""
    now = dt.datetime.now(dt.UTC)
    record: dict[str, Any] = {
        "id": _new_id(now),
        "captured_at": _iso_utc(now),
        "channel": channel,
        "content": content,
    }
    if source_path is not None:
        record["source_path"] = source_path

    _validate(record)

    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{record['id']}.json"
    if path.exists():
        raise CaptureError(f"raw capture id collision: {path}")
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def scan_inbox(
    inbox_dir: Path = INBOX_DIR, raw_dir: Path = RAW_DIR
) -> tuple[list[dict[str, Any]], list[tuple[Path, str]]]:
    """Turn every unprocessed file in `inbox_dir` into a raw capture record.

    A converted file is moved to `<inbox_dir>/processed/` so a later scan never recaptures
    it — the inbox itself then shows exactly what is still waiting. A file that fails to
    convert (empty content, unreadable bytes) is left where it is rather than moved, so it
    stays visible as something needing attention; the scan continues with the rest, per
    REQ-002 R9 — one bad item never blocks the others.

    Returns `(records written, [(path, error message) for files that failed])`.
    """
    if not inbox_dir.exists():
        return [], []

    processed_dir = inbox_dir / INBOX_PROCESSED_SUBDIR
    records: list[dict[str, Any]] = []
    failures: list[tuple[Path, str]] = []

    for path in sorted(inbox_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        try:
            content = path.read_text(encoding="utf-8")
            record = write_raw_capture(
                content,
                channel="inbox",
                source_path=str(path.relative_to(inbox_dir)),
                raw_dir=raw_dir,
            )
        except (CaptureError, OSError, UnicodeDecodeError) as exc:
            failures.append((path, str(exc)))
            continue
        processed_dir.mkdir(parents=True, exist_ok=True)
        path.rename(processed_dir / path.name)
        records.append(record)

    return records, failures
