# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Compare every path the install-state record names against the disk. Changes nothing.

Each recorded file is reported as unchanged, drifted (its SHA-256 differs from the record) or
missing; each recorded directory as unchanged or missing. A file changed under recorded consent,
such as ``.gitignore``, is reported the same way but marked as consented, since people edit it.

Exit codes: 0 when every recorded file and directory is unchanged, 1 when any has drifted or is
missing, 2 when there is no install-state record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import paths
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
    results = []
    for entry in record.get("files", []):
        results.append((file_state(root / entry["path"], entry["sha256"]), entry["path"],
                        entry.get("feature", "")))
    for entry in record.get("directories", []):
        state = "unchanged" if (root / entry["path"]).is_dir() else "missing"
        results.append((state, entry["path"] + "/", entry.get("feature", "")))
    latest: dict[str, dict[str, str]] = {}
    for entry in record.get("consent", []):
        latest[entry["path"]] = entry
    for path, entry in latest.items():
        results.append((file_state(root / path, entry["sha256"]), path,
                        f"consent: {entry['target']}"))
    return results


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--root", help=f"repository root (env {paths.ROOT_ENV}; "
                                       "default: git top level)")
    args = parser.parse_args(argv)
    root = paths.repository_root(args.root)
    if not (root / RECORD).is_file():
        print(f"no install-state record at {RECORD.as_posix()}; run the scaffold first",
              file=sys.stderr)
        return 2
    results = diagnose(root)
    for state, path, note in results:
        print(f"{state:<9} {path}" + (f"  ({note})" if note else ""))
    bad = [result for result in results if result[0] != "unchanged"]
    print(f"{len(results)} recorded, {len(bad)} drifted or missing")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
