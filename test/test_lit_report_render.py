"""Tests for tools/lit_report_render.py -- REQ-027 R02, R05, R06, R07, R08 on the render seam.

Two things anchor this file, following test_lit_report_extract.py's pattern for the same reasons.

First, determinism (R05): two calls to render_report() against the same extraction must produce
byte-identical strings, and no figure the pages show may be computed here -- every count traces
back to data["counts"] or to a data["deliverables"]/data["tables"] entry the extractor already
measured. The one documented exception (the entry page's duplicate-discovery-rate trend inside
{{FRAMING}}, which tools/lit_report_render.py's own module docstring explains data["counts"]
cannot carry) is not covered by that drift guarantee and is asserted only as fixed text, never
compared to a computed number.

Second, expectations are derived from the corpus at run time rather than hardcoded, exactly as
test_lit_report_extract.py does: the eleven Markdown deliverables' heading and table counts are
recomputed from research/literature-review/ and checked against the rendered output, not compared
to literals like 30, 1200 or 67.

fill()'s two-directional strictness is tested against the real template family, which is why the
false-positive tools/generate_overview.py's own precedent already solves is worth pinning here
too: templates/styles/lit-report.css's own header comment mentions the literal string
"{{INLINE_STYLES}}" as documentation, and that must survive inlined into every rendered page
without fill() mistaking it for an unfilled placeholder in the *template*.
"""

from __future__ import annotations

import copy
import html
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "research" / "literature-review"

#: The eleven Markdown deliverables' filenames, matched against data["deliverables"] rather than
#: hardcoded as a bare count -- see test_deliverable_set_is_eleven_markdown_plus_three_csv, which
#: pins that this list and the extractor's own count agree.
_MARKDOWN_DELIVERABLE_GLOB = "[0-9][0-9]_*.md"
_CSV_DELIVERABLE_GLOB = "[0-9][0-9]_*.csv"

#: A CommonMark table's delimiter row (the line of dashes/colons under the header row) -- one per
#: table, so counting these in the source is an independent check against the rendered <table>
#: count, following the same "recompute, don't hardcode" rule as test_lit_report_extract.py's
#: collision/hypothesis counts.
_TABLE_DELIMITER_ROW = re.compile(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)+\|?\s*$")

#: Phrases that make a "NOVEL" mention a *statement of unavailability* rather than an assertion
#: that the verdict holds -- derived from how research/literature-review/*.md actually phrases it
#: (grep-verified: "NOVEL is not available", "NOVEL remains unavailable", "categorically not
#: NOVEL", "distinction between NOVEL and the four permitted statuses"). REQ-027 R06 forbids the
#: verdict being asserted, not the word being named while explaining that it never applies.
_NOVEL_UNAVAILABILITY_MARKERS = (
    "unavailable",
    "not available",
    "distinction between",
    "categorically not",
    "is not",
    "no verdict",
    "not claim",
)


