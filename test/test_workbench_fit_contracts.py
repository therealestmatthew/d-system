"""Content-fit contracts for workbench panels and floating surfaces (REQ-037, REQ-011 R09/R10).

`docs/06-requirements/REQ-037-workbench-content-fit-contracts.md` declares, per panel type, how
each region of the panel behaves when its content exceeds its box: fills, scrolls, wraps,
truncates, or is never allowed to clip. Its two tables are the machine-readable contract; this
module reads them.

Two halves, run differently:

**Static half (pytest, always runs, no browser).** Discovers the registered panel types by
parsing `PANEL_REGISTRY` in `ts/src/workbench/panelRegistry.tsx`, and fails when a registered type
has no contract row, when a contract row names a type that is not registered, when a type lacks
the mandatory slot-fill row, when a contract selector names a CSS class that no longer exists in
`ts/src`, or when a floating surface (a component portaled into `document.body`, or a tooltip)
exists in source without a contract row. The judge that turns browser measurements into
violations is also pure Python and is unit-tested here against synthetic measurements, including
the five instances the contract exists to catch.

**Live half (a command, not a pytest test).** `python test/test_workbench_fit_contracts.py --live
<url>` drives Chromium through Playwright, seeds every layout x registered panel x eligible slot x
required window size, measures every contract region, and judges the measurements with the same
judge. `--self-test` additionally breaks each panel's own contract with injected CSS and requires
the judge to notice. It is not a pytest test because it needs a running workbench, Chromium and
Node Playwright; a pytest test that silently passes without them would be the vacuous pass this
module exists to prevent. The live half exits non-zero on any violation, and on any scroll rule
that no cell exercised.

Discovery is by parsing source text, not by a generated manifest. It cannot pass vacuously because
the static half cross-checks the parse three ways: the key count must equal the `displayName:`
count and the `Component:` count inside the same block, every panel id in the layout files must be
registered, and every registered id must appear in at least one layout (otherwise the live half
could never measure it).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "06-requirements" / "REQ-037-workbench-content-fit-contracts.md"
REGISTRY_PATH = ROOT / "ts" / "src" / "workbench" / "panelRegistry.tsx"
TS_SRC = ROOT / "ts" / "src"
LAYOUTS_DIR = ROOT / "_data" / "workbench" / "layouts"

# REQ-006 R02 / REQ-007: the four window sizes every browser-facing row is verified at.
REQUIRED_SIZES: tuple[tuple[int, int], ...] = ((1280, 720), (1366, 768), (1920, 1080), (1024, 768))

# Slot-body padding the panel root may leave unfilled on each axis, in px. Measured: the multi-panel
# slot body sits 19-20 px larger than the panel root in both axes (10 px padding a side).
ROOT_FILL_TOLERANCE_PX = 24.0
# How far short of the panel root's bottom/right edge a fill region may stop. Measured against the
# panel root, not the slot body: the ~98 px of legitimate chrome (slot header, panel header, tab
# bar) is what defeats a naive "terminal height vs slot height" check, and is also why the check
# is anchored on the root.
REGION_FILL_TOLERANCE_PX = 32.0
BOUNDS_TOLERANCE_PX = 1.5

# CSS classes owned by a library, not by `ts/src`, so the selector-grounding check cannot find
# them in source.
LIBRARY_CLASSES = frozenset({"xterm", "xterm-viewport", "scrollbar", "vertical"})
# A popover may open this far short of the room it could use before it counts as starved. 15%
# keeps the idea 000117 case (142 px bubble, 432 px available) flagged while ignoring the few
# pixels by which a clamp to one side of the trigger can miss the larger side.
STARVED_BELOW_FRACTION = 0.85
# A tracked directory with more than twenty compatible files, seeded into the HTML Viewer so its
# file selector popover has a list long enough to need a height decision (REQ-012 R25).
STRESS_VIEWER_DIRECTORY = "_public/engine/trace"
SCROLL_MODES = frozenset({"scroll-y", "scroll-x", "scrollbar"})
# Smallest box a scroller, marquee, visible region or wrapping header may have before it counts as
# collapsed (instance 1). A scrollbar track is narrow by design, so only its height is floored.
MIN_BOX_PX = 16.0
MIN_TRACK_WIDTH_PX = 4.0
# Style properties whose animation moves content horizontally; an opacity fade is not motion.
MOTION_PROPERTIES = ("transform", "translate", "left", "marginLeft", "textIndent")

PANEL_MODES = frozenset(
    {"fill", "frame", "scroll-y", "scroll-x", "scrollbar", "marquee", "wrap", "truncate", "visible"}
)
SURFACE_MODES = frozenset(
    {"in-viewport", "not-clipped", "not-starved", "dismiss-visible", "text-fits"}
)
MODE_ARGS: dict[str, frozenset[str]] = {
    "fill": frozenset({"min-h", "min-w", "tol"}),
    "scroll-y": frozenset({"min-h", "min-w"}),
    "scroll-x": frozenset({"min-h", "min-w"}),
    "scrollbar": frozenset({"min-h", "min-w"}),
    "marquee": frozenset({"min-h", "min-w"}),
    "wrap": frozenset({"min-h", "min-w"}),
    "visible": frozenset({"min-h", "min-w"}),
    "frame": frozenset({"min-h"}),
}


# ---------------------------------------------------------------------------------------------
# Contract parsing
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Alt:
    """One acceptable behavior for a region: a mode name and its numeric arguments."""

    name: str
    args: tuple[tuple[str, float], ...] = ()

    def arg(self, key: str, default: float) -> float:
        return dict(self.args).get(key, default)


@dataclass(frozen=True)
class Rule:
    """One contract row: a region of a panel (or floating surface) and how it may overflow.

    `alts` are alternatives joined by `or` in the table; the rule holds when any one holds, which
    is how the notes strip declares both vertical scroll and the horizontal-scroll rotator variant
    as acceptable. `optional` marks a region that exists only in some states (an xterm exists only
    where the shell is available); absence is then recorded as not applicable, never as a pass.
    """

    owner: str
    region: str
    selector: str
    alts: tuple[Alt, ...]
    optional: bool = False
    source: str = ""


@dataclass
class Contract:
    panels: dict[str, list[Rule]] = field(default_factory=dict)
    surfaces: dict[str, list[Rule]] = field(default_factory=dict)

    def surface_sources(self) -> set[str]:
        return {rule.source for rules in self.surfaces.values() for rule in rules}


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _unquote(cell: str) -> str:
    return cell.strip().strip("`").strip()


def parse_alts(cell: str) -> tuple[tuple[Alt, ...], bool]:
    """Parse a mode cell such as `scroll-y or scroll-x optional` or `fill(min-h=48)`."""
    text = _unquote(cell)
    optional = False
    if text.endswith(" optional"):
        optional = True
        text = text[: -len(" optional")].strip()
    alts: list[Alt] = []
    for part in re.split(r"\s+or\s+", text):
        match = re.fullmatch(r"([a-z-]+)(?:\(([^)]*)\))?", part.strip())
        if not match:
            raise ValueError(f"unparseable mode {part!r} in cell {cell!r}")
        args: list[tuple[str, float]] = []
        if match.group(2):
            for pair in match.group(2).split(","):
                key, _, value = pair.partition("=")
                args.append((key.strip(), float(value)))
        alts.append(Alt(match.group(1), tuple(args)))
    return tuple(alts), optional


def _table_after(markdown: str, heading: str) -> list[list[str]]:
    """The cell rows (header excluded) of the first pipe table after the given heading."""
    lines = markdown.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        raise ValueError(f"contract document has no heading {heading!r}") from None
    rows: list[list[str]] = []
    in_table = False
    for line in lines[start + 1 :]:
        if line.startswith("|"):
            in_table = True
            rows.append(_cells(line))
        elif in_table:
            break
    # rows[0] is the header, rows[1] the separator line
    return rows[2:]


def parse_contract(markdown: str) -> Contract:
    contract = Contract()
    for owner, region, selector, mode, _basis in (
        row[:5] for row in _table_after(markdown, "## Panel contract table")
    ):
        alts, optional = parse_alts(mode)
        contract.panels.setdefault(_unquote(owner), []).append(
            Rule(_unquote(owner), region, _unquote(selector), alts, optional)
        )
    for owner, source, selector, mode, _basis in (
        row[:5] for row in _table_after(markdown, "## Floating surface contract table")
    ):
        alts, optional = parse_alts(mode)
        contract.surfaces.setdefault(_unquote(owner), []).append(
            Rule(_unquote(owner), "bubble", _unquote(selector), alts, optional, _unquote(source))
        )
    return contract


def load_contract() -> Contract:
    return parse_contract(CONTRACT_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------------------------


def registry_block(source: str) -> str:
    """The text of the `PANEL_REGISTRY` object literal, braces included."""
    match = re.search(r"export const PANEL_REGISTRY[^=]*=\s*\{", source)
    if not match:
        raise ValueError("PANEL_REGISTRY object literal not found in panelRegistry.tsx")
    depth = 0
    for index in range(match.end() - 1, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[match.end() - 1 : index + 1]
    raise ValueError("PANEL_REGISTRY object literal is not closed")


def scan_ts(text: str) -> tuple[str, list[str]]:
    """Split TypeScript source into (code with comments removed, string literal contents).

    A small scanner, not a parser: it understands line and block comments and single, double and
    template strings. An unterminated single or double quote (an apostrophe in JSX text) is treated
    as an ordinary character so one stray quote cannot swallow the rest of the file.
    """
    code: list[str] = []
    strings: list[str] = []
    i, n = 0, len(text)
    while i < n:
        char, pair = text[i], text[i : i + 2]
        if pair == "//":
            end = text.find("\n", i)
            i = n if end == -1 else end
        elif pair == "/*":
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
        elif char in "'\"`":
            j = i + 1
            while j < n and text[j] != char:
                if text[j] == "\\":
                    j += 1
                elif text[j] == "\n" and char != "`":
                    break
                j += 1
            if j < n and text[j] == char:
                strings.append(text[i + 1 : j])
                code.append(text[i : j + 1])
                i = j + 1
            else:
                code.append(char)
                i += 1
        else:
            code.append(char)
            i += 1
    return "".join(code), strings


def class_names_in_source(texts: Iterable[str]) -> set[str]:
    """Class names that appear as whole tokens inside string literals of the given sources.

    Whole tokens, not substrings: `stage-file-browser__tree` is not found inside
    `stage-file-browser__tree-item`. Comments are excluded, and so is anything outside a string
    literal, so only a class an element can actually be given counts as existing.
    """
    names: set[str] = set()
    for text in texts:
        for literal in scan_ts(text)[1]:
            names.update(t for t in re.split(r"\s+|\$\{[^}]*\}", literal) if t)
    return names


def registered_panel_types(source: str) -> list[str]:
    """Registered panel type ids, parsed from the registry source.

    Keys are the entries opening at the literal's own indent: `'id': {` or `id: {`.
    """
    block = registry_block(source)
    keys = re.findall(r"^  (?:'([^']+)'|([A-Za-z_]\w*))\s*:\s*\{", block, flags=re.MULTILINE)
    return [quoted or bare for quoted, bare in keys]


_ENTRY_LINE = re.compile(r"""(?:'[^']+'|"[^"]+"|[A-Za-z_]\w*)\s*:\s*\{""")
_REGISTRY_MUTATIONS = (
    r"PANEL_REGISTRY\s*\[[^\]]*\]\s*=(?!=)",
    r"PANEL_REGISTRY\s*\.\s*\w+\s*=(?!=)",
    r"PANEL_REGISTRY\s*=(?!=)",
    r"\b(?:assign|defineProperty|defineProperties|set)\s*\(\s*PANEL_REGISTRY\b",
)


