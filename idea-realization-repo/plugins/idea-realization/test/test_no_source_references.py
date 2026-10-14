"""No file in the plugin names a particular repository, person, record or date.

The plugin carries concepts that hold in any repository. It must not carry instances: idea ids,
phase ids, document codes, session records, commit hashes, calendar dates, the confidential
directory's name, or the name and people of the repository it was built in.

The repository's own name, its remote owner and the committer's identity are read from git at
test time, so this file never has to spell them out.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from conftest import PLUGIN_ROOT

SKIP_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv"}

PATTERNS: dict[str, re.Pattern[str]] = {
    "confidential directory": re.compile(r"_priv[a]te"),
    "idea id": re.compile(r"(?<![\w.])\d{6}(?![\w.])"),
    "phase id": re.compile(r"\bphase-[a-z]+-\d+\b"),
    "document code": re.compile(r"\b(?:PLAN|REQ|ADR|GOV|OPS|PROMPT|SESS|ARCH)-\d"),
    "session record": re.compile(r"\bSESS-"),
    "commit hash": re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b"),
    "calendar date": re.compile(r"\b(?:19|20)\d\d-[01]\d-[0-3]\d\b"),
}


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=PLUGIN_ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def identities() -> set[str]:
    """Names of the enclosing repository and its people, as git reports them."""
    found: set[str] = set()
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    if common:
        found.add(Path(common).parent.name)
    remote = git("remote", "get-url", "origin")
    if remote:
        parts = re.split(r"[/:]", remote.removesuffix(".git"))
        found.update(parts[-2:])
    for key in ("user.name", "user.email"):
        value = git("config", key)
        found.add(value)
        found.update(value.split())
    # "idea-realization" is this plugin's own name, never a source reference.
    return {item for item in found if len(item) >= 3 and item != "idea-realization"}


def identity_pattern(names: set[str]) -> re.Pattern[str] | None:
    if not names:
        return None
    alternatives = "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True))
    return re.compile(rf"(?<![A-Za-z0-9])(?:{alternatives})(?![A-Za-z0-9])", re.IGNORECASE)


def text_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*")
                  if p.is_file() and not SKIP_PARTS.intersection(p.relative_to(root).parts))


def scan(root: Path, names: set[str]) -> list[str]:
    patterns = dict(PATTERNS)
    identity = identity_pattern(names)
    if identity is not None:
        patterns["source repository or person"] = identity
    found = []
    for path in text_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in patterns.items():
                match = pattern.search(line)
                if match:
                    where = path.relative_to(root).as_posix()
                    found.append(f"{where}:{number}: {label}: {match.group(0)!r}")
    return found


def test_plugin_names_no_source_instance() -> None:
    assert scan(PLUGIN_ROOT, identities()) == []


def test_identities_are_found_when_inside_a_repository() -> None:
    if git("rev-parse", "--is-inside-work-tree") == "true":
        assert identities()


def test_scan_catches_a_phase_id(tmp_path: Path) -> None:
    (tmp_path / "note.md").write_text("Carried over from " + "-".join(["phase", "demo", "01"]))
    assert [line.split(": ")[1] for line in scan(tmp_path, set())] == ["phase id"]


def test_scan_catches_every_pattern(tmp_path: Path) -> None:
    samples = {
        "confidential directory": "_priv" + "ate/notes",
        "idea id": "see " + "0" * 3 + "123",
        "document code": "per " + "ADR" + "-9",
        "commit hash": "at " + "ab12" + "cd3",
        "calendar date": "on " + "-".join(["2030", "01", "02"]),
    }
    for label, text in samples.items():
        (tmp_path / "sample.md").write_text(text)
        assert label in "\n".join(scan(tmp_path, set())), label


def test_scan_catches_a_repository_name(tmp_path: Path) -> None:
    (tmp_path / "sample.md").write_text("Built in the Sample-Repo checkout.")
    assert scan(tmp_path, {"sample-repo"})


def test_plugin_concepts_are_allowed(tmp_path: Path) -> None:
    text = ("An idea becomes a plan, a phase, a requirement; the adversary reviews it. "
            "Version 0.1.0 of idea-realization.")
    (tmp_path / "sample.md").write_text(text)
    assert scan(tmp_path, {"sample-repo"}) == []