def _load(name: str) -> Any:
    """Import a tools/ script by path -- tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


lit_report_extract = _load("lit_report_extract")
lit_report_render = _load("lit_report_render")


@pytest.fixture(scope="module")
def data() -> dict[str, Any]:
    """The extraction, once per module -- render_report() consumes exactly this shape."""
    return lit_report_extract.extract()  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def pages(data: dict[str, Any]) -> dict[str, str]:
    """The rendered fifteen-page mapping, built once and shared read-only across tests."""
    return lit_report_render.render_report(data)


def _strip_pre_blocks(rendered_html: str) -> str:
    """`rendered_html` with every `<pre>...</pre>` region removed.

    R02's "no raw markdown line leaks into the output" check must not fire on `05`/`06`'s fenced
    YAML blocks (`evidence:\\n  - >`), which legitimately render as literal `-`-prefixed text
    inside `<pre><code>`.
    """
    return re.sub(r"<pre>.*?</pre>", "", rendered_html, flags=re.S)


def _synthetic_data() -> dict[str, Any]:
    """A minimal, hand-built `data` dict in the extractor's shape, for render_report() tests that
    are about the renderer's own logic (escaping, editorial-note placement, placeholder marker)
    rather than about the real corpus's content."""
    md_entry = {
        "anchor": "deliverable-99-synthetic-deliverable",
        "filename": "99_synthetic_deliverable.md",
        "number": "99",
        "slug": "synthetic_deliverable",
        "format": "md",
        "bytes": 42,
        "sha256": "a" * 64,
        "markdown": "# Synthetic\n\nHello world.\n",
        "line_count": 3,
    }
    csv_entry = {
        "anchor": "deliverable-98-synthetic-table",
        "filename": "98_synthetic_table.csv",
        "number": "98",
        "slug": "synthetic_table",
        "format": "csv",
        "bytes": 24,
        "sha256": "b" * 64,
    }
    table = {
        "anchor": "table-synthetic-table",
        "filename": "98_synthetic_table.csv",
        "columns": ["a<b", "plain"],
        "column_count": 2,
        "rows": [["1", "2"]],
        "row_count": 1,
    }
    return {
        "deliverables": [md_entry, csv_entry],
        "tables": {"ledger": table},
        "counts": {
            "collision_sections": 3,
            "collision_second_review": {
                "confirmed": 1,
                "disputed": 2,
                "not_applicable": 0,
                "unrecognised": 0,
                "none": 0,
            },
            "deliverables": 2,
            "deliverables_csv": 1,
            "deliverables_markdown": 1,
            "hypothesis_blocks": 0,
            "ledger_columns": 2,
            "ledger_rows": 1,
        },
    }


# --- fill() ----------------------------------------------------------------------------------


def test_fill_substitutes_every_declared_token() -> None:
    rendered = lit_report_render.fill(
        "<p>{{A}}</p><p>{{B}}</p>", {"A": "one", "B": "two"}
    )
    assert rendered == "<p>one</p><p>two</p>"


def test_fill_raises_on_unfilled_token() -> None:
    with pytest.raises(ValueError, match="unfilled"):
        lit_report_render.fill("<p>{{A}}</p><p>{{B}}</p>", {"A": "one"})


def test_fill_raises_on_unknown_token() -> None:
    with pytest.raises(ValueError, match="not present in template"):
        lit_report_render.fill("<p>{{A}}</p>", {"A": "one", "B": "two"})


def test_fill_tolerates_a_substituted_value_containing_literal_braces() -> None:
    """The false positive tools/generate_overview.py's precedent already solves.

    A substituted *value* containing `{{...}}` text of its own (exactly what
    templates/styles/lit-report.css's header comment does with `{{INLINE_STYLES}}`) must not be
    mistaken for an unfilled placeholder in the template being filled.
    """
    rendered = lit_report_render.fill(
        "<style>{{CSS}}</style>", {"CSS": "/* mentions {{INLINE_STYLES}} in prose */"}
    )
    assert "{{INLINE_STYLES}}" in rendered


# --- load_template() ---------------------------------------------------------------------------


def test_load_template_strips_the_leading_doc_comment_from_html() -> None:
    raw = (ROOT / "templates" / "html" / "lit-report-page.html").read_text(encoding="utf-8")
    assert "Token contract" in raw
    loaded = lit_report_render.load_template("lit-report-page.html")
    assert "Token contract" not in loaded
    assert loaded.startswith("<!DOCTYPE html>")


def test_load_template_strips_css_comments_but_keeps_the_rules() -> None:
    """Comments are stripped at load time (page-weight and false-positive-avoidance reasons the
    module docstring and _CSS_COMMENT's own comment explain) -- the rules themselves are not."""
    raw = (ROOT / "templates" / "styles" / "lit-report.css").read_text(encoding="utf-8")
    assert "/*" in raw and "*/" in raw, "fixture assumption: the real file has comments"
    loaded = lit_report_render.load_template("lit-report.css")
    assert "/*" not in loaded
    assert "*/" not in loaded
    assert loaded != raw
    assert len(loaded) < len(raw)
    # A real rule (not just comment prose) survives.
    assert ".lr-editorial-note {" in loaded
    assert ":root {" in loaded


# --- render_markdown() -------------------------------------------------------------------------


