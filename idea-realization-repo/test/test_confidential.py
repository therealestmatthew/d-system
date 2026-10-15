"""tools/check_confidential.py on temporary git repositories."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

IRR = Path(__file__).resolve().parent.parent
CONTROL_COPY = IRR / "tools" / "check_confidential.py"
TEMPLATE_TOOLS = IRR / "templates" / "product-repo" / "tools"
TEMPLATE_COPY = TEMPLATE_TOOLS / "check_confidential.py"

sys.path.insert(0, str(IRR / "tools"))
import check_confidential as check  # noqa: E402


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


def test_missing_deny_list_skips_content_with_a_warning(
        repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert check.main(repo) == 0
    captured = capsys.readouterr()
    assert "WARNING: check_confidential found NO deny-list." in captured.err
    assert str(repo / ".private" / "deny-list.txt") in captured.err
    assert "content check SKIPPED" in captured.out


def test_missing_deny_list_still_runs_the_path_check(repo: Path) -> None:
    (repo / ".private").mkdir()
    (repo / ".private" / "notes.txt").write_text("x\n", encoding="utf-8")
    git(repo, "add", "-f", ".private/notes.txt")
    assert check.main(repo) == 1


def test_configured_deny_list_that_does_not_exist_fails(
        repo: Path, tmp_path_factory: pytest.TempPathFactory,
        monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    missing = tmp_path_factory.mktemp("machine") / "absent.txt"
    monkeypatch.setenv("PRIVATE_DENY_LIST", str(missing))
    assert check.main(repo) == 1
    assert "PRIVATE_DENY_LIST is set but" in capsys.readouterr().out


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


def test_text_content_is_scanned_whatever_its_extension(
        repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    deny(repo, "acme")
    (repo / "notes.pdf").write_text("Notes for acme.\n", encoding="utf-8")
    git(repo, "add", "notes.pdf")
    assert check.main(repo) == 1
    assert "notes.pdf: matches deny-listed identifier 'acme'" in capsys.readouterr().out


def test_binary_content_is_not_scanned(repo: Path) -> None:
    deny(repo, "acme")
    (repo / "image.bin").write_bytes(b"\x00\x01acme\x00")
    git(repo, "add", "image.bin")
    assert check.main(repo) == 0


def test_submodule_gitlink_under_the_private_directory_fails(
        repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    commit = "1" * 40
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{commit},.private/vault")
    assert check.main(repo) == 1
    assert "tracked file under the private directory: .private/vault" in capsys.readouterr().out


# ---- Linked worktrees ------------------------------------------------------------------------
# The deny-list is untracked, so a linked worktree has no .private/ of its own. The check must
# read the main checkout's copy, or the content check is skipped wherever sessions commit.

GIT_ENV = {"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
           "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}


def commit(root: Path, message: str) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "PRIVATE_DENY_LIST"} | GIT_ENV
    return subprocess.run(["git", "-c", "commit.gpgsign=false", "commit", "-q", "-m", message],
                          cwd=root, env=env, capture_output=True, text=True)


@pytest.fixture
def hooked_repo(repo: Path) -> Path:
    """A repository with the product template's pre-commit hook and check script installed, a
    deny-list in its main checkout, and one commit."""
    shutil.copytree(TEMPLATE_TOOLS / "git-hooks", repo / "tools" / "git-hooks")
    shutil.copy2(TEMPLATE_COPY, repo / "tools" / "check_confidential.py")
    git(repo, "config", "core.hooksPath", "tools/git-hooks")
    deny(repo, "zorblaxian")
    git(repo, "add", "tools")
    first = commit(repo, "initial")
    assert first.returncode == 0, first.stdout + first.stderr
    return repo


def test_worktree_reads_the_main_checkout_deny_list(
        hooked_repo: Path, tmp_path_factory: pytest.TempPathFactory,
        capsys: pytest.CaptureFixture[str]) -> None:
    worktree = tmp_path_factory.mktemp("trees") / "feature"
    git(hooked_repo, "worktree", "add", "-q", "-b", "feature", str(worktree))
    assert not (worktree / ".private").exists()
    (worktree / "notes.md").write_text("Call with Zorblaxian on Friday.\n", encoding="utf-8")
    git(worktree, "add", "notes.md")
    assert check.main(worktree) == 1
    assert "notes.md: matches deny-listed identifier 'zorblaxian'" in capsys.readouterr().out


def test_commit_from_a_linked_worktree_with_a_deny_listed_word_is_refused(
        hooked_repo: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    worktree = tmp_path_factory.mktemp("trees") / "feature"
    git(hooked_repo, "worktree", "add", "-q", "-b", "feature", str(worktree))
    assert not (worktree / ".private").exists()

    (worktree / "clean.md").write_text("Nothing confidential.\n", encoding="utf-8")
    git(worktree, "add", "clean.md")
    allowed = commit(worktree, "clean change")
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr
    assert "1 identifiers checked" in allowed.stdout + allowed.stderr

    (worktree / "notes.md").write_text("Call with Zorblaxian on Friday.\n", encoding="utf-8")
    git(worktree, "add", "notes.md")
    refused = commit(worktree, "leak")
    assert refused.returncode != 0
    output = refused.stdout + refused.stderr
    assert "notes.md: matches deny-listed identifier 'zorblaxian'" in output
    head = subprocess.run(["git", "log", "-1", "--format=%s"], cwd=worktree,
                          capture_output=True, text=True, check=True).stdout.strip()
    assert head == "clean change"


def test_the_two_copies_of_the_check_are_identical() -> None:
    assert CONTROL_COPY.read_bytes() == TEMPLATE_COPY.read_bytes(), (
        "tools/check_confidential.py and templates/product-repo/tools/check_confidential.py "
        "differ; change both copies together")


@pytest.mark.parametrize("lines", [(), ("",), ("# only a comment", "", "   "), ("#a", "#b")])
def test_deny_list_with_no_identifiers_fails(
        repo: Path, lines: tuple[str, ...], capsys: pytest.CaptureFixture[str]) -> None:
    """A deny-list that exists but names nothing would report OK without checking anything."""
    (repo / ".private").mkdir(exist_ok=True)
    (repo / ".private" / "deny-list.txt").write_text("\n".join(lines), encoding="utf-8")
    assert check.main(repo) == 1
    out = capsys.readouterr().out
    assert "check_confidential: FAILED" in out
    assert "names no identifiers" in out


def test_configured_deny_list_with_no_identifiers_fails(
        repo: Path, tmp_path_factory: pytest.TempPathFactory,
        monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The CI path: a DENY_LIST secret holding only comments is non-empty, so the workflow's
    own empty-secret check passes it on; the script must refuse it."""
    secret = tmp_path_factory.mktemp("runner") / "deny-list.txt"
    secret.write_text("# TODO: fill this in\n\n", encoding="utf-8")
    monkeypatch.setenv("PRIVATE_DENY_LIST", str(secret))
    assert check.main(repo) == 1
    assert "names no identifiers" in capsys.readouterr().out


