#!/usr/bin/env python3
"""Generate the accent theme sheet, `ui-kit/gallery/theme-sheet.html`.

The page exists so the owner can choose the product's brand accent. For every accent set in
`tokens/tokens.json` it shows the same small product view in the light and the dark theme, side
by side, with the accent's raw colours, its lowest accent-dependent contrast ratios and how close
its hue sits to each status hue.

Why every sample is an iframe: the kit's dark theme is keyed on `:root[data-theme="dark"]`, and
`data-theme` belongs on `<html>` only, so a dark sample cannot be nested inside a light page. Each
sample is therefore its own document in an `<iframe srcdoc>` whose `<html>` carries
`data-theme` and `data-accent`. Light samples go through the same path as dark ones, so both
render from identical markup under identical rules, and neither depends on the viewer's
`prefers-color-scheme`. Each iframe document inlines `dist/ui.css`; the page makes no request.

The contrast and hue figures come from `build_tokens.py` (`load_tokens`, `contrast_ratio`,
`hue_gap`, `chroma`); this file does not repeat that maths.

Determinism: no clock or environment is read, accents are ordered default first and then by
name, and output is LF-terminated UTF-8.

    uv run python ui-kit/tools/build_theme_sheet.py            # rewrite gallery/theme-sheet.html
    uv run python ui-kit/tools/build_theme_sheet.py --check    # exit 1 if it is stale
"""

from __future__ import annotations

import argparse
import html
import sys
from dataclasses import dataclass
from pathlib import Path

import build_tokens as tk

esc = html.escape

KIT = Path(__file__).resolve().parent.parent
CSS = KIT / "dist" / "ui.css"
OUTPUT = KIT / "gallery" / "theme-sheet.html"
STATUS_ROLES = ("ok", "warn", "info", "err")
STATUS_NAMES = {"ok": "ok", "warn": "warn", "info": "info", "err": "err"}
THEME_LABEL = {"light": "Light", "dark": "Dark"}
SAMPLE_HEIGHT_PX = 640  # iframe height when script is off; script sizes it to the content

# ---------------------------------------------------------------- figures


@dataclass(frozen=True)
class Worst:
    """The lowest-ratio contrast pair that involves an accent role, for one theme."""

    ratio: float
    fg: str
    bg: str
    minimum: float
    use: str


@dataclass(frozen=True)
class HueNote:
    """How close the accent's hue sits to the nearest status hue, for one theme."""

    neutral: bool  # accent chroma under the floor: its hue is not meaningful
    chroma: float
    nearest: str  # status role
    gap: float  # degrees
    near: tuple[tuple[str, float], ...]  # every status role under the threshold, with its gap


def worst_accent_pair(tokens: tk.Tokens, theme: str, accent: str) -> Worst:
    """The declared pair with the lowest ratio among pairs that use an accent role."""
    palette = tokens.palette(theme, accent)
    rows = [
        Worst(tk.contrast_ratio(palette[p.fg], palette[p.bg]), p.fg, p.bg, p.min, p.use)
        for p in tokens.pairs
        if p.fg in tk.ACCENT_ROLES or p.bg in tk.ACCENT_ROLES
    ]
    return min(rows, key=lambda w: (w.ratio, w.fg, w.bg))


def hue_note(tokens: tk.Tokens, theme: str, accent: str) -> HueNote:
    palette = tokens.palette(theme, accent)
    colour = palette["accent"]
    rule = tokens.distinctness
    gaps = [
        (role, tk.hue_gap(colour, palette[role]))
        for role in STATUS_ROLES
        if tk.chroma(palette[role]) >= rule.chroma_floor
    ]
    nearest, gap = min(gaps, key=lambda g: (g[1], g[0]))
    near = tuple(g for g in sorted(gaps, key=lambda g: (g[1], g[0])) if g[1] < rule.min_hue_gap_deg)
    c = tk.chroma(colour)
    return HueNote(c < rule.chroma_floor, c, nearest, gap, near)


