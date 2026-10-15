"""Every data path resolves flag, then environment, then local.yaml, then plugin option, then
project.yaml, then default."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import paths
import pytest
from conftest import PLUGIN_ROOT

EXPECTED_KEYS = {
    "ideas_path", "ideas_view_path", "priority_path", "backlog_path", "docs_root",
    "integration_branch", "worktree_dir", "triage_search", "exempt_files", "staging_dir",
    "partitions_dir", "brain_root", "product_root", "product_worktree_dir", "aws_read_profile",
    "aws_deploy_profile", "aws_region", "handle", "dev_port_range", "control_remote",
    "control_github", "product_remote", "product_github",
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
    # Outside a git repository, CLAUDE_PROJECT_DIR comes before the working directory.
    assert paths.repository_root(None, {"CLAUDE_PROJECT_DIR": str(c)}, cwd=tmp_path) == c
    assert paths.repository_root(None, {}, cwd=tmp_path) == tmp_path.resolve()


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), "-c", "user.name=fixture",
                    "-c", "user.email=fixture@example", *args],
                   capture_output=True, text=True, check=True)


def test_a_command_run_in_a_worktree_resolves_that_worktree(tmp_path: Path) -> None:
    primary = tmp_path / "sample"
    primary.mkdir()
    _git(primary, "init", "-q")
    _git(primary, "commit", "-q", "--allow-empty", "-m", "fixture")
    worktree = tmp_path / "sample-worktrees" / "session"
    _git(primary, "worktree", "add", "-q", "-b", "session", str(worktree))
    (worktree / "docs").mkdir()
    env = {"CLAUDE_PROJECT_DIR": str(primary)}
    assert paths.repository_root(None, env, cwd=worktree / "docs") == worktree.resolve()
    # A worktree inside the project directory (as Claude Code's own worktrees are) is its own root.
    inner = primary / ".claude" / "worktrees" / "inner"
    _git(primary, "worktree", "add", "-q", "-b", "inner", str(inner))
    assert paths.repository_root(None, env, cwd=inner) == inner.resolve()
    # The explicit sources still come first.
    assert paths.repository_root(str(primary), env, cwd=worktree) == primary.resolve()
    env_root = {**env, "IDEA_REALIZATION_ROOT": str(primary)}
    assert paths.repository_root(None, env_root, cwd=worktree) == primary.resolve()


def test_a_project_directory_nested_in_another_repository_is_kept(tmp_path: Path) -> None:
    outer = tmp_path / "outer"
    nested = outer / "control"
    (nested / "docs").mkdir(parents=True)
    _git(outer, "init", "-q")
    env = {"CLAUDE_PROJECT_DIR": str(nested)}
    assert paths.repository_root(None, env, cwd=nested / "docs") == nested.resolve()
    assert paths.repository_root(None, env, cwd=outer) == outer.resolve()


def test_help_lists_every_path_flag(capsys: object) -> None:
    import argparse

    parser = argparse.ArgumentParser()
    paths.add_arguments(parser)
    text = parser.format_help()
    for key in paths.KEYS.values():
        assert key.flag in text


# --- every configured value is validated -----------------------------------------------------
#
# The refusals are written as ``ValueError`` (``paths.PathError`` subclasses it) so each test
# fails before the fix on behavior, not on a missing name.


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


# --- local.yaml and project.yaml -------------------------------------------------------------


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), "-c", "user.name=fixture",
                    "-c", "user.email=fixture@example", *args],
                   capture_output=True, text=True, check=True)


def _write(root: Path, name: str, text: str) -> None:
    (root / ".idea-realization").mkdir(parents=True, exist_ok=True)
    (root / ".idea-realization" / name).write_text(text)


PROJECT = ("schema_version: 1\ncontrol:\n  remote: REPLACE-WITH-THE-CONTROL-REPOSITORY-GIT-URL\n"
           "  integration_branch: dev\naws:\n  region: eu-west-1\n")


def test_project_yaml_sits_between_the_plugin_option_and_the_default(tmp_path: Path) -> None:
    _write(tmp_path, "project.yaml", PROJECT)
    config = paths.resolve({"root": str(tmp_path)}, env={})
    assert config.text("integration_branch") == "dev"
    assert config.text("aws_region") == "eu-west-1"
    assert config.sources["integration_branch"] == "project.yaml"
    assert config.sources["ideas_path"] == "default"
    option = paths.resolve({"root": str(tmp_path)},
                           env={"CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH": "trunk"})
    assert option.text("integration_branch") == "trunk"
    assert option.sources["integration_branch"] == "CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH"


def test_the_integration_branch_option_is_declared_empty() -> None:
    manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["userConfig"]["integration_branch"]["default"] == ""
    assert paths.KEYS["integration_branch"].default == "main"


def test_a_saved_empty_integration_branch_option_leaves_project_yaml_in_force(
        tmp_path: Path) -> None:
    _write(tmp_path, "project.yaml", PROJECT)
    config = paths.resolve({"root": str(tmp_path)},
                           env={"CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH": ""})
    assert config.text("integration_branch") == "dev"
    assert config.sources["integration_branch"] == "project.yaml"


def test_main_is_the_integration_branch_when_nothing_sets_it(tmp_path: Path) -> None:
    config = paths.resolve({"root": str(tmp_path)},
                           env={"CLAUDE_PLUGIN_OPTION_INTEGRATION_BRANCH": ""})
    assert config.text("integration_branch") == "main"
    assert config.sources["integration_branch"] == "default"


def test_local_yaml_sits_between_the_environment_and_the_plugin_option(tmp_path: Path) -> None:
    _write(tmp_path, "project.yaml", PROJECT)
    _write(tmp_path, "local.yaml", "aws_region: us-west-2\naws_read_profile: hack-read\n")
    env = {"CLAUDE_PLUGIN_OPTION_AWS_REGION": "ap-south-1",
           "CLAUDE_PLUGIN_OPTION_AWS_READ_PROFILE": "option-read"}
    config = paths.resolve({"root": str(tmp_path)}, env=env)
    assert config.text("aws_region") == "us-west-2"
    assert config.text("aws_read_profile") == "hack-read"
    assert config.sources["aws_region"] == "local.yaml"
    env["IDEA_REALIZATION_AWS_REGION"] = "ca-central-1"
    config = paths.resolve({"root": str(tmp_path)}, env=env)
    assert (config.text("aws_region"), config.sources["aws_region"]) == (
        "ca-central-1", "IDEA_REALIZATION_AWS_REGION")
    flagged = paths.resolve({"root": str(tmp_path), "aws_region": "sa-east-1"}, env=env)
    assert (flagged.text("aws_region"), flagged.sources["aws_region"]) == (
        "sa-east-1", "--aws-region")


def test_a_placeholder_counts_as_unset(tmp_path: Path) -> None:
    _write(tmp_path, "project.yaml", PROJECT.replace("eu-west-1", "REPLACE-WITH-THE-REGION"))
    _write(tmp_path, "local.yaml", "aws_read_profile: REPLACE-WITH-YOUR-READ-ONLY-AWS-PROFILE\n")
    config = paths.resolve({"root": str(tmp_path)}, env={})
    assert config.text("aws_region") == ""
    assert config.text("aws_read_profile") == ""
    assert config.sources["aws_read_profile"] == "default"


def test_local_yaml_is_read_from_the_primary_checkout(tmp_path: Path) -> None:
    primary = tmp_path / "sample"
    primary.mkdir()
    _git(primary, "init", "-q")
    _git(primary, "commit", "-q", "--allow-empty", "-m", "fixture")
    worktree = tmp_path / "sample-worktrees" / "session"
    _git(primary, "worktree", "add", "-q", "-b", "session", str(worktree))
    _write(primary, "local.yaml", "handle: ana\n")
    _write(worktree, "local.yaml", "handle: bo\n")  # a session worktree's copy is never read
    config = paths.resolve({"root": str(worktree)}, env={})
    assert config.text("handle") == "ana"
    assert paths.local_record(worktree) == primary.resolve() / ".idea-realization" / "local.yaml"


def test_local_yaml_keeps_the_roots_place_below_the_git_top_level(tmp_path: Path) -> None:
    primary = tmp_path / "outer"
    (primary / "inner").mkdir(parents=True)
    _git(primary, "init", "-q")
    _git(primary, "commit", "-q", "--allow-empty", "-m", "fixture")
    worktree = tmp_path / "outer-worktrees" / "session"
    _git(primary, "worktree", "add", "-q", "-b", "session", str(worktree))
    (worktree / "inner").mkdir()
    assert paths.local_record(worktree / "inner") == (
        primary.resolve() / "inner" / ".idea-realization" / "local.yaml")


def test_an_invalid_local_yaml_is_refused_by_name(tmp_path: Path) -> None:
    _write(tmp_path, "local.yaml", "ideas_path: elsewhere.jsonl\n")
    with pytest.raises(paths.PathError, match="local.yaml"):
        paths.resolve({"root": str(tmp_path)}, env={})
    _write(tmp_path, "local.yaml", "handle: [unclosed\n")
    with pytest.raises(paths.PathError, match="not valid YAML"):
        paths.resolve({"root": str(tmp_path)}, env={})


def test_an_invalid_project_yaml_is_refused_by_name(tmp_path: Path) -> None:
    # An unquoted date parses as a date, not the string the schema asks for.
    unquoted = "-".join(["2030", "01", "02"])
    _write(tmp_path, "project.yaml", f"schema_version: 1\ndemo:\n  date: {unquoted}\n")
    with pytest.raises(paths.PathError, match="project.yaml"):
        paths.resolve({"root": str(tmp_path)}, env={})


@pytest.mark.parametrize(("name", "value"), [
    ("handle", "Ana"), ("handle", "1ana"), ("dev_port_range", "3000"),
    ("dev_port_range", "4000-3000"), ("dev_port_range", "80-90"),
])
def test_a_malformed_handle_or_port_range_is_refused(tmp_path: Path, name: str,
                                                      value: str) -> None:
    with pytest.raises(ValueError, match=name):
        _config(tmp_path, **{name: value}).text(name)


def test_a_well_formed_handle_and_port_range_are_accepted(tmp_path: Path) -> None:
    config = _config(tmp_path, handle="ana", dev_port_range="3000-3099")
    assert (config.text("handle"), config.text("dev_port_range")) == ("ana", "3000-3099")
    assert config.invalid() == []


def test_show_prints_a_source_column(tmp_path: Path, capsys: pytest.CaptureFixture[str],
                                     monkeypatch: pytest.MonkeyPatch) -> None:
    for name in [*paths.KEYS, "root"]:
        monkeypatch.delenv("IDEA_REALIZATION_" + name.upper(), raising=False)
        monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_" + name.upper(), raising=False)
    _write(tmp_path, "project.yaml", PROJECT)
    monkeypatch.setenv("IDEA_REALIZATION_HANDLE", "ana")
    assert paths.main(["show", "--root", str(tmp_path), "--docs-root", "notes"]) == 0
    rows = {line.split()[0]: line.split() for line in capsys.readouterr().out.splitlines()}
    assert rows["key"] == ["key", "value", "source"]
    assert rows["integration_branch"][1:] == ["dev", "project.yaml"]
    assert rows["handle"][1:] == ["ana", "IDEA_REALIZATION_HANDLE"]
    assert rows["docs_root"][-1] == "--docs-root"
    assert rows["ideas_path"][-1] == "default"
    assert "local" in rows


def test_plain_output_is_unchanged_without_show(tmp_path: Path,
                                                capsys: pytest.CaptureFixture[str]) -> None:
    assert paths.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0] == f"root: {tmp_path.resolve()}"
    assert "integration_branch: " in out and "source" not in out


def test_this_repository_integrates_on_dev_from_project_yaml() -> None:
    repository = PLUGIN_ROOT.parent.parent
    config = paths.resolve({"root": str(repository)}, env={})
    assert config.text("integration_branch") == "dev"
    assert config.sources["integration_branch"] == "project.yaml"


CONTROL_URL = "git@forge.example.com:team/hack-control.git"
PRODUCT_URL = "git@forge.example.com:team/hack-product.git"
REPOSITORY_KEYS = ("control_remote", "control_github", "product_remote", "product_github")


def test_repository_keys_resolve_env_then_local_yaml_then_the_tracked_files(
        tmp_path: Path) -> None:
    _write(tmp_path, "project.yaml", "schema_version: 1\ncontrol:\n  integration_branch: dev\n"
           "  remote: https://forge.example.com/tracked/control\n  github: tracked/control\n")
    _write(tmp_path, "product.yaml", "schema_version: 1\nname: hack\nintegration_branch: dev\n"
           "remote: https://forge.example.com/tracked/product\ngithub: tracked/product\n")
    tracked = paths.resolve({"root": str(tmp_path)}, env={})
    assert [tracked.sources[key] for key in REPOSITORY_KEYS] == [
        "project.yaml", "project.yaml", "product.yaml", "product.yaml"]
    assert tracked.text("product_github") == "tracked/product"
    _write(tmp_path, "local.yaml", f"control_remote: {CONTROL_URL}\ncontrol_github: team/c\n"
           f"product_remote: {PRODUCT_URL}\nproduct_github: team/p\n")
    local = paths.resolve({"root": str(tmp_path)}, env={})
    assert [local.text(key) for key in REPOSITORY_KEYS] == [CONTROL_URL, "team/c",
                                                            PRODUCT_URL, "team/p"]
    assert {local.sources[key] for key in REPOSITORY_KEYS} == {"local.yaml"}
    env = {"IDEA_REALIZATION_PRODUCT_REMOTE": "https://forge.example.com/env/product"}
    from_env = paths.resolve({"root": str(tmp_path)}, env=env)
    assert (from_env.text("product_remote"), from_env.sources["product_remote"]) == (
        "https://forge.example.com/env/product", "IDEA_REALIZATION_PRODUCT_REMOTE")
    assert from_env.sources["control_remote"] == "local.yaml"


def test_placeholder_repository_values_count_as_unset(tmp_path: Path) -> None:
    _write(tmp_path, "project.yaml", PROJECT)
    _write(tmp_path, "product.yaml", "schema_version: 1\nname: hack\nintegration_branch: dev\n"
           "remote: REPLACE-WITH-THE-PRODUCT-REPOSITORY-GIT-URL\n")
    _write(tmp_path, "local.yaml", "control_github: REPLACE-WITH-THE-CONTROL-ORG-AND-NAME\n")
    config = paths.resolve({"root": str(tmp_path)}, env={})
    assert [config.text(key) for key in REPOSITORY_KEYS] == ["", "", "", ""]
    assert {config.sources[key] for key in REPOSITORY_KEYS} == {"default"}
    assert config.invalid() == []


@pytest.mark.parametrize(("name", "value"), [
    ("control_github", "team"), ("product_github", "a/b/c"),
    ("product_github", "https://forge.example.com/team/x"),
    ("control_remote", "git@forge.example.com:team/a b.git"),
])
def test_a_malformed_repository_value_is_refused(tmp_path: Path, name: str, value: str) -> None:
    with pytest.raises(ValueError, match=name):
        _config(tmp_path, **{name: value}).text(name)


def test_show_names_where_a_repository_url_came_from(
        tmp_path: Path, capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch) -> None:
    for name in [*paths.KEYS, "root"]:
        monkeypatch.delenv("IDEA_REALIZATION_" + name.upper(), raising=False)
        monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_" + name.upper(), raising=False)
    _write(tmp_path, "local.yaml", f"product_remote: {PRODUCT_URL}\n")
    assert paths.main(["show", "--root", str(tmp_path)]) == 0
    rows = {line.split()[0]: line.split() for line in capsys.readouterr().out.splitlines()}
    assert rows["product_remote"][1:] == [PRODUCT_URL, "local.yaml"]
    assert rows["control_remote"][1:] == ["default"]


def test_this_repository_tracks_no_repository_url() -> None:
    repository = PLUGIN_ROOT.parent.parent
    config = paths.resolve({"root": str(repository)}, env={})
    tracked = paths.project_values(repository)
    assert not set(REPOSITORY_KEYS) & set(tracked)
    assert all(config.sources[key] != "project.yaml" for key in REPOSITORY_KEYS)


def test_git_env_drops_every_location_variable() -> None:
    env = {name: "/elsewhere" for name in paths.GIT_LOCATION_VARIABLES}
    env.update({"HOME": "/home/ana", "GIT_CONFIG_GLOBAL": "/home/ana/.gitconfig"})
    assert paths.git_env(env) == {"HOME": "/home/ana", "GIT_CONFIG_GLOBAL": "/home/ana/.gitconfig"}


def test_every_git_dash_c_call_drops_the_location_variables() -> None:
    """A ``git -C <path>`` that inherits GIT_DIR reads the hook's repository, not ``<path>``. Every
    such call in the plugin's scripts and the control repository's tools passes ``git_env``."""
    import ast

    roots = [paths.PLUGIN_ROOT / "scripts", paths.PLUGIN_ROOT.parent.parent / "tools"]
    missing = []
    for source in sorted(p for root in roots if root.is_dir() for p in root.rglob("*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and node.args
                    and isinstance(node.args[0], ast.List) and len(node.args[0].elts) >= 2):
                continue
            first, second = node.args[0].elts[:2]
            if not (isinstance(first, ast.Constant) and first.value == "git"
                    and isinstance(second, ast.Constant) and second.value == "-C"):
                continue
            env = next((kw.value for kw in node.keywords if kw.arg == "env"), None)
            if not (isinstance(env, ast.Call) and ast.unparse(env.func).endswith("git_env")):
                missing.append(f"{source.name}:{node.lineno}")
    assert missing == []
