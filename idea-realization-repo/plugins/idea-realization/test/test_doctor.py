"""The doctor names drifted and missing files, exits 1, and changes nothing."""

from __future__ import annotations

from pathlib import Path

import doctor
import paths
import pytest
import scaffold


def listing(root: Path) -> dict[str, bytes | None]:
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None)
            for p in sorted(root.rglob("*"))}


def test_doctor_reports_drift_and_missing(tmp_path: Path, capsys: object) -> None:
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["ideas", "backlog"])
    (tmp_path / "ideas" / "priority.yaml").write_text("edited\n")
    (tmp_path / "backlog" / "backlog.yaml").unlink()
    before = listing(tmp_path)
    assert doctor.main(["--root", str(tmp_path)]) == 1
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "drifted   ideas/priority.yaml" in output
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


def test_an_edit_without_consent_is_still_drift(tmp_path: Path,
                                                capsys: pytest.CaptureFixture[str]) -> None:
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["product"])
    product = tmp_path / ".idea-realization" / "product.yaml"
    product.write_text(product.read_text() + "github: team/x\n")
    assert doctor.main(["--root", str(tmp_path)]) == 1
    assert "drifted   .idea-realization/product.yaml" in capsys.readouterr().out


def test_doctor_reports_a_control_origin_that_is_not_project_yaml_remote(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    git(tmp_path, "init", "-q")
    git(tmp_path, "remote", "add", "origin", "git@forge.example.com:team/control.git")
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["project"],
                      consent=["edit"])
    project = tmp_path / ".idea-realization" / "project.yaml"
    text = project.read_text()
    project.write_text(text.replace("REPLACE-WITH-THE-CONTROL-REPOSITORY-GIT-URL",
                                    "https://forge.example.com/team/control"))
    assert doctor.main(["--root", str(tmp_path)]) == 0
    assert "origin    matches" in capsys.readouterr().out
    project.write_text(text.replace("REPLACE-WITH-THE-CONTROL-REPOSITORY-GIT-URL",
                                    "git@forge.example.com:team/other.git"))
    assert doctor.main(["--root", str(tmp_path)]) == 1
    assert "not the control repository" in capsys.readouterr().out


def test_an_invalid_project_yaml_exits_two_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    scaffold.scaffold(paths.resolve({"root": str(tmp_path)}, env={}), ["project"])
    (tmp_path / ".idea-realization" / "project.yaml").write_text("schema_version: 2\n")
    assert doctor.main(["--root", str(tmp_path)]) == 2
    assert "project.yaml" in capsys.readouterr().err
