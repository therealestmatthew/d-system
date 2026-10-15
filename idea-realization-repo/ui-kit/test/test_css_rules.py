"""Lint rules for every hand-written stylesheet under `ui-kit/src/css/`.

From the Kit v0 class contract and ARCH-001 principle 3 (layout and look are data): component CSS
takes colour, type, space, radius, shadow, z and motion from `var(--ui-…)` only. Each test is
parametrised by file, so a failure names the file. The rules:

- no colour literal: hex, rgb()/rgba(), hsl()/hsla(), hwb(), lab(), lch(), oklab(), oklch(),
  color(), or a named colour (transparent, currentColor and inherit are allowed);
- no px length other than 0px and 1px (hairline borders), in declarations and in at-rule
  preludes such as media queries;
- every var() names an --ui- property, and every one named is defined in dist/tokens.css;
- every class selector has the ui- prefix;
- no state class: .is-*, .active, .selected, .open, .disabled, or a BEM modifier of those names
  (state is expressed with ARIA, native or data attributes).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent.parent
SRC = KIT / "src" / "css"
TOKENS = KIT / "dist" / "tokens.css"
CSS_FILES = sorted(SRC.rglob("*.css"))
IDS = [p.relative_to(KIT).as_posix() for p in CSS_FILES]

NAMED_COLOURS = frozenset(
    """
    aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond blue
    blueviolet brown burlywood cadetblue chartreuse chocolate coral cornflowerblue cornsilk
    crimson cyan darkblue darkcyan darkgoldenrod darkgray darkgreen darkgrey darkkhaki
    darkmagenta darkolivegreen darkorange darkorchid darkred darksalmon darkseagreen
    darkslateblue darkslategray darkslategrey darkturquoise darkviolet deeppink deepskyblue
    dimgray dimgrey dodgerblue firebrick floralwhite forestgreen fuchsia gainsboro ghostwhite
    gold goldenrod gray green greenyellow grey honeydew hotpink indianred indigo ivory khaki
    lavender lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan
    lightgoldenrodyellow lightgray lightgreen lightgrey lightpink lightsalmon lightseagreen
    lightskyblue lightslategray lightslategrey lightsteelblue lightyellow lime limegreen linen
    magenta maroon mediumaquamarine mediumblue mediumorchid mediumpurple mediumseagreen
    mediumslateblue mediumspringgreen mediumturquoise mediumvioletred midnightblue mintcream
    mistyrose moccasin navajowhite navy oldlace olive olivedrab orange orangered orchid
    palegoldenrod palegreen paleturquoise palevioletred papayawhip peachpuff peru pink plum
    powderblue purple rebeccapurple red rosybrown royalblue saddlebrown salmon sandybrown
    seagreen seashell sienna silver skyblue slateblue slategray slategrey snow springgreen
    steelblue tan teal thistle tomato turquoise violet wheat white whitesmoke yellow
    yellowgreen
    canvas canvastext linktext visitedtext activetext buttonface buttontext buttonborder field
    fieldtext highlight highlighttext selecteditem selecteditemtext mark marktext graytext
    accentcolor accentcolortext
    """.split()
)
COLOUR_FUNCTION = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|\b(rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\(", re.IGNORECASE
)
PX = re.compile(r"(?<![\w.#-])(-?(?:\d+\.?\d*|\.\d+))px\b")
VAR = re.compile(r"var\(\s*(--[\w-]+)")
CLASS = re.compile(r"\.(-?[_a-zA-Z][\w-]*)")
STATE_WORDS = ("active", "selected", "open", "disabled")
# Properties whose values are names, not colours; a named-colour word there is not a colour.
NAME_VALUED = re.compile(
    r"^(grid-area|grid-template-areas|grid-row|grid-column|animation(-name)?|"
    r"font-family|counter-.*|list-style.*|content|container(-name)?|view-transition-name)$"
)


@dataclass
class Sheet:
    selectors: list[str] = field(default_factory=list)
    preludes: list[str] = field(default_factory=list)
    declarations: list[tuple[str, str]] = field(default_factory=list)


def _strip(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    return re.sub(r'"[^"]*"|\'[^\']*\'', '""', css)


def parse(css: str) -> Sheet:
    """A small brace-level parser: enough to separate selectors, at-rule preludes and
    declarations in hand-written CSS (comments and strings removed first)."""
    sheet = Sheet()
    buf = ""

    def flush_declaration(text: str) -> None:
        text = text.strip()
        if not text:
            return
        prop, sep, value = text.partition(":")
        if sep:
            sheet.declarations.append((prop.strip().lower(), value.strip()))

    for ch in _strip(css):
        if ch == "{":
            *decls, head = buf.split(";")
            for d in decls:
                flush_declaration(d)
            head = head.strip()
            (sheet.preludes if head.startswith("@") else sheet.selectors).append(head)
            buf = ""
        elif ch == "}":
            flush_declaration(buf)
            buf = ""
        elif ch == ";":
            flush_declaration(buf)
            buf = ""
        else:
            buf += ch
    return sheet


def _defined_tokens() -> set[str]:
    return set(re.findall(r"(--ui-[\w-]+)\s*:", TOKENS.read_text(encoding="utf-8")))


def _sheet(path: Path) -> Sheet:
    return parse(path.read_text(encoding="utf-8"))


def test_there_are_stylesheets() -> None:
    assert (SRC / "base.css") in CSS_FILES
    assert (SRC / "layout.css") in CSS_FILES


@pytest.mark.parametrize("path", CSS_FILES, ids=IDS)
def test_no_colour_literal(path: Path) -> None:
    bad: list[str] = []
    for prop, value in _sheet(path).declarations:
        if COLOUR_FUNCTION.search(value):
            bad.append(f"{prop}: {value}")
            continue
        if NAME_VALUED.match(prop):
            continue
        words = re.findall(r"(?<![\w-])[a-zA-Z]+(?![\w(-])", re.sub(r"var\([^)]*\)", "", value))
        if any(w.lower() in NAMED_COLOURS for w in words):
            bad.append(f"{prop}: {value}")
    assert not bad, f"{path.name}: colour literals (use var(--ui-color-*)): {bad}"


@pytest.mark.parametrize("path", CSS_FILES, ids=IDS)
def test_no_px_other_than_0_and_1(path: Path) -> None:
    sheet = _sheet(path)
    texts = [f"{p}: {v}" for p, v in sheet.declarations] + sheet.preludes
    bad = [t for t in texts for n in PX.findall(t) if float(n) not in (0.0, 1.0)]
    assert not bad, f"{path.name}: px values other than 0/1px (use tokens or em/rem): {bad}"


@pytest.mark.parametrize("path", CSS_FILES, ids=IDS)
def test_every_var_is_a_defined_ui_token(path: Path) -> None:
    defined = _defined_tokens()
    sheet = _sheet(path)
    used = {n for _, v in sheet.declarations for n in VAR.findall(v)}
    used |= {n for p in sheet.preludes for n in VAR.findall(p)}
    not_ui = sorted(n for n in used if not n.startswith("--ui-"))
    undefined = sorted(n for n in used if n.startswith("--ui-") and n not in defined)
    assert not not_ui, f"{path.name}: var() of a non --ui- property: {not_ui}"
    assert not undefined, f"{path.name}: var() of a name not in dist/tokens.css: {undefined}"


def _classes(path: Path) -> set[str]:
    names: set[str] = set()
    for selector in _sheet(path).selectors:
        names |= set(CLASS.findall(re.sub(r"\[[^\]]*\]", "", selector)))
    return names


@pytest.mark.parametrize("path", CSS_FILES, ids=IDS)
def test_every_class_has_ui_prefix(path: Path) -> None:
    bad = sorted(c for c in _classes(path) if not c.startswith("ui-"))
    assert not bad, f"{path.name}: class selectors without the ui- prefix: {bad}"


@pytest.mark.parametrize("path", CSS_FILES, ids=IDS)
def test_no_state_classes(path: Path) -> None:
    bad = sorted(
        c
        for c in _classes(path)
        if c.startswith("is-")
        or c in STATE_WORDS
        or any(c.endswith(f"--{w}") for w in STATE_WORDS)
    )
    assert not bad, f"{path.name}: state expressed as a class (use ARIA/data attributes): {bad}"


# ---- the linter itself ----


def test_linter_catches_violations() -> None:
    css = """
    .card.is-open { color: #fff; background: rgb(0 0 0); border: 2px solid red; }
    .ui-x--selected { padding: var(--ui-nope); margin: var(--private); }
    @media (max-width: 1100px) { .ui-y { border: 1px solid transparent; } }
    """
    sheet = parse(css)
    assert ".card.is-open" in sheet.selectors
    assert "@media (max-width: 1100px)" in sheet.preludes
    values = dict(sheet.declarations)
    assert COLOUR_FUNCTION.search(values["color"])
    borders = [v for p, v in sheet.declarations if p == "border"]
    assert PX.findall(borders[0]) == ["2"]
    assert any(w in NAMED_COLOURS for w in borders[0].split())
    assert PX.findall(sheet.preludes[0]) == ["1100"]
    assert VAR.findall(values["padding"]) == ["--ui-nope"]


def test_linter_allows_hairlines_and_keywords() -> None:
    sheet = parse(".ui-a { border: 1px solid currentColor; outline: 0px; color: inherit; }")
    for prop, value in sheet.declarations:
        assert not COLOUR_FUNCTION.search(value), prop
        assert all(float(n) in (0.0, 1.0) for n in PX.findall(value))
