"""Skills pass saved options in a form the shell accepts when the option was never saved."""

from __future__ import annotations

import re

from conftest import PLUGIN_ROOT

SKILLS = sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md"))


def test_every_skill_has_a_name_and_description() -> None:
    assert SKILLS
    for skill in SKILLS:
        front = skill.read_text().split("---")[1]
        assert f"name: {skill.parent.name}" in front, skill
        assert "description: " in front, skill


def test_no_option_is_double_quoted() -> None:
    # Unsubstituted, "${user_config.x}" is a shell "bad substitution" error.
    for skill in SKILLS:
        assert not re.search(r'"\$\{user_config\.', skill.read_text()), skill


def test_scripts_are_reached_through_the_plugin_root() -> None:
    for skill in SKILLS:
        for line in skill.read_text().splitlines():
            if "scripts/" in line and ("uv run" in line or "python3" in line):
                assert "${CLAUDE_PLUGIN_ROOT}/scripts/" in line, (skill, line)
