"""Tests for the leak checker (phase-priv-04).

Unit tests monkeypatch the module's ROOT to a temporary tree, so they never depend on
whether the real `_private/portfolio/` exists on the machine running them — it does on
the owner's, never in CI, and the module must behave correctly either way (see
docs/08-governance/OPS-009-check-no-private-content.md).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checker = _load("check_no_private_content")


def test_check_paths_flags_private_prefix() -> None:
    files = ["README.md", "_private/portfolio/projects/acme-widget.json"]
    violations = checker.check_paths(files)
    assert len(violations) == 1
    assert "_private/portfolio/projects/acme-widget.json" in violations[0]


def test_check_paths_allows_ordinary_files() -> None:
    files = ["README.md", "_data/projects/example-web-platform.json"]
    assert checker.check_paths(files) == []


def _seed_portfolio(tmp_path: Path, stems: list[str], tag_ids: list[str]) -> None:
    portfolio = tmp_path / "_private" / "portfolio" / "projects"
    portfolio.mkdir(parents=True)
    for stem in stems:
        (portfolio / f"{stem}.json").write_text("{}", encoding="utf-8")

    data_dir = tmp_path / "_data"
    data_dir.mkdir(parents=True)
    tags = [{"id": t, "label": t.title()} for t in tag_ids]
    (data_dir / "tags.json").write_text(json.dumps(tags), encoding="utf-8")


def test_identifiers_empty_when_no_private_portfolio(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    assert checker.confidential_identifiers() == set()


def test_identifiers_include_hyphenated_stems(tmp_path: Path, monkeypatch: Any) -> None:
    _seed_portfolio(tmp_path, ["acme-widget-build", "meditation"], tag_ids=[])
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    ids = checker.confidential_identifiers()
    assert "acme-widget-build" in ids
    assert "meditation" not in ids  # single-word stems are not used as identifiers


def test_identifiers_include_repeated_prefix_not_in_tags(tmp_path: Path, monkeypatch: Any) -> None:
    _seed_portfolio(
        tmp_path,
        ["acme-widget-build", "acme-gadget-launch"],
        tag_ids=["python", "consulting"],
    )
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    ids = checker.confidential_identifiers()
    assert "acme" in ids


def test_identifiers_exclude_prefix_kept_as_public_tag(tmp_path: Path, monkeypatch: Any) -> None:
    _seed_portfolio(
        tmp_path,
        ["anaplan-widget-build", "anaplan-gadget-launch"],
        tag_ids=["anaplan", "consulting"],
    )
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    ids = checker.confidential_identifiers()
    assert "anaplan" not in ids
    # the compound project names are still real project IDs and stay flagged
    assert "anaplan-widget-build" in ids


def test_identifiers_respect_exemption_list(tmp_path: Path, monkeypatch: Any) -> None:
    _seed_portfolio(tmp_path, ["acme-widget-build"], tag_ids=[])
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    monkeypatch.setattr(checker, "EXEMPT_IDENTIFIERS", {"acme-widget-build": "test exemption"})
    assert "acme-widget-build" not in checker.confidential_identifiers()


def test_check_content_flags_planted_identifier(tmp_path: Path, monkeypatch: Any) -> None:
    (tmp_path / "notes.md").write_text(
        "This mentions acme-widget-build in prose.", encoding="utf-8"
    )
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    violations = checker.check_content(["notes.md"], {"acme-widget-build"})
    assert len(violations) == 1
    assert "notes.md" in violations[0]


def test_check_content_flags_identifier_in_filename(tmp_path: Path, monkeypatch: Any) -> None:
    (tmp_path / "SESS-acme-widget-build-notes.md").write_text("clean content", encoding="utf-8")
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    violations = checker.check_content(["SESS-acme-widget-build-notes.md"], {"acme-widget-build"})
    assert any("path matches" in v for v in violations)


def test_check_content_no_false_positive_on_substring(tmp_path: Path, monkeypatch: Any) -> None:
    (tmp_path / "notes.md").write_text(
        "acme-widget-builder is unrelated to the flagged identifier.", encoding="utf-8"
    )
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    violations = checker.check_content(["notes.md"], {"acme-widget-build"})
    assert violations == []


def test_tracked_tree_passes_the_checker() -> None:
    """The acceptance test: the checker exits 0 on the current, cleaned tree."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_no_private_content.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_planted_identifier_fails_the_checker(tmp_path: Path, monkeypatch: Any) -> None:
    """git add -f of a planted identifier is caught, not just ignored by .gitignore."""
    _seed_portfolio(tmp_path, ["acme-widget-build"], tag_ids=[])
    (tmp_path / "leak.md").write_text("acme-widget-build shipped last week.", encoding="utf-8")
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    monkeypatch.setattr(checker, "tracked_files", lambda: ["leak.md"])
    assert checker.main() == 1
