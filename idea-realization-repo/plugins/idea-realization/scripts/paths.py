# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""The one place a script resolves a configured value.

Every key is resolved with one precedence:

1. a command-line flag (``--ideas-path``),
2. the environment variable ``IDEA_REALIZATION_<KEY>``,
3. this machine's ``.idea-realization/local.yaml`` (untracked),
4. the plugin option ``CLAUDE_PLUGIN_OPTION_<KEY>``,
5. the tracked ``.idea-realization/project.yaml`` or ``.idea-realization/product.yaml``, for the
   keys they carry,
6. the default declared in ``.claude-plugin/plugin.json``, or, where that default is empty, the
   built-in fallback in ``FALLBACKS``.

``integration_branch`` declares an empty default and falls back to ``main``. Claude Code can save a
plugin option with its declared default even when the developer never chose it, and a saved option
(level 4) outranks ``project.yaml`` (level 5). An empty default saves as an empty option, which
counts as unset, so the team's ``control.integration_branch`` in ``project.yaml`` still applies.

``local.yaml`` is gitignored and holds what differs per machine: a flat map of key to value for
the keys ``schemas/local.schema.json`` allows. It is read from the primary checkout, the first
entry of ``git worktree list``, at the same place relative to the git top level as the root, so
every session worktree sees the one file. ``local.example.yaml`` is its tracked template.

``project.yaml`` is tracked and holds what the whole team shares (``schemas/project.schema.json``):
``control.integration_branch`` supplies ``integration_branch``, ``aws.region`` supplies
``aws_region``, and the optional ``control.remote`` and ``control.github`` supply
``control_remote`` and ``control_github``. Its other values (the demo dates, the team URLs) are
read by ``project.py``. A value in either file that starts with ``REPLACE-WITH-`` is a placeholder
and counts as unset. A file that fails its schema raises ``PathError`` naming the file.

The repository URLs are keys like any other, because a team may not be allowed to track them (a
URL can name a confidential organization). ``control_remote`` and ``control_github`` name the
control repository; ``product_remote`` and ``product_github`` name the product repository, and
fall back to the optional ``remote`` and ``github`` of the tracked ``product.yaml``. Each machine
sets the real values in its ``local.yaml`` (or ``IDEA_REALIZATION_<KEY>``). A ``*_github`` value
must be ``<org>/<repo>``; a ``*_remote`` value must contain no whitespace.

Claude Code exports ``CLAUDE_PLUGIN_OPTION_<KEY>`` to hooks only. A skill passes the saved option
to a script by prefixing the command with ``CLAUDE_PLUGIN_OPTION_<KEY>='${user_config.<key>}'``,
single-quoted because the shell rejects the unsubstituted text inside double quotes.
When the option was never saved, Claude Code leaves that text unsubstituted, so a value that still
reads ``${user_config.`` counts as unset.

Relative paths resolve against the repository root: ``--root``, then ``IDEA_REALIZATION_ROOT``,
then the git top level of the working directory, then ``CLAUDE_PROJECT_DIR``, then the working
directory. A command run inside a worktree therefore resolves that worktree even when
``CLAUDE_PROJECT_DIR`` names the primary checkout. The one case where ``CLAUDE_PROJECT_DIR``
comes before the git top level is a project directory inside that working tree (a repository kept
in a subdirectory of another one) with the command run inside the project directory. No path is
ever derived from a script's own location except the plugin's own files.

``worktree_dir`` is the exception: it names a directory beside the repository rather than a file
in one checkout, so it resolves against the primary checkout, the first entry of
``git worktree list``, and ``<repository>`` in it is the primary checkout's directory name. Run
from any worktree, it names the same directory.

Every value is validated when it is read, and a bad one raises ``PathError`` naming the key. A path
key, and every entry of a list key, must resolve, after following symlinks and collapsing ``..``,
inside the root it is taken from, with no ``.git`` component; an absolute path inside the root is
kept. ``worktree_dir`` must resolve outside the primary checkout. ``integration_branch`` must not
start with ``-`` and must pass ``git check-ref-format --branch``. Each script's ``main`` turns a
``PathError`` into exit 2 with its message (``exits_on_path_error``).

``product_root`` and ``product_worktree_dir`` name the product repository this control repository
drives (see ``product.py``). They differ per machine, may be unset, and must resolve outside the
control repository. ``product_worktree_dir`` resolves against the product checkout, and
``<product>`` in it is the product checkout's directory name. ``aws_read_profile``,
``aws_deploy_profile`` and ``aws_region`` are plain text, may be unset, and are read by the cloud
agents, which refuse to run without them.

``handle`` asserts this machine's developer handle (``identity.py`` still requires the git email
to match it) and ``dev_port_range`` names the local ports a developer server may use, as
``<first>-<last>``. Both are plain text and may be unset.

