"""Exercise governance failures on isolated files, without touching the repository DB."""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from src.governance.__main__ import ROOT, audit, inventory, parse_frontmatter, public_path

TODAY = date(2026, 9, 5)


def document(**changes: Any) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "id": "doc-example",
        "code": "PLAN-001",
        "title": "Example",
        "kind": "plan",
        "status": "draft",
        "owner": "repository-owner",
        "created": "2026-09-05",
        "updated": "2026-09-05",
        "systems": ["sys-example"],
        "depends_on": [],
        **changes,
    }


def write_doc(
    root: Path, meta: dict[str, Any], path: str = "docs/01-plans/PLAN-001-example.md"
) -> Path:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("---\n" + json.dumps(meta) + "\n---\n\n# Body\n", encoding="utf-8")
    return target


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "schemas", tmp_path / "schemas")
    (tmp_path / "_data/projects").mkdir(parents=True)
    (tmp_path / "_data/tags.json").write_text('[{"id": "python"}]')
    (tmp_path / "docs/08-governance").mkdir(parents=True)
    registry = {
        "schema_version": 1,
        "owners": {"repository-owner": "Maintainer"},
        "systems": [
            {
                "id": "sys-example",
                "name": "Example",
                "domain": "governance",
                "status": "implemented",
                "owner": "repository-owner",
                "paths": ["schemas"],
                "depends_on": [],
                "description": "Example component",
            }
        ],
    }
    (tmp_path / "docs/08-governance/systems.yaml").write_text(json.dumps(registry))
    shutil.copy(
        ROOT / "docs/08-governance/codes.yaml", tmp_path / "docs/08-governance/codes.yaml"
    )
    write_doc(tmp_path, document())
    return tmp_path


def test_current_repository_validates() -> None:
    errors, _, result = audit(ROOT)
    assert errors == []
    assert "doc-system-audit" in result["documents"]
    assert result["memories"]


def test_inventory_is_derived_and_read_only(repository: Path) -> None:
    errors, warnings, result = audit(repository, TODAY)
    assert errors == warnings == []
    assert "doc-example" in inventory(result)
    assert "sys-example" in inventory(result)
    assert not (repository / "data").exists()
    write_doc(
        repository, document(status="complete", completion_evidence=["schemas/memory.schema.json"])
    )
    errors, _, result = audit(repository, TODAY)
    assert errors == []
    assert "doc-example" not in inventory(result)


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"unexpected": True}, "Additional properties"),
        ({"created": "2026-02-30"}, "is not a"),
        ({"created": "2026-09-06"}, "created <= updated"),
        ({"updated": "2026-09-04"}, "created <= updated"),
        ({"owner": "nobody"}, "unknown owner"),
        ({"systems": ["sys-missing"]}, "unknown system"),
        ({"tags": ["missing"]}, "unknown tag"),
        ({"depends_on": ["doc-missing"]}, "unresolved"),
        ({"status": "accepted"}, "invalid status"),
        ({"status": "complete"}, "requires completion_evidence"),
        ({"status": "complete", "completion_evidence": ["absent.py"]}, "missing evidence"),
        ({"status": "superseded"}, "has no replacement"),
        ({"kind": "adr", "status": "draft"}, "belongs under docs/04-decisions/"),
    ],
)
def test_invalid_document_fails(repository: Path, changes: dict[str, Any], expected: str) -> None:
    write_doc(repository, document(**changes))
    errors, _, _ = audit(repository, TODAY)
    assert any(expected in error for error in errors), errors


def test_overdue_review_is_advisory(repository: Path) -> None:
    write_doc(repository, document(review_after="2026-09-04"))
    errors, warnings, _ = audit(repository, TODAY)
    assert errors == []
    assert len(warnings) == 1
    assert "review overdue" in warnings[0]


def test_duplicate_ids_and_dependency_cycle(repository: Path) -> None:
    write_doc(repository, document(code="PLAN-002"), "docs/01-plans/PLAN-002-duplicate.md")
    assert any("duplicate ID" in error for error in audit(repository, TODAY)[0])
    write_doc(
        repository,
        document(id="doc-other", code="PLAN-002", depends_on=["doc-example"]),
        "docs/01-plans/PLAN-002-duplicate.md",
    )
    write_doc(repository, document(depends_on=["doc-other"]))
    assert any("dependency cycle" in error for error in audit(repository, TODAY)[0])


