"""The workstream registry: its check, the claim and release commands, and cli dispatch."""

from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path
from typing import Any

import paths
import pytest
import workstreams
import yaml
from checks import workstreams as feature
from conftest import SCRIPTS, as_developer

SYSTEMS = {
    "schema_version": 1,
    "owners": {
        "repository-owner": "The person accountable for this repository.",
        "ana": {"description": "Ana, user interface.", "emails": ["ana@example.com"]},
        "ben": {"description": "Ben, backend.", "emails": ["ben@example.com"]},
    },
    "systems": [],
}


def stream(stream_id: str, path: str, owner: str = "", **changes: Any) -> dict[str, Any]:
    return {
        "id": stream_id,
        "title": stream_id.upper(),
        "owner": owner,
        "status": "claimed" if owner else "open",
        "paths": [path],
        "interfaces": [],
        **changes,
    }


def phase(phase_id: str, agent: str, deliverables: list[str], **changes: Any) -> dict[str, Any]:
    return {"id": phase_id, "status": "active", "agent": agent, "deliverables": deliverables,
            **changes}


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for key in ("IDEA_REALIZATION_HANDLE", "IDEA_REALIZATION_ROOT", "CLAUDE_PROJECT_DIR",
                "IDEA_REALIZATION_DOCS_ROOT", "IDEA_REALIZATION_BACKLOG_PATH",
                "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0"):
        monkeypatch.delenv(key, raising=False)
    (tmp_path / "docs").mkdir()
    (tmp_path / "backlog").mkdir()
    (tmp_path / "docs" / "systems.yaml").write_text(yaml.safe_dump(SYSTEMS, sort_keys=False))
    return tmp_path


def write_registry(root: Path, streams: list[dict[str, Any]]) -> Path:
    path = root / "docs" / "workstreams.yaml"
    path.write_text(yaml.safe_dump({"schema_version": 1, "workstreams": streams},
                                   sort_keys=False))
    return path


def write_backlog(root: Path, items: list[dict[str, Any]]) -> None:
    (root / "backlog" / "backlog.yaml").write_text(yaml.safe_dump({"items": items}))


def config(root: Path) -> paths.Config:
    return paths.resolve({"root": str(root)}, env={})


def problems(root: Path) -> list[str]:
    return feature.check(config(root))


def registry(root: Path) -> dict[str, Any]:
    return yaml.safe_load((root / "docs" / "workstreams.yaml").read_text())


# --- The check ------------------------------------------------------------------------------------


def test_an_absent_registry_has_no_problems(repo: Path) -> None:
    assert problems(repo) == []


