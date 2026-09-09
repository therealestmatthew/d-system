"""Tests for the DuckDB projection of the expanded entity model (phase-cap-07).

Every case builds a temporary source tree and points `rebuild()` at it directly, rather
than mutating the real one, because the point of most of these tests is a *rebuild*, and
the repository's own `data/d_system.duckdb` is derived and gitignored — nothing here may
depend on running against it.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> Any:
    """Import a tools/ script by path — tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rebuild_db = _load("rebuild_db")

VALID_PROJECT = {
    "id": "proj1",
    "name": "Project One",
    "status": "active",
    "category": "system",
    "type": "system",
}


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A minimal but valid source tree, sharing the repository's real schemas."""
    shutil.copytree(ROOT / "schemas", tmp_path / "schemas")
    (tmp_path / "_data").mkdir()
    return tmp_path


def write(tree: Path, subdir: str, name: str, document: object) -> Path:
    directory = tree / "_data" / subdir
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def connect(tree: Path) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(tree / "data" / "d_system.duckdb"))


# --- the four new types round-trip (REQ-002 R20) -----------------------------------

INTERACTION = {
    "id": "i-1",
    "date": "2026-09-01",
    "type": "meeting",
    "summary": "Kickoff call",
    "project_id": "proj1",
}

DECISION = {
    "id": "d-1",
    "date": "2026-09-02",
    "decision": "Use DuckDB",
    "rationale": "Already embedded, no server to run",
    "project_id": "proj1",
}

WAITING_ON = {
    "id": "w-1",
    "description": "Signed SOW",
    "requested": "2026-09-03",
    "status": "open",
    "project_id": "proj1",
}

DEVELOPMENT_EVENT = {
    "id": "de-1",
    "date": "2026-09-04",
    "type": "certification",
    "title": "Platform exam",
    "project_id": "proj1",
}

NEW_TYPE_FIXTURES: dict[str, tuple[str, str, dict[str, Any]]] = {
    "interaction": ("interactions", "interactions", INTERACTION),
    "decision": ("decisions", "decisions", DECISION),
    "waiting-on": ("waiting-on", "waiting_on", WAITING_ON),
    "development-event": ("development-events", "development_events", DEVELOPMENT_EVENT),
}


@pytest.mark.parametrize("kind", NEW_TYPE_FIXTURES)
def test_new_type_fixture_survives_a_rebuild_unchanged(tree: Path, kind: str) -> None:
    directory, table, fixture = NEW_TYPE_FIXTURES[kind]
    write(tree, "projects", "proj1", VALID_PROJECT)
    write(tree, directory, fixture["id"], fixture)

    rebuild_db.rebuild(tree)

    conn = connect(tree)
    row = conn.execute(f"SELECT id FROM {table} WHERE id = ?", [fixture["id"]]).fetchone()
    assert row is not None
    count = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]  # type: ignore[index]
    assert count == 1


# --- tasks: both parents optional (REQ-002 R18) -------------------------------------

TASK_BASE = {"description": "Draft it", "status": "open", "created": "2026-09-01"}


@pytest.mark.parametrize(
    "parents",
    [
        {},
        {"commitment_id": "c-1"},
        {"project_id": "proj1"},
        {"commitment_id": "c-1", "project_id": "proj1"},
    ],
    ids=["neither", "commitment-only", "project-only", "both"],
)
def test_task_loads_with_any_combination_of_parents(
    tree: Path, parents: dict[str, str]
) -> None:
    write(tree, "projects", "proj1", VALID_PROJECT)
    write(tree, "tasks", "t-1", {"id": "t-1", **TASK_BASE, **parents})

    rebuild_db.rebuild(tree)

    conn = connect(tree)
    row = conn.execute(
        "SELECT commitment_id, project_id FROM tasks WHERE id = ?", ["t-1"]
    ).fetchone()
    assert row is not None
    assert row[0] == parents.get("commitment_id")
    assert row[1] == parents.get("project_id")


