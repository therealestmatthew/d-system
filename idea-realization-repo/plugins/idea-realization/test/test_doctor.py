"""The doctor names stale and missing files, exits 1 and changes nothing; edited data passes."""

from __future__ import annotations

import json
from pathlib import Path

import doctor
import paths
import pytest
import scaffold


def listing(root: Path) -> dict[str, bytes | None]:
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None)
            for p in sorted(root.rglob("*"))}


def test_doctor_reports_edited_and_missing(tmp_path: Path, capsys: object) -> None:
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["ideas", "backlog"])
    (tmp_path / "ideas" / "priority.yaml").write_text("edited\n")
    (tmp_path / "backlog" / "backlog.yaml").unlink()
    before = listing(tmp_path)
    assert doctor.main(["--root", str(tmp_path)]) == 1
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "edited    ideas/priority.yaml" in output
    assert "missing   backlog/backlog.yaml" in output
    assert "unchanged ideas/ideas.jsonl" in output
    assert listing(tmp_path) == before


def test_clean_install_exits_zero(tmp_path: Path) -> None:
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["ideas"])
    assert doctor.main(["--root", str(tmp_path)]) == 0


def test_no_record_exits_two(tmp_path: Path) -> None:
    assert doctor.main(["--root", str(tmp_path)]) == 2
    assert list(tmp_path.iterdir()) == []


# --- doctor reports every invalid key --------------------------------------------------------


def test_doctor_names_every_invalid_key_and_exits_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    scaffold.scaffold(paths.resolve({"root": str(root)}, env={}), list(scaffold.FEATURES))
    monkeypatch.setenv("IDEA_REALIZATION_IDEAS_PATH", "../escape.jsonl")
    monkeypatch.setenv("IDEA_REALIZATION_DOCS_ROOT", str(tmp_path / "elsewhere"))
    assert doctor.main(["--root", str(root)]) == 1
    out = capsys.readouterr()
    text = out.out + out.err
    assert "ideas_path" in text
    assert "docs_root" in text
    assert "Traceback" not in text


# --- consent to edit configuration, and the control origin ------------------------------------


def git(cwd: Path, *args: str) -> None:
    import subprocess

    subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True)


def test_a_consented_config_edit_is_reported_edited_not_drifted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = paths.resolve({"root": str(tmp_path)}, env={})
    scaffold.scaffold(config, ["product", "project"], consent=["edit"])
    product = tmp_path / ".idea-realization" / "product.yaml"
    product.write_text(product.read_text().replace("integration_branch: main",
                                                   "integration_branch: dev"))
    project = tmp_path / ".idea-realization" / "project.yaml"
    project.write_text(project.read_text().replace("integration_branch: main",
                                                   "integration_branch: dev"))
    assert doctor.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "edited    .idea-realization/product.yaml  (product, consent: edit)" in out
    assert "edited    .idea-realization/project.yaml  (project, consent: edit)" in out
    assert "origin    not compared" in out
    project.unlink()
    assert doctor.main(["--root", str(tmp_path)]) == 1
    assert "missing   .idea-realization/project.yaml" in capsys.readouterr().out


def test_a_config_edit_without_consent_is_edited_too(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """product.yaml is repository-owned; the consent only adds a note to the line."""
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["product"])
    product = tmp_path / ".idea-realization" / "product.yaml"
    product.write_text(product.read_text() + "github: " + "/".join(["team", "x"]) + "\n")
    assert doctor.main(["--root", str(tmp_path)]) == 0
    assert "edited    .idea-realization/product.yaml  (product)\n" in capsys.readouterr().out


def test_doctor_reports_a_control_origin_that_is_not_the_control_remote(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("IDEA_REALIZATION_CONTROL_REMOTE", raising=False)
    monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_CONTROL_REMOTE", raising=False)
    git(tmp_path, "init", "-q")
    git(tmp_path, "remote", "add", "origin", "git@forge.example.com:team/control.git")
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["project"],
                      consent=["edit"])
    assert doctor.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "origin    not compared: control_remote is not set" in out
    assert ".idea-realization/local.yaml" in out
    local = tmp_path / ".idea-realization" / "local.yaml"
    local.write_text("control_remote: https://forge.example.com/team/control\n")
    assert doctor.main(["--root", str(tmp_path)]) == 0
    assert "origin    matches control_remote (from local.yaml)" in capsys.readouterr().out
    local.write_text("control_remote: git@forge.example.com:team/other.git\n")
    assert doctor.main(["--root", str(tmp_path)]) == 1
    assert "not the control repository" in capsys.readouterr().out
    monkeypatch.setenv("IDEA_REALIZATION_CONTROL_REMOTE", "git@forge.example.com:team/control.git")
    assert doctor.main(["--root", str(tmp_path)]) == 0
    assert "(from IDEA_REALIZATION_CONTROL_REMOTE)" in capsys.readouterr().out


