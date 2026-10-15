"""The accent theme sheet generator and its generated page, `gallery/theme-sheet.html`."""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "tools"))

import build_theme_sheet as sheet  # noqa: E402
import build_tokens as tk  # noqa: E402

PAGE = KIT / "gallery" / "theme-sheet.html"
SCRIPT = KIT / "tools" / "build_theme_sheet.py"
EXTERNAL = re.compile(
    r"https?://|(?:src|href|action|srcset|poster|data)\s*=\s*[\"']?\s*//|url\(\s*[\"']?\s*//"
    r"|@import",
    re.IGNORECASE,
)


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )


@pytest.fixture(scope="module")
def tokens() -> tk.Tokens:
    return tk.load_tokens()


@pytest.fixture(scope="module")
def page() -> str:
    return PAGE.read_bytes().decode("utf-8")


@pytest.fixture(scope="module")
def full_text(page: str) -> str:
    """The page with every srcdoc sample unescaped, so checks see the sample documents too."""
    docs = [html.unescape(m) for m in re.findall(r'srcdoc="([^"]*)"', page)]
    return "\n".join([page, *docs])


def test_committed_page_matches_regeneration(tokens: tk.Tokens, page: str) -> None:
    assert page == sheet.render(tokens, sheet.CSS.read_text(encoding="utf-8"))


def test_regenerating_twice_is_byte_identical(tmp_path: Path) -> None:
    a, b = tmp_path / "a.html", tmp_path / "b.html"
    assert run("--out", str(a)).returncode == 0
    assert run("--out", str(b)).returncode == 0
    assert a.read_bytes() == b.read_bytes()
    assert a.read_bytes() == PAGE.read_bytes()


def test_check_passes_on_the_committed_page() -> None:
    result = run("--check")
    assert result.returncode == 0, result.stdout + result.stderr


def test_check_fails_on_a_stale_copy(tmp_path: Path) -> None:
    copy = tmp_path / "theme-sheet.html"
    shutil.copyfile(PAGE, copy)
    assert run("--check", "--out", str(copy)).returncode == 0
    copy.write_text(copy.read_text(encoding="utf-8") + "<!-- edited -->\n", encoding="utf-8")
    assert run("--check", "--out", str(copy)).returncode == 1


def test_check_fails_when_the_bundle_changes(tmp_path: Path) -> None:
    css = tmp_path / "ui.css"
    css.write_text(sheet.CSS.read_text(encoding="utf-8") + "\n/* changed */\n", encoding="utf-8")
    assert run("--check", "--css", str(css)).returncode == 1


def test_check_fails_when_the_page_is_missing(tmp_path: Path) -> None:
    assert run("--check", "--out", str(tmp_path / "absent.html")).returncode == 1


def test_every_accent_appears_in_both_themes(tokens: tk.Tokens, page: str) -> None:
    for name in tokens.accents:
        assert f'id="accent-{name}"' in page
        assert f'href="#accent-{name}"' in page
        for theme in tk.THEMES:
            assert f'data-theme=&quot;{theme}&quot; data-accent=&quot;{name}&quot;' in page
            for role in tk.ACCENT_ROLES:
                assert tokens.accents[name].colours[theme][role] in page
    assert page.count("<iframe ") == 2 * len(tokens.accents)


def test_default_accent_is_marked_provisional(tokens: tk.Tokens, page: str) -> None:
    assert "Provisional default. Not a decision." in page
    assert page.count("(provisional default)") == 1
    first = re.search(r'class="ts-accent" id="accent-([a-z0-9-]+)"', page)
    assert first is not None and first.group(1) == tokens.default_accent


def test_figures_come_from_the_token_maths(tokens: tk.Tokens, page: str) -> None:
    for name in tokens.accents:
        for theme in tk.THEMES:
            worst = sheet.worst_accent_pair(tokens, theme, name)
            assert f"{worst.ratio:.2f}:1" in page
            assert worst.ratio >= worst.minimum


def test_no_external_reference(full_text: str) -> None:
    hits = EXTERNAL.findall(full_text)
    assert hits == []


def test_page_basics(page: str) -> None:
    assert re.search(r"<html lang=\"en\"", page)
    assert re.search(r"<title>[^<]+</title>", page)
    assert len(re.findall(r"<h1[\s>]", page)) == 1
    assert page.endswith("</html>\n") and "\r" not in page


def test_controls_are_hidden_without_script(page: str) -> None:
    assert re.search(r'class="ts-controls"[^>]*\bhidden\b', page)
    assert 'data-show="both"' in page


def test_samples_use_the_kit_classes(full_text: str) -> None:
    for cls in (
        "ui-panel", "ui-panel__header", "ui-panel__title", "ui-panel__controls",
        "ui-button--primary", "ui-button--secondary", "ui-button--ghost", "ui-tabs__tab",
        "ui-pill", "ui-card--ai", "ui-table", "ui-chip", "ui-chip__remove",
    ):
        assert cls in full_text, cls
    for status in ("ok", "warn", "info", "err", "ai"):
        assert f'data-status="{status}"' in full_text


def test_colour_strings_are_escaped_at_output() -> None:
    """Values are validated upstream, but the sheet escapes them where it writes HTML anyway."""
    hostile = '#fff" onmouseover="alert(1)'
    out = sheet.swatch_dot(hostile)
    assert 'onmouseover="' not in out
    assert html.escape(hostile) in out