def test_render_markdown_produces_structured_elements_not_literal_syntax() -> None:
    source = (
        "# Title\n\n"
        "## Section\n\n"
        "A paragraph with `inline code`, a [link](https://example.invalid) and ~~strike~~.\n\n"
        "- one\n- two\n\n"
        "1. first\n2. second\n\n"
        "> a blockquote\n\n"
        "```python\nprint('x')\n```\n\n"
        "| A | B |\n|---|---|\n| 1 | 2 |\n"
    )
    rendered = lit_report_render.render_markdown(source)
    # <s>, not <del>: markdown-it-py's strikethrough rule emits <s> (verified directly). REQ-027
    # R02's own element list does not name strikethrough at all -- no deliverable in the corpus
    # uses "~~" (grep-verified) -- so this is checked because hard constraint 1 mandates the
    # "strikethrough" plugin be enabled, not because R02 requires it.
    for tag in ("<h1>", "<h2>", "<code>", "<a href=", "<s>", "<ul>", "<li>", "<ol>",
                "<blockquote>", "<pre>", "<table>", "<th>", "<td>"):
        assert tag in rendered, f"expected {tag!r} in rendered output"
    assert "## Section" not in rendered
    assert "- one" not in rendered


# --- Determinism (REQ-027 R05) -------------------------------------------------------------


def test_render_report_is_deterministic_across_two_calls(data: dict[str, Any]) -> None:
    first = lit_report_render.render_report(data)
    second = lit_report_render.render_report(copy.deepcopy(data))
    assert first == second
    assert first, "expected a non-empty page mapping"


def test_render_report_source_carries_no_wall_clock_reading() -> None:
    source = (ROOT / "tools" / "lit_report_render.py").read_text(encoding="utf-8")
    for forbidden in ("datetime.now", "time.time", "date.today", "utcnow"):
        assert forbidden not in source


def test_no_leftover_template_tokens_or_doc_comment_in_any_page(pages: dict[str, str]) -> None:
    """Every {{TOKEN}} the template family declares is filled, and no page carries the
    template's own `<!-- token contract -->` doc comment. The one accepted exception is the
    literal `{{INLINE_STYLES}}` text inside the inlined CSS's own header comment -- the same
    exception test_generate_overview.py's precedent documents for overview.css."""
    for path, rendered in pages.items():
        stripped = rendered.replace("{{INLINE_STYLES}}", "")
        assert "{{" not in stripped, f"unfilled {{TOKEN}} left in {path}"
        assert "Token contract" not in rendered, f"leaked doc comment in {path}"


# --- Fifteen entries, all reachable (REQ-027 R01) -------------------------------------------


def test_render_report_produces_fifteen_entries(pages: dict[str, str]) -> None:
    assert len(pages) == 15
    assert "index.html" in pages


def test_deliverable_set_is_eleven_markdown_plus_three_csv(data: dict[str, Any]) -> None:
    markdown_on_disk = sorted(p.name for p in CORPUS.glob(_MARKDOWN_DELIVERABLE_GLOB))
    csv_on_disk = sorted(p.name for p in CORPUS.glob(_CSV_DELIVERABLE_GLOB))
    assert len(markdown_on_disk) == data["counts"]["deliverables_markdown"]
    assert len(csv_on_disk) == data["counts"]["deliverables_csv"]
    assert len(markdown_on_disk) + len(csv_on_disk) == data["counts"]["deliverables"]


def test_all_fourteen_deliverables_reachable_from_the_entry_page(
    data: dict[str, Any], pages: dict[str, str]
) -> None:
    expected_hrefs = {
        f"{Path(entry['filename']).stem}.html" for entry in data["deliverables"]
    }
    assert len(expected_hrefs) == data["counts"]["deliverables"]
    index_hrefs = set(re.findall(r'href="([^"]+\.html)"', pages["index.html"]))
    assert expected_hrefs <= index_hrefs
    # And every deliverable page's own sidebar reaches every sibling directly (one click).
    for href in expected_hrefs:
        page_hrefs = set(re.findall(r'href="([^"]+\.html)"', pages[href]))
        assert expected_hrefs <= page_hrefs | {href}


