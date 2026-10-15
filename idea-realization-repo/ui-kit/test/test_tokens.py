"""The ui-kit tokens file, its generator and the generated stylesheet.

Ported from d-system's `test/test_house_css.py` where it applies: regeneration is byte-identical,
`--check` catches a stale file, dark mode and densities stay in their lanes, font stacks end in a
generic family. Added: no external request at all, every contrast pair for every theme and accent,
the AI hue's distinctness, the strict loader, and the pinned list of variable names that the
component CSS and React units build on.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "tools"))

import build_tokens as gen  # noqa: E402

TOKENS = KIT / "tokens" / "tokens.json"
DIST = KIT / "dist" / "tokens.css"
SCRIPT = KIT / "tools" / "build_tokens.py"

# The public contract. A rename or removal here breaks every unit built on the kit, so it has to
# change in the same diff as the tokens, deliberately.
EXPECTED_NAMES = {
    *(f"--ui-color-{r}" for r in (
        "accent", "accent-2", "accent-hover", "ai", "bg", "err", "err-bg", "focus", "info",
        "info-bg", "line", "line-strong", "muted", "ok", "ok-bg", "on-accent", "overlay",
        "selection", "shadow", "sunken", "surface", "surface-2", "surface-e1", "surface-e2",
        "surface-e3", "text", "warn", "warn-bg",
    )),
    "--ui-ctl-sm", "--ui-ctl-md", "--ui-ctl-lg",
    "--ui-dur-fast", "--ui-dur-base", "--ui-dur-slow",
    "--ui-ease-standard", "--ui-ease-exit",
    "--ui-focus-width", "--ui-focus-offset",
    "--ui-font-sans", "--ui-font-mono",
    *(f"--ui-fs-{s}" for s in ("xs", "sm", "md", "lg", "xl", "2xl", "3xl")),
    "--ui-fw-regular", "--ui-fw-semibold", "--ui-fw-bold",
    "--ui-lh-tight", "--ui-lh-ui", "--ui-lh-prose",
    *(f"--ui-radius-{s}" for s in ("none", "sm", "md", "lg", "pill")),
    *(f"--ui-shadow-e{i}" for i in range(4)),
    *(f"--ui-space-{i}" for i in range(10)),
    *(f"--ui-z-{s}" for s in (
        "base", "sticky", "dock", "dropdown", "overlay", "modal", "toast", "tooltip",
    )),
}

COLOUR_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")
GENERIC_FAMILIES = {"serif", "sans-serif", "monospace", "system-ui", "cursive", "fantasy"}
COLOUR_NAMES = {f"--ui-color-{role}" for role in gen.COLOUR_ROLES}
DARK_SCOPES = (':root:not([data-theme="light"])', ':root[data-theme="dark"]')

Rule = tuple[str, str, dict[str, str]]  # (media condition or "", selector, declarations)


@pytest.fixture(scope="module")
def tokens() -> gen.Tokens:
    return gen.load_tokens()


@pytest.fixture(scope="module")
def css() -> str:
    return DIST.read_bytes().decode("utf-8")


@pytest.fixture(scope="module")
def raw() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(TOKENS.read_text(encoding="utf-8"))
    return data


def _rules(css: str) -> list[Rule]:
    """Every rule in the sheet, with the `@media` condition it sits in (or "")."""
    text = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules: list[Rule] = []

    def flat(body: str, media: str) -> None:
        for selector, decls in re.findall(r"([^{}]+)\{([^{}]*)\}", body):
            parsed = {
                name.strip(): value.strip()
                for name, value in re.findall(r"([\w-]+)\s*:\s*([^;]+);", decls)
            }
            rules.append((media, " ".join(selector.split()), parsed))

    media_re = re.compile(r"@media\s*([^{]+)\{((?:[^{}]*\{[^{}]*\})*)\s*\}")
    for match in media_re.finditer(text):
        flat(match.group(2), match.group(1).strip())
    flat(media_re.sub("", text), "")
    return rules


def _rule(css: str, selector: str, media: str = "") -> dict[str, str]:
    found = [d for m, s, d in _rules(css) if s == selector and m == media]
    assert len(found) == 1, f"expected one rule {selector!r} in {media!r}, found {len(found)}"
    return found[0]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )


def test_rule_parser_sees_every_block(css: str, tokens: gen.Tokens) -> None:
    selectors = {(m, s) for m, s, _ in _rules(css)}
    assert ("", ":root") in selectors
    assert ("", ':root[data-theme="light"]') in selectors
    assert ("", ':root[data-theme="dark"]') in selectors
    assert ("(prefers-color-scheme: dark)", ':root:not([data-theme="light"])') in selectors
    assert ("(prefers-reduced-motion: reduce)", ":root") in selectors
    for name in tokens.accents:
        assert ("", f'[data-accent="{name}"]') in selectors
    # 1 root + 1 forced light + accents + 2 x (dark base + accents) + 2 densities + 1 motion
    assert len(_rules(css)) == 1 + 1 + 3 * len(tokens.accents) + 2 + 2 + 1


# ---- generation is deterministic and the committed file is current ----


def test_committed_css_matches_regeneration(tokens: gen.Tokens, css: str) -> None:
    assert gen.render_css(tokens, gen.read_source()) == css


def test_regenerating_twice_is_byte_identical(tmp_path: Path) -> None:
    first, second = tmp_path / "a.css", tmp_path / "b.css"
    assert gen.main(["--out", str(first)]) == 0
    assert gen.main(["--out", str(second)]) == 0
    assert first.read_bytes() == second.read_bytes() == DIST.read_bytes()


def test_output_is_lf_utf8_with_one_trailing_newline(css: str) -> None:
    data = DIST.read_bytes()
    assert b"\r" not in data
    assert data.endswith(b"}\n") and not data.endswith(b"\n\n")
    assert css.startswith("/*\n  ui-kit design tokens. GENERATED: do not edit by hand.")
    assert "ui-kit/tokens/tokens.json" in css.split("*/", 1)[0]


def test_header_records_the_source_hash(css: str) -> None:
    sha = hashlib.sha256(gen.read_source().encode("utf-8")).hexdigest()
    assert f"sha256:     {sha}" in css


def test_declarations_are_sorted_in_every_block(css: str) -> None:
    for media, selector, decls in _rules(css):
        names = [n for n in decls if n.startswith("--")]
        assert names == sorted(names), f"{media} {selector} is not sorted"


def test_check_mode_passes_on_the_committed_file() -> None:
    result = _run("--check")
    assert result.returncode == 0, result.stdout + result.stderr


def test_check_mode_fails_on_a_stale_output(tmp_path: Path) -> None:
    before = _sha(DIST)
    stale = tmp_path / "tokens.css"
    stale.write_text(DIST.read_text(encoding="utf-8") + "/* hand edit */\n", encoding="utf-8")
    result = _run("--check", "--out", str(stale))
    assert result.returncode == 1
    assert "stale" in result.stdout
    assert _sha(DIST) == before


def test_check_mode_fails_when_the_tokens_change(tmp_path: Path, raw: dict[str, Any]) -> None:
    before = _sha(DIST)
    changed = copy.deepcopy(raw)
    changed["space"]["3"] = "10px"
    src = tmp_path / "tokens.json"
    src.write_text(json.dumps(changed, indent=2), encoding="utf-8")
    out = tmp_path / "tokens.css"
    shutil.copy(DIST, out)
    assert gen.main(["--check", "--tokens", str(src), "--out", str(out)]) == 1
    assert gen.main(["--check", "--out", str(out)]) == 0
    assert _sha(DIST) == before


def test_check_mode_fails_when_the_output_is_missing(tmp_path: Path) -> None:
    assert gen.main(["--check", "--out", str(tmp_path / "absent.css")]) == 1


# ---- the names are the contract ----


def test_variable_names_are_the_pinned_contract(css: str) -> None:
    declared = {n for _, _, d in _rules(css) for n in d if n.startswith("--")}
    assert declared == EXPECTED_NAMES


def test_root_declares_every_name(css: str) -> None:
    assert set(_rule(css, ":root")) - {"color-scheme"} == EXPECTED_NAMES


def test_every_var_reference_is_defined(css: str) -> None:
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    defined = set(re.findall(r"(--ui-[\w-]+)\s*:", body))
    referenced = set(re.findall(r"var\(\s*(--[\w-]+)", body))
    assert referenced, "expected the shadows to reference the shadow colour"
    assert referenced <= defined, sorted(referenced - defined)


def test_every_name_has_the_ui_prefix(css: str) -> None:
    for _, _, decls in _rules(css):
        for name in decls:
            assert name == "color-scheme" or re.fullmatch(r"--ui-[a-z]+-[a-z0-9-]+", name), name


# ---- themes: dark sets colour only ----


def _dark_rules(css: str) -> list[Rule]:
    return [r for r in _rules(css) if any(r[1].startswith(s) for s in DARK_SCOPES)]


def test_dark_blocks_set_only_colour(css: str, tokens: gen.Tokens) -> None:
    rules = _dark_rules(css)
    assert len(rules) == 2 * (1 + len(tokens.accents))
    for media, selector, decls in rules:
        extra = set(decls) - COLOUR_NAMES - {"color-scheme"}
        assert not extra, f"{selector} sets non-colour properties {sorted(extra)}"


@pytest.mark.parametrize(
    ("media", "selector"),
    [("(prefers-color-scheme: dark)", DARK_SCOPES[0]), ("", DARK_SCOPES[1])],
)
def test_dark_base_blocks_set_every_colour(css: str, media: str, selector: str) -> None:
    block = _rule(css, selector, media)
    assert set(block) == COLOUR_NAMES | {"color-scheme"}
    assert block["color-scheme"] == "dark"


def test_dark_follows_the_viewer_and_data_theme_overrides(css: str) -> None:
    assert '@media (prefers-color-scheme: dark) {\n  :root:not([data-theme="light"]) {' in css
    assert '\n:root[data-theme="dark"] {' in css
    assert '\n:root[data-theme="light"] {' in css


def test_forced_light_block_sets_neutral_colour_only(css: str) -> None:
    block = _rule(css, ':root[data-theme="light"]')
    neutral = {f"--ui-color-{r}" for r in gen.NEUTRAL_ROLES}
    assert set(block) == neutral | {"color-scheme"}
    assert block["color-scheme"] == "light"


def test_accent_blocks_set_exactly_the_accent_roles(css: str, tokens: gen.Tokens) -> None:
    accent = {f"--ui-color-{r}" for r in gen.ACCENT_ROLES}
    for name in tokens.accents:
        assert set(_rule(css, f'[data-accent="{name}"]')) == accent
        for scope, media in zip(DARK_SCOPES, ("(prefers-color-scheme: dark)", ""), strict=True):
            selector = f'{scope}[data-accent="{name}"], {scope} [data-accent="{name}"]'
            assert set(_rule(css, selector, media)) == accent


def test_dark_values_are_the_dark_tokens(css: str, tokens: gen.Tokens) -> None:
    block = _rule(css, ':root[data-theme="dark"]')
    for role, value in tokens.palette("dark", tokens.default_accent).items():
        assert block[f"--ui-color-{role}"] == value


# ---- density sets type and space, never colour ----


@pytest.mark.parametrize("density", gen.DENSITIES)
def test_density_blocks_set_no_colour(css: str, density: str) -> None:
    block = _rule(css, f'[data-density="{density}"]')
    assert block
    for name, value in block.items():
        assert name not in COLOUR_NAMES and not name.startswith("--ui-color-"), name
        assert name != "color-scheme"
        assert not COLOUR_LITERAL.search(value), f"{density} {name} carries a colour"
        group = name.removeprefix("--ui-").split("-", 1)[0]
        assert group in gen.DENSITY_GROUPS, f"{density} sets {name}, outside type and space"
        assert name in EXPECTED_NAMES


def test_density_keeps_targets_at_the_wcag_floor(tokens: gen.Tokens) -> None:
    for groups in tokens.density.values():
        for size in groups.get("ctl", {}).values():
            assert float(size.removesuffix("px")) >= 24


def test_reduced_motion_zeroes_durations_only(css: str) -> None:
    block = _rule(css, ":root", "(prefers-reduced-motion: reduce)")
    assert block == {"--ui-dur-fast": "0ms", "--ui-dur-base": "0ms", "--ui-dur-slow": "0ms"}


# ---- fonts and offline safety ----


def test_every_font_stack_ends_in_a_generic_family(css: str) -> None:
    root = _rule(css, ":root")
    stacks = {n: v for n, v in root.items() if n.startswith("--ui-font-")}
    assert set(stacks) == {"--ui-font-sans", "--ui-font-mono"}
    for name, value in stacks.items():
        families = [part.strip().strip('"') for part in value.split(",")]
        assert families[-1] in GENERIC_FAMILIES, f"{name} ends in {families[-1]!r}"
        assert len(families) > 2, f"{name} has no system stack before the generic family"
    assert root["--ui-font-sans"].endswith("sans-serif")
    assert root["--ui-font-mono"].endswith("monospace")


def test_no_external_reference_anywhere_in_the_css(css: str) -> None:
    for pattern in (r"https?:", r"url\(", r"@import", r"@font-face", r"//[a-z0-9]"):
        assert not re.search(pattern, css, flags=re.I), pattern


def test_colour_literals_only_on_colour_names(css: str) -> None:
    for _, selector, decls in _rules(css):
        for name, value in decls.items():
            if COLOUR_LITERAL.search(value):
                assert name in COLOUR_NAMES, f"{selector} {name} carries a colour literal"


# ---- contrast and the AI hue ----


def test_contrast_formula_matches_known_values() -> None:
    assert gen.contrast_ratio("#000000", "#ffffff") == pytest.approx(21.0)
    assert gen.contrast_ratio("#ffffff", "#ffffff") == pytest.approx(1.0)
    assert gen.contrast_ratio("#777777", "#ffffff") == pytest.approx(4.48, abs=0.01)
    assert gen.contrast_ratio("#767676", "#ffffff") == pytest.approx(4.54, abs=0.01)
    assert gen.contrast_ratio("#ffffff", "#767676") == gen.contrast_ratio("#767676", "#ffffff")


def test_there_are_enough_accent_candidates(tokens: gen.Tokens) -> None:
    assert len(tokens.accents) >= 8
    assert tokens.default_accent in tokens.accents
    assert tokens.accents["magenta"].colours["light"]["accent"] == "#c8205f"


def test_declared_pairs_cover_the_required_set(tokens: gen.Tokens) -> None:
    declared = {(p.fg, p.bg): p.min for p in tokens.pairs}
    required = {
        ("text", "bg"): 4.5, ("text", "surface"): 4.5, ("text", "surface-2"): 4.5,
        ("muted", "bg"): 4.5, ("muted", "surface"): 4.5, ("on-accent", "accent"): 4.5,
        ("accent", "bg"): 4.5, ("focus", "bg"): 3.0, ("ai", "bg"): 4.5,
        **{(s, f"{s}-bg"): 4.5 for s in ("ok", "warn", "info", "err")},
        **{(s, "bg"): 4.5 for s in ("ok", "warn", "info", "err")},
    }
    for pair, minimum in required.items():
        assert pair in declared, pair
        assert declared[pair] >= minimum, pair


@pytest.mark.parametrize("theme", gen.THEMES)
def test_every_contrast_pair_passes_for_every_accent(tokens: gen.Tokens, theme: str) -> None:
    results = [r for r in gen.contrast_results(tokens) if r.theme == theme]
    assert len(results) == len(tokens.pairs) * len(tokens.accents)
    failures = [
        f"{r.accent} {r.pair.fg}/{r.pair.bg} {r.ratio:.2f} < {r.pair.min}"
        for r in results if not r.ok
    ]
    assert not failures, failures


def test_ai_hue_is_distinct_from_accent_and_status(tokens: gen.Tokens) -> None:
    assert gen.distinctness_failures(tokens) == []


def test_contrast_cli_passes_and_reports_every_check(tokens: gen.Tokens) -> None:
    result = _run("--contrast")
    assert result.returncode == 0, result.stdout + result.stderr
    total = len(gen.THEMES) * len(tokens.accents) * len(tokens.pairs)
    assert f"{total} contrast checks, 0 failed; ai distinctness: 0 failed" in result.stdout


def test_contrast_cli_fails_on_a_weak_pair(tmp_path: Path, raw: dict[str, Any]) -> None:
    weak = copy.deepcopy(raw)
    weak["color"]["light"]["muted"] = "#b0b0b0"
    src = tmp_path / "tokens.json"
    src.write_text(json.dumps(weak), encoding="utf-8")
    result = _run("--contrast", "--tokens", str(src))
    assert result.returncode == 1
    assert "FAIL light" in result.stdout


def test_contrast_cli_fails_when_ai_matches_the_accent(tmp_path: Path, raw: dict[str, Any]) -> None:
    clash = copy.deepcopy(raw)
    clash["accents"]["sets"]["blue"]["light"]["ai"] = "#1e40af"
    src = tmp_path / "tokens.json"
    src.write_text(json.dumps(clash), encoding="utf-8")
    result = _run("--contrast", "--tokens", str(src))
    assert result.returncode == 1
    assert "FAIL ai distinctness light/blue" in result.stdout


# ---- the strict loader ----


def _mutations() -> list[tuple[str, Any]]:
    def drop(path: tuple[str, ...]) -> Any:
        def f(d: dict[str, Any]) -> None:
            for k in path[:-1]:
                d = d[k]
            del d[path[-1]]
        return f

    def put(path: tuple[str, ...], value: Any) -> Any:
        def f(d: dict[str, Any]) -> None:
            for k in path[:-1]:
                d = d[k]
            d[path[-1]] = value
        return f

    def pair(**fields: Any) -> Any:
        def f(d: dict[str, Any]) -> None:
            d["contrast_pairs"].append({"fg": "text", "bg": "bg", "min": 4.5, "use": "x", **fields})
        return f

    return [
        ("unknown top-level group", put(("colours",), {})),
        ("missing group", drop(("z",))),
        ("unknown key in a scalar group", put(("space", "10"), "96px")),
        ("missing key in a scalar group", drop(("fs", "md"))),
        ("bad value", put(("space", "3"), "8")),
        ("colour literal in a shadow", put(("shadow", "e1"), "0 1px 2px #000000")),
        ("font without a generic family", put(("font", "sans"), "Inter, Arial")),
        ("unknown neutral role", put(("color", "light", "brand"), "#123456")),
        ("unknown theme", put(("color", "sepia"), {})),
        ("uppercase hex", put(("color", "light", "bg"), "#FFFFFF")),
        ("unknown accent role", put(("accents", "sets", "blue", "light", "brand"), "#123456")),
        ("missing accent role", drop(("accents", "sets", "blue", "dark", "ai"))),
        ("unknown accent set key", put(("accents", "sets", "blue", "hue"), 220)),
        ("bad accent name", put(("accents", "sets", "Blue Two"), {})),
        ("default not a set", put(("accents", "default"), "cyan")),
        ("colour in a density", put(("density", "compact", "color"), {"bg": "#000000"})),
        ("unknown density", put(("density", "cozy"), {})),
        ("density key not in base group", put(("density", "compact", "space", "12"), "1px")),
        ("reduced motion outside dur", put(("reduced_motion", "ease"), {})),
        ("unknown pair role", pair(fg="brand")),
        ("unknown pair key", pair(level="AA")),
        ("translucent pair role", pair(fg="overlay")),
        ("non-numeric minimum", pair(min="4.5")),
        ("unknown meta key", put(("meta", "author"), "x")),
    ]


@pytest.mark.parametrize(("label", "mutate"), _mutations(), ids=[m[0] for m in _mutations()])
def test_loader_rejects(raw: dict[str, Any], label: str, mutate: Any) -> None:
    broken = copy.deepcopy(raw)
    mutate(broken)
    with pytest.raises(gen.TokenError):
        gen.parse_tokens(broken)


def test_loader_accepts_the_real_file(raw: dict[str, Any]) -> None:
    gen.parse_tokens(copy.deepcopy(raw))


def test_cli_reports_a_broken_tokens_file(tmp_path: Path, raw: dict[str, Any]) -> None:
    broken = copy.deepcopy(raw)
    broken["mystery"] = {}
    src = tmp_path / "tokens.json"
    src.write_text(json.dumps(broken), encoding="utf-8")
    result = _run("--check", "--tokens", str(src))
    assert result.returncode == 2
    assert "unknown key(s) ['mystery']" in result.stderr
