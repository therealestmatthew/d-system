# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""The one place a script resolves a configured value.

Every key is resolved with one precedence:

1. a command-line flag (``--ideas-path``),
2. the environment variable ``IDEA_REALIZATION_<KEY>``,
3. the plugin option ``CLAUDE_PLUGIN_OPTION_<KEY>``,
4. the default declared in ``.claude-plugin/plugin.json``.

Claude Code exports ``CLAUDE_PLUGIN_OPTION_<KEY>`` to hooks only. A skill passes the saved option
to a script by prefixing the command with ``CLAUDE_PLUGIN_OPTION_<KEY>='${user_config.<key>}'``,
single-quoted because the shell rejects the unsubstituted text inside double quotes.
When the option was never saved, Claude Code leaves that text unsubstituted, so a value that still
reads ``${user_config.`` counts as unset.

Relative paths resolve against the repository root: ``--root``, then ``IDEA_REALIZATION_ROOT``,
then ``CLAUDE_PROJECT_DIR``, then the git top level of the working directory, then the working
directory. No path is ever derived from a script's own location except the plugin's own files.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
UNSUBSTITUTED = "${user_config."
ROOT_ENV = "IDEA_REALIZATION_ROOT"


@dataclass(frozen=True)
class Key:
    name: str
    kind: str  # "path", "paths" or "text"
    default: str | list[str]
    description: str

    @property
    def flag(self) -> str:
        return "--" + self.name.replace("_", "-")

    @property
    def env(self) -> str:
        return "IDEA_REALIZATION_" + self.name.upper()

    @property
    def option_env(self) -> str:
        return "CLAUDE_PLUGIN_OPTION_" + self.name.upper()


#: Keys that hold plain text rather than a path. A ``multiple`` key is a list of paths.
TEXT_KEYS = {"integration_branch"}


def load_keys(manifest: Path = MANIFEST) -> dict[str, Key]:
    """Read every configurable key and its default from the manifest's ``userConfig``."""
    config = json.loads(manifest.read_text(encoding="utf-8"))["userConfig"]
    keys = {}
    for name, spec in config.items():
        kind = "paths" if spec.get("multiple") else "text" if name in TEXT_KEYS else "path"
        keys[name] = Key(name, kind, spec.get("default", [] if kind == "paths" else ""),
                         spec["description"])
    return keys


KEYS = load_keys()


def add_arguments(parser: argparse.ArgumentParser, names: Sequence[str] | None = None) -> None:
    """Add ``--root`` and one flag per key (all keys when ``names`` is None)."""
    parser.add_argument("--root", help=f"repository root (env {ROOT_ENV}; default: git top level)")
    for name in names if names is not None else KEYS:
        key = KEYS[name]
        default = ",".join(key.default) if isinstance(key.default, list) else key.default
        extra = " (comma-separated)" if key.kind == "paths" else ""
        parser.add_argument(
            key.flag, dest=name, default=None,
            help=f"{key.description}{extra} Env {key.env}, then {key.option_env}; "
                 f"default {default!r}.",
        )


def _set(value: str | None) -> bool:
    return value is not None and value != "" and UNSUBSTITUTED not in value


def raw_value(name: str, flags: Mapping[str, str | None] | None = None,
              env: Mapping[str, str] | None = None) -> str | list[str]:
    """Return a key's value before path resolution, following the four-level precedence."""
    key = KEYS[name]
    env = os.environ if env is None else env
    for candidate in ((flags or {}).get(name), env.get(key.env), env.get(key.option_env)):
        if _set(candidate):
            assert candidate is not None
            if key.kind == "paths":
                return [part.strip() for part in candidate.split(",") if part.strip()]
            return candidate
    return list(key.default) if isinstance(key.default, list) else key.default


def repository_root(flag: str | None = None, env: Mapping[str, str] | None = None,
                    cwd: Path | None = None) -> Path:
    """Resolve the repository root that relative paths are taken from."""
    env = os.environ if env is None else env
    cwd = Path.cwd() if cwd is None else cwd
    for candidate in (flag, env.get(ROOT_ENV), env.get("CLAUDE_PROJECT_DIR")):
        if _set(candidate):
            assert candidate is not None
            return Path(candidate).expanduser().resolve()
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd,
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return cwd.resolve()
    return Path(top).resolve()


def _to_path(root: Path, value: str) -> Path:
    value = value.replace("<repository>", root.name)
    path = Path(value).expanduser()
    return path if path.is_absolute() else (root / path)


@dataclass(frozen=True)
class Config:
    """Resolved configuration: the root plus every key."""

    root: Path
    values: Mapping[str, str | list[str]]

    def path(self, name: str) -> Path:
        value = self.values[name]
        assert isinstance(value, str) and KEYS[name].kind == "path", name
        return _to_path(self.root, value)

    def paths(self, name: str) -> list[Path]:
        value = self.values[name]
        assert isinstance(value, list), name
        return [_to_path(self.root, item) for item in value]

    def text(self, name: str) -> str:
        value = self.values[name]
        assert isinstance(value, str), name
        return value


def resolve(args: argparse.Namespace | Mapping[str, str | None] | None = None,
            env: Mapping[str, str] | None = None, cwd: Path | None = None) -> Config:
    """Resolve every key from parsed arguments, the environment and the manifest defaults."""
    flags: Mapping[str, str | None]
    if args is None:
        flags = {}
    elif isinstance(args, argparse.Namespace):
        flags = vars(args)
    else:
        flags = args
    root = repository_root(flags.get("root"), env, cwd)
    return Config(root, {name: raw_value(name, flags, env) for name in KEYS})


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print every resolved configuration value.")
    add_arguments(parser)
    config = resolve(parser.parse_args(argv))
    print(f"root: {config.root}")
    for name, key in KEYS.items():
        if key.kind == "path":
            print(f"{name}: {config.path(name)}")
        elif key.kind == "paths":
            print(f"{name}: {', '.join(str(p) for p in config.paths(name))}")
        else:
            print(f"{name}: {config.text(name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
