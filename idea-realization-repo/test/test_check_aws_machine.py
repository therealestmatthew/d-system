"""tools/check_aws_machine.py: the machine rule's file and environment checks."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import check_aws_machine as machine


def home_with(tmp_path: Path, config: str = "", credentials: str = "") -> dict[str, str]:
    (tmp_path / ".aws").mkdir()
    (tmp_path / ".aws" / "config").write_text(config, encoding="utf-8")
    (tmp_path / ".aws" / "credentials").write_text(credentials, encoding="utf-8")
    return {"HOME": str(tmp_path)}


def test_named_sandbox_profiles_only_pass(tmp_path: Path) -> None:
    env = home_with(tmp_path, config="[profile sandbox-read]\nregion = us-east-1\n"
                                     "[profile sandbox-deploy]\nregion = us-east-1\n")
    assert machine.static_findings(env) == []


def test_default_profile_in_config_is_found(tmp_path: Path) -> None:
    env = home_with(tmp_path, config="[profile default]\nregion = us-east-1\n")
    assert any("has a default profile" in f for f in machine.static_findings(env))


def test_default_section_in_credentials_is_found(tmp_path: Path) -> None:
    env = home_with(tmp_path, credentials="[default]\naws_access_key_id = x\n")
    assert any("credentials has a default profile" in f for f in machine.static_findings(env))


def test_ambient_variables_are_found(tmp_path: Path) -> None:
    env = {**home_with(tmp_path), "AWS_ACCESS_KEY_ID": "x",
           "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI": "/v2/creds"}
    findings = machine.static_findings(env)
    assert any(f.startswith("AWS_ACCESS_KEY_ID") for f in findings)
    assert any(f.startswith("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI") for f in findings)


def test_no_aws_directory_passes(tmp_path: Path) -> None:
    assert machine.static_findings({"HOME": str(tmp_path)}) == []


def test_configured_file_locations_are_used(tmp_path: Path) -> None:
    other = tmp_path / "elsewhere"
    other.write_text("[default]\n", encoding="utf-8")
    env = {"HOME": str(tmp_path), "AWS_CONFIG_FILE": str(other)}
    assert any(str(other) in f for f in machine.static_findings(env))


def clean_machine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, path: str) -> None:
    """A machine with no ambient credentials, no metadata service and only ``path`` on PATH."""
    for name in list(machine.os.environ):
        if name.startswith("AWS_"):
            monkeypatch.delenv(name)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("PATH", path)
    monkeypatch.setattr(machine, "instance_metadata_reachable", lambda: False)


def test_probe_without_the_aws_cli_is_not_reported_ok(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    clean_machine(tmp_path, monkeypatch, path="")
    assert machine.main(["--probe"]) == 2
    out = capsys.readouterr().out
    assert "NOT CHECKED" in out and "AWS CLI" in out and "OK" not in out


def test_without_probe_a_missing_aws_cli_still_passes(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    clean_machine(tmp_path, monkeypatch, path="")
    assert machine.main([]) == 0
    assert "check_aws_machine: OK" in capsys.readouterr().out


def test_an_ambient_finding_outranks_a_skipped_probe(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    clean_machine(tmp_path, monkeypatch, path="")
    monkeypatch.setenv("AWS_PROFILE", "default")
    assert machine.main(["--probe"]) == 1
    assert "ambient AWS credentials found" in capsys.readouterr().out


def test_probe_with_the_aws_cli_asks_the_default_chain(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "aws"
    fake.write_text("#!/bin/sh\nexit 255\n")
    fake.chmod(0o755)
    clean_machine(tmp_path, monkeypatch, path=str(bin_dir))
    assert machine.main(["--probe"]) == 0
    assert "check_aws_machine: OK" in capsys.readouterr().out
