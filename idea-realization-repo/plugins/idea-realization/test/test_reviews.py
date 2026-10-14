"""Review verdict records validate, are named by their id, and keep finding ids unique."""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import paths
import product
import pytest
import yaml
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


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


def complete_phase(root: Path, **changes: Any) -> None:
    item = {"id": "build-api", "status": "complete", **changes}
    (root / "backlog").mkdir(exist_ok=True)
    (root / "backlog" / "backlog.yaml").write_text(yaml.safe_dump({"items": [item]}))


def run(root: Path, product_root: Path | None = None) -> list[str]:
    env = {"IDEA_REALIZATION_PRODUCT_ROOT": str(product_root)} if product_root else {}
    return reviews.check(paths.resolve({"root": str(root)}, env=env))


def test_a_complete_phase_with_no_reviews_fails(tmp_path: Path) -> None:
    complete_phase(tmp_path)
    assert any("complete without a passing gating verdict" in e for e in run(tmp_path))


def test_a_complete_phase_with_a_passing_gating_verdict_is_clean(tmp_path: Path) -> None:
    complete_phase(tmp_path)
    assert check(tmp_path, stamped(phase="build-api")) == []


@pytest.mark.parametrize("changes", [{"gating": False}, {"verdict": "reject"}])
def test_a_shadow_or_rejecting_verdict_does_not_complete_a_phase(
        tmp_path: Path, changes: dict[str, Any]) -> None:
    complete_phase(tmp_path)
    errors = check(tmp_path, stamped(phase="build-api", **changes))
    assert any("complete without a passing gating verdict" in e for e in errors)


@pytest.fixture
def two_repos(tmp_path: Path) -> tuple[Path, Path, str, str]:
    """A control folder naming a product checkout whose main has one commit and whose phase
    branch has one more: (control, product checkout, main commit, branch commit)."""
    control, checkout = tmp_path / "control", tmp_path / "hack-product"
    control.mkdir()
    checkout.mkdir()
    git(control, "init", "-q", "-b", "main")
    git(checkout, "init", "-q", "-b", "main")
    git(checkout, "remote", "add", "origin", "https://forge.example.com/team/hack-product")
    for message in ("base", "phase work"):
        if message == "phase work":
            git(checkout, "checkout", "-q", "-b", "agent/build-api")
        (checkout / f"{message.replace(' ', '-')}.txt").write_text(message)
        git(checkout, "add", "-A")
        git(checkout, "-c", "user.email=a@example.com", "-c", "user.name=a", "commit", "-qm",
            message)
    base, tip = git(checkout, "rev-parse", "main"), git(checkout, "rev-parse", "HEAD")
    git(checkout, "checkout", "-q", "main")
    (control / ".idea-realization").mkdir()
    (control / product.RECORD).write_text(
        "schema_version: 1\nname: hack-product\n"
        "remote: https://forge.example.com/team/hack-product\nintegration_branch: main\n")
    return control, checkout, base, tip


def test_two_repositories_need_the_product_merge(two_repos: tuple[Path, Path, str, str]) -> None:
    control, _, _, tip = two_repos
    complete_phase(control)
    errors = check(control, stamped(phase="build-api", reviewed_commit=tip))
    assert any("without product_merge" in e for e in errors)


def test_the_verdict_must_have_judged_the_merged_commit(
        two_repos: tuple[Path, Path, str, str]) -> None:
    control, _, base, tip = two_repos
    complete_phase(control, product_merge=tip)
    errors = check(control, stamped(phase="build-api", reviewed_commit=base))
    assert any("judged its product_merge" in e for e in errors)


def test_a_complete_phase_whose_merge_never_landed_is_stranded(
        two_repos: tuple[Path, Path, str, str]) -> None:
    control, checkout, _, tip = two_repos
    complete_phase(control, product_merge=tip)
    check(control, stamped(phase="build-api", reviewed_commit=tip))
    assert any("stranded" in e for e in run(control, checkout))
    assert run(control) == []  # without a checkout on this machine, landing cannot be checked
    git(checkout, "merge", "-q", "--ff-only", "agent/build-api")
    assert run(control, checkout) == []