def test_a_valid_registry_is_clean(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", "ana"), stream("api", "product:api/")])
    assert problems(repo) == []


def test_a_schema_violation_is_reported(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", paths=[])])
    found = problems(repo)
    assert len(found) == 1 and "workstreams.0.paths" in found[0]


def test_an_unknown_field_is_a_schema_violation(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", lock=True)])
    assert any("lock" in line for line in problems(repo))


def test_a_duplicate_id_is_reported(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/"), stream("ui", "product:mobile/")])
    assert problems(repo) == ["docs/workstreams.yaml: duplicate workstream id ui"]


@pytest.mark.parametrize("owner", ["", "carla", "repository-owner"])
def test_claimed_needs_a_developer_owner(repo: Path, owner: str) -> None:
    write_registry(repo, [stream("ui", "product:web/", status="claimed", owner=owner)])
    found = problems(repo)
    assert len(found) == 1 and "is claimed but its owner" in found[0]


def test_open_must_have_no_owner(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", status="open", owner="ana")])
    found = problems(repo)
    assert len(found) == 1 and "is open but names owner 'ana'" in found[0]


def test_overlapping_paths_name_both_workstreams(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/"), stream("forms", "product:web/forms/")])
    assert problems(repo) == [
        "docs/workstreams.yaml: workstreams ui and forms overlap: ui path product:web/, "
        "forms path product:web/forms/"
    ]


def test_a_product_path_and_an_unprefixed_path_with_the_same_tail_do_not_conflict(
        repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", "ana"), stream("site", "web/", "ben")])
    write_backlog(repo, [phase("phase-site", "ben/agent-builder", ["web/index.html"])])
    assert problems(repo) == []


def test_a_deliverable_inside_another_developers_workstream_is_an_error(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", "ana")])
    write_backlog(repo, [phase("phase-api", "ben/agent-builder", ["product:web/app.tsx"])])
    assert problems(repo) == [
        "backlog/backlog.yaml: phase phase-api (agent handle ben) declares deliverable "
        "product:web/app.tsx inside workstream ui owned by ana"
    ]


def test_a_matching_cross_workstream_approval_is_clean(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", "ana")])
    approval = [{"workstream": "ui", "approved_by": "ana"}]
    write_backlog(repo, [phase("phase-api", "ben/agent-builder", ["product:web/app.tsx"],
                               cross_workstream=approval)])
    assert problems(repo) == []


def test_an_approval_by_the_wrong_handle_is_still_an_error(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", "ana")])
    approval = [{"workstream": "ui", "approved_by": "ben"}]
    write_backlog(repo, [phase("phase-api", "ben/agent-builder", ["product:web/app.tsx"],
                               cross_workstream=approval)])
    assert len(problems(repo)) == 1


def test_phases_outside_the_checked_cases_are_not_errors(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", "ana"), stream("api", "product:api/")])
    write_backlog(repo, [
        phase("phase-own", "ana/agent-builder", ["product:web/app.tsx"]),
        phase("phase-queued", "ben/agent-builder", ["product:web/app.tsx"], status="queued"),
        phase("phase-open", "ben/agent-builder", ["product:api/server.py"]),
        phase("phase-shared", "ben/agent-builder", ["README.md"]),
    ])
    assert problems(repo) == []


def test_a_working_phase_without_a_handle_is_an_error(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", "ana")])
    write_backlog(repo, [
        phase("phase-anon", "agent-builder", ["README.md"]),
        phase("phase-later", "agent-builder", ["README.md"], status="queued"),
    ])
    assert problems(repo) == [
        "backlog/backlog.yaml: phase phase-anon is claimed without a developer handle "
        "(agent must be <handle>/agent-...)"
    ]


def test_agents_are_not_checked_without_workstreams(repo: Path) -> None:
    write_registry(repo, [])
    write_backlog(repo, [phase("phase-anon", "agent-builder", ["README.md"])])
    assert problems(repo) == []
    (repo / "docs" / "workstreams.yaml").unlink()
    assert problems(repo) == []


def test_a_blocked_phase_is_checked(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/", "ana")])
    write_backlog(repo, [phase("phase-api", "ben/agent-builder", ["product:web/"],
                               status="blocked")])
    assert len(problems(repo)) == 1


# --- Claim and release ----------------------------------------------------------------------------


def run(root: Path, *args: str) -> int:
    command, rest = args[0], list(args[1:])
    return workstreams.main([command, "--root", str(root), *rest])


def test_claim_by_environment_handle(repo: Path, monkeypatch: pytest.MonkeyPatch,
                                     capsys: pytest.CaptureFixture[str]) -> None:
    write_registry(repo, [stream("ui", "product:web/"), stream("api", "product:api/")])
    as_developer(monkeypatch, "ana")
    assert run(repo, "claim", "ui") == 0
    claimed = registry(repo)["workstreams"]
    assert claimed[0]["owner"] == "ana" and claimed[0]["status"] == "claimed"
    assert [s["id"] for s in claimed] == ["ui", "api"]
    assert list(claimed[0]) == ["id", "title", "owner", "status", "paths", "interfaces"]
    out = capsys.readouterr().out
    assert "commit only docs/workstreams.yaml" in out and "pull with rebase" in out
    assert problems(repo) == []


def test_claim_by_git_email(repo: Path) -> None:
    write_registry(repo, [stream("api", "product:api/")])
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "Ben@example.com"],
                   check=True)
    assert run(repo, "claim", "api") == 0
    assert registry(repo)["workstreams"][0]["owner"] == "ben"


def test_claim_of_a_claimed_workstream_is_refused(
        repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    path = write_registry(repo, [stream("ui", "product:web/", "ana")])
    before = path.read_text()
    as_developer(monkeypatch, "ben")
    assert run(repo, "claim", "ui") == 1
    assert "already claimed by ana" in capsys.readouterr().err
    assert path.read_text() == before


def test_claim_of_an_unknown_workstream_is_refused(
        repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    write_registry(repo, [stream("ui", "product:web/")])
    as_developer(monkeypatch, "ben")
    assert run(repo, "claim", "absent") == 1
    assert "unknown workstream 'absent'" in capsys.readouterr().err


def test_claim_without_an_identity_fails(repo: Path, monkeypatch: pytest.MonkeyPatch,
                                         capsys: pytest.CaptureFixture[str]) -> None:
    write_registry(repo, [stream("ui", "product:web/")])
    as_developer(monkeypatch, "carla")
    assert run(repo, "claim", "ui") == 1
    assert "carla" in capsys.readouterr().err


def test_release_by_a_non_owner_is_refused(repo: Path, monkeypatch: pytest.MonkeyPatch,
                                           capsys: pytest.CaptureFixture[str]) -> None:
    path = write_registry(repo, [stream("ui", "product:web/", "ana")])
    before = path.read_text()
    as_developer(monkeypatch, "ben")
    assert run(repo, "release", "ui") == 1
    assert "only its owner may release it" in capsys.readouterr().err
    assert path.read_text() == before


def test_release_by_the_owner(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_registry(repo, [stream("ui", "product:web/", "ana")])
    as_developer(monkeypatch, "ana")
    assert run(repo, "release", "ui") == 0
    released = registry(repo)["workstreams"][0]
    assert released["owner"] == "" and released["status"] == "open"


def test_a_claim_that_fails_validation_restores_the_file(
        repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    path = write_registry(repo, [stream("ui", "product:web/")])
    path.write_text("# hand-written comment\n" + path.read_text())
    before = path.read_text()
    write_backlog(repo, [phase("phase-api", "ben/agent-builder", ["product:web/app.tsx"])])
    as_developer(monkeypatch, "ana")
    assert run(repo, "claim", "ui") == 1
    assert "registry was restored" in capsys.readouterr().err
    assert path.read_text() == before


def test_show_and_check(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(repo, "show") == 0
    assert "not in use" in capsys.readouterr().out
    write_registry(repo, [stream("ui", "product:web/", "ana"), stream("api", "product:api/")])
    assert run(repo, "show") == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines == ["ui  claimed  ana  UI  product:web/", "api  open  -  API  product:api/"]
    assert run(repo, "check") == 0
    broken = copy.deepcopy(registry(repo))
    broken["workstreams"].append(stream("ui", "product:mobile/"))
    write_registry(repo, broken["workstreams"])
    assert run(repo, "check") == 1
    assert "duplicate workstream id ui" in capsys.readouterr().out


def test_a_refused_path_exits_two(repo: Path) -> None:
    assert workstreams.main(["show", "--root", str(repo), "--docs-root", "../outside"]) == 2


# --- Dispatch -------------------------------------------------------------------------------------


def test_the_feature_exposes_check_and_the_command() -> None:
    assert callable(feature.check)
    assert "workstreams" in feature.COMMANDS


def test_cli_dispatches_the_command(repo: Path) -> None:
    write_registry(repo, [stream("ui", "product:web/")])
    cli = SCRIPTS / "cli.py"
    listed = subprocess.run([sys.executable, str(cli), "--help"], capture_output=True, text=True,
                            check=False)
    assert "workstreams" in listed.stdout
    shown = subprocess.run([sys.executable, str(cli), "workstreams", "show", "--root", str(repo)],
                           capture_output=True, text=True, check=False)
    assert shown.returncode == 0, shown.stderr
    assert shown.stdout.startswith("ui  open  -  UI")
