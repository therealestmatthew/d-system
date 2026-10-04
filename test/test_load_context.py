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


# --- Scope semantics, --all, limits, tag conjunction and ordering (phase-rel-08) ---------------
#
# GOV-003 "Global memory retrieval": a project query includes every scope: global memory —
# including the ones carrying project: d-system, which is how the shipped brain/ records
# repository-wide memories — alongside that project's own entries, and nothing else.

# (id, tags, project_id, created, confidence, scope)
CORPUS: list[tuple[str, list[str], str | None, str, str, str]] = [
    ("g-null", ["python"], None, "2026-09-01", "high", "global"),
    ("g-repo", ["python", "duckdb"], "d-system", "2026-09-02", "high", "global"),
    ("g-repo-2", ["duckdb"], "d-system", "2026-09-03", "medium", "global"),
    ("p-alpha", ["python", "duckdb"], "alpha", "2026-09-04", "high", "project"),
    ("s-alpha", ["python"], "alpha", "2026-09-05", "low", "session"),
    ("p-beta", ["python", "duckdb"], "beta", "2026-09-06", "high", "project"),
    ("s-beta", ["python"], "beta", "2026-09-07", "medium", "session"),
    ("p-repo", ["python"], "d-system", "2026-09-08", "medium", "project"),
    ("s-null", ["python", "duckdb"], None, "2026-09-09", "high", "session"),
    ("g-tie-b", ["duckdb"], None, "2026-09-10", "medium", "global"),
    ("g-tie-a", ["duckdb"], None, "2026-09-10", "medium", "global"),
    ("g-low", ["python"], None, "2026-09-11", "low", "global"),
    ("g-old", ["python", "duckdb"], None, "2026-08-01", "high", "global"),
]

# The ordering load() promises: confidence high > medium > low, newest first, then id.
ORDER = [
    "s-null", "p-beta", "p-alpha", "g-repo", "g-null", "g-old",
    "g-tie-a", "g-tie-b", "p-repo", "s-beta", "g-repo-2",
    "g-low", "s-alpha",
]


