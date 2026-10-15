"""tools/github/apply_rulesets.sh: it applies a kind's rulesets only to the repository this
machine's configuration names for that kind, with a fake `gh` on PATH and a temporary local.yaml."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

IRR = Path(__file__).resolve().parent.parent
SCRIPT = IRR / "tools" / "github" / "apply_rulesets.sh"

CONTROL = "team-org/control-repo"
PRODUCT = "team-org/product-repo"

FAKE_GH = """#!/usr/bin/env bash
# Records every call, one line each, and answers the calls apply_rulesets.sh makes.
printf '%s\\n' "$*" >> "$GH_LOG"
case "$*" in
  "auth status") exit 0 ;;
  "api users/"*) echo 4242 ;;
  "api orgs/"*) echo 4343 ;;
  *"/branches/"*) exit 0 ;;
  "api -X PATCH"*) echo "  default_branch=dev" ;;
  "api -X POST"*) echo 7 ;;
  "api -X PUT"*) exit 0 ;;
  *"/rulesets?"*) exit 0 ;;
  *) echo "fake gh: unexpected call: $*" >&2; exit 9 ;;
esac
"""


@pytest.fixture
def machine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A control checkout with a local.yaml, and a fake gh first on PATH."""
    for name in list(os.environ):
        if name.startswith(("IDEA_REALIZATION_", "CLAUDE_PLUGIN_OPTION_")):
            monkeypatch.delenv(name)
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    root = tmp_path / "control"
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".idea-realization").mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH, encoding="utf-8")
    gh.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("GH_LOG", str(tmp_path / "gh.log"))
    monkeypatch.setenv("IDEA_REALIZATION_ROOT", str(root))
    return root


def local_yaml(root: Path, text: str) -> None:
    (root / ".idea-realization" / "local.yaml").write_text(text, encoding="utf-8")


def both_named(root: Path) -> None:
    local_yaml(root, f"control_github: {CONTROL}\nproduct_github: {PRODUCT}\n")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


def gh_calls() -> list[str]:
    log = Path(os.environ["GH_LOG"])
    return log.read_text(encoding="utf-8").splitlines() if log.exists() else []


def test_the_matching_repository_and_kind_are_applied(machine: Path) -> None:
    both_named(machine)
    result = run(CONTROL, "control", "user:owner")
    assert result.returncode == 0, result.stdout + result.stderr
    calls = gh_calls()
    assert f"api -X POST repos/{CONTROL}/rulesets --input" in "\n".join(calls)
    assert all(PRODUCT not in call for call in calls)


def test_github_names_compare_without_case(machine: Path) -> None:
    both_named(machine)
    result = run("Team-Org/Product-Repo", "product", "user:owner")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(("repo", "kind"), [(PRODUCT, "control"), (CONTROL, "product"),
                                            ("team-org/someone-else", "control")])
def test_a_repository_that_is_not_the_kinds_configured_one_is_refused(
        machine: Path, repo: str, kind: str) -> None:
    both_named(machine)
    result = run(repo, kind, "user:owner")
    assert result.returncode != 0
    assert "does not match" in result.stderr
    assert f"{kind}_github" in result.stderr
    assert gh_calls() == [], "nothing may reach GitHub before the target is verified"


@pytest.mark.parametrize("text", [
    None,  # no local.yaml at all
    f"product_github: {PRODUCT}\n",
    "control_github: REPLACE-WITH-THE-CONTROL-REPOSITORY-ORG-AND-NAME\n",
])
def test_an_unset_repository_name_is_refused(machine: Path, text: str | None) -> None:
    if text is not None:
        local_yaml(machine, text)
    result = run(CONTROL, "control", "user:owner")
    assert result.returncode != 0
    assert "control_github" in result.stderr
    assert "not set" in result.stderr
    assert gh_calls() == []


@pytest.mark.parametrize("remote", [
    "git@github.com:team-org/control-repo.git",
    "https://github.com/team-org/control-repo.git",
    "https://github.com/team-org/control-repo",
    "ssh://git@github.com/team-org/control-repo.git",
])
def test_the_remote_url_names_the_repository_when_the_github_name_is_unset(
        machine: Path, remote: str) -> None:
    local_yaml(machine, f"control_remote: {remote}\n")
    assert run(CONTROL, "control", "user:owner").returncode == 0
    refused = run(PRODUCT, "control", "user:owner")
    assert refused.returncode != 0
    assert "does not match" in refused.stderr


def test_a_remote_that_is_not_on_github_is_refused(machine: Path) -> None:
    local_yaml(machine, "control_remote: https://example.com/team-org/control-repo.git\n")
    result = run(CONTROL, "control", "user:owner")
    assert result.returncode != 0
    assert "not set" in result.stderr
    assert gh_calls() == []


def test_shellcheck_is_clean() -> None:
    if shutil.which("shellcheck") is None:
        pytest.skip("shellcheck is not installed")
    result = subprocess.run(["shellcheck", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
