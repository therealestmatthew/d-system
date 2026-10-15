"""project.yaml is valid, feeds paths.py, and the control checkout must be its remote."""

from __future__ import annotations

import subprocess
from pathlib import Path

import paths
import project
import pytest
from checks import project as feature
from conftest import PLUGIN_ROOT

REMOTE = "git@forge.example.com:team/hack-control.git"
REPOSITORY = PLUGIN_ROOT.parent.parent


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True)


def control(tmp_path: Path, remote: str, origin: str | None = REMOTE) -> Path:
    git(tmp_path, "init", "-q")
    if origin:
        git(tmp_path, "remote", "add", "origin", origin)
    (tmp_path / ".idea-realization").mkdir()
    (tmp_path / project.RECORD).write_text(
        f"schema_version: 1\ncontrol:\n  remote: {remote}\n  integration_branch: dev\n")
    return tmp_path


def test_no_record_gets_no_report(tmp_path: Path) -> None:
    assert project.control_origin(tmp_path) == (None, None)
    assert feature.check(paths.resolve({"root": str(tmp_path)}, env={})) == []


def test_a_placeholder_remote_is_not_compared(tmp_path: Path) -> None:
    root = control(tmp_path, "REPLACE-WITH-THE-CONTROL-REPOSITORY-GIT-URL", origin=None)
    problem, note = project.control_origin(root)
    assert problem is None and note is not None and "placeholder" in note


@pytest.mark.parametrize("remote", [REMOTE, "https://forge.example.com/team/hack-control"])
def test_a_matching_origin_passes(tmp_path: Path, remote: str) -> None:
    root = control(tmp_path, remote)
    assert project.control_origin(root) == (None, "matches .idea-realization/project.yaml "
                                                  "control.remote")
    assert project.main(["verify", "--root", str(root)]) == 0


def test_another_origin_is_reported_by_check_and_verify(tmp_path: Path) -> None:
    root = control(tmp_path, "git@forge.example.com:team/other.git")
    found = feature.check(paths.resolve({"root": str(root)}, env={}))
    assert len(found) == 1 and "not the control repository" in found[0]
    assert project.main(["verify", "--root", str(root)]) == 1


def test_a_missing_origin_is_reported(tmp_path: Path) -> None:
    root = control(tmp_path, REMOTE, origin=None)
    problem, _ = project.control_origin(root)
    assert problem is not None and "no origin" in problem


def test_show_marks_placeholders(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = control(tmp_path, "REPLACE-WITH-THE-CONTROL-REPOSITORY-GIT-URL", origin=None)
    assert project.main(["show", "--root", str(root)]) == 0
    out = capsys.readouterr().out
    assert "control.remote: REPLACE-WITH-THE-CONTROL-REPOSITORY-GIT-URL  (placeholder" in out
    assert "control.integration_branch: dev" in out


@pytest.mark.parametrize("github", ["team", "<org>/<repo>", "a/b/c"])
def test_a_malformed_github_slug_is_refused(tmp_path: Path, github: str) -> None:
    root = control(tmp_path, REMOTE)
    record = root / project.RECORD
    record.write_text(record.read_text() + f"  github: '{github}'\n")
    with pytest.raises(paths.PathError, match="project.yaml"):
        project.read_record(root)


def test_this_repositorys_record_carries_the_team_values() -> None:
    record = project.read_record(REPOSITORY)
    assert record is not None
    assert record["control"]["integration_branch"] == "dev"
    demo, freeze = "-".join(["2026", "11", "05"]), "-".join(["2026", "11", "03"])
    assert record["demo"] == {"date": demo, "freeze": freeze, "tag_prefix": "demo-"}
    assert set(record["urls"]) == {"hackathon_portal", "demo_app", "team_chat"}
    assert "region" in record["aws"]
    # Repository URLs and organization stay placeholders in the tracked file.
    assert project.is_placeholder(record["control"]["remote"])
    assert project.is_placeholder(record["control"]["github"])


def test_this_repository_ignores_local_yaml() -> None:
    ignored = subprocess.run(["git", "-C", str(REPOSITORY), "check-ignore", "-q",
                              ".idea-realization/local.yaml"], check=False)
    assert ignored.returncode == 0
    assert (REPOSITORY / ".idea-realization" / "local.example.yaml").is_file()
