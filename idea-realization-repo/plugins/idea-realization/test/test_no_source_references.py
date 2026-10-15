"""No file in the plugin names a particular repository, person, record or date.

The plugin carries concepts that hold in any repository. It must not carry instances: idea ids,
phase ids, document codes, session records, commit hashes, calendar dates, the confidential
directory's name, or the name of the repository it was built in.

The repository is named by its origin remote's whole ``owner/repo`` slug, read from git at test
time, so this file never has to spell it out. Nothing else is read from git: not the developer's
name or email, not the checkout directory's name, and not the slug's parts on their own. Those are
often ordinary words (a developer called Ana, a repository called ``control``), and matching them
fails the suite for whoever happens to share a word with the plugin's prose. People's names and
the organization's names are the deny-list's job: ``tools/check_confidential.py`` matches every
identifier on it against every tracked file, the plugin included, in the pre-commit hook and in
CI.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
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


def git(*args: str, cwd: Path = PLUGIN_ROOT) -> str:
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def remote_slug(url: str) -> str | None:
    """The ``owner/repo`` an origin URL names (scp-style, ssh or https), or None for a URL with
    fewer than two path parts, such as a local bare repository's directory."""
    path = re.sub(r"^[A-Za-z][A-Za-z0-9+.-]*://[^/]*/", "", url.strip())
    path = re.sub(r"^[^/:]+@[^/:]+:", "", path).removesuffix("/").removesuffix(".git")
    parts = [part for part in path.split("/") if part]
    return "/".join(parts[-2:]) if len(parts) >= 2 else None


def identities(cwd: Path = PLUGIN_ROOT) -> set[str]:
    """The enclosing repository's whole ``owner/repo`` slug, from its origin remote; empty when
    there is no origin or it names no owner."""
    slug = remote_slug(git("remote", "get-url", "origin", cwd=cwd))
    return {slug} if slug else set()


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


def test_identities_are_found_when_the_repository_has_an_origin() -> None:
    if git("remote", "get-url", "origin"):
        assert identities()


@pytest.mark.parametrize("url", ["git@github.com:example-owner/control.git",
                                 "https://github.com/example-owner/control",
                                 "ssh://git@github.com/example-owner/control.git",
                                 "https://github.com/example-owner/control.git/"])
def test_remote_slug_reads_every_url_form(url: str) -> None:
    assert remote_slug(url) == "example-owner/control"


@pytest.mark.parametrize(("developer", "directory", "slug"), [
    ("Ana Dev", "control", "example-owner/control"),
    ("Work", "product", "team/product"),
    ("Sam Team", "ideas", "work/ideas"),
])
def test_identity_is_the_slug_not_the_developer_or_the_directory(
        tmp_path: Path, developer: str, directory: str, slug: str) -> None:
    """A developer, a checkout directory and an organization each named with an ordinary word
    are not identities, and prose that uses those words passes. The whole slug is still caught."""
    checkout = tmp_path / directory
    checkout.mkdir()
    for args in (["init", "-q"], ["config", "user.name", developer],
                 ["config", "user.email", f"{developer.split()[0].lower()}@example.invalid"],
                 ["remote", "add", "origin", f"git@github.com:{slug}.git"]):
        subprocess.run(["git", *args], cwd=checkout, check=True)
    names = identities(checkout)
    assert names == {slug}
    prose = tmp_path / "prose"
    prose.mkdir()
    (prose / "sample.md").write_text(
        "Ask the control dev, Ana, about the team's work on product ideas before a release.")
    assert scan(prose, names) == []
    (prose / "sample.md").write_text(f"Cloned from {slug}.")
    assert scan(prose, names)


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
