"""Tests for the pre-rebuild source preflight.

Every case builds a temporary source tree rather than mutating the real one, because
the point of the preflight is what it does with a *broken* tree and the repository's
own files are not allowed to be broken.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import duckdb
import pytest

from src.db.source_validation import (
    SourceError,
    format_errors,
    split_front_matter,
    validate_sources,
)

ROOT = Path(__file__).resolve().parents[1]

VALID_PROJECT = {
    "id": "example",
    "name": "Example",
    "status": "active",
    "category": "system",
    "type": "system",
    "last_reviewed": "2026-09-06",
    "review_cadence": "weekly",
}

VALID_MEMORY = """---
id: mem-example
title: Example
type: concept
created: 2026-09-05
updated: 2026-09-06
---

Body text.
"""


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A minimal but valid source tree, sharing the repository's real schemas."""
    shutil.copytree(ROOT / "schemas", tmp_path / "schemas")
    (tmp_path / "_data/projects").mkdir(parents=True)
    (tmp_path / "brain/concepts").mkdir(parents=True)
    (tmp_path / "_data/tags.json").write_text("[]", encoding="utf-8")
    write_project(tmp_path, "example", VALID_PROJECT)
    (tmp_path / "brain/concepts/example.md").write_text(VALID_MEMORY, encoding="utf-8")
    return tmp_path


def write_project(tree: Path, name: str, document: object) -> Path:
    path = tree / "_data/projects" / f"{name}.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def fields(errors: list[SourceError], path_fragment: str) -> set[str]:
    return {e.field for e in errors if path_fragment in e.path}


# --- the happy path ---------------------------------------------------------------


def test_valid_tree_passes(tree: Path) -> None:
    assert validate_sources(tree) == []


def test_the_real_repository_passes() -> None:
    """The guard that matters: this is the tree the rebuild actually runs against."""
    assert validate_sources(ROOT) == []


def test_validation_creates_no_database_directory(tree: Path) -> None:
    """Acceptance: valid files pass without creating data/."""
    validate_sources(tree)
    assert not (tree / "data").exists()


def test_failed_validation_creates_no_database_directory(tree: Path) -> None:
    write_project(tree, "broken", {"id": "broken"})
    assert validate_sources(tree)
    assert not (tree / "data").exists()


def test_missing_optional_directories_are_not_errors(tree: Path) -> None:
    """_data/tasks/ and friends do not exist until capture creates them."""
    assert not (tree / "_data/tasks").exists()
    assert validate_sources(tree) == []


# --- malformed entity JSON --------------------------------------------------------


def test_invalid_json_is_reported_with_the_file(tree: Path) -> None:
    (tree / "_data/projects/broken.json").write_text("{not json", encoding="utf-8")
    errors = validate_sources(tree)
    assert [e.path for e in errors] == ["_data/projects/broken.json"]
    assert "invalid JSON" in errors[0].message


def test_missing_required_field_names_the_field(tree: Path) -> None:
    document = {k: v for k, v in VALID_PROJECT.items() if k != "status"}
    write_project(tree, "example", document)
    errors = validate_sources(tree)
    assert "status" in " ".join(e.message for e in errors)


def test_unknown_field_names_the_field(tree: Path) -> None:
    write_project(tree, "example", {**VALID_PROJECT, "cadence": "weekly"})
    assert "cadence" in fields(validate_sources(tree), "example.json")


def test_retired_cadence_value_is_rejected(tree: Path) -> None:
    write_project(tree, "example", {**VALID_PROJECT, "review_cadence": "ongoing"})
    assert "review_cadence" in fields(validate_sources(tree), "example.json")


@pytest.mark.parametrize(
    "bad_date",
    ["2026-13-45", "06/09/2026", "yesterday", "", "2026-02-29"],
    ids=["out-of-range", "wrong-order", "prose", "empty", "not-a-leap-year"],
)
def test_invalid_dates_are_rejected(tree: Path, bad_date: str) -> None:
    """Acceptance: a bad date fails here, not as a cast error mid-insert.

    2026-02-29 is the case a regex would wave through: well formed, and not a day.
    """
    write_project(tree, "example", {**VALID_PROJECT, "last_reviewed": bad_date})
    assert "last_reviewed" in fields(validate_sources(tree), "example.json")


