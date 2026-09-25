"""The working-agreement and orientation templates, and the script that renders them."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import render_template
from conftest import PLUGIN_ROOT, SCRIPTS
from test_no_source_references import identities, scan

TEMPLATES = [PLUGIN_ROOT / "templates" / name for name in ("AGENTS.md", "CLAUDE.md")]
VALUES = {
    "integration_branch": "trunk",
    "worktree_dir": "../sample-worktrees",
    "data_root": "records",
    "confidential_dir": "secret",
}


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / "render_template.py"), *args],
                          cwd=cwd, capture_output=True, text=True, check=False)


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.name)
def test_a_rendered_template_has_no_marker_and_passes_the_source_reference_check(
    template: Path, tmp_path: Path
) -> None:
    rendered = render_template.render(template.read_text(), VALUES)
    assert "{{" not in rendered and "}}" not in rendered
    for value in VALUES.values():
        assert value in rendered
    (tmp_path / template.name).write_text(rendered)
    assert scan(tmp_path, identities()) == []


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.name)
def test_each_template_uses_only_the_four_placeholders(template: Path) -> None:
    assert set(render_template.placeholders(template.read_text())) <= set(render_template.KNOWN)


def test_between_them_the_templates_use_all_four() -> None:
    used = {name for t in TEMPLATES for name in render_template.placeholders(t.read_text())}
    assert used == set(render_template.KNOWN)


def test_an_unknown_placeholder_fails_rendering() -> None:
    with pytest.raises(render_template.TemplateError, match="unknown placeholder"):
        render_template.render("Deploy to {{production_host}}.\n", VALUES)


def test_a_placeholder_without_a_value_fails_rendering() -> None:
    with pytest.raises(render_template.TemplateError, match="no value for placeholder"):
        render_template.render("Data lives in {{data_root}}.\n", {})


def test_the_command_writes_a_new_file_and_never_overwrites(tmp_path: Path) -> None:
    args = ["--root", str(tmp_path), "--set", "data_root=records", "--set", "confidential_dir=s",
            "--output", "AGENTS.md"]
    first = run(str(TEMPLATES[0]), *args, cwd=tmp_path)
    assert first.returncode == 0, first.stderr
    written = (tmp_path / "AGENTS.md").read_text()
    assert "{{" not in written
    second = run(str(TEMPLATES[0]), *args, cwd=tmp_path)
    assert second.returncode == 1
    assert "not overwritten" in second.stderr
    assert (tmp_path / "AGENTS.md").read_text() == written


def test_the_command_refuses_an_unknown_placeholder(tmp_path: Path) -> None:
    template = tmp_path / "bad.md"
    template.write_text("Deploy to {{production_host}}.\n")
    result = run(str(template), "--root", str(tmp_path), cwd=tmp_path)
    assert result.returncode == 1
    assert "unknown placeholder(s): production_host" in result.stderr


def test_the_command_requires_the_values_without_a_default(tmp_path: Path) -> None:
    result = run(str(TEMPLATES[0]), "--root", str(tmp_path), cwd=tmp_path)
    assert result.returncode == 1
    assert "confidential_dir" in result.stderr and "data_root" in result.stderr


def test_configured_values_fill_the_two_with_a_default(tmp_path: Path) -> None:
    repo = tmp_path / "sample"
    repo.mkdir()
    result = run(str(TEMPLATES[1]), "--root", str(repo), "--set", "data_root=records",
                 "--set", "confidential_dir=secret", "--integration-branch", "trunk", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "`trunk`" in result.stdout
    assert "../sample-worktrees" in result.stdout


def test_a_malformed_set_is_a_usage_error(tmp_path: Path) -> None:
    result = run(str(TEMPLATES[0]), "--root", str(tmp_path), "--set", "nonsense", cwd=tmp_path)
    assert result.returncode == 2
