#!/usr/bin/env python3
"""Generate the ui-kit token stylesheet from its tokens file.

`ui-kit/tokens/tokens.json` is the only place the kit's design values live. This tool turns it
into `ui-kit/dist/tokens.css`, which no one edits by hand. It loads the file strictly, writes a
block per accent set, and `--contrast` checks every colour pair for every theme and accent.

Every custom property is named `--ui-<group>-<name>`; colours are `--ui-color-<role>`.

The generated sheet has these blocks, always in this order:

    :root { scalar tokens, light neutrals, default accent (light) }
    :root[data-theme="light"] { light neutrals }             forced light (no accent: see below)
    [data-accent="<name>"] { accent set, light }              one per accent, any element
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) { dark neutrals, default accent (dark) }
      :root:not([data-theme="light"])[data-accent="<name>"],
      :root:not([data-theme="light"]) [data-accent="<name>"] { accent set, dark }
    }
    :root[data-theme="dark"] { dark neutrals, default accent (dark) }   forced dark
    :root[data-theme="dark"][data-accent="<name>"], ... { accent set, dark }
    [data-density="compact"] / [data-density="comfortable"] { type and space only }
    @media (width < W), (height < H) {                        automatic density (auto_density)
      .ui-shell:not([data-density="comfortable"], [data-density="comfortable"] *) { compact }
    }
    @media (prefers-reduced-motion: reduce) { :root { durations 0ms } }

The automatic-density block repeats one density's declarations inside a viewport media query,
scoped to the app shell, so every component in a small shell steps down and a report page (no
.ui-shell) does not. `src/css/layout.css` names the same breakpoint in its header; a test keeps
any media query there equal to this one.

Dark blocks set colour properties and `color-scheme` only. The forced-light block carries no
accent roles because its specificity (0,2,0) would beat `[data-accent]` (0,1,0) on <html>.
`data-theme` belongs on <html>; `data-accent` and `data-density` work on any element.

Determinism: declarations are sorted by name inside each block, accent blocks by accent name;
no clock or environment is read; output is LF-terminated UTF-8.

    uv run python ui-kit/tools/build_tokens.py              # rewrite dist/tokens.css
    uv run python ui-kit/tools/build_tokens.py --check      # exit 1 if dist/tokens.css is stale
    uv run python ui-kit/tools/build_tokens.py --contrast   # every pair x theme x accent
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

KIT = Path(__file__).resolve().parent.parent
TOKENS = KIT / "tokens" / "tokens.json"
OUTPUT = KIT / "dist" / "tokens.css"

PREFIX = "--ui-"
THEMES = ("light", "dark")
DENSITIES = ("compact", "comfortable")
DENSITY_GROUPS = ("fs", "lh", "space", "ctl")
AUTO_DENSITY_KEYS = ("density", "below")
AUTO_DENSITY_BELOW = ("width", "height")
# The shell, unless it or an ancestor asks for comfortable explicitly. An explicit
# data-density="compact" needs no exception: it sets the same values.
AUTO_DENSITY_SCOPE = '.ui-shell:not([data-density="comfortable"], [data-density="comfortable"] *)'
_EM = r"\d+(\.\d+)?em"
GENERIC_FAMILIES = ("sans-serif", "serif", "monospace", "system-ui", "cursive", "fantasy")

_PX = r"\d+(\.\d+)?px"
_NUM = r"\d+(\.\d+)?"
_INT = r"\d+"
_MS = r"\d+ms"
_BEZIER = r"cubic-bezier\(\s*[\d.]+,\s*[\d.]+,\s*[\d.]+,\s*[\d.]+\s*\)"
_SHADOW = r"none|[^#;{}]+"
_FONT = r"[^;{}]+"

# The schema. Each scalar group: its exact key set and the pattern every value must match.
SCALAR_GROUPS: dict[str, tuple[tuple[str, ...], str]] = {
    "font": (("sans", "mono"), _FONT),
    "fs": (("xs", "sm", "md", "lg", "xl", "2xl", "3xl"), _PX),
    "lh": (("tight", "ui", "prose"), _NUM),
    "fw": (("regular", "semibold", "bold"), _INT),
    "space": (tuple(str(i) for i in range(10)), _PX),
    "ctl": (("sm", "md", "lg"), _PX),
    "radius": (("none", "sm", "md", "lg", "pill"), _PX),
    "shadow": (("e0", "e1", "e2", "e3"), _SHADOW),
    "z": (("base", "sticky", "dock", "dropdown", "overlay", "modal", "toast", "tooltip"), _INT),
    "dur": (("fast", "base", "slow"), _MS),
    "ease": (("standard", "exit"), _BEZIER),
    "focus": (("width", "offset"), _PX),
}
NEUTRAL_ROLES = (
    "bg", "surface", "surface-2", "sunken", "surface-e1", "surface-e2", "surface-e3",
    "line", "line-strong", "text", "muted", "overlay", "shadow",
    "ok", "ok-bg", "warn", "warn-bg", "info", "info-bg", "err", "err-bg",
)
ACCENT_ROLES = ("accent", "accent-hover", "on-accent", "accent-2", "focus", "selection", "ai")
COLOUR_ROLES = NEUTRAL_ROLES + ACCENT_ROLES
TOP_LEVEL = (
    "meta", *SCALAR_GROUPS, "reduced_motion", "density", "auto_density", "color", "accents",
    "ai_distinctness", "contrast_pairs",
)
META_KEYS = ("name", "version", "description", "origin")
PAIR_KEYS = ("fg", "bg", "min", "use")
DISTINCT_KEYS = ("min_hue_gap_deg", "chroma_floor", "from")

HEX = re.compile(r"#[0-9a-f]{6}([0-9a-f]{2})?")
OPAQUE_HEX = re.compile(r"#[0-9a-f]{6}")
NAME = re.compile(r"[a-z][a-z0-9-]*")


class TokenError(ValueError):
    """The tokens file breaks the schema."""


@dataclass(frozen=True)
class Pair:
    fg: str
    bg: str
    min: float
    use: str


@dataclass(frozen=True)
class AccentSet:
    label: str
    note: str
    colours: dict[str, dict[str, str]]  # theme -> role -> hex


@dataclass(frozen=True)
class Distinctness:
    min_hue_gap_deg: float
    chroma_floor: float
    against: tuple[str, ...]


@dataclass(frozen=True)
class AutoDensity:
    density: str
    width: str  # em
    height: str  # em

    @property
    def media(self) -> str:
        """The media query condition, the same text layout.css uses."""
        return f"(width < {self.width}), (height < {self.height})"


@dataclass(frozen=True)
class Tokens:
    meta: dict[str, str]
    scalars: dict[str, dict[str, str]]  # group -> key -> value
    reduced_motion: dict[str, dict[str, str]]
    density: dict[str, dict[str, dict[str, str]]]  # density -> group -> key -> value
    auto_density: AutoDensity
    neutrals: dict[str, dict[str, str]]  # theme -> role -> hex
    default_accent: str
    accents: dict[str, AccentSet]
    distinctness: Distinctness
    pairs: tuple[Pair, ...]

    def palette(self, theme: str, accent: str) -> dict[str, str]:
        """Every colour role for one theme and one accent set."""
        return {**self.neutrals[theme], **self.accents[accent].colours[theme]}


# ---------------------------------------------------------------- strict loader


def _obj(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TokenError(f"{where}: expected an object")
    return value


def _keys(
    obj: dict[str, Any], where: str, required: tuple[str, ...], optional: tuple[str, ...] = ()
) -> None:
    unknown = sorted(set(obj) - set(required) - set(optional))
    if unknown:
        raise TokenError(f"{where}: unknown key(s) {unknown}")
    missing = [k for k in required if k not in obj]
    if missing:
        raise TokenError(f"{where}: missing key(s) {missing}")


def _str(value: Any, where: str, pattern: str | re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str):
        raise TokenError(f"{where}: expected a string")
    if pattern is not None and not re.fullmatch(pattern, value):
        raise TokenError(f"{where}: {value!r} is not a valid value")
    return value


def _strings(value: Any, where: str, keys: tuple[str, ...], pattern: str | re.Pattern[str],
             subset: bool = False) -> dict[str, str]:
    obj = _obj(value, where)
    if subset:
        _keys(obj, where, (), keys)
    else:
        _keys(obj, where, keys)
    return {k: _str(v, f"{where}.{k}", pattern) for k, v in obj.items()}


def _number(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TokenError(f"{where}: expected a number")
    return float(value)


def parse_tokens(data: Any) -> Tokens:
    """Validate a parsed tokens document; raise `TokenError` on any unknown or missing key."""
    root = _obj(data, "tokens")
    _keys(root, "tokens", TOP_LEVEL)

    meta = _strings(root["meta"], "meta", META_KEYS, r".+")
    scalars = {g: _strings(root[g], g, keys, pat) for g, (keys, pat) in SCALAR_GROUPS.items()}
    for name, stack in scalars["font"].items():
        last = stack.rsplit(",", 1)[-1].strip()
        if last not in GENERIC_FAMILIES:
            raise TokenError(f"font.{name}: stack ends in {last!r}, not a generic family")

    rm = _obj(root["reduced_motion"], "reduced_motion")
    _keys(rm, "reduced_motion", ("dur",))
    reduced = {"dur": _strings(rm["dur"], "reduced_motion.dur", SCALAR_GROUPS["dur"][0], _MS)}

    dens = _obj(root["density"], "density")
    _keys(dens, "density", DENSITIES)
    density: dict[str, dict[str, dict[str, str]]] = {}
    for d in DENSITIES:
        groups = _obj(dens[d], f"density.{d}")
        _keys(groups, f"density.{d}", (), DENSITY_GROUPS)
        density[d] = {
            g: _strings(groups[g], f"density.{d}.{g}", SCALAR_GROUPS[g][0], SCALAR_GROUPS[g][1],
                        subset=True)
            for g in groups
        }

    auto = _obj(root["auto_density"], "auto_density")
    _keys(auto, "auto_density", AUTO_DENSITY_KEYS, ("note",))
    auto_name = _str(auto["density"], "auto_density.density")
    if auto_name not in DENSITIES:
        raise TokenError(f"auto_density.density: {auto_name!r} is not a density")
    _str(auto.get("note", ""), "auto_density.note")
    below = _strings(auto["below"], "auto_density.below", AUTO_DENSITY_BELOW, _EM)
    auto_density = AutoDensity(auto_name, below["width"], below["height"])

    col = _obj(root["color"], "color")
    _keys(col, "color", THEMES)
    neutrals = {t: _strings(col[t], f"color.{t}", NEUTRAL_ROLES, HEX) for t in THEMES}

    acc = _obj(root["accents"], "accents")
    _keys(acc, "accents", ("default", "sets"))
    sets = _obj(acc["sets"], "accents.sets")
    if not sets:
        raise TokenError("accents.sets: no accent set")
    accents: dict[str, AccentSet] = {}
    for name, raw in sets.items():
        where = f"accents.sets.{name}"
        _str(name, f"{where} (name)", NAME)
        obj = _obj(raw, where)
        _keys(obj, where, ("label", *THEMES), ("note",))
        accents[name] = AccentSet(
            label=_str(obj["label"], f"{where}.label", r".+"),
            note=_str(obj.get("note", ""), f"{where}.note"),
            colours={t: _strings(obj[t], f"{where}.{t}", ACCENT_ROLES, HEX) for t in THEMES},
        )
    default = _str(acc["default"], "accents.default")
    if default not in accents:
        raise TokenError(f"accents.default: {default!r} is not an accent set")

    dist = _obj(root["ai_distinctness"], "ai_distinctness")
    _keys(dist, "ai_distinctness", DISTINCT_KEYS)
    against = dist["from"]
    if not isinstance(against, list) or not all(isinstance(r, str) for r in against):
        raise TokenError("ai_distinctness.from: expected a list of role names")
    for role in against:
        if role not in COLOUR_ROLES:
            raise TokenError(f"ai_distinctness.from: unknown colour role {role!r}")
    distinctness = Distinctness(
        _number(dist["min_hue_gap_deg"], "ai_distinctness.min_hue_gap_deg"),
        _number(dist["chroma_floor"], "ai_distinctness.chroma_floor"),
        tuple(against),
    )

    raw_pairs = root["contrast_pairs"]
    if not isinstance(raw_pairs, list) or not raw_pairs:
        raise TokenError("contrast_pairs: expected a non-empty list")
    pairs: list[Pair] = []
    for i, raw in enumerate(raw_pairs):
        where = f"contrast_pairs[{i}]"
        obj = _obj(raw, where)
        _keys(obj, where, PAIR_KEYS)
        pair = Pair(
            _str(obj["fg"], f"{where}.fg"), _str(obj["bg"], f"{where}.bg"),
            _number(obj["min"], f"{where}.min"), _str(obj["use"], f"{where}.use"),
        )
        for role in (pair.fg, pair.bg):
            if role not in COLOUR_ROLES:
                raise TokenError(f"{where}: unknown colour role {role!r}")
        pairs.append(pair)

    tokens = Tokens(meta, scalars, reduced, density, auto_density, neutrals, default, accents,
                    distinctness, tuple(pairs))
    for theme in THEMES:
        for name in accents:
            palette = tokens.palette(theme, name)
            for pair in pairs:
                for role in (pair.fg, pair.bg):
                    if not OPAQUE_HEX.fullmatch(palette[role]):
                        raise TokenError(
                            f"contrast pair {pair.fg}/{pair.bg}: {role} is translucent in "
                            f"{theme}/{name}; contrast needs opaque colours"
                        )
    return tokens


def read_source(path: Path = TOKENS) -> str:
    """The tokens file's text with line endings normalised to LF."""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def load_tokens(path: Path = TOKENS) -> Tokens:
    """The validated tokens file."""
    return parse_tokens(json.loads(read_source(path)))