def assert_registry_parse_is_sound(source: str, ids: list[str]) -> None:
    """Fail when the parse could be silently missing or inventing entries.

    Three guards: the key count must equal the `displayName:` and `Component:` counts; every line
    at the literal's own indent must open a `key: {` entry (a spread or a factory call there would
    register a type this parse cannot see); and nothing else in the file may assign to the registry.
    """
    code = scan_ts(source)[0]
    block = registry_block(code)
    assert ids, "no panel types parsed from PANEL_REGISTRY: discovery is vacuous"
    assert len(set(ids)) == len(ids), f"duplicate panel type ids parsed: {ids}"
    display_names = len(re.findall(r"\bdisplayName\s*:", block))
    components = len(re.findall(r"\bComponent\s*:", block))
    assert len(ids) == display_names == components, (
        f"parsed {len(ids)} panel ids but the registry block holds {display_names} displayName "
        f"and {components} Component entries; the discovery regex has drifted from the source"
    )
    body = [line for line in block.splitlines()[1:-1] if line.strip()]
    indent = len(body[0]) - len(body[0].lstrip()) if body else 0
    for line in body:
        if len(line) - len(line.lstrip()) != indent:
            continue
        text = line.strip()
        if _ENTRY_LINE.match(text) or text.startswith("}"):
            continue
        raise AssertionError(
            f"registry line {text!r} is not a `key: {{` entry: a spread or call there registers "
            f"panel types the discovery cannot see; write each entry as a literal"
        )
    for pattern in _REGISTRY_MUTATIONS:
        found = re.search(pattern, code)
        assert not found, (
            f"PANEL_REGISTRY is modified outside its literal ({found.group(0)!r}); a type "
            f"registered that way is invisible to discovery"
        )


def checked_panel_types(source: str) -> list[str]:
    """`registered_panel_types` that refuses a registry the parse cannot be trusted on."""
    ids = registered_panel_types(source)
    assert_registry_parse_is_sound(source, ids)
    return ids


