"""Tests for the workbench read routes (`src/api/routes/workbench.py`, ADR-015).

Covers: the routes exist only when `D_SYSTEM_DEMO_TERMINAL=1` (404, not merely refusing, with
the flag unset — REQ-007 W14); the platform route reports the host platform and per-shell
availability by reusing `src.api.routes.demo_terminal`'s own availability check (REQ-007 W17);
injection-source enumeration matches a direct listing of
`.claude/skills/`, `.claude/agents/` and the governed `PROMPT-*` files under `docs/02-prompts/`;
the curated overrides file relabels, replaces injected text, and hides entries; path
validation rejects `..` traversal, an absolute path, and a symlink whose target leaves the
repository, all on the *resolved* path; a root directory listing carries no `_private/` or
gitignored entry; the idea route matches an independent `fold()` recomputation (REQ-007 W10);
the backlog route's queue view matches an independent read of `next_up` plus ready-by-priority
(REQ-007 W11); the reveal-in-explorer action rejects escapes and non-POST, with its spawned
argument list asserted via monkeypatching (no real opener process); and every other route
responds to GET only.
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from collections.abc import Callable, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient

import src.api as api_module
import src.main as main_module
from src.api.routes import workbench as workbench_module
from src.api.routes.workbench import (
    AGENTS_DIR,
    BACKLOG_PATH,
    IDEA_QUEUE_STATUS_PRECEDENCE,
    INJECTION_OVERRIDES_PATH_ENV_VAR,
    PROMPT_FILENAME_PREFIX,
    PROMPTS_DIR,
    REPO_ROOT,
    SKILLS_DIR,
    PathEscapesRepositoryError,
    resolve_repo_relative_path,
)
from src.db.ideas import fold, load_events
from src.governance.backlog import queue_order, readiness

WORKBENCH_PLATFORM_PATH = "/api/v1/workbench/platform"
WORKBENCH_INJECTION_SOURCES_PATH = "/api/v1/workbench/injection-sources"
WORKBENCH_LIST_PATH = "/api/v1/workbench/list"
WORKBENCH_SEARCH_PATH = "/api/v1/workbench/search"
WORKBENCH_ABSOLUTE_PATH_PATH = "/api/v1/workbench/absolute-path"
WORKBENCH_IDEAS_PATH = "/api/v1/workbench/ideas"
WORKBENCH_IDEAS_QUEUE_PATH = "/api/v1/workbench/ideas/queue"
WORKBENCH_BACKLOG_PATH = "/api/v1/workbench/backlog"
WORKBENCH_BACKLOG_QUEUE_PATH = "/api/v1/workbench/backlog/queue"
WORKBENCH_REVEAL_PATH = "/api/v1/workbench/reveal"


# --- app-rebuild fixture: mirrors test/test_demo_terminal.py's rebuild_app -------------------


def _uncache_workbench_modules() -> None:
    """Force the next import of demo_terminal/workbench to genuinely re-execute them.

    Same reasoning as `test_demo_terminal.py`'s `_uncache_demo_terminal_module`: CPython's
    `from package import submodule` skips re-importing whenever `submodule` is already an
    attribute on the parent package object, so that attribute must be cleared too.
    """
    routes_package = sys.modules.get("src.api.routes")
    for name in ("src.api.routes.demo_terminal", "src.api.routes.workbench"):
        sys.modules.pop(name, None)
    if routes_package is not None:
        for attr in ("demo_terminal", "workbench"):
            if hasattr(routes_package, attr):
                delattr(routes_package, attr)


def _live_workbench_module() -> Any:
    """The `src.api.routes.workbench` module object the currently-built app actually runs.

    `rebuild_app` pops `src.api.routes.workbench` from `sys.modules` and reloads
    `src.api`, which re-imports it — creating a *new* module object each time. The
    `workbench_module` name imported at the top of this file keeps pointing at whichever
    object was current at collection time, so monkeypatching it after a `rebuild_app` call
    would patch a module the running app no longer uses. Reading `sys.modules` fresh, after
    the rebuild, is what makes the patch land on the code path actually being exercised.
    """
    return sys.modules["src.api.routes.workbench"]


@pytest.fixture
def rebuild_app(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[..., FastAPI]]:
    def _build(*, flag: str | None) -> FastAPI:
        if flag is None:
            monkeypatch.delenv("D_SYSTEM_DEMO_TERMINAL", raising=False)
        else:
            monkeypatch.setenv("D_SYSTEM_DEMO_TERMINAL", flag)
        _uncache_workbench_modules()
        importlib.reload(api_module)
        importlib.reload(main_module)
        return main_module.app

    yield _build

    monkeypatch.delenv("D_SYSTEM_DEMO_TERMINAL", raising=False)
    _uncache_workbench_modules()
    importlib.reload(api_module)
    importlib.reload(main_module)


# --- flag gating (REQ-007 W14) ----------------------------------------------------------------


def test_every_workbench_route_absent_with_flag_unset(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    app = rebuild_app(flag=None)
    assert "src.api.routes.workbench" not in sys.modules
    client = TestClient(app)
    assert client.get(WORKBENCH_PLATFORM_PATH).status_code == 404
    assert client.get(WORKBENCH_INJECTION_SOURCES_PATH).status_code == 404
    assert client.get(WORKBENCH_LIST_PATH).status_code == 404
    assert client.get(WORKBENCH_SEARCH_PATH).status_code == 404
    assert client.get(WORKBENCH_ABSOLUTE_PATH_PATH).status_code == 404


def test_routes_registered_with_flag_set(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    assert "src.api.routes.workbench" in sys.modules
    client = TestClient(app)
    assert client.get(WORKBENCH_PLATFORM_PATH).status_code == 200
    assert client.get(WORKBENCH_INJECTION_SOURCES_PATH).status_code == 200
    assert client.get(WORKBENCH_LIST_PATH).status_code == 200


# --- host platform and shell availability (REQ-007 W17) ----------------------------------------


def test_platform_route_reports_linux_and_bash_available_but_not_cmd_or_powershell(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    """On this (Linux) host: `platform` reports `linux`, bash is available, and the two
    Windows-only shells are not — the identical family rule
    `src.api.routes.demo_terminal._shell_is_available_on_host` applies to the unavailable-shell
    refusal, exercised here through the reused function rather than a second copy of it.
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)

    response = client.get(WORKBENCH_PLATFORM_PATH)
    assert response.status_code == 200
    body = response.json()

    assert body["platform"] == "linux"
    availability = {entry["shell"]: entry["available"] for entry in body["shells"]}
    assert availability == {"bash": True, "cmd": False, "powershell": False}