# ---------------------------------------------------------------- rendering

HEADER = """\
/*
  ui-kit design tokens. GENERATED: do not edit by hand.

  Source:     ui-kit/tokens/tokens.json ({name} {version})
  sha256:     {sha}
  Regenerate: uv run python ui-kit/tools/build_tokens.py
  Check:      uv run python ui-kit/tools/build_tokens.py --check

  Every property is --ui-<group>-<name>. Put data-theme="light|dark" on <html> to force a
  theme; without it the page follows prefers-color-scheme. data-accent="<name>" and
  data-density="compact|comfortable" work on any element.
  Accent sets: {accents} (default {default}).
*/"""


def _decls(values: dict[str, str], indent: str) -> list[str]:
    return [f"{indent}{PREFIX}{name}: {values[name]};" for name in sorted(values)]


def _colours(roles: dict[str, str]) -> dict[str, str]:
    return {f"color-{role}": value for role, value in roles.items()}


def _flat(groups: dict[str, dict[str, str]]) -> dict[str, str]:
    return {f"{g}-{k}": v for g, values in groups.items() for k, v in values.items()}


def _block(selectors: list[str], body: list[str], indent: str = "") -> list[str]:
    head = (",\n" + indent).join(selectors)
    return [f"{indent}{head} {{", *body, f"{indent}}}"]


