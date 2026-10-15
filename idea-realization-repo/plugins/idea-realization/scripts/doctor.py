# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Compare every path the install-state record names against the disk. Changes nothing.

Each recorded file is reported as unchanged, drifted (its SHA-256 differs from the record) or
missing; each recorded directory as unchanged or missing. A file changed under recorded consent,
such as ``.gitignore``, is reported the same way but marked as consented, since people edit it.
A configuration file recorded with ``edit`` consent (``scaffold.py --consent edit``: the tracked
``product.yaml`` and ``project.yaml``, which people fill in) is reported as edited, not drifted,
when its content changed; it is still reported missing when it is gone.

When ``project.yaml`` names a real ``control.remote``, the control checkout's ``origin`` must be
that repository (``project.py``); while the value is a ``REPLACE-WITH-`` placeholder the comparison
is skipped with a note.

It first checks every configured key the way the scripts do (``paths``) and names each one it
would refuse, with the reason, rather than stopping at the first.

Exit codes: 0 when every recorded file and directory is unchanged or edited under consent, 1 when
any has drifted or is missing, any configured key is invalid or the control origin differs, 2 when
there is no install-state record or a configuration file is refused.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import paths
import project
from scaffold import RECORD


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_state(path: Path, recorded: str) -> str:
    if not path.is_file():
        return "missing"
    return "unchanged" if sha256(path) == recorded else "drifted"


def diagnose(root: Path) -> list[tuple[str, str, str]]:
    """Return (state, path, note) for every recorded path. Reads only."""
    record = json.loads((root / RECORD).read_text(encoding="utf-8"))
    editable = {entry["path"] for entry in record.get("consent", []) if entry["target"] == "edit"}
    results = []
    for entry in record.get("files", []):
        state, note = file_state(root / entry["path"], entry["sha256"]), entry.get("feature", "")
        if entry["path"] in editable:
            state = "edited" if state == "drifted" else state
            note = f"{note}, consent: edit" if note else "consent: edit"
        results.append((state, entry["path"], note))
    for entry in record.get("directories", []):
        state = "unchanged" if (root / entry["path"]).is_dir() else "missing"
        results.append((state, entry["path"] + "/", entry.get("feature", "")))
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
    results = diagnose(root)
    for state, path, note in results:
        print(f"{state:<9} {path}" + (f"  ({note})" if note else ""))
    bad = [result for result in results if result[0] not in ("unchanged", "edited")]
    print(f"{len(results)} recorded, {len(bad)} drifted or missing")
    origin_problem, origin_note = project.control_origin(root)
    if origin_problem:
        print(f"origin    {origin_problem}")
    elif origin_note:
        print(f"origin    {origin_note}")
    return 1 if bad or origin_problem else 0


if __name__ == "__main__":
    raise SystemExit(main())