def ordered_accents(tokens: tk.Tokens) -> list[str]:
    rest = sorted(n for n in tokens.accents if n != tokens.default_accent)
    return [tokens.default_accent, *rest]


def fmt_ratio(r: float) -> str:
    return f"{r:.2f}:1"


def hue_sentence(tokens: tk.Tokens, note: HueNote, theme: str, accent: str) -> str:
    palette = tokens.palette(theme, accent)
    threshold = f"{tokens.distinctness.min_hue_gap_deg:g}°"
    if note.neutral:
        return (
            f"Low chroma ({note.chroma:.2f}, under the {tokens.distinctness.chroma_floor:g} "
            f"floor): reads as a neutral, so it competes with no status hue."
        )
    if note.near:
        parts = ", ".join(
            f"{STATUS_NAMES[role]} {palette[role]} ({gap:.1f}°)" for role, gap in note.near
        )
        return f"Within {threshold} of a status hue: {parts}. Status and action may be confused."
    return (
        f"Nearest status hue is {STATUS_NAMES[note.nearest]} {palette[note.nearest]}, "
        f"{note.gap:.1f}° away; clear of the {threshold} threshold."
    )


# ---------------------------------------------------------------- sample document

SAMPLE_CSS = """
html, body { margin: 0; }
body {
  background: var(--ui-color-bg);
  color: var(--ui-color-text);
  font-family: var(--ui-font-sans);
  font-size: var(--ui-fs-md);
  line-height: var(--ui-lh-ui);
  padding: var(--ui-space-5);
}
.ts-stack { display: grid; gap: var(--ui-space-4); }
.ts-row { display: flex; flex-wrap: wrap; align-items: center; gap: var(--ui-space-3); }
.ts-swatches {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(7.5rem, 1fr));
  gap: var(--ui-space-3);
  margin: 0;
  padding: 0;
  list-style: none;
}
.ts-swatch {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: var(--ui-space-3);
  font-size: var(--ui-fs-xs);
}
.ts-chip {
  width: var(--ui-ctl-md);
  height: var(--ui-ctl-md);
  border-radius: var(--ui-radius-sm);
  border: 1px solid var(--ui-color-line);
}
.ts-swatch code { font-family: var(--ui-font-mono); color: var(--ui-color-muted); }
.ts-swatch b { display: block; font-weight: var(--ui-fw-semibold); }
.ts-heading {
  margin: 0;
  font-size: var(--ui-fs-xs);
  font-weight: var(--ui-fw-semibold);
  color: var(--ui-color-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
"""


