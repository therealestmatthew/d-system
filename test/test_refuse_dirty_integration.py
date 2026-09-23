"""Tests for the integration guard (phase-conc-02, REQ-013 R04).

Runs `tools/git-hooks/refuse_dirty_integration.py` as a real subprocess against a disposable
git repository built under `tmp_path` — never against `/code/d-system` or this worktree's own
checkout, which the guard must never inspect during a test run.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "git-hooks" / "refuse_dirty_integration.py"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_repo(tmp_path: Path) -> Path:
    """A minimal, disposable git repository with one committed file."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "dev")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "committed.txt").write_text("hello\n", encoding="utf-8")
    _git(repo, "add", "committed.txt")
    _git(repo, "commit", "-q", "-m", "initial commit")
    return repo


def _run_guard(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo)],
        capture_output=True,
        text=True,
    )


def test_clean_checkout_is_not_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)

    result = _run_guard(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "not refused" in result.stdout


def test_unrelated_modified_file_is_refused_and_named(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    (repo / "unrelated.txt").write_text("someone else's work\n", encoding="utf-8")

    result = _run_guard(repo)

    assert result.returncode != 0, result.stdout + result.stderr
    assert "Refused" in result.stdout
    assert "unrelated.txt" in result.stdout


def test_stashing_the_dirty_file_still_refuses(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    (repo / "unrelated.txt").write_text("someone else's work\n", encoding="utf-8")

    # Confirm the guard sees the dirty file before it is hidden.
    dirty_result = _run_guard(repo)
    assert dirty_result.returncode != 0

    _git(repo, "stash", "-u")

    # The working tree is now clean by `git status` alone -- the stash is what must still
    # trigger the refusal, or this guard teaches the exact behaviour that caused 000041.
    status_after_stash = _git(repo, "status", "--porcelain")
    assert status_after_stash.stdout == ""

    stashed_result = _run_guard(repo)

    assert stashed_result.returncode != 0, stashed_result.stdout + stashed_result.stderr
    assert "Refused" in stashed_result.stdout
    assert "stash" in stashed_result.stdout.lower()
