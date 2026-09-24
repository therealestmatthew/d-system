"""Governance fails on a stale catalog.md or ideas.md and writes neither (REQ-028 R01, R02)."""

from __future__ import annotations

import hashlib
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from src.governance.staleness import (
    CATALOG,
    IDEAS_LOG,
    IDEAS_MD,
    IDEAS_PRIORITY,
    catalog_errors,
    ideas_md_errors,
    render_ideas_md,
)

ROOT = Path(__file__).resolve().parents[1]


def _append_idea() -> ModuleType:
    """The sanctioned idea writer, imported by path — tools/ is not a package."""
    if "append_idea" in sys.modules:
        return sys.modules["append_idea"]
    spec = importlib.util.spec_from_file_location("append_idea", ROOT / "tools" / "append_idea.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["append_idea"] = module
    spec.loader.exec_module(module)
    return module


def test_catalog_matching_its_rendering_passes(tmp_path: Path) -> None:
    (tmp_path / CATALOG).parent.mkdir(parents=True)
    (tmp_path / CATALOG).write_text("# Catalog\n\nrow\n", encoding="utf-8")
    # write_catalog stores exactly one trailing newline, whatever the rendering ends with.
    assert catalog_errors(tmp_path, "# Catalog\n\nrow") == []
    assert catalog_errors(tmp_path, "# Catalog\n\nrow\n\n") == []


def test_stale_catalog_fails_naming_the_file(tmp_path: Path) -> None:
    (tmp_path / CATALOG).parent.mkdir(parents=True)
    (tmp_path / CATALOG).write_text("# Catalog\n\nold row\n", encoding="utf-8")
    errors = catalog_errors(tmp_path, "# Catalog\n\nnew row\n")
    assert len(errors) == 1
    assert errors[0].startswith(f"{CATALOG}: differs")
    assert "--catalog" in errors[0]


def test_missing_catalog_fails(tmp_path: Path) -> None:
    errors = catalog_errors(tmp_path, "# Catalog\n")
    assert errors and errors[0].startswith(f"{CATALOG}: is missing")


def _idea_root(tmp_path: Path) -> Path:
    """A root holding a copy of the repository's idea log, priority queue and rendered view."""
    for relative in (IDEAS_LOG, IDEAS_PRIORITY, IDEAS_MD):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def test_current_ideas_md_passes(tmp_path: Path) -> None:
    root = _idea_root(tmp_path)
    (root / IDEAS_MD).write_text(render_ideas_md(root), encoding="utf-8")
    assert ideas_md_errors(root) == []


def test_idea_appended_without_regeneration_fails_naming_ideas_md(tmp_path: Path) -> None:
    root = _idea_root(tmp_path)
    (root / IDEAS_MD).write_text(render_ideas_md(root), encoding="utf-8")
    _append_idea().add(
        "Scratch idea for the staleness test",
        "Appended without regenerating ideas.md.",
        log=root / IDEAS_LOG,
    )
    errors = ideas_md_errors(root)
    assert len(errors) == 1
    assert errors[0].startswith(f"{IDEAS_MD}: differs")
    (root / IDEAS_MD).write_text(render_ideas_md(root), encoding="utf-8")
    assert ideas_md_errors(root) == []


def test_missing_ideas_md_fails(tmp_path: Path) -> None:
    root = _idea_root(tmp_path)
    (root / IDEAS_MD).unlink()
    errors = ideas_md_errors(root)
    assert errors and errors[0].startswith(f"{IDEAS_MD}: is missing")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("relative", [CATALOG, IDEAS_MD])
def test_plain_check_writes_neither_generated_file(relative: str) -> None:
    before = _digest(ROOT / relative)
    subprocess.run(
        [sys.executable, "-m", "src.governance"], cwd=ROOT, capture_output=True, check=False
    )
    assert _digest(ROOT / relative) == before