def render_css(tokens: Tokens, source_text: str) -> str:
    """The token stylesheet, as a string ending in one newline."""
    sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    default = tokens.default_accent
    names = sorted(tokens.accents)
    lines = [
        HEADER.format(
            sha=sha, name=tokens.meta["name"], version=tokens.meta["version"],
            accents=", ".join(names), default=default,
        ),
        "",
    ]

    root = {
        **_flat(tokens.scalars),
        **_colours(tokens.neutrals["light"]),
        **_colours(tokens.accents[default].colours["light"]),
    }
    lines += _block([":root"], _decls(root, "  ") + ["  color-scheme: light;"])
    lines.append("")
    lines += _block(
        [':root[data-theme="light"]'],
        _decls(_colours(tokens.neutrals["light"]), "  ") + ["  color-scheme: light;"],
    )
    for name in names:
        lines.append("")
        lines += _block(
            [f'[data-accent="{name}"]'],
            _decls(_colours(tokens.accents[name].colours["light"]), "  "),
        )

    def dark_blocks(scope: str, indent: str) -> list[str]:
        out = _block(
            [scope],
            _decls(
                {
                    **_colours(tokens.neutrals["dark"]),
                    **_colours(tokens.accents[default].colours["dark"]),
                },
                indent + "  ",
            ) + [f"{indent}  color-scheme: dark;"],
            indent,
        )
        for name in names:
            out.append("")
            out += _block(
                [f'{scope}[data-accent="{name}"]', f'{scope} [data-accent="{name}"]'],
                _decls(_colours(tokens.accents[name].colours["dark"]), indent + "  "),
                indent,
            )
        return out

    lines.append("")
    lines.append("@media (prefers-color-scheme: dark) {")
    lines += dark_blocks(':root:not([data-theme="light"])', "  ")
    lines.append("}")
    lines.append("")
    lines += dark_blocks(':root[data-theme="dark"]', "")

    for density in DENSITIES:
        lines.append("")
        lines += _block(
            [f'[data-density="{density}"]'], _decls(_flat(tokens.density[density]), "  ")
        )

    auto = tokens.auto_density
    lines.append("")
    lines.append(f"@media {auto.media} {{")
    lines += _block([AUTO_DENSITY_SCOPE], _decls(_flat(tokens.density[auto.density]), "    "), "  ")
    lines.append("}")

    lines.append("")
    lines.append("@media (prefers-reduced-motion: reduce) {")
    lines += _block([":root"], _decls(_flat(tokens.reduced_motion), "    "), "  ")
    lines.append("}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- contrast (WCAG 2.x)


def _rgb(hex_colour: str) -> tuple[float, float, float]:
    h = hex_colour.lstrip("#")
    return int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255


def relative_luminance(hex_colour: str) -> float:
    """WCAG 2.x relative luminance of an opaque sRGB hex colour."""

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in _rgb(hex_colour))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: str, b: str) -> float:
    """WCAG 2.x contrast ratio between two opaque hex colours, 1.0 to 21.0."""
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


