"""Tests for the pre-rebuild source preflight.

Every case builds a temporary source tree rather than mutating the real one, because
the point of the preflight is what it does with a *broken* tree and the repository's
own files are not allowed to be broken.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

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
