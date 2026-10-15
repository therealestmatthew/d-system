"""The shell demo is built from Kit v0 parts only, and its script drives gallery controls only.

`gallery/shell-demo.html` shows the app shell and the panel frame. Like the other gallery pages it
is held to:

- every `ui-` class it uses is defined in some stylesheet under `src/css/`, and no state class;
- it loads only `../dist/ui.css`, names no external URL and loads no script file;
- the shell starts in the `ide` layout, and every layout the layout control offers is a shipped
  layout under `layouts/`.

Its one inline script is gallery-only: it is not a kit behaviour (those are declared through
`data-ui`, planned in later phases), so it must not use `data-ui`, and the only elements it looks
up are the `[data-gallery]` controls and the `.ui-shell` it switches.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "test"))

from test_catalogue_contract import _all_src_classes, html_classes  # noqa: E402

PAGE = KIT / "gallery" / "shell-demo.html"
LAYOUTS = KIT / "layouts"
ALLOWED_LOOKUPS = {'[data-gallery="theme"]', '[data-gallery="layout"]', ".ui-shell"}


class _Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.layouts: list[str] = []
        self.options: list[str] = []
        self._in_layout_select = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = (values.get("class") or "").split()
        if "ui-shell" in classes and values.get("data-layout"):
            self.layouts.append(values["data-layout"] or "")
        if tag == "select" and values.get("data-gallery") == "layout":
            self._in_layout_select = True
        if tag == "option" and self._in_layout_select:
            self.options.append(values.get("value") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "select":
            self._in_layout_select = False


def _text() -> str:
    return PAGE.read_text(encoding="utf-8")


def _collect() -> _Collector:
    collector = _Collector()
    collector.feed(_text())
    return collector


def _scripts() -> list[str]:
    return re.findall(r"<script\b[^>]*>(.*?)</script>", _text(), flags=re.S)


def test_every_ui_class_is_defined_in_src_css() -> None:
    used = {c for c in html_classes(_text()) if c.startswith("ui-")}
    assert used, "the demo uses no ui- class"
    missing = sorted(used - _all_src_classes())
    assert not missing, f"the demo uses classes no stylesheet defines: {missing}"


def test_no_state_class() -> None:
    bad = sorted(
        c
        for c in html_classes(_text())
        if c.startswith("is-") or c in {"active", "selected", "open", "disabled"}
    )
    assert not bad, f"state expressed as a class in the demo: {bad}"


def test_loads_only_the_bundle_and_no_external_url() -> None:
    text = _text()
    sheets = re.findall(r'<link[^>]+rel="stylesheet"[^>]*href="([^"]+)"', text)
    assert sheets == ["../dist/ui.css"]
    external = re.findall(r"(?:https?:)?//[\w.-]+\.[a-z]{2,}", text, flags=re.I)
    assert not external, f"external URL in the demo: {external}"
    assert not re.search(r"<script[^>]+src=", text), "the demo loads a script file"


def test_shell_starts_in_ide_and_offers_only_shipped_layouts() -> None:
    collector = _collect()
    assert collector.layouts == ["ide"]
    shipped = {p.stem for p in LAYOUTS.glob("*.json") if p.name != "layout.schema.json"}
    assert collector.options, "no layout options found"
    unknown = sorted(set(collector.options) - shipped)
    assert not unknown, f"the layout control offers layouts that do not exist: {unknown}"


def test_script_is_gallery_only() -> None:
    scripts = _scripts()
    assert len(scripts) == 1, f"expected one inline script, found {len(scripts)}"
    script = scripts[0]
    assert "data-ui" not in script and "data-ui" not in _text()
    lookups = set(re.findall(r"querySelector(?:All)?\(\s*['\"](.+?)['\"]\s*\)", script))
    assert lookups, "the script looks nothing up"
    extra = sorted(lookups - ALLOWED_LOOKUPS)
    assert not extra, f"the script reaches beyond the gallery controls and the shell: {extra}"
