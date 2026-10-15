"""The project settings run the plugin's session banner when a session starts."""

from __future__ import annotations

import json
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parent.parent


def test_session_start_runs_the_banner() -> None:
    settings = json.loads((REPOSITORY / ".claude" / "settings.json").read_text())
    commands = [hook["command"] for entry in settings["hooks"]["SessionStart"]
                for hook in entry["hooks"]]
    assert any("/plugins/idea-realization/scripts/session_banner.py" in command
               and "--hook" in command for command in commands)
    assert (REPOSITORY / "plugins" / "idea-realization" / "scripts" / "session_banner.py").is_file()