# --- R02: Markdown deliverables render as structured HTML ----------------------------------


@pytest.mark.parametrize(
    "path", sorted(CORPUS.glob(_MARKDOWN_DELIVERABLE_GLOB)), ids=lambda p: p.name
)
def test_markdown_deliverable_has_no_leaked_syntax_and_matching_h2_count(
    path: Path, pages: dict[str, str]
) -> None:
    """Checked against the deliverable's own CONTENT region, not the full page.

    The full page also carries the inlined stylesheet inside {{INLINE_STYLES}}; scanning the
    whole page for a bare '<table>' or 'lr-editorial-note' substring would count the CSS's own
    rules and comments as if they were part of the rendered deliverable. render_markdown(source)
    is exactly what render_report() puts into {{CONTENT}} for a Markdown deliverable -- nothing
    wraps or alters it further -- so calling it directly here is the content region, not an
    approximation of it. That equivalence is pinned by the last assertion below.
    """
    source = path.read_text(encoding="utf-8")
    content = lit_report_render.render_markdown(source)

    stripped = _strip_pre_blocks(content)
    bad_lines = [
        line for line in stripped.splitlines()
        if line.strip().startswith("## ") or line.strip().startswith("- ")
    ]
    assert bad_lines == [], f"{path.name}: raw markdown leaked: {bad_lines[:5]}"

    source_h2_count = len(re.findall(r"^## ", source, flags=re.M))
    assert content.count("<h2>") == source_h2_count

    href = f"{path.stem}.html"
    assert content in pages[href], f"{path.name}: CONTENT region not found verbatim in the page"


@pytest.mark.parametrize(
    "path", sorted(CORPUS.glob(_MARKDOWN_DELIVERABLE_GLOB)), ids=lambda p: p.name
)
def test_every_markdown_table_in_source_produced_a_table_element(path: Path) -> None:
    """Checked against render_markdown(source) directly -- see the docstring above for why the
    full page (stylesheet inlined) is the wrong region to scan for a bare '<table>' count."""
    source = path.read_text(encoding="utf-8")
    content = lit_report_render.render_markdown(source)
    source_table_count = sum(
        1 for line in source.splitlines() if _TABLE_DELIMITER_ROW.match(line)
    )
    assert content.count("<table>") == source_table_count


# --- R05: no figure computed by the renderer -------------------------------------------------


def test_index_counts_match_the_extractors_counts_exactly(
    data: dict[str, Any], pages: dict[str, str]
) -> None:
    counts = data["counts"]
    index = pages["index.html"]
    assert f"<strong>{counts['deliverables']}</strong> deliverables" in index
    assert f"<strong>{counts['deliverables_markdown']}</strong> Markdown" in index
    assert f"<strong>{counts['deliverables_csv']}</strong> CSV" in index
    assert f"<strong>{counts['collision_sections']}</strong>" in index
    verdicts = counts["collision_second_review"]
    assert f"<strong>{verdicts['disputed']}</strong> disputed" in index
    assert f"<strong>{verdicts['confirmed']}</strong> confirmed" in index
    assert f"<strong>{counts['hypothesis_blocks']}</strong> hypothesis blocks" in index
    for table in data["tables"].values():
        assert html.escape(table["filename"]) in index
        assert f"<strong>{table['row_count']:,}</strong> rows" in index
        assert f"<strong>{table['column_count']}</strong> columns" in index


def test_csv_placeholder_counts_match_the_extracted_table(
    data: dict[str, Any], pages: dict[str, str]
) -> None:
    for entry in data["deliverables"]:
        if entry["format"] != "csv":
            continue
        href = f"{Path(entry['filename']).stem}.html"
        rendered = pages[href]
        table = next(
            t for t in data["tables"].values() if t["filename"] == entry["filename"]
        )
        assert f"<strong>{table['row_count']:,}</strong>" in rendered
        assert f"<strong>{table['column_count']}</strong>" in rendered
        for column in table["columns"]:
            assert html.escape(column) in rendered


