"""The brain feature: the team's shared memory. ``brain.py`` holds the rules and commands."""

from __future__ import annotations

import paths

import brain

COMMANDS = brain.COMMANDS


def check(config: paths.Config) -> list[str]:
    return brain.problems(config)
