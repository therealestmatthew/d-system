#!/usr/bin/env python3
"""Validate the shell layouts and generate `ui-kit/dist/layouts.css` from them.

Each `ui-kit/layouts/<id>.json` is one fixed app-shell layout: the regions it uses and the grid
that places them. The React shell imports the same files, so the JSON is the only place a layout
is defined. Every file must pass `layouts/layout.schema.json` (JSON Schema draft 2020-12) and
these rules, which the schema cannot express:

    id               equals the file name without .json
    tracks           auto, Nfr or minmax(0, Nfr) only (the schema pattern; checked again here so
                     the message names the track)
    areas shape      every row names the same number of cells, and that number equals the
                     number of columns; the number of rows equals the number of row tracks
    regions          the set of names in areas equals the set in regions
    rectangles       each region's cells form one filled rectangle (CSS rejects any other shape)

The generated sheet has, per layout (sorted by id), inside one
`@media (width >= 64em)` block (the stacked single-column shell below 1024px is in layout.css):

    .ui-shell[data-layout="<id>"] { grid-template-columns / rows / areas }
    .ui-shell[data-layout="<id>"] > [data-region="<r>"] { grid-area: <r>; }   per region

and, after that block, for each layout that does not use every region the schema admits:

    .ui-shell[data-layout="<id>"] > [data-region]:not(<its regions>) { display: none; }

so a region element left in the markup does not land in an implicit grid track.

Determinism: layouts are sorted by id, regions keep their listed order; no clock or environment
is read; output is LF-terminated UTF-8.

    uv run python ui-kit/tools/build_layouts.py           # validate and rewrite dist/layouts.css
    uv run python ui-kit/tools/build_layouts.py --check   # exit 1 if invalid or stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

KIT = Path(__file__).resolve().parent.parent
LAYOUTS = KIT / "layouts"
SCHEMA_NAME = "layout.schema.json"
OUTPUT = KIT / "dist" / "layouts.css"

# 64em is 1024px at the browser's initial 16px; media queries resolve em against that, not the
# root font size, so the breakpoint does not move when the page's type changes.
WIDE_QUERY = "(width >= 64em)"
TRACK = re.compile(r"^(auto|\d+(\.\d+)?fr|minmax\(0, \d+(\.\d+)?fr\))$")


class LayoutError(Exception):
    """A layout file that fails the schema or a rule. The message names the file."""


@dataclass(frozen=True)
class Layout:
    id: str
    label: str
    regions: tuple[str, ...]
    columns: tuple[str, ...]
    rows: tuple[str, ...]
    areas: tuple[str, ...]


def load_schema(path: Path) -> dict[str, Any]:
    schema: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def schema_regions(path: Path) -> tuple[str, ...]:
    """Every region name the schema admits, in schema order."""
    regions: list[str] = load_schema(path)["$defs"]["region"]["enum"]
    return tuple(regions)


def rule_errors(data: dict[str, Any], stem: str) -> list[str]:
    """The rules beyond the schema, as messages. Assumes `data` already passed the schema."""
    errors: list[str] = []
    if data["id"] != stem:
        errors.append(f"id {data['id']!r} does not match the file name {stem!r}")
    grid = data["grid"]
    columns: list[str] = grid["columns"]
    rows: list[str] = grid["rows"]
    areas: list[str] = grid["areas"]
    for kind, tracks in (("column", columns), ("row", rows)):
        for track in tracks:
            if not TRACK.match(track):
                errors.append(f"{kind} track {track!r} is not auto, Nfr or minmax(0, Nfr)")
    cells = [row.split() for row in areas]
    if len(areas) != len(rows):
        errors.append(f"areas has {len(areas)} rows but rows has {len(rows)} tracks")
    for i, row_cells in enumerate(cells):
        if len(row_cells) != len(columns):
            errors.append(
                f"areas row {i + 1} {areas[i]!r} has {len(row_cells)} cells "
                f"but columns has {len(columns)} tracks"
            )
    named = {name for row_cells in cells for name in row_cells}
    listed = set(data["regions"])
    if named - listed:
        errors.append(f"areas names regions not in regions: {sorted(named - listed)}")
    if listed - named:
        errors.append(f"regions not placed in areas: {sorted(listed - named)}")
    if not errors:
        errors += _rectangle_errors(cells)
    return errors


def _rectangle_errors(cells: list[list[str]]) -> list[str]:
    errors: list[str] = []
    positions: dict[str, list[tuple[int, int]]] = {}
    for r, row_cells in enumerate(cells):
        for c, name in enumerate(row_cells):
            positions.setdefault(name, []).append((r, c))
    for name, spots in positions.items():
        r0 = min(r for r, _ in spots)
        r1 = max(r for r, _ in spots)
        c0 = min(c for _, c in spots)
        c1 = max(c for _, c in spots)
        if len(spots) != (r1 - r0 + 1) * (c1 - c0 + 1):
            errors.append(f"region {name!r} does not cover one rectangle in areas")
    return errors


def load_layout(path: Path, validator: Draft202012Validator) -> Layout:
    """Read and check one layout file; raise LayoutError naming the file on any failure."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LayoutError(f"{path.name}: not valid JSON: {exc}") from exc
    schema_errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if schema_errors:
        lines = [
            f"{path.name}: {'/'.join(str(p) for p in e.absolute_path) or '(root)'}: {e.message}"
            for e in schema_errors
        ]
        raise LayoutError("\n".join(lines))
    errors = rule_errors(data, path.stem)
    if errors:
        raise LayoutError("\n".join(f"{path.name}: {e}" for e in errors))
    grid = data["grid"]
    return Layout(
        id=data["id"],
        label=data["label"],
        regions=tuple(data["regions"]),
        columns=tuple(grid["columns"]),
        rows=tuple(grid["rows"]),
        areas=tuple(" ".join(row.split()) for row in grid["areas"]),
    )


