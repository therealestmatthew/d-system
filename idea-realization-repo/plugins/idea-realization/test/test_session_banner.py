"""The session banner prints the resolved configuration and the mode menu, and never fails.

Dates are built at run time so this file carries no calendar date literally.
"""

from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import session_banner
from conftest import SCRIPTS, as_developer

TODAY = datetime.date(2030, 1, 1)
DEMO = TODAY + datetime.timedelta(days=10)
FREEZE = TODAY + datetime.timedelta(days=8)


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True)


@pytest.fixture
def control(tmp_path: Path) -> Path:
    """A control checkout with a project record, one developer and a product checkout."""
    root = tmp_path / "control"
    root.mkdir()
    git(root, "init", "-q")
    (root / ".idea-realization").mkdir()
    (root / ".idea-realization" / "project.yaml").write_text(
        "schema_version: 1\n"
        "control:\n  remote: REPLACE-WITH-THE-CONTROL-REPOSITORY-GIT-URL\n"
        "  integration_branch: dev\n"
        f"demo:\n  date: '{DEMO.isoformat()}'\n  freeze: '{FREEZE.isoformat()}'\n"
        "  tag_prefix: demo-\n")
    (root / "docs").mkdir()
    (root / "docs" / "systems.yaml").write_text(
        "owners:\n  ana:\n    description: A developer.\n    emails: [ana@example.com]\n")
    (tmp_path / "product").mkdir()
    return root


def lines(capsys: pytest.CaptureFixture[str], *argv: str) -> list[str]:
    assert session_banner.main(list(argv)) == 0
    return capsys.readouterr().out.splitlines()


def test_prints_every_field(control: Path, monkeypatch: pytest.MonkeyPatch,
                            capsys: pytest.CaptureFixture[str]) -> None:
    as_developer(monkeypatch, "ana")
    monkeypatch.setenv("IDEA_REALIZATION_PRODUCT_ROOT", str(control.parent / "product"))
    out = lines(capsys, "--root", str(control), "--today", TODAY.isoformat())
    assert out[0] == f"idea-realization session: {control.resolve()}"
    assert "integration branch: dev (from project.yaml)" in out
    assert f"product root: {(control.parent / 'product').resolve()}" in out
    assert "handle: ana" in out
    assert f"demo date: {DEMO.isoformat()} (10 days left)" in out
    assert f"code freeze: {FREEZE.isoformat()} (8 days left)" in out
    assert out[-1] == session_banner.MENU
    assert "Run /start to pick a mode" in session_banner.MENU


def test_unset_product_root_and_unresolved_handle_are_reported(
        control: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    as_developer(monkeypatch, "bob")
    monkeypatch.delenv("IDEA_REALIZATION_PRODUCT_ROOT", raising=False)
    monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_PRODUCT_ROOT", raising=False)
    out = lines(capsys, "--root", str(control), "--today", TODAY.isoformat())
    assert "product root: not set on this machine" in out
    handle = next(line for line in out if line.startswith("handle: "))
    assert handle.startswith("handle: (unavailable: ")


def test_past_and_present_days(control: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = lines(capsys, "--root", str(control), "--today", DEMO.isoformat())
    assert f"demo date: {DEMO.isoformat()} (today)" in out
    assert f"code freeze: {FREEZE.isoformat()} (2 days ago)" in out


def test_exits_zero_with_missing_config(tmp_path: Path,
                                        capsys: pytest.CaptureFixture[str]) -> None:
    out = lines(capsys, "--root", str(tmp_path))
    assert any(line.startswith("demo date: (unavailable: ") for line in out)
    assert any(line.startswith("code freeze: (unavailable: ") for line in out)
    assert out[-1] == session_banner.MENU


def test_exits_zero_with_an_invalid_config(control: Path,
                                           capsys: pytest.CaptureFixture[str]) -> None:
    (control / ".idea-realization" / "project.yaml").write_text("control: [not, a, map\n")
    out = lines(capsys, "--root", str(control))
    assert len(out) == 2 and out[0].startswith("idea-realization session banner unavailable: ")
    assert out[1] == session_banner.MENU


def test_exits_zero_on_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert session_banner.main(["--no-such-flag"]) == 0
    assert session_banner.main(["--today", "not-a-date"]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == session_banner.MENU


def test_hook_output_is_session_start_json(control: Path,
                                           capsys: pytest.CaptureFixture[str]) -> None:
    assert session_banner.main(["--root", str(control), "--hook"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert printed["systemMessage"] == printed["hookSpecificOutput"]["additionalContext"]
    assert printed["systemMessage"].endswith(session_banner.MENU)


def test_exits_zero_when_the_plugin_modules_cannot_load(tmp_path: Path) -> None:
    """Run alone, with no paths.py beside it, the script still prints the menu and exits 0."""
    alone = tmp_path / "alone"
    alone.mkdir()
    shutil.copy(SCRIPTS / "session_banner.py", alone / "session_banner.py")
    result = subprocess.run([sys.executable, str(alone / "session_banner.py"), "--root",
                             str(tmp_path)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    out = result.stdout.splitlines()
    assert out[0].startswith("idea-realization session banner unavailable: ")
    assert out[-1] == session_banner.MENU