def sample_body(tokens: tk.Tokens, theme: str, accent: str) -> str:
    """The mini product view and swatches, written against the kit class contract."""
    palette = tokens.palette(theme, accent)
    swatches = "\n".join(
        f'<li class="ts-swatch"><span class="ts-chip" '
        f'style="background: var(--ui-color-{esc(role)})">'
        f"</span><span><b>{esc(role)}</b><code>{esc(palette[role])}</code></span></li>"
        for role in tk.ACCENT_ROLES
    )
    return f"""<div class="ts-stack">
<section class="ui-panel" data-variant="standard" aria-labelledby="sample-title">
<div class="ui-panel__header">
<div class="ui-panel__identity"><h2 class="ui-panel__title" id="sample-title">Ingest run 42</h2>
</div>
<div class="ui-panel__controls" role="toolbar" aria-label="Run actions">
<button type="button" class="ui-button ui-button--ghost ui-button--sm">Refresh</button>
<button type="button" class="ui-button ui-button--secondary ui-button--sm"
 data-focus-visible>Export CSV</button>
<button type="button" class="ui-button ui-button--primary ui-button--sm">Run triage</button>
</div>
</div>
<div class="ui-tabs">
<div class="ui-tabs__list" role="tablist" aria-label="Run views">
<button type="button" class="ui-tabs__tab" role="tab" aria-selected="true">Findings</button>
<button type="button" class="ui-tabs__tab" role="tab" aria-selected="false">Sources</button>
<button type="button" class="ui-tabs__tab" role="tab" aria-selected="false">Log</button>
</div>
</div>
<div class="ui-panel__body" data-body="document">
<div class="ts-stack">
<p>12 findings from 3 files. <a href="#sample-title">View the source files</a></p>
<div class="ts-row">
<span class="ui-pill" data-status="ok"><span class="ui-pill__dot"></span>Passed</span>
<span class="ui-pill" data-status="warn"><span class="ui-pill__dot"></span>Needs review</span>
<span class="ui-pill" data-status="info"><span class="ui-pill__dot"></span>Queued</span>
<span class="ui-pill" data-status="err"><span class="ui-pill__dot"></span>Failed</span>
<span class="ui-pill" data-status="ai"><span class="ui-pill__dot"></span>AI draft</span>
</div>
<div class="ts-row">
<span class="ui-chip">Status: open<button type="button" class="ui-chip__remove"
 aria-label="Remove filter: Status: open">×</button>
</span>
</div>
<article class="ui-card ui-card--ai">
<p class="ui-card__kicker">AI draft</p>
<h3 class="ui-card__title">Summary of 12 findings</h3>
<p class="ui-card__body">Three findings repeat across files.
Two need a decision before the run can close.</p>
<p class="ui-card__meta">Source: run 42, 3 files. Drafted 09:12. Check before use.</p>
</article>
<div class="ui-table-wrap">
<table class="ui-table">
<thead><tr><th scope="col">ID</th><th scope="col">Finding</th><th scope="col">Files</th></tr>
</thead>
<tbody>
<tr><td class="ui-table__id">F-07</td><td>Duplicate owner field</td><td class="ui-table__num">2</td>
</tr>
<tr data-selected><td class="ui-table__id">F-08</td><td>Missing due date</td>
<td class="ui-table__num">3</td></tr>
<tr><td class="ui-table__id">F-09</td><td>Unknown status value</td><td class="ui-table__num">1</td>
</tr>
</tbody>
</table>
</div>
</div>
</div>
</section>
<p class="ts-heading">Accent roles</p>
<ul class="ts-swatches">
{swatches}
</ul>
</div>"""


def sample_document(tokens: tk.Tokens, css: str, theme: str, accent: str) -> str:
    label = tokens.accents[accent].label
    return (
        f'<!doctype html><html lang="en" data-theme="{esc(theme)}" '
        f'data-accent="{esc(accent)}">'
        f'<head><meta charset="utf-8"><title>{esc(label)}, {esc(theme)}</title>'
        f"<style>\n{css}\n/* theme sheet sample layout */{SAMPLE_CSS}</style></head>"
        f"<body inert>\n{sample_body(tokens, theme, accent)}\n</body></html>"
    )


# ---------------------------------------------------------------- page