def test_a_commitment_alone_creates_no_tasks(tree: Path) -> None:
    """Tasks load only from _data/tasks/ now; a commitment carries none of its own."""
    write(
        tree,
        "commitments",
        "c-1",
        {
            "id": "c-1",
            "description": "Send the estimate",
            "status": "open",
            "priority": "high",
            "created": "2026-09-01",
        },
    )

    rebuild_db.rebuild(tree)

    conn = connect(tree)
    count = conn.execute("SELECT count(*) FROM tasks").fetchone()[0]  # type: ignore[index]
    assert count == 0


# --- last_touched is derived, never stored (REQ-002 R21, R24) -----------------------


def test_last_touched_is_absent_without_activity(tree: Path) -> None:
    write(tree, "projects", "proj1", {**VALID_PROJECT, "last_reviewed": "2026-08-01"})

    rebuild_db.rebuild(tree)

    conn = connect(tree)
    row = conn.execute(
        "SELECT last_touched FROM project_last_touched WHERE project_id = ?", ["proj1"]
    ).fetchone()
    assert row is None


def test_last_touched_advances_when_an_interaction_is_added(tree: Path) -> None:
    write(tree, "projects", "proj1", {**VALID_PROJECT, "last_reviewed": "2026-08-01"})
    write(tree, "commitments", "c-1", {
        "id": "c-1", "project_id": "proj1", "description": "Send it",
        "status": "open", "priority": "medium", "created": "2026-09-01",
    })
    rebuild_db.rebuild(tree)
    conn = connect(tree)
    before = conn.execute(
        "SELECT last_touched FROM project_last_touched WHERE project_id = ?", ["proj1"]
    ).fetchone()[0]  # type: ignore[index]
    assert str(before) == "2026-09-01"

    write(tree, "interactions", "i-1", {**INTERACTION, "date": "2026-09-15"})
    rebuild_db.rebuild(tree)
    conn = connect(tree)
    after = conn.execute(
        "SELECT last_touched FROM project_last_touched WHERE project_id = ?", ["proj1"]
    ).fetchone()[0]  # type: ignore[index]
    assert str(after) == "2026-09-15"


def test_last_reviewed_is_unchanged_by_activity(tree: Path) -> None:
    write(tree, "projects", "proj1", {**VALID_PROJECT, "last_reviewed": "2026-08-01"})
    write(tree, "interactions", "i-1", INTERACTION)

    rebuild_db.rebuild(tree)

    conn = connect(tree)
    last_reviewed = conn.execute(
        "SELECT last_reviewed FROM projects WHERE id = ?", ["proj1"]
    ).fetchone()[0]  # type: ignore[index]
    assert str(last_reviewed) == "2026-08-01"


def test_last_touched_not_present_in_any_source_file() -> None:
    """R21: no _data/ file may carry last_touched — it exists only in the projection."""
    for path in ROOT.glob("schemas/*.schema.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert "last_touched" not in schema.get("properties", {})


# --- the unfiled view (REQ-002 R19) -------------------------------------------------


def test_unfiled_view_returns_exactly_the_parentless_fixtures(tree: Path) -> None:
    write(tree, "projects", "proj1", VALID_PROJECT)
    write(tree, "commitments", "c-1", {
        "id": "c-1", "project_id": "proj1", "description": "Filed",
        "status": "open", "priority": "medium", "created": "2026-09-01",
    })
    write(tree, "commitments", "c-2", {
        "id": "c-2", "description": "Unfiled",
        "status": "open", "priority": "medium", "created": "2026-09-01",
    })
    write(tree, "tasks", "t-1", {
        "id": "t-1", "project_id": "proj1", **TASK_BASE,
    })
    write(tree, "tasks", "t-2", {"id": "t-2", **TASK_BASE})

    rebuild_db.rebuild(tree)

    conn = connect(tree)
    rows = conn.execute("SELECT record_type, id FROM unfiled ORDER BY id").fetchall()
    assert rows == [
        ("commitment", "c-2"),
        ("task", "t-2"),
    ]
