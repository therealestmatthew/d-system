#!/usr/bin/env python3
"""Structured JSON over the adversarial literature-review campaign — `REQ-027` R05's extractor.

The campaign ([PLAN-023](../docs/01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md))
left fourteen files in `research/literature-review/` and nothing that renders them. This tool reads
those files and emits the structured form the report's later phases render; it writes no HTML and
touches nothing under `_public/`.

Every number it emits is measured from the files at run time. No count is restated from prose, and
no figure is recomputed downstream — that split is what `REQ-027` R05 means by "the generator
computes nothing", and it is what makes `phase-lrr-04`'s drift test meaningful.

The tool makes no model or network call and asks the wall clock for nothing: the output is a pure
function of the fourteen files, so two runs against an unchanged tree produce byte-identical bytes.
Three things carry that guarantee, and each has its own test:

- `Path.glob()` has no guaranteed order across platforms or filesystems, so every glob result is
  passed through `sorted()` before anything reads it.
- Every dict is emitted through `json.dumps(..., sort_keys=True)` and every list is built in a
  defined order.
- CSV cells stay strings. Round-tripping a numeric-looking cell through `float()` would rewrite
  `04` as `4.0` and `1e5` as `100000.0`, which is a silent edit to the corpus.

What comes out, per `phase-lrr-01`'s scope:

- `deliverables` — the fourteen files matching `[0-9][0-9]_*`, each with its anchor, its byte count
  and digest, and, for the thirteen Markdown files, the full source text for `phase-lrr-02` to
  render. `CLAUDE.md` and `HANDOFF.md` sit in the same directory and fall outside that glob; they
  are the campaign's own working instructions, not deliverables.
- `tables` — the three CSVs as `columns` plus `rows` (a list of row lists, aligned to `columns`).
- `collisions` — the 30 sections of `05_critical_collisions.md`, each joined to its matrix row.
- `hypotheses` — the 11 `H1`-`H11` blocks of `06_hypothesis_tests.md`.
- `counts` — every figure the report needs, measured here so no renderer computes one.

Anchors are keyed on the **slug**, not the section number. `05`'s headings read `## 3. <slug>`, and
that slug is a `source_id` in `04_evidence_matrix.csv`, so keying on it survives a renumbering of
the file and doubles as the join key to the matrix. Hypothesis anchors key on the `H<n>` token for
the same reason: the descriptive title after the em dash can be rewritten without breaking a link.

    uv run python tools/lit_report_extract.py               # print to stdout
    uv run python tools/lit_report_extract.py --out FILE    # write to FILE instead

This tool never writes to `research/literature-review/`. Defects it surfaces in the corpus are
findings to report, not repairs to make — see `PLAN-043`'s out-of-scope section.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "research" / "literature-review"

#: The deliverable set, as a glob rather than a list of fourteen names. `REQ-027` R01 defines the
#: set as "the files matching `research/literature-review/[0-9][0-9]_*` on disk", so a file added
#: to that directory must appear here rather than being silently dropped by a hardcoded roster.
DELIVERABLE_GLOB = "[0-9][0-9]_*"

#: `## 3. em-llm-human-inspired-episodic-memory-infinite-context-2024` in `05`. The number is
#: captured for display order and the slug for identity; see the module docstring on why the
#: anchor keys on the slug.
COLLISION_HEADING = re.compile(r"^## (?P<number>\d+)\.\s+(?P<slug>\S+)\s*$")

#: `## H4 — Independence-aware convergence` in `06`. `06` also carries a `## Summary table`
#: heading, which this pattern excludes by requiring the `H<n>` token.
HYPOTHESIS_HEADING = re.compile(r"^## (?P<id>H\d+)\b\s*(?:[-—–]\s*)?(?P<title>.*?)\s*$")

#: The three CSVs, by the key the report refers to them by. Each is also a deliverable; this map
#: is only about which of them get parsed as tables.
TABLES = {
    "ledger": "00_search_ledger.csv",
    "inventory": "03_source_inventory.csv",
    "matrix": "04_evidence_matrix.csv",
}

#: `04_evidence_matrix.csv`'s `second_review` is prose, not an enum: it opens with a verdict word
#: and continues into commentary ("disputed: reviewer re-derives component_overlap to 3 ..."). The
#: verdict is derived from that opening token so `REQ-027` R07's 18-of-30 count is assertable,
#: while the prose is carried through untouched so nothing of the reviewer's reasoning is lost.
#: A value matching none of these becomes `unrecognised` rather than a guess, so a future edit to
#: the corpus surfaces as a visible value instead of a silent miscount.
SECOND_REVIEW_VERDICTS = ("confirmed", "disputed", "not_applicable")


class ExtractError(Exception):
    """A corpus the extractor cannot read as the report's structure assumes."""


def _slug_to_anchor(prefix: str, slug: str) -> str:
    """An HTML-id-safe anchor. Lowercased, and anything outside `[a-z0-9]` becomes a hyphen."""
    cleaned = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    return f"{prefix}-{cleaned}"


