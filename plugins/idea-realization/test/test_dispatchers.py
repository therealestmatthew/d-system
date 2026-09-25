"""check.py and cli.py find feature modules in scripts/checks/ without being edited."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from conftest import PLUGIN_ROOT

FEATURE = '''
COMMANDS = {"hello": ("say hello", lambda argv: print("hello", *argv) or 0)}


def check(config):
    marker = config.root / "broken"
    return [f"{marker.name} exists"] if marker.exists() else []
'''


def plugin_copy(tmp_path: Path, feature: bool = True) -> Path:
    copy = tmp_path / "plugin"
    shutil.copytree(PLUGIN_ROOT / "scripts", copy / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(PLUGIN_ROOT / ".claude-plugin", copy / ".claude-plugin")
    if feature:
        (copy / "scripts" / "checks" / "sample.py").write_text(FEATURE)
    return copy


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True,
                          check=False)


def test_check_runs_a_new_feature_module(tmp_path: Path) -> None:
    copy = plugin_copy(tmp_path)
    target = tmp_path / "target"
    target.mkdir()
    clean = run(copy / "scripts" / "check.py", "--root", str(target))
    assert clean.returncode == 0 and "sample: OK" in clean.stdout
    (target / "broken").write_text("")
    broken = run(copy / "scripts" / "check.py", "--root", str(target))
    assert broken.returncode == 1 and "sample: broken exists" in broken.stdout


def test_check_rejects_an_unknown_feature(tmp_path: Path) -> None:
    copy = plugin_copy(tmp_path)
    result = run(copy / "scripts" / "check.py", "--feature", "absent", "--root", str(tmp_path))
    assert result.returncode == 2


def test_cli_dispatches_a_new_command(tmp_path: Path) -> None:
    copy = plugin_copy(tmp_path)
    result = run(copy / "scripts" / "cli.py", "hello", "there")
    assert result.returncode == 0 and result.stdout.strip() == "hello there"
    assert "hello" in run(copy / "scripts" / "cli.py", "--help").stdout
    assert run(copy / "scripts" / "cli.py", "absent").returncode == 2


def test_no_features_is_clean(tmp_path: Path) -> None:
    copy = plugin_copy(tmp_path, feature=False)
    result = run(copy / "scripts" / "check.py", "--root", str(tmp_path))
    assert result.returncode == 0
