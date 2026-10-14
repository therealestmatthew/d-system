"""The document scan and check, the registries, and the catalog, on fixture repositories.

Codes and dates are built at run time so this file carries no literal document code or calendar
date for the plugin's source-reference check to flag.
"""

from __future__ import annotations

import shutil
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import documents
import paths
import pytest
import yaml
from conftest import PLUGIN_ROOT

TODAY = date.today()
STAMP = TODAY.isoformat()
PLAN_1 = "PLAN" + "-001"
PLAN_2 = "PLAN" + "-002"
REQ_1 = "REQ" + "-001"
ADR_1 = "ADR" + "-001"


def front(**meta: Any) -> str:
    return "---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n\n# Title\n\nBody.\n"


def plan_meta(**changes: Any) -> dict[str, Any]:
    return {"schema_version": 1, "id": "doc-a", "code": PLAN_1, "title": "A plan",
            "kind": "plan", "status": "draft", "owner": "repository-owner",
            "created": STAMP, "updated": STAMP, "systems": [], "depends_on": [], **changes}


class Repo:
    """A fixture repository with the template registers under ``docs/``."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.docs = root / "docs"
        self.docs.mkdir(parents=True)
        for name in ("codes.yaml", "systems.yaml"):
            shutil.copy(PLUGIN_ROOT / "templates" / name, self.docs / name)

    def config(self, **flags: str) -> paths.Config:
        return paths.resolve({"root": str(self.root), **flags}, env={})

    def write(self, relative: str, text: str) -> Path:
        path = self.docs / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def plan(self, **changes: Any) -> Path:
        meta = plan_meta(**changes)
        return self.write(f"plans/{meta['code']}-a.md", front(**meta))

    def systems(self, entries: list[dict[str, Any]]) -> None:
        registry = yaml.safe_load((self.docs / "systems.yaml").read_text())
        registry["systems"] = entries
        (self.docs / "systems.yaml").write_text(yaml.safe_dump(registry))

    def errors(self, **flags: str) -> list[str]:
        return documents.scan(self.config(**flags)).errors

    def catalog(self) -> int:
        return documents.main(["--root", str(self.root)])

    def check(self) -> list[str]:
        return documents.check(self.config())


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    return Repo(tmp_path)


def system(**changes: Any) -> dict[str, Any]:
    return {"id": "sys-core", "name": "Core", "domain": "application", "status": "planned",
            "owner": "repository-owner", "paths": [], "depends_on": [],
            "description": "The core.", **changes}


# --- A clean tree and the catalog ------------------------------------------------------------


def test_the_scaffolded_registers_with_no_documents_are_clean(repo: Repo) -> None:
    assert repo.errors() == []
    assert repo.check() == [f"docs/{documents.CATALOG}: is missing; run the catalog command "
                            "and commit it"]
    assert repo.catalog() == 0
    assert repo.check() == []


def test_a_clean_tree_passes_and_the_scan_hands_over_its_contract(repo: Repo) -> None:
    repo.systems([system()])
    repo.plan(systems=["sys-core"])
    result = documents.scan(repo.config())
    assert result.errors == []
    assert result.documents["doc-a"]["path"] == f"docs/plans/{PLAN_1}-a.md"
    assert result.documents["doc-a"]["location"] == f"plans/{PLAN_1}-a.md"
    assert set(result.systems) == {"sys-core"}
    assert set(result.owners) == {"repository-owner"}
    assert [entry["kind"] for entry in result.register["series"]][0] == "plan"


def test_a_hand_edited_catalog_fails_check(repo: Repo) -> None:
    repo.plan()
    assert repo.catalog() == 0
    assert repo.check() == []
    catalog = repo.docs / documents.CATALOG
    catalog.write_text(catalog.read_text() + "\nAn edit.\n")
    assert any("differs from the rendered catalog" in e for e in repo.check())


def test_a_new_document_makes_the_catalog_stale(repo: Repo) -> None:
    assert repo.catalog() == 0
    repo.plan()
    assert any("differs from the rendered catalog" in e for e in repo.check())


def test_the_catalog_writes_nothing_when_the_tree_fails(repo: Repo) -> None:
    repo.plan(kind="nonsense")
    assert repo.catalog() == 1
    assert not (repo.docs / documents.CATALOG).exists()


def test_the_catalog_counts_phases_when_a_backlog_exists(repo: Repo) -> None:
    repo.plan()
    backlog = repo.root / "backlog" / "backlog.yaml"
    backlog.parent.mkdir()
    backlog.write_text(yaml.safe_dump({"items": [
        {"id": "one", "plan": "doc-a", "sources": [], "status": "active", "agent": "agent-x"},
    ]}))
    assert repo.catalog() == 0
    text = (repo.docs / documents.CATALOG).read_text()
    assert f"| {PLAN_1} | doc-a | draft | 0 | 1 | 0 | agent-x |" in text
    assert repo.check() == []


def test_an_unscaffolded_repository_has_nothing_to_check(tmp_path: Path) -> None:
    config = paths.resolve({"root": str(tmp_path)}, env={})
    assert documents.check(config) == []


def test_one_missing_register_is_reported(repo: Repo) -> None:
    (repo.docs / "codes.yaml").unlink()
    assert any("docs/codes.yaml: missing" in e for e in repo.check())


# --- Front matter ------------------------------------------------------------------------------


def test_a_document_with_an_unknown_kind_fails_check(repo: Repo) -> None:
    repo.plan(kind="nonsense")
    assert any("'nonsense' is not one of" in e for e in repo.check())


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"status": "accepted"}, "invalid status accepted for kind plan"),
        ({"owner": "nobody"}, "unknown owner nobody"),
        ({"systems": ["sys-missing"]}, "unknown system sys-missing"),
        ({"status": "complete"}, "complete document requires completion_evidence"),
        ({"status": "complete", "completion_evidence": ["nowhere.txt"]},
         "missing evidence file nowhere.txt"),
        ({"status": "complete", "completion_evidence": ["../outside.txt"]},
         "missing evidence file ../outside.txt"),
        ({"depends_on": ["doc-missing"]}, "unresolved or self document reference doc-missing"),
        ({"depends_on": ["doc-a"]}, "unresolved or self document reference doc-a"),
        ({"updated": (TODAY - timedelta(days=1)).isoformat()},
         "require created <= updated <= today"),
        ({"created": (TODAY + timedelta(days=1)).isoformat(),
          "updated": (TODAY + timedelta(days=1)).isoformat()},
         "require created <= updated <= today"),
        ({"tags": ["x"]}, "Additional properties are not allowed"),
        ({"code": "plan-1"}, "does not match"),
        ({"status": "superseded"}, "superseded document has no replacement"),
    ],
)
def test_an_invalid_document_fails(repo: Repo, changes: dict[str, Any], expected: str) -> None:
    repo.plan(**changes)
    errors = repo.errors()
    assert any(expected in error for error in errors), errors


def test_an_adr_uses_its_own_lifecycle(repo: Repo) -> None:
    meta = plan_meta(id="doc-d", code=ADR_1, kind="adr", status="accepted")
    repo.write(f"decisions/{ADR_1}-d.md", front(**meta))
    assert repo.errors() == []
    meta["status"] = "active"
    repo.write(f"decisions/{ADR_1}-d.md", front(**meta))
    assert any("invalid status active for kind adr" in e for e in repo.errors())


def test_evidence_that_exists_satisfies_a_complete_plan(repo: Repo) -> None:
    (repo.root / "result.txt").write_text("done\n")
    repo.plan(status="complete", completion_evidence=["result.txt"])
    assert repo.errors() == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("no front matter\n", "missing opening front matter delimiter"),
        ("---\nid: doc-a\n", "missing closing front matter delimiter"),
        (front(**plan_meta()).split("# Title")[0], "document body is empty"),
        ("---\n- a list\n---\n\nBody.\n", "front matter must be a mapping"),
        ("---\nid: doc-a\nid: doc-b\n---\n\nBody.\n", "duplicate YAML key: id"),
    ],
)
def test_malformed_front_matter_is_rejected(repo: Repo, text: str, expected: str) -> None:
    repo.write(f"plans/{PLAN_1}-a.md", text)
    assert any(expected in error for error in repo.errors())


def test_dates_stay_strings_and_are_checked_by_format(repo: Repo) -> None:
    repo.plan(created="not-a-date", updated="not-a-date")
    assert any("is not a 'date'" in e for e in repo.errors())


def test_duplicate_ids_and_dependency_cycles(repo: Repo) -> None:
    repo.plan()
    repo.write(f"plans/{PLAN_2}-b.md", front(**plan_meta(code=PLAN_2)))
    assert any("duplicate id doc-a" in e for e in repo.errors())
    repo.write(f"plans/{PLAN_1}-a.md", front(**plan_meta(depends_on=["doc-b"])))
    repo.write(f"plans/{PLAN_2}-b.md",
               front(**plan_meta(id="doc-b", code=PLAN_2, depends_on=["doc-a"])))
    assert any("documents depends_on: dependency cycle" in e for e in repo.errors())


def test_parent_is_only_valid_between_plans(repo: Repo) -> None:
    repo.plan()
    meta = plan_meta(id="doc-r", code=REQ_1, kind="requirement", parent="doc-a")
    repo.write(f"requirements/{REQ_1}-r.md", front(**meta))
    assert any("parent is only valid between plans" in e for e in repo.errors())


def test_a_replacement_requires_the_replaced_document_to_be_superseded(repo: Repo) -> None:
    repo.plan()
    repo.write(f"plans/{PLAN_2}-b.md",
               front(**plan_meta(id="doc-b", code=PLAN_2, supersedes=["doc-a"])))
    assert any("replaced document doc-a must be superseded" in e for e in repo.errors())
    repo.plan(status="superseded")
    assert repo.errors() == []


def test_the_code_rules_run_on_the_scan(repo: Repo) -> None:
    repo.write("plans/wrong-name.md", front(**plan_meta()))
    assert any(f"filename must start with {PLAN_1}-" in e for e in repo.errors())


# --- Which files are governed ------------------------------------------------------------------


def test_a_readme_is_governed_unless_listed_as_exempt(repo: Repo) -> None:
    repo.write("README.md", "# About these documents\n")
    assert any("docs/README.md: missing opening front matter" in e for e in repo.errors())
    assert repo.errors(exempt_files="docs/README.md") == []


def test_a_symlink_is_reported_and_not_read(repo: Repo, tmp_path_factory: Any) -> None:
    outside = tmp_path_factory.mktemp("outside") / "secret.md"
    outside.write_text(front(**plan_meta()))
    (repo.docs / "plans").mkdir()
    (repo.docs / "plans" / f"{PLAN_1}-a.md").symlink_to(outside)
    result = documents.scan(repo.config())
    assert "doc-a" not in result.documents
    assert any("symlink is not followed" in e for e in result.errors)


def test_a_configured_document_root_is_used(tmp_path: Path) -> None:
    repo = Repo(tmp_path)
    shutil.move(str(repo.docs), str(tmp_path / "governed"))
    config = paths.resolve({"root": str(tmp_path), "docs_root": "governed"}, env={})
    assert documents.scan(config).errors == []


def test_kinds_by_id_reads_front_matter_without_checking_it(repo: Repo) -> None:
    repo.plan(owner="nobody")
    assert documents.kinds_by_id(repo.config()) == {"doc-a": "plan"}


# --- The registries --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entries", "expected"),
    [
        ([system(owner="nobody")], "sys-core: unknown owner nobody"),
        ([system(status="implemented")], "implemented or scaffold system requires paths"),
        ([system(paths=["src/missing"])], "sys-core: missing path src/missing"),
        ([system(depends_on=["sys-missing"])], "unknown system dependency sys-missing"),
        ([system(depends_on=["sys-other"]), system(id="sys-other", depends_on=["sys-core"])],
         "systems: dependency cycle"),
        ([system(), system()], "duplicate system id"),
    ],
)
def test_the_systems_registry_is_checked(repo: Repo, entries: list[dict[str, Any]],
                                         expected: str) -> None:
    repo.systems(entries)
    assert any(expected in error for error in repo.errors()), repo.errors()


def test_the_code_register_is_checked_against_the_document_kinds(repo: Repo) -> None:
    register = yaml.safe_load((repo.docs / "codes.yaml").read_text())
    register["series"] = [s for s in register["series"] if s["kind"] != "adr"]
    (repo.docs / "codes.yaml").write_text(yaml.safe_dump(register))
    assert "codes: no series registered for kind adr" in repo.errors()


def test_an_invalid_register_is_reported_by_schema(repo: Repo) -> None:
    (repo.docs / "codes.yaml").write_text("schema_version: 2\n")
    assert any(e.startswith("docs/codes.yaml:") for e in repo.errors())


def test_every_kind_in_the_schema_has_a_lifecycle() -> None:
    assert set(documents.schema("document")["properties"]["kind"]["enum"]) == set(
        documents.LIFECYCLE)
    union = set().union(*documents.LIFECYCLE.values())
    assert union == set(documents.schema("document")["properties"]["status"]["enum"])


# --- The skills --------------------------------------------------------------------------------


@pytest.mark.parametrize(("skill", "script"), [("next-code", "cli.py"), ("catalog", "cli.py"),
                                               ("plan-check", "plan_check.py")])
def test_each_skill_runs_exactly_one_script(skill: str, script: str) -> None:
    import re

    text = (PLUGIN_ROOT / "skills" / skill / "SKILL.md").read_text()
    named = set(re.findall(r"scripts/([a-z_]+\.py)", text))
    assert named == {script}


def test_the_next_code_skill_names_the_register_only_to_forbid_editing_it() -> None:
    text = (PLUGIN_ROOT / "skills" / "next-code" / "SKILL.md").read_text()
    paragraphs = [p for p in text.split("\n\n") if "codes.yaml" in p]
    assert len(paragraphs) == 1
    assert "never edited by hand" in paragraphs[0]


@pytest.mark.parametrize("skill", ["next-code", "catalog", "plan-check"])
def test_a_skill_runs_nothing_but_its_script(skill: str) -> None:
    """Every command in the skill's code blocks, after option assignments, is its one script."""
    text = (PLUGIN_ROOT / "skills" / skill / "SKILL.md").read_text()
    blocks = text.split("```bash\n")[1:]
    assert blocks
    for block in blocks:
        command = " ".join(block.split("```")[0].replace("\\\n", " ").split())
        words = [w for w in command.split(" ") if not w.startswith("CLAUDE_PLUGIN_OPTION_")]
        assert words[:2] == ["uv", "run"], command
        assert words[2].startswith('"${CLAUDE_PLUGIN_ROOT}/scripts/'), command
        assert not any(w in {">", ">>", "|", "&&", ";", "tee"} for w in words), command