PAGE_CSS = """
body {
  margin: 0;
  background: var(--ui-color-bg);
  color: var(--ui-color-text);
  font-family: var(--ui-font-sans);
  font-size: var(--ui-fs-lg);
  line-height: var(--ui-lh-ui);
}
.ts-page { max-width: 1440px; margin: 0 auto; padding: var(--ui-space-7) clamp(16px, 3vw, 40px); }
.ts-page h1 {
  font-size: var(--ui-fs-3xl);
  line-height: var(--ui-lh-tight);
  margin: 0 0 var(--ui-space-4);
}
.ts-page h2 { font-size: var(--ui-fs-2xl); line-height: var(--ui-lh-tight); margin: 0; }
.ts-lede { max-width: 72ch; margin: 0 0 var(--ui-space-4); }
.ts-muted { color: var(--ui-color-muted); }
.ts-compare-wrap { overflow-x: auto; margin: var(--ui-space-6) 0; }
.ts-compare { border-collapse: collapse; font-size: var(--ui-fs-md); min-width: 100%; }
.ts-compare th, .ts-compare td {
  text-align: left;
  padding: var(--ui-space-3) var(--ui-space-4);
  border-bottom: 1px solid var(--ui-color-line);
  vertical-align: top;
}
.ts-compare caption {
  caption-side: bottom;
  text-align: left;
  padding-top: var(--ui-space-3);
  font-size: var(--ui-fs-sm);
}
.ts-compare th[scope="col"] { color: var(--ui-color-muted); font-weight: var(--ui-fw-semibold); }
.ts-compare code, .ts-notes code { font-family: var(--ui-font-mono); font-size: var(--ui-fs-sm); }
.ts-dot {
  display: inline-block;
  width: 0.9em;
  height: 0.9em;
  border-radius: var(--ui-radius-pill);
  border: 1px solid var(--ui-color-line-strong);
  vertical-align: -0.1em;
  margin-right: var(--ui-space-2);
}
.ts-flag { color: var(--ui-color-warn); font-weight: var(--ui-fw-semibold); }
.ts-controls {
  display: flex;
  gap: var(--ui-space-3);
  align-items: center;
  margin: var(--ui-space-5) 0;
}
.ts-controls button {
  font: inherit;
  font-size: var(--ui-fs-md);
  min-height: var(--ui-ctl-md);
  padding: 0 var(--ui-space-4);
  border-radius: var(--ui-radius-md);
  border: 1px solid var(--ui-color-line-strong);
  background: var(--ui-color-surface);
  color: var(--ui-color-text);
  cursor: pointer;
}
.ts-controls button[aria-pressed="true"] {
  background: var(--ui-color-text);
  color: var(--ui-color-bg);
}
.ts-controls button:focus-visible {
  outline: var(--ui-focus-width) solid var(--ui-color-focus);
  outline-offset: var(--ui-focus-offset);
}
.ts-accent { margin: var(--ui-space-8) 0 0; }
.ts-accent__head {
  display: flex;
  flex-wrap: wrap;
  gap: var(--ui-space-3) var(--ui-space-5);
  align-items: baseline;
  margin-bottom: var(--ui-space-4);
}
.ts-accent__head p { margin: 0; }
.ts-pair {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--ui-space-5);
}
.ts-sheet[data-show="light"] .ts-pair, .ts-sheet[data-show="dark"] .ts-pair {
  grid-template-columns: minmax(0, 1fr);
}
.ts-sheet[data-show="light"] [data-theme-tile="dark"],
.ts-sheet[data-show="dark"] [data-theme-tile="light"] { display: none; }
.ts-tile { margin: 0; }
.ts-tile iframe {
  display: block;
  width: 100%;
  height: %HEIGHT%px;
  border: 1px solid var(--ui-color-line-strong);
  border-radius: var(--ui-radius-lg);
  background: var(--ui-color-surface);
}
.ts-tile figcaption { font-size: var(--ui-fs-md); margin-top: var(--ui-space-3); }
.ts-notes { margin: 0; padding-left: 1.2em; }
.ts-notes li + li { margin-top: var(--ui-space-2); }
@media (max-width: 900px) { .ts-pair { grid-template-columns: minmax(0, 1fr); } }
""".replace("%HEIGHT%", str(SAMPLE_HEIGHT_PX))

PAGE_SCRIPT = """
(function () {
  var sheet = document.querySelector('.ts-sheet');
  var controls = document.querySelector('.ts-controls');
  if (!sheet || !controls) return;
  controls.hidden = false;
  var buttons = controls.querySelectorAll('button[data-show]');
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      sheet.setAttribute('data-show', b.getAttribute('data-show'));
      buttons.forEach(function (o) { o.setAttribute('aria-pressed', String(o === b)); });
    });
  });
  function fit(f) {
    try {
      var d = f.contentDocument;
      var stack = d && d.body && d.body.firstElementChild;
      if (!stack) return;
      var pad = parseFloat(d.defaultView.getComputedStyle(d.body).paddingBottom) || 0;
      f.style.height = Math.ceil(stack.getBoundingClientRect().bottom + pad) + 2 + 'px';
    } catch (e) { /* keep the fixed height */ }
  }
  document.querySelectorAll('.ts-tile iframe').forEach(function (f) {
    f.addEventListener('load', function () { fit(f); });
    fit(f);
  });
})();
"""


