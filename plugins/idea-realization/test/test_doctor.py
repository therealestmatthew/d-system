"""The doctor names drifted and missing files, exits 1, and changes nothing."""

from __future__ import annotations

from pathlib import Path

import pytest

import doctor
import paths
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


# --- REQ-035 R07: doctor reports every invalid key --------------------------------------------


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