def test_parent_cycle_and_replacement_consistency(repository: Path) -> None:
    write_doc(repository, document(parent="doc-other"))
    write_doc(
        repository,
        document(id="doc-other", code="PLAN-002", parent="doc-example"),
        "docs/01-plans/PLAN-002-other.md",
    )
    assert any("documents parent" in error for error in audit(repository, TODAY)[0])
    write_doc(repository, document(status="superseded"))
    write_doc(
        repository,
        document(id="doc-other", code="PLAN-002", supersedes=["doc-example"]),
        "docs/01-plans/PLAN-002-other.md",
    )
    assert audit(repository, TODAY)[0] == []
    write_doc(repository, document())
    assert any("must be superseded" in error for error in audit(repository, TODAY)[0])


def test_new_readme_is_not_an_exemption(repository: Path) -> None:
    target = repository / "docs/01-plans/extra/README.md"
    target.parent.mkdir()
    target.write_text("# Undocumented new plan")
    assert any("missing opening" in error for error in audit(repository, TODAY)[0])


@pytest.mark.parametrize(
    "text",
    [
        "# No metadata",
        "---\nid: doc-test",
        "---\n[]\n---\nBody",
        "---\nid: doc-test\nid: doc-other\n---\nBody",
        "---\nid: doc-test\n---\n",
    ],
)
def test_malformed_frontmatter_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        parse_frontmatter(text)


def test_dates_and_body_delimiters() -> None:
    meta = parse_frontmatter("---\ncreated: 2026-09-05\ntitle: a---b\n---\nBody\n---\nMore")
    assert meta == {"created": "2026-09-05", "title": "a---b"}


def test_memory_compatibility_and_references(repository: Path) -> None:
    memory = {
        "id": "mem-example",
        "title": "Example",
        "type": "concept",
        "created": "2026-09-05",
        "project": "d-system",
        "scope": "global",
        "tags": ["python"],
        "systems": ["sys-example"],
    }
    write_doc(repository, memory, "brain/concepts/example.md")
    assert audit(repository, TODAY)[0] == []
    memory.update(project="unknown", related=["mem-missing"], systems=["sys-missing"])
    write_doc(repository, memory, "brain/concepts/example.md")
    errors = audit(repository, TODAY)[0]
    assert any("unknown project" in error for error in errors)
    assert any("unknown related memory" in error for error in errors)
    assert any("unknown system" in error for error in errors)


@pytest.mark.parametrize("value", ["/etc/passwd", "../outside", "_private/secret", "data/x"])
def test_protected_paths_rejected(repository: Path, value: str) -> None:
    with pytest.raises(ValueError):
        public_path(repository, value)


def test_symlink_not_read(repository: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    outside = tmp_path_factory.mktemp("outside") / "unread.md"
    outside.write_text("This must never be parsed")
    (repository / "docs/leak.md").symlink_to(outside)
    errors = audit(repository, TODAY)[0]
    assert any("symlink" in error for error in errors)
    assert not any("missing opening" in error for error in errors)


def test_registry_integrity(repository: Path) -> None:
    path = repository / "docs/08-governance/systems.yaml"
    registry = json.loads(path.read_text())
    registry["systems"][0].update(paths=["missing"], depends_on=["sys-example"], owner="unknown")
    path.write_text(json.dumps(registry))
    errors = audit(repository, TODAY)[0]
    assert any("missing path" in error for error in errors)
    assert any("dependency cycle" in error for error in errors)
    assert any("unknown owner" in error for error in errors)


def test_idea_staging_directory_is_ungoverned() -> None:
    """Files parked in docs/00-working/ carry no front matter by design (ADR-010).

    The staging area exists to relieve the pressure that turns an unformed idea into a
    governed document prematurely. A file here must never fail the audit.
    """
    staging = ROOT / "docs/00-working"
    probe = staging / "probe-ungoverned.md"
    probe.write_text("# no front matter here\n")
    try:
        errors, _warnings, _result = audit(ROOT)
        assert not [e for e in errors if "00-working" in e], errors
    finally:
        probe.unlink()