def test_platform_route_rejects_non_get(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    assert client.post(WORKBENCH_PLATFORM_PATH).status_code == 405
    assert client.put(WORKBENCH_PLATFORM_PATH).status_code == 405
    assert client.delete(WORKBENCH_PLATFORM_PATH).status_code == 405


# --- injection-source enumeration (REQ-007 W04) ------------------------------------------------


def test_enumeration_matches_the_three_directories_with_no_active_overrides(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    """With the shipped overrides file (no active overrides), each category's ids are exactly
    the corresponding directory's entries, and each default injection text matches REQ-007 W04.
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)

    response = client.get(WORKBENCH_INJECTION_SOURCES_PATH)
    assert response.status_code == 200
    body = response.json()

    expected_skill_names = sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir())
    expected_agent_names = sorted(
        p.stem for p in AGENTS_DIR.iterdir() if p.is_file() and p.suffix == ".md"
    )
    expected_prompt_names = sorted(
        p.name
        for p in PROMPTS_DIR.iterdir()
        if p.is_file() and p.suffix == ".md" and p.name.startswith(PROMPT_FILENAME_PREFIX)
    )

    assert [entry["id"] for entry in body["skills"]] == expected_skill_names
    assert [entry["id"] for entry in body["agents"]] == expected_agent_names
    assert [entry["id"] for entry in body["prompts"]] == expected_prompt_names

    assert expected_skill_names, "fixture assumption: .claude/skills/ is non-empty"
    assert expected_agent_names, "fixture assumption: .claude/agents/ is non-empty"
    assert expected_prompt_names, "fixture assumption: docs/02-prompts/ has PROMPT-* files"

    sample_skill = expected_skill_names[0]
    skill_entry = next(e for e in body["skills"] if e["id"] == sample_skill)
    assert skill_entry["injection"] == f"/{sample_skill}"

    sample_agent = expected_agent_names[0]
    agent_entry = next(e for e in body["agents"] if e["id"] == sample_agent)
    assert agent_entry["injection"] == f"Use the {sample_agent} agent to "

    sample_prompt = expected_prompt_names[0]
    prompt_entry = next(e for e in body["prompts"] if e["id"] == sample_prompt)
    assert prompt_entry["injection"] == (
        f"Execute docs/02-prompts/{sample_prompt}: read it in full and follow its prompt block"
    )

    # README.md and non-PROMPT-* files under docs/02-prompts/ are not governed prompt documents.
    assert "README.md" not in expected_prompt_names


def test_overrides_relabel_replace_and_hide_each_take_effect(
    rebuild_app: Callable[..., FastAPI],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    skill_names = sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir())
    assert len(skill_names) >= 3, "fixture assumption: at least three skills exist"
    relabeled, replaced, hidden = skill_names[0], skill_names[1], skill_names[2]

    overrides_file = tmp_path / "injection-overrides.json"
    overrides_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "skills": {
                    relabeled: {"label": "Custom Label"},
                    replaced: {"injection": "/custom-injection-text"},
                    hidden: {"hidden": True},
                },
                "agents": {},
                "prompts": {},
            }
        )
    )
    monkeypatch.setenv(INJECTION_OVERRIDES_PATH_ENV_VAR, str(overrides_file))

    app = rebuild_app(flag="1")
    client = TestClient(app)
    body = client.get(WORKBENCH_INJECTION_SOURCES_PATH).json()

    skills_by_id = {entry["id"]: entry for entry in body["skills"]}
    assert skills_by_id[relabeled]["label"] == "Custom Label"
    assert skills_by_id[relabeled]["injection"] == f"/{relabeled}"  # injection unchanged
    assert skills_by_id[replaced]["injection"] == "/custom-injection-text"
    assert skills_by_id[replaced]["label"] == replaced  # label unchanged
    assert hidden not in skills_by_id


# --- path validation (ADR-015 rule 2) ----------------------------------------------------------


def test_resolve_repo_relative_path_accepts_a_plain_relative_path() -> None:
    resolved = resolve_repo_relative_path("src")
    assert resolved == (REPO_ROOT / "src").resolve()


def test_resolve_repo_relative_path_rejects_dotdot_traversal() -> None:
    with pytest.raises(PathEscapesRepositoryError):
        resolve_repo_relative_path("../../etc/passwd")


def test_resolve_repo_relative_path_rejects_absolute_path() -> None:
    with pytest.raises(PathEscapesRepositoryError):
        resolve_repo_relative_path("/etc/passwd")


def test_resolve_repo_relative_path_rejects_symlink_escape() -> None:
    outside_target = tempfile.mkdtemp(prefix="workbench-escape-target-")
    link_path = REPO_ROOT / "test" / "_workbench_symlink_escape_tmp"
    try:
        link_path.symlink_to(outside_target, target_is_directory=True)
        with pytest.raises(PathEscapesRepositoryError):
            resolve_repo_relative_path("test/_workbench_symlink_escape_tmp")
    finally:
        if link_path.is_symlink() or link_path.exists():
            link_path.unlink()
        os.rmdir(outside_target)


def test_list_route_rejects_dotdot_traversal(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_LIST_PATH, params={"path": "../../etc"})
    assert response.status_code == 400


def test_list_route_rejects_absolute_path(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_LIST_PATH, params={"path": "/etc"})
    assert response.status_code == 400


def test_search_route_rejects_symlink_escape(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)

    outside_target = tempfile.mkdtemp(prefix="workbench-escape-target-")
    link_path = REPO_ROOT / "test" / "_workbench_symlink_escape_tmp"
    try:
        link_path.symlink_to(outside_target, target_is_directory=True)
        response = client.get(
            WORKBENCH_SEARCH_PATH, params={"path": "test/_workbench_symlink_escape_tmp"}
        )
        assert response.status_code == 400
    finally:
        if link_path.is_symlink() or link_path.exists():
            link_path.unlink()
        os.rmdir(outside_target)


# --- listing excludes _private/ and gitignored entries (ADR-015 rule 3) -----------------------


def test_root_listing_contains_no_private_or_gitignored_entry(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    private_dir = REPO_ROOT / "_private"
    private_dir_preexisted = private_dir.is_dir()
    if not private_dir_preexisted:
        private_dir.mkdir()
    try:
        assert private_dir.is_dir(), "fixture assumption: a real _private/ dir exists"

        app = rebuild_app(flag="1")
        client = TestClient(app)
        response = client.get(WORKBENCH_LIST_PATH, params={"path": "."})
        assert response.status_code == 200
        names = {entry["name"] for entry in response.json()}

        assert (REPO_ROOT / ".venv").is_dir(), "fixture assumption: a real gitignored dir exists"
        assert ".venv" not in names
        assert "_private" not in names
        assert ".git" not in names
    finally:
        if not private_dir_preexisted and private_dir.is_dir():
            private_dir.rmdir()


def test_search_under_root_never_descends_into_gitignored_directories(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    """A recursive search rooted at `.` never returns anything from `.venv/` — proving ignored
    directories are pruned before being walked, not merely filtered out of the final result.
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_SEARCH_PATH, params={"path": "."})
    assert response.status_code == 200
    paths = [entry["path"] for entry in response.json()]
    assert not any(p.startswith(".venv/") for p in paths)


def test_search_extension_filter_matches_html_and_svg_only(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(
        WORKBENCH_SEARCH_PATH, params={"path": "docs", "ext": [".md"]}
    )
    assert response.status_code == 200
    body = response.json()
    assert body, "fixture assumption: docs/ has at least one .md file"
    assert all(entry["name"].endswith(".md") for entry in body)


def test_search_text_filter_narrows_by_name(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(
        WORKBENCH_SEARCH_PATH, params={"path": "docs/02-prompts", "q": "workbench"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body, "fixture assumption: at least one prompt filename contains 'workbench'"
    assert all("workbench" in entry["name"].lower() for entry in body)


# --- Copy absolute path (ADR-015 consequences, REQ-007 W09) ------------------------------------


def test_absolute_path_route_matches_an_independent_repo_root_join(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    """The returned absolute path equals a repo-root join computed here, independently of the
    route's own `resolve_repo_relative_path` call.
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_ABSOLUTE_PATH_PATH, params={"path": "src/main.py"})
    assert response.status_code == 200
    expected = str((REPO_ROOT / "src" / "main.py").resolve())
    assert response.json()["absolute_path"] == expected


def test_absolute_path_route_rejects_dotdot_traversal(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_ABSOLUTE_PATH_PATH, params={"path": "../../etc/passwd"})
    assert response.status_code == 400


def test_absolute_path_route_rejects_absolute_input(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_ABSOLUTE_PATH_PATH, params={"path": "/etc/passwd"})
    assert response.status_code == 400


def test_absolute_path_route_rejects_symlink_escape(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)

    outside_target = tempfile.mkdtemp(prefix="workbench-abspath-escape-target-")
    link_path = REPO_ROOT / "test" / "_workbench_abspath_symlink_escape_tmp"
    try:
        link_path.symlink_to(outside_target, target_is_directory=True)
        response = client.get(
            WORKBENCH_ABSOLUTE_PATH_PATH,
            params={"path": "test/_workbench_abspath_symlink_escape_tmp"},
        )
        assert response.status_code == 400
    finally:
        if link_path.is_symlink() or link_path.exists():
            link_path.unlink()
        os.rmdir(outside_target)


def test_absolute_path_route_404s_a_gitignored_path_never_confirming_existence(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    """`/absolute-path` must apply the same `_private`/gitignore exclusion (ADR-015 rule 3) that
    `/list` and `/search` apply when rendering entries — the finding this guards against:
    `/absolute-path` checked only the repo-boundary rule (rule 2), so a gitignored path (here,
    `.venv`, git-ignored by `.gitignore`) 200'd with its absolute location while `/list` and
    `/search` never show it and `/reveal` refuses it — a clean existence/location oracle over
    content the sibling routes hide. The correct response is 404, indistinguishable from a
    genuinely nonexistent path, not the 400 `/reveal` uses for its own exclusion.
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)

    venv_dir = REPO_ROOT / ".venv"
    assert venv_dir in workbench_module._git_ignored_paths([venv_dir]), (
        "fixture assumption: .venv is git-ignored at the repository root"
    )
    response = client.get(WORKBENCH_ABSOLUTE_PATH_PATH, params={"path": ".venv"})
    assert response.status_code == 404


def test_absolute_path_route_rejects_non_get(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    assert client.post(WORKBENCH_ABSOLUTE_PATH_PATH).status_code == 405
    assert client.put(WORKBENCH_ABSOLUTE_PATH_PATH).status_code == 405
    assert client.delete(WORKBENCH_ABSOLUTE_PATH_PATH).status_code == 405


# --- GET-only (REQ-007 W14) ---------------------------------------------------------------------


def test_injection_sources_route_rejects_non_get(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    assert client.post(WORKBENCH_INJECTION_SOURCES_PATH).status_code == 405
    assert client.put(WORKBENCH_INJECTION_SOURCES_PATH).status_code == 405
    assert client.delete(WORKBENCH_INJECTION_SOURCES_PATH).status_code == 405


def test_list_route_rejects_non_get(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    assert client.post(WORKBENCH_LIST_PATH).status_code == 405
    assert client.put(WORKBENCH_LIST_PATH).status_code == 405
    assert client.delete(WORKBENCH_LIST_PATH).status_code == 405


def test_search_route_rejects_non_get(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    assert client.post(WORKBENCH_SEARCH_PATH).status_code == 405
    assert client.put(WORKBENCH_SEARCH_PATH).status_code == 405
    assert client.delete(WORKBENCH_SEARCH_PATH).status_code == 405


# --- Idea Explorer route (ADR-015 rule 4, REQ-007 W10) ------------------------------------------


def test_ideas_route_matches_independent_fold_recomputation(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    """The route's rows equal an independent `fold(load_events())` run computed here, in the
    test, from the same log — not by trusting the route's own JSON, which is what W10's
    verification ("assert the rendered rows match an independent fold() run") requires.
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_IDEAS_PATH)
    assert response.status_code == 200
    body = {row["id"]: row for row in response.json()}

    expected_state = fold(load_events())
    assert expected_state, "fixture assumption: the idea log is non-empty"
    assert set(body) == set(expected_state)
    for idea_id, entry in expected_state.items():
        row = body[idea_id]
        assert row["title"] == entry["title"]
        assert row["status"] == entry["status"]
        assert row["created"] == entry["created"]
        assert row["updated"] == entry["updated"]
        assert row["annotation_count"] == len(entry["annotations"])
        assert row["link_count"] == len(entry["links"])


def test_ideas_route_reports_zero_annotation_and_link_counts_as_zero(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    body = {row["id"]: row for row in client.get(WORKBENCH_IDEAS_PATH).json()}
    state = fold(load_events())
    zero_annotation_ideas = [key for key, entry in state.items() if not entry["annotations"]]
    assert zero_annotation_ideas, "fixture assumption: at least one idea has no annotations"
    for idea_id in zero_annotation_ideas:
        assert body[idea_id]["annotation_count"] == 0


def test_ideas_queue_route_orders_by_status_precedence_then_age(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_IDEAS_QUEUE_PATH)
    assert response.status_code == 200
    body = response.json()

    state = fold(load_events())
    assert state, "fixture assumption: the idea log is non-empty"

    def expected_key(idea_id: str) -> tuple[int, datetime, str]:
        entry = state[idea_id]
        precedence = IDEA_QUEUE_STATUS_PRECEDENCE[entry["status"]]
        return (precedence, datetime.fromisoformat(entry["created"]), idea_id)

    expected_order = sorted(state, key=expected_key)
    assert [row["id"] for row in body] == expected_order

    # Every idea still open or triaged outranks every promoted or discarded idea.
    open_or_triaged = {idea_id for idea_id, entry in state.items() if entry["status"] == "open"}
    terminal = {idea_id for idea_id, entry in state.items() if entry["status"] == "discarded"}
    assert open_or_triaged, "fixture assumption: at least one open idea exists"
    assert terminal, "fixture assumption: at least one discarded idea exists"
    ranks = {row["id"]: index for index, row in enumerate(body)}
    assert max(ranks[idea_id] for idea_id in open_or_triaged) < min(
        ranks[idea_id] for idea_id in terminal
    )


def test_ideas_routes_reject_non_get(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    assert client.post(WORKBENCH_IDEAS_PATH).status_code == 405
    assert client.post(WORKBENCH_IDEAS_QUEUE_PATH).status_code == 405


# --- Backlog Explorer route (ADR-015 rule 4, REQ-007 W11) ---------------------------------------


def test_backlog_route_matches_backlog_yaml(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_BACKLOG_PATH)
    assert response.status_code == 200
    body = {row["id"]: row for row in response.json()}

    catalog = yaml.safe_load(BACKLOG_PATH.read_text(encoding="utf-8"))
    items = {item["id"]: item for item in catalog["items"]}
    next_up = catalog.get("next_up", [])
    assert set(body) == set(items)
    for phase_id, item in items.items():
        row = body[phase_id]
        assert row["title"] == item["title"]
        assert row["status"] == item["status"]
        assert row["priority"] == item["priority"]
        assert row["depends_on"] == item["depends_on"]
        expected_position = next_up.index(phase_id) + 1 if phase_id in next_up else None
        assert row["queue_position"] == expected_position


def test_backlog_queue_route_matches_ready_by_priority_ordering(
    rebuild_app: Callable[..., FastAPI],
) -> None:
    """The queue view equals `next_up` order narrowed to ready phases, then the remaining ready
    phases by priority — recomputed here independently from a fresh read of `backlog.yaml` via
    the same `queue_order()`/`readiness()` functions the governance `--ready` command uses
    (REQ-007 W11's own text: "matching the governance --ready rendering").
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_BACKLOG_QUEUE_PATH)
    assert response.status_code == 200
    body = response.json()

    catalog = yaml.safe_load(BACKLOG_PATH.read_text(encoding="utf-8"))
    items = {item["id"]: item for item in catalog["items"]}
    next_up = catalog.get("next_up", [])
    ordered = queue_order(items, next_up)
    expected_ready_ids = [item["id"] for item in ordered if readiness(item, items) == "ready"]

    assert expected_ready_ids, "fixture assumption: at least one phase is ready"
    assert [row["id"] for row in body] == expected_ready_ids

    next_up_ready = [key for key in next_up if key in expected_ready_ids]
    if next_up_ready:
        assert [row["id"] for row in body[: len(next_up_ready)]] == next_up_ready


def test_backlog_routes_reject_non_get(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    assert client.post(WORKBENCH_BACKLOG_PATH).status_code == 405
    assert client.post(WORKBENCH_BACKLOG_QUEUE_PATH).status_code == 405


# --- Reveal-in-explorer action (ADR-015 rule 5, REQ-007 W09) ------------------------------------


def test_reveal_rejects_dotdot_traversal(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.post(WORKBENCH_REVEAL_PATH, json={"path": "../../etc/passwd"})
    assert response.status_code == 400


def test_reveal_rejects_absolute_path(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.post(WORKBENCH_REVEAL_PATH, json={"path": "/etc/passwd"})
    assert response.status_code == 400


def test_reveal_rejects_symlink_escape(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)

    outside_target = tempfile.mkdtemp(prefix="workbench-reveal-escape-target-")
    link_path = REPO_ROOT / "test" / "_workbench_reveal_symlink_escape_tmp"
    try:
        link_path.symlink_to(outside_target, target_is_directory=True)
        response = client.post(
            WORKBENCH_REVEAL_PATH, json={"path": "test/_workbench_reveal_symlink_escape_tmp"}
        )
        assert response.status_code == 400
    finally:
        if link_path.is_symlink() or link_path.exists():
            link_path.unlink()
        os.rmdir(outside_target)


def test_reveal_rejects_nonexistent_path(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.post(WORKBENCH_REVEAL_PATH, json={"path": "does/not/exist.txt"})
    assert response.status_code == 404


def test_reveal_refuses_a_private_path_and_never_spawns(
    rebuild_app: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The same `_private/` exclusion the listing routes apply
    (`test_root_listing_contains_no_private_or_gitignored_entry`) must also stop `/reveal` from
    spawning an opener on a `_private/`-scoped path — the finding this guards against: `/reveal`
    checked only path escape, never the private/gitignored exclusion, so it could be pointed at
    `_private/` and would actually spawn.
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)

    captured: list[list[str]] = []
    live_workbench = _live_workbench_module()
    monkeypatch.setattr(live_workbench, "_launch_reveal_opener", captured.append)
    monkeypatch.setattr(live_workbench.platform, "system", lambda: "Linux")

    private_dir = REPO_ROOT / "_private"
    secret_dir = private_dir / "_workbench_reveal_private_tmp"
    secret_file = secret_dir / "secret.txt"
    private_dir_preexisted = private_dir.is_dir()
    if not private_dir_preexisted:
        private_dir.mkdir()
    secret_dir.mkdir()
    secret_file.write_text("not for reveal\n")
    try:
        response = client.post(
            WORKBENCH_REVEAL_PATH,
            json={"path": "_private/_workbench_reveal_private_tmp/secret.txt"},
        )
        assert response.status_code == 400
        assert captured == [], "no opener process may be spawned on a _private/ path"
    finally:
        secret_file.unlink()
        secret_dir.rmdir()
        if not private_dir_preexisted:
            private_dir.rmdir()


def test_reveal_refuses_a_gitignored_path_and_never_spawns(
    rebuild_app: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A path excluded by `git check-ignore` alone (no `_private/` involved) must also be
    refused — the guard is the same exclusion the listing routes apply, not a hand-kept
    `_private/`-only special case. `*.py[cod]` (`.gitignore`) is used as the fixture pattern.
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)

    captured: list[list[str]] = []
    live_workbench = _live_workbench_module()
    monkeypatch.setattr(live_workbench, "_launch_reveal_opener", captured.append)
    monkeypatch.setattr(live_workbench.platform, "system", lambda: "Linux")

    ignored_file = REPO_ROOT / "test" / "_workbench_reveal_gitignore_tmp.pyc"
    ignored_file.write_text("not for reveal\n")
    try:
        assert ignored_file in workbench_module._git_ignored_paths([ignored_file]), (
            "fixture assumption: *.py[cod] under test/ is git-ignored"
        )
        response = client.post(
            WORKBENCH_REVEAL_PATH, json={"path": "test/_workbench_reveal_gitignore_tmp.pyc"}
        )
        assert response.status_code == 400
        assert captured == [], "no opener process may be spawned on a gitignored path"
    finally:
        ignored_file.unlink()


def test_reveal_spawns_xdg_open_on_the_containing_directory_for_a_file(
    rebuild_app: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    """No real opener process starts: `_launch_reveal_opener` is monkeypatched to record the
    argument list instead of calling `subprocess.Popen`.
    """
    app = rebuild_app(flag="1")
    client = TestClient(app)

    captured: list[list[str]] = []
    live_workbench = _live_workbench_module()
    monkeypatch.setattr(live_workbench, "_launch_reveal_opener", captured.append)
    monkeypatch.setattr(live_workbench.platform, "system", lambda: "Linux")

    target_file = "README.md"
    assert (REPO_ROOT / target_file).is_file(), "fixture assumption: README.md exists"
    response = client.post(WORKBENCH_REVEAL_PATH, json={"path": target_file})
    assert response.status_code == 200
    assert captured == [["xdg-open", str(REPO_ROOT)]]


def test_reveal_spawns_xdg_open_on_a_directory_entry_itself(
    rebuild_app: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)

    captured: list[list[str]] = []
    live_workbench = _live_workbench_module()
    monkeypatch.setattr(live_workbench, "_launch_reveal_opener", captured.append)
    monkeypatch.setattr(live_workbench.platform, "system", lambda: "Linux")

    response = client.post(WORKBENCH_REVEAL_PATH, json={"path": "test"})
    assert response.status_code == 200
    assert captured == [["xdg-open", str(REPO_ROOT / "test")]]


def test_reveal_spawns_explorer_select_on_windows(
    rebuild_app: Callable[..., FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)

    captured: list[list[str]] = []
    live_workbench = _live_workbench_module()
    monkeypatch.setattr(live_workbench, "_launch_reveal_opener", captured.append)
    monkeypatch.setattr(live_workbench.platform, "system", lambda: "Windows")

    target_file = "README.md"
    response = client.post(WORKBENCH_REVEAL_PATH, json={"path": target_file})
    assert response.status_code == 200
    expected_path = REPO_ROOT / target_file
    assert captured == [["explorer.exe", f"/select,{expected_path}"]]


def test_reveal_never_spawns_a_real_process_when_unpatched_argv_is_checked_directly() -> None:
    """`_reveal_argv` is pure — it can be asserted on without touching `subprocess` at all."""
    resolved = REPO_ROOT / "README.md"
    assert workbench_module._reveal_argv(resolved) == ["xdg-open", str(REPO_ROOT)]


def test_reveal_route_rejects_non_post(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    client = TestClient(app)
    assert client.get(WORKBENCH_REVEAL_PATH).status_code == 405
    assert client.put(WORKBENCH_REVEAL_PATH).status_code == 405
    assert client.delete(WORKBENCH_REVEAL_PATH).status_code == 405