``paths.py`` prints every resolved value; ``paths.py show`` also prints where each one came from.
"""

from __future__ import annotations

import argparse
import dataclasses
import functools
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft7Validator

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
UNSUBSTITUTED = "${user_config."
ROOT_ENV = "IDEA_REALIZATION_ROOT"
PLACEHOLDER = "REPLACE-WITH-"
LOCAL_RECORD = Path(".idea-realization") / "local.yaml"
PROJECT_RECORD = Path(".idea-realization") / "project.yaml"
PRODUCT_RECORD = Path(".idea-realization") / "product.yaml"

#: Keys ``project.yaml`` supplies, and where in it each one sits.
PROJECT_KEYS = {"integration_branch": ("control", "integration_branch"),
                "aws_region": ("aws", "region"),
                "control_remote": ("control", "remote"),
                "control_github": ("control", "github")}

#: Keys ``product.yaml`` supplies, and the field of it each one is.
PRODUCT_RECORD_KEYS = {"product_remote": "remote", "product_github": "github"}

#: Keys naming a repository on its forge, as ``<org>/<repo>``.
GITHUB_KEYS = {"control_github", "product_github"}
GITHUB_SLUG = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


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
TEXT_KEYS = {"integration_branch", "aws_read_profile", "aws_deploy_profile", "aws_region",
             "handle", "dev_port_range", "control_remote", "control_github", "product_remote",
             "product_github"}

#: Keys that resolve against the primary checkout rather than the current one.
PRIMARY_KEYS = {"worktree_dir"}

#: Keys that locate the product repository; they may be unset and resolve outside this repository.
PRODUCT_KEYS = {"product_root", "product_worktree_dir"}

#: The value a key takes when nothing sets it and its manifest default is empty. A manifest default
#: would be saved as a plugin option and outrank ``project.yaml``; this one never is.
FALLBACKS = {"integration_branch": "main"}


def load_keys(manifest: Path = MANIFEST) -> dict[str, Key]:
    """Read every configurable key and its default from the manifest's ``userConfig``."""
    config = json.loads(manifest.read_text(encoding="utf-8"))["userConfig"]
    keys = {}
    for name, spec in config.items():
        kind = "paths" if spec.get("multiple") else "text" if name in TEXT_KEYS else "path"
        default = spec.get("default", [] if kind == "paths" else "")
        if not default and name in FALLBACKS:
            default = FALLBACKS[name]
        keys[name] = Key(name, kind, default, spec["description"])
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
    return (value is not None and value != "" and UNSUBSTITUTED not in value
            and not value.startswith(PLACEHOLDER))


def raw_source(name: str, flags: Mapping[str, str | None] | None = None,
               env: Mapping[str, str] | None = None, local: Mapping[str, str] | None = None,
               project: Mapping[str, str] | None = None) -> tuple[str | list[str], str]:
    """Return a key's value before path resolution and the source it came from, following the
    six-level precedence. ``local`` is the keys read from ``local.yaml``; ``project`` is the keys
    read from the tracked files (``project.yaml`` and ``product.yaml``)."""
    key = KEYS[name]
    env = os.environ if env is None else env
    tracked = PRODUCT_RECORD.name if name in PRODUCT_RECORD_KEYS else PROJECT_RECORD.name
    candidates = (((flags or {}).get(name), key.flag), (env.get(key.env), key.env),
                  ((local or {}).get(name), LOCAL_RECORD.name),
                  (env.get(key.option_env), key.option_env),
                  ((project or {}).get(name), tracked))
    for candidate, source in candidates:
        if _set(candidate):
            assert candidate is not None
            if key.kind == "paths":
                return [part.strip() for part in candidate.split(",") if part.strip()], source
            return candidate, source
    return (list(key.default) if isinstance(key.default, list) else key.default), "default"


