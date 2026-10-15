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


def test_skills_that_remove_a_next_up_entry_say_to_write_an_empty_list() -> None:
    # Deleting the last `- phase-...` line under `next_up:` leaves `next_up: null`, which the
    # backlog schema refuses; every skill that removes an entry says what to write instead.
    for name in ("session-close", "checkpoint"):
        text = (PLUGIN_ROOT / "skills" / name / "SKILL.md").read_text()
        assert "`next_up: []`" in text, name


def test_session_start_updates_the_product_checkout_before_orientation() -> None:
    # Orientation runs the check, which reads the product checkout; pulling only the control
    # checkout first leaves a peer's merged product work invisible to it (workflow-sim M4).
    text = (PLUGIN_ROOT / "skills" / "session-start" / "SKILL.md").read_text()
    before_orientation = text.split("**Pull before anything else.**", 1)[1].split("## 1.", 1)[0]
    assert "git -C <product checkout> fetch origin" in before_orientation
    assert "git -C <product checkout> merge --ff-only origin/<product integration branch>" in (
        before_orientation)
