#!/usr/bin/env python3
"""Generate the house family's token stylesheet from its tokens file — `REQ-036` R01-R05.

`templates/styles/house-tokens.json` is the only place the house style's values live: colour
roles in light and dark, fonts, sizes, spacing, rules and radius, transcribed from the round-two
gallery the owner approved on 2026-09-30. This tool turns that file into
`templates/styles/house.css`, which no one edits by hand. The component rules in
`templates/styles/house-components.css` refer to the tokens through `var()` only and carry no
value of their own.

The generated sheet has five blocks, always in this order:

    :root { stacks, fonts, scale, light colours }        the house style, light mode
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) { dark colours }   dark mode follows the viewer
    }
    :root[data-theme="dark"] { dark colours }            and an explicit override
    :root[data-variant="swiss"] { type and spacing }     the two variants, which set
    :root[data-variant="mono"]  { type and spacing }     no colour (R03)

Dark mode redefines colour tokens and `color-scheme` only (R04). A page selects a variant with
`data-variant` and a mode with `data-theme` on its `<html>` element; with neither, it renders the
house style following the viewer's colour scheme.

Determinism (R01). The output is a pure function of the tokens file: keys are emitted in the
file's own order, no clock or environment is read, and the same file always yields the same bytes.

    uv run python tools/generate_house_css.py                      # rewrite house.css
    uv run python tools/generate_house_css.py --check              # exit 1 if house.css is stale
    uv run python tools/generate_house_css.py --specimen out.html  # write a specimen page
    uv run python tools/generate_house_css.py --specimen out.html --variant mono --theme dark
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STYLES = ROOT / "templates" / "styles"
HTML = ROOT / "templates" / "html"
TOKENS = STYLES / "house-tokens.json"
OUTPUT = STYLES / "house.css"
COMPONENTS_CSS = STYLES / "house-components.css"
PAGE = HTML / "house-page.html"
COMPONENTS_HTML = HTML / "house-components.html"

VARIANTS = ("house", "swiss", "mono")
THEMES = ("auto", "light", "dark")

HEADER = """\
/*
  House family — token stylesheet. GENERATED: do not edit by hand.

  Source: templates/styles/house-tokens.json, regenerated with
  `uv run python tools/generate_house_css.py`. Edit the tokens file and regenerate;
  tests fail when this file and the tokens disagree (REQ-036 R01).

  Provenance: {source}
  {url} (artifact version {artifact_version}).

  Usage: inline this file, then templates/styles/house-components.css, into
  templates/html/house-page.html's {{{{INLINE_STYLES}}}}. Select a variant with
  data-variant="swiss" or data-variant="mono" on <html>, and force a mode with
  data-theme="light" or data-theme="dark"; without data-theme the page follows
  prefers-color-scheme. Fonts load from Google Fonts; every font token ends in a
  system stack, so a page whose font request fails still renders.
*/
"""


def load_tokens(path: Path = TOKENS) -> dict[str, Any]:
    """The parsed tokens file."""
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _declarations(groups: list[dict[str, str]], indent: str) -> list[str]:
    return [f"{indent}--{name}: {value};" for group in groups for name, value in group.items()]


def render_css(tokens: dict[str, Any]) -> str:
    """The token stylesheet for `tokens`, as a string ending in one newline."""
    provenance = tokens["provenance"]
    colors = tokens["colors"]
    lines = [HEADER.format(**provenance).rstrip("\n"), ""]
    lines.append(f'@import url("{tokens["fonts_url"]}");')
    lines.append("")
    lines.append(":root {")
    lines += _declarations(
        [tokens["stacks"], tokens["fonts"], tokens["scale"], colors["light"]], "  "
    )
    lines.append("  color-scheme: light;")
    lines.append("}")
    lines.append("")
    lines.append("@media (prefers-color-scheme: dark) {")
    lines.append('  :root:not([data-theme="light"]) {')
    lines += _declarations([colors["dark"]], "    ")
    lines.append("    color-scheme: dark;")
    lines.append("  }")
    lines.append("}")
    lines.append("")
    lines.append(':root[data-theme="dark"] {')
    lines += _declarations([colors["dark"]], "  ")
    lines.append("  color-scheme: dark;")
    lines.append("}")
    for name, overrides in tokens["variants"].items():
        lines.append("")
        lines.append(f':root[data-variant="{name}"] {{')
        lines += _declarations([overrides], "  ")
        lines.append("}")
    return "\n".join(lines) + "\n"


def fill(template: str, values: dict[str, str]) -> str:
    """Replace every `{{NAME}}` in `template`; refuse an unknown or unfilled name.

    Both checks read the template, not the output, because a filled value may itself contain
    `{{...}}` text — the inlined stylesheets' comments name `{{INLINE_STYLES}}`.
    """
    wanted = set(re.findall(r"\{\{([A-Z_]+)\}\}", template))
    unknown = sorted(set(values) - wanted)
    if unknown:
        raise ValueError(f"template has no {', '.join('{{' + n + '}}' for n in unknown)}")
    missing = sorted(wanted - set(values))
    if missing:
        raise ValueError(f"unfilled {', '.join('{{' + n + '}}' for n in missing)}")
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda match: values[match.group(1)], template)


def _strip_leading_comment(text: str) -> str:
    """A template without its documentation comment, which is for authors, not readers."""
    stripped = text.lstrip()
    if stripped.startswith("<!--"):
        stripped = stripped[stripped.index("-->") + 3 :].lstrip()
    return stripped


def render_specimen(tokens: dict[str, Any], variant: str = "house", theme: str = "auto") -> str:
    """A self-contained page showing every house component, for review and browser checks."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; choose one of {VARIANTS}")
    if theme not in THEMES:
        raise ValueError(f"unknown theme {theme!r}; choose one of {THEMES}")
    styles = render_css(tokens) + "\n" + COMPONENTS_CSS.read_text(encoding="utf-8")
    root_attrs = ""
    if variant != "house":
        root_attrs += f' data-variant="{variant}"'
    if theme != "auto":
        root_attrs += f' data-theme="{theme}"'
    body = _strip_leading_comment(COMPONENTS_HTML.read_text(encoding="utf-8"))
    return fill(
        _strip_leading_comment(PAGE.read_text(encoding="utf-8")),
        {
            "ROOT_ATTRS": root_attrs,
            "PAGE_TITLE": "House family specimen",
            "INLINE_STYLES": styles,
            "KICKER": "templates/html/house-components.html",
            "HEADING": "House family specimen",
            "LEDE": f"Every component in the family, variant {variant}, mode {theme}.",
            "META": "<span>Generated by tools/generate_house_css.py --specimen</span>",
            "BODY": body,
            "FOOTER": "Generated from templates/styles/house-tokens.json.",
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the house family's token stylesheet.")
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if house.css differs from the tokens"
    )
    parser.add_argument(
        "--specimen", type=Path, metavar="PATH", help="write a specimen page to PATH instead"
    )
    parser.add_argument("--variant", default="house", choices=VARIANTS, help="specimen variant")
    parser.add_argument("--theme", default="auto", choices=THEMES, help="specimen mode")
    args = parser.parse_args(argv)

    tokens = load_tokens()
    if args.specimen:
        args.specimen.write_text(render_specimen(tokens, args.variant, args.theme), "utf-8")
        print(f"wrote {args.specimen}")
        return 0
    css = render_css(tokens)
    current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None
    if args.check:
        if current != css:
            print(f"{OUTPUT.relative_to(ROOT)} is stale; run tools/generate_house_css.py")
            return 1
        print(f"{OUTPUT.relative_to(ROOT)} matches the tokens")
        return 0
    OUTPUT.write_text(css, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