def swatch_dot(hex_colour: str) -> str:
    return (
        f'<span class="ts-dot" style="background-color: {esc(hex_colour)}" '
        'aria-hidden="true"></span>'
    )


def comparison_table(tokens: tk.Tokens) -> str:
    rows = []
    for name in ordered_accents(tokens):
        accent = tokens.accents[name]
        light, dark = accent.colours["light"]["accent"], accent.colours["dark"]["accent"]
        worst = {t: worst_accent_pair(tokens, t, name) for t in tk.THEMES}
        low_theme = min(tk.THEMES, key=lambda t: (worst[t].ratio, t))
        low = worst[low_theme]
        hue_cells = []
        for theme in tk.THEMES:
            note = hue_note(tokens, theme, name)
            if note.neutral:
                text = "neutral (low chroma)"
            else:
                text = esc(f"{STATUS_NAMES[note.nearest]}, {note.gap:.1f}°")
                if note.near:
                    text = f'<span class="ts-flag">{text}, under threshold</span>'
            hue_cells.append(f"{THEME_LABEL[theme]}: {text}")
        default = " <em>(provisional default)</em>" if name == tokens.default_accent else ""
        rows.append(
            "<tr>"
            f'<th scope="row"><a href="#accent-{esc(name)}">{esc(accent.label)}</a>'
            f"{default}</th>"
            f"<td>{swatch_dot(light)}<code>{esc(light)}</code></td>"
            f"<td>{swatch_dot(dark)}<code>{esc(dark)}</code></td>"
            f"<td>{fmt_ratio(low.ratio)} <span class=\"ts-muted\">"
            f"{THEME_LABEL[low_theme].lower()}, "
            f"{esc(low.fg)} on {esc(low.bg)}</span></td>"
            f"<td>{'<br>'.join(hue_cells)}</td>"
            "</tr>"
        )
    return (
        '<div class="ts-compare-wrap"><table class="ts-compare">'
        "<caption class=\"ts-muted\">Minimum ratio is the lowest across both themes among "
        "the declared contrast pairs that use an accent role. Hue gap is measured from the "
        "accent to the status hue in the same theme.</caption>"
        "<thead><tr><th scope=\"col\">Accent</th><th scope=\"col\">Accent, light</th>"
        "<th scope=\"col\">Accent, dark</th><th scope=\"col\">Lowest contrast</th>"
        "<th scope=\"col\">Nearest status hue and gap</th></tr></thead>"
        f"<tbody>\n{chr(10).join(rows)}\n</tbody></table></div>"
    )


def accent_section(tokens: tk.Tokens, css: str, name: str) -> str:
    accent = tokens.accents[name]
    tiles = []
    for theme in tk.THEMES:
        worst = worst_accent_pair(tokens, theme, name)
        note = hue_note(tokens, theme, name)
        doc = sample_document(tokens, css, theme, name)
        title = f"{accent.label} accent, {theme} theme sample"
        tiles.append(
            f'<figure class="ts-tile" data-theme-tile="{esc(theme)}">'
            f'<iframe title="{esc(title)}" '
            f'srcdoc="{esc(doc, quote=True)}"></iframe>'
            f"<figcaption><ul class=\"ts-notes\">"
            f"<li><strong>{THEME_LABEL[theme]}.</strong> Lowest accent contrast "
            f"{fmt_ratio(worst.ratio)}: {esc(worst.fg)} on {esc(worst.bg)} "
            f"({esc(worst.use)}; "
            f"minimum {worst.minimum:g}:1).</li>"
            f"<li>{esc(hue_sentence(tokens, note, theme, name))}</li>"
            "</ul></figcaption></figure>"
        )
    default = (
        '<p class="ts-flag">Provisional default. Not a decision.</p>'
        if name == tokens.default_accent
        else ""
    )
    blurb = f"<p class=\"ts-muted\">{esc(accent.note)}</p>" if accent.note else ""
    safe = esc(name)
    return (
        f'<section class="ts-accent" id="accent-{safe}" aria-labelledby="accent-{safe}-title">'
        f'<div class="ts-accent__head"><h2 id="accent-{safe}-title">{esc(accent.label)}'
        f'</h2><p class="ts-muted"><code>data-accent="{safe}"</code></p>{default}{blurb}</div>'
        f'<div class="ts-pair">{"".join(tiles)}</div></section>'
    )


