"""Pre-merge code reservations, shared by every worktree of one repository.

A test that only calls ``reserve`` twice in one process proves mutual exclusion but not sharing,
so most tests here build a real git repository with two linked worktrees and check that a
reservation taken in one is seen from the other with nothing committed anywhere.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import codes
import pytest
import reservations
import yaml
from conftest import PLUGIN_ROOT, SCRIPTS

PLAN_1 = "PLAN" + "-001"
PLAN_2 = "PLAN" + "-002"


def git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> dict[str, Path]:
    """A git repository holding the template registers, with two linked worktrees."""
    primary = tmp_path / "primary"
    (primary / "docs").mkdir(parents=True)
    for name in ("codes.yaml", "systems.yaml"):
        shutil.copy(PLUGIN_ROOT / "templates" / name, primary / "docs" / name)
    git("init", "-b", "main", cwd=primary)
    git("config", "user.email", "test@example.invalid", cwd=primary)
    git("config", "user.name", "Test", cwd=primary)
    git("add", "docs", cwd=primary)
    git("commit", "-m", "registers", cwd=primary)
    first, second = tmp_path / "wt-first", tmp_path / "wt-second"
    git("worktree", "add", "-b", "first", str(first), "main", cwd=primary)
    git("worktree", "add", "-b", "second", str(second), "main", cwd=primary)
    return {"primary": primary, "first": first, "second": second}


def register() -> dict[str, Any]:
    return dict(yaml.safe_load((PLUGIN_ROOT / "templates" / "codes.yaml").read_text()))


def test_reserve_is_mutually_exclusive(repo: dict[str, Path]) -> None:
    assert reservations.reserve(repo["primary"], PLAN_1) is True
    assert reservations.reserve(repo["primary"], PLAN_1) is False
    assert reservations.active(repo["primary"]) == {PLAN_1}


@pytest.mark.parametrize("value", ["../config", "..", ".", "", "plan/1", "PLAN 1"])
def test_reserve_and_release_refuse_a_code_that_would_escape_the_store(
    repo: dict[str, Path], value: str
) -> None:
    with pytest.raises(ValueError, match="malformed code"):
        reservations.reserve(repo["primary"], value)
    with pytest.raises(ValueError, match="malformed code"):
        reservations.release(repo["primary"], value)
    assert (repo["primary"] / ".git" / "config").is_file()


def test_the_store_is_under_the_git_common_directory(repo: dict[str, Path]) -> None:
    store = reservations.reservation_dir(repo["first"])
    assert store == (repo["primary"] / ".git" / reservations.RESERVATION_DIR).resolve()


def test_two_worktrees_share_one_reservation_store(repo: dict[str, Path]) -> None:
    assert reservations.reserve(repo["first"], PLAN_1)
    assert PLAN_1 in reservations.active(repo["second"])
    assert reservations.reserve(repo["second"], PLAN_1) is False
    assert subprocess.run(["git", "status", "--porcelain"], cwd=repo["first"],
                          capture_output=True, text=True).stdout == ""


def test_two_worktrees_allocating_the_same_kind_get_different_codes(
    repo: dict[str, Path],
) -> None:
    first = codes.allocate(repo["first"], "plan", register(), {})
    second = codes.allocate(repo["second"], "plan", register(), {})
    assert (first, second) == (PLAN_1, PLAN_2)


def test_two_next_code_commands_from_two_worktrees_return_different_codes(
    repo: dict[str, Path],
) -> None:
    def next_code(worktree: Path) -> str:
        result = subprocess.run([sys.executable, str(SCRIPTS / "cli.py"), "next-code", "plan"],
                                cwd=worktree, capture_output=True, text=True, check=False,
                                env={**os.environ, "CLAUDE_PROJECT_DIR": ""})
        assert result.returncode == 0, result.stderr
        return result.stdout.strip()

    assert [next_code(repo["first"]), next_code(repo["second"])] == [PLAN_1, PLAN_2]


def test_prune_drops_only_an_expired_reservation(repo: dict[str, Path]) -> None:
    reservations.reserve(repo["first"], PLAN_1)
    reservations.reserve(repo["first"], PLAN_2)
    stale = reservations.reservation_dir(repo["first"]) / PLAN_1
    stale.write_text(json.dumps({"code": PLAN_1, "at": time.time()
                                 - reservations.TTL_SECONDS - 60}))
    assert reservations.prune(repo["second"]) == [PLAN_1]
    assert reservations.active(repo["second"]) == {PLAN_2}


def test_a_damaged_reservation_still_expires(repo: dict[str, Path]) -> None:
    reservations.reserve(repo["first"], PLAN_1)
    path = reservations.reservation_dir(repo["first"]) / PLAN_1
    path.write_text("not json")
    old = time.time() - reservations.TTL_SECONDS - 60
    os.utime(path, (old, old))
    assert reservations.prune(repo["first"]) == [PLAN_1]


def test_a_written_but_unmerged_document_does_not_free_its_code(repo: dict[str, Path]) -> None:
    """The document exists in one worktree only; its reservation must still hold for the other."""
    code = codes.allocate(repo["first"], "plan", register(), {})
    folder = repo["first"] / "docs" / "plans" / f"{code}-a"
    folder.mkdir(parents=True)
    (folder / f"{code}-overview.md").write_text("written, not merged\n")
    reservations.prune(repo["first"])
    assert codes.allocate(repo["second"], "plan", register(), {}) == PLAN_2


def test_release_frees_a_code_and_reports_a_missing_one(repo: dict[str, Path]) -> None:
    reservations.reserve(repo["first"], PLAN_1)
    assert reservations.release(repo["second"], PLAN_1) is True
    assert reservations.release(repo["second"], PLAN_1) is False
    assert codes.allocate(repo["second"], "plan", register(), {}) == PLAN_1


def test_the_release_command_lists_and_releases(repo: dict[str, Path],
                                                capsys: pytest.CaptureFixture[str]) -> None:
    reservations.reserve(repo["first"], PLAN_1)
    assert reservations.main(["--root", str(repo["second"])]) == 0
    assert PLAN_1 in capsys.readouterr().out
    assert reservations.main([PLAN_1, "--root", str(repo["second"])]) == 0
    assert reservations.main([PLAN_1, "--root", str(repo["second"])]) == 1
    assert reservations.main(["../config", "--root", str(repo["second"])]) == 2


def test_outside_a_git_repository_allocation_refuses(tmp_path: Path) -> None:
    with pytest.raises(subprocess.CalledProcessError):
        reservations.reservation_dir(tmp_path)
