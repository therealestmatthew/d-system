"""Every data path resolves flag, then environment, then plugin option, then default."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import paths
from conftest import PLUGIN_ROOT

EXPECTED_KEYS = {
    "ideas_path", "ideas_view_path", "priority_path", "backlog_path", "docs_root",
    "integration_branch", "worktree_dir", "triage_search", "exempt_files", "staging_dir",
    "partitions_dir",
}


def test_keys_come_from_the_manifest() -> None:
    manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert set(paths.KEYS) == set(manifest["userConfig"]) == EXPECTED_KEYS
    assert paths.KEYS["triage_search"].kind == "paths"
    assert paths.KEYS["integration_branch"].kind == "text"
    assert paths.KEYS["ideas_path"].kind == "path"


def test_default_applies_when_nothing_is_set(tmp_path: Path) -> None:
    config = paths.resolve({"root": str(tmp_path)}, env={})
    assert config.path("ideas_path") == tmp_path / "ideas" / "ideas.jsonl"
    assert config.text("integration_branch") == "main"
    assert config.paths("triage_search") == [tmp_path / "docs"]
    assert config.paths("exempt_files") == []


def test_plugin_option_beats_default(tmp_path: Path) -> None:
    env = {"CLAUDE_PLUGIN_OPTION_IDEAS_PATH": "option.jsonl"}
    assert paths.resolve({"root": str(tmp_path)}, env=env).path("ideas_path") == (
        tmp_path / "option.jsonl")


def test_environment_beats_plugin_option(tmp_path: Path) -> None:
    env = {"CLAUDE_PLUGIN_OPTION_IDEAS_PATH": "option.jsonl",
           "IDEA_REALIZATION_IDEAS_PATH": "env.jsonl"}
    assert paths.resolve({"root": str(tmp_path)}, env=env).path("ideas_path") == (
        tmp_path / "env.jsonl")


def test_flag_beats_everything(tmp_path: Path) -> None:
    env = {"CLAUDE_PLUGIN_OPTION_IDEAS_PATH": "option.jsonl",
           "IDEA_REALIZATION_IDEAS_PATH": "env.jsonl"}
    flags = {"root": str(tmp_path), "ideas_path": "flag.jsonl"}
    assert paths.resolve(flags, env=env).path("ideas_path") == tmp_path / "flag.jsonl"


def test_unsubstituted_option_counts_as_unset(tmp_path: Path) -> None:
    env = {"CLAUDE_PLUGIN_OPTION_IDEAS_PATH": "${user_config.ideas_path}"}
    assert paths.resolve({"root": str(tmp_path)}, env=env).path("ideas_path") == (
        tmp_path / "ideas" / "ideas.jsonl")


def test_list_option_is_comma_separated(tmp_path: Path) -> None:
    env = {"CLAUDE_PLUGIN_OPTION_EXEMPT_FILES": "docs/a b.md, docs/c.md"}
    config = paths.resolve({"root": str(tmp_path)}, env=env)
    assert config.paths("exempt_files") == [tmp_path / "docs/a b.md", tmp_path / "docs/c.md"]


def test_absolute_path_is_kept(tmp_path: Path) -> None:
    other = tmp_path / "elsewhere.jsonl"
    config = paths.resolve({"root": str(tmp_path), "ideas_path": str(other)}, env={})
    assert config.path("ideas_path") == other


def test_worktree_dir_names_the_repository(tmp_path: Path) -> None:
    root = tmp_path / "sample"
    root.mkdir()
    config = paths.resolve({"root": str(root)}, env={})
    assert config.path("worktree_dir") == root / ".." / "sample-worktrees"


def test_worktree_dir_from_a_worktree_is_the_repositorys(tmp_path: Path) -> None:
    def git(cwd: Path, *args: str) -> None:
        subprocess.run(["git", "-C", str(cwd), "-c", "user.name=fixture",
                        "-c", "user.email=fixture@example", *args],
                       capture_output=True, text=True, check=True)

    primary = tmp_path / "sample"
    primary.mkdir()
    git(primary, "init", "-q")
    git(primary, "commit", "-q", "--allow-empty", "-m", "fixture")
    worktree = tmp_path / "sample-worktrees" / "session"
    git(primary, "worktree", "add", "-q", "-b", "session", str(worktree))
    expected = primary.resolve() / ".." / "sample-worktrees"
    assert paths.resolve({"root": str(worktree)}, env={}).path("worktree_dir") == expected
    assert paths.resolve({"root": str(primary)}, env={}).path("worktree_dir") == expected
    # Every other relative path still belongs to the checkout it was resolved in.
    assert paths.resolve({"root": str(worktree)}, env={}).path("ideas_path") == (
        worktree / "ideas" / "ideas.jsonl")


def test_root_precedence(tmp_path: Path) -> None:
    a, b, c = (tmp_path / name for name in "abc")
    assert paths.repository_root(str(a), {"IDEA_REALIZATION_ROOT": str(b)}) == a
    env = {"IDEA_REALIZATION_ROOT": str(b), "CLAUDE_PROJECT_DIR": str(c)}
    assert paths.repository_root(None, env) == b
    assert paths.repository_root(None, {"CLAUDE_PROJECT_DIR": str(c)}) == c
    assert paths.repository_root(None, {}, cwd=tmp_path) == tmp_path.resolve()


def test_help_lists_every_path_flag(capsys: object) -> None:
    import argparse

    parser = argparse.ArgumentParser()
    paths.add_arguments(parser)
    text = parser.format_help()
    for key in paths.KEYS.values():
        assert key.flag in text


# --- R04 to R06: every configured value is validated (PLAN-052, REQ-035) ----------------------
#
# The refusals are written as ``ValueError`` (``paths.PathError`` subclasses it) so each test
# fails at the baseline on behavior, not on a missing name (PLAN-052 D10).


def _config(root: Path, **flags: str) -> paths.Config:
    return paths.resolve({"root": str(root), **flags}, env={})


def test_absolute_path_outside_the_root_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    config = _config(root, ideas_path=str(tmp_path / "outside.jsonl"))
    with pytest.raises(ValueError, match="ideas_path"):
        config.path("ideas_path")


def test_traversal_out_of_the_root_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    with pytest.raises(ValueError, match="ideas_path"):
        _config(root, ideas_path="../x.jsonl").path("ideas_path")


def test_symlink_escape_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ideas").mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "ideas" / "link").symlink_to(outside)
    with pytest.raises(ValueError, match="ideas_path"):
        _config(root, ideas_path="ideas/link/x.jsonl").path("ideas_path")


def test_a_git_component_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="ideas_path"):
        _config(tmp_path, ideas_path=".git/x.jsonl").path("ideas_path")


def test_an_escaping_list_entry_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    with pytest.raises(ValueError, match="triage_search"):
        _config(root, triage_search="docs,../elsewhere").paths("triage_search")
    with pytest.raises(ValueError, match="exempt_files"):
        _config(root, exempt_files=str(tmp_path / "x.md")).paths("exempt_files")


def test_a_relative_path_inside_the_root_still_resolves(tmp_path: Path) -> None:
    assert _config(tmp_path, ideas_path="ideas/a/../b.jsonl").path("ideas_path") == (
        tmp_path / "ideas/a/../b.jsonl")


def test_worktree_dir_inside_the_primary_checkout_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="worktree_dir"):
        _config(tmp_path, worktree_dir="wt").path("worktree_dir")


@pytest.mark.parametrize("branch", ["--output=x", "-x", "a..b", "with space"])
def test_a_malformed_integration_branch_is_refused(tmp_path: Path, branch: str) -> None:
    with pytest.raises(ValueError, match="integration_branch"):
        _config(tmp_path, integration_branch=branch).text("integration_branch")


@pytest.mark.parametrize("branch", ["dev", "main", "release/1.2"])
def test_a_well_formed_integration_branch_is_accepted(tmp_path: Path, branch: str) -> None:
    assert _config(tmp_path, integration_branch=branch).text("integration_branch") == branch