def render(tokens: tk.Tokens, css: str) -> str:
    css = css.replace("\r\n", "\n").rstrip("\n")
    count = len(tokens.accents)
    default = tokens.accents[tokens.default_accent].label
    sections = "\n".join(accent_section(tokens, css, n) for n in ordered_accents(tokens))
    return f"""<!doctype html>
<!-- GENERATED by ui-kit/tools/build_theme_sheet.py from tokens/tokens.json and
     dist/ui.css. Do not edit by hand. -->
<html lang="en" data-accent="slate">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Accent theme sheet</title>
<style>
{css}
/* theme sheet page layout */{PAGE_CSS}</style>
</head>
<body>
<main class="ts-page ts-sheet" data-show="both">
<h1>Choose the brand accent</h1>
<p class="ts-lede">This page shows each of the {count} candidate accent colours on the same small
product view, in the light and the dark theme side by side. Under each view are its lowest contrast
ratio and how close it sits to a status colour, so a choice can weigh appearance against those
limits. The current default, {esc(default)}, is provisional; nothing here has
been decided.</p>
<p class="ts-lede ts-muted">The page itself uses the neutral slate accent so its own links do not
favour a candidate. Each sample is a separate document with its own theme, so it looks the same
whichever theme your system uses.</p>
{comparison_table(tokens)}
<div class="ts-controls" role="group" aria-label="Themes shown" hidden>
<span class="ts-muted">Show</span>
<button type="button" data-show="both" aria-pressed="true">Light and dark</button>
<button type="button" data-show="light" aria-pressed="false">Light only</button>
<button type="button" data-show="dark" aria-pressed="false">Dark only</button>
</div>
{sections}
</main>
<script>{PAGE_SCRIPT}</script>
</body>
</html>
"""


# ---------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the ui-kit accent theme sheet.")
    parser.add_argument("--check", action="store_true", help="exit 1 if the output is stale")
    parser.add_argument("--tokens", type=Path, default=None, help="tokens file (default: kit)")
    parser.add_argument("--css", type=Path, default=None, help="bundle (default: dist/ui.css)")
    parser.add_argument("--out", type=Path, default=None, help="output (default: gallery)")
    args = parser.parse_args(argv)

    tokens_path: Path = args.tokens or tk.TOKENS
    css_path: Path = args.css or CSS
    out: Path = args.out or OUTPUT
    try:
        tokens = tk.load_tokens(tokens_path)
    except (tk.TokenError, ValueError) as exc:
        print(f"{tokens_path}: {exc}", file=sys.stderr)
        return 2
    if not css_path.is_file():
        print(f"{css_path} is missing; run ui-kit/tools/build_css.py", file=sys.stderr)
        return 2
    page = render(tokens, css_path.read_text(encoding="utf-8"))
    if args.check:
        current = out.read_bytes().decode("utf-8") if out.is_file() else None
        if current != page:
            print(f"{out} is stale; run ui-kit/tools/build_theme_sheet.py")
            return 1
        print(f"{out} matches its inputs")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
