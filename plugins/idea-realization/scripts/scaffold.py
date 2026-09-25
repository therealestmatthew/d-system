# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Create the directories and seed files each feature needs in the target repository.

Never overwrites a file that exists: every such path is reported as skipped and left
byte-identical. Every file written is recorded, with its SHA-256, in
``.idea-realization/install-state.json``. ``--dry-run`` reports the same plan and writes nothing.

The target's ``.gitignore`` is changed only with ``--consent gitignore``, and that consent is
recorded. The scaffold never writes ``.claude/settings.json`` or a hook.

Exit codes: 0 on success, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import paths

RECORD = Path(".idea-realization") / "install-state.json"
SCHEMA_DIR = Path(".idea-realization") / "schemas"
FEATURES = ("ideas", "partition", "backlog", "documents")


@dataclass(frozen=True)
class Seed:
    """One path the scaffold creates.

    ``content`` is the file's text; ``source`` is a plugin file to copy instead, reported as not
    shipped when this plugin version lacks it; neither means a directory.
    """

    feature: str
    target: Callable[[paths.Config], Path]
    content: Callable[[], str] | None = None
    source: str | None = None


def today() -> str:
    return dt.date.today().isoformat()


def now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _key(name: str) -> Callable[[paths.Config], Path]:
    return lambda config: config.path(name)


def _under(name: str, *parts: str) -> Callable[[paths.Config], Path]:
    return lambda config: config.path(name).joinpath(*parts)


def _schema(feature: str, name: str) -> Seed:
    return Seed(feature, lambda config: config.root / SCHEMA_DIR / name,
                source=f"schemas/{name}")


