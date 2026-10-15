"""The examiner workbench mock is built from Kit v0 parts only.

`gallery/examiner-workbench.html` is a static mock of the product's examiner workbench, used to
match the kit to the real screens. These tests hold it to that:

- every `ui-` class it uses is defined in some stylesheet under `src/css/` (the same collectors
  as the catalogue contract test), and it uses no state class;
- it loads only `../dist/ui.css` and names no external URL (no http, https or protocol-relative
  reference anywhere in the file);
- the five screens are present by id, each reachable from a nav link, and the shell uses the
  `examiner` layout;
- `layouts/examiner.json` validates through build_layouts' own functions, uses all six regions,
  and its grid rules are in the committed `dist/layouts.css`.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "tools"))
sys.path.insert(0, str(KIT / "test"))

import build_layouts as gen  # noqa: E402
from test_catalogue_contract import _all_src_classes, html_classes  # noqa: E402

PAGE = KIT / "gallery" / "examiner-workbench.html"
LAYOUTS = KIT / "layouts"
SCHEMA = LAYOUTS / "layout.schema.json"
DIST_LAYOUTS = KIT / "dist" / "layouts.css"
SCREENS = ("queue", "case", "decision", "supervisor", "accuracy")


class _Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: dict[str, str] = {}
        self.hrefs: list[str] = []
        self.layouts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids[values["id"] or ""] = tag
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")
        classes = (values.get("class") or "").split()
        if "ui-shell" in classes and values.get("data-layout"):
            self.layouts.append(values["data-layout"] or "")


def _text() -> str:
    return PAGE.read_text(encoding="utf-8")


def _collect() -> _Collector:
    collector = _Collector()
    collector.feed(_text())
    return collector


# ---- kit parts only ----


def test_every_ui_class_is_defined_in_src_css() -> None:
    used = {c for c in html_classes(_text()) if c.startswith("ui-")}
    assert used, "the mock uses no ui- class"
    missing = sorted(used - _all_src_classes())
    assert not missing, f"the mock uses classes no stylesheet defines: {missing}"


def test_no_state_class() -> None:
    bad = sorted(
        c
        for c in html_classes(_text())
        if c.startswith("is-") or c in {"active", "selected", "open", "disabled"}
    )
    assert not bad, f"state expressed as a class in the mock: {bad}"


def test_loads_only_the_bundle_and_no_external_url() -> None:
    text = _text()
    sheets = re.findall(r'<link[^>]+rel="stylesheet"[^>]*href="([^"]+)"', text)
    assert sheets == ["../dist/ui.css"]
    external = re.findall(r"(?:https?:)?//[\w.-]+\.[a-z]{2,}", text, flags=re.I)
    assert not external, f"external URL in the mock: {external}"
    assert not re.search(r"<script[^>]+src=", text), "the mock loads a script file"


# ---- screens ----


@pytest.mark.parametrize("screen", SCREENS)
def test_screen_is_present_by_id_and_linked(screen: str) -> None:
    collector = _collect()
    assert collector.ids.get(screen) == "section", f"no <section id={screen!r}>"
    assert f"#{screen}" in collector.hrefs, f"no link reaches #{screen}"


def test_shell_uses_the_examiner_layout() -> None:
    assert _collect().layouts == ["examiner"]


def test_one_main_landmark() -> None:
    assert len(re.findall(r"<main\b", _text())) == 1


# ---- the examiner layout ----


def test_examiner_layout_validates_through_build_layouts() -> None:
    validator = gen.Draft202012Validator(gen.load_schema(SCHEMA))
    layout = gen.load_layout(LAYOUTS / "examiner.json", validator)
    assert layout.id == "examiner"
    assert set(layout.regions) == set(gen.schema_regions(SCHEMA))
    assert "examiner" in {lay.id for lay in gen.load_layouts(LAYOUTS, SCHEMA)}


def test_examiner_layout_is_in_the_committed_sheet() -> None:
    expected = gen.render(gen.load_layouts(LAYOUTS, SCHEMA), gen.schema_regions(SCHEMA))
    sheet = DIST_LAYOUTS.read_text(encoding="utf-8")
    assert sheet == expected, "dist/layouts.css is stale; run build_layouts.py"
    assert '.ui-shell[data-layout="examiner"] {' in sheet
