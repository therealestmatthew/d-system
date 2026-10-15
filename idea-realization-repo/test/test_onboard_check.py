"""tools/onboard_check.py: the first-day checklist, against temporary repositories and homes."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import onboard_check as onboard

REMOTE = "https://example.com/team/product.git"
CONTROL_REMOTE = "https://example.com/team/control.git"
DENIED = "secret-client-name"


def git(*args: str) -> None:
    subprocess.run(["git", *args], check=True, capture_output=True)


@pytest.fixture(autouse=True)
def isolated_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No global or system git configuration leaks in, and no plugin root override."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for name in ("IDEA_REALIZATION_ROOT", "CLAUDE_PROJECT_DIR", "PRIVATE_DENY_LIST"):
        monkeypatch.delenv(name, raising=False)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def machine(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """A control checkout, a product checkout and a home directory that pass every check."""
    control, product, home = tmp_path / "control", tmp_path / "product", tmp_path / "home"
    git("init", "-q", str(control))
    git("-C", str(control), "config", "user.email", "ana@example.com")
    git("-C", str(control), "config", "core.hooksPath", "tools/git-hooks")
    git("-C", str(control), "remote", "add", "origin", CONTROL_REMOTE)
    git("init", "-q", str(product))
    git("-C", str(product), "remote", "add", "origin", REMOTE)
    write(control / "docs" / "systems.yaml",
          "schema_version: 1\nowners:\n  repository-owner: Owner.\n"
          "  ana:\n    description: Ana.\n    emails: [ana@example.com]\n")
    write(control / ".idea-realization" / "project.yaml",
          "schema_version: 1\ncontrol:\n  integration_branch: dev\n")
    write(control / ".idea-realization" / "product.yaml",
          f"schema_version: 1\nname: product\nremote: {REMOTE}\nintegration_branch: dev\n")
    write(control / ".idea-realization" / "local.yaml",
          f"product_root: {product}\naws_read_profile: sandbox-read\n"
          "aws_deploy_profile: sandbox-deploy\naws_region: eu-west-1\nhandle: ana\n"
          f"control_remote: {CONTROL_REMOTE}\nproduct_remote: {REMOTE}\n")
    (control / ".idea-realization" / "staging").mkdir()
    write(control / ".idea-realization" / "install-state.json",
          '{"schema_version": 1, "files": [], "consent": [],\n'
          ' "directories": [{"path": ".idea-realization/staging", "feature": "partition"}]}\n')
    write(control / ".private" / "deny-list.txt", DENIED + "\n")
    write(home / ".aws" / "config",
          "[profile sandbox-read]\nregion = eu-west-1\n[profile sandbox-deploy]\n"
          "region = eu-west-1\n")
    return control, {"HOME": str(home)}


def every_tool(name: str) -> str | None:
    return f"/usr/bin/{name}"


def authenticated(command: Sequence[str]) -> int:
    return 0


def fixes(lines: list[onboard.Line]) -> dict[str, str]:
    return {line.item: line.detail for line in lines
            if not line.ok and not getattr(line, "pending", False)}


def test_a_complete_machine_is_all_ok(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    lines = onboard.run_checks(root, env, every_tool, authenticated)
    assert fixes(lines) == {}
    assert next(line.detail for line in lines if line.item == "developer handle") == "ana"


def test_missing_tools_and_gh_login_are_fixes(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    lines = onboard.run_checks(root, env, lambda name: None, authenticated)
    assert {"uv", "Claude Code", "gh"} <= set(fixes(lines))
    lines = onboard.run_checks(root, env, every_tool, lambda command: 1)
    assert "not authenticated" in fixes(lines)["gh"]


def test_gh_auth_status_is_the_command_run(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    ran: list[list[str]] = []
    onboard.run_checks(root, env, every_tool, lambda command: ran.append(list(command)) or 0)
    assert ran == [["gh", "auth", "status"]]


def test_git_email_not_in_owners_is_a_fix_and_the_email_is_not_printed(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    git("-C", str(root), "config", "user.email", "someone@example.com")
    found = fixes(onboard.run_checks(root, env, every_tool, authenticated))
    assert "developer handle" in found
    assert "someone@example.com" not in found["developer handle"]


def test_unset_email_and_hooks_path_are_fixes(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    git("-C", str(root), "config", "--unset", "user.email")
    git("-C", str(root), "config", "--unset", "core.hooksPath")
    found = fixes(onboard.run_checks(root, env, every_tool, authenticated))
    assert "git user.email" in found and "core.hooksPath" in found


def test_deny_list_missing_or_empty_is_a_fix_and_its_content_is_never_printed(
        tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    lines = onboard.run_checks(root, env, every_tool, authenticated)
    assert all(DENIED not in str(line) for line in lines)
    (root / ".private" / "deny-list.txt").write_text("", encoding="utf-8")
    assert "is empty" in fixes(onboard.run_checks(root, env, every_tool, authenticated))[
        "deny-list"]
    (root / ".private" / "deny-list.txt").unlink()
    assert "is missing" in fixes(onboard.run_checks(root, env, every_tool, authenticated))[
        "deny-list"]


def test_missing_local_yaml_is_a_fix(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    (root / ".idea-realization" / "local.yaml").unlink()
    lines = onboard.run_checks(root, env, every_tool, authenticated)
    found = fixes(lines)
    assert "is missing" in found["local.yaml"]
    assert "product checkout" in found
    # No profile is configured without local.yaml, so the AWS lines wait for the owner's setup.
    assert "AWS read profile" in {line.item for line in lines if line.pending}


def test_invalid_local_yaml_stops_the_dependent_checks(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    write(root / ".idea-realization" / "local.yaml", "not_a_key: 1\n")
    found = fixes(onboard.run_checks(root, env, every_tool, authenticated))
    assert "local.yaml" in found and "remaining checks" in found


def test_placeholders_in_local_yaml_are_named(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    write(root / ".idea-realization" / "local.yaml",
          "product_root: REPLACE-WITH-THE-PATH\naws_read_profile: sandbox-read\n")
    found = fixes(onboard.run_checks(root, env, every_tool, authenticated))
    assert found["local.yaml"] == "still a placeholder: product_root"
    assert "product_root is not set" in found["product checkout"]


def test_product_checkout_with_another_origin_is_a_fix(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    git("-C", str(tmp_path / "product"), "remote", "set-url", "origin",
        "https://example.com/team/other.git")
    assert "verify fails" in fixes(onboard.run_checks(root, env, every_tool, authenticated))[
        "product checkout"]


def test_control_checkout_with_another_origin_is_a_fix(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    git("-C", str(root), "remote", "set-url", "origin", "https://example.com/team/other.git")
    assert "control repository" in fixes(onboard.run_checks(root, env, every_tool, authenticated))


def test_missing_aws_cli_is_a_fix(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    lines = onboard.run_checks(root, env, lambda name: None if name == "aws" else every_tool(name),
                               authenticated)
    assert set(fixes(lines)) == {"AWS CLI"}
    assert "install AWS CLI v2" in fixes(lines)["AWS CLI"]


def test_doctor_is_a_checked_line(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    lines = onboard.run_checks(root, env, every_tool, authenticated)
    assert next(line for line in lines if line.item == "doctor").ok
    (root / ".idea-realization" / "install-state.json").write_text(
        '{"schema_version": 1, "directories": [], "consent": [],\n'
        ' "files": [{"path": "ideas/ideas.jsonl", "sha256": "0", "feature": "ideas"}]}\n')
    found = fixes(onboard.run_checks(root, env, every_tool, authenticated))
    assert set(found) == {"doctor"} and "ideas/ideas.jsonl missing" in found["doctor"]
    (root / ".idea-realization" / "install-state.json").unlink()
    assert "run the scaffold" in fixes(onboard.run_checks(root, env, every_tool,
                                                          authenticated))["doctor"]


def test_missing_scaffold_is_a_fix(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    (root / ".idea-realization" / "staging").rmdir()
    assert "scaffold" in fixes(onboard.run_checks(root, env, every_tool, authenticated))


def test_aws_profile_problems_are_fixes(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    write(Path(env["HOME"]) / ".aws" / "config", "[profile sandbox-read]\n[default]\n")
    found = fixes(onboard.run_checks(root, env, every_tool, authenticated))
    assert "not in your AWS config" in found["AWS deploy profile"]
    assert "default profile" in found["AWS machine rule"]
    lines = onboard.run_checks(root, {**env, "AWS_ACCESS_KEY_ID": "x"}, every_tool,
                               authenticated)
    assert any(not line.ok and line.detail.startswith("AWS_ACCESS_KEY_ID is set")
               for line in lines)


def test_same_profile_for_both_roles_is_a_fix(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    env = {**env, "IDEA_REALIZATION_AWS_DEPLOY_PROFILE": "sandbox-read"}
    assert "AWS profiles" in fixes(onboard.run_checks(root, env, every_tool, authenticated))


def test_main_exits_one_and_lists_manual_steps(tmp_path: Path,
                                               monkeypatch: pytest.MonkeyPatch,
                                               capsys: pytest.CaptureFixture[str]) -> None:
    root, env = machine(tmp_path)
    (root / ".private" / "deny-list.txt").unlink()
    monkeypatch.setenv("HOME", env["HOME"])
    monkeypatch.setattr(onboard, "run_quietly", authenticated)  # no network call in a test
    for name in list(os.environ):
        if name.startswith("AWS_"):
            monkeypatch.delenv(name)
    code = onboard.main(["--root", str(root)])
    out = capsys.readouterr().out
    assert code == 1
    assert "FIX  deny-list" in out
    assert "check_aws_machine.py --probe" in out and "aws-sandbox whoami" in out
    assert "doctor.py" not in out.split("Run by hand")[1]



def without_aws_profiles(root: Path) -> None:
    """local.yaml as it is before the owner's AWS setup: no profile, no region."""
    local = root / ".idea-realization" / "local.yaml"
    local.write_text("".join(line + "\n" for line in local.read_text().splitlines()
                             if not line.startswith("aws_")), encoding="utf-8")