def test_csv_pages_carry_the_phase_lrr_03_handoff_marker_and_md_pages_do_not(
    data: dict[str, Any], pages: dict[str, str]
) -> None:
    marker = "phase-lrr-03"
    for entry in data["deliverables"]:
        href = f"{Path(entry['filename']).stem}.html"
        if entry["format"] == "csv":
            assert marker in pages[href]
        else:
            assert marker not in pages[href]


# --- The 2026-09-22 editorial-note ruling on 05 -----------------------------------------------


def test_editorial_note_appears_only_on_05_and_carries_the_measured_count(
    data: dict[str, Any], pages: dict[str, str]
) -> None:
    """Checked against the actual note markup ('<div class="lr-editorial-note">'), not the bare
    class name -- lit-report.css defines a .lr-editorial-note *rule*, which the inlined
    stylesheet legitimately carries on every page regardless of whether that page has a note."""
    note_markup = '<div class="lr-editorial-note">'
    measured = data["counts"]["collision_sections"]
    note_05 = pages["05_critical_collisions.html"]
    assert note_markup in note_05
    assert str(measured) in note_05
    assert lit_report_render.STALE_05_PREAMBLE_ROW_COUNT in note_05
    # 05's own preamble states a different figure than the measured one.
    assert lit_report_render.STALE_05_PREAMBLE_ROW_COUNT != str(measured)

    for href, rendered in pages.items():
        if href == "05_critical_collisions.html":
            continue
        assert note_markup not in rendered, f"unexpected editorial note markup on {href}"


def test_05_prose_renders_verbatim_alongside_the_note(pages: dict[str, str]) -> None:
    """The owner's ruling: 05's own stale prose is never corrected, only annotated."""
    source = (CORPUS / "05_critical_collisions.md").read_text(encoding="utf-8")
    assert "24 rows" in source
    rendered = pages["05_critical_collisions.html"]
    assert "24 rows" in rendered  # the source's own stale claim, rendered as-is


# --- R06: epistemic posture, R07: disputed share -----------------------------------------------


def test_entry_page_carries_the_memo_and_saturation_statements(pages: dict[str, str]) -> None:
    index = pages["index.html"]
    assert "first research memo" in index
    assert "not a final novelty claim" in index
    assert "Saturation was measured and is explicitly not demonstrated" in index


def test_entry_page_carries_the_disputed_count(
    data: dict[str, Any], pages: dict[str, str]
) -> None:
    verdicts = data["counts"]["collision_second_review"]
    index = pages["index.html"]
    assert f"<strong>{verdicts['disputed']}</strong> are recorded <code>disputed</code>" in index
    assert f"<strong>{data['counts']['collision_sections']}</strong> critical collisions" in index


def test_novel_appears_nowhere_outside_an_unavailability_statement(pages: dict[str, str]) -> None:
    for href, rendered in pages.items():
        for match in re.finditer("NOVEL", rendered):
            window = rendered[max(0, match.start() - 80) : match.end() + 60].lower()
            assert any(marker in window for marker in _NOVEL_UNAVAILABILITY_MARKERS), (
                f"{href}: NOVEL mention with no unavailability marker nearby: {window!r}"
            )


# --- R08: self-contained and offline ------------------------------------------------------------


def test_no_off_origin_network_dependency_in_any_page(pages: dict[str, str]) -> None:
    for href, rendered in pages.items():
        assert "<link" not in rendered, f"{href}: external stylesheet link present"
        assert "<script" not in rendered, f"{href}: script tag present"
        assert re.search(r'src="https?://', rendered) is None, f"{href}: off-origin src"


# --- R09: design-system conformance (this phase's slice) ---------------------------------------


def test_every_page_inlines_the_lit_report_stylesheet(pages: dict[str, str]) -> None:
    css = lit_report_render.load_template("lit-report.css")
    for href, rendered in pages.items():
        assert css in rendered, f"{href}: lit-report.css not inlined"


# --- render_report() escaping and structure, in isolation from the real corpus -----------------


