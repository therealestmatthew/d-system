"""The component catalogue and the component stylesheets name the same classes.

`gallery/catalogue.html` is the reference page for the display components. Two directions:

- every `ui-` class the catalogue uses is defined in some stylesheet under `src/css/`, so the
  page never shows a class the kit does not style;
- every class defined in the ten display-component stylesheets appears in the catalogue, so
  no styled class goes without a reference rendering.

Classes are read from `class="…"` attributes in the HTML and from selectors in the CSS
(comments, strings and attribute selectors removed first, so `[data-state="x.y"]` or a class
named in a comment does not count).
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent.parent
CATALOGUE = KIT / "gallery" / "catalogue.html"
SRC = KIT / "src" / "css"
COMPONENTS = SRC / "components"
DISPLAY_COMPONENTS = (
    "button.css",
    "card.css",
    "pill.css",
    "table.css",
    "state.css",
    "dialog.css",
    "tabs.css",
    "toast.css",
    "citation.css",
    "approval.css",
)
CLASS = re.compile(r"\.(-?[_a-zA-Z][\w-]*)")


class _ClassCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.classes: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name == "class" and value:
                self.classes.update(value.split())


def html_classes(text: str) -> set[str]:
    collector = _ClassCollector()
    collector.feed(text)
    return collector.classes


def css_classes(text: str) -> set[str]:
    """Class names used in selectors (not in declarations, comments or strings)."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r'"[^"]*"|\'[^\']*\'', '""', text)
    names: set[str] = set()
    for selector in re.findall(r"([^{};]+)\{", text):
        selector = selector.strip()
        if selector.startswith("@"):
            continue
        names |= set(CLASS.findall(re.sub(r"\[[^\]]*\]", "", selector)))
    return names


def _all_src_classes() -> set[str]:
    names: set[str] = set()
    for path in sorted(SRC.rglob("*.css")):
        names |= css_classes(path.read_text(encoding="utf-8"))
    return names


def _catalogue_classes() -> set[str]:
    return html_classes(CATALOGUE.read_text(encoding="utf-8"))


def test_catalogue_exists_and_loads_only_the_bundle() -> None:
    text = CATALOGUE.read_text(encoding="utf-8")
    sheets = re.findall(r'<link[^>]+rel="stylesheet"[^>]*href="([^"]+)"', text)
    assert sheets == ["../dist/ui.css"]
    assert "http://" not in text and "https://" not in text


def test_every_catalogue_ui_class_is_defined_in_src_css() -> None:
    used = {c for c in _catalogue_classes() if c.startswith("ui-")}
    assert used, "the catalogue uses no ui- class"
    missing = sorted(used - _all_src_classes())
    assert not missing, f"catalogue uses classes no stylesheet defines: {missing}"


@pytest.mark.parametrize("name", DISPLAY_COMPONENTS)
def test_every_component_class_appears_in_the_catalogue(name: str) -> None:
    path = COMPONENTS / name
    defined = css_classes(path.read_text(encoding="utf-8"))
    assert defined, f"{name} defines no class"
    missing = sorted(defined - _catalogue_classes())
    assert not missing, f"{name} defines classes the catalogue never shows: {missing}"


def test_catalogue_uses_no_state_class() -> None:
    bad = sorted(
        c
        for c in _catalogue_classes()
        if c.startswith("is-") or c in {"active", "selected", "open", "disabled"}
    )
    assert not bad, f"state expressed as a class in the catalogue: {bad}"


# ---- the collectors themselves ----


def test_css_collector_ignores_comments_strings_and_attributes() -> None:
    css = """
    /* .ui-ghost in a comment */
    .ui-a:is(:hover, [data-x=".ui-attr"]) > .ui-b::after { content: ".ui-str"; }
    .ui-c:nth-child(2 of .ui-d) { transform: scale(0.96); }
    @media (prefers-reduced-motion: reduce) { .ui-e { animation: none; } }
    @keyframes k { from { opacity: 0; } to { opacity: 1; } }
    """
    assert css_classes(css) == {"ui-a", "ui-b", "ui-c", "ui-d", "ui-e"}


def test_html_collector_reads_class_attributes_only() -> None:
    html = '<p class="ui-a  ui-b">.ui-text <code>.ui-code</code></p><b class="x"></b>'
    assert html_classes(html) == {"ui-a", "ui-b", "x"}
