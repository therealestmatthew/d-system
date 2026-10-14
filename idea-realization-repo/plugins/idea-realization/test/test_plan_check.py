"""The mechanical section check for plan drafts."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import plan_check
import pytest
import yaml
from conftest import PLUGIN_ROOT, SCRIPTS

TEMPLATE = PLUGIN_ROOT / "templates" / "plan.md"


def phase_id(area: str, number: int) -> str:
    return "-".join(["phase", area, f"{number:02d}"])


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / "plan_check.py"), *args], cwd=cwd,
                          capture_output=True, text=True, check=False)


def template() -> str:
    return TEMPLATE.read_text()


def test_the_plan_template_passes(tmp_path: Path) -> None:
    result = run(str(TEMPLATE), "--root", str(tmp_path), cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_draft_missing_its_boundaries_section_fails_and_names_it(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(template().replace("## Out of scope", "## Things we skip"))
    result = run(str(draft), "--root", str(tmp_path), cwd=tmp_path)
    assert result.returncode == 1
    assert result.stdout.strip() == f"{draft}: missing: Boundaries"


def test_every_required_section_is_reported(tmp_path: Path) -> None:
    missing = plan_check.missing_sections("# Only a title\n\nBody.\n", {})
    assert missing == ["Context", "Design", "Work", "Verification", "Boundaries",
                       "Open questions"]


def test_every_accepted_heading_satisfies_its_section() -> None:
    for name, accepted in plan_check.REQUIRED:
        for heading in accepted:
            text = "\n".join(f"## {h[1][0]}" for h in plan_check.REQUIRED if h[0] != name)
            assert name not in plan_check.missing_sections(f"{text}\n### {heading}\n", {})


def test_a_heading_inside_a_fence_does_not_count() -> None:
    text = template().replace("## Out of scope", "```\n## Out of scope\n```")
    assert plan_check.missing_sections(text, {}) == ["Boundaries"]


def test_a_heading_must_match_exactly() -> None:
    for variant in ("## Out of scope (none)", "## out of scope", "#### Out of scope",
                    "# Out of scope"):
        text = template().replace("## Out of scope", variant)
        assert plan_check.missing_sections(text, {}) == ["Boundaries"], variant


def test_a_plan_on_a_requirement_needs_requirement_coverage() -> None:
    text = template().replace("depends_on: []", "depends_on: [doc-needs]")
    kinds = {"doc-needs": "requirement"}
    assert plan_check.missing_sections(text, kinds) == ["Requirement coverage"]
    assert plan_check.missing_sections(text, {"doc-needs": "plan"}) == []
    covered = text.replace("## Acceptance and verification", "## Requirement coverage")
    assert plan_check.missing_sections(covered, kinds) == []


def test_a_block_list_depends_on_is_read() -> None:
    text = template().replace("depends_on: []", "depends_on:\n- doc-needs")
    assert plan_check.missing_sections(text, {"doc-needs": "requirement"}) == [
        "Requirement coverage"]


def test_two_phase_ids_need_an_execution_order() -> None:
    one = template() + f"\nDelivered by {phase_id('demo', 1)}.\n"
    assert plan_check.missing_sections(one, {}) == []
    two = one + f"Then {phase_id('demo', 2)}.\n"
    assert plan_check.missing_sections(two, {}) == ["Concurrency"]
    assert plan_check.missing_sections(two + "\n## Execution order\n\nIn turn.\n", {}) == []
    fenced = one + f"```\n{phase_id('demo', 2)}\n```\n"
    assert plan_check.missing_sections(fenced, {}) == []


def test_the_requirement_lookup_reads_the_document_root(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "requirements"
    docs.mkdir(parents=True)
    meta = {"id": "doc-needs", "kind": "requirement"}
    (docs / "r.md").write_text("---\n" + yaml.safe_dump(meta) + "---\n\nBody.\n")
    draft = tmp_path / "draft.md"
    draft.write_text(template().replace("depends_on: []", "depends_on: [doc-needs]"))
    result = run(str(draft), "--root", str(tmp_path), cwd=tmp_path)
    assert result.returncode == 1
    assert "missing: Requirement coverage" in result.stdout


def test_an_unreadable_draft_exits_2(tmp_path: Path) -> None:
    result = run(str(tmp_path / "absent.md"), "--root", str(tmp_path), cwd=tmp_path)
    assert result.returncode == 2


def test_the_check_runs_from_a_copy_of_the_scripts(tmp_path: Path) -> None:
    copy = tmp_path / "copy"
    shutil.copytree(SCRIPTS, copy / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(PLUGIN_ROOT / ".claude-plugin", copy / ".claude-plugin")
    result = subprocess.run([sys.executable, str(copy / "scripts" / "plan_check.py"),
                             str(TEMPLATE), "--root", str(tmp_path)],
                            cwd=tmp_path, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("name", ["plan.md", "requirement.md"])
def test_the_templates_carry_no_real_code(name: str) -> None:
    text = (PLUGIN_ROOT / "templates" / name).read_text()
    assert "-NNN" in text