SEEDS: tuple[Seed, ...] = (
    Seed("ideas", _key("ideas_path"), lambda: ""),
    Seed("ideas", _key("ideas_view_path"),
         lambda: "# Ideas\n\nGenerated from the idea log. Never edit by hand; re-render it.\n"),
    Seed("ideas", _key("priority_path"),
         lambda: f"schema_version: 1\nupdated: '{today()}'\nnext_up: []\n"),
    _schema("ideas", "idea.schema.json"),
    _schema("ideas", "idea-priority.schema.json"),
    Seed("partition", _key("staging_dir")),
    _schema("partition", "idea-partition-record.schema.json"),
    Seed("backlog", _key("backlog_path"),
         lambda: f"schema_version: 1\nupdated: '{today()}'\nmax_active: 1\nnext_up: []\n"
                 "items: []\n"),
    _schema("backlog", "backlog.schema.json"),
    Seed("documents", _key("docs_root")),
    Seed("documents", _under("docs_root", "codes.yaml"), source="templates/codes.yaml"),
    Seed("documents", _under("docs_root", "systems.yaml"), source="templates/systems.yaml"),
    _schema("documents", "document.schema.json"),
    _schema("documents", "codes.schema.json"),
    _schema("documents", "systems.schema.json"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(config: paths.Config, path: Path) -> str:
    try:
        return path.resolve().relative_to(config.root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def plugin_version() -> str:
    return str(json.loads(paths.MANIFEST.read_text(encoding="utf-8")).get("version", "0"))


def load_record(root: Path) -> dict[str, object]:
    path = root / RECORD
    if path.exists():
        loaded: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
        return loaded
    return {"schema_version": 1, "plugin": "idea-realization", "plugin_version": plugin_version(),
            "installed_at": None, "updated_at": None, "features": [], "files": [],
            "directories": [], "consent": []}


def gitignore_lines(config: paths.Config, features: Sequence[str]) -> list[str]:
    """The lines the partition feature needs in ``.gitignore``: its staging directory."""
    if "partition" not in features:
        return []
    return ["/" + relative(config, config.path("staging_dir")).rstrip("/") + "/"]


def scaffold(config: paths.Config, features: Sequence[str], dry_run: bool = False,
             consent: Sequence[str] = (), plugin_root: Path = paths.PLUGIN_ROOT) -> list[str]:
    """Create every missing path for ``features``; return one report line per path."""
    lines: list[str] = []
    record = load_record(config.root)
    files: list[dict[str, str]] = record["files"]  # type: ignore[assignment]
    directories: list[dict[str, str]] = record["directories"]  # type: ignore[assignment]
    written = False

    def remember(entries: list[dict[str, str]], entry: dict[str, str]) -> None:
        entries[:] = [item for item in entries if item["path"] != entry["path"]] + [entry]

    for seed in SEEDS:
        if seed.feature not in features:
            continue
        target = seed.target(config)
        name = relative(config, target)
        if seed.content is None and seed.source is None:
            if target.is_dir():
                lines.append(f"skipped  {name}/ (exists)")
                continue
            if target.exists():
                lines.append(f"skipped  {name}/ (a file is in the way)")
                continue
            lines.append(f"{'would create' if dry_run else 'created'}  {name}/")
            if not dry_run:
                target.mkdir(parents=True)
                remember(directories, {"path": name, "feature": seed.feature})
                written = True
            continue
        if target.exists() or target.is_symlink():
            lines.append(f"skipped  {name} (exists)")
            continue
        if seed.source is not None:
            source = plugin_root / seed.source
            if not source.is_file():
                lines.append(f"skipped  {name} (not shipped by this plugin version)")
                continue
            data = source.read_bytes()
        else:
            assert seed.content is not None
            data = seed.content().encode("utf-8")
        lines.append(f"{'would create' if dry_run else 'created'}  {name}")
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open("xb") as handle:  # "x": never overwrite, even in a race
                handle.write(data)
        except FileExistsError:
            lines[-1] = f"skipped  {name} (appeared during this run)"
            continue
        remember(files, {"path": name, "sha256": sha256(target), "feature": seed.feature})
        written = True

    wanted = gitignore_lines(config, features)
    if wanted:
        gitignore = config.root / ".gitignore"
        present = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
        needed = [line for line in wanted if line not in present]
        if not needed:
            lines.append("skipped  .gitignore (already ignores the staging directory)")
        elif "gitignore" not in consent:
            lines.append(f"needs consent  .gitignore: add {', '.join(needed)} "
                         "(re-run with --consent gitignore)")
        elif dry_run:
            lines.append(f"would change  .gitignore: add {', '.join(needed)}")
        else:
            text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
            if text and not text.endswith("\n"):
                text += "\n"
            gitignore.write_text(text + "".join(line + "\n" for line in needed), encoding="utf-8")
            consents: list[dict[str, object]] = record["consent"]  # type: ignore[assignment]
            consents.append({"target": "gitignore", "path": ".gitignore", "lines": needed,
                             "sha256": sha256(gitignore), "granted_at": now()})
            lines.append(f"changed  .gitignore: added {', '.join(needed)} (consent recorded)")
            written = True

    if written:
        stamp = now()
        record["installed_at"] = record["installed_at"] or stamp
        record["updated_at"] = stamp
        record["plugin_version"] = plugin_version()
        record["features"] = sorted(set(record["features"]) | set(features))  # type: ignore[call-overload]
        path = config.root / RECORD
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        lines.append(f"recorded {RECORD.as_posix()}")
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--feature", action="append", default=None,
                        choices=[*FEATURES, "all"], help="feature to scaffold; repeatable")
    parser.add_argument("--dry-run", action="store_true", help="report the plan; write nothing")
    parser.add_argument("--consent", action="append", default=[], choices=["gitignore"],
                        help="allow the scaffold to change this file; recorded in the state")
    paths.add_arguments(parser)
    args = parser.parse_args(argv)
    if not args.feature:
        print("choose at least one --feature", file=sys.stderr)
        return 2
    features = list(FEATURES) if "all" in args.feature else sorted(set(args.feature))
    config = paths.resolve(args)
    for line in scaffold(config, features, args.dry_run, args.consent):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
