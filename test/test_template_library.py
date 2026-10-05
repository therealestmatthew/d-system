"""Tests for the template library (`tools/template_library.py`, `templates/html/library.yaml`) —
`REQ-021` R05 and R06, `phase-des-03`.

R05: a template added without touching a generator renders, and the existing families still
render byte-identically. R06: the population method is machine-readable and the library
dispatches on it. Cases that add or change templates work on a copy of `templates/` under
`tmp_path`; the real tree is only read.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "templates" / "html"


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


lib = _load("template_library")
generate_overview = _load("generate_overview")


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A copy of templates/ plus the generator files the manifest names."""
    shutil.copytree(ROOT / "templates", tmp_path / "templates")
    (tmp_path / "tools").mkdir()
    for generator in (
        "generate_overview.py",
        "generate_engine_pages.py",
        "generate_house_css.py",
        "lit_report_render.py",
    ):
        shutil.copy(ROOT / "tools" / generator, tmp_path / "tools" / generator)
    return tmp_path


def manifest(tree: Path) -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load((tree / lib.MANIFEST).read_text(encoding="utf-8"))
    return data


def write_manifest(tree: Path, data: dict[str, Any]) -> None:
    (tree / lib.MANIFEST).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def family(data: dict[str, Any], fid: str) -> dict[str, Any]:
    found: dict[str, Any] = next(f for f in data["families"] if f["id"] == fid)
    return found


# --- the real library -------------------------------------------------------------------------


def test_every_template_file_is_declared_with_a_population_method() -> None:
    library = lib.load()
    files = sorted(p.name for p in HTML.glob("*.html"))
    assert sorted(library.templates) == files
    for template in library.templates.values():
        assert template.population in lib.POPULATION_METHODS


def test_the_declarations_match_the_shipped_families() -> None:
    library = lib.load()
    by_family: dict[str, set[str]] = {}
    for template in library.templates.values():
        by_family.setdefault(template.family, set()).add(template.population)
    assert by_family == {
        "overview": {"slot-fill"},
        "house": {"slot-fill", "ai-adaptation"},
        "atlas": {"both", "ai-adaptation"},
        "lit-report": {"slot-fill"},
    }
    atlas = library.get("atlas-page.html")
    assert atlas.ai_slots == ("MASTHEAD", "SECTIONS", "PAGE_SCRIPT")
    assert library.get("house-components.html").reference
    assert library.get("atlas-components.html").reference


