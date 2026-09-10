#!/usr/bin/env python3
"""Consolidated JSON inventories of the repository's concepts and its systems registry.

Two sections, each read from its own single source of truth. Concepts and terminology come
from `brain/`'s `concept` memories, read exactly the way `tools/generate_glossary.py` reads
them — this module imports that script's `load_concepts()` rather than re-parsing front matter
a second time — plus every `### Term` heading found inside a concept's body, since several
concept memories (`brain/concepts/terms-*.md`) are themselves grouped glossaries of individual
terms. Systems come from `docs/08-governance/systems.yaml`: id, name, domain, status and the
`depends_on` dependency edges, one row per registry entry, nothing inferred or reconciled
against actual imports.

The tool makes no model or network call and asks the wall clock for nothing: every value is a
pure function of `brain/` and `docs/08-governance/systems.yaml`. Two runs against an unchanged
repository produce byte-identical output — every list is sorted and every dict key is emitted
in sorted order (`json.dumps(..., sort_keys=True)`).

    uv run python tools/overview_inventory.py               # print to stdout
    uv run python tools/overview_inventory.py --out FILE     # write to FILE instead
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parent.parent
SYSTEMS = ROOT / "docs" / "08-governance" / "systems.yaml"

#: Matches an ATX level-3 heading such as `### Governed plan` — the convention the
#: `terms-*.md` concept memories use to mark one defined term within a larger grouped entry.
_TERM_HEADING = re.compile(r"^### (.+)$", re.MULTILINE)


def _load_generate_glossary() -> ModuleType:
    """Import `tools/generate_glossary.py` by path so its reading conventions are reused,
    not re-implemented — `tools/` carries no `__init__.py`, so this is a plain file import.
    """
    spec = importlib.util.spec_from_file_location(
        "generate_glossary", ROOT / "tools" / "generate_glossary.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_concepts() -> list[dict[str, Any]]:
    """Every `type: concept` brain memory, via `generate_glossary.load_concepts()`."""
    generate_glossary = _load_generate_glossary()
    concepts: list[dict[str, Any]] = generate_glossary.load_concepts()
    return concepts


def concept_entries(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per concept: id, title, and its sorted tags and systems."""
    rows = [
        {
            "id": entry["id"],
            "title": entry["title"],
            "tags": sorted(entry.get("tags", [])),
            "systems": sorted(entry.get("systems", [])),
        }
        for entry in concepts
    ]
    return sorted(rows, key=lambda row: row["id"])


def term_entries(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every `### Term` heading found in a concept's body, one row per term.

    A concept memory that is a single definition (no `### ` heading in its body) contributes
    no rows here — its own entry in `concept_entries()` already stands for it; this section
    exists for the grouped glossary memories that define several terms in one file.
    """
    rows = [
        {"term": match.group(1).strip(), "concept_id": entry["id"], "concept_title": entry["title"]}
        for entry in concepts
        for match in _TERM_HEADING.finditer(entry.get("content", ""))
    ]
    return sorted(rows, key=lambda row: (row["term"].lower(), row["concept_id"]))


def load_systems(path: Path = SYSTEMS) -> list[dict[str, Any]]:
    """Every entry in the systems registry. A missing file is an empty registry, not an error."""
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    systems: list[dict[str, Any]] = list(data.get("systems", []))
    return systems


def system_entries(systems: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per system: id, name, domain, status, and its sorted dependency edges."""
    rows = [
        {
            "id": entry["id"],
            "name": entry["name"],
            "domain": entry["domain"],
            "status": entry["status"],
            "depends_on": sorted(entry.get("depends_on", [])),
        }
        for entry in systems
    ]
    return sorted(rows, key=lambda row: row["id"])


def build_inventory(
    concepts: list[dict[str, Any]], systems: list[dict[str, Any]]
) -> dict[str, Any]:
    """The full inventory, assembled from one read of brain/ and one read of the registry."""
    concepts_out = concept_entries(concepts)
    terms_out = term_entries(concepts)
    systems_out = system_entries(systems)
    return {
        "meta": {
            "concept_count": len(concepts_out),
            "term_count": len(terms_out),
            "system_count": len(systems_out),
        },
        "concepts": concepts_out,
        "terms": terms_out,
        "systems": systems_out,
    }


def render(concepts: list[dict[str, Any]], systems: list[dict[str, Any]]) -> str:
    """The full JSON document, deterministically ordered and newline-terminated."""
    inventory = build_inventory(concepts, systems)
    return json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", type=Path, default=None, help="write the JSON here instead of stdout"
    )
    args = parser.parse_args(argv)

    rendered = render(load_concepts(), load_systems())

    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