def discover_deliverables(corpus: Path) -> list[Path]:
    """The deliverable files, in filename order.

    `Path.glob()` makes no ordering guarantee — it yields whatever `os.scandir()` yields, which is
    filesystem order and differs between machines. Sorting here is the whole of the determinism
    guarantee for the deliverable list, the anchors derived from it, and the `counts` that follow.
    """
    return sorted(corpus.glob(DELIVERABLE_GLOB))


def _read_table(path: Path) -> dict[str, Any]:
    """One CSV as `columns` plus `rows`, with every cell left as the string the file holds."""
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            columns = next(reader)
        except StopIteration as exc:
            raise ExtractError(f"{path.name} is empty: no header row") from exc
        rows = [row for row in reader]

    ragged = [i for i, row in enumerate(rows, start=2) if len(row) != len(columns)]
    if ragged:
        raise ExtractError(
            f"{path.name}: {len(ragged)} row(s) do not match the {len(columns)}-column header; "
            f"first at line {ragged[0]}"
        )
    return {
        "anchor": _slug_to_anchor("table", path.stem),
        "filename": path.name,
        "columns": columns,
        "column_count": len(columns),
        "rows": rows,
        "row_count": len(rows),
    }


def _split_blocks(
    text: str, pattern: re.Pattern[str]
) -> list[tuple[re.Match[str], int, int, str]]:
    """Every `## ` block whose heading matches `pattern`, as (match, start line, end line, body).

    A block runs from its own heading to the line before the next `## ` heading of any kind, or to
    the end of the file. Trailing blank lines are dropped so the body does not vary with how much
    whitespace separates one section from the next. Line numbers are 1-based and inclusive.
    """
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    blocks: list[tuple[re.Match[str], int, int, str]] = []
    for position, start in enumerate(starts):
        match = pattern.match(lines[start])
        if match is None:
            continue
        stop = starts[position + 1] if position + 1 < len(starts) else len(lines)
        body = lines[start:stop]
        while body and not body[-1].strip():
            body.pop()
        blocks.append((match, start + 1, start + len(body), "\n".join(body)))
    return blocks


def extract_collisions(text: str, matrix: dict[str, Any]) -> list[dict[str, Any]]:
    """The collision sections of `05`, each joined to its `04` row by slug.

    The join is what lets `REQ-027` R07 be checked: the verdict lives in the matrix's
    `second_review`, the prose lives in `05`, and the two are tied together by the slug the
    heading already carries.
    """
    by_source_id = _matrix_rows_by_source_id(matrix)
    collisions: list[dict[str, Any]] = []
    for match, line_start, line_end, body in _split_blocks(text, COLLISION_HEADING):
        slug = match["slug"]
        row = by_source_id.get(slug)
        second_review = row.get("second_review", "") if row is not None else ""
        collisions.append(
            {
                "anchor": _slug_to_anchor("collision", slug),
                "slug": slug,
                "number": int(match["number"]),
                "heading": match.group(0).removeprefix("## "),
                "line_start": line_start,
                "line_end": line_end,
                "markdown": body,
                "matrix_row": slug if row is not None else None,
                "second_review": second_review,
                "second_review_verdict": classify_second_review(second_review),
            }
        )
    return collisions


def classify_second_review(value: str) -> str:
    """The verdict word opening a `second_review` cell, or `unrecognised`.

    The field is prose. Its first token is the verdict and everything after it is commentary,
    punctuated inconsistently across nine sessions (`confirmed,`, `confirmed;`, `disputed:`), so
    the token is taken up to the first character that is not a letter or underscore.
    """
    token = re.match(r"[A-Za-z_]+", value.strip())
    if token is None:
        return "unrecognised" if value.strip() else "none"
    word = token.group(0).lower()
    return word if word in SECOND_REVIEW_VERDICTS else "unrecognised"


def _matrix_rows_by_source_id(matrix: dict[str, Any]) -> dict[str, dict[str, str]]:
    """The matrix keyed by `source_id`. A duplicated id keeps its first row; see `counts`."""
    columns: list[str] = matrix["columns"]
    index = columns.index("source_id")
    keyed: dict[str, dict[str, str]] = {}
    for row in matrix["rows"]:
        keyed.setdefault(row[index], dict(zip(columns, row, strict=True)))
    return keyed


def extract_hypotheses(text: str) -> list[dict[str, Any]]:
    """The `H1`-`H11` blocks of `06`, keyed on the `H<n>` token rather than the heading text."""
    hypotheses: list[dict[str, Any]] = []
    for match, line_start, line_end, body in _split_blocks(text, HYPOTHESIS_HEADING):
        hypothesis_id = match["id"]
        hypotheses.append(
            {
                "anchor": _slug_to_anchor("hypothesis", hypothesis_id),
                "id": hypothesis_id,
                "number": int(hypothesis_id[1:]),
                "title": match["title"],
                "heading": match.group(0).removeprefix("## "),
                "line_start": line_start,
                "line_end": line_end,
                "markdown": body,
            }
        )
    return hypotheses