def test_the_population_method_is_machine_readable_from_the_cli(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """R06: read a template's declaration as data, not prose."""
    assert lib.main(["list"]) == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert {row["template"] for row in rows} == {p.name for p in HTML.glob("*.html")}
    assert all(row["population"] in lib.POPULATION_METHODS for row in rows)
    assert lib.main(["show", "atlas-page.html"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["population"] == "both"
    assert shown["ai_slots"] == ["MASTHEAD", "SECTIONS", "PAGE_SCRIPT"]


# --- R06: dispatch ------------------------------------------------------------------------------

HOUSE_VALUES = {
    "ROOT_ATTRS": "",
    "PAGE_TITLE": "T",
    "KICKER": "K",
    "HEADING": "H",
    "LEDE": "L",
    "META": "<span>m</span>",
    "BODY": "<p>b</p>",
    "FOOTER": "f",
}


def test_slot_fill_returns_a_page_with_its_styles_inlined() -> None:
    library = lib.load()
    result = library.render("house-page.html", HOUSE_VALUES)
    assert isinstance(result, lib.Rendered)
    assert "{{" not in result.html.split("<style>", 1)[0]
    styles = (ROOT / "templates/styles/house.css").read_text(encoding="utf-8")
    assert styles in result.html


def test_both_fills_the_deterministic_slots_and_briefs_the_rest() -> None:
    library = lib.load()
    result = library.render(
        "atlas-page.html", {"PAGE_TITLE": "Atlas", "BRAND": "D", "BRAND_SUB": "sub"}
    )
    assert isinstance(result, lib.AdaptationBrief)
    assert result.ai_slots == ("MASTHEAD", "SECTIONS", "PAGE_SCRIPT")
    assert result.filled_slots == ("BRAND", "BRAND_SUB", "INLINE_STYLES", "PAGE_TITLE")
    for slot in result.ai_slots:
        assert "{{" + slot + "}}" in result.partial
    styles = (ROOT / "templates/styles/atlas.css").read_text(encoding="utf-8")
    for slot in result.filled_slots:
        # atlas.css names {{INLINE_STYLES}} in its own comment; only the slot itself must go.
        token = "{{" + slot + "}}"
        assert result.partial.count(token) == styles.count(token)
    brief = json.loads(result.to_json())
    assert brief["population"] == "both" and brief["partial"] == result.partial


def test_both_refuses_a_missing_deterministic_slot() -> None:
    with pytest.raises(lib.LibraryError, match="BRAND_SUB"):
        lib.load().render("atlas-page.html", {"PAGE_TITLE": "A", "BRAND": "D"})


def test_a_reference_catalogue_is_not_rendered() -> None:
    with pytest.raises(lib.LibraryError, match="reference"):
        lib.load().render("house-components.html", {})


def test_dispatch_follows_the_declaration_not_the_caller(tree: Path) -> None:
    """Change only the manifest and the same call comes back as a brief: the caller never needs
    to know which templates an agent populates."""
    values = {"BAR_LABEL": "a", "BAR_VALUE": "1", "BAR_PERCENT": "50"}
    before = lib.load(tree).render("overview-bar.html", values)
    assert isinstance(before, lib.Rendered)

    data = manifest(tree)
    family(data, "overview")["templates"].append(
        {"file": "overview-bar.html", "population": "ai-adaptation"}
    )
    write_manifest(tree, data)
    after = lib.load(tree).render("overview-bar.html", values)
    assert isinstance(after, lib.AdaptationBrief)
    assert after.population == "ai-adaptation" and after.filled_slots == ()
    assert set(after.ai_slots) == {"BAR_LABEL", "BAR_VALUE", "BAR_PERCENT"}


def test_slot_fill_is_strict_and_single_pass() -> None:
    assert lib.fill("<p>{{A}}{{B}}</p>", {"A": "{{B}}", "B": "x"}) == "<p>{{B}}x</p>"
    with pytest.raises(lib.LibraryError, match="unfilled"):
        lib.fill("{{A}}{{B}}", {"A": "1"})
    with pytest.raises(lib.LibraryError, match="no slot"):
        lib.fill("{{A}}", {"A": "1", "C": "2"})


# --- R05: adding a template needs no generation-code change --------------------------------------


def test_a_new_file_in_an_existing_family_renders_without_any_change(tree: Path) -> None:
    (tree / "templates/html/overview-callout.html").write_text(
        "<!-- Token contract: {{NOTE}} -->\n<aside class=\"callout\">{{NOTE}}</aside>\n",
        encoding="utf-8",
    )
    result = lib.load(tree).render("overview-callout.html", {"NOTE": "hello"})
    assert isinstance(result, lib.Rendered)
    assert result.html == '<aside class="callout">hello</aside>\n'


def test_a_new_family_is_a_manifest_entry_and_renders_through_the_cli(
    tree: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tree / "templates/styles/note.css").write_text("p { margin: 0; }\n", encoding="utf-8")
    (tree / "templates/html/note-page.html").write_text(
        "<!-- note family: {{TITLE}} {{TEXT}} {{INLINE_STYLES}} -->\n"
        "<!DOCTYPE html><title>{{TITLE}}</title><style>{{INLINE_STYLES}}</style><p>{{TEXT}}</p>\n",
        encoding="utf-8",
    )
    data = manifest(tree)
    data["families"].append(
        {
            "id": "note",
            "generators": [],
            "inline_styles": {"files": ["templates/styles/note.css"], "separator": ""},
            "templates": [{"file": "note-page.html", "population": "slot-fill"}],
        }
    )
    write_manifest(tree, data)
    (tree / "data.json").write_text(json.dumps({"TITLE": "N", "TEXT": "t"}), encoding="utf-8")
    monkeypatch.setattr(lib, "ROOT", tree)
    out = tree / "page.html"
    assert lib.main(["render", "note-page.html", "--data", str(tree / "data.json"),
                     "--out", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == (
        "<!DOCTYPE html><title>N</title><style>p { margin: 0; }\n</style><p>t</p>\n"
    )


def test_a_future_lit_report_file_is_declared_by_its_family_pattern(tree: Path) -> None:
    """phase-lrr-03 adds lit-report-table.html; the family's pattern already covers it."""
    (tree / "templates/html/lit-report-table.html").write_text(
        "<!-- contract -->\n<div data-lr-table=\"{{TABLE_KEY}}\"></div>\n", encoding="utf-8"
    )
    template = lib.load(tree).get("lit-report-table.html")
    assert (template.family, template.population, template.page) == (
        "lit-report", "slot-fill", False
    )


def test_an_ai_adaptation_template_comes_back_as_a_brief_from_the_cli(
    tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tree / "data.json").write_text(json.dumps({"PAGE_TITLE": "A", "BRAND": "D",
                                                "BRAND_SUB": "s"}), encoding="utf-8")
    monkeypatch.setattr(lib, "ROOT", tree)
    out = tree / "brief.json"
    assert lib.main(["render", "atlas-page.html", "--data", str(tree / "data.json"),
                     "--out", str(out)]) == 0
    brief = json.loads(out.read_text(encoding="utf-8"))
    assert brief["ai_slots"] == ["MASTHEAD", "SECTIONS", "PAGE_SCRIPT"]
    assert "{{SECTIONS}}" in brief["partial"]


# --- R05: the existing families render byte-identically -------------------------------------------


def test_every_overview_fill_replays_byte_identically_through_the_library(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Record each fill generate_overview.py makes while building the real page, then render the
    same template with the same values through the library and compare the bytes."""
    original = generate_overview._fill
    calls: list[tuple[str, dict[str, str], str]] = []

    def recording(template: str, tokens: dict[str, str]) -> str:
        out: str = original(template, tokens)
        calls.append((template, dict(tokens), out))
        return out

    monkeypatch.setattr(generate_overview, "_fill", recording)
    generate_overview.generate()
    library = lib.load()
    by_body = {
        t.body(): t.name for t in library.templates.values() if t.family == "overview"
    }
    seen = set()
    for template, tokens, out in calls:
        name = by_body[template]
        seen.add(name)
        result = library.render(name, tokens)
        assert isinstance(result, lib.Rendered)
        assert result.html == out, name
    assert seen == set(by_body.values()), "every overview template was exercised"


def test_overview_page_styles_from_the_manifest_match_the_generator() -> None:
    library = lib.load()
    assert library.inline_styles(library.get("overview-page.html")) == (
        generate_overview.Templates().css
    )


def test_house_page_replays_byte_identically_through_the_library(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _load("generate_engine_pages")
    original = engine.house.fill
    calls: list[tuple[dict[str, str], str]] = []

    def recording(template: str, values: dict[str, str]) -> str:
        out: str = original(template, values)
        calls.append((dict(values), out))
        return out

    monkeypatch.setattr(engine.house, "fill", recording)
    engine._page({"commit": "abc1234", "date": "2026-10-05", "dirty": False},
                 "Title", "Lede.", "<p>body</p>")
    (values, out), = calls
    result = lib.load().render("house-page.html", values)
    assert isinstance(result, lib.Rendered) and result.html == out


def test_house_specimen_replays_byte_identically_through_the_library(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """generate_house_css.py --specimen is the house page's second generator."""
    house = _load("generate_house_css")
    original = house.fill
    calls: list[tuple[dict[str, str], str]] = []

    def recording(template: str, values: dict[str, str]) -> str:
        out: str = original(template, values)
        calls.append((dict(values), out))
        return out

    monkeypatch.setattr(house, "fill", recording)
    house.render_specimen(house.load_tokens(), variant="swiss", theme="dark")
    (values, out), = calls
    result = lib.load().render("house-page.html", values)
    assert isinstance(result, lib.Rendered) and result.html == out


def test_adding_templates_leaves_existing_renders_byte_identical(tree: Path) -> None:
    """R05's second half, on a tree that gains a template and a family."""
    atlas_values = {"PAGE_TITLE": "A", "BRAND": "D", "BRAND_SUB": "s"}
    bar_values = {"BAR_LABEL": "a", "BAR_VALUE": "1", "BAR_PERCENT": "50"}
    templates = generate_overview.Templates(
        root=tree / "templates/html", css=tree / "templates/styles/overview.css"
    )
    before = (
        lib.load(tree).render("atlas-page.html", atlas_values),
        lib.load(tree).render("overview-bar.html", bar_values),
        generate_overview.render_bars(["x"], [1], templates.bar),
    )
    (tree / "templates/html/overview-callout.html").write_text("<p>{{NOTE}}</p>\n", "utf-8")
    data = manifest(tree)
    (tree / "templates/html/note-page.html").write_text("<p>{{T}}</p>\n", encoding="utf-8")
    data["families"].append({"id": "note", "generators": [], "templates": [
        {"file": "note-page.html", "population": "slot-fill"}]})
    write_manifest(tree, data)
    templates = generate_overview.Templates(
        root=tree / "templates/html", css=tree / "templates/styles/overview.css"
    )
    after = (
        lib.load(tree).render("atlas-page.html", atlas_values),
        lib.load(tree).render("overview-bar.html", bar_values),
        generate_overview.render_bars(["x"], [1], templates.bar),
    )
    assert before == after


# --- the declaration cannot drift from the files ------------------------------------------------


def test_an_undeclared_template_is_rejected(tree: Path) -> None:
    (tree / "templates/html/stray.html").write_text("<p>{{X}}</p>\n", encoding="utf-8")
    with pytest.raises(lib.LibraryError, match="undeclared template.*stray.html"):
        lib.load(tree)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda d: family(d, "overview")["templates"].append(
            {"pattern": "nothing-*.html", "population": "slot-fill"}), "matches no file"),
        (lambda d: family(d, "house")["templates"][0].update(population="manual"),
         "population must be one of"),
        (lambda d: family(d, "house")["templates"][0].update(ai_slots=["BODY"]),
         "ai_slots is required for both and allowed only there"),
        (lambda d: family(d, "atlas")["templates"][0].update(ai_slots=["NOPE"]),
         "ai_slots not in the template"),
        (lambda d: family(d, "overview")["templates"].append(
            {"pattern": "overview-b*.html", "population": "slot-fill"}),
         "declared twice at the same level"),
        (lambda d: family(d, "atlas").update(generators=["tools/missing.py"]), "does not exist"),
        (lambda d: family(d, "atlas").update(generators=None), "generators must be a list"),
        (lambda d: d.update(schema_version=2), "schema_version"),
    ],
    ids=["empty-pattern", "bad-method", "ai-slots-on-slot-fill", "unknown-ai-slot",
         "double-declared", "missing-generator", "generators-not-a-list", "schema-version"],
)
def test_an_inconsistent_manifest_is_rejected(tree: Path, change: Any, message: str) -> None:
    data = manifest(tree)
    change(data)
    write_manifest(tree, data)
    with pytest.raises(lib.LibraryError, match=message):
        lib.load(tree)