@dataclass(frozen=True)
class PairResult:
    theme: str
    accent: str
    pair: Pair
    ratio: float

    @property
    def ok(self) -> bool:
        return self.ratio >= self.pair.min


def contrast_results(tokens: Tokens) -> list[PairResult]:
    """Every declared pair, for every theme and every accent set."""
    results = []
    for theme in THEMES:
        for name in sorted(tokens.accents):
            palette = tokens.palette(theme, name)
            for pair in tokens.pairs:
                ratio = contrast_ratio(palette[pair.fg], palette[pair.bg])
                results.append(PairResult(theme, name, pair, ratio))
    return results


def hue_deg(hex_colour: str) -> float:
    h, _, _ = colorsys.rgb_to_hls(*_rgb(hex_colour))
    return h * 360


def chroma(hex_colour: str) -> float:
    rgb = _rgb(hex_colour)
    return max(rgb) - min(rgb)


def hue_gap(a: str, b: str) -> float:
    d = abs(hue_deg(a) - hue_deg(b)) % 360
    return min(d, 360 - d)


def distinctness_failures(tokens: Tokens) -> list[str]:
    """Where the `ai` hue sits within the declared gap of the accent or a status hue.

    A colour whose chroma is under the floor (a neutral such as slate) has no meaningful hue
    and is skipped as a comparison target.
    """
    rule = tokens.distinctness
    failures = []
    for theme in THEMES:
        for name in sorted(tokens.accents):
            palette = tokens.palette(theme, name)
            ai = palette["ai"]
            for role in rule.against:
                other = palette[role]
                if chroma(other) < rule.chroma_floor:
                    continue
                gap = hue_gap(ai, other)
                if gap < rule.min_hue_gap_deg:
                    failures.append(
                        f"{theme}/{name}: ai {ai} is {gap:.0f} deg from {role} {other} "
                        f"(min {rule.min_hue_gap_deg:g})"
                    )
    return failures


