"""The house family's tokens, generated stylesheet and templates — REQ-036 R01-R06.

`GALLERY` below is the transcription of the round-two house-style gallery the owner approved on
2026-09-30. It was extracted mechanically from the artifact's published `index.html` (the
`.spec`, `.spec[data-mode="dark"]`, `.spec[data-var="swiss"]` and `.spec[data-var="mono"]`
custom properties, the system stacks, the Google Fonts link and the pill radius), not typed from
memory. It is the record of what was approved: `templates/styles/house-tokens.json` must match
it, so a change to an approved value has to change this fixture in the same diff.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import generate_house_css as gen  # noqa: E402

STYLES = ROOT / "templates" / "styles"
HTML = ROOT / "templates" / "html"

GALLERY_SOURCE = {
    "url": "https://claude.ai/artifact/D15aCx8HqwfVmKmKtKDKFi",
    "artifact_version": "1790623455-daec",
    "file_sha256": "32c775b4112c378ef2e86503de4303b1de51d0ae5577a82210b68a588f4c7a24",
}

GALLERY = {
    "fonts_url": (
        "https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700;800"
        "&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800"
        "&family=JetBrains+Mono:wght@400;600;700"
        "&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=swap"
    ),
    "sys": {
        "sys-sans": (
            'ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
        ),
        "sys-serif": 'Georgia, "Times New Roman", serif',
        "sys-mono": 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace',
    },
    "house": {
        "display": '"Bricolage Grotesque", var(--sys-sans)',
        "body": '"Literata", var(--sys-serif)',
        "label": '"Bricolage Grotesque", var(--sys-sans)',
        "mono": '"JetBrains Mono", var(--sys-mono)',
        "fs": "17px", "lh": "1.62", "h1": "3.4", "h2": "1.6", "htrack": "-.04em", "hw": "800",
        "pad": "22px", "gap": "24px", "rule": "1px", "label-track": ".1em", "cell": "10px 14px",
        "bg": "#ffffff", "surface": "#f6f1ea", "line": "#ddd6cd", "strong": "#1a1a1a",
        "text": "#141414", "muted": "#5a5a5a", "accent": "#c8205f", "on-accent": "#ffffff",
        "accent-2": "#0f7b6c", "ok": "#17693a", "ok-bg": "#e3f4e8", "warn": "#8a5a00",
        "warn-bg": "#fdf1d4", "info": "#1d5fa8", "info-bg": "#e4eefb", "err": "#b3162f",
        "err-bg": "#fbe5e8", "soft": "color-mix(in srgb, var(--accent) 10%, var(--bg))",
    },
    "dark": {
        "bg": "#121015", "surface": "#1d1a22", "line": "#39333f", "strong": "#e9e4ee",
        "text": "#f1edf4", "muted": "#aaa3b3", "accent": "#ff5c9a", "on-accent": "#121015",
        "accent-2": "#3cc9b4", "ok": "#5fd68d", "ok-bg": "#16291e", "warn": "#f0b74a",
        "warn-bg": "#2d2412", "info": "#7fb2f0", "info-bg": "#172335", "err": "#ff7a8c",
        "err-bg": "#341820",
    },
    "swiss": {
        "body": '"Archivo", var(--sys-sans)', "label": '"Archivo", var(--sys-sans)',
        "fs": "15.5px", "lh": "1.55", "h1": "3.1", "h2": "1.5", "pad": "18px", "gap": "20px",
        "rule": "2px", "label-track": ".16em", "cell": "9px 12px",
    },
    "mono": {
        "body": '"JetBrains Mono", var(--sys-mono)', "label": '"JetBrains Mono", var(--sys-mono)',
        "fs": "14px", "lh": "1.62", "h1": "2.5", "h2": "1.35", "htrack": "-.03em",
        "pad": "16px", "gap": "18px", "label-track": ".06em", "cell": "8px 12px",
    },
    "radius-pill": "999px",
}

COLOUR_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")
GENERIC_FAMILIES = {"serif", "sans-serif", "monospace", "system-ui", "cursive", "fantasy"}


@pytest.fixture(scope="module")
def tokens() -> dict:
    return gen.load_tokens()


@pytest.fixture(scope="module")
def css() -> str:
    return (STYLES / "house.css").read_text(encoding="utf-8")


def _blocks(css: str) -> dict[str, dict[str, str]]:
    """Each innermost rule's selector mapped to its declarations, comments removed."""
    text = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    blocks: dict[str, dict[str, str]] = {}
    for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", text):
        decls = dict(
            (name.strip(), value.strip())
            for name, value in re.findall(r"([\w-]+)\s*:\s*([^;]+);", body)
        )
        blocks[selector.strip()] = decls
    return blocks