def test_a_valid_leap_day_is_accepted(tree: Path) -> None:
    write_project(tree, "example", {**VALID_PROJECT, "last_reviewed": "2028-02-29"})
    assert validate_sources(tree) == []


def test_every_bad_file_is_reported_not_just_the_first(tree: Path) -> None:
    write_project(tree, "one", {"id": "one"})
    write_project(tree, "two", {"id": "two"})
    reported = {e.path for e in validate_sources(tree)}
    assert "_data/projects/one.json" in reported
    assert "_data/projects/two.json" in reported


def test_tags_file_entries_are_validated(tree: Path) -> None:
    (tree / "_data/tags.json").write_text(
        json.dumps([{"id": "ok", "label": "OK", "category": "invented"}]),
        encoding="utf-8",
    )
    errors = validate_sources(tree)
    assert errors and "tags.json[0]" in errors[0].path
    assert errors[0].field == "category"


def test_tags_file_must_be_a_list(tree: Path) -> None:
    (tree / "_data/tags.json").write_text("{}", encoding="utf-8")
    errors = validate_sources(tree)
    assert errors and "expected a list" in errors[0].message


# --- malformed memory front matter ------------------------------------------------


def write_memory(tree: Path, name: str, text: str) -> None:
    (tree / "brain/concepts" / f"{name}.md").write_text(text, encoding="utf-8")


def test_memory_without_front_matter_is_reported(tree: Path) -> None:
    """The failure this phase exists for: the loader used to skip these in silence."""
    write_memory(tree, "bare", "Just a note with no front matter.\n")
    errors = validate_sources(tree)
    assert [e.path for e in errors] == ["brain/concepts/bare.md"]
    assert errors[0].message == "missing YAML front matter"


def test_memory_with_unterminated_front_matter_is_reported(tree: Path) -> None:
    write_memory(tree, "unterminated", "---\nid: mem-x\ntitle: X\n")
    errors = validate_sources(tree)
    assert errors[0].message == "missing YAML front matter"


def test_memory_with_unreadable_yaml_is_reported(tree: Path) -> None:
    write_memory(tree, "broken", "---\nid: [unclosed\n---\n\nBody.\n")
    errors = validate_sources(tree)
    assert "unreadable front matter" in errors[0].message


def test_memory_with_empty_front_matter_is_reported(tree: Path) -> None:
    write_memory(tree, "empty", "---\n---\n\nBody.\n")
    errors = validate_sources(tree)
    assert errors[0].message == "empty front matter"


def test_memory_front_matter_that_is_not_a_mapping_is_reported(tree: Path) -> None:
    write_memory(tree, "list", "---\n- one\n- two\n---\n\nBody.\n")
    errors = validate_sources(tree)
    assert errors[0].message == "front matter is not a mapping"


@pytest.mark.parametrize("field", ["id", "title", "type", "created"])
def test_memory_missing_required_metadata_names_the_field(tree: Path, field: str) -> None:
    lines = [line for line in VALID_MEMORY.splitlines() if not line.startswith(f"{field}:")]
    write_memory(tree, "example", "\n".join(lines) + "\n")
    errors = validate_sources(tree)
    assert field in " ".join(e.message for e in errors)


def test_memory_with_an_invalid_type_names_the_field(tree: Path) -> None:
    write_memory(tree, "example", VALID_MEMORY.replace("type: concept", "type: invented"))
    assert "type" in fields(validate_sources(tree), "example.md")


def test_memory_with_an_invalid_date_is_rejected(tree: Path) -> None:
    text = VALID_MEMORY.replace("created: 2026-09-05", "created: '2026-13-45'")
    write_memory(tree, "example", text)
    assert "created" in fields(validate_sources(tree), "example.md")


def test_unquoted_yaml_dates_are_accepted(tree: Path) -> None:
    """PyYAML resolves these to date objects; the schema declares strings."""
    assert "created: 2026-09-05" in VALID_MEMORY
    assert validate_sources(tree) == []


