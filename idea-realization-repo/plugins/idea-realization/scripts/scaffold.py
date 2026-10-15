# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Create the directories and seed files each feature needs in the target repository.

Never overwrites a file that exists: every such path is reported as skipped and left
byte-identical. Every file written is recorded, with its SHA-256 and its owner, in
``.idea-realization/install-state.json``. ``--dry-run`` reports the same plan and writes nothing.

The record is rewritten only when what it records changes. A run that only recreates paths the
record already lists, such as the gitignored staging directory on a fresh clone, leaves the tracked
record byte-identical, so the checkout stays clean.

Each seeded file has one of two owners, recorded as ``owner`` on its entry:

- ``plugin``: a copy whose content must equal the file this plugin version ships, namely the
  schema copies under ``.idea-realization/schemas/``. Nobody edits them. ``doctor.py`` reports
  one as stale when it differs from the plugin's file.
- ``repository``: a data or configuration file people and agents edit by design: the idea log,
  its view and priority file, the backlog, the code register, the systems and workstreams
  registries, the brain README and index, ``product.yaml``, ``project.yaml`` and
  ``local.example.yaml``. The scaffold only seeds a starting point; ``doctor.py`` reports an
  edited one as edited, never as drifted, and ``check.py`` validates its content.

``--refresh-schemas`` is the one exception to never overwriting: for the selected features it
overwrites every plugin-owned copy that differs from the plugin's file with that file, and records
the new SHA-256 (also when the copy already matches and only the record is out of date). Run it
after updating the plugin, or when ``doctor.py`` reports a stale or unrecorded copy.

The target's ``.gitignore`` is changed only with ``--consent gitignore``, and that consent is
recorded. The scaffold never writes ``.claude/settings.json`` or a hook.

``--consent edit`` records that the configuration files people are expected to fill in
(``product.yaml`` and ``project.yaml``, for the selected features) will change after the scaffold
wrote them. Both are repository-owned, so ``doctor.py`` reports them as edited with or without
it; with it, the doctor's line also names the consent.

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
from typing import cast

import paths

RECORD = Path(".idea-realization") / "install-state.json"
SCHEMA_DIR = Path(".idea-realization") / "schemas"
FEATURES = ("ideas", "partition", "backlog", "documents", "workstreams", "reviews", "product",
            "brain", "project")
CONSENTS = ("gitignore", "edit")
#: Configuration files people fill in after the scaffold, by feature (``--consent edit``).
EDITABLE = {"product": Path(".idea-realization") / "product.yaml",
            "project": Path(".idea-realization") / "project.yaml"}