def raw_value(name: str, flags: Mapping[str, str | None] | None = None,
              env: Mapping[str, str] | None = None, local: Mapping[str, str] | None = None,
              project: Mapping[str, str] | None = None) -> str | list[str]:
    """Return a key's value before path resolution, following the six-level precedence."""
    return raw_source(name, flags, env, local, project)[0]


#: The variables through which git names a repository, exported to the hooks it runs: in a linked
#: worktree's commit hook, GIT_DIR names that worktree's git directory and GIT_INDEX_FILE its index.
#: They outrank ``git -C <path>``, so a command that names another checkout with ``-C`` while one
#: of them is set reads the hook's repository instead (the product check then saw the control
#: repository's origin and refused every commit in a control worktree).
GIT_LOCATION_VARIABLES = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX",
                          "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
                          "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE")


def git_env(env: Mapping[str, str] | None = None) -> dict[str, str]:
    """``env`` (default: this process's environment) without git's location variables. Pass it
    to every git call (and to ``gh``, which resolves its repository through git), so ``-C`` or
    the working directory alone decides which repository is read."""
    source = os.environ if env is None else env
    return {name: value for name, value in source.items() if name not in GIT_LOCATION_VARIABLES}


def repository_root(flag: str | None = None, env: Mapping[str, str] | None = None,
                    cwd: Path | None = None) -> Path:
    """Resolve the repository root that relative paths are taken from."""
    env = os.environ if env is None else env
    cwd = Path.cwd() if cwd is None else cwd
    for candidate in (flag, env.get(ROOT_ENV)):
        if _set(candidate):
            assert candidate is not None
            return Path(candidate).expanduser().resolve()
    project_dir = env.get("CLAUDE_PROJECT_DIR")
    project = Path(project_dir).expanduser().resolve() if _set(project_dir) else None
    here = cwd.resolve()
    try:
        top_text = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd,
                                  env=git_env(), capture_output=True, text=True,
                                  check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return project or here
    top = Path(top_text).resolve()
    # The project directory wins only when it is a folder nested inside the working tree the
    # command runs in and the command runs inside it: a control repository kept in a
    # subdirectory of another repository. A worktree elsewhere is always its own root.
    if project is not None and project != top and project.is_relative_to(top) \
            and here.is_relative_to(project):
        return project
    return top


def primary_checkout(root: Path) -> Path:
    """The first entry of ``git worktree list``; the root itself outside a git repository."""
    listed = subprocess.run(["git", "-C", str(root), "worktree", "list", "--porcelain"],
                            env=git_env(), capture_output=True, text=True, check=False)
    if listed.returncode == 0:
        for line in listed.stdout.splitlines():
            if line.startswith("worktree "):
                return Path(line.removeprefix("worktree ")).resolve()
    return root.resolve()


def local_record(root: Path) -> Path:
    """Where this machine's ``local.yaml`` is: in the primary checkout, at the root's place
    relative to the git top level, so a session worktree reads the primary checkout's file."""
    top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                         env=git_env(), capture_output=True, text=True, check=False)
    offset = Path()
    if top.returncode == 0:
        try:
            offset = root.resolve().relative_to(Path(top.stdout.strip()).resolve())
        except ValueError:
            offset = Path()
    return primary_checkout(root) / offset / LOCAL_RECORD


