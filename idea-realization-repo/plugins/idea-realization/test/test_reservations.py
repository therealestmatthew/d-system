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
#: What the fixture repository's developer, ana, allocates in the scoped plan series.
ANA_1 = "PLAN" + "-ana-001"
ANA_2 = "PLAN" + "-ana-002"


def git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> dict[str, Path]:
    """A git repository holding the template registers, with two linked worktrees."""
    primary = tmp_path / "primary"
    (primary / "docs").mkdir(parents=True)
    shutil.copy(PLUGIN_ROOT / "templates" / "codes.yaml", primary / "docs" / "codes.yaml")
    registry = yaml.safe_load((PLUGIN_ROOT / "templates" / "systems.yaml").read_text())
    registry["owners"]["ana"] = {"description": "Ana.", "emails": ["test@example.invalid"]}
    (primary / "docs" / "systems.yaml").write_text(yaml.safe_dump(registry))
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
    first = codes.allocate(repo["first"], "plan", register(), {}, handle="ana")
    second = codes.allocate(repo["second"], "plan", register(), {}, handle="ana")
    assert (first, second) == (ANA_1, ANA_2)


def test_two_next_code_commands_from_two_worktrees_return_different_codes(
    repo: dict[str, Path],
) -> None:
    def next_code(worktree: Path) -> str:
        result = subprocess.run([sys.executable, str(SCRIPTS / "cli.py"), "next-code", "plan"],
                                cwd=worktree, capture_output=True, text=True, check=False,
                                env={**os.environ, "CLAUDE_PROJECT_DIR": ""})
        assert result.returncode == 0, result.stderr
        return result.stdout.strip()

    assert [next_code(repo["first"]), next_code(repo["second"])] == [ANA_1, ANA_2]


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
    code = codes.allocate(repo["first"], "plan", register(), {}, handle="ana")
    folder = repo["first"] / "docs" / "plans" / f"{code}-a"
    folder.mkdir(parents=True)
    (folder / f"{code}-overview.md").write_text("written, not merged\n")
    reservations.prune(repo["first"])
    assert codes.allocate(repo["second"], "plan", register(), {}, handle="ana") == ANA_2


def test_release_frees_a_code_and_reports_a_missing_one(repo: dict[str, Path]) -> None:
    reservations.reserve(repo["first"], ANA_1)
    assert reservations.release(repo["second"], ANA_1) is True
    assert reservations.release(repo["second"], ANA_1) is False
    assert codes.allocate(repo["second"], "plan", register(), {}, handle="ana") == ANA_1


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


# --- Handle-scoped allocation ------------------------------------------------------------------


def machine(tmp_path: Path, name: str) -> Path:
    """One developer's clone: its own git directory, so it shares no reservation with another."""
    root = tmp_path / name
    (root / "docs").mkdir(parents=True)
    shutil.copy(PLUGIN_ROOT / "templates" / "codes.yaml", root / "docs" / "codes.yaml")
    registry = yaml.safe_load((PLUGIN_ROOT / "templates" / "systems.yaml").read_text())
    registry["owners"].update({
        "ana": {"description": "Ana.", "emails": ["ana@example.com"]},
        "ben": {"description": "Ben.", "emails": ["ben@example.com"]},
    })
    (root / "docs" / "systems.yaml").write_text(yaml.safe_dump(registry))
    git("init", "-b", "main", cwd=root)
    git("config", "user.name", "Test", cwd=root)
    return root


def next_code_command(root: Path, email: str, kind: str = "plan") -> subprocess.CompletedProcess:
    git("config", "user.email", email, cwd=root)
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("GIT_CONFIG", "IDEA_REALIZATION"))}
    return subprocess.run([sys.executable, str(SCRIPTS / "cli.py"), "next-code", kind],
                          cwd=root, capture_output=True, text=True, check=False,
                          env={**env, "CLAUDE_PROJECT_DIR": ""})


def test_two_developers_on_separate_machines_get_different_codes(tmp_path: Path) -> None:
    first = next_code_command(machine(tmp_path, "ana-laptop"), "ana@example.com")
    second = next_code_command(machine(tmp_path, "ben-laptop"), "ben@example.com")
    assert first.returncode == second.returncode == 0, first.stderr + second.stderr
    assert (first.stdout.strip(), second.stdout.strip()) == ("PLAN" + "-ana-001",
                                                             "PLAN" + "-ben-001")


def test_next_code_without_a_handle_refuses_and_reserves_nothing(tmp_path: Path) -> None:
    root = machine(tmp_path, "stranger")
    result = next_code_command(root, "nobody@example.com")
    assert result.returncode == 1
    assert "carry the allocating developer's handle" in result.stderr, result.stderr
    assert "no developer in systems.yaml owners lists the email" in result.stderr, result.stderr
    assert reservations.active(root) == set()


def test_an_unscoped_series_allocates_without_a_handle(tmp_path: Path) -> None:
    result = next_code_command(machine(tmp_path, "stranger"), "nobody@example.com",
                               kind="governance")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "GOV" + "-001"


def test_a_handle_scoped_code_can_be_reserved_and_released(repo: dict[str, Path]) -> None:
    value = "PLAN" + "-ana-001"
    assert reservations.reserve(repo["first"], value) is True
    assert value in reservations.active(repo["second"])
    assert reservations.release(repo["second"], value) is True
