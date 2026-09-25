# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Document code series, allocation, register consistency and the catalog.

Two numbering modes exist. Counter series take the next free three-digit number in the series,
with an optional ``.NN`` sub-code under a parent plan; dated series derive their code from the
document's own date plus a same-day sequence, so kinds written by several sessions at once never
contend on one counter.

Run directly, this script is the ``next-code`` command: it scans the document root, then
allocates the next free code for a kind and holds it with a pre-merge reservation (see
``reservations.py``) before printing it, so two worktrees allocating the same kind before either
merges receive different codes. Never choose a code by hand.

Exit codes: 0 with the code printed; 1 when the document tree fails its check or no code can be
allocated; 2 on a usage error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

import paths
import reservations

COUNTER = re.compile(r"^(?P<series>[A-Z]+)-(?P<number>[0-9]{3})(?:\.(?P<sub>[0-9]{2}))?$")
DATED = re.compile(
    r"^(?P<series>[A-Z]+)-(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})-(?P<sequence>[0-9]{2})$"
)

#: How many candidates an allocation tries before giving up. Each failed pass means a peer took
#: that exact code between this caller's read and its write.
RESERVATION_ATTEMPTS = 50


def parse_code(value: str) -> dict[str, Any] | None:
    """Split a code into its parts, or return None when it matches no grammar."""
    match = COUNTER.match(value)
    if match:
        return {
            "series": match["series"],
            "numbering": "counter",
            "number": int(match["number"]),
            "sub": int(match["sub"]) if match["sub"] else None,
            "stem": f"{match['series']}-{match['number']}",
        }
    match = DATED.match(value)
    if match:
        return {
            "series": match["series"],
            "numbering": "dated",
            "date": match["date"],
            "sequence": int(match["sequence"]),
            "stem": value,
        }
    return None


def series_by_kind(register: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["kind"]: entry for entry in register["series"]}


def held_codes(register: dict[str, Any]) -> dict[str, str]:
    """Codes the register holds, mapped to the reason they cannot be freely allocated."""
    return {
        **{entry["code"]: "retired" for entry in register["retired"]},
        **{entry["code"]: "reserved" for entry in register["reserved"]},
    }


def allocated(
    register: dict[str, Any], documents: dict[str, Any], reserved: set[str] | None = None
) -> list[str]:
    """Every code spent: in use, held by the register, or reserved pre-merge by a worktree."""
    return (
        [meta["code"] for meta in documents.values() if meta.get("code")]
        + list(held_codes(register))
        + sorted(reserved or ())
    )


def next_code(
    kind: str,
    register: dict[str, Any],
    documents: dict[str, Any],
    parent: str | None = None,
    today: date | None = None,
    reserved: set[str] | None = None,
) -> str:
    """The next free code for a kind, treating pre-merge reservations as already spent.

    Pure in its arguments; the caller reads the reservation store and passes ``reserved`` in.
    Without it, two worktrees calling this before either merges get the same answer.
    """
    series = series_by_kind(register).get(kind)
    if not series:
        raise ValueError(f"no series is registered for kind {kind}")
    spent = [
        parsed for value in allocated(register, documents, reserved)
        if (parsed := parse_code(value))
    ]
    mine = [parsed for parsed in spent if parsed["series"] == series["code"]]

    if series["numbering"] == "dated":
        if parent:
            raise ValueError(f"{series['code']} is a dated series and takes no parent")
        stamp = (today or date.today()).isoformat()
        used = {parsed["sequence"] for parsed in mine if parsed["date"] == stamp}
        return f"{series['code']}-{stamp}-{max(used, default=0) + 1:02d}"

    if not parent:
        used = {parsed["number"] for parsed in mine}
        return f"{series['code']}-{max(used, default=0) + 1:03d}"

    if not series["sub_codes"]:
        raise ValueError(f"{series['code']} does not allow sub-codes")
    document = documents.get(parent)
    if not document or not document.get("code"):
        raise ValueError(f"unknown parent document {parent}")
    stem = parse_code(document["code"])
    if not stem or stem["numbering"] != "counter" or stem["sub"] is not None:
        raise ValueError(f"{parent} does not hold a top-level {series['code']} code")
    used = {
        parsed["sub"] for parsed in mine
        if parsed["stem"] == stem["stem"] and parsed["sub"] is not None
    }
    return f"{stem['stem']}.{max(used, default=0) + 1:02d}"


def inspect_register(register: dict[str, Any], kinds: set[str]) -> list[str]:
    """Check the register against itself before any document is scanned."""
    errors = []
    series = register["series"]
    if len({entry["code"] for entry in series}) != len(series):
        errors.append("codes: duplicate series code")
    if len({entry["kind"] for entry in series}) != len(series):
        errors.append("codes: duplicate series kind")
    for missing in sorted(kinds - {entry["kind"] for entry in series}):
        errors.append(f"codes: no series registered for kind {missing}")
    known = {entry["code"] for entry in series}
    for entry in series:
        if entry["numbering"] == "dated" and entry["sub_codes"]:
            errors.append(f"codes: dated series {entry['code']} cannot allow sub-codes")
    reserved = {entry["code"] for entry in register["reserved"]}
    retired = {entry["code"] for entry in register["retired"]}
    for code in sorted(reserved & retired):
        errors.append(f"codes: {code} cannot be reserved and retired at once")
    for code in sorted(reserved | retired):
        parsed = parse_code(code)
        if not parsed or parsed["series"] not in known:
            errors.append(f"codes: held code {code} is malformed or names an unknown series")
    return errors


