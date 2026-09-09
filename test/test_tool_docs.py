"""Tests for the generated tool-reference blocks -- determinism and the hand-edit guard.

Mirrors the pattern already proven for docs/08-governance/GLOSSARY.md and catalog.md: the
generated block inside each paired OPS document is derived from a real source (the tool's own
AST), never hand-written, and a test fails the moment the committed block diverges from a fresh
render.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> Any:
    """Import a tools/ script by path -- tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generate_tool_docs = _load("generate_tool_docs")


def test_every_existing_tool_is_paired_with_a_document() -> None:
    tools = generate_tool_docs.discover_tools()
    assert tools, "expected at least one tool under tools/"
    unpaired = [t.name for t in tools if generate_tool_docs.find_doc(t) is None]
    assert unpaired == [], f"no OPS document found for: {unpaired}"


def test_every_paired_document_matches_regenerated_output() -> None:
    for tool in generate_tool_docs.discover_tools():
        doc = generate_tool_docs.find_doc(tool)
        assert doc is not None
        rendered = generate_tool_docs.render(tool)
        expected = generate_tool_docs.update_doc(doc, rendered)
        assert doc.read_text(encoding="utf-8") == expected, (
            f"{doc} has a stale generated block. Regenerate it with "
            "tools/generate_tool_docs.py; do not edit the generated block by hand."
        )


def test_regenerating_twice_produces_identical_output() -> None:
    for tool in generate_tool_docs.discover_tools():
        assert generate_tool_docs.render(tool) == generate_tool_docs.render(tool)


def test_a_hand_edit_is_detected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`--check` actually catches a tampered file, not just a string comparison in memory."""
    tool = ROOT / "tools" / "rebuild_db.py"
    real_doc = generate_tool_docs.find_doc(tool)
    assert real_doc is not None

    tampered_doc = tmp_path / real_doc.name
    tampered_doc.write_text(
        real_doc.read_text(encoding="utf-8").replace(
            generate_tool_docs.START, generate_tool_docs.START + "\n(tampered)"
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        generate_tool_docs, "find_doc", lambda t: tampered_doc if t == tool else None
    )
    monkeypatch.setattr(generate_tool_docs, "discover_tools", lambda: [tool])

    assert generate_tool_docs.main(["--check"]) == 1


def test_a_tool_with_no_document_is_reported_not_created(tmp_path: Path) -> None:
    """The generator never creates a document -- a tool with no OPS doc is left alone."""
    fake_tool = tmp_path / "not_yet_built.py"
    fake_tool.write_text('"""Not built yet."""\n', encoding="utf-8")
    assert generate_tool_docs.find_doc(fake_tool) is None


def test_arguments_and_exit_codes_are_read_from_source() -> None:
    module = generate_tool_docs.render(ROOT / "tools" / "load_context.py")
    assert "--query" in module
    assert "Keyword search across title and content" in module

    codes = generate_tool_docs.render(ROOT / "tools" / "generate_glossary.py")
    assert "Exit codes found in source: 0, 1." in codes


def test_update_doc_survives_marker_text_quoted_inside_the_rendered_block(tmp_path: Path) -> None:
    """A regenerated block that itself quotes the marker text must not truncate at the quote.

    This is the real shape of the bug: generate_tool_docs.py documents itself, and its own
    docstring quotes START/END as a usage example, so a naive first-START/first-END split would
    cut the block off at the quoted example instead of the true closing marker.
    """
    start, end = generate_tool_docs.START, generate_tool_docs.END
    doc = tmp_path / "OPS-999-fake.md"
    doc.write_text(f"# Fake\n\nNarrative.\n\n{start}\nold\n{end}\n", encoding="utf-8")

    rendered = f"{start}\nExample usage quotes {start} and {end} literally.\nTail content.\n{end}"
    new_text = generate_tool_docs.update_doc(doc, rendered)

    assert new_text == f"# Fake\n\nNarrative.\n\n{rendered}\n"
    assert new_text.count("Tail content.") == 1
    assert new_text.endswith(f"{end}\n")