def load_layouts(layouts_dir: Path, schema_path: Path) -> list[Layout]:
    validator = Draft202012Validator(load_schema(schema_path))
    files = sorted(p for p in layouts_dir.glob("*.json") if p.name != SCHEMA_NAME)
    if not files:
        raise LayoutError(f"no layout files in {layouts_dir}")
    failures: list[str] = []
    layouts: list[Layout] = []
    for path in files:
        try:
            layouts.append(load_layout(path, validator))
        except LayoutError as exc:
            failures.append(str(exc))
    if failures:
        raise LayoutError("\n".join(failures))
    return sorted(layouts, key=lambda lay: lay.id)


def render(layouts: list[Layout], all_regions: tuple[str, ...]) -> str:
    """The stylesheet text for the given layouts. `all_regions` is the schema's region enum."""
    lines = [
        "/*",
        "  ui-kit shell layouts. GENERATED: do not edit by hand.",
        "",
        "  Source:     ui-kit/layouts/*.json (schema: ui-kit/layouts/layout.schema.json)",
        "  Regenerate: uv run python ui-kit/tools/build_layouts.py",
        "  Check:      uv run python ui-kit/tools/build_layouts.py --check",
        "",
        '  Put data-layout="<id>" on .ui-shell. Below 1024px wide these rules do not apply and',
        "  layout.css stacks the regions in one column.",
        "  Layouts:",
        *(f"    {lay.id}: {lay.label}" for lay in layouts),
        "*/",
        "",
        f"@media {WIDE_QUERY} {{",
    ]
    for i, lay in enumerate(layouts):
        if i:
            lines.append("")
        shell = f'.ui-shell[data-layout="{lay.id}"]'
        lines += [
            f"  {shell} {{",
            f"    grid-template-columns: {' '.join(lay.columns)};",
            f"    grid-template-rows: {' '.join(lay.rows)};",
            "    grid-template-areas:",
            *(
                f'      "{row}"' + (";" if j == len(lay.areas) - 1 else "")
                for j, row in enumerate(lay.areas)
            ),
            "  }",
        ]
        for region in lay.regions:
            lines.append(f'  {shell} > [data-region="{region}"] {{ grid-area: {region}; }}')
    lines.append("}")
    hidden = [lay for lay in layouts if set(all_regions) - set(lay.regions)]
    if hidden:
        lines += ["", "/* Regions a layout does not use have no grid area; they are not shown. */"]
    for lay in hidden:
        used = ", ".join(f'[data-region="{r}"]' for r in lay.regions)
        lines.append(
            f'.ui-shell[data-layout="{lay.id}"] > [data-region]:not({used}) {{ display: none; }}'
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the shell layouts and build their CSS.")
    parser.add_argument("--check", action="store_true", help="exit 1 if the output is stale")
    parser.add_argument("--layouts", type=Path, default=LAYOUTS, help="layouts folder")
    parser.add_argument("--schema", type=Path, default=None, help="schema (default: in layouts)")
    parser.add_argument("--out", type=Path, default=OUTPUT, help="output CSS (default: kit dist)")
    args = parser.parse_args(argv)
    layouts_dir: Path = args.layouts
    schema_path: Path = args.schema or layouts_dir / SCHEMA_NAME
    out: Path = args.out
    try:
        text = render(load_layouts(layouts_dir, schema_path), schema_regions(schema_path))
    except LayoutError as exc:
        print(f"error: invalid layout\n{exc}", file=sys.stderr)
        return 1
    if args.check:
        current = out.read_text(encoding="utf-8") if out.is_file() else None
        if current != text:
            print(f"{out} is stale; run build_layouts.py", file=sys.stderr)
            return 1
        print(f"{out} matches the layouts")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