def report_contrast(tokens: Tokens) -> int:
    results = contrast_results(tokens)
    for r in results:
        verdict = "ok  " if r.ok else "FAIL"
        print(
            f"{verdict} {r.theme:<5} {r.accent:<8} {r.pair.fg + '/' + r.pair.bg:<24} "
            f"{r.ratio:6.2f} (min {r.pair.min:g})"
        )
    print()
    for name in sorted(tokens.accents):
        worst = min((r for r in results if r.accent == name), key=lambda r: r.ratio - r.pair.min)
        print(
            f"lowest margin {name:<8} {worst.theme:<5} {worst.pair.fg}/{worst.pair.bg} "
            f"{worst.ratio:.2f} (min {worst.pair.min:g})"
        )
    failed = [r for r in results if not r.ok]
    distinct = distinctness_failures(tokens)
    for line in distinct:
        print(f"FAIL ai distinctness {line}")
    print(
        f"{len(results)} contrast checks, {len(failed)} failed; "
        f"ai distinctness: {len(distinct)} failed"
    )
    return 1 if failed or distinct else 0


# ---------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the ui-kit token stylesheet.")
    parser.add_argument("--check", action="store_true", help="exit 1 if the output is stale")
    parser.add_argument(
        "--contrast", action="store_true",
        help="print every contrast pair for every theme and accent; exit 1 on any failure",
    )
    parser.add_argument("--tokens", type=Path, default=None, help="tokens file (default: kit)")
    parser.add_argument("--out", type=Path, default=None, help="output CSS (default: kit dist)")
    args = parser.parse_args(argv)

    source_path: Path = args.tokens or TOKENS
    out: Path = args.out or OUTPUT
    try:
        source = read_source(source_path)
        tokens = parse_tokens(json.loads(source))
    except (TokenError, json.JSONDecodeError) as exc:
        print(f"{source_path}: {exc}", file=sys.stderr)
        return 2

    if args.contrast:
        return report_contrast(tokens)
    css = render_css(tokens, source)
    if args.check:
        current = out.read_bytes().decode("utf-8") if out.exists() else None
        if current != css:
            print(f"{out} is stale; run ui-kit/tools/build_tokens.py")
            return 1
        print(f"{out} matches the tokens")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(css, encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
