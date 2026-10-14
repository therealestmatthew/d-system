"""The tool-docs generator: paired operations documents and the one reference document.

Document codes in fixture filenames are built at run time so this file carries none literally.
"""

from __future__ import annotations

import ast
import shutil
import subprocess
import sys
from pathlib import Path

import generate_tool_docs as gen
import pytest
from conftest import PLUGIN_ROOT, SCRIPTS

OPS_DOC = "OPS" + "-001-sample-tool.md"
TOOL = '''"""Do one sample thing.

Exit codes: 0 on success, 3 when nothing was found.
"""
import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", help="how many", default=5)
    parser.add_argument("--mode", choices=["a", "b"], required=True)
    if parser.parse_args().limit:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
DOC = f"# Sample tool\n\nNarrative written by hand.\n\n{gen.START}\n{gen.END}\n\nMore narrative.\n"

#: The arguments docs/tools.md is generated with, as its own header states.
REFERENCE_ARGS = ["--tools", "scripts", "--reference", "docs/tools.md",
                  "--title", "idea-realization tools",
                  "--invocation", 'uv run "${CLAUDE_PLUGIN_ROOT}/scripts/{name}"',
                  "--preamble-from", "paths.py"]


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / "generate_tool_docs.py"), *args],
                          cwd=cwd, capture_output=True, text=True, check=False)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "sample_tool.py").write_text(TOOL)
    (tmp_path / "docs" / "governance").mkdir(parents=True)
    (tmp_path / "docs" / "governance" / OPS_DOC).write_text(DOC)
    return tmp_path


def doc(repo: Path) -> Path:
    return repo / "docs" / "governance" / OPS_DOC


# --- Paired documents --------------------------------------------------------------------------


def test_the_generated_block_is_filled_and_the_narrative_kept(repo: Path) -> None:
    assert run("--root", str(repo), cwd=repo).returncode == 0
    text = doc(repo).read_text()
    assert text.startswith("# Sample tool\n\nNarrative written by hand.\n")
    assert text.endswith(f"{gen.END}\n\nMore narrative.\n")
    assert "Do one sample thing." in text
    assert "| `--limit` | how many |  | 5 |  |" in text
    assert "| `--mode` |  | a, b |  | yes |" in text
    assert "Exit codes found in source: 0, 3." in text


def test_running_twice_produces_identical_output(repo: Path) -> None:
    run("--root", str(repo), cwd=repo)
    first = doc(repo).read_bytes()
    run("--root", str(repo), cwd=repo)
    assert doc(repo).read_bytes() == first
    assert run("--root", str(repo), "--check", cwd=repo).returncode == 0


def test_a_hand_edit_inside_the_block_fails_the_check_naming_the_file(repo: Path) -> None:
    run("--root", str(repo), cwd=repo)
    text = doc(repo).read_text().replace("how many", "how many, edited by hand")
    doc(repo).write_text(text)
    result = run("--root", str(repo), "--check", cwd=repo)
    assert result.returncode == 1
    assert str(doc(repo)) in result.stderr
    assert doc(repo).read_text() == text


def test_a_tool_with_no_document_is_reported_and_not_created(repo: Path) -> None:
    (repo / "tools" / "lonely.py").write_text('"""Alone."""\n')
    result = run("--root", str(repo), "--check", cwd=repo)
    assert result.returncode == 1
    assert "no paired document for: lonely.py" in result.stderr
    assert not list((repo / "docs" / "governance").glob("*lonely*"))


def test_a_document_without_the_block_is_a_usage_error(repo: Path) -> None:
    doc(repo).write_text("# Sample tool\n\nNo markers.\n")
    assert run("--root", str(repo), cwd=repo).returncode == 2


def test_the_block_survives_marker_text_quoted_inside_it(tmp_path: Path) -> None:
    tool = tmp_path / "quoting.py"
    tool.write_text(f'"""Quotes its own markers:\n\n    {gen.START}\n    {gen.END}\n"""\n')
    rendered = gen.render_block(tool, "quoting.py")
    once = gen.update_doc(f"a\n{gen.START}\n{gen.END}\nb\n", rendered, tool)
    assert gen.update_doc(once, rendered, tool) == once


def test_arguments_path_keys_and_exit_codes_are_read_without_importing() -> None:
    tree = ast.parse((SCRIPTS / "codes.py").read_text())
    assert gen.extract_path_keys(tree) == ["docs_root", "exempt_files", "backlog_path"]
    assert any(arg["flags"] == ["kind"] for arg in gen.extract_arguments(tree))
    assert gen.extract_path_keys(ast.parse("x = 1\n")) is None
    assert gen.extract_exit_codes(ast.parse("def f():\n    return 4\nraise SystemExit(5)\n")) \
        == [4, 5]


# --- The reference document ---------------------------------------------------------------------


def test_the_committed_tools_reference_is_current() -> None:
    result = run("--root", str(PLUGIN_ROOT), *REFERENCE_ARGS, "--check", cwd=PLUGIN_ROOT)
    assert result.returncode == 0, result.stderr


def test_the_reference_names_every_script_except_paths_and_the_checks() -> None:
    text = (PLUGIN_ROOT / "docs" / "tools.md").read_text()
    sections = {line[4:-1] for line in text.splitlines() if line.startswith("## `")}
    expected = {p.name for p in SCRIPTS.glob("*.py") if p.name not in {"paths.py", "__init__.py"}}
    assert sections == expected
    assert "## Configuration" in text
    for name in expected:
        assert f'uv run "${{CLAUDE_PLUGIN_ROOT}}/scripts/{name}"' in text


def test_regenerating_the_reference_twice_is_identical(tmp_path: Path) -> None:
    copy = tmp_path / "plugin"
    shutil.copytree(SCRIPTS, copy / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    for _ in range(2):
        assert run("--root", str(copy), *REFERENCE_ARGS, cwd=copy).returncode == 0
    generated = (copy / "docs" / "tools.md").read_text()
    assert generated == (PLUGIN_ROOT / "docs" / "tools.md").read_text()


def test_a_new_script_makes_the_reference_stale_until_regenerated(tmp_path: Path) -> None:
    copy = tmp_path / "plugin"
    shutil.copytree(SCRIPTS, copy / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (copy / "docs").mkdir()
    shutil.copy(PLUGIN_ROOT / "docs" / "tools.md", copy / "docs" / "tools.md")
    assert run("--root", str(copy), *REFERENCE_ARGS, "--check", cwd=copy).returncode == 0
    (copy / "scripts" / "fixture_extra.py").write_text('"""A fixture script."""\n')
    stale = run("--root", str(copy), *REFERENCE_ARGS, "--check", cwd=copy)
    assert stale.returncode == 1
    assert "docs/tools.md" in stale.stderr
    assert run("--root", str(copy), *REFERENCE_ARGS, cwd=copy).returncode == 0
    assert run("--root", str(copy), *REFERENCE_ARGS, "--check", cwd=copy).returncode == 0
    assert "## `fixture_extra.py`" in (copy / "docs" / "tools.md").read_text()


def test_the_reference_states_how_it_was_generated() -> None:
    header = (PLUGIN_ROOT / "docs" / "tools.md").read_text().split("## Configuration")[0]
    assert "--reference docs/tools.md" in header and "--preamble-from paths.py" in header


def test_the_tools_skill_reads_only_the_reference() -> None:
    import re

    text = (PLUGIN_ROOT / "skills" / "tools" / "SKILL.md").read_text()
    assert "${CLAUDE_PLUGIN_ROOT}/docs/tools.md" in text
    assert re.findall(r"[\w./${}-]+\.(?:md|py|yaml|json)", text) == [
        "${CLAUDE_PLUGIN_ROOT}/docs/tools.md"]
    assert "```" not in text, "the skill reads the reference; it runs no command"


def test_the_command_in_the_reference_header_runs_as_written(tmp_path: Path) -> None:
    """The header's command, run from a copy of the plugin, finds the committed file current."""
    import shlex

    copy = tmp_path / "plugin"
    shutil.copytree(SCRIPTS, copy / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(PLUGIN_ROOT / ".claude-plugin", copy / ".claude-plugin")
    (copy / "docs").mkdir()
    shutil.copy(PLUGIN_ROOT / "docs" / "tools.md", copy / "docs" / "tools.md")
    header = (copy / "docs" / "tools.md").read_text().split("## Configuration")[0]
    command = shlex.split(header.split("`")[1])
    assert command[:3] == ["uv", "run", "scripts/generate_tool_docs.py"]
    uv = shutil.which("uv")
    runner = [uv, "run", "--quiet", "--no-project", "--script"] if uv else [sys.executable]
    result = subprocess.run([*runner, *command[2:], "--check"], cwd=copy,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