def layout_panel_ids() -> dict[str, set[str]]:
    """layout_id -> the panel ids its file declares."""
    result: dict[str, set[str]] = {}
    for path in sorted(LAYOUTS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        result[data["layout_id"]] = {panel["panel_id"] for panel in data["panels"]}
    return result


def undeclared_panels(registered: Iterable[str], contract: Contract) -> list[str]:
    return sorted(set(registered) - set(contract.panels))


def stale_contract_panels(registered: Iterable[str], contract: Contract) -> list[str]:
    return sorted(set(contract.panels) - set(registered))


def assert_every_panel_declared(registered: Iterable[str], contract: Contract) -> None:
    """The REQ-011 R10 check: an undeclared panel type fails here and is named."""
    missing = undeclared_panels(registered, contract)
    assert not missing, (
        f"panel type(s) {missing} are registered in panelRegistry.tsx but have no row in the "
        f"panel contract table of {CONTRACT_PATH.name}; declare how each overflows"
    )


def floating_surface_sources(ts_src: Path) -> set[str]:
    """Repo-relative paths of source files that create a floating surface.

    A floating surface is a component portaled into `document.body` (a popover, a context menu)
    or a tooltip bubble (`role="tooltip"`). Panel portals into a panel host are not floating
    surfaces.
    """
    found: set[str] = set()
    for path in sorted(ts_src.rglob("*.tsx")):
        if ".test." in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        portals_to_body = bool(re.search(r"createPortal\([\s\S]*?document\.body", text))
        if portals_to_body or 'role="tooltip"' in text:
            base = ROOT if ts_src.is_relative_to(ROOT) else ts_src
            found.add(path.relative_to(base).as_posix())
    return found


def selector_classes(selector: str) -> set[str]:
    without_attrs = re.sub(r"\[[^\]]*\]", "", selector)
    return set(re.findall(r"\.([A-Za-z_][\w-]*)", without_attrs))


def source_class_names(ts_src: Path) -> set[str]:
    """Class names in the `.tsx` sources (comments and tests excluded), as whole string tokens."""
    return class_names_in_source(
        path.read_text(encoding="utf-8")
        for path in sorted(ts_src.rglob("*.tsx"))
        if ".test." not in path.name
    )


# ---------------------------------------------------------------------------------------------
# Judge: measurements in, violations out. Pure Python, no browser.
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    where: str
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"{self.where}: {self.rule}: {self.detail}"


def _bounded(region: dict[str, Any], root: dict[str, Any]) -> bool:
    tol = BOUNDS_TOLERANCE_PX
    return bool(
        region["x"] >= root["x"] - tol
        and region["y"] >= root["y"] - tol
        and region["r"] <= root["r"] + tol
        and region["b"] <= root["b"] + tol
    )


def _fmt(region: dict[str, Any]) -> str:
    return (
        f"box {region['w']:.0f}x{region['h']:.0f} at ({region['x']:.0f},{region['y']:.0f}), "
        f"bottom {region['b']:.0f}, right {region['r']:.0f}"
    )


def _too_small(
    alt: Alt, region: dict[str, Any], *, min_w: float = MIN_BOX_PX, min_h: float = MIN_BOX_PX
) -> str | None:
    """A region smaller than its floor is collapsed, whatever else it satisfies."""
    need_w, need_h = alt.arg("min-w", min_w), alt.arg("min-h", min_h)
    if region["w"] < need_w or region["h"] < need_h:
        return (
            f"region is {region['w']:.0f}x{region['h']:.0f}, below the minimum "
            f"{need_w:.0f}x{need_h:.0f}"
        )
    return None


def _clipped_on(region: dict[str, Any], axis: str) -> bool:
    """True when content exceeds the box on `axis` and overflow there is hidden or clipped."""
    if axis == "y":
        return bool(region["oy"] in {"hidden", "clip"} and region["sh"] > region["ch"] + 1)
    return bool(region["ox"] in {"hidden", "clip"} and region["sw"] > region["cw"] + 1)


def check_alt(
    alt: Alt, selector: str, region: dict[str, Any], root: dict[str, Any], body: dict[str, Any]
) -> str | None:
    """None when the region satisfies the mode; otherwise the reason it does not."""
    name = alt.name
    if name == "fill" and selector == ":root":
        tol = alt.arg("tol", ROOT_FILL_TOLERANCE_PX)
        gap_h, gap_w = body["h"] - root["h"], body["w"] - root["w"]
        if not _bounded(root, body):
            return f"panel box leaves its slot body ({_fmt(root)} vs slot body {_fmt(body)})"
        if gap_h > tol or gap_w > tol:
            return (
                f"panel box {root['w']:.0f}x{root['h']:.0f} does not fill its slot body "
                f"{body['w']:.0f}x{body['h']:.0f} (gap {gap_w:.0f}x{gap_h:.0f}, "
                f"tolerance {tol:.0f})"
            )
        return None
    if name == "fill":
        tol = alt.arg("tol", REGION_FILL_TOLERANCE_PX)
        min_h, min_w = alt.arg("min-h", 1), alt.arg("min-w", 1)
        if region["h"] < min_h or region["w"] < min_w:
            return (
                f"region is {region['w']:.0f}x{region['h']:.0f}, below the floor "
                f"{min_w:.0f}x{min_h:.0f}"
            )
        if not _bounded(region, root):
            return f"region leaves its panel box ({_fmt(region)} vs panel {_fmt(root)})"
        if root["b"] - region["b"] > tol:
            return (
                f"region stops {root['b'] - region['b']:.0f}px short of the panel bottom "
                f"(tolerance {tol:.0f})"
            )
        return None
    if name == "frame":
        if region["h"] < alt.arg("min-h", 1) or region["w"] < 1:
            return (
                f"frame is {region['w']:.0f}x{region['h']:.0f}, below the floor "
                f"{alt.arg('min-h', 1):.0f}px high"
            )
        if not _bounded(region, root):
            return f"frame leaves its panel box ({_fmt(region)} vs panel {_fmt(root)})"
        return None
    if name == "scrollbar":
        # xterm 6 scrolls through its own virtual scrollbar, not a native overflow box: its
        # `.xterm-viewport` reports overflow `scroll` but never moves. The scrollbar track must be
        # bounded by the panel and carry a slider.
        small = _too_small(alt, region, min_w=MIN_TRACK_WIDTH_PX)
        if small:
            return small
        if not _bounded(region, root):
            return f"scrollbar track is not bounded by its panel: {_fmt(region)} vs {_fmt(root)}"
        if region.get("slider") is None:
            return "scrollbar has no slider element"
        return None
    if name in {"scroll-y", "scroll-x"}:
        axis, cross = ("y", "x") if name == "scroll-y" else ("x", "y")
        small = _too_small(alt, region)
        if small:
            return small
        if not _bounded(region, root):
            return (
                f"scroller is not bounded by its panel: {_fmt(region)} vs panel {_fmt(root)}, "
                f"so its content is cut off by an ancestor instead of scrolling"
            )
        overflow = region["oy" if axis == "y" else "ox"]
        if overflow not in {"auto", "scroll"}:
            return f"computed overflow-{axis} is {overflow!r}, which cannot scroll"
        if _clipped_on(region, cross):
            return (
                f"content is clipped on {cross} ({region['sw']:.0f}x{region['sh']:.0f} in a "
                f"{region['cw']:.0f}x{region['ch']:.0f} box, overflow-{cross} "
                f"{region['o' + cross]!r}): scrolling {axis} leaves part of it unreachable"
            )
        reach = (region.get("reach") or {}).get(axis)
        if reach is False:
            return f"content exceeds the box on {axis} but scrolling does not move it"
        return None
    if name == "marquee":
        small = _too_small(alt, region)
        if small:
            return small
        if not _bounded(region, root):
            return f"marquee element is not bounded by its panel: {_fmt(region)} vs {_fmt(root)}"
        if region["sh"] > region["ch"] + 1:
            return (
                f"content is {region['sh']:.0f}px high in a {region['ch']:.0f}px box: a marquee "
                f"moves text sideways and cannot show vertical overflow"
            )
        if region["sw"] > region["cw"] + 1:
            motion = region.get("motion") or {}
            if not (motion.get("animations") or motion.get("changed")):
                return (
                    f"content is {region['sw']:.0f}px wide in a {region['cw']:.0f}px box and "
                    f"nothing moves it: no running animation and no transform or scroll offset "
                    f"changed between two samples, so the overflow is only clipped"
                )
        return None
    if name == "wrap":
        small = _too_small(alt, region)
        if small:
            return small
        if region["sw"] > region["cw"] + 1:
            return (
                f"content is {region['sw']:.0f}px wide in a {region['cw']:.0f}px box: it overflows "
                f"instead of wrapping"
            )
        if (
            region["h"] > root["h"] + BOUNDS_TOLERANCE_PX
            or region["b"] > root["b"] + BOUNDS_TOLERANCE_PX
        ):
            return (
                f"wrapped content is {region['h']:.0f}px high and ends at {region['b']:.0f}px, "
                f"beyond its panel ({_fmt(root)}): it wrapped into more rows than the panel holds"
            )
        return None
    if name == "truncate":
        if region["tov"] != "ellipsis" or not region["ws"].startswith("nowrap"):
            return (
                f"text-overflow {region['tov']!r} / white-space {region['ws']!r} is not an "
                f"ellipsis truncation"
            )
        return None
    if name == "visible":
        small = _too_small(alt, region)
        if small:
            return small
        if not _bounded(region, root):
            return f"region is partly outside its panel box: {_fmt(region)} vs panel {_fmt(root)}"
        return None
    return f"unknown mode {name!r}"


def scroll_exercised(region: dict[str, Any], root: dict[str, Any]) -> bool:
    """True when this cell gave a scroll region more content than its box holds.

    Content is "more than the box holds" when it overflows the scroller's own box, when the
    scroller grew out past its panel (the unbounded case the judge reports as a violation), or,
    for a virtual scrollbar, when its slider is shorter than its track.
    """
    slider = region.get("slider")
    if slider is not None:
        return bool(0 < slider["h"] < region["h"] - 1)
    return bool(
        region.get("sh", 0) > region.get("ch", 0) + 1
        or region.get("sw", 0) > region.get("cw", 0) + 1
        or not _bounded(region, root)
    )


def judge_panel_cell(
    rules: list[Rule], cell: dict[str, Any]
) -> tuple[list[Finding], dict[str, int]]:
    """Judge one measured cell (layout x panel x slot x size) against its panel's rules.

    Returns the findings and counters: `pass`, `fail`, `na` (optional region absent) and
    `exercised` (a scroll region whose content actually exceeded its box).
    """
    where = f"{cell['layout']}/{cell['panel']}@{cell['slot']} {cell['size'][0]}x{cell['size'][1]}"
    counts = {"pass": 0, "fail": 0, "na": 0, "exercised": 0}
    findings: list[Finding] = []
    if not cell.get("found"):
        return [Finding(where, "panel-missing", "the panel host was not rendered in this cell")], {
            "pass": 0,
            "fail": 1,
            "na": 0,
            "exercised": 0,
        }
    doc, root, body = cell["doc"], cell["root"], cell["body"]
    if doc["sw"] > doc["vw"] or doc["sh"] > doc["vh"]:
        findings.append(
            Finding(
                where,
                "page-scroll",
                f"document is {doc['sw']}x{doc['sh']} in a {doc['vw']}x{doc['vh']} viewport",
            )
        )
    for rule in rules:
        region = cell["regions"].get(rule.selector)
        if rule.selector == ":root":
            region = root
        label = f"{rule.region} ({rule.selector})"
        if region is None or region.get("found") is False:
            if rule.optional:
                counts["na"] += 1
            else:
                counts["fail"] += 1
                findings.append(Finding(where, "region-missing", f"{label} is not rendered"))
            continue
        reasons = [check_alt(alt, rule.selector, region, root, body) for alt in rule.alts]
        if any(reason is None for reason in reasons):
            counts["pass"] += 1
        else:
            counts["fail"] += 1
            modes = " or ".join(alt.name for alt in rule.alts)
            findings.append(
                Finding(where, modes, f"{label}: " + "; ".join(str(r) for r in reasons))
            )
        if any(alt.name in SCROLL_MODES for alt in rule.alts):
            if scroll_exercised(region, root):
                counts["exercised"] += 1
    for clip in cell.get("clips", []):
        if not clip.get("exempt"):
            counts["fail"] += 1
            findings.append(
                Finding(
                    where,
                    "silent-clip",
                    f"{clip['el']} clips its own content (scroll {clip['sw']}x{clip['sh']} in a "
                    f"{clip['cw']}x{clip['ch']} box, overflow {clip['ox']}/{clip['oy']}) and no "
                    f"contract row declares it a scroller",
                )
            )
    return findings, counts


def judge_surface_cell(surface: str, rules: list[Rule], cell: dict[str, Any]) -> list[Finding]:
    """Judge one measured floating surface (popover, tooltip, context menu)."""
    where = (
        f"{cell['layout']}/{surface} '{cell.get('label', '?')}' {cell['size'][0]}x{cell['size'][1]}"
    )
    if cell.get("error"):
        return [Finding(where, "not-measured", str(cell["error"]))]
    b, vw, vh = cell["bubble"], cell["vw"], cell["vh"]
    findings: list[Finding] = []
    for rule in rules:
        for alt in rule.alts:
            name = alt.name
            if name == "in-viewport":
                if b["x"] < -1 or b["y"] < -1 or b["r"] > vw + 1 or b["b"] > vh + 1:
                    findings.append(
                        Finding(where, name, f"bubble {_fmt(b)} is outside the {vw}x{vh} viewport")
                    )
            elif name == "not-clipped":
                for clip in cell.get("clipRects", []):
                    if (
                        b["x"] < clip["x"] - 1
                        or b["y"] < clip["y"] - 1
                        or b["r"] > clip["r"] + 1
                        or b["b"] > clip["b"] + 1
                    ):
                        findings.append(
                            Finding(
                                where,
                                name,
                                f"bubble {_fmt(b)} is cut by ancestor {clip['el']} {_fmt(clip)}",
                            )
                        )
                        break
            elif name == "dismiss-visible":
                d = cell.get("dismiss")
                if d is None or d["x"] < 0 or d["y"] < 0 or d["r"] > vw or d["b"] > vh:
                    findings.append(
                        Finding(where, name, "the dismiss control is outside the viewport")
                    )
            elif name == "text-fits":
                if cell["tipSw"] > cell["tipCw"] + 1 or cell["tipSh"] > cell["tipCh"] + 1:
                    findings.append(
                        Finding(
                            where,
                            name,
                            f"tooltip text {cell['tipSw']}x{cell['tipSh']} is cut in a "
                            f"{cell['tipCw']}x{cell['tipCh']} bubble",
                        )
                    )
            elif name == "not-starved":
                natural = cell["natural"]
                room = max(cell["spaceAbove"], cell["spaceBelow"])
                needed = min(natural, 0.6 * vh, room) - 2
                if b["h"] < STARVED_BELOW_FRACTION * needed:
                    findings.append(
                        Finding(
                            where,
                            name,
                            f"bubble is {b['h']:.0f}px high but its content needs {natural:.0f}px, "
                            f"{room:.0f}px of room exists on the larger side and 60% of the "
                            f"viewport is {0.6 * vh:.0f}px: it should reach about {needed:.0f}px",
                        )
                    )
            else:
                findings.append(Finding(where, name, f"unknown surface mode {name!r}"))
    return findings


# ---------------------------------------------------------------------------------------------
# Live half: Playwright measurement
# ---------------------------------------------------------------------------------------------

# Every key the judge reads from a measurement must be produced by the measurement script; the
# static half asserts this so the two cannot drift apart unnoticed.
JUDGE_FIELDS = (
    "found", "doc", "root", "body", "regions", "clips", "exempt", "reach",
    "bubble", "clipRects", "dismiss", "tipSw", "natural", "spaceAbove", "spaceBelow",
    "unavailable",
    "motion",
    "animations",
)  # fmt: skip

MEASURE_JS = r"""
const fs = require('fs');
const { chromium } = require(process.env.FIT_PLAYWRIGHT_MODULE || 'playwright');
const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

const rectOf = (e) => {
  const b = e.getBoundingClientRect();
  return { x: b.x, y: b.y, w: b.width, h: b.height, r: b.right, b: b.bottom };
};

async function open(browser, cell) {
  const ctx = await browser.newContext({ viewport: { width: cell.size[0], height: cell.size[1] } });
  const state = { schema_version: cell.schemaVersion, active_layout: cell.layout };
  if (cell.viewerDirectory) {
    state.html_viewer_tabs = {
      tabs: [{ id: 1, directory: cell.viewerDirectory, search_text: '', selected_file: null }],
      active_tab_id: 1,
    };
  }
  if (cell.panel) {
    state.panel_assignments = { [cell.layout]: { [cell.panel]: cell.slot } };
    state.slot_visible_panel = { [cell.layout]: { [cell.slot]: cell.panel } };
  }
  await ctx.addInitScript(
    ([key, value]) => localStorage.setItem(key, value),
    [`d-system:workbench-state:v${cell.schemaVersion}`, JSON.stringify(state)],
  );
  const page = await ctx.newPage();
  await page.goto(cfg.baseUrl);
  return { ctx, page };
}

async function measureCell(browser, cell) {
  const { ctx, page } = await open(browser, cell);
  try {
    await page.waitForSelector(`[data-panel-host="${cell.panel}"] > *`, { timeout: 15000 });
    for (const sel of cell.selectors.filter((s) => s !== ':root')) {
      await page
        .waitForSelector(`[data-panel-host="${cell.panel}"] ${sel}`, { timeout: 4000 })
        .catch(() => {});
    }
    // Stress: a tab bar or scrollback the page never fills is a scroll rule nothing exercised.
    // Tab-adding controls are clicked past the point a narrow panel can show them all (the
    // terminal caps itself at four sessions per panel).
    for (const [sel, times] of [['.stage-html-viewer__tab-new', 10], ['.stage-terminal-tab__new', 3]]) {
      const add = await page.$(`[data-panel-host="${cell.panel}"] ${sel}`);
      for (let i = 0; add && i < times; i++) await add.click({ timeout: 1500 }).catch(() => {});
    }
    if (await page.$(`[data-panel-host="${cell.panel}"] .xterm`)) {
      await page
        .click(`[data-panel-host="${cell.panel}"] .stage-terminal-session--active .xterm`, { timeout: 2500 })
        .catch(() => {});
      await page.keyboard.type('seq 1 400\n');
    }
    await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(900);
    if (cell.css) await page.addStyleTag({ content: cell.css });
    await page.waitForTimeout(150);
    return await page.evaluate(
      async ({ panel, selectors, exempt, motionSelectors, motionProps }) => {
        const rectOf = (e) => {
          const b = e.getBoundingClientRect();
          return { x: b.x, y: b.y, w: b.width, h: b.height, r: b.right, b: b.bottom };
        };
        const host = document.querySelector(`[data-panel-host="${panel}"]`);
        if (!host || !host.firstElementChild) return { found: false };
        const root = host.firstElementChild;
        const body = host.parentElement;
        const regions = {};
        for (const sel of selectors) {
          if (sel === ':root') continue;
          // The first match that renders: a hidden session tab's terminal also matches `.xterm`.
          const all = root.matches(sel) ? [root] : [...root.querySelectorAll(sel)];
          const e = all.find((c) => { const b = c.getBoundingClientRect(); return b.width > 0 && b.height > 0; }) || all[0];
          if (!e) { regions[sel] = { found: false }; continue; }
          const cs = getComputedStyle(e);
          const reach = {};
          if (e.scrollHeight > e.clientHeight + 1) {
            const before = e.scrollTop; e.scrollTop = e.scrollHeight; reach.y = e.scrollTop > before; e.scrollTop = before;
          }
          if (e.scrollWidth > e.clientWidth + 1) {
            const before = e.scrollLeft; e.scrollLeft = e.scrollWidth; reach.x = e.scrollLeft > before; e.scrollLeft = before;
          }
          regions[sel] = {
            found: true, ...rectOf(e), ox: cs.overflowX, oy: cs.overflowY,
            tov: cs.textOverflow, ws: cs.whiteSpace,
            sh: e.scrollHeight, ch: e.clientHeight, sw: e.scrollWidth, cw: e.clientWidth, reach,
            slider: (() => { const sl = e.querySelector('.slider'); return sl ? { h: sl.getBoundingClientRect().height } : null; })(),
          };
        }
        // Evidence that text moves, for regions declared `marquee`: a running animation of a
        // horizontal-motion property, or a transform or scroll offset that differs between two
        // samples. An opacity fade is not motion.
        const sampleMotion = (e) =>
          [e, ...e.querySelectorAll('*')].map((x) => getComputedStyle(x).transform + '|' + x.scrollLeft);
        const motionBefore = {};
        for (const sel of motionSelectors) {
          const e = root.matches(sel) ? root : root.querySelector(sel);
          if (e && regions[sel] && regions[sel].found) motionBefore[sel] = { e, before: sampleMotion(e) };
        }
        if (Object.keys(motionBefore).length) await new Promise((r) => setTimeout(r, 350));
        const exemptAll = [...exempt];
        for (const [sel, { e, before }] of Object.entries(motionBefore)) {
          let animations = 0;
          try {
            animations = e
              .getAnimations({ subtree: true })
              .filter((a) => a.playState === 'running' && a.effect && a.effect.getKeyframes().some(
                (k) => motionProps.some((p) => p in k && k[p] !== undefined && k[p] !== 'none'),
              )).length;
          } catch (err) { animations = 0; }
          const after = sampleMotion(e);
          const changed = after.length !== before.length || after.some((v, i) => v !== before[i]);
          regions[sel].motion = { animations, changed };
          if (animations || changed) exemptAll.push(sel);
        }
        const clips = [];
        for (const e of [root, ...root.querySelectorAll('*')]) {
          const cs = getComputedStyle(e);
          if (cs.overflowX === 'visible' && cs.overflowY === 'visible') continue;
          if (e.scrollHeight <= e.clientHeight + 1 && e.scrollWidth <= e.clientWidth + 1) continue;
          const exemptHit = exemptAll.some((s) => { const c = e.closest(s); return c && root.contains(c) && c !== root; });
          clips.push({
            el: e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : ''),
            ox: cs.overflowX, oy: cs.overflowY, sh: e.scrollHeight, ch: e.clientHeight,
            sw: e.scrollWidth, cw: e.clientWidth, exempt: exemptHit,
          });
        }
        const de = document.documentElement;
        return {
          found: true, root: rectOf(root), body: rectOf(body), regions, clips,
          // A shell the host lacks (CMD or PowerShell on Linux) mounts an xterm that never connects
          // and shows this overlay; its scrollback cannot be exercised here.
          unavailable: !!root.querySelector('.stage-terminal-mount__overlay'),
          doc: { sw: de.scrollWidth, sh: de.scrollHeight, vw: innerWidth, vh: innerHeight },
        };
      },
      {
        panel: cell.panel,
        selectors: cell.selectors,
        exempt: cell.exempt,
        motionSelectors: cell.motionSelectors,
        motionProps: cell.motionProps,
      },
    );
  } finally {
    await ctx.close();
  }
}

async function measureBubble(page, bubbleSel, trigger) {
  return page.evaluate(
    ({ bubbleSel, trig }) => {
      const rectOf = (e) => {
        const b = e.getBoundingClientRect();
        return { x: b.x, y: b.y, w: b.width, h: b.height, r: b.right, b: b.bottom };
      };
      const bubble = document.querySelector(bubbleSel);
      if (!bubble) return { error: 'bubble did not render' };
      const clipRects = [];
      for (let a = bubble.parentElement; a; a = a.parentElement) {
        const cs = getComputedStyle(a);
        if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible') {
          if (a === document.documentElement) continue;
          clipRects.push({ el: a.tagName.toLowerCase() + '.' + String(a.className).trim().split(/\s+/).join('.'), ...rectOf(a) });
        }
      }
      const header = bubble.querySelector('.stage-popover__header');
      const popBody = bubble.querySelector('.stage-popover__body');
      const dismiss = bubble.querySelector('.stage-popover__dismiss');
      const t = trig;
      return {
        bubble: rectOf(bubble), clipRects, vw: innerWidth, vh: innerHeight,
        dismiss: dismiss ? rectOf(dismiss) : null,
        natural: header && popBody ? header.offsetHeight + popBody.scrollHeight : bubble.scrollHeight,
        spaceAbove: t.y - 8, spaceBelow: innerHeight - t.b - 8,
        tipSw: bubble.scrollWidth, tipCw: bubble.clientWidth, tipSh: bubble.scrollHeight, tipCh: bubble.clientHeight,
      };
    },
    { bubbleSel, trig: trigger },
  );
}

async function measureFloating(browser, cell) {
  const { ctx, page } = await open(browser, cell);
  const out = [];
  try {
    await page.waitForSelector('[data-panel-host]', { timeout: 15000 });
    await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(900);
    const popovers = await page.$$('.stage-popover__trigger:not([disabled])');
    for (let i = 0; i < popovers.length; i++) {
      const trig = (await page.$$('.stage-popover__trigger:not([disabled])'))[i];
      if (!trig || !(await trig.boundingBox())) continue;
      const label = (await trig.innerText()).trim().slice(0, 40) || (await trig.getAttribute('aria-label')) || 'popover';
      const tr = await trig.evaluate((e) => { const b = e.getBoundingClientRect(); return { y: b.y, b: b.bottom }; });
      let m;
      try {
        await trig.click({ timeout: 2500 });
        await page.waitForSelector('.stage-popover__bubble', { timeout: 2000 });
        await page.waitForTimeout(150);
        m = await measureBubble(page, '.stage-popover__bubble', tr);
      } catch (e) { m = { error: String(e.message).split('\n')[0] }; }
      out.push({ surface: 'popover', label, layout: cell.layout, size: cell.size, ...m });
      await page.keyboard.press('Escape');
      await page.waitForTimeout(100);
    }
    const tips = await page.$$('.stage-tooltip__trigger');
    for (let i = 0; i < tips.length; i++) {
      const trig = (await page.$$('.stage-tooltip__trigger'))[i];
      if (!trig || !(await trig.boundingBox())) continue;
      const label = 'tooltip ' + (await trig.evaluate((e) => (e.closest('[aria-label]') || {}).ariaLabel || e.closest('section')?.className || '')).toString().slice(0, 40);
      const tr = await trig.evaluate((e) => { const b = e.getBoundingClientRect(); return { y: b.y, b: b.bottom }; });
      let m;
      try {
        await trig.hover({ timeout: 2500 });
        await page.waitForSelector('.stage-tooltip__bubble', { timeout: 2000 });
        m = await measureBubble(page, '.stage-tooltip__bubble', tr);
      } catch (e) { m = { error: String(e.message).split('\n')[0] }; }
      out.push({ surface: 'tooltip', label, layout: cell.layout, size: cell.size, ...m });
      await page.mouse.move(2, 2);
      await page.waitForTimeout(100);
    }
    const entry = await page.$('.stage-file-browser__tree-toggle, .stage-file-browser__tree-file');
    if (entry) {
      let m;
      try {
        await entry.click({ button: 'right', timeout: 2500 });
        await page.waitForSelector('.stage-file-tree-menu', { timeout: 2000 });
        m = await measureBubble(page, '.stage-file-tree-menu', { y: 0, b: 0 });
      } catch (e) { m = { error: String(e.message).split('\n')[0] }; }
      out.push({ surface: 'context-menu', label: 'file tree entry', layout: cell.layout, size: cell.size, ...m });
    }
  } finally {
    await ctx.close();
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const out = { cells: [], floating: [] };
  for (const cell of cfg.cells) {
    process.stderr.write(`cell ${cell.layout}/${cell.panel}@${cell.slot} ${cell.size.join('x')}\n`);
    const m = await measureCell(browser, cell);
    out.cells.push({ layout: cell.layout, panel: cell.panel, slot: cell.slot, size: cell.size, ...m });
  }
  for (const cell of cfg.floating) {
    process.stderr.write(`floating ${cell.layout} ${cell.size.join('x')}\n`);
    out.floating.push(...(await measureFloating(browser, cell)));
  }
  await browser.close();
  process.stdout.write(JSON.stringify(out));
})().catch((e) => { process.stderr.write(String(e.stack || e) + '\n'); process.exit(1); });
"""  # noqa: E501


def find_playwright_module() -> str | None:
    """A directory Node can `require('playwright')` from, or None."""

    candidates: list[Path] = []
    if os.environ.get("FIT_PLAYWRIGHT_MODULE"):
        return os.environ["FIT_PLAYWRIGHT_MODULE"]
    candidates.append(ROOT / "ts" / "node_modules" / "playwright")
    npm = shutil.which("npm")
    if npm:
        result = subprocess.run([npm, "root", "-g"], capture_output=True, text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            candidates.append(Path(result.stdout.strip()) / "playwright")
    for candidate in candidates:
        if candidate.is_dir():
            return str(candidate)
    return None


def exempt_selectors(contract: Contract) -> list[str]:
    """Selectors whose subtree may clip: declared scrollers, frames and truncation.

    A `marquee` selector is not listed: its content is clipped by design, so it is exempt only for a
    cell where the measurement found it actually moving (see `motionSelectors`). A row that also
    offers a scroll alternative stays exempt through that alternative, whose own check rejects a
    scroller that does not scroll.
    """
    exempt = {".xterm"}
    for rules in contract.panels.values():
        for rule in rules:
            if rule.selector != ":root" and any(
                alt.name in SCROLL_MODES | {"frame", "truncate"} for alt in rule.alts
            ):
                exempt.add(rule.selector)
    return sorted(exempt)


def motion_selectors(rules: list[Rule]) -> list[str]:
    """Selectors of a panel's regions that may satisfy their row by moving (`marquee`)."""
    return sorted(
        {r.selector for r in rules if any(a.name == "marquee" for a in r.alts)} - {":root"}
    )


def live_cells(
    contract: Contract,
    sizes: Iterable[tuple[int, int]],
    layout_filter: str | None = None,
    panel_filter: str | None = None,
) -> list[dict[str, Any]]:
    """layout x panel x eligible slot x size, from the layout files, for every contracted panel."""
    cells: list[dict[str, Any]] = []
    exempt = exempt_selectors(contract)
    for path in sorted(LAYOUTS_DIR.glob("*.json")):
        layout = json.loads(path.read_text(encoding="utf-8"))
        if layout_filter and layout["layout_id"] != layout_filter:
            continue
        for panel in layout["panels"]:
            if panel_filter and panel["panel_id"] != panel_filter:
                continue
            rules = contract.panels.get(panel["panel_id"], [])
            for slot in panel["eligible_slots"]:
                for size in sizes:
                    cells.append(
                        {
                            "layout": layout["layout_id"],
                            "schemaVersion": layout["schema_version"],
                            "panel": panel["panel_id"],
                            "slot": slot,
                            "size": list(size),
                            "selectors": sorted({rule.selector for rule in rules} | {":root"}),
                            "exempt": exempt,
                            "motionSelectors": motion_selectors(rules),
                            "motionProps": list(MOTION_PROPERTIES),
                        }
                    )
    return cells


def contract_breaks(rules: list[Rule]) -> list[tuple[str, str, str]]:
    """Every way to violate one of the panel's own rows: (css, label, selector).

    A scroller loses its overflow, a fill region collapses, and a region that may also be a
    marquee or must stay visible is pushed out of its panel.
    """
    breaks: list[tuple[str, str, str]] = []
    for rule in rules:
        if rule.selector == ":root":
            continue
        names = {alt.name for alt in rule.alts}
        scope = f"[data-panel-host] {rule.selector}"
        if names & {"scroll-y", "scroll-x"} and "marquee" not in names:
            css, label = f"{scope}{{overflow:hidden !important}}", "overflow:hidden"
        elif "fill" in names:
            css = f"{scope}{{height:12px !important;min-height:0 !important;flex:none !important}}"
            label = "height:12px"
        elif names & {"marquee", "visible", "frame"}:
            css, label = f"{scope}{{transform:translateY(900px) !important}}", "moved out"
        else:
            continue
        breaks.append((css, f"{rule.selector} {label}", rule.selector))
    return breaks


def break_contract_css(rules: list[Rule]) -> tuple[str, str] | None:
    """The first break `contract_breaks` offers, as (css, label), or None when nothing breaks."""
    breaks = contract_breaks(rules)
    return (breaks[0][0], breaks[0][1]) if breaks else None


def on_region(findings: Iterable[Finding], selector: str) -> list[Finding]:
    """Findings that name a contract region (as `(selector)` in their detail)."""
    return [f for f in findings if f"({selector})" in f.detail]


def choose_differential_breaks(
    contract: Contract, cells: list[dict[str, Any]], baseline: list[list[Finding]]
) -> tuple[list[tuple[dict[str, Any], str, str]], list[str]]:
    """Pick, per panel, a cell and break whose region passes unbroken.

    A break proves the judge only if the region was clean before it: a region that already fails
    produces the same finding with or without the injection. Returns the chosen
    (cell with css, label, selector) triples and one message per panel with no clean candidate.
    """
    chosen: list[tuple[dict[str, Any], str, str]] = []
    unproven: list[str] = []
    for panel in dict.fromkeys(c["panel"] for c in cells):
        failing: list[str] = []
        picked = False
        for cell, findings in zip(cells, baseline, strict=True):
            if cell["panel"] != panel or picked:
                continue
            for css, label, selector in contract_breaks(contract.panels[panel]):
                if on_region(findings, selector):
                    failing.append(f"{selector} ({cell['layout']}@{cell['slot']})")
                    continue
                chosen.append(({**cell, "css": css}, label, selector))
                picked = True
                break
        if not picked:
            unproven.append(
                f"{panel}: every breakable region already fails unbroken in the cells measured "
                f"({', '.join(dict.fromkeys(failing)) or 'none breakable'}), so no injected "
                f"break can be told apart from the existing finding"
            )
    return chosen, unproven


def run_node(config: dict[str, Any], module: str) -> dict[str, Any]:
    node = shutil.which("node")
    if not node:
        raise SystemExit("node is not on PATH; the live half needs Node and Playwright")
    with tempfile.TemporaryDirectory() as tmp:
        script, cfg_path = Path(tmp) / "measure.cjs", Path(tmp) / "cfg.json"
        script.write_text(MEASURE_JS, encoding="utf-8")
        cfg_path.write_text(json.dumps(config), encoding="utf-8")
        env = {**os.environ, "FIT_PLAYWRIGHT_MODULE": module}
        # stderr passes through so a long run shows which cell it is on; stdout carries the JSON.
        result = subprocess.run(
            [node, str(script), str(cfg_path)],
            stdout=subprocess.PIPE,
            text=True,
            env=env,
            check=False,
        )
    if result.returncode != 0:
        raise SystemExit("measurement script failed (see its stderr above)")
    data: dict[str, Any] = json.loads(result.stdout)
    return data


def judge_live(
    contract: Contract, data: dict[str, Any], cells: list[dict[str, Any]], *, whole_matrix: bool
) -> tuple[list[Finding], str]:
    """Judge a whole live run: every cell, every floating surface, and the run's own coverage."""
    findings: list[Finding] = []
    totals = {"pass": 0, "fail": 0, "na": 0, "exercised": 0}
    exercised: dict[tuple[str, str], int] = {}
    seen: dict[tuple[str, str], int] = {}
    rendered: set[str] = set()
    unavailable: set[str] = set()
    for measured in data["cells"]:
        rules = contract.panels[measured["panel"]]
        cell_findings, counts = judge_panel_cell(rules, measured)
        findings.extend(cell_findings)
        for counter in totals:
            totals[counter] += counts[counter]
        if not measured.get("found"):
            continue
        rendered.add(measured["panel"])
        if measured.get("unavailable"):
            unavailable.add(measured["panel"])
            continue
        for rule in rules:
            region = measured["regions"].get(rule.selector)
            if not region or not region.get("found"):
                continue
            if any(a.name in SCROLL_MODES for a in rule.alts):
                key = (measured["panel"], rule.selector)
                seen[key] = seen.get(key, 0) + 1
                if scroll_exercised(region, measured["root"]):
                    exercised[key] = exercised.get(key, 0) + 1
    for measured in data["floating"]:
        surface = measured["surface"]
        findings.extend(judge_surface_cell(surface, contract.surfaces.get(surface, []), measured))
    wanted = {cell["panel"] for cell in cells}
    for panel in sorted(wanted - rendered):
        findings.append(
            Finding("matrix", "unmeasured-panel", f"{panel} was never rendered in any cell")
        )
    # A scroll rule that was present but never given content to scroll passed vacuously. A rule
    # whose region never rendered at all (an optional region absent on this host) is n/a.
    for (panel, selector), count in sorted(seen.items()):
        if exercised.get((panel, selector), 0) == 0:
            findings.append(
                Finding(
                    "matrix",
                    "unexercised",
                    f"{panel} {selector}: present in {count} cell(s), never given content to "
                    f"scroll",
                )
            )
    kinds: dict[str, int] = {}
    for measured in data["floating"]:
        kinds[measured["surface"]] = kinds.get(measured["surface"], 0) + 1
    if whole_matrix:
        missing_surfaces = sorted(set(contract.surfaces) - set(kinds))
        for surface in missing_surfaces:
            findings.append(
                Finding("matrix", "unmeasured-surface", f"no {surface} was opened in any cell")
            )
    summary = (
        f"{len(data['cells'])} panel cells; floating surfaces measured "
        f"{dict(sorted(kinds.items()))}; rules pass={totals['pass']} fail={totals['fail']} "
        f"n/a(optional region absent)={totals['na']}; "
        f"scroll regions exercised in {len(exercised)} of {len(seen)} (panel, region) pairs; "
        f"shell unavailable on this host, scrollback not exercised (owner-machine, C10): "
        f"{sorted(unavailable) or 'none'}; "
        f"{len(findings)} finding(s)"
    )
    return findings, summary


def live_main(args: argparse.Namespace) -> int:
    contract = load_contract()
    registered = checked_panel_types(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert_every_panel_declared(registered, contract)
    module = find_playwright_module()
    if module is None:
        print(
            "Playwright for Node was not found (set FIT_PLAYWRIGHT_MODULE or install it)",
            file=sys.stderr,
        )
        return 2
    sizes = REQUIRED_SIZES[:1] + REQUIRED_SIZES[3:] if args.quick else REQUIRED_SIZES
    cells = live_cells(contract, sizes, args.layout, args.panel)
    layouts = sorted({c["layout"] for c in cells})
    schema = {c["layout"]: c["schemaVersion"] for c in cells}
    floating = [
        {
            "layout": layout,
            "schemaVersion": schema[layout],
            "size": list(size),
            "viewerDirectory": STRESS_VIEWER_DIRECTORY,
        }
        for layout in layouts
        for size in sizes
    ]
    data = run_node({"baseUrl": args.live, "cells": cells, "floating": floating}, module)

    if args.dump:
        Path(args.dump).write_text(json.dumps(data, indent=1), encoding="utf-8")
    all_findings, summary = judge_live(contract, data, cells, whole_matrix=not args.panel)
    for finding in all_findings:
        print(finding)
    print("\n" + summary)
    status = 1 if all_findings else 0

    if args.self_test:
        status = max(status, self_test(contract, args, module))
    return status


def self_test(contract: Contract, args: argparse.Namespace, module: str) -> int:
    """Differential self-test: break each panel's own contract and require a new finding.

    First every candidate cell is judged unbroken. Each panel then gets one injected violation in a
    cell and region that passed unbroken, and the break counts as caught only when the judge
    reports a finding on that region. A panel whose regions all fail unbroken is named as unproven
    rather than reported as caught.
    """
    cells = live_cells(contract, [REQUIRED_SIZES[0]], args.layout, args.panel)
    base = run_node({"baseUrl": args.live, "cells": cells, "floating": []}, module)
    baseline = [judge_panel_cell(contract.panels[m["panel"]], m)[0] for m in base["cells"]]
    chosen, unproven = choose_differential_breaks(contract, cells, baseline)
    failures = len(unproven)
    for message in unproven:
        print(f"self-test UNPROVEN {message}")
    if chosen:
        data = run_node(
            {"baseUrl": args.live, "cells": [c for c, _, _ in chosen], "floating": []}, module
        )
        for measured, (cell, label, selector) in zip(data["cells"], chosen, strict=True):
            findings, _ = judge_panel_cell(contract.panels[measured["panel"]], measured)
            caught = on_region(findings, selector)
            where = f"{cell['layout']}@{cell['slot']}"
            print(
                f"self-test {measured['panel']} ({where}): unbroken region passed, injected "
                f"{label}: {'caught' if caught else 'NOT CAUGHT'}"
            )
            if caught:
                print(f"    {caught[0]}")
            else:
                failures += 1
    return 1 if failures or not chosen else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Live content-fit contract check (REQ-037)")
    parser.add_argument(
        "--live", required=True, metavar="URL", help="base URL of a running workbench"
    )
    parser.add_argument("--quick", action="store_true", help="only 1280x720 and 1024x768")
    parser.add_argument("--layout", help="restrict to one layout id")
    parser.add_argument("--panel", help="restrict to one panel type")
    parser.add_argument("--self-test", action="store_true", help="also inject contract violations")
    parser.add_argument("--dump", metavar="PATH", help="write the raw measurements as JSON")
    return live_main(parser.parse_args(argv))


# ---------------------------------------------------------------------------------------------
# Static half: pytest
# ---------------------------------------------------------------------------------------------

REGISTRY_SOURCE = REGISTRY_PATH.read_text(encoding="utf-8")


def test_contract_document_is_the_governed_requirement() -> None:
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    assert re.search(r"^code: REQ-037$", text, flags=re.MULTILINE)
    assert re.search(r"^kind: requirement$", text, flags=re.MULTILINE)
    contract = parse_contract(text)
    assert contract.panels and contract.surfaces


def test_registry_discovery_cannot_pass_vacuously() -> None:
    ids = checked_panel_types(REGISTRY_SOURCE)
    declared_in_layouts = set().union(*layout_panel_ids().values())
    unregistered = sorted(declared_in_layouts - set(ids))
    assert not unregistered, (
        f"layout files name panel ids missing from the registry: {unregistered}"
    )
    unplaceable = sorted(set(ids) - declared_in_layouts)
    assert not unplaceable, (
        f"registered panel types {unplaceable} appear in no layout file, so the live check could "
        f"never render or measure them"
    )


def test_registry_parser_sees_added_and_removed_types() -> None:
    ids = checked_panel_types(REGISTRY_SOURCE)
    added = REGISTRY_SOURCE.replace(
        "export const PANEL_REGISTRY: Record<string, PanelDefinition> = {",
        "export const PANEL_REGISTRY: Record<string, PanelDefinition> = {\n"
        "  'fake-panel': { displayName: 'Fake', Component: TerminalRegion },",
    )
    assert added != REGISTRY_SOURCE, "the registry declaration changed shape; update this fixture"
    new_ids = registered_panel_types(added)
    assert new_ids == ["fake-panel", *ids]
    assert_registry_parse_is_sound(added, new_ids)
    removed = re.sub(r"^  'html-viewer':.*\n", "", REGISTRY_SOURCE, flags=re.MULTILINE)
    assert "html-viewer" not in registered_panel_types(removed)
    # A drifted regex (a key the parse misses) trips the three-way count rather than passing.
    broken = REGISTRY_SOURCE.replace("  overview: {", "  [overviewKey]: {")
    assert broken != REGISTRY_SOURCE
    with pytest.raises(AssertionError, match="drifted"):
        assert_registry_parse_is_sound(broken, registered_panel_types(broken))


def _registry_with_extra_entry(entry: str) -> str:
    """A copy of the registry source with one more line at the start of the literal."""
    declaration = "export const PANEL_REGISTRY: Record<string, PanelDefinition> = {"
    assert declaration in REGISTRY_SOURCE, "the registry declaration changed shape; update this"
    return REGISTRY_SOURCE.replace(declaration, f"{declaration}\n  {entry}")


@pytest.mark.parametrize(
    ("label", "entry", "tail"),
    [
        ("a factory call entry", "'fake-panel': makeDefinition('x'),", ""),
        ("a spread entry", "...EXTRA_PANELS,", ""),
        ("a subscript assignment", "", "\nPANEL_REGISTRY['fake-panel'] = fakeDefinition\n"),
        (
            "an Object.assign call",
            "",
            "\nObject.assign(PANEL_REGISTRY, { fake: fakeDefinition })\n",
        ),
        ("a property assignment", "", "\nPANEL_REGISTRY.fake = fakeDefinition\n"),
    ],
)
def test_registry_registration_the_parse_cannot_see_is_refused(
    label: str, entry: str, tail: str
) -> None:
    """A panel type registered by a call, a spread or a later assignment would be invisible."""
    mutated = _registry_with_extra_entry(entry) + tail if entry else REGISTRY_SOURCE + tail
    with pytest.raises(AssertionError):
        checked_panel_types(mutated)
    assert checked_panel_types(REGISTRY_SOURCE), f"{label}: the unmodified registry must pass"


def test_registry_mutation_scan_ignores_comments_and_reads() -> None:
    """Reads like `PANEL_REGISTRY[id]?.Component` and prose in comments are not mutations."""
    commented = (
        REGISTRY_SOURCE + "\n// PANEL_REGISTRY['x'] = y; Object.assign(PANEL_REGISTRY, {})\n"
    )
    assert checked_panel_types(commented) == checked_panel_types(REGISTRY_SOURCE)


def test_every_registered_panel_type_has_a_contract() -> None:
    """REQ-011 R09/R10: one contract per shipped panel type, none undeclared."""
    assert_every_panel_declared(checked_panel_types(REGISTRY_SOURCE), load_contract())


def test_undeclared_panel_fails_and_is_named() -> None:
    """REQ-011 R10: a panel registered without a contract fails, and the failure names it.

    The fake type is registered in a copy of the registry source and read back through the same
    discovery the live check uses, so the whole path from source to failure is exercised.
    """
    contract = load_contract()
    mutated = _registry_with_extra_entry(
        "'fake-panel': { displayName: 'Fake', Component: TerminalRegion },"
    )
    ids = checked_panel_types(mutated)
    assert "fake-panel" in ids
    with pytest.raises(AssertionError, match="fake-panel"):
        assert_every_panel_declared(ids, contract)
    real_ids = checked_panel_types(REGISTRY_SOURCE)
    stripped = Contract(
        panels={k: v for k, v in contract.panels.items() if k != "file-browser"},
        surfaces=contract.surfaces,
    )
    with pytest.raises(AssertionError, match="file-browser"):
        assert_every_panel_declared(real_ids, stripped)
    assert undeclared_panels(real_ids, contract) == []


def test_no_contract_row_names_an_unregistered_panel() -> None:
    stale = stale_contract_panels(checked_panel_types(REGISTRY_SOURCE), load_contract())
    assert not stale, f"contract rows name panel types the registry no longer has: {stale}"


def test_every_panel_declares_how_it_fills_its_slot() -> None:
    """Fill is mandatory: a panel with only scroll rows could still collapse to nothing.

    Iterates the registry, not the contract, so a registered type with no rows at all fails here
    too and is named.
    """
    contract = load_contract()
    for panel in checked_panel_types(REGISTRY_SOURCE):
        rules = contract.panels.get(panel, [])
        fills = [
            r for r in rules if r.selector == ":root" and any(a.name == "fill" for a in r.alts)
        ]
        assert fills, f"{panel} has no `:root` fill row, so a height collapse would go unchecked"


def test_every_row_uses_known_modes_and_arguments() -> None:
    contract = load_contract()
    for owner, rules in contract.panels.items():
        for rule in rules:
            for alt in rule.alts:
                assert alt.name in PANEL_MODES, (
                    f"{owner} {rule.selector}: unknown mode {alt.name!r}"
                )
                allowed = MODE_ARGS.get(alt.name, frozenset())
                for key, _ in alt.args:
                    assert key in allowed, f"{owner} {rule.selector}: {alt.name} takes no {key!r}"
    for owner, rules in contract.surfaces.items():
        for rule in rules:
            for alt in rule.alts:
                assert alt.name in SURFACE_MODES, f"{owner}: unknown surface mode {alt.name!r}"


def _contract_classes() -> dict[str, set[str]]:
    """class name -> the rows (owner and selector) that rely on it, library classes excluded."""
    users: dict[str, set[str]] = {}
    contract = load_contract()
    for owner, rules in [*contract.panels.items(), *contract.surfaces.items()]:
        for rule in rules:
            for cls in selector_classes(rule.selector) - LIBRARY_CLASSES:
                users.setdefault(cls, set()).add(f"{owner} {rule.selector}")
    return users


def test_contract_selectors_name_classes_that_exist_in_source() -> None:
    """A renamed CSS class makes a row stale without any browser; catch it statically."""
    existing = source_class_names(TS_SRC)
    assert len(existing) > 100, "class discovery found almost nothing: it is vacuous"
    for cls, users in sorted(_contract_classes().items()):
        assert cls in existing, (
            f"class {cls!r} (rows: {sorted(users)}) is in no className in ts/src"
        )


def test_renaming_a_class_in_source_is_detected() -> None:
    """The File Browser tree row survives only while its exact class does, not a longer one."""
    tree = "stage-file-browser__tree"
    sources = {
        path: path.read_text(encoding="utf-8")
        for path in sorted(TS_SRC.rglob("*.tsx"))
        if ".test." not in path.name
    }
    before = class_names_in_source(sources.values())
    assert tree in before
    assert f"{tree}-item" in before, "the longer sibling classes are what a substring check hits"
    renamed = {
        path: re.sub(rf"(?<![\w-]){tree}(?![\w-])", f"{tree}-pane", text)
        for path, text in sources.items()
    }
    after = class_names_in_source(renamed.values())
    assert tree not in after, "a whole-token match must see that the exact class is gone"
    assert f"{tree}-pane" in after
    assert tree in _contract_classes()
    stale = sorted(cls for cls in _contract_classes() if cls not in after)
    assert tree in stale


def test_class_discovery_ignores_comments_and_prefix_matches() -> None:
    source = """
    // className="in-a-line-comment"
    /* className="in-a-block-comment" */
    const a = <div className="stage-x stage-x__item" />
    const b = <div className={'stage-y' + (on ? ' stage-y--on' : '')} />
    const c = <p>Don't {x}</p>
    const d = <i className={`stage-z ${extra}`} />
    """
    names = class_names_in_source([source])
    assert {"stage-x", "stage-x__item", "stage-y", "stage-y--on", "stage-z"} <= names
    assert not {"in-a-line-comment", "in-a-block-comment", "stage"} & names
    assert "stage-x__it" not in names


def test_every_floating_surface_in_source_has_a_contract_row() -> None:
    contract = load_contract()
    in_source = floating_surface_sources(TS_SRC)
    assert in_source, "no floating surfaces discovered in ts/src: discovery is vacuous"
    undeclared = sorted(in_source - contract.surface_sources())
    assert not undeclared, f"floating surface source(s) without a contract row: {undeclared}"
    stale = sorted(contract.surface_sources() - in_source)
    assert not stale, (
        f"floating-surface contract rows point at sources that are not floating surfaces: {stale}"
    )


def test_undeclared_floating_surface_is_named(tmp_path: Path) -> None:
    ts = tmp_path / "src"
    ts.mkdir()
    (ts / "Flyout.tsx").write_text(
        "export default function F() { return createPortal(<div/>, document.body) }",
        encoding="utf-8",
    )
    (ts / "Hint.tsx").write_text('export const H = () => <span role="tooltip" />', encoding="utf-8")
    (ts / "Ordinary.tsx").write_text(
        "export default function O() { return <div/> }", encoding="utf-8"
    )
    (ts / "PanelPortal.tsx").write_text(
        "export const P = () => createPortal(<div/>, panelHost)", encoding="utf-8"
    )
    found = {Path(p).name for p in floating_surface_sources(ts)}
    assert found == {"Flyout.tsx", "Hint.tsx"}, (
        "a body portal and a tooltip are floating surfaces only"
    )


def test_stress_directory_gives_the_file_selector_a_long_list() -> None:
    compatible = [
        p for p in (ROOT / STRESS_VIEWER_DIRECTORY).rglob("*") if p.suffix in {".html", ".svg"}
    ]
    assert len(compatible) > 20, (
        f"{STRESS_VIEWER_DIRECTORY} must hold more than twenty .html/.svg files so the live check "
        f"can exercise the file selector popover; it holds {len(compatible)}"
    )


def test_judge_reads_only_fields_the_measurement_script_produces() -> None:
    for name in JUDGE_FIELDS:
        assert name in MEASURE_JS, (
            f"the judge reads {name!r} but the measurement script never produces it"
        )


# --- synthetic measurements -------------------------------------------------------------------


def _box(x: float, y: float, w: float, h: float) -> dict[str, Any]:
    return {"x": x, "y": y, "w": w, "h": h, "r": x + w, "b": y + h}


def _region(x: float, y: float, w: float, h: float, **extra: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "found": True, "ox": "visible", "oy": "visible", "tov": "clip", "ws": "normal",
        "sh": h, "ch": h, "sw": w, "cw": w, "reach": {},
    }  # fmt: skip
    return {**base, **_box(x, y, w, h), **extra}


def _cell(
    panel: str,
    regions: dict[str, Any],
    *,
    root: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    clips: list[Any] | None = None,
) -> dict[str, Any]:
    body = body or _box(0, 0, 500, 300)
    return {
        "layout": "layout-1", "panel": panel, "slot": "primary", "size": [1280, 720], "found": True,
        "body": body, "root": root or _box(10, 10, 480, 280), "regions": regions,
        "clips": clips or [], "doc": {"sw": 1280, "sh": 720, "vw": 1280, "vh": 720},
    }  # fmt: skip


def _rules(panel: str) -> list[Rule]:
    return load_contract().panels[panel]


def _tree(**over: Any) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "ox": "auto",
        "oy": "auto",
        "sh": 700,
        "ch": 180,
        "reach": {"y": True},
    }
    return _region(20, 100, 460, 180, **{**fields, **over})


def test_judge_accepts_a_conforming_file_browser() -> None:
    header = _region(10, 10, 480, 30, sw=300, cw=480)
    regions = {sel: header for sel in (".stage-region__header", ".stage-file-browser__filters")}
    regions[".stage-file-browser__tree"] = _tree()
    findings, counts = judge_panel_cell(_rules("file-browser"), _cell("file-browser", regions))
    assert findings == [], [str(f) for f in findings]
    assert counts["exercised"] >= 1


def test_judge_flags_the_file_browser_clip_w18() -> None:
    """Instance 2: tree content exceeds the body and nothing scrolls it (REQ-007 W18)."""
    header = _region(10, 10, 480, 30)
    regions = {sel: header for sel in (".stage-region__header", ".stage-file-browser__filters")}
    regions[".stage-file-browser__tree"] = _tree(oy="hidden", ox="hidden")
    findings, _ = judge_panel_cell(_rules("file-browser"), _cell("file-browser", regions))
    assert any(
        ".stage-file-browser__tree" in f.detail and "cannot scroll" in f.detail for f in findings
    )


def test_judge_flags_a_scroller_that_grew_past_its_panel() -> None:
    """The notes strip today: a scroll-y paragraph taller than the strip, cut off by an ancestor."""
    rules = _rules("notes-strip")
    tall = _region(20, 12, 420, 71, ox="auto", oy="auto", sh=71, ch=71)
    regions = {r.selector: tall for r in rules if r.selector != ":root"}
    root = _box(10, 10, 480, 28)
    clip = {
        "el": "section.stage-notes-strip",
        "ox": "hidden",
        "oy": "hidden",
        "sh": 77,
        "ch": 26,
        "sw": 479,
        "cw": 479,
        "exempt": False,
    }
    findings, _ = judge_panel_cell(rules, _cell("notes-strip", regions, root=root, clips=[clip]))
    text = "\n".join(str(f) for f in findings)
    assert "not bounded by its panel" in text
    assert "silent-clip" in text


@pytest.mark.parametrize(
    "overflow",
    [
        {"ox": "visible", "oy": "auto"},  # vertical scroll, the shipped behavior
        {"ox": "auto", "oy": "hidden"},  # horizontal-scroll rotator variant (REQ-012 R12)
    ],
)
def test_notes_strip_declares_vertical_and_horizontal_scroll_as_alternatives(
    overflow: dict[str, str],
) -> None:
    """phase-wbf-06 changes how long entries overflow; both variants conform, neither violates."""
    rules = _rules("notes-strip")
    entry = _region(20, 12, 420, 20, sw=900, cw=420, sh=20, ch=20, reach={"x": True}, **overflow)
    regions = {r.selector: entry for r in rules if r.selector != ":root"}
    regions[".stage-popover__trigger"] = _region(450, 12, 30, 20)
    regions[".stage-tooltip__trigger"] = _region(12, 12, 20, 20)
    findings, _ = judge_panel_cell(
        rules, _cell("notes-strip", regions, root=_box(10, 10, 480, 40), body=_box(0, 0, 500, 50))
    )
    assert findings == [], [str(f) for f in findings]


def test_notes_strip_marquee_variant_is_declared_and_bounded() -> None:
    rules = _rules("notes-strip")
    assert any(a.name == "marquee" for r in rules for a in r.alts), (
        "the marquee alternative must stay declared"
    )
    root = _box(10, 10, 480, 40)
    moving = _region(20, 12, 420, 20, ox="hidden", oy="hidden")
    escaped = _region(20, 12, 420, 20, ox="hidden", oy="hidden", b=400)
    marquee = next(r for r in rules if any(a.name == "marquee" for a in r.alts))
    ok = [check_alt(a, marquee.selector, moving, root, _box(0, 0, 500, 300)) for a in marquee.alts]
    bad = [
        check_alt(a, marquee.selector, escaped, root, _box(0, 0, 500, 300)) for a in marquee.alts
    ]
    assert any(r is None for r in ok) and all(r is not None for r in bad)


def test_judge_flags_a_height_collapse() -> None:
    """Instance 1 (phase-wb-08, idea 000104): the panel box collapses inside a tall slot body."""
    rules = _rules("terminal")
    findings, _ = judge_panel_cell(rules, _cell("terminal", {}, root=_box(10, 10, 480, 60)))
    assert any("does not fill its slot body" in f.detail for f in findings)


def test_chrome_offset_does_not_make_a_correct_panel_fail() -> None:
    """Instance 5: ~98 px of chrome between slot body and the xterm is legitimate.

    The fill row is anchored on the panel box, so a terminal whose screen is 98 px shorter than
    its slot body but ends at its panel's bottom edge conforms. A slot-height proxy would fail it.
    """
    rules = _rules("terminal")
    body = _box(0, 0, 500, 620)
    root = _box(10, 10, 480, 600)
    xterm = _region(20, 108, 460, 500, oy="hidden", ox="hidden")
    tabbar = _region(20, 60, 460, 36, ox="auto", oy="auto")
    track = _region(466, 108, 14, 500, slider={"h": 43})
    regions = {
        ".stage-terminal-tabbar": tabbar,
        ".xterm": xterm,
        ".xterm .scrollbar.vertical": track,
    }
    regions[".stage-region__header"] = _region(10, 10, 480, 40)
    cell = _cell("terminal", regions, root=root)
    cell["body"] = body
    findings, _ = judge_panel_cell(rules, cell)
    assert findings == [], [str(f) for f in findings]
    assert body["h"] - xterm["h"] >= 98 > ROOT_FILL_TOLERANCE_PX, (
        "fixture must carry the 98px offset"
    )


def test_judge_flags_a_header_that_overflows_instead_of_wrapping() -> None:
    rules = _rules("terminal")
    regions = {r.selector: _region(10, 10, 480, 40) for r in rules if r.selector != ":root"}
    regions[".stage-region__header"] = _region(10, 10, 393, 40, sw=410, cw=393)
    findings, _ = judge_panel_cell(rules, _cell("terminal", regions))
    assert any("overflows instead of wrapping" in f.detail for f in findings)


def test_judge_reports_a_missing_non_optional_region_and_skips_optional_ones() -> None:
    rules = _rules("file-browser")
    findings, counts = judge_panel_cell(rules, _cell("file-browser", {}))
    assert any(f.rule == "region-missing" for f in findings)
    term_rules = _rules("terminal-cmd")
    findings, counts = judge_panel_cell(
        term_rules, _cell("terminal-cmd", {".stage-region__header": _region(10, 10, 480, 40)})
    )
    assert counts["na"] >= 1 and not any(f.rule == "region-missing" for f in findings)


def test_truncate_mode_requires_an_ellipsis() -> None:
    alt = Alt("truncate")
    root, body = _box(0, 0, 100, 100), _box(0, 0, 100, 100)
    good = _region(0, 0, 100, 20, tov="ellipsis", ws="nowrap")
    bad = _region(0, 0, 100, 20, tov="clip", ws="nowrap")
    assert check_alt(alt, ".x", good, root, body) is None
    assert check_alt(alt, ".x", bad, root, body) is not None


def _popover(**over: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "layout": "layout-1", "label": "file selector", "size": [1280, 720], "vw": 1280, "vh": 720,
        "bubble": _box(100, 200, 256, 300), "clipRects": [], "dismiss": _box(320, 202, 20, 20),
        "natural": 300, "spaceAbove": 400, "spaceBelow": 300,
    }  # fmt: skip
    return {**base, **over}


def _surface_rules(name: str) -> list[Rule]:
    return load_contract().surfaces[name]


def test_popover_judge_flags_the_height_floor_000117() -> None:
    """Instance 4 (idea 000117): opens upward into 142 px while 500 px of room exists below."""
    starved = _popover(bubble=_box(100, 20, 256, 142), natural=480, spaceAbove=142, spaceBelow=500)
    findings = judge_surface_cell("popover", _surface_rules("popover"), starved)
    assert any(f.rule == "not-starved" for f in findings), [str(f) for f in findings]
    assert judge_surface_cell("popover", _surface_rules("popover"), _popover()) == []


def test_popover_judge_flags_a_dismiss_control_off_screen() -> None:
    off = _popover(bubble=_box(100, 650, 256, 120), dismiss=_box(320, 700, 20, 20), vh=720)
    findings = judge_surface_cell(
        "popover", _surface_rules("popover"), {**off, "dismiss": _box(320, 740, 20, 20)}
    )
    assert any(f.rule == "dismiss-visible" for f in findings)
    assert any(f.rule == "in-viewport" for f in findings)


def test_tooltip_judge_flags_the_rotator_cutoff_000130() -> None:
    """Instance 3 (idea 000130): the bubble is cut by its overflow-hidden ancestor."""
    strip = {"el": "section.stage-region", **_box(10, 10, 480, 40)}
    cut = {
        "layout": "layout-1", "label": "tooltip notes", "size": [1280, 720], "vw": 1280, "vh": 720,
        "bubble": _box(12, 30, 200, 90), "clipRects": [strip],
        "tipSw": 200, "tipCw": 200, "tipSh": 90, "tipCh": 90,
    }  # fmt: skip
    findings = judge_surface_cell("tooltip", _surface_rules("tooltip"), cut)
    assert any(f.rule == "not-clipped" for f in findings), [str(f) for f in findings]
    inside = {**cut, "bubble": _box(12, 30, 200, 10)}
    assert judge_surface_cell("tooltip", _surface_rules("tooltip"), inside) == []


def test_live_matrix_covers_every_registered_panel_in_every_eligible_slot() -> None:
    contract = load_contract()
    cells = live_cells(contract, REQUIRED_SIZES)
    ids = set(checked_panel_types(REGISTRY_SOURCE))
    assert {c["panel"] for c in cells} == ids
    for layout in LAYOUTS_DIR.glob("*.json"):
        data = json.loads(layout.read_text(encoding="utf-8"))
        expected = sum(len(p["eligible_slots"]) for p in data["panels"]) * len(REQUIRED_SIZES)
        assert sum(1 for c in cells if c["layout"] == data["layout_id"]) == expected


def test_break_contract_css_exists_for_every_scrolling_or_filling_panel() -> None:
    """The live self-test needs a violation to inject for each panel; none may be unbreakable."""
    for panel, rules in load_contract().panels.items():
        assert break_contract_css(rules) is not None, (
            f"{panel} has no region the self-test can break"
        )


def test_scrollbar_mode_needs_a_bounded_track_with_a_slider() -> None:
    """xterm 6 scrolls through a virtual scrollbar; its native viewport never moves."""
    alt = Alt("scrollbar")
    root, body = _box(10, 10, 480, 300), _box(0, 0, 500, 320)
    good = _region(466, 40, 14, 250, slider={"h": 43})
    assert check_alt(alt, ".track", good, root, body) is None
    assert scroll_exercised(good, root)
    no_slider = _region(466, 40, 14, 250, slider=None)
    assert "no slider" in (check_alt(alt, ".track", no_slider, root, body) or "")
    escaped = _region(466, 40, 14, 900, slider={"h": 43})
    assert "not bounded" in (check_alt(alt, ".track", escaped, root, body) or "")
    idle = _region(466, 40, 14, 250, slider={"h": 250})
    assert not scroll_exercised(idle, root), "a slider as tall as its track means nothing scrolled"


def test_frame_and_visible_modes() -> None:
    root, body = _box(10, 10, 480, 300), _box(0, 0, 500, 320)
    frame, visible = Alt("frame", (("min-h", 60.0),)), Alt("visible")
    assert check_alt(frame, ".f", _region(10, 60, 480, 200), root, body) is None
    assert "below the floor" in (check_alt(frame, ".f", _region(10, 60, 480, 20), root, body) or "")
    assert check_alt(visible, ".v", _region(450, 12, 26, 20), root, body) is None
    assert "outside" in (check_alt(visible, ".v", _region(470, 300, 40, 30), root, body) or "")


def _notes_judgement(entry: dict[str, Any]) -> list[Finding]:
    """Judge a notes strip whose entry region is `entry`; every other region conforms."""
    rules = _rules("notes-strip")
    regions = {".stage-notes-strip__current": entry}
    regions[".stage-popover__trigger"] = _region(450, 12, 30, 24)
    regions[".stage-tooltip__trigger"] = _region(12, 12, 20, 24)
    cell = _cell("notes-strip", regions, root=_box(10, 10, 480, 40), body=_box(0, 0, 500, 50))
    return judge_panel_cell(rules, cell)[0]


def _on_entry(findings: list[Finding]) -> list[Finding]:
    return on_region(findings, ".stage-notes-strip__current")


def test_bounded_clip_with_no_way_to_read_it_fails() -> None:
    """A strip entry cut off at 20 px with 90 px of text and no scrolling must not conform."""
    clipped = _region(20, 12, 420, 20, ox="hidden", oy="hidden", sh=90, ch=20)
    assert _on_entry(_notes_judgement(clipped)), "overflow hidden must not pass any alternative"


def test_horizontal_scroller_that_clips_vertically_fails() -> None:
    entry = _region(20, 12, 420, 20, ox="auto", oy="hidden", sw=900, cw=420, sh=90, ch=20)
    findings = _on_entry(_notes_judgement(entry))
    assert findings and "clipped on y" in findings[0].detail


def test_collapsed_regions_fail_their_minimum_size() -> None:
    entry = _region(20, 12, 1, 1, ox="auto", oy="auto")
    assert "below the minimum" in _on_entry(_notes_judgement(entry))[0].detail
    tiny_trigger = _region(450, 12, 4, 4)
    assert "below the minimum" in (
        check_alt(Alt("visible"), ".t", tiny_trigger, _box(10, 10, 480, 40), _box(0, 0, 500, 50))
        or ""
    )


def test_a_legal_horizontal_scroll_still_passes() -> None:
    entry = _region(
        20, 12, 420, 20, ox="auto", oy="hidden", sw=900, cw=420, sh=20, ch=20, reach={"x": True}
    )
    assert _on_entry(_notes_judgement(entry)) == []


@pytest.mark.parametrize(
    "motion", [{"animations": 1, "changed": False}, {"animations": 0, "changed": True}]
)
def test_a_legal_animated_marquee_passes(motion: dict[str, Any]) -> None:
    """phase-wbf-06's variant: text wider than its box, clipped by design, moving."""
    entry = _region(20, 12, 420, 20, ox="hidden", oy="hidden", sw=900, cw=420, motion=motion)
    assert _on_entry(_notes_judgement(entry)) == []


def test_a_marquee_that_does_not_move_fails() -> None:
    entry = _region(
        20,
        12,
        420,
        20,
        ox="hidden",
        oy="hidden",
        sw=900,
        cw=420,
        motion={"animations": 0, "changed": False},
    )
    findings = _on_entry(_notes_judgement(entry))
    assert findings and "nothing moves it" in findings[0].detail


def test_a_marquee_with_nothing_to_move_passes_without_motion() -> None:
    entry = _region(20, 12, 420, 20, ox="hidden", oy="hidden", sw=300, cw=420)
    assert _on_entry(_notes_judgement(entry)) == []


def test_wrap_fails_when_the_header_wraps_taller_than_its_panel() -> None:
    alt = Alt("wrap")
    root, body = _box(10, 10, 300, 100), _box(0, 0, 320, 120)
    fits = _region(10, 10, 300, 60, sw=300, cw=300)
    too_tall = _region(10, 10, 300, 160, sw=300, cw=300)
    assert check_alt(alt, ".h", fits, root, body) is None
    assert "more rows than the panel holds" in (check_alt(alt, ".h", too_tall, root, body) or "")


def test_differential_choice_skips_regions_that_already_fail() -> None:
    contract = load_contract()
    cells = [
        {"panel": "notes-strip", "layout": "layout-1", "slot": "strip"},
        {"panel": "notes-strip", "layout": "layout-2", "slot": "strip"},
    ]
    failing_entry = Finding("w", "scroll-y", "Active entry (.stage-notes-strip__current): x")
    chosen, unproven = choose_differential_breaks(contract, cells, [[failing_entry], []])
    assert unproven == []
    (cell, _label, selector) = chosen[0]
    assert selector != ".stage-notes-strip__current" or cell["layout"] == "layout-2"
    assert "css" in cell


def test_differential_choice_names_a_panel_whose_every_region_already_fails() -> None:
    contract = load_contract()
    cells = [{"panel": "notes-strip", "layout": "layout-1", "slot": "strip"}]
    every = [
        Finding("w", "m", f"x ({sel}): y")
        for _, _, sel in contract_breaks(contract.panels["notes-strip"])
    ]
    chosen, unproven = choose_differential_breaks(contract, cells, [every])
    assert chosen == []
    assert len(unproven) == 1 and unproven[0].startswith("notes-strip:")
    assert "already fails" in unproven[0]


if __name__ == "__main__":
    raise SystemExit(main())
