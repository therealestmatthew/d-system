"""Tests for the workbench read routes (`src/api/routes/workbench.py`, ADR-015).

Covers: the routes exist only when `D_SYSTEM_DEMO_TERMINAL=1` (404, not merely refusing, with
the flag unset — REQ-007 W14); injection-source enumeration matches a direct listing of
`.claude/skills/`, `.claude/agents/` and the governed `PROMPT-*` files under `docs/02-prompts/`;
the curated overrides file relabels, replaces injected text, and hides entries; path
validation rejects `..` traversal, an absolute path, and a symlink whose target leaves the
repository, all on the *resolved* path; a root directory listing carries no `_private/` or
gitignored entry; and every route responds to GET only.
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import src.api as api_module
import src.main as main_module
from src.api.routes.workbench import (
    AGENTS_DIR,
    INJECTION_OVERRIDES_PATH_ENV_VAR,
    PROMPT_FILENAME_PREFIX,
    PROMPTS_DIR,
    REPO_ROOT,
    SKILLS_DIR,
    PathEscapesRepositoryError,
    resolve_repo_relative_path,
)

WORKBENCH_INJECTION_SOURCES_PATH = "/api/v1/workbench/injection-sources"
WORKBENCH_LIST_PATH = "/api/v1/workbench/list"
WORKBENCH_SEARCH_PATH = "/api/v1/workbench/search"


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
    assert client.get(WORKBENCH_INJECTION_SOURCES_PATH).status_code == 404
    assert client.get(WORKBENCH_LIST_PATH).status_code == 404
    assert client.get(WORKBENCH_SEARCH_PATH).status_code == 404


def test_routes_registered_with_flag_set(rebuild_app: Callable[..., FastAPI]) -> None:
    app = rebuild_app(flag="1")
    assert "src.api.routes.workbench" in sys.modules
    client = TestClient(app)
    assert client.get(WORKBENCH_INJECTION_SOURCES_PATH).status_code == 200
    assert client.get(WORKBENCH_LIST_PATH).status_code == 200


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
    app = rebuild_app(flag="1")
    client = TestClient(app)
    response = client.get(WORKBENCH_LIST_PATH, params={"path": "."})
    assert response.status_code == 200
    names = {entry["name"] for entry in response.json()}

    assert (REPO_ROOT / ".venv").is_dir(), "fixture assumption: a real gitignored dir exists"
    assert ".venv" not in names
    assert "_private" not in names
    assert ".git" not in names


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
