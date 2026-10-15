"""The project settings load the plugin from this repository's own marketplace.

A plain ``claude`` started in the repository registers the marketplace that
``extraKnownMarketplaces`` declares and enables the plugin that ``enabledPlugins`` names, so the
names in the settings, the marketplace file and the plugin's manifest must agree.
"""

from __future__ import annotations

import json
from pathlib import Path

IRR = Path(__file__).resolve().parent.parent


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_settings_enable_the_plugin_from_the_repositorys_marketplace() -> None:
    settings = _json(IRR / ".claude" / "settings.json")
    marketplace = _json(IRR / ".claude-plugin" / "marketplace.json")
    name = marketplace["name"]
    assert settings["extraKnownMarketplaces"] == {
        name: {"source": {"source": "directory", "path": "./"}}}
    [entry] = marketplace["plugins"]
    plugin = _json(IRR / entry["source"] / ".claude-plugin" / "plugin.json")
    assert entry["name"] == plugin["name"] == "idea-realization"
    assert settings["enabledPlugins"] == {f"{plugin['name']}@{name}": True}


def test_the_launch_docs_use_a_plain_claude() -> None:
    for doc in ("ONBOARDING.md", "README.md", "docs/guides/OPS-010-day-one-prompts.md"):
        assert "--plugin-dir" not in (IRR / doc).read_text(encoding="utf-8"), doc