def test_render_report_escapes_csv_columns_and_filenames() -> None:
    pages = lit_report_render.render_report(_synthetic_data())
    csv_page = pages["98_synthetic_table.html"]
    assert "a&lt;b" in csv_page
    assert "<b>" not in csv_page.split("<style>", 1)[-1].split("</style>", 1)[-1].replace(
        "a&lt;b", ""
    )


def test_render_report_synthetic_mapping_has_expected_keys() -> None:
    pages = lit_report_render.render_report(_synthetic_data())
    assert set(pages) == {
        "99_synthetic_deliverable.html",
        "98_synthetic_table.html",
        "index.html",
    }


def test_output_path_derives_from_the_deliverable_filename_stem() -> None:
    assert (
        lit_report_render._output_path("05_critical_collisions.md")
        == "05_critical_collisions.html"
    )
    assert lit_report_render._output_path("00_search_ledger.csv") == "00_search_ledger.html"


def test_the_uncorroborated_duplicate_rate_figure_carries_its_provenance(
    pages: dict[str, str],
) -> None:
    """`REQ-027` R06's stated exception to R05, owner-ruled 2026-09-22.

    20.0% and 15.0% are stated in five campaign deliverables. 6.4-7.7% is in none of them -- it
    is recorded only in two session records, outside the corpus the extractor reads. The ruling
    keeps the figure, because the falling trend is the campaign's actual finding and R06's point
    depends on all three, on condition that the page says plainly where it comes from. This
    asserts that condition holds, and that the first two figures really are in the corpus.
    """
    index = pages["index.html"]
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(CORPUS.glob("[0-9][0-9]_*.md"))
    )
    assert "20.0%" in corpus and "15.0%" in corpus
    assert "6.4" not in corpus.replace("Thm 6.4", "").replace("Sec.6.4", "")

    assert "lr-provenance" in index
    provenance = index[index.index('class="lr-provenance"') :][:900]
    assert "SESS-2026-09-19-08" in provenance
    assert "SESS-2026-09-20-02" in provenance
    assert "6.4" in index


def test_fill_does_not_substitute_into_an_already_substituted_value() -> None:
    """Substitution is one pass over the template, so token order cannot change the result.

    Found by the adversarial review of this phase. A loop of `str.replace` over a growing
    result is order-dependent: a value substituted early that contains a later token's
    `{{TOKEN}}` shape has that shape replaced too, silently corrupting the value, and neither
    of `fill()`'s checks can catch it because both look at the template and never re-scan the
    output. Rendered Markdown is a substitution value here, so a deliverable containing literal
    `{{FOOTER}}`-shaped text would hit exactly this. None does today; the single pass means it
    would not matter if one did.
    """
    template = "<a>{{A}}</a><b>{{B}}</b>"
    forwards = lit_report_render.fill(template, {"A": "look at {{B}} here", "B": "REPLACED"})
    backwards = lit_report_render.fill(
        template, dict(reversed(list({"A": "look at {{B}} here", "B": "REPLACED"}.items())))
    )
    assert forwards == "<a>look at {{B}} here</a><b>REPLACED</b>"
    assert forwards == backwards


def test_raw_html_in_markdown_is_escaped_not_passed_through() -> None:
    """`REQ-027` R08 forbids a script tag; CommonMark passes raw HTML through by default.

    Found by the adversarial review of this phase. No deliverable contains raw HTML today, so
    `html=False` changes nothing in the rendered corpus -- verified byte-identical -- but a
    deliverable that grew a literal `<script>` later would otherwise render it live on a page
    generated from files this module trusts completely.
    """
    rendered = lit_report_render.render_markdown("<script>alert(1)</script>\n\nA <b>b</b> c.\n")
    assert "<script>" not in rendered
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered
    assert "<b>" not in rendered


def test_no_deliverable_currently_contains_raw_html_or_token_shaped_text() -> None:
    """The corpus assumption both guards above rest on, asserted rather than trusted."""
    for path in sorted(CORPUS.glob(_MARKDOWN_DELIVERABLE_GLOB)):
        source = path.read_text(encoding="utf-8")
        assert "{{" not in source, f"{path.name} contains token-shaped text"
        assert "<script" not in source.lower(), f"{path.name} contains a script tag"