def test_quoted_yaml_dates_are_also_accepted(tree: Path) -> None:
    text = VALID_MEMORY.replace("created: 2026-09-05", "created: '2026-09-05'")
    write_memory(tree, "example", text)
    assert validate_sources(tree) == []


def test_brain_index_is_not_validated(tree: Path) -> None:
    """index.md is a hand-written table of contents, not a memory."""
    (tree / "brain/index.md").write_text("# Index\n", encoding="utf-8")
    assert validate_sources(tree) == []


# --- shared helpers ---------------------------------------------------------------


def test_split_front_matter_returns_none_without_a_leading_marker() -> None:
    assert split_front_matter("no front matter") is None


def test_split_front_matter_separates_metadata_from_body() -> None:
    split = split_front_matter("---\nid: mem-x\n---\n\nBody.\n")
    assert split is not None
    assert "id: mem-x" in split[0]
    assert split[1].strip() == "Body."


def test_error_renders_file_and_field() -> None:
    rendered = str(SourceError("_data/projects/x.json", "status", "is required"))
    assert rendered == "_data/projects/x.json: status: is required"


def test_error_without_a_field_renders_the_file_alone() -> None:
    assert str(SourceError("x.json", "", "invalid JSON")) == "x.json: invalid JSON"


def test_format_errors_indents_one_per_line() -> None:
    errors = [SourceError("a.json", "", "one"), SourceError("b.json", "", "two")]
    assert format_errors(errors) == "  a.json: one\n  b.json: two"


# --- references and global identities (phase-rel-03) ------------------------------


def write_entity(tree: Path, directory: str, name: str, document: object) -> Path:
    path = tree / "_data" / directory / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def write_tags(tree: Path, *ids: str) -> None:
    tags = [{"id": tag, "label": tag, "category": "tech"} for tag in ids]
    (tree / "_data/tags.json").write_text(json.dumps(tags), encoding="utf-8")


def task(identifier: str, **extra: object) -> dict[str, object]:
    return {
        "id": identifier,
        "description": "Do it",
        "status": "open",
        "created": "2026-10-05",
        **extra,
    }


def commitment(identifier: str, **extra: object) -> dict[str, object]:
    return {
        "id": identifier,
        "description": "Promise",
        "status": "open",
        "priority": "medium",
        "created": "2026-10-05",
        **extra,
    }


def by_field(errors: list[SourceError]) -> dict[tuple[str, str], str]:
    return {(e.path, e.field): e.message for e in errors}


def test_fully_cross_referenced_tree_passes(tree: Path) -> None:
    write_tags(tree, "python", "react")
    (tree / "_data/tags.json").write_text(
        json.dumps(
            [
                {"id": "python", "label": "P", "category": "tech", "related": ["react"]},
                {"id": "react", "label": "R", "category": "tech"},
            ]
        ),
        encoding="utf-8",
    )
    write_project(
        tree, "example", {**VALID_PROJECT, "tags": ["python"], "stakeholders": ["ana"]}
    )
    write_entity(tree, "people", "ana", {"id": "ana", "name": "Ana", "projects": ["example"]})
    write_entity(tree, "commitments", "c-1", commitment("c-1", project_id="example"))
    write_entity(
        tree, "tasks", "t-1", task("t-1", commitment_id="c-1", project_id="example", tags=["react"])
    )
    write_memory(
        tree,
        "second",
        "---\nid: mem-second\ntitle: S\ntype: concept\ncreated: 2026-10-05\n"
        "project: example\ntags: [python]\nrelated: [mem-example]\n---\n",
    )
    assert validate_sources(tree) == []


