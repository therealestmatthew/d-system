"""tools/github/apply_rulesets.sh: it applies a kind's rulesets only to the repository this
machine's configuration names for that kind, with a fake `gh` on PATH and a temporary local.yaml."""

from __future__ import annotations

import json
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
# Records every call, one line each, and answers the calls apply_rulesets.sh makes. The body of
# every ruleset sent with --input is appended, one JSON document per line, to $GH_BODIES.
printf '%s\\n' "$*" >> "$GH_LOG"
prev=""
for arg in "$@"; do
  if [ "$prev" = "--input" ]; then
    python3 -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))))' "$arg" \\
      >> "$GH_BODIES"
  fi
  prev="$arg"
done
case "$*" in
  "auth status") exit 0 ;;
  *"/collaborators/"* | "api orgs/"*"/repos/"*)
    # Repository access: 204 (no output, exit 0) unless the actor is named in $GH_NO_ACCESS.
    if [ -n "${GH_NO_ACCESS:-}" ] && [[ "$*" == *"$GH_NO_ACCESS"* ]]; then
      echo "gh: Not Found (HTTP 404)" >&2; exit 1
    fi
    exit 0 ;;
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
    monkeypatch.setenv("GH_BODIES", str(tmp_path / "gh-bodies.jsonl"))
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


def sent_rulesets() -> dict[str, dict]:
    """Every ruleset body sent to gh, by ruleset name."""
    log = Path(os.environ["GH_BODIES"])
    lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    bodies = [json.loads(line) for line in lines]
    return {body["name"]: body for body in bodies}


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


@pytest.mark.parametrize(("kind", "repo"), [("control", CONTROL), ("product", PRODUCT)])
def test_each_kind_sends_its_branch_rulesets_and_both_demo_tag_rulesets(
        machine: Path, kind: str, repo: str) -> None:
    both_named(machine)
    result = run(repo, kind, "user:owner")
    assert result.returncode == 0, result.stdout + result.stderr
    assert sorted(sent_rulesets()) == sorted(
        [f"{kind}-dev", f"{kind}-main", "demo-tags-create", "demo-tags-protect"])


@pytest.mark.parametrize(("merger", "actor"), [
    ("user:owner", {"actor_id": 4242, "actor_type": "User", "bypass_mode": "always"}),
    ("team:team-org/owners", {"actor_id": 4343, "actor_type": "Team", "bypass_mode": "always"}),
])
def test_only_the_main_merger_may_create_demo_tags(
        machine: Path, merger: str, actor: dict) -> None:
    both_named(machine)
    result = run(CONTROL, "control", merger)
    assert result.returncode == 0, result.stdout + result.stderr
    create = sent_rulesets()["demo-tags-create"]
    assert create["target"] == "tag"
    assert create["conditions"]["ref_name"]["include"] == ["refs/tags/demo-*"]
    assert [rule["type"] for rule in create["rules"]] == ["creation"]
    assert create["bypass_actors"] == [actor]


def test_nobody_may_move_or_delete_demo_tags(machine: Path) -> None:
    both_named(machine)
    result = run(CONTROL, "control", "user:owner")
    assert result.returncode == 0, result.stdout + result.stderr
    protect = sent_rulesets()["demo-tags-protect"]
    assert protect["target"] == "tag"
    assert protect["conditions"]["ref_name"]["include"] == ["refs/tags/demo-*"]
    assert sorted(rule["type"] for rule in protect["rules"]) == [
        "deletion", "non_fast_forward", "update"]
    assert protect["bypass_actors"] == []


def test_the_main_merger_bypasses_main_through_pull_requests_only(machine: Path) -> None:
    both_named(machine)
    result = run(CONTROL, "control", "user:owner")
    assert result.returncode == 0, result.stdout + result.stderr
    sent = sent_rulesets()
    assert sent["control-main"]["bypass_actors"] == [
        {"actor_id": 4242, "actor_type": "User", "bypass_mode": "pull_request"}]
    assert sent["control-dev"]["bypass_actors"] == []


def test_no_committed_ruleset_names_a_bypass_actor() -> None:
    for path in sorted((IRR / ".github" / "rulesets").glob("*.json")):
        assert json.loads(path.read_text(encoding="utf-8"))["bypass_actors"] == [], path.name


@pytest.mark.parametrize(("merger", "check"), [
    ("user:outsider", f"api repos/{CONTROL}/collaborators/outsider"),
    ("team:team-org/strangers", f"api orgs/team-org/teams/strangers/repos/{CONTROL}"),
])
def test_a_main_merger_without_access_to_the_repository_is_refused(
        machine: Path, monkeypatch: pytest.MonkeyPatch, merger: str, check: str) -> None:
    both_named(machine)
    monkeypatch.setenv("GH_NO_ACCESS", merger.rsplit("/", 1)[-1].removeprefix("user:"))
    result = run(CONTROL, "control", merger)
    assert result.returncode != 0
    assert "has no access to" in result.stderr
    calls = gh_calls()
    assert any(call.startswith(check) for call in calls), calls
    assert sent_rulesets() == {}, "no ruleset may be sent for an actor without access"
    assert not any("-X PATCH" in call for call in calls), "the repository must not be changed"


@pytest.mark.parametrize(("merger", "check"), [
    ("user:owner", f"api repos/{CONTROL}/collaborators/owner"),
    ("team:team-org/owners", f"api orgs/team-org/teams/owners/repos/{CONTROL}"),
])
def test_a_main_merger_with_access_to_the_repository_passes(
        machine: Path, merger: str, check: str) -> None:
    both_named(machine)
    result = run(CONTROL, "control", merger)
    assert result.returncode == 0, result.stdout + result.stderr
    calls = gh_calls()
    assert any(call.startswith(check) for call in calls), calls
    first_send = next(i for i, call in enumerate(calls) if "--input" in call)
    assert calls.index(next(c for c in calls if c.startswith(check))) < first_send