def test_an_invalid_project_yaml_exits_two_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["project"])
    (tmp_path / ".idea-realization" / "project.yaml").write_text("schema_version: 2\n")
    assert doctor.main(["--root", str(tmp_path)]) == 2
    assert "project.yaml" in capsys.readouterr().err


# --- plugin-owned schema copies against repository-owned data -----------------------------------


def test_data_files_edited_after_scaffold_are_not_drift(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A claim edits the backlog and an allocation the code register: normal use, exit 0."""
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), list(scaffold.FEATURES))
    edited = ["backlog/backlog.yaml", "docs/codes.yaml", "docs/systems.yaml",
              "docs/workstreams.yaml", "ideas/ideas.jsonl", "ideas/ideas.md",
              "ideas/priority.yaml", "brain/index.md"]
    for name in edited:
        with (tmp_path / name).open("a") as handle:
            handle.write("\n# edited\n")
    assert doctor.main(["--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    for name in edited:
        assert f"edited    {name}  (" in out
    assert "drifted" not in out.replace("0 drifted", "")


def test_a_stale_schema_copy_is_reported_with_the_fix(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["backlog"])
    copy = tmp_path / ".idea-realization" / "schemas" / "backlog.schema.json"
    copy.write_text(copy.read_text().replace('"maximum"', '"maximumm"', 1))
    before = listing(tmp_path)
    assert doctor.main(["--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert ("stale     .idea-realization/schemas/backlog.schema.json  (backlog, differs from "
            "the plugin's copy, fix: scaffold.py --feature backlog --refresh-schemas)") in out
    assert listing(tmp_path) == before


def test_a_hand_updated_schema_copy_is_unrecorded_until_refreshed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The copy matches the plugin but the record still holds the old hash."""
    plugin = tmp_path / "plugin"
    (plugin / "schemas").mkdir(parents=True)
    source = plugin / "schemas" / "backlog.schema.json"
    source.write_text('{"version": 1}\n')
    root = tmp_path / "repo"
    root.mkdir()
    config = paths.resolve({"root": str(root)}, env={})
    scaffold.scaffold(config, ["backlog"], plugin_root=plugin)
    source.write_text('{"version": 2}\n')
    copy = root / ".idea-realization" / "schemas" / "backlog.schema.json"
    states = {path: state for state, path, _ in doctor.diagnose(root, config, plugin)}
    assert states[".idea-realization/schemas/backlog.schema.json"] == "stale"
    copy.write_text('{"version": 2}\n')
    states = {path: state for state, path, _ in doctor.diagnose(root, config, plugin)}
    assert states[".idea-realization/schemas/backlog.schema.json"] == "unrecorded"
    lines = scaffold.scaffold(config, ["backlog"], plugin_root=plugin, refresh_schemas=True)
    assert "recorded  .idea-realization/schemas/backlog.schema.json" in lines
    states = {path: state for state, path, _ in doctor.diagnose(root, config, plugin)}
    assert states[".idea-realization/schemas/backlog.schema.json"] == "unchanged"


def test_a_record_without_owners_is_read_by_path(tmp_path: Path) -> None:
    """Install-state records written before owners were recorded still classify correctly."""
    config = paths.resolve({"root": str(tmp_path)}, env={})
    scaffold.scaffold(config, ["backlog"])
    state_path = tmp_path / scaffold.RECORD
    state = json.loads(state_path.read_text())
    for entry in state["files"]:
        del entry["owner"]
    state_path.write_text(json.dumps(state))
    (tmp_path / "backlog" / "backlog.yaml").write_text("items: []\n")
    copy = tmp_path / ".idea-realization" / "schemas" / "backlog.schema.json"
    copy.write_text("{}\n")
    states = {path: state for state, path, _ in doctor.diagnose(tmp_path, config)}
    assert states["backlog/backlog.yaml"] == "edited"
    assert states[".idea-realization/schemas/backlog.schema.json"] == "stale"


def test_a_missing_gitignored_directory_is_absent_not_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A fresh clone never has the gitignored staging directory."""
    git(tmp_path, "init", "-q")
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["partition"],
                      consent=["gitignore"])
    (tmp_path / ".idea-realization" / "staging").rmdir()
    assert doctor.main(["--root", str(tmp_path)]) == 0
    assert ("absent    .idea-realization/staging/  (partition, gitignored; the scaffold "
            "recreates it)") in capsys.readouterr().out
    (tmp_path / ".gitignore").write_text("")
    assert doctor.main(["--root", str(tmp_path)]) == 1
    assert "missing   .idea-realization/staging/" in capsys.readouterr().out