@pytest.mark.parametrize(
    ("directory", "document", "field", "target"),
    [
        ("projects", {**VALID_PROJECT, "id": "p2", "tags": ["nope"]}, "tags[0]", "tag"),
        ("projects", {**VALID_PROJECT, "id": "p2", "stakeholders": ["nobody"]},
         "stakeholders[0]", "person"),
        ("people", {"id": "ana", "name": "Ana", "projects": ["missing"]}, "projects[0]",
         "project"),
        ("commitments", commitment("c-1", project_id="missing"), "project_id", "project"),
        ("tasks", task("t-1", commitment_id="c-9"), "commitment_id", "commitment"),
        ("tasks", task("t-1", project_id="missing"), "project_id", "project"),
        ("tasks", task("t-1", tags=["nope"]), "tags[0]", "tag"),
        ("interactions",
         {"id": "i-1", "date": "2026-10-05", "type": "call", "summary": "s",
          "participants": ["nobody"]}, "participants[0]", "person"),
        ("decisions",
         {"id": "d-1", "date": "2026-10-05", "decision": "d", "rationale": "r",
          "decided_by": ["nobody"]}, "decided_by[0]", "person"),
        ("decisions",
         {"id": "d-1", "date": "2026-10-05", "decision": "d", "rationale": "r",
          "interaction_id": "i-9"}, "interaction_id", "interaction"),
        ("decisions",
         {"id": "d-1", "date": "2026-10-05", "decision": "d", "rationale": "r",
          "supersedes": "d-9"}, "supersedes", "decision"),
        ("waiting-on",
         {"id": "w-1", "description": "x", "requested": "2026-10-05", "status": "open",
          "project_id": "missing"}, "project_id", "project"),
        ("development-events",
         {"id": "de-1", "date": "2026-10-05", "type": "course", "title": "t",
          "tags": ["nope"]}, "tags[0]", "tag"),
    ],
)
def test_unknown_entity_reference_names_record_field_and_id(
    tree: Path, directory: str, document: dict[str, object], field: str, target: str
) -> None:
    path = write_entity(tree, directory, str(document["id"]), document)
    errors = validate_sources(tree)
    name = str(path.relative_to(tree))
    assert (name, field) in by_field(errors), format_errors(errors)
    assert by_field(errors)[(name, field)].startswith(f"unknown {target} '")


def test_unknown_tag_relation_is_reported(tree: Path) -> None:
    (tree / "_data/tags.json").write_text(
        json.dumps([{"id": "python", "label": "P", "category": "tech", "related": ["gone"]}]),
        encoding="utf-8",
    )
    assert by_field(validate_sources(tree)) == {
        ("_data/tags.json[0]", "related[0]"): "unknown tag 'gone'"
    }


@pytest.mark.parametrize(
    ("line", "field", "message"),
    [
        ("project: elsewhere", "project", "unknown project 'elsewhere'"),
        ("tags: [nope]", "tags[0]", "unknown tag 'nope'"),
        ("related: [mem-gone]", "related[0]", "unknown memory 'mem-gone'"),
    ],
)
def test_unknown_memory_reference_is_reported(
    tree: Path, line: str, field: str, message: str
) -> None:
    write_memory(tree, "example", VALID_MEMORY.replace("type: concept", f"type: concept\n{line}"))
    assert by_field(validate_sources(tree)) == {("brain/concepts/example.md", field): message}


@pytest.mark.parametrize("scope", ["global", "project"])
def test_repository_scope_memory_is_valid_without_a_project_record(
    tree: Path, scope: str
) -> None:
    """`project: d-system` is the repository's own memory scope (ADR-001), not a
    portfolio project, so no _data/projects/ record backs it."""
    assert not (tree / "_data/projects/d-system.json").exists()
    text = VALID_MEMORY.replace(
        "type: concept", f"type: concept\nproject: d-system\nscope: {scope}"
    )
    write_memory(tree, "example", text)
    assert validate_sources(tree) == []


def test_repository_scope_is_not_a_project_for_entities(tree: Path) -> None:
    """The exemption is for memories only: a task filed under d-system names a project
    record that does not exist."""
    write_entity(tree, "tasks", "t-1", task("t-1", project_id="d-system"))
    assert by_field(validate_sources(tree)) == {
        ("_data/tasks/t-1.json", "project_id"): "unknown project 'd-system'"
    }


def test_null_references_are_not_errors(tree: Path) -> None:
    write_entity(tree, "tasks", "t-1", task("t-1", commitment_id=None, project_id=None))
    text = VALID_MEMORY.replace("type: concept", "type: concept\nproject: null")
    write_memory(tree, "example", text)
    assert validate_sources(tree) == []


