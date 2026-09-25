# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Check what the plugin's scripts need on this machine, and install what is missing on --yes.

Checks Python 3.12 or later, ``uv`` and ``git``; with ``--feature triage`` or ``--feature
partition`` also the ``claude`` CLI. Each missing item is reported with the exact command that
installs it. Without ``--yes`` nothing is installed and no file is changed.

Uses only the standard library, so it runs with a bare ``python3`` on a machine without ``uv``.

Exit codes: 0 when everything required is present, 1 when something is still missing.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass

MINIMUM_PYTHON = (3, 12)
#: Features whose workflows need the ``claude`` CLI on PATH.
CLAUDE_FEATURES = {"triage", "partition"}

UV_INSTALL = {
    "windows": 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"',
    "other": "curl -LsSf https://astral.sh/uv/install.sh | sh",
}
GIT_INSTALL = {
    "windows": "winget install --id Git.Git -e --source winget",
    "darwin": "xcode-select --install",
    "apt-get": "sudo apt-get install -y git",
    "dnf": "sudo dnf install -y git",
    "pacman": "sudo pacman -S --noconfirm git",
    "other": "see https://git-scm.com/downloads",
}
CLAUDE_INSTALL = {
    "windows": 'powershell -ExecutionPolicy ByPass -c "irm https://claude.ai/install.ps1 | iex"',
    "other": "curl -fsSL https://claude.ai/install.sh | bash",
}


@dataclass(frozen=True)
class Item:
    name: str
    present: bool
    detail: str
    install: str
    required: bool


Which = Callable[[str], str | None]


def system_name() -> str:
    system = platform.system().lower()
    return "windows" if system.startswith("win") else system


def git_install(which: Which, system: str) -> str:
    if system in {"windows", "darwin"}:
        return GIT_INSTALL[system]
    for manager in ("apt-get", "dnf", "pacman"):
        if which(manager):
            return GIT_INSTALL[manager]
    return GIT_INSTALL["other"]


def survey(features: Sequence[str], which: Which = shutil.which,
           version: tuple[int, int] = (sys.version_info[0], sys.version_info[1]),
           system: str | None = None) -> list[Item]:
    """Report every prerequisite. Reads PATH and the interpreter version; changes nothing."""
    system = system or system_name()
    shell_key = "windows" if system == "windows" else "other"
    uv = which("uv")
    items = [
        Item("python", version >= MINIMUM_PYTHON, "{}.{}".format(*version),
             f"uv python install {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}", True),
        Item("uv", uv is not None, uv or "not on PATH", UV_INSTALL[shell_key], True),
    ]
    git = which("git")
    items.append(Item("git", git is not None, git or "not on PATH", git_install(which, system),
                      True))
    claude = which("claude")
    items.append(Item("claude", claude is not None, claude or "not on PATH",
                      CLAUDE_INSTALL[shell_key], bool(CLAUDE_FEATURES & set(features))))
    return items


def report(items: Sequence[Item]) -> list[str]:
    lines = []
    for item in items:
        if item.present:
            lines.append(f"ok       {item.name:<7} {item.detail}")
        else:
            label = "missing " if item.required else "optional"
            lines.append(f"{label} {item.name:<7} {item.detail}; install: {item.install}")
    return lines


def missing(items: Sequence[Item]) -> list[Item]:
    return [item for item in items if item.required and not item.present]


Runner = Callable[[str], int]


def run_shell(command: str) -> int:
    return subprocess.run(command, shell=True, check=False).returncode


def main(argv: Sequence[str] | None = None, which: Which = shutil.which,
         runner: Runner = run_shell) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--feature", action="append", default=[],
                        choices=["ideas", "triage", "partition", "backlog", "documents", "all"],
                        help="the features that will be used; triage and partition need claude")
    parser.add_argument("--yes", action="store_true",
                        help="install every missing required item; without it nothing is installed")
    args = parser.parse_args(argv)
    features = sorted(CLAUDE_FEATURES) if "all" in args.feature else args.feature
    items = survey(features, which)
    print("\n".join(report(items)))
    absent = missing(items)
    if not absent:
        return 0
    if not args.yes:
        print(f"{len(absent)} required item(s) missing; nothing was installed. "
              "Re-run with --yes to install them.")
        return 1
    # uv first: the Python install command runs through uv.
    order = {"uv": 0, "git": 1, "python": 2, "claude": 3}
    for item in sorted(absent, key=lambda entry: order[entry.name]):
        if item.install.startswith("see "):
            print(f"cannot install {item.name} automatically: {item.install}")
            continue
        print(f"installing {item.name}: {item.install}")
        code = runner(item.install)
        if code:
            print(f"install of {item.name} exited {code}")
    after = missing(survey(features, which))
    for item in after:
        print(f"still missing {item.name}; a new shell may be needed for PATH to update")
    return 1 if after else 0


if __name__ == "__main__":
    raise SystemExit(main())
