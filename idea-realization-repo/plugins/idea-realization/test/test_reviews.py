"""Review verdict records validate, are named by their id, and keep finding ids unique."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import paths
from checks import reviews

COMMIT = "a" * 40
SHA = "b" * 64


def record(**changes: Any) -> dict[str, Any]:
    return {
        "verdict_id": "day-build-api-phase-adversary",
        "date": date(2030, 1, 5).isoformat(),
        "phase": "build-api",
        "repository": "product",
        "reviewed_commit": COMMIT,
        "reviewer": {"type": "phase-adversary", "definition_sha256": SHA},
        "model": "a model",
        "verdict": "pass",
        "gating": True,
        "findings": [],
        "outcomes": [],
        **changes,
    }


def check(root: Path, *records: dict[str, Any], name: str | None = None) -> list[str]:
    directory = root / "docs" / "reviews"
    directory.mkdir(parents=True, exist_ok=True)
    for item in records:
        (directory / f"{name or item['verdict_id']}.json").write_text(json.dumps(item))
    return reviews.check(paths.resolve({"root": str(root)}, env={}))


def stamped(**changes: Any) -> dict[str, Any]:
    """A record whose id carries a date built at runtime, as real records do."""
    item = record(**changes)
    item["verdict_id"] = f"{item['date']}-build-api-phase-adversary"
    return item


def test_no_reviews_directory_is_clean(tmp_path: Path) -> None:
    assert reviews.check(paths.resolve({"root": str(tmp_path)}, env={})) == []


def test_a_valid_record_is_clean(tmp_path: Path) -> None:
    assert check(tmp_path, stamped()) == []


def test_a_record_must_be_named_by_its_id(tmp_path: Path) -> None:
    errors = check(tmp_path, stamped(), name="other-name")
    assert any("is not the file name" in error for error in errors)


def test_schema_violations_are_reported(tmp_path: Path) -> None:
    errors = check(tmp_path, stamped(verdict="maybe", repository="elsewhere"))
    assert any("verdict" in error for error in errors)
    assert any("repository" in error for error in errors)


def test_finding_ids_are_unique(tmp_path: Path) -> None:
    finding = {"id": "F01", "severity": "minor", "title": "A defect.", "evidence": "a file"}
    errors = check(tmp_path, stamped(findings=[finding, finding]))
    assert any("duplicate finding id" in error for error in errors)


def test_unreadable_json_is_reported(tmp_path: Path) -> None:
    directory = tmp_path / "docs" / "reviews"
    directory.mkdir(parents=True)
    (directory / "broken.json").write_text("{")
    assert any(error.startswith("reviews/broken.json") for error in check(tmp_path))