def location_error(meta: dict[str, Any], series: dict[str, Any]) -> str | None:
    """``meta['location']`` is the document's path relative to the document root."""
    if any(meta["location"].startswith(location) for location in series["locations"]):
        return None
    return f"{meta['path']}: {series['kind']} belongs under {' or '.join(series['locations'])}"


def naming_errors(
    meta: dict[str, Any], code: str, parsed: dict[str, Any], series: dict[str, Any]
) -> list[str]:
    """The filename, and the plan folder holding it, must announce the document's code.

    A plan folder may group its children one level deeper under an area folder, whose name is a
    reader-facing label rather than a code. The overview stays at the plan folder's root, so only
    a sub-coded child may sit inside an area folder.
    """
    path = meta["path"]
    errors = []
    relative = next(
        PurePosixPath(meta["location"]).relative_to(location)
        for location in series["locations"]
        if meta["location"].startswith(location)
    )
    if not relative.name.startswith(f"{code}-"):
        errors.append(f"{path}: filename must start with {code}-")
    if len(relative.parts) > 3:
        errors.append(f"{path}: a plan folder nests at most one area folder deep")
    elif len(relative.parts) > 1 and not relative.parts[0].startswith(f"{parsed['stem']}-"):
        errors.append(f"{path}: containing folder must start with {parsed['stem']}-")
    elif len(relative.parts) == 3 and parsed.get("sub") is None:
        errors.append(f"{path}: an area folder holds child plans; the overview sits beside it")
    return errors


def inspect_codes(register: dict[str, Any], documents: dict[str, Any]) -> list[str]:
    """Check every document's code against the register, its kind, its path and its parent."""
    errors: list[str] = []
    series_index = series_by_kind(register)
    held = held_codes(register)
    seen: dict[str, str] = {}

    for key, meta in sorted(documents.items()):
        path = meta["path"]
        code = meta["code"]
        series = series_index.get(meta["kind"])
        if not series:
            errors.append(f"{path}: no series is registered for kind {meta['kind']}")
            continue
        message = location_error(meta, series)
        if message:
            errors.append(message)
        parsed = parse_code(code)
        if not parsed:
            errors.append(f"{path}: malformed code {code}")
            continue
        if parsed["series"] != series["code"]:
            errors.append(
                f"{path}: kind {meta['kind']} requires a {series['code']} code, not {code}"
            )
            continue
        if parsed["numbering"] != series["numbering"]:
            errors.append(f"{path}: {series['code']} uses {series['numbering']} numbering")
            continue
        if code in seen:
            errors.append(f"{path}: duplicate code {code}, already held by {seen[code]}")
        seen[code] = path
        if held.get(code) == "retired":
            errors.append(f"{path}: {code} is retired and can never be reused")
        elif held.get(code) == "reserved":
            errors.append(f"{path}: {code} is reserved; remove the reservation in this change")
        if not message:
            errors.extend(naming_errors(meta, code, parsed, series))
        if parsed["numbering"] == "dated" and parsed["date"] != meta["created"]:
            errors.append(
                f"{path}: code date {parsed['date']} must equal created {meta['created']}"
            )
        errors.extend(parent_errors(key, meta, parsed, documents, series))
    return errors


def parent_errors(
    key: str,
    meta: dict[str, Any],
    parsed: dict[str, Any],
    documents: dict[str, Any],
    series: dict[str, Any],
) -> list[str]:
    """A sub-code and a parent reference must imply each other and agree on the stem."""
    path = meta["path"]
    parent = documents.get(meta.get("parent", ""))
    if parsed["numbering"] != "counter" or parsed["sub"] is None:
        if parent and series["sub_codes"]:
            return [f"{path}: child of {meta['parent']} requires a sub-code under its parent"]
        return []
    if not series["sub_codes"]:
        return [f"{path}: {series['code']} does not allow sub-codes"]
    if not parent:
        return [f"{path}: sub-code {meta['code']} requires a parent"]
    if parent.get("code") != parsed["stem"]:
        return [
            f"{path}: sub-code stem {parsed['stem']} does not match parent {parent.get('code')}"
        ]
    return [] if key != meta.get("parent") else [f"{path}: document is its own parent"]


def catalog_key(meta: dict[str, Any]) -> tuple[int, str, str, int, str]:
    """Order documents by series, then number or date, then sub-code."""
    parsed = parse_code(meta["code"]) if meta.get("code") else None
    if not parsed:
        return (1, "", "", 0, meta["path"])
    if parsed["numbering"] == "counter":
        return (0, parsed["series"], f"{parsed['number']:03d}", parsed["sub"] or 0, meta["path"])
    return (0, parsed["series"], parsed["date"], parsed["sequence"], meta["path"])