def _colour_names(tokens: dict) -> set[str]:
    return {f"--{name}" for mode in tokens["colors"].values() for name in mode}


# ---- R01: one tokens file, a generated stylesheet, no colour literal elsewhere ----


def test_committed_css_matches_regeneration(tokens: dict, css: str) -> None:
    assert gen.render_css(tokens) == css


def test_regenerating_twice_is_byte_identical(tokens: dict) -> None:
    assert gen.render_css(tokens) == gen.render_css(gen.load_tokens())


def test_check_mode_passes_on_the_committed_file() -> None:
    result = subprocess.run(
        [sys.executable, "tools/generate_house_css.py", "--check"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_check_mode_fails_on_a_stale_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stale = tmp_path / "house.css"
    stale.write_text("/* hand edit */\n", encoding="utf-8")
    monkeypatch.setattr(gen, "OUTPUT", stale)
    monkeypatch.setattr(gen, "ROOT", tmp_path)
    assert gen.main(["--check"]) == 1


@pytest.mark.parametrize(
    "path",
    [
        STYLES / "house-components.css",
        HTML / "house-page.html",
        HTML / "house-components.html",
    ],
    ids=lambda p: p.name,
)
def test_no_colour_literal_outside_the_generated_css(path: Path) -> None:
    found = COLOUR_LITERAL.findall(path.read_text(encoding="utf-8"))
    assert not found, f"{path.name} carries colour literals {found}; use a token"


def test_every_colour_literal_in_the_generated_css_comes_from_the_tokens(
    tokens: dict, css: str
) -> None:
    values = {v for mode in tokens["colors"].values() for v in mode.values()}
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for literal in re.findall(r"#[0-9a-fA-F]{3,8}\b", body):
        assert literal in values


# ---- R02: the tokens are the approved gallery values ----


def test_tokens_cite_the_gallery_they_were_read_from(tokens: dict) -> None:
    for key, value in GALLERY_SOURCE.items():
        assert tokens["provenance"][key] == value


def test_tokens_match_the_gallery(tokens: dict) -> None:
    house = {**tokens["fonts"], **tokens["scale"], **tokens["colors"]["light"]}
    expected_house = {**GALLERY["house"], "radius-pill": GALLERY["radius-pill"]}
    assert house == expected_house
    assert tokens["colors"]["dark"] == GALLERY["dark"]
    assert tokens["variants"] == {"swiss": GALLERY["swiss"], "mono": GALLERY["mono"]}
    assert tokens["stacks"] == GALLERY["sys"]
    assert tokens["fonts_url"] == GALLERY["fonts_url"]


def test_the_named_fonts_are_the_approved_ones(tokens: dict) -> None:
    assert tokens["fonts"]["display"].startswith('"Bricolage Grotesque"')
    assert tokens["fonts"]["body"].startswith('"Literata"')
    assert tokens["fonts"]["mono"].startswith('"JetBrains Mono"')
    assert tokens["variants"]["swiss"]["body"].startswith('"Archivo"')


# ---- R03: variants set no colour ----


@pytest.mark.parametrize("variant", ["swiss", "mono"])
def test_variant_blocks_set_no_colour(tokens: dict, css: str, variant: str) -> None:
    block = _blocks(css)[f':root[data-variant="{variant}"]']
    assert block, f"no {variant} block"
    colour_names = _colour_names(tokens)
    for name, value in block.items():
        assert name not in colour_names, f"{variant} sets colour token {name}"
        assert name != "color-scheme"
        assert not COLOUR_LITERAL.search(value), f"{variant} {name} carries a colour"


# ---- R04: dark mode is one colour-only flag ----


def test_dark_blocks_set_only_colour(tokens: dict, css: str) -> None:
    blocks = _blocks(css)
    dark_selectors = [':root:not([data-theme="light"])', ':root[data-theme="dark"]']
    allowed = _colour_names(tokens) | {"color-scheme"}
    for selector in dark_selectors:
        block = blocks[selector]
        assert block, selector
        extra = set(block) - allowed
        assert not extra, f"{selector} sets non-colour properties {sorted(extra)}"
        assert block["color-scheme"] == "dark"
        assert {f"--{n}" for n in tokens["colors"]["dark"]} <= set(block)


def test_dark_follows_the_viewer_and_data_theme_overrides(css: str) -> None:
    assert '@media (prefers-color-scheme: dark) {\n  :root:not([data-theme="light"]) {' in css
    assert ':root[data-theme="dark"] {' in css


# ---- R05: every font token ends in a system stack and a generic family ----


def _resolve(value: str, stacks: dict[str, str]) -> list[str]:
    for name, stack in stacks.items():
        value = value.replace(f"var(--{name})", stack)
    return [part.strip().strip('"') for part in value.split(",")]


def test_every_font_token_falls_back_to_a_generic_family(tokens: dict) -> None:
    fonts = dict(tokens["fonts"])
    for variant in tokens["variants"].values():
        fonts.update({f"{k}@variant": v for k, v in variant.items() if k in tokens["fonts"]})
    for name, value in fonts.items():
        families = _resolve(value, tokens["stacks"])
        assert families[-1] in GENERIC_FAMILIES, f"{name} ends in {families[-1]!r}"
        assert len(families) > 2, f"{name} has no system stack before the generic family"


def test_google_fonts_is_the_only_external_request(tokens: dict) -> None:
    page = re.sub(r"/\*.*?\*/|<!--.*?-->", "", gen.render_specimen(tokens), flags=re.S)
    requests = set(re.findall(r"url\(\s*[\"']?([^\"')]+)", page))
    requests |= set(re.findall(r"(?:href|src)\s*=\s*[\"']([^\"']+)", page))
    assert requests == {GALLERY["fonts_url"]}


# ---- R06 and the templates ----


def test_house_family_is_registered_in_the_readme() -> None:
    readme = (ROOT / "templates" / "README.md").read_text(encoding="utf-8")
    row = next(line for line in readme.splitlines() if line.startswith("| `house` |"))
    for needed in (
        "house-tokens.json", "house.css", "house-components.css", "house-page.html",
        "house-components.html", 'data-variant="swiss"', 'data-variant="mono"',
        'data-theme="light"', 'data-theme="dark"', "prefers-color-scheme",
    ):
        assert needed in row, needed


@pytest.mark.parametrize("variant", gen.VARIANTS)
@pytest.mark.parametrize("theme", gen.THEMES)
def test_specimen_renders_every_component(tokens: dict, variant: str, theme: str) -> None:
    page = gen.render_specimen(tokens, variant, theme)
    assert page.startswith("<!doctype html>")
    assert "<script" not in page
    for cls in ('class="stats"', 'class="cols"', 'class="callout"', 'class="pill ok"',
                'class="gate"', 'class="tbl-wrap"'):
        assert cls in page, cls
    html_tag = page.splitlines()[1]
    assert ('data-variant' in html_tag) == (variant != "house")
    assert ('data-theme' in html_tag) == (theme != "auto")


def test_fill_refuses_unknown_and_missing_tokens() -> None:
    with pytest.raises(ValueError, match="has no"):
        gen.fill("{{A}}", {"A": "1", "B": "2"})
    with pytest.raises(ValueError, match="unfilled"):
        gen.fill("{{A}} {{B}}", {"A": "1"})
    assert gen.fill("{{A}}", {"A": "{{NOT_A_TOKEN}}"}) == "{{NOT_A_TOKEN}}"


def test_tokens_file_is_valid_json_with_every_group() -> None:
    data = json.loads((STYLES / "house-tokens.json").read_text(encoding="utf-8"))
    assert set(data) == {
        "family", "provenance", "fonts_url", "stacks", "fonts", "scale", "colors", "variants"
    }