def test_aws_lines_are_pending_notes_until_a_profile_is_configured(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    """Owner ruling: before the AWS setup exists, onboarding must not fail on AWS."""
    root, env = machine(tmp_path)
    without_aws_profiles(root)
    no_aws = lambda name: None if name == "aws" else every_tool(name)  # noqa: E731
    lines = onboard.run_checks(root, env, no_aws, authenticated)
    assert fixes(lines) == {}
    pending = {line.item for line in lines if line.pending}
    assert pending == {"AWS CLI", "AWS read profile", "AWS deploy profile", "AWS region"}
    assert all(str(line).startswith("NOTE") for line in lines if line.pending)
    monkeypatch.setenv("HOME", env["HOME"])
    monkeypatch.setattr(onboard, "run_quietly", authenticated)
    monkeypatch.setattr(onboard.shutil, "which", no_aws)
    for name in list(os.environ):
        if name.startswith(("AWS_", "IDEA_REALIZATION_AWS_")):
            monkeypatch.delenv(name)
    assert onboard.main(["--root", str(root)]) == 0
    assert "All checks OK (4 pending the owner's AWS setup)" in capsys.readouterr().out


def test_once_a_profile_is_configured_aws_problems_fail_again(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    without_aws_profiles(root)
    local = root / ".idea-realization" / "local.yaml"
    local.write_text(local.read_text() + "aws_read_profile: sandbox-read\n", encoding="utf-8")
    found = fixes(onboard.run_checks(root, env, lambda n: None if n == "aws" else every_tool(n),
                                     authenticated))
    assert {"AWS CLI", "AWS deploy profile", "AWS region"} <= set(found)


def test_the_machine_rule_fails_even_before_the_aws_setup(tmp_path: Path) -> None:
    root, env = machine(tmp_path)
    without_aws_profiles(root)
    write(Path(env["HOME"]) / ".aws" / "config", "[default]\nregion = eu-west-1\n")
    assert "default profile" in fixes(onboard.run_checks(root, env, every_tool,
                                                         authenticated))["AWS machine rule"]
