"""Tests for the generated glossary — determinism and the hand-edit guard.

Mirrors the pattern already proven for docs/00-working/ideas.md and docs/08-governance/catalog.md:
the file is generated from a real source (here, brain/'s `concept` memories), never hand-written,
and a test fails the moment the committed output diverges from a fresh render.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = ROOT / "docs" / "08-governance" / "GLOSSARY.md"


def _load(name: str) -> Any:
    """Import a tools/ script by path — tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generate_glossary = _load("generate_glossary")


def test_the_committed_glossary_matches_regenerated_output() -> None:
    entries = generate_glossary.load_concepts()
    rendered = generate_glossary.render(entries)
    assert GLOSSARY.read_text(encoding="utf-8") == rendered, (
        "docs/08-governance/GLOSSARY.md is generated. Regenerate it with "
        "tools/generate_glossary.py; do not edit it by hand."
    )


def test_regenerating_twice_produces_identical_output() -> None:
    entries = generate_glossary.load_concepts()
    assert generate_glossary.render(entries) == generate_glossary.render(entries)


def test_a_hand_edit_is_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--check` actually catches a tampered file, not just a string comparison in memory."""
    tampered_path = tmp_path / "GLOSSARY.md"
    entries = generate_glossary.load_concepts()
    rendered = generate_glossary.render(entries)
    tampered_path.write_text(rendered.replace("# Glossary", "# Glossary (edited)", 1),
                              encoding="utf-8")

    monkeypatch.setattr(generate_glossary, "TARGET", tampered_path)
    assert generate_glossary.main(["--check"]) == 1

    tampered_path.write_text(rendered, encoding="utf-8")
    assert generate_glossary.main(["--check"]) == 0


def test_only_concept_memories_appear(tmp_path: Path) -> None:
    brain = tmp_path / "brain" / "concepts"
    brain.mkdir(parents=True)
    procedures = tmp_path / "brain" / "procedures"
    procedures.mkdir(parents=True)

    (brain / "a.md").write_text(
        "---\nid: mem-a\ntitle: A Term\ntype: concept\ncreated: 2026-09-07\n---\n\n"
        "Definition of A.",
        encoding="utf-8",
    )
    (procedures / "b.md").write_text(
        "---\nid: mem-b\ntitle: A Procedure\ntype: procedure\ncreated: 2026-09-07\n---\n\nSteps.",
        encoding="utf-8",
    )

    entries = generate_glossary.load_concepts(tmp_path / "brain")
    titles = [entry["title"] for entry in entries]
    assert titles == ["A Term"]


def test_filtering_by_tag_and_system(tmp_path: Path) -> None:
    brain = tmp_path / "brain" / "concepts"
    brain.mkdir(parents=True)

    (brain / "a.md").write_text(
        "---\nid: mem-a\ntitle: Term A\ntype: concept\ncreated: 2026-09-07\n"
        "tags: [alpha]\nsystems: [sys-one]\n---\n\nDef A.",
        encoding="utf-8",
    )
    (brain / "b.md").write_text(
        "---\nid: mem-b\ntitle: Term B\ntype: concept\ncreated: 2026-09-07\n"
        "tags: [beta]\nsystems: [sys-two]\n---\n\nDef B.",
        encoding="utf-8",
    )

    entries = generate_glossary.load_concepts(tmp_path / "brain")
    assert "Term A" in generate_glossary.render(entries, tag="alpha")
    assert "Term B" not in generate_glossary.render(entries, tag="alpha")
    assert "Term B" in generate_glossary.render(entries, system="sys-two")
    assert "Term A" not in generate_glossary.render(entries, system="sys-two")


def test_missing_brain_directory_is_an_empty_glossary(tmp_path: Path) -> None:
    assert generate_glossary.load_concepts(tmp_path / "does-not-exist") == []
