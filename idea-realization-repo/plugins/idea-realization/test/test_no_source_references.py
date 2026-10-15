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

Residual risk, accepted: a slug written directly after a different host
(``git@forge.example.com:<owner>/<repo>``) is read as another repository and not reported, so the
plugin's own test fixtures can use placeholder URLs. The real repository named that way, on a host
it does not live on, would be missed here; the deny-list check would still catch its names.
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
    "phase id": re.compile(r"\bphase-[a-z]+-(?:[a-z][a-z0-9]*-)?\d+\b"),
    "document code": re.compile(
        r"\b(?:PLAN|REQ|ADR|GOV|OPS|PROMPT|SESS|ARCH)-(?:[a-z][a-z0-9]*-)?\d"),
    "session record": re.compile(r"\bSESS-"),
    "commit hash": re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b"),
    "calendar date": re.compile(r"\b(?:19|20)\d\d-[01]\d-[0-3]\d\b"),
}


# A fixture slug, built from parts so that no origin can ever match it in this file's text.
FIXTURE = "/".join(["example-owner", "control"])


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


def remote_host(url: str) -> str | None:
    """The host an origin URL names, or None for a path on this machine."""
    match = (re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://(?:[^@/]*@)?([^/:]+)", url.strip())
             or re.match(r"^(?:[^/:@]+@)?([^/:]+):(?!//)", url.strip()))
    return match.group(1).lower() if match and not url.startswith("file:") else None


def identities(cwd: Path = PLUGIN_ROOT) -> set[str]:
    """The enclosing repository's whole ``owner/repo`` slug, from its origin remote; empty when
    there is no origin or it names no owner."""
    slug = remote_slug(git("remote", "get-url", "origin", cwd=cwd))
    return {slug} if slug else set()


IDENTITY = "source repository or person"


def identity_pattern(names: set[str]) -> re.Pattern[str] | None:
    if not names:
        return None
    alternatives = "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True))
    return re.compile(rf"(?<![A-Za-z0-9])(?:{alternatives})(?![A-Za-z0-9])", re.IGNORECASE)


def text_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*")
                  if p.is_file() and not SKIP_PARTS.intersection(p.relative_to(root).parts))


# A host name directly before a slug (``example.com/`` or ``example.com:``).
HOST_BEFORE = re.compile(r"(?<![A-Za-z0-9.-])([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)[:/]$")


def names_the_origin(line: str, match: re.Match[str], host: str | None) -> bool:
    """Whether a slug match names the origin repository: it does unless a different host sits
    directly before it, as in a test fixture's ``git@forge.example.com:team/control.git``."""
    before = HOST_BEFORE.search(line[:match.start()])
    return before is None or host is None or before.group(1).lower() == host


def scan(root: Path, names: set[str], host: str | None = None) -> list[str]:
    patterns = dict(PATTERNS)
    identity = identity_pattern(names)
    if identity is not None:
        patterns[IDENTITY] = identity
    found = []
    for path in text_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in patterns.items():
                match = next((m for m in pattern.finditer(line) if label != IDENTITY
                              or names_the_origin(line, m, host)), None)
                if match:
                    where = path.relative_to(root).as_posix()
                    found.append(f"{where}:{number}: {label}: {match.group(0)!r}")
    return found


def test_plugin_names_no_source_instance() -> None:
    origin = git("remote", "get-url", "origin")
    assert scan(PLUGIN_ROOT, identities(), remote_host(origin)) == []


def test_identities_are_found_when_the_repository_has_an_origin() -> None:
    if git("remote", "get-url", "origin"):
        assert identities()


@pytest.mark.parametrize("url", [f"git@github.com:{FIXTURE}.git", f"https://github.com/{FIXTURE}",
                                 f"ssh://git@github.com/{FIXTURE}.git",
                                 f"https://github.com/{FIXTURE}.git/"])
def test_remote_slug_reads_every_url_form(url: str) -> None:
    assert remote_slug(url) == FIXTURE


@pytest.mark.parametrize(("developer", "directory", "slug"), [
    ("Ana Dev", "control", FIXTURE),
    ("Work", "product", "/".join(["team", "product"])),
    ("Sam Team", "ideas", "/".join(["work", "ideas"])),
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
    assert scan(prose, names, "github.com")
    (prose / "sample.md").write_text(f"Cloned from https://github.com/{slug}.")
    assert scan(prose, names, "github.com")
    # The same owner/repo on another host is another repository, such as a test fixture's.
    (prose / "sample.md").write_text(f"origin git@forge.example.com:{slug}.git")
    assert scan(prose, names, "github.com") == []


@pytest.mark.parametrize(("url", "host"), [
    (f"git@github.com:{FIXTURE}.git", "github.com"),
    (f"https://someone@GitHub.com/{FIXTURE}", "github.com"),
    (f"ssh://git@github.com:22/{FIXTURE}.git", "github.com"),
    (f"git@github-work:{FIXTURE}.git", "github-work"),
    ("/srv/git/control.git", None), ("file:///srv/control.git", None),
])
def test_remote_host_reads_every_url_form(url: str, host: str | None) -> None:
    assert remote_host(url) == host


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


@pytest.mark.parametrize(("label", "text"), [
    ("phase id", "from " + "-".join(["phase", "demo", "ana", "01"])),
    ("document code", "per " + "-".join(["PLAN", "ana", "004"])),
])
def test_scan_catches_a_handle_scoped_instance(tmp_path: Path, label: str, text: str) -> None:
    (tmp_path / "sample.md").write_text(text)
    assert label in "\n".join(scan(tmp_path, set())), label


# The owner/repo slugs the plugin's own tests used as fixtures. Built from parts, like every other
# sample here, so this list never spells them out either.
TODAYS_FIXTURE_SLUGS = [("team", "product"), ("work", "ideas"), ("example-owner", "control"),
                        ("team", "control"), ("team", "hack-product"), ("team", "other-product")]


@pytest.mark.parametrize("host", ["github.com", "github-work"])
@pytest.mark.parametrize("parts", TODAYS_FIXTURE_SLUGS)
def test_no_fixture_collides_with_a_real_origin(parts: tuple[str, str], host: str) -> None:
    """A team whose origin happens to equal a fixture slug must not fail the suite: no test
    spells a slug out where the origin's host, or no host, would come before it."""
    assert scan(PLUGIN_ROOT, {"/".join(parts)}, host) == []
