"""Document code series, deterministic allocation and register consistency.

Two numbering modes exist. Counter series take the next free number in the series; dated series
derive their code from the document's own date plus a same-day sequence, so the kinds written
concurrently by several agents never contend on a single counter.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import PurePosixPath
from typing import Any

COUNTER = re.compile(r"^(?P<series>[A-Z]+)-(?P<number>[0-9]{3})(?:\.(?P<sub>[0-9]{2}))?$")
DATED = re.compile(
    r"^(?P<series>[A-Z]+)-(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})-(?P<sequence>[0-9]{2})$"
)


def parse_code(value: str) -> dict[str, Any] | None:
    """Split a code into its parts, or return None when it matches no grammar."""
    match = COUNTER.match(value)
    if match:
        stem = f"{match['series']}-{match['number']}"
        return {
            "series": match["series"],
            "numbering": "counter",
            "number": int(match["number"]),
            "sub": int(match["sub"]) if match["sub"] else None,
            "stem": stem,
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
    """Codes the ledger holds, mapped to the reason they cannot be freely allocated."""
    return {
        **{entry["code"]: "retired" for entry in register["retired"]},
        **{entry["code"]: "reserved" for entry in register["reserved"]},
    }


def allocated(register: dict[str, Any], documents: dict[str, Any]) -> list[str]:
    """Every code the repository has spent: in use, reserved or retired."""
    return [meta["code"] for meta in documents.values() if meta.get("code")] + list(
        held_codes(register)
    )


def next_code(
    kind: str,
    register: dict[str, Any],
    documents: dict[str, Any],
    parent: str | None = None,
    today: date | None = None,
) -> str:
    """The next free code for a kind; a pure function of committed repository state."""
    series = series_by_kind(register).get(kind)
    if not series:
        raise ValueError(f"no series is registered for kind {kind}")
    spent = [parsed for value in allocated(register, documents) if (parsed := parse_code(value))]
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
        parsed["sub"]
        for parsed in mine
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


def location_error(path: str, series: dict[str, Any]) -> str | None:
    if any(path.startswith(location) for location in series["locations"]):
        return None
    return f"{path}: {series['kind']} belongs under {' or '.join(series['locations'])}"


def naming_errors(
    path: str, code: str, parsed: dict[str, Any], series: dict[str, Any]
) -> list[str]:
    """The filename, and the plan folder holding it, must announce the document's code.

    A plan folder may group its children one level deeper under an area folder, whose name is
    a reader-facing label rather than a code. The overview stays at the plan folder's root, so
    only a sub-coded child may sit inside an area folder.
    """
    errors = []
    relative = next(
        PurePosixPath(path).relative_to(location)
        for location in series["locations"]
        if path.startswith(location)
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


def inspect_codes(register: dict[str, Any], documents: dict[str, Any], strict: bool) -> list[str]:
    """Check every document's code against the register, its kind, its path and its parent.

    strict turns on the rules that only hold once the tree is fully backfilled: a code is
    mandatory, and a filename must announce it.
    """
    errors: list[str] = []
    series_index = series_by_kind(register)
    held = held_codes(register)
    seen: dict[str, str] = {}

    for key, meta in sorted(documents.items()):
        path = meta["path"]
        code = meta.get("code")
        series = series_index.get(meta["kind"])
        if not series:
            errors.append(f"{path}: no series is registered for kind {meta['kind']}")
            continue
        message = location_error(path, series)
        if message:
            errors.append(message)
        if not code:
            if strict:
                errors.append(f"{path}: missing code; run --next-code {meta['kind']}")
            continue
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
        if strict and not message:
            errors.extend(naming_errors(path, code, parsed, series))
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
    """Order documents by series, then number or date, then sub-code; uncoded files last."""
    parsed = parse_code(meta["code"]) if meta.get("code") else None
    if not parsed:
        return (1, "", "", 0, meta["path"])
    if parsed["numbering"] == "counter":
        return (0, parsed["series"], f"{parsed['number']:03d}", parsed["sub"] or 0, meta["path"])
    return (0, parsed["series"], parsed["date"], parsed["sequence"], meta["path"])


def render_catalog(
    register: dict[str, Any], documents: dict[str, Any], items: list[dict[str, Any]]
) -> str:
    """Render the committed catalog. Derived from documents, the register and the backlog."""

    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    lines = [
        "# Documentation catalog",
        "",
        "Generated by `uv run python -m src.governance --catalog`. Never edit this file by hand;",
        "CI regenerates it and fails on any difference.",
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

    lines += [
        "",
        "## Plans and their phases",
        "",
        "| Code | Plan | Status | Queued | Active | Complete | Agents |",
        "|---|---|---|---|---|---|---|",
    ]
    for key, meta in ordered:
        if meta["kind"] != "plan":
            continue
        phases = [
            item
            for item in items
            if key in [item["plan"], *item["sources"]] and item["status"] != "cancelled"
        ]
        states = [item["status"] for item in phases]
        agents = sorted({item["agent"] for item in phases if item.get("agent")})
        lines.append(
            f"| {meta.get('code', '—')} | {key} | {meta['status']} | "
            f"{states.count('queued')} | {states.count('active')} | "
            f"{states.count('complete')} | {', '.join(agents) or '—'} |"
        )

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
    lines += ["", f"{len(documents)} documents — {summary}."]
    return "\n".join(lines)
