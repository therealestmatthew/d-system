"""Tests for the build-review command runner (phase-asr-02, REQ-030 R02).

Every run happens against a disposable git repository built under `tmp_path`, whose `dev` branch
carries a fixture backlog. The real gate checks and `uv sync` are replaced with small commands, so
no test runs the suite inside itself or touches this checkout's worktrees.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "run_review_checks.py"

spec = importlib.util.spec_from_file_location("run_review_checks", SCRIPT)
assert spec and spec.loader
rrc = importlib.util.module_from_spec(spec)
sys.modules["run_review_checks"] = rrc  # dataclasses resolve their module through sys.modules
spec.loader.exec_module(rrc)

PHASES: list[dict[str, Any]] = [
    {
        "id": "phase-fix-01",
        "verification": [
            "echo listed check",
            "test -f marker.txt",
            "Read the document and confirm it says so.",
            "echo gate one",
        ],
    },
    {"id": "phase-fix-02", "verification": ["echo before", "sh -c 'exit 3'", "echo after"]},
    {"id": "phase-fix-03", "verification": ["echo attempt >> \"$HOME_MARK\"; exit 5"]},
    {"id": "phase-fix-04", "verification": ["sleep 30"]},
]
GATES = ("echo gate one", "echo gate two")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "dev")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    backlog = repo / "docs" / "09-backlog" / "backlog.yaml"
    backlog.parent.mkdir(parents=True)
    backlog.write_text(yaml.safe_dump({"items": PHASES}), encoding="utf-8")
    (repo / "marker.txt").write_text("present\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "fixture backlog")
    return repo


def _run(
    repo: Path, tmp_path: Path, phase: str, commit: str = "dev", **kwargs: Any
) -> tuple[int, dict[str, Any]]:
    kwargs.setdefault("gate_checks", GATES)
    kwargs.setdefault("setup", ())
    return rrc.run(phase, commit, repo=repo, worktree_parent=tmp_path / "worktrees", **kwargs)


def _worktrees(repo: Path) -> list[str]:
    return [line for line in _git(repo, "worktree", "list", "--porcelain").splitlines()
            if line.startswith("worktree ")]


def test_a_phase_whose_commands_run_lists_each_with_its_exit_code(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)

    code, manifest = _run(repo, tmp_path, "phase-fix-01")

    assert code == 0
    assert manifest["result"] == "passed"
    rows = [(e["kind"], e["command"], e["exit_code"]) for e in manifest["entries"]]
    assert rows == [
        ("verification", "echo listed check", 0),
        ("verification", "test -f marker.txt", 0),  # runs at the commit, inside the worktree
        ("verification", "Read the document and confirm it says so.", None),
        ("verification+gate", "echo gate one", 0),  # listed once, not run twice
        ("gate", "echo gate two", 0),
    ]
    prose = manifest["entries"][2]
    assert prose["ran"] is False and prose["note"] == "not run: not a command"
    first = manifest["entries"][0]
    evidence = repo / first["file"]
    assert evidence.read_text(encoding="utf-8") == "listed check\n"
    assert first["sha256"] == hashlib.sha256(evidence.read_bytes()).hexdigest()
    assert first["file"].startswith("_working/review-checks/phase-fix-01/")
    on_disk = json.loads((repo / first["file"]).parent.joinpath("manifest.json").read_text())
    assert on_disk == manifest


def test_a_failing_command_is_recorded_and_the_rest_still_run(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)

    code, manifest = _run(repo, tmp_path, "phase-fix-02")

    assert code == 1
    assert manifest["result"] == "failed"
    assert [e["exit_code"] for e in manifest["entries"]] == [0, 3, 0, 0, 0]


def test_a_failing_command_is_not_retried(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _make_repo(tmp_path)
    mark = tmp_path / "attempts.txt"
    monkeypatch.setenv("HOME_MARK", str(mark))

    code, manifest = _run(repo, tmp_path, "phase-fix-03")

    assert code == 1
    assert manifest["entries"][0]["exit_code"] == 5
    assert mark.read_text(encoding="utf-8") == "attempt\n"


def test_a_command_past_the_time_limit_is_killed_and_recorded(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)

    code, manifest = _run(repo, tmp_path, "phase-fix-04", timeout=0.5)

    assert code == 1
    entry = manifest["entries"][0]
    assert entry["exit_code"] == rrc.TIMEOUT_EXIT and entry["note"] == "timed out"
    assert _worktrees(repo) == [f"worktree {repo}"]


def test_an_unknown_phase_id_is_refused_before_anything_is_created(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)

    with pytest.raises(rrc.Refused, match="unknown phase id"):
        _run(repo, tmp_path, "phase-nope-99")

    assert not (tmp_path / "worktrees").exists()
    assert not (repo / "_working").exists()


def test_an_unresolvable_commit_is_refused(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)

    with pytest.raises(rrc.Refused, match="does not resolve"):
        _run(repo, tmp_path, "phase-fix-01", commit="no-such-ref")


def test_the_list_is_read_from_dev_not_from_the_commit(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    _git(repo, "switch", "-q", "-c", "agent/phase-fix-02")
    backlog = repo / "docs" / "09-backlog" / "backlog.yaml"
    weakened = [dict(p, verification=["echo nothing to see"]) if p["id"] == "phase-fix-02" else p
                for p in PHASES]
    backlog.write_text(yaml.safe_dump({"items": weakened}), encoding="utf-8")
    _git(repo, "commit", "-q", "-am", "drop the failing check on the branch")

    code, manifest = _run(repo, tmp_path, "phase-fix-02", commit="agent/phase-fix-02")

    assert code == 1
    assert "sh -c 'exit 3'" in [e["command"] for e in manifest["entries"]]
    assert manifest["backlog"].startswith("dev ")


@pytest.mark.parametrize("phase", ["phase-fix-01", "phase-fix-02", "phase-fix-04"])
def test_no_worktree_is_left_behind(tmp_path: Path, phase: str) -> None:
    repo = _make_repo(tmp_path)

    _run(repo, tmp_path, phase, timeout=0.5)

    assert _worktrees(repo) == [f"worktree {repo}"]
    assert list((tmp_path / "worktrees").iterdir()) == []


def test_the_worktree_is_removed_when_the_run_is_interrupted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _make_repo(tmp_path)

    def interrupted(*args: Any, **kwargs: Any) -> Any:
        raise KeyboardInterrupt

    monkeypatch.setattr(rrc, "execute", interrupted)
    with pytest.raises(KeyboardInterrupt):
        _run(repo, tmp_path, "phase-fix-01")

    assert _worktrees(repo) == [f"worktree {repo}"]


@pytest.mark.parametrize("entry, expected", [
    ("uv run pytest", True),
    ("cd ts && npm run build", True),
    ("D_SYSTEM_DATA_ROOT=/tmp/x uv run python -m src.governance", True),
    ("Run focused preflight tests against temporary source trees.", False),
    ("Adversarial review of the diff", False),
    ("exit 3", False),  # a bash builtin is not a program on PATH, so it counts as prose
    ("", False),
])
def test_is_command(entry: str, expected: bool) -> None:
    assert rrc.is_command(entry) is expected


def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_the_cli_refuses_an_extra_command_argument() -> None:
    result = _cli("phase-asr-02", "dev", "echo", "injected")

    assert result.returncode == 2
    assert "unrecognized arguments: echo injected" in result.stderr


def test_the_cli_refuses_an_option_it_does_not_define() -> None:
    result = _cli("phase-asr-02", "dev", "--command", "echo injected")

    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr


def test_the_cli_refuses_an_unknown_phase_id() -> None:
    # Refused while reading dev's backlog, before any worktree or evidence directory is created.
    result = _cli("phase-nope-99", "dev")

    assert result.returncode == 2
    assert "unknown phase id 'phase-nope-99'" in result.stderr
    assert not (ROOT / "_working" / "review-checks" / "phase-nope-99").exists()