@pytest.mark.parametrize("copy", [CONTROL_COPY, TEMPLATE_COPY], ids=["control", "product"])
def test_each_copy_refuses_an_empty_deny_list_from_the_command_line(
        repo: Path, copy: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    tools = repo / "tools"
    tools.mkdir()
    shutil.copy(copy, tools / "check_confidential.py")
    secret = tmp_path_factory.mktemp("runner") / "deny-list.txt"
    secret.write_text("# nothing here\n\n", encoding="utf-8")
    env = {**os.environ, "PRIVATE_DENY_LIST": str(secret)}
    result = subprocess.run([sys.executable, str(tools / "check_confidential.py")], cwd=repo,
                            env=env, capture_output=True, text=True)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "names no identifiers" in result.stdout


# ---- Commit messages -------------------------------------------------------------------------


def test_identifier_in_a_commit_message_fails(
        repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    deny(repo, "zorblaxcorp")
    message = repo / "MSG"
    message.write_text("Work for ZorblaxCorp client\n", encoding="utf-8")
    assert check.main(repo, ["--message", str(message)]) == 1
    assert "commit message: matches deny-listed identifier 'zorblaxcorp'" in capsys.readouterr().out


def test_a_clean_commit_message_passes(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    deny(repo, "zorblaxcorp")
    message = repo / "MSG"
    message.write_text("Work for a client, Zorblaxcorpse aside\n", encoding="utf-8")
    assert check.main(repo, ["--message", str(message)]) == 0
    assert "commit message, 1 identifiers checked" in capsys.readouterr().out


def test_a_commit_message_with_an_empty_deny_list_fails(repo: Path) -> None:
    deny(repo, "# nothing")
    message = repo / "MSG"
    message.write_text("Anything\n", encoding="utf-8")
    assert check.main(repo, ["--message", str(message)]) == 1


def test_the_commit_msg_hook_refuses_a_deny_listed_word_in_a_worktree(
        hooked_repo: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    worktree = tmp_path_factory.mktemp("trees") / "feature"
    git(hooked_repo, "worktree", "add", "-q", "-b", "feature", str(worktree))
    (worktree / "clean.md").write_text("Nothing confidential.\n", encoding="utf-8")
    git(worktree, "add", "clean.md")
    refused = commit(worktree, "Notes from the Zorblaxian call")
    assert refused.returncode != 0
    assert "commit message: matches deny-listed identifier 'zorblaxian'" in (
        refused.stdout + refused.stderr)
    allowed = commit(worktree, "Notes from the call")
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr


def test_both_hook_directories_install_a_commit_msg_hook() -> None:
    for hooks in (IRR / "tools" / "git-hooks", TEMPLATE_TOOLS / "git-hooks"):
        hook = hooks / "commit-msg"
        assert hook.is_file() and os.access(hook, os.X_OK), hook
        assert "check_confidential.py --message" in hook.read_text(encoding="utf-8")


def test_the_control_hooks_check_again_before_a_push() -> None:
    """A rebased commit skips pre-commit, so the push is where the checks must run again."""
    hook = IRR / "tools" / "git-hooks" / "pre-push"
    assert hook.is_file() and os.access(hook, os.X_OK)
    text = hook.read_text(encoding="utf-8")
    assert "tools/check_confidential.py" in text
    assert "plugins/idea-realization/scripts/check.py" in text