def render_catalog(
    register: dict[str, Any],
    documents: dict[str, Any],
    items: list[dict[str, Any]] | None = None,
) -> str:
    """Render the catalog from documents, the register and, when one exists, the backlog.

    ``items`` is the backlog's phase list, or None when the repository has no backlog; the plans
    table's phase counts appear only when it is given.
    """

    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    lines = [
        "# Documentation catalog",
        "",
        "Generated by the idea-realization `catalog` command. Never edit this file by hand;",
        "the `check` command regenerates it in memory and fails on any difference.",
        "",
        "## Documents",
        "",
        "| Code | Kind | Status | Owner | Path |",
        "|---|---|---|---|---|",
    ]
    ordered = sorted(documents.items(), key=lambda pair: catalog_key(pair[1]))
    for _, meta in ordered:
        lines.append(
            f"| {meta.get('code', '—')} | {meta['kind']} | {meta['status']} | "
            f"{meta['owner']} | {cell(meta['path'])} |"
        )

    plans = [(key, meta) for key, meta in ordered if meta["kind"] == "plan"]
    if items is None:
        lines += ["", "## Plans", "", "| Code | Plan | Status |", "|---|---|---|"]
        for key, meta in plans:
            lines.append(f"| {meta.get('code', '—')} | {key} | {meta['status']} |")
    else:
        lines += [
            "",
            "## Plans and their phases",
            "",
            "| Code | Plan | Status | Queued | Active | Complete | Agents |",
            "|---|---|---|---|---|---|---|",
        ]
        for key, meta in plans:
            phases = [
                item for item in items
                if key in [item.get("plan"), *item.get("sources", [])]
                and item.get("status") != "cancelled"
            ]
            states = [item.get("status") for item in phases]
            agents = sorted({item["agent"] for item in phases if item.get("agent")})
            lines.append(
                f"| {meta.get('code', '—')} | {key} | {meta['status']} | "
                f"{states.count('queued')} | {states.count('active')} | "
                f"{states.count('complete')} | {', '.join(agents) or '—'} |"
            )
    if not plans:
        lines.append("| — | — | — |" if items is None else "| — | — | — | — | — | — | — |")

    lines += ["", "## Held codes", "", "| Code | State | Reason |", "|---|---|---|"]
    holds = [(entry, "reserved") for entry in register["reserved"]]
    holds += [(entry, "retired") for entry in register["retired"]]
    for entry, state in sorted(holds, key=lambda pair: pair[0]["code"]):
        lines.append(f"| {entry['code']} | {state} | {cell(entry['reason'])} |")
    if not holds:
        lines.append("| — | — | — |")

    counts: dict[str, int] = {}
    for meta in documents.values():
        counts[meta["kind"]] = counts.get(meta["kind"], 0) + 1
    summary = ", ".join(f"{kind}: {count}" for kind, count in sorted(counts.items()))
    lines += ["", f"{len(documents)} documents" + (f" — {summary}." if summary else ".")]
    return "\n".join(lines) + "\n"


def allocate(
    root: Path,
    kind: str,
    register: dict[str, Any],
    documents: dict[str, Any],
    parent: str | None = None,
    today: date | None = None,
) -> str:
    """Allocate a code and hold it against peers before returning it.

    Computing a free code and taking it must be one operation from a peer's point of view, or two
    worktrees both compute the same code and the second finds out only at merge. Expired
    reservations are pruned first; the loop re-reads the store on each pass, so a code a peer took
    between this caller's read and its write is seen on the next candidate.
    """
    reservations.prune(root)
    for _ in range(RESERVATION_ATTEMPTS):
        code = next_code(kind, register, documents, parent, today,
                         reserved=reservations.active(root))
        if reservations.reserve(root, code):
            return code
    raise ValueError(
        f"could not reserve a {kind} code after {RESERVATION_ATTEMPTS} attempts; "
        f"inspect {reservations.reservation_dir(root)}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="next-code",
        description="Allocate the next free document code for a kind and reserve it against "
                    "every other worktree of this repository. Never choose a code by hand.",
    )
    parser.add_argument("kind", help="document kind, as the code register's series names it")
    parser.add_argument("--parent", metavar="DOC_ID",
                        help="allocate a sub-code under this plan's code")
    paths.add_arguments(parser, ["docs_root", "exempt_files", "backlog_path"])
    args = parser.parse_args(argv)
    import documents  # the document scan imports this module, so it is loaded on use

    config = paths.resolve(args)
    scan = documents.scan(config)
    if scan.errors:
        for error in scan.errors:
            print(error, file=sys.stderr)
        print("fix the document tree before allocating a code", file=sys.stderr)
        return 1
    try:
        print(allocate(config.root, args.kind, scan.register, scan.documents, args.parent))
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    except subprocess.CalledProcessError:
        print(f"{config.root} is not inside a git repository", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
