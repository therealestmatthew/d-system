# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Compare every path the install-state record names against the disk. Changes nothing.

How a recorded file is judged depends on its owner (``scaffold.py`` records it; a record written
before owners were recorded is read by path):

- A repository-owned file (the idea log, the backlog, the registers, ``product.yaml``,
  ``project.yaml`` and every other data or configuration file people and agents edit) is
  ``unchanged`` or ``edited`` against the recorded SHA-256, and ``missing`` when it is gone.
  Editing it is normal use, so ``edited`` never fails the run; ``check.py`` validates its
  content. An entry with ``edit`` consent (``scaffold.py --consent edit``) also names it.
- A plugin-owned copy (the schemas under ``.idea-realization/schemas/``) is compared with the
  file this plugin version ships. It is ``stale`` when its content differs, and ``unrecorded``
  when its content matches but the recorded SHA-256 does not (the copy was updated by hand).
  Both fail the run and name the fix: ``scaffold.py --feature <feature> --refresh-schemas``. When
  this plugin version no longer ships the file, the copy is compared with the record instead and
  reported ``unchanged`` or ``drifted``.

Each recorded directory is ``unchanged`` or ``missing``. A missing directory that git ignores,
such as the partition staging directory, is reported ``absent`` and does not fail the run: a
fresh clone never has it, and the scaffold (or the first partition sweep) creates it.

A file changed under recorded ``gitignore`` consent (``.gitignore``) is reported unchanged or
drifted against the hash recorded with the consent, marked as consented; people edit it.

When ``control_remote`` is set (this machine's ``local.yaml``, ``IDEA_REALIZATION_CONTROL_REMOTE``,
or a real ``control.remote`` in ``project.yaml``), the control checkout's ``origin`` must be that
repository (``project.py``); while it is unset the comparison is skipped with a note naming
``local.yaml``.

It first checks every configured key the way the scripts do (``paths``) and names each one it
would refuse, with the reason, rather than stopping at the first.

Exit codes: 0 when every recorded file and directory is unchanged, edited or absent as above, 1
when any is drifted, stale, unrecorded or missing, any configured key is invalid or the control
origin differs, 2 when there is no install-state record or a configuration file is refused.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import paths
import project
from scaffold import RECORD, owner_of, plugin_owned

#: States that do not fail the run.
OK_STATES = ("unchanged", "edited", "absent")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_state(path: Path, recorded: str) -> str:
    if not path.is_file():
        return "missing"
    return "unchanged" if sha256(path) == recorded else "drifted"


def ignored(root: Path, directory: str) -> bool:
    """Whether git ignores ``directory`` in ``root``; False outside a git repository. The
    trailing slash lets a directory-only pattern such as ``staging/`` match a directory that does
    not exist."""
    try:
        result = subprocess.run(["git", "-C", str(root), "check-ignore", "-q", "--",
                                 directory.rstrip("/") + "/"],
                                env=paths.git_env(), capture_output=True, check=False)
    except OSError:
        return False
    return result.returncode == 0


def plugin_file_state(path: Path, recorded: str, source: Path) -> tuple[str, str]:
    """(state, note) of a plugin-owned copy, compared with the plugin's ``source``."""
    if not path.is_file():
        return "missing", ""
    if not source.is_file():
        return file_state(path, recorded), ("not shipped by this plugin version; compared with "
                                            "the record")
    actual = sha256(path)
    if actual != sha256(source):
        return "stale", "differs from the plugin's copy"
    if actual != recorded:
        return "unrecorded", "matches the plugin's copy; the record is out of date"
    return "unchanged", ""


def diagnose(root: Path, config: paths.Config | None = None,
             plugin_root: Path = paths.PLUGIN_ROOT) -> list[tuple[str, str, str]]:
    """Return (state, path, note) for every recorded path. Reads only."""
    record = json.loads((root / RECORD).read_text(encoding="utf-8"))
    owned = plugin_owned(config if config is not None else paths.resolve({"root": str(root)}))
    editable = {entry["path"] for entry in record.get("consent", []) if entry["target"] == "edit"}
    results = []
    for entry in record.get("files", []):
        path, notes = root / entry["path"], [entry.get("feature", "")]
        if owner_of(entry, owned) == "plugin" and entry["path"] in owned:
            seed = owned[entry["path"]]
            assert seed.source is not None
            state, note = plugin_file_state(path, entry["sha256"], plugin_root / seed.source)
            notes.append(note)
            if state in ("stale", "unrecorded"):
                notes.append(f"fix: scaffold.py --feature {seed.feature} --refresh-schemas")
        else:
            state = file_state(path, entry["sha256"])
            state = "edited" if state == "drifted" else state
            if entry["path"] in editable:
                notes.append("consent: edit")
        results.append((state, entry["path"], ", ".join(note for note in notes if note)))
    for entry in record.get("directories", []):
        state, note = "unchanged", entry.get("feature", "")
        if not (root / entry["path"]).is_dir():
            state = "missing"
            if ignored(root, entry["path"]):
                state = "absent"
                note = ", ".join(part for part in (note, "gitignored; the scaffold recreates it")
                                 if part)
        results.append((state, entry["path"] + "/", note))
    latest: dict[str, dict[str, str]] = {}
    for entry in record.get("consent", []):
        if entry["target"] != "edit":
            latest[entry["path"]] = entry
    for path, entry in latest.items():
        results.append((file_state(root / path, entry["sha256"]), path,
                        f"consent: {entry['target']}"))
    return results


@paths.exits_on_path_error
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    paths.add_arguments(parser)
    args = parser.parse_args(argv)
    config = paths.resolve(args)
    invalid = config.invalid()
    for error in invalid:
        print(f"invalid   {error}")
    if invalid:
        print(f"{len(invalid)} configured value(s) invalid")
        return 1
    root = config.root
    if not (root / RECORD).is_file():
        print(f"no install-state record at {RECORD.as_posix()}; run the scaffold first",
              file=sys.stderr)
        return 2
    results = diagnose(root, config)
    for state, path, note in results:
        print(f"{state:<9} {path}" + (f"  ({note})" if note else ""))
    bad = [result for result in results if result[0] not in OK_STATES]
    print(f"{len(results)} recorded, {len(bad)} drifted, stale, unrecorded or missing")
    origin_problem, origin_note = project.control_origin(config)
    if origin_problem:
        print(f"origin    {origin_problem}")
    elif origin_note:
        print(f"origin    {origin_note}")
    return 1 if bad or origin_problem else 0


if __name__ == "__main__":
    raise SystemExit(main())