@dataclass(frozen=True)
class Seed:
    """One path the scaffold creates.

    ``content`` is the file's text; ``source`` is a plugin file to copy instead, reported as not
    shipped when this plugin version lacks it; neither means a directory. ``plugin_owned`` marks
    a copy that must stay equal to ``source`` (owner ``plugin``); every other file is a starting
    point the repository then edits (owner ``repository``).
    """

    feature: str
    target: Callable[[paths.Config], Path]
    content: Callable[[], str] | None = None
    source: str | None = None
    plugin_owned: bool = False

    @property
    def owner(self) -> str:
        return "plugin" if self.plugin_owned else "repository"


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
                source=f"schemas/{name}", plugin_owned=True)


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
    Seed("workstreams", _under("docs_root", "workstreams.yaml"),
         lambda: "schema_version: 1\n# One entry per workstream: the paths one developer owns. "
                 "Claim with workstreams.py.\nworkstreams: []\n"),
    _schema("workstreams", "workstreams.schema.json"),
    Seed("reviews", _under("docs_root", "reviews")),
    _schema("reviews", "review-verdict.schema.json"),
    Seed("product", lambda config: config.root / ".idea-realization" / "product.yaml",
         source="templates/product.yaml"),
    _schema("product", "product.schema.json"),
    *(Seed("brain", _under("brain_root", folder))
      for folder in ("decisions", "research", "concepts", "entities", "learnings")),
    Seed("brain", _under("brain_root", "README.md"), source="templates/brain-readme.md"),
    Seed("brain", _under("brain_root", "index.md"),
         lambda: "# Brain index\n\nGenerated by `brain.py index`. Never edit by hand; "
                 "`brain.py check` fails while it is stale.\n\nNo entries yet.\n"),
    _schema("brain", "brain-entry.schema.json"),
    Seed("project", lambda config: config.root / EDITABLE["project"],
         source="templates/project.yaml"),
    Seed("project", lambda config: config.root / ".idea-realization" / "local.example.yaml",
         source="templates/local.example.yaml"),
    _schema("project", "project.schema.json"),
    _schema("project", "local.schema.json"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(config: paths.Config, path: Path) -> str:
    try:
        return path.resolve().relative_to(config.root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def plugin_owned(config: paths.Config) -> dict[str, Seed]:
    """Every plugin-owned seed, by the path it is recorded under in ``config``'s repository."""
    return {relative(config, seed.target(config)): seed for seed in SEEDS if seed.plugin_owned}


def owner_of(entry: dict[str, str], owned: dict[str, Seed]) -> str:
    """The recorded ``owner`` of a file entry; for a record written before owners were recorded,
    ``plugin`` when the path is a plugin-owned seed's and ``repository`` otherwise."""
    return entry.get("owner") or ("plugin" if entry["path"] in owned else "repository")


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
    """The lines ``.gitignore`` needs: the partition staging directory and the project
    feature's per-machine ``local.yaml``."""
    lines = []
    if "partition" in features:
        lines.append("/" + relative(config, config.path("staging_dir")).rstrip("/") + "/")
    if "project" in features:
        lines.append("/" + paths.LOCAL_RECORD.as_posix())
    return lines


def scaffold(config: paths.Config, features: Sequence[str], dry_run: bool = False,
             consent: Sequence[str] = (), plugin_root: Path = paths.PLUGIN_ROOT,
             refresh_schemas: bool = False) -> list[str]:
    """Create every missing path for ``features``; return one report line per path.

    With ``refresh_schemas``, also bring every existing plugin-owned copy for ``features`` back
    to the plugin's file and record its hash."""
    lines: list[str] = []
    record = load_record(config.root)
    recorded_before = json.dumps(record, sort_keys=True)
    files: list[dict[str, str]] = record["files"]  # type: ignore[assignment]
    directories: list[dict[str, str]] = record["directories"]  # type: ignore[assignment]
    written = False
    # Resolve every key this run will write before the first write, so a refused value
    # (``paths.PathError``) leaves the repository untouched.
    targets = {id(seed): seed.target(config) for seed in SEEDS if seed.feature in features}
    wanted = gitignore_lines(config, features)

    def remember(entries: list[dict[str, str]], entry: dict[str, str]) -> None:
        """Record ``entry``, in the place of an entry for the same path if there is one."""
        for index, item in enumerate(entries):
            if item["path"] == entry["path"]:
                entries[index] = entry
                return
        entries.append(entry)

    def refresh(seed: Seed, target: Path, name: str) -> bool:
        """Bring one existing plugin-owned copy back to the plugin's file; True when the record
        changed."""
        assert seed.source is not None
        source = plugin_root / seed.source
        if not source.is_file():
            lines.append(f"skipped  {name} (not shipped by this plugin version)")
            return False
        if target.is_symlink() or not target.is_file():
            lines.append(f"skipped  {name} (not a regular file; remove it and re-run)")
            return False
        data = source.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        stale = target.read_bytes() != data
        recorded = next((entry for entry in files if entry["path"] == name), None)
        if not stale and recorded is not None and recorded["sha256"] == digest \
                and recorded.get("owner") == "plugin":
            lines.append(f"skipped  {name} (current)")
            return False
        verb = "refresh" if stale else "record"
        if dry_run:
            lines.append(f"would {verb}  {name}")
            return False
        if stale:
            temporary = target.with_name(target.name + ".refresh")
            temporary.write_bytes(data)
            temporary.replace(target)
        remember(files, {"path": name, "sha256": digest, "feature": seed.feature,
                         "owner": "plugin"})
        lines.append(f"{'refreshed' if stale else 'recorded'}  {name}")
        return True

    for seed in SEEDS:
        if seed.feature not in features:
            continue
        target = targets[id(seed)]
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
            if refresh_schemas and seed.plugin_owned and seed.source is not None:
                written |= refresh(seed, target, name)
                continue
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
        remember(files, {"path": name, "sha256": sha256(target), "feature": seed.feature,
                         "owner": seed.owner})
        written = True

    if wanted:
        gitignore = config.root / ".gitignore"
        present = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
        needed = [line for line in wanted if line not in present]
        if not needed:
            lines.append("skipped  .gitignore (already has every line it needs)")
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

    if "edit" in consent:
        edits = cast("list[dict[str, object]]", record["consent"])
        granted = {entry["path"] for entry in edits if entry["target"] == "edit"}
        for feature, path in EDITABLE.items():
            name = path.as_posix()
            if feature not in features or name in granted:
                continue
            if dry_run:
                lines.append(f"would record  consent to edit {name}")
                continue
            edits.append({"target": "edit", "path": name, "granted_at": now()})
            lines.append(f"recorded consent to edit {name}")
            written = True

    if written:
        stamp = now()
        record["installed_at"] = record["installed_at"] or stamp
        record["plugin_version"] = plugin_version()
        record["features"] = sorted(set(record["features"]) | set(features))  # type: ignore[call-overload]
        if json.dumps(record, sort_keys=True) == recorded_before:
            lines.append(f"skipped  {RECORD.as_posix()} (already records every path)")
            return lines
        record["updated_at"] = stamp
        path = config.root / RECORD
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        lines.append(f"recorded {RECORD.as_posix()}")
    return lines


@paths.exits_on_path_error
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--feature", action="append", default=None,
                        choices=[*FEATURES, "all"], help="feature to scaffold; repeatable")
    parser.add_argument("--dry-run", action="store_true", help="report the plan; write nothing")
    parser.add_argument("--refresh-schemas", action="store_true",
                        help="replace every schema copy that differs from the plugin's with the "
                             "plugin's, and record its hash")
    parser.add_argument("--consent", action="append", default=[], choices=list(CONSENTS),
                        help="gitignore: allow the scaffold to change .gitignore; edit: record "
                             "that product.yaml and project.yaml will be filled in; recorded in "
                             "the state")
    paths.add_arguments(parser)
    args = parser.parse_args(argv)
    if not args.feature:
        print("choose at least one --feature", file=sys.stderr)
        return 2
    features = list(FEATURES) if "all" in args.feature else sorted(set(args.feature))
    config = paths.resolve(args)
    for line in scaffold(config, features, args.dry_run, args.consent,
                         refresh_schemas=args.refresh_schemas):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
