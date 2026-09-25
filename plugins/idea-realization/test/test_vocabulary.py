"""The vocabulary document's tables list exactly the values the idea schema accepts.

The document is written by hand; this test is what stops it drifting. Each table's first column
holds values in backticks, and each table is compared as a set with the schema's ``enum`` (or,
for transitions and inverses, with what the fold reads from the schema).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from conftest import PLUGIN_ROOT
from ideas import INVERSE_LINK_TYPE, SCHEMA, legal_transitions

VOCABULARY = PLUGIN_ROOT / "docs" / "vocabulary.md"
CELL = re.compile(r"`([^`]+)`")

#: Heading of each table → where its values live in the schema's ``properties`` (or definitions).
ENUM_TABLES = {
    "Statuses": ("definitions", "status"),
    "Event kinds": ("properties", "event"),
    "Annotation kinds": ("properties", "kind"),
    "Link types": ("properties", "type"),
    "Record kinds": ("properties", "record_kind"),
    "Ontological axis": ("properties", "ontological"),
    "Epistemic axis": ("properties", "epistemic"),
    "Lifecycle axis": ("properties", "lifecycle"),
    "Lifecycle remedy": ("properties", "lifecycle_remedy"),
    "Temporal axis": ("properties", "temporal"),
    "Tie-break rules": ("properties", "tie_breaks"),
}


def tables(text: str) -> dict[str, list[list[str]]]:
    """Each heading's first table, as rows of cells, header and separator dropped."""
    found: dict[str, list[list[str]]] = {}
    heading = None
    for line in text.splitlines():
        match = re.match(r"^#{2,3} (.+)$", line)
        if match:
            heading = match.group(1).strip()
            continue
        if heading and line.startswith("|") and not re.match(r"^\|[-| ]+\|$", line):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            found.setdefault(heading, []).append(cells)
    return {name: rows[1:] for name, rows in found.items()}


def first(cell: str) -> str | None:
    match = CELL.search(cell)
    return match.group(1) if match else None


def schema_enum(schema: dict[str, Any], section: str, name: str) -> set[str]:
    node = schema[section][name]
    if "items" in node:
        node = node["items"]
    return set(node["enum"])


def mismatches(text: str, schema: dict[str, Any]) -> list[str]:
    """Every difference between the document's tables and the schema, one line each."""
    found = tables(text)
    problems = []
    for heading, (section, name) in ENUM_TABLES.items():
        rows = found.get(heading)
        if rows is None:
            problems.append(f"no table under {heading!r}")
            continue
        documented = {value for row in rows if (value := first(row[0]))}
        expected = schema_enum(schema, section, name)
        for value in sorted(expected - documented):
            problems.append(f"{heading}: {value} is in the schema but not the document")
        for value in sorted(documented - expected):
            problems.append(f"{heading}: {value} is in the document but not the schema")

    documented_moves = {(first(row[0]), first(row[1])) for row in found.get("Transitions", [])}
    for source, target in sorted(legal_transitions() - documented_moves):
        problems.append(f"Transitions: {source} -> {target} is legal but not documented")
    for source, target in sorted(documented_moves - legal_transitions()):
        problems.append(f"Transitions: {source} -> {target} is documented but not legal")

    for row in found.get("Link types", []):
        link_type, inverse = first(row[0]), first(row[1])
        expected_inverse = INVERSE_LINK_TYPE.get(link_type or "", link_type)
        if inverse != expected_inverse:
            problems.append(f"Link types: {link_type} inverse is {expected_inverse}, not {inverse}")
    return problems


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return loaded


def test_the_vocabulary_matches_the_schema(schema: dict[str, Any]) -> None:
    assert mismatches(VOCABULARY.read_text(encoding="utf-8"), schema) == []


def test_a_document_missing_one_status_fails(schema: dict[str, Any], tmp_path: Path) -> None:
    text = VOCABULARY.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if line.startswith("| `absorbed` |"))
    fixture = tmp_path / "vocabulary.md"
    fixture.write_text(text.replace(row + "\n", ""), encoding="utf-8")

    problems = mismatches(fixture.read_text(encoding="utf-8"), schema)

    assert problems == ["Statuses: absorbed is in the schema but not the document"]


def test_a_document_missing_one_transition_fails(schema: dict[str, Any]) -> None:
    text = VOCABULARY.read_text(encoding="utf-8")
    row = "| `promoted` | `delivered` | `closes_with` |\n"
    assert row in text

    problems = mismatches(text.replace(row, ""), schema)

    assert problems == ["Transitions: promoted -> delivered is legal but not documented"]


def test_a_wrong_inverse_fails(schema: dict[str, Any]) -> None:
    text = VOCABULARY.read_text(encoding="utf-8").replace("`has_component`", "`contains`")

    assert mismatches(text, schema) == [
        "Link types: component_of inverse is has_component, not contains"
    ]
