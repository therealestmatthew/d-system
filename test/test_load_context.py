"""Tests for tools/load_context.py's query building and the --system filter.

`load()` reads from the built DuckDB, so the --system filter is proven against a real temporary
database seeded with the shipped memories table shape, rather than only unit-testing the SQL
string build_where() produces.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load_context = _load("load_context")


def test_build_where_filters_on_system() -> None:
    where, params = load_context.build_where(None, None, None, [], system="sys-brain")
    assert "list_contains(systems, ?)" in where
    assert params == ["sys-brain"]


def test_build_where_with_no_filters_is_empty() -> None:
    where, params = load_context.build_where(None, None, None, [])
    assert where == ""
    assert params == []


@pytest.fixture
def seeded_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A real DuckDB, built from the shipped DDL, seeded with two memories in different systems."""
    ddl = (ROOT / "sql" / "001_schema.sql").read_text(encoding="utf-8")
    clean = "\n".join(line for line in ddl.splitlines() if not line.strip().startswith("--"))
    db_path = tmp_path / "d_system.duckdb"
    conn = duckdb.connect(str(db_path))
    for statement in (s.strip() for s in clean.split(";") if s.strip()):
        conn.execute(statement)

    rows = [
        ("mem-a", "Memory A", "concept", ["python"], ["sys-brain"], "human", None,
         "2026-09-07", None, "high", [], "global", "Content A", "brain/concepts/a.md"),
        ("mem-b", "Memory B", "concept", ["python"], ["sys-backlog"], "human", None,
         "2026-09-07", None, "high", [], "global", "Content B", "brain/concepts/b.md"),
    ]
    for row in rows:
        conn.execute("INSERT INTO memories VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", list(row))
    conn.close()

    monkeypatch.setattr(load_context, "DB_PATH", db_path)
    return db_path


def test_system_filter_returns_only_matching_memories(seeded_db: Path) -> None:
    result = load_context.load(system="sys-brain")
    assert "Memory A" in result
    assert "Memory B" not in result


def test_system_filter_excludes_non_matching_system(seeded_db: Path) -> None:
    result = load_context.load(system="sys-backlog")
    assert "Memory B" in result
    assert "Memory A" not in result


def test_no_system_filter_returns_both(seeded_db: Path) -> None:
    result = load_context.load()
    assert "Memory A" in result
    assert "Memory B" in result