def test_unconfirmed_names_in_promised_to_are_not_references(tree: Path) -> None:
    """ADR-008: promised_to holds the name as written until an identity is confirmed."""
    write_entity(tree, "commitments", "c-1", commitment("c-1", promised_to="Someone Unresolved"))
    assert validate_sources(tree) == []


def test_duplicate_task_across_commitments_names_both_files(tree: Path) -> None:
    """Acceptance: duplicate tasks across commitments identify both source records."""
    write_entity(tree, "commitments", "c-1", commitment("c-1"))
    write_entity(tree, "commitments", "c-2", commitment("c-2"))
    write_entity(tree, "tasks", "a", task("t-1", commitment_id="c-1"))
    write_entity(tree, "tasks", "b", task("t-1", commitment_id="c-2"))
    errors = validate_sources(tree)
    assert by_field(errors) == {
        ("_data/tasks/b.json", "id"): "duplicate task ID 't-1', also defined in _data/tasks/a.json"
    }


@pytest.mark.parametrize(
    ("directory", "make"),
    [
        ("projects", lambda i: {**VALID_PROJECT, "id": i}),
        ("people", lambda i: {"id": i, "name": "N"}),
        ("commitments", lambda i: commitment(i)),
    ],
)
def test_duplicate_entity_ids_name_both_files(
    tree: Path, directory: str, make: object
) -> None:
    assert callable(make)
    identifier = "c-7" if directory == "commitments" else "same"
    write_entity(tree, directory, "first", make(identifier))
    write_entity(tree, directory, "second", make(identifier))
    errors = validate_sources(tree)
    message = by_field(errors)[(f"_data/{directory}/second.json", "id")]
    assert f"'{identifier}'" in message and f"_data/{directory}/first.json" in message


def test_duplicate_tag_ids_name_both_entries(tree: Path) -> None:
    write_tags(tree, "python", "python")
    assert by_field(validate_sources(tree)) == {
        ("_data/tags.json[1]", "id"):
            "duplicate tag ID 'python', also defined in _data/tags.json[0]"
    }


def test_duplicate_memory_ids_name_both_files(tree: Path) -> None:
    write_memory(tree, "copy", VALID_MEMORY)
    assert by_field(validate_sources(tree)) == {
        ("brain/concepts/example.md", "id"):
            "duplicate memory ID 'mem-example', also defined in brain/concepts/copy.md"
    }


def test_same_id_in_different_kinds_is_not_a_duplicate(tree: Path) -> None:
    write_tags(tree, "example")
    write_entity(tree, "people", "example", {"id": "example", "name": "N"})
    assert validate_sources(tree) == []


def test_schema_invalid_record_is_not_reported_again_as_a_reference(tree: Path) -> None:
    """A malformed file is reported once by its schema, not as a cascade of references."""
    write_entity(tree, "tasks", "t-1", {"id": "t-1", "project_id": "missing"})
    errors = validate_sources(tree)
    assert errors and all("unknown" not in e.message for e in errors)


def test_reference_failure_leaves_an_existing_projection_unchanged(tree: Path) -> None:
    """Acceptance: validation failure leaves an existing temporary projection unchanged."""
    spec = importlib.util.spec_from_file_location(
        "rebuild_db", ROOT / "tools" / "rebuild_db.py"
    )
    assert spec and spec.loader
    rebuild_db = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("rebuild_db", rebuild_db)
    spec.loader.exec_module(rebuild_db)
    shutil.copytree(ROOT / "sql", tree / "sql")

    rebuild_db.rebuild(tree)
    db_path = tree / "data" / "d_system.duckdb"
    before = db_path.read_bytes()

    write_entity(tree, "tasks", "t-1", task("t-1", project_id="missing"))
    with pytest.raises(SystemExit):
        rebuild_db.rebuild(tree)

    assert db_path.read_bytes() == before
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        assert conn.execute("SELECT id FROM projects").fetchall() == [("example",)]
        assert conn.execute("SELECT count(*) FROM tasks").fetchone() == (0,)
    finally:
        conn.close()