def read_yaml_record(location: Path, schema: str) -> dict[str, Any] | None:
    """A configuration file validated against ``schemas/<schema>``; None when it is absent.
    A file that does not parse or fails the schema raises ``PathError`` naming the file."""
    if not location.is_file():
        return None
    try:
        loaded = yaml.safe_load(location.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise PathError(location.name, str(location), f"is not valid YAML: {error}") from error
    validator = Draft7Validator(json.loads((PLUGIN_ROOT / "schemas" / schema)
                                           .read_text(encoding="utf-8")))
    issues = [f"{'.'.join(map(str, issue.absolute_path)) or '(top)'}: {issue.message}"
              for issue in validator.iter_errors(loaded)]
    if issues:
        raise PathError(location.name, str(location), "; ".join(issues))
    return dict(loaded)


def local_values(root: Path) -> dict[str, str]:
    """The keys this machine's ``local.yaml`` sets."""
    record = read_yaml_record(local_record(root), "local.schema.json") or {}
    return {name: str(value) for name, value in record.items() if name in KEYS}


def project_values(root: Path) -> dict[str, str]:
    """The keys the tracked files supply: ``project.yaml`` (``PROJECT_KEYS``) and
    ``product.yaml`` (``PRODUCT_RECORD_KEYS``).

    ``product.yaml`` is read without its schema: ``product.py`` validates it and reports a bad
    one, so a broken product record does not stop scripts that never touch the product."""
    record = read_yaml_record(root / PROJECT_RECORD, "project.schema.json") or {}
    found = {}
    for name, (section, field) in PROJECT_KEYS.items():
        value = (record.get(section) or {}).get(field)
        if value is not None:
            found[name] = str(value)
    location = root / PRODUCT_RECORD
    if location.is_file():
        try:
            product = yaml.safe_load(location.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            product = None
        if isinstance(product, dict):
            for name, field in PRODUCT_RECORD_KEYS.items():
                if isinstance(product.get(field), str):
                    found[name] = product[field]
    return found


def _to_path(root: Path, value: str) -> Path:
    value = value.replace("<repository>", root.name)
    path = Path(value).expanduser()
    return path if path.is_absolute() else (root / path)


class PathError(ValueError):
    """A configured value the plugin refuses to use. The message names the key."""

    def __init__(self, name: str, value: str, reason: str) -> None:
        super().__init__(f"{name} = {value!r}: {reason}")
        self.name = name


def _inside(root: Path, path: Path) -> Path | None:
    """``path``'s location relative to ``root`` after symlinks and ``..``; None when outside."""
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError:
        return None


def _contained(name: str, value: str, root: Path) -> Path:
    path = _to_path(root, value)
    relative = _inside(root, path)
    if relative is None:
        raise PathError(name, value, f"resolves outside the repository root {root}")
    if ".git" in relative.parts:
        raise PathError(name, value, "names a path inside .git")
    return path


def _outside(name: str, value: str, primary: Path) -> Path:
    path = _to_path(primary, value)
    if _inside(primary, path) is not None:
        raise PathError(name, value, f"resolves inside the primary checkout {primary}; it must "
                                     "name a directory outside the repository")
    return path


def _branch(name: str, value: str) -> str:
    if value.startswith("-"):
        raise PathError(name, value, "a branch name must not start with '-'")
    checked = subprocess.run(["git", "check-ref-format", "--branch", value],
                             env=git_env(), capture_output=True, text=True, check=False)
    if checked.returncode != 0:
        raise PathError(name, value, "is not a valid branch name (git check-ref-format --branch)")
    return value


HANDLE = re.compile(r"^[a-z][a-z0-9]{0,15}$")


def _port_range(name: str, value: str) -> str:
    match = re.fullmatch(r"(\d+)-(\d+)", value)
    if not match or not 1024 <= int(match.group(1)) <= int(match.group(2)) <= 65535:
        raise PathError(name, value, "must be <first>-<last> with 1024 <= first <= last <= 65535")
    return value


@dataclass(frozen=True)
class Config:
    """Resolved configuration: the root plus every key, validated as each is read."""

    root: Path
    values: Mapping[str, str | list[str]]
    sources: Mapping[str, str] = dataclasses.field(default_factory=dict)

    def path(self, name: str) -> Path:
        value = self.values[name]
        assert isinstance(value, str) and KEYS[name].kind == "path", name
        if name in PRODUCT_KEYS:
            root = self.product_root()
            if root is None:
                raise PathError("product_root", "", "is not set on this machine")
            return root if name == "product_root" else self.product_worktree_dir(root)
        if name in PRIMARY_KEYS:
            return _outside(name, value, primary_checkout(self.root))
        return _contained(name, value, self.root)

    def product_root(self) -> Path | None:
        """The product checkout on this machine, or None when it is not configured."""
        value = self.values["product_root"]
        assert isinstance(value, str)
        if not value:
            return None
        return _outside("product_root", value, primary_checkout(self.root))

    def product_worktree_dir(self, product_root: Path) -> Path:
        """Where product worktrees go: beside the product checkout, never inside either one."""
        value = self.values["product_worktree_dir"]
        assert isinstance(value, str)
        path = _to_path(product_root, value.replace("<product>", product_root.name))
        for checkout in (product_root, primary_checkout(self.root)):
            if _inside(checkout, path) is not None:
                raise PathError("product_worktree_dir", value,
                                f"resolves inside {checkout}; it must name a directory beside it")
        return path.resolve()

    def paths(self, name: str) -> list[Path]:
        value = self.values[name]
        assert isinstance(value, list), name
        return [_contained(name, item, self.root) for item in value]

    def text(self, name: str) -> str:
        value = self.values[name]
        assert isinstance(value, str), name
        if name == "integration_branch":
            return _branch(name, value)
        if name == "handle" and value and not HANDLE.match(value):
            raise PathError(name, value, f"a handle must match {HANDLE.pattern}")
        if name == "dev_port_range" and value:
            return _port_range(name, value)
        if name in GITHUB_KEYS and value and not GITHUB_SLUG.match(value):
            raise PathError(name, value, "must be <org>/<repo>")
        if name in {"control_remote", "product_remote"} and re.search(r"\s", value):
            raise PathError(name, value, "a repository URL must contain no whitespace")
        return value

    def invalid(self) -> list[PathError]:
        """Every key that fails validation, in manifest order. Reads only."""
        found = []
        for name, key in KEYS.items():
            if name in PRODUCT_KEYS and not self.values["product_root"]:
                continue
            reader = {"path": self.path, "paths": self.paths, "text": self.text}[key.kind]
            try:
                reader(name)
            except PathError as error:
                found.append(error)
        return found


def exits_on_path_error(main: Callable[..., int]) -> Callable[..., int]:
    """Wrap a script's ``main`` so a refused configured value exits 2 with its message."""

    @functools.wraps(main)
    def wrapper(*args: object, **kwargs: object) -> int:
        try:
            return main(*args, **kwargs)
        except PathError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2

    return wrapper


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
    local, project = local_values(root), project_values(root)
    resolved = {name: raw_source(name, flags, env, local, project) for name in KEYS}
    return Config(root, {name: value for name, (value, _) in resolved.items()},
                  {name: source for name, (_, source) in resolved.items()})


def shown(config: Config, name: str) -> str:
    """One key's resolved value as ``paths.py`` prints it."""
    key = KEYS[name]
    if name in PRODUCT_KEYS and config.product_root() is None:
        return "(not set)"
    if key.kind == "path":
        return str(config.path(name))
    if key.kind == "paths":
        return ", ".join(str(p) for p in config.paths(name))
    return config.text(name)


@exits_on_path_error
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print every resolved configuration value.")
    parser.add_argument("command", nargs="?", choices=("show",),
                        help="show: also print the source each value came from")
    add_arguments(parser)
    args = parser.parse_args(argv)
    config = resolve(args)
    if args.command != "show":
        print(f"root: {config.root}")
        for name in KEYS:
            print(f"{name}: {shown(config, name)}")
        return 0
    rows = [("key", "value", "source"), ("root", str(config.root), "")]
    rows += [(name, shown(config, name), config.sources.get(name, "")) for name in KEYS]
    width = max(len(row[0]) for row in rows)
    value_width = max(len(row[1]) for row in rows)
    for name, value, source in rows:
        print(f"{name:<{width}}  {value:<{value_width}}  {source}".rstrip())
    print(f"local file: {local_record(config.root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