def _read_deliverable(path: Path) -> dict[str, Any]:
    """One deliverable's identity and, for a Markdown file, its full source text."""
    raw = path.read_bytes()
    number, _, stem = path.stem.partition("_")
    entry: dict[str, Any] = {
        "anchor": _slug_to_anchor("deliverable", path.stem),
        "filename": path.name,
        "number": number,
        "slug": stem,
        "format": path.suffix.lstrip(".").lower(),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    if entry["format"] == "md":
        text = raw.decode("utf-8")
        entry["markdown"] = text
        entry["line_count"] = len(text.splitlines())
    return entry


def _duplicate_source_ids(table: dict[str, Any]) -> list[str]:
    """`source_id` values appearing on more than one row, sorted.

    The inventory has two of these (idea `000308`). They are reported, never deduplicated: the
    report renders the corpus as it stands, and a repair here would hide a tracked defect.
    """
    index: int = table["columns"].index("source_id")
    seen: dict[str, int] = {}
    for row in table["rows"]:
        seen[row[index]] = seen.get(row[index], 0) + 1
    return sorted(source_id for source_id, count in seen.items() if count > 1)


def _counts(
    deliverables: list[dict[str, Any]],
    tables: dict[str, dict[str, Any]],
    collisions: list[dict[str, Any]],
    hypotheses: list[dict[str, Any]],
) -> dict[str, Any]:
    """Every figure the report shows, measured here so no renderer computes one."""
    verdicts: dict[str, int] = {verdict: 0 for verdict in SECOND_REVIEW_VERDICTS}
    verdicts["unrecognised"] = 0
    verdicts["none"] = 0
    for collision in collisions:
        verdicts[collision["second_review_verdict"]] += 1

    counts: dict[str, Any] = {
        "collision_sections": len(collisions),
        "collision_second_review": verdicts,
        "deliverables": len(deliverables),
        "deliverables_csv": sum(1 for entry in deliverables if entry["format"] == "csv"),
        "deliverables_markdown": sum(1 for entry in deliverables if entry["format"] == "md"),
        "hypothesis_blocks": len(hypotheses),
    }
    for key, table in sorted(tables.items()):
        counts[f"{key}_columns"] = table["column_count"]
        counts[f"{key}_rows"] = table["row_count"]
    return counts


def extract(corpus: Path = CORPUS) -> dict[str, Any]:
    """The whole structured form, as a plain dict. The CLI is a thin wrapper over this."""
    if not corpus.is_dir():
        raise ExtractError(f"corpus directory not found: {corpus}")

    paths = discover_deliverables(corpus)
    if not paths:
        raise ExtractError(f"no files match {DELIVERABLE_GLOB} under {corpus}")
    deliverables = [_read_deliverable(path) for path in paths]

    by_name = {path.name: path for path in paths}
    missing = sorted(name for name in TABLES.values() if name not in by_name)
    if missing:
        raise ExtractError(f"expected CSV deliverable(s) missing: {', '.join(missing)}")
    tables = {key: _read_table(by_name[name]) for key, name in sorted(TABLES.items())}

    def _markdown(name: str) -> str:
        path = by_name.get(name)
        if path is None:
            raise ExtractError(f"expected Markdown deliverable missing: {name}")
        return path.read_text(encoding="utf-8")

    collisions = extract_collisions(_markdown("05_critical_collisions.md"), tables["matrix"])
    hypotheses = extract_hypotheses(_markdown("06_hypothesis_tests.md"))

    anchors = [entry["anchor"] for entry in (*deliverables, *collisions, *hypotheses)]
    anchors += [table["anchor"] for table in tables.values()]
    duplicates = sorted({anchor for anchor in anchors if anchors.count(anchor) > 1})
    if duplicates:
        raise ExtractError(f"anchor ids are not unique: {', '.join(duplicates)}")

    return {
        "collisions": collisions,
        "counts": _counts(deliverables, tables, collisions, hypotheses),
        "deliverables": deliverables,
        "hypotheses": hypotheses,
        "known_defects": {
            "duplicate_inventory_source_ids": _duplicate_source_ids(tables["inventory"]),
            "unmatched_collision_slugs": sorted(
                collision["slug"] for collision in collisions if collision["matrix_row"] is None
            ),
        },
        "tables": tables,
    }


def render(data: dict[str, Any]) -> str:
    """The emitted bytes. `sort_keys` is what makes two runs byte-identical, not merely equal."""
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", type=Path, default=None, help="write the JSON here instead of stdout"
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=CORPUS,
        help=f"read the campaign files from here instead of {CORPUS.relative_to(ROOT)}",
    )
    args = parser.parse_args(argv)

    try:
        rendered = render(extract(args.corpus))
    except ExtractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
