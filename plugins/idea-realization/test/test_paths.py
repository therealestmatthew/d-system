"""Every data path resolves flag, then environment, then plugin option, then default."""

from __future__ import annotations

import json
from pathlib import Path

import paths
from conftest import PLUGIN_ROOT

EXPECTED_KEYS = {
    "ideas_path", "ideas_view_path", "priority_path", "backlog_path", "docs_root",
    "integration_branch", "worktree_dir", "triage_search", "exempt_files", "staging_dir",
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
