"""tools/check_confidential.py on temporary git repositories."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import check_confidential as check


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.delenv("PRIVATE_DENY_LIST", raising=False)
    git(tmp_path, "init", "-q")
    (tmp_path / "README.md").write_text("A public readme.\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    return tmp_path


def deny(root: Path, *lines: str) -> None:
    (root / ".private").mkdir(exist_ok=True)
    (root / ".private" / "deny-list.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_clean_repository_passes(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    deny(repo, "# a comment", "", "acme-corp")
    assert check.main(repo) == 0
    assert "OK (1 tracked files, 1 identifiers checked)" in capsys.readouterr().out


def test_missing_deny_list_skips_content_but_checks_paths(
        repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert check.main(repo) == 0
    assert "content check skipped" in capsys.readouterr().out


def test_identifier_in_content_fails(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    deny(repo, "Acme-Corp")
    (repo / "notes.md").write_text("Kickoff with ACME-CORP next week.\n", encoding="utf-8")
    git(repo, "add", "notes.md")
    assert check.main(repo) == 1
    assert "notes.md: matches deny-listed identifier 'Acme-Corp'" in capsys.readouterr().out


def test_identifier_in_path_fails(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    deny(repo, "acme")
    (repo / "acme-plan.md").write_text("Nothing here.\n", encoding="utf-8")
    git(repo, "add", "acme-plan.md")
    assert check.main(repo) == 1
    assert "acme-plan.md: path matches deny-listed identifier 'acme'" in capsys.readouterr().out


def test_word_boundary_does_not_match_inside_a_word(repo: Path) -> None:
    deny(repo, "acme")
    (repo / "notes.md").write_text("The acmeology handbook.\n", encoding="utf-8")
    git(repo, "add", "notes.md")
    assert check.main(repo) == 0


def test_unstaged_file_is_not_checked(repo: Path) -> None:
    deny(repo, "acme")
    (repo / "draft.md").write_text("acme\n", encoding="utf-8")
    assert check.main(repo) == 0


def test_force_added_confidential_file_fails(
        repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    deny(repo, "acme")
    git(repo, "add", "-f", ".private/deny-list.txt")
    assert check.main(repo) == 1
    assert "tracked file under the private directory: .private/deny-list.txt" in (
        capsys.readouterr().out)


def test_deny_list_path_from_environment(
        repo: Path, tmp_path_factory: pytest.TempPathFactory,
        monkeypatch: pytest.MonkeyPatch) -> None:
    elsewhere = tmp_path_factory.mktemp("machine") / "deny.txt"
    elsewhere.write_text("public\n", encoding="utf-8")
    monkeypatch.setenv("PRIVATE_DENY_LIST", str(elsewhere))
    assert check.main(repo) == 1


def test_staged_identifier_caught_after_disk_copy_is_reverted(
        repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    deny(repo, "acme")
    (repo / "notes.md").write_text("Meeting with acme.\n", encoding="utf-8")
    git(repo, "add", "notes.md")
    (repo / "notes.md").write_text("Meeting with a client.\n", encoding="utf-8")
    assert check.main(repo) == 1
    assert "notes.md: matches deny-listed identifier 'acme'" in capsys.readouterr().out


def test_identifier_only_on_disk_is_not_reported(repo: Path) -> None:
    deny(repo, "acme")
    (repo / "README.md").write_text("acme\n", encoding="utf-8")
    assert check.main(repo) == 0


def test_staged_deletion_is_not_scanned(repo: Path) -> None:
    deny(repo, "acme")
    (repo / "old.md").write_text("acme\n", encoding="utf-8")
    git(repo, "add", "old.md")
    git(repo, "rm", "-q", "--cached", "old.md")
    assert check.main(repo) == 0
