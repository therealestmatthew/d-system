"""Every script runs from a copy, against a temporary data root, with its own inline metadata."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import PLUGIN_ROOT, SCRIPTS

HEADER = re.compile(r"\A# /// script\n(?:#.*\n)*?# ///\n")
SCRIPTS_LIST = sorted(p for p in SCRIPTS.glob("*.py") if p.name != "__init__.py")
ALLOWED = {"jsonschema", "pyyaml", "filelock"}
#: Packages every header must pin to one exact version, the same in each header.
PINNED = {"filelock"}
REQUIREMENT = re.compile(r"([A-Za-z0-9_.-]+)\s*(.*)")


def python_files() -> list[Path]:
    return sorted(p for p in SCRIPTS.rglob("*.py") if "__pycache__" not in p.parts)


def requirements(text: str) -> dict[str, str]:
    """Each package a PEP 723 header names, mapped to its version specifier ('' when none)."""
    match = HEADER.match(text)
    assert match, "no PEP 723 header"
    dependencies = re.search(r"dependencies = \[(.*?)\]", match.group(0))
    assert dependencies
    found = {}
    for entry in dependencies.group(1).split(","):
        if entry.strip():
            parsed = REQUIREMENT.fullmatch(entry.strip().strip('"'))
            assert parsed, entry
            found[parsed.group(1)] = parsed.group(2).strip()
    return found


def pin_conflicts(headers: dict[str, str]) -> list[str]:
    """Every pinned package that is unpinned somewhere or pinned to two versions."""
    specifiers: dict[str, set[str]] = {}
    for text in headers.values():
        for name, specifier in requirements(text).items():
            if name in PINNED:
                specifiers.setdefault(name, set()).add(specifier)
    return sorted(
        f"{name}: {sorted(found)}" for name, found in specifiers.items()
        if len(found) != 1 or not next(iter(found)).startswith("==")
    )


@pytest.mark.parametrize("script", SCRIPTS_LIST, ids=lambda p: p.name)
def test_inline_metadata_names_only_allowed_packages(script: Path) -> None:
    assert set(requirements(script.read_text())) <= ALLOWED


def test_a_pinned_package_has_one_exact_version_in_every_header() -> None:
    assert pin_conflicts({p.name: p.read_text() for p in SCRIPTS_LIST}) == []


def test_two_headers_pinning_different_versions_conflict() -> None:
    def header(specifier: str) -> str:
        return f'# /// script\n# dependencies = ["filelock{specifier}"]\n# ///\n'

    assert pin_conflicts({"a": header("==1.0"), "b": header("==1.0")}) == []
    assert pin_conflicts({"a": header("==1.0"), "b": header("==2.0")}) != []
    assert pin_conflicts({"a": header(">=1.0")}) != []


def test_no_script_derives_data_paths_from_its_location_or_imports_src() -> None:
    for path in python_files():
        text = path.read_text()
        assert "parents[" not in text, path
        assert "from src" not in text and "import src" not in text, path


@pytest.fixture
def copied(tmp_path: Path) -> Path:
    copy = tmp_path / "copy"
    shutil.copytree(SCRIPTS, copy / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(PLUGIN_ROOT / ".claude-plugin", copy / ".claude-plugin")
    shutil.copytree(PLUGIN_ROOT / "schemas", copy / "schemas")
    return copy / "scripts"


def runner() -> list[str]:
    uv = shutil.which("uv")
    return [uv, "run", "--quiet", "--no-project", "--script"] if uv else [sys.executable]


@pytest.mark.parametrize("script", SCRIPTS_LIST, ids=lambda p: p.name)
def test_help_runs_from_a_copy(copied: Path, script: Path, tmp_path: Path) -> None:
    result = subprocess.run([*runner(), str(copied / script.name), "--help"], cwd=tmp_path,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_help_lists_path_flags(copied: Path, tmp_path: Path) -> None:
    for name in ("paths.py", "scaffold.py", "check.py"):
        result = subprocess.run([*runner(), str(copied / name), "--help"], cwd=tmp_path,
                                capture_output=True, text=True, check=False)
        assert "--ideas-path" in result.stdout and "--root" in result.stdout, name


def test_scripts_run_against_a_temporary_root(copied: Path, tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    def run(name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([*runner(), str(copied / name), *args], cwd=elsewhere,
                              capture_output=True, text=True, check=False)

    assert run("paths.py", "--root", str(data)).returncode == 0
    scaffolded = run("scaffold.py", "--root", str(data), "--feature", "all")
    assert scaffolded.returncode == 0, scaffolded.stderr
    assert (data / "ideas" / "ideas.jsonl").is_file()
    assert run("doctor.py", "--root", str(data)).returncode == 0
    assert run("check.py", "--root", str(data)).returncode == 0
    assert run("cli.py", "--help").returncode == 0
    assert run("prerequisites.py").returncode in {0, 1}
    assert list(elsewhere.iterdir()) == []
    assert not (copied.parent / "ideas").exists()
