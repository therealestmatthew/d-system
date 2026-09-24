"""Tests for the dev-CI grant check (phase-grd-02, REQ-028 R06).

Every `gh run list` payload below was recorded from the live repository on 2026-09-24 with
`gh run list --workflow ci.yaml --commit <sha> --json <the tool's JSON_FIELDS>`. Cases that need
a conclusion the live history does not contain (timed_out, cancelled, ...) change only that field
of a recorded run. `git` and `gh` are replaced by a fake runner, so no test touches the network or
the repository's refs.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


tool = _load("check_dev_ci")

HEAD = "51dd9e69e8a5b0f0cd6d8858596d6dc07d8d5e47"
OLDER = "024443c04138ad4b6fb0b8850796d6ee0b87feee"

# Recorded: dev's head after phase-grd-01 merged, CI green.
SUCCESS_AT_HEAD = {
    "conclusion": "success", "createdAt": "2026-09-24T09:45:34Z", "databaseId": 35983187775,
    "event": "push", "headBranch": "dev", "headSha": HEAD, "status": "completed",
    "url": "https://github.com/therealestmatthew/d-system/actions/runs/35983187775",
    "workflowName": "CI",
}
# Recorded: a red dev push from the six-day red period (REQ-028's context).
FAILURE_OLDER = {
    "conclusion": "failure", "createdAt": "2026-09-23T14:41:25Z", "databaseId": 35876027675,
    "event": "push", "headBranch": "dev", "headSha": OLDER, "status": "completed",
    "url": "https://github.com/therealestmatthew/d-system/actions/runs/35876027675",
    "workflowName": "CI",
}
# Recorded: the grd-02 claim commit's run while it was still running.
IN_PROGRESS = {
    "conclusion": "", "createdAt": "2026-09-24T10:21:03Z", "databaseId": 35986703694,
    "event": "push", "headBranch": "dev", "headSha": HEAD, "status": "in_progress",
    "url": "https://github.com/therealestmatthew/d-system/actions/runs/35986703694",
    "workflowName": "CI",
}
# Recorded: a pull_request run (a different commit; headSha changed to HEAD for the test).
PULL_REQUEST = {
    "conclusion": "success", "createdAt": "2026-09-12T17:15:37Z", "databaseId": 34707689849,
    "event": "pull_request", "headBranch": "dev", "headSha": HEAD, "status": "completed",
    "url": "https://github.com/therealestmatthew/d-system/actions/runs/34707689849",
    "workflowName": "CI",
}
GH_404 = (
    "HTTP 404: workflow nope.yaml not found on the default branch "
    "(https://api.github.com/repos/therealestmatthew/d-system/actions/workflows/nope.yaml)"
)


def at_head(run: dict[str, Any], **changes: Any) -> dict[str, Any]:
    return {**run, "headSha": HEAD, **changes}


class FakeRunner:
    """Answers `git rev-parse` from a ref table and `gh run list` from a queue of payloads."""

    def __init__(
        self,
        payloads: list[Any],
        refs: dict[str, str] | None = None,
        gh_rc: int = 0,
        gh_stderr: str = "",
    ) -> None:
        self.payloads = payloads
        self.refs = refs if refs is not None else {"dev": HEAD, "origin/dev": HEAD}
        self.gh_rc = gh_rc
        self.gh_stderr = gh_stderr
        self.gh_calls: list[list[str]] = []

    def __call__(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        if args[:2] == ["git", "rev-parse"]:
            ref = args[-1].removesuffix("^{commit}")
            sha = self.refs.get(ref) or next(
                (full for full in self.refs.values() if full.startswith(ref)), None
            )
            return subprocess.CompletedProcess(args, 0 if sha else 1, (sha or "") + "\n", "")
        assert args[:3] == ["gh", "run", "list"]
        self.gh_calls.append(args)
        if self.gh_rc:
            return subprocess.CompletedProcess(args, self.gh_rc, "", self.gh_stderr)
        payload = self.payloads[min(len(self.gh_calls), len(self.payloads)) - 1]
        text = payload if isinstance(payload, str) else json.dumps(payload)
        return subprocess.CompletedProcess(args, 0, text, "")


# The five acceptance cases of REQ-028 R06.


def test_success_at_head_exits_0() -> None:
    verdict = tool.check(None, FakeRunner([[SUCCESS_AT_HEAD]]))
    assert verdict.code == 0
    assert SUCCESS_AT_HEAD["url"] in verdict.message


def test_failure_at_head_exits_1_naming_the_run() -> None:
    verdict = tool.check(None, FakeRunner([[at_head(FAILURE_OLDER)]]))
    assert verdict.code == 1
    assert FAILURE_OLDER["url"] in verdict.message


def test_in_progress_exits_2() -> None:
    verdict = tool.check(None, FakeRunner([[IN_PROGRESS]]))
    assert verdict.code == 2
    assert "in_progress" in verdict.message


def test_run_only_for_an_older_commit_exits_2() -> None:
    verdict = tool.check(None, FakeRunner([[FAILURE_OLDER]]))
    assert verdict.code == 2
    assert "no push run" in verdict.message


def test_gh_error_exits_2() -> None:
    verdict = tool.check(None, FakeRunner([], gh_rc=1, gh_stderr=GH_404))
    assert verdict.code == 2
    assert "HTTP 404" in verdict.message


# The review's sixth case: an unpushed dev is told apart from CI not having finished.


def test_unpushed_dev_exits_2_without_asking_gh() -> None:
    runner = FakeRunner([[SUCCESS_AT_HEAD]], refs={"dev": HEAD, "origin/dev": OLDER})
    verdict = tool.check(None, runner)
    assert verdict.code == 2
    assert "dev is not pushed" in verdict.message
    assert runner.gh_calls == []


# The query and the filters.


def test_query_names_workflow_and_dev_head_commit() -> None:
    runner = FakeRunner([[SUCCESS_AT_HEAD]])
    tool.check(None, runner)
    (args,) = runner.gh_calls
    assert args[args.index("--workflow") + 1] == "ci.yaml"
    assert args[args.index("--commit") + 1] == HEAD


def test_pull_request_run_does_not_count() -> None:
    assert tool.check(None, FakeRunner([[PULL_REQUEST]])).code == 2


def test_other_branch_does_not_count() -> None:
    assert tool.check(None, FakeRunner([[at_head(SUCCESS_AT_HEAD, headBranch="main")]])).code == 2


def test_latest_completed_run_decides() -> None:
    old_red = at_head(FAILURE_OLDER, createdAt="2026-09-24T09:00:00Z")
    assert tool.check(None, FakeRunner([[old_red, SUCCESS_AT_HEAD]])).code == 0
    new_red = at_head(FAILURE_OLDER, createdAt="2026-09-24T10:00:00Z")
    assert tool.check(None, FakeRunner([[SUCCESS_AT_HEAD, new_red]])).code == 1


# The conclusion mapping (owner ruling, 2026-09-24).


@pytest.mark.parametrize(
    ("conclusion", "code"),
    [
        ("success", 0),
        ("failure", 1),
        ("timed_out", 1),
        ("startup_failure", 1),
        ("cancelled", 2),
        ("skipped", 2),
        ("neutral", 2),
        ("action_required", 2),
    ],
)
def test_conclusion_mapping(conclusion: str, code: int) -> None:
    run = at_head(SUCCESS_AT_HEAD, conclusion=conclusion)
    assert tool.check(None, FakeRunner([[run]])).code == code


# --commit, and git and gh failures.


def test_commit_override_expands_short_sha_and_skips_push_check() -> None:
    runner = FakeRunner([[FAILURE_OLDER]], refs={"dev": HEAD, "origin/dev": HEAD, "x": OLDER})
    verdict = tool.check(OLDER[:7], runner)
    assert verdict.code == 1
    assert runner.gh_calls[0][runner.gh_calls[0].index("--commit") + 1] == OLDER


def test_unresolvable_commit_exits_2() -> None:
    verdict = tool.check("deadbeef", FakeRunner([[SUCCESS_AT_HEAD]]))
    assert verdict.code == 2
    assert "could not resolve deadbeef" in verdict.message


def test_invalid_json_exits_2() -> None:
    assert tool.check(None, FakeRunner(["not json"])).code == 2


def test_missing_gh_binary_exits_2() -> None:
    def runner(args: list[str]) -> subprocess.CompletedProcess[str]:
        if args[0] == "gh":
            raise FileNotFoundError("gh")
        return FakeRunner([])(args)

    verdict = tool.check(None, runner)
    assert verdict.code == 2
    assert "gh could not run" in verdict.message


# --wait.


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds

    def __call__(self) -> float:
        return self.now


def test_wait_polls_until_green() -> None:
    clock = FakeClock()
    runner = FakeRunner([[IN_PROGRESS], [IN_PROGRESS], [SUCCESS_AT_HEAD]])
    verdict = tool.check_with_wait(None, 600, 30, runner, clock.sleep, clock)
    assert verdict.code == 0
    assert len(runner.gh_calls) == 3
    assert clock.sleeps == [30, 30]


def test_wait_stops_at_red() -> None:
    clock = FakeClock()
    runner = FakeRunner([[IN_PROGRESS], [at_head(FAILURE_OLDER)], [SUCCESS_AT_HEAD]])
    assert tool.check_with_wait(None, 600, 30, runner, clock.sleep, clock).code == 1
    assert len(runner.gh_calls) == 2


def test_wait_times_out_with_2() -> None:
    clock = FakeClock()
    runner = FakeRunner([[IN_PROGRESS]])
    verdict = tool.check_with_wait(None, 100, 30, runner, clock.sleep, clock)
    assert verdict.code == 2
    assert "still unknown after waiting 100 s" in verdict.message
    assert len(runner.gh_calls) == 4
    assert clock.now <= 100


def test_no_wait_queries_once() -> None:
    clock = FakeClock()
    runner = FakeRunner([[IN_PROGRESS]])
    verdict = tool.check_with_wait(None, 0, 30, runner, clock.sleep, clock)
    assert verdict.code == 2
    assert "still unknown" not in verdict.message
    assert len(runner.gh_calls) == 1


def test_main_rejects_negative_wait() -> None:
    with pytest.raises(SystemExit) as exc:
        tool.main(["--wait", "-1"])
    assert exc.value.code == 2
