"""The manifest validates under --strict, carries no licence, and --strict catches unknown keys."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import PLUGIN_ROOT

MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
needs_claude = pytest.mark.skipif(shutil.which("claude") is None,
                                  reason="the claude CLI validates the manifest")


def validate(plugin: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["claude", "plugin", "validate", str(plugin), "--strict"],
                          capture_output=True, text=True, check=False)


def test_manifest_names_the_plugin_and_has_no_licence() -> None:
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["name"] == "idea-realization"
    assert "license" not in manifest


def test_component_directories_exist() -> None:
    for name in ("skills", "agents", "scripts", "schemas", "templates", "docs"):
        assert (PLUGIN_ROOT / name).is_dir(), name


@needs_claude
def test_manifest_passes_strict_validation() -> None:
    result = validate(PLUGIN_ROOT)
    assert result.returncode == 0, result.stdout + result.stderr


@needs_claude
def test_unknown_top_level_key_fails_strict(tmp_path: Path) -> None:
    copy = tmp_path / "plugin"
    (copy / ".claude-plugin").mkdir(parents=True)
    manifest = json.loads(MANIFEST.read_text())
    manifest["unexpected"] = True
    (copy / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest))
    result = validate(copy)
    assert result.returncode != 0, result.stdout
    assert "unexpected" in result.stdout + result.stderr