@pytest.fixture
def corpus_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A real DuckDB from the shipped DDL, seeded with more than ten memories across scopes."""
    ddl = (ROOT / "sql" / "001_schema.sql").read_text(encoding="utf-8")
    clean = "\n".join(line for line in ddl.splitlines() if not line.strip().startswith("--"))
    db_path = tmp_path / "d_system.duckdb"
    conn = duckdb.connect(str(db_path))
    for statement in (s.strip() for s in clean.split(";") if s.strip()):
        conn.execute(statement)
    for id_, tags, project_id, created, confidence, scope in CORPUS:
        conn.execute(
            "INSERT INTO memories VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [id_, f"Title {id_}", "concept", tags, [], "human", project_id, created, None,
             confidence, [], scope, f"Content {id_}", f"brain/concepts/{id_}.md"],
        )
    conn.close()
    monkeypatch.setattr(load_context, "DB_PATH", db_path)
    return db_path


def _ids(result: str) -> list[str]:
    """The memory ids load() rendered, in output order."""
    return [line.split("id:", 1)[1].split(" |", 1)[0]
            for line in result.splitlines() if line.startswith("*id:")]


def test_corpus_is_larger_than_the_default_limit() -> None:
    assert len(CORPUS) > load_context.DEFAULT_LIMIT


def test_project_query_includes_globals_and_own_entries_only(corpus_db: Path) -> None:
    ids = set(_ids(load_context.load(project="alpha", all_memories=False, limit=100)))
    assert ids == {"g-null", "g-repo", "g-repo-2", "g-tie-a", "g-tie-b", "g-low", "g-old",
                   "p-alpha", "s-alpha"}


def test_project_query_excludes_unrelated_project_and_session_entries(corpus_db: Path) -> None:
    ids = set(_ids(load_context.load(project="alpha", limit=100)))
    assert not ids & {"p-beta", "s-beta", "p-repo", "s-null"}


def test_repository_scoped_globals_reach_every_project(corpus_db: Path) -> None:
    for project in ("alpha", "beta"):
        ids = set(_ids(load_context.load(project=project, limit=100)))
        assert {"g-repo", "g-repo-2"} <= ids


def test_d_system_project_query_adds_its_project_scoped_entry(corpus_db: Path) -> None:
    ids = set(_ids(load_context.load(project="d-system", limit=100)))
    assert "p-repo" in ids
    assert not ids & {"p-alpha", "p-beta", "s-null"}


def test_default_limit_is_ten(corpus_db: Path) -> None:
    assert _ids(load_context.load()) == ORDER[:10]


def test_all_is_unbounded_without_a_limit(corpus_db: Path) -> None:
    assert _ids(load_context.load(all_memories=True)) == ORDER


def test_all_honours_an_explicit_limit(corpus_db: Path) -> None:
    assert _ids(load_context.load(all_memories=True, limit=5)) == ORDER[:5]


def test_explicit_limit_above_default_without_all(corpus_db: Path) -> None:
    assert _ids(load_context.load(limit=12)) == ORDER[:12]


def test_all_ignores_other_filters(corpus_db: Path) -> None:
    assert _ids(load_context.load(project="alpha", tags=["duckdb"], all_memories=True)) == ORDER


def test_tags_are_conjunctive(corpus_db: Path) -> None:
    ids = _ids(load_context.load(tags=["python", "duckdb"], limit=100))
    assert ids == [i for i in ORDER if i in {"g-repo", "p-alpha", "p-beta", "s-null", "g-old"}]


def test_tags_and_project_combine(corpus_db: Path) -> None:
    ids = _ids(load_context.load(project="alpha", tags=["python", "duckdb"], limit=100))
    assert ids == ["p-alpha", "g-repo", "g-old"]


def test_ordering_breaks_ties_by_id_and_is_repeatable(corpus_db: Path) -> None:
    first = _ids(load_context.load(all_memories=True))
    assert first.index("g-tie-a") < first.index("g-tie-b")
    assert _ids(load_context.load(all_memories=True)) == first


def _run_cli(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
             *argv: str) -> list[str]:
    monkeypatch.setattr(sys, "argv", ["load_context.py", *argv])
    load_context.main()
    return _ids(capsys.readouterr().out)


def test_cli_all_is_unbounded(corpus_db: Path, monkeypatch: pytest.MonkeyPatch,
                              capsys: pytest.CaptureFixture[str]) -> None:
    assert _run_cli(monkeypatch, capsys, "--all") == ORDER


def test_cli_all_with_limit(corpus_db: Path, monkeypatch: pytest.MonkeyPatch,
                            capsys: pytest.CaptureFixture[str]) -> None:
    assert _run_cli(monkeypatch, capsys, "--all", "--limit", "3") == ORDER[:3]


def test_cli_default_limit(corpus_db: Path, monkeypatch: pytest.MonkeyPatch,
                           capsys: pytest.CaptureFixture[str]) -> None:
    assert _run_cli(monkeypatch, capsys) == ORDER[:10]


def test_cli_project_and_tags(corpus_db: Path, monkeypatch: pytest.MonkeyPatch,
                              capsys: pytest.CaptureFixture[str]) -> None:
    ids = _run_cli(monkeypatch, capsys, "--project", "alpha", "--tags", "python,duckdb", "-n", "50")
    assert ids == ["p-alpha", "g-repo", "g-old"]


# --- --limit must be a positive integer (idea 000565) ------------------------------------------


@pytest.mark.parametrize("argv", [["--limit", "0"], ["--limit", "-1"], ["-n", "-5"],
                                  ["--limit=-1"], ["--all", "--limit", "0"], ["--limit", "abc"]])
def test_cli_rejects_a_non_positive_or_non_integer_limit(
    corpus_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
    argv: list[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["load_context.py", *argv])
    with pytest.raises(SystemExit) as exit_info:
        load_context.main()
    assert exit_info.value.code == 2
    captured = capsys.readouterr()
    assert "argument --limit/-n:" in captured.err
    assert "Traceback" not in captured.err
    assert captured.out == ""


def test_positive_int_messages() -> None:
    import argparse

    assert load_context.positive_int("1") == 1
    with pytest.raises(argparse.ArgumentTypeError, match="must be at least 1, got 0"):
        load_context.positive_int("0")
    with pytest.raises(argparse.ArgumentTypeError, match="invalid int value: 'x'"):
        load_context.positive_int("x")


def test_cli_accepts_a_limit_of_one(corpus_db: Path, monkeypatch: pytest.MonkeyPatch,
                                    capsys: pytest.CaptureFixture[str]) -> None:
    assert _run_cli(monkeypatch, capsys, "--all", "--limit", "1") == ORDER[:1]
