#!/usr/bin/env python3
"""Render the literature-review campaign report's pages — `REQ-027` `phase-lrr-02`.

This module renders. It writes nothing to `_public/` and assembles no CLI — `phase-lrr-04` owns
both. It consumes `tools/lit_report_extract.extract()`'s output (see that module's docstring for
the shape) and returns a mapping of relative output path to complete HTML document; writing that
mapping to disk is `phase-lrr-04`'s job, and replacing the three CSV pages' placeholder bodies
with interactive tables is `phase-lrr-03`'s.

Fifteen entries come out of `render_report()`: `index.html` plus one page per deliverable
(fourteen — eleven Markdown, three CSV). The three CSV pages carry a placeholder body in this
phase — their column list and row count, both read from the extractor's `tables` — rather than a
sortable, filterable table; `_csv_placeholder()` below is where `phase-lrr-03` replaces the body.

Determinism (`REQ-027` R05). `render_report()` is a pure function of its `data` argument and the
on-disk template family under `templates/html/` and `templates/styles/` — no wall clock, no
random input, no model or network call. Two calls against the same `data` produce identical
strings, and iteration over `data["tables"]` (a dict) is always `sorted()` for the same reason
`tools/lit_report_extract.py`'s own docstring gives: dict iteration order is Python's, not the
corpus's, but sorting removes even that dependency.

The renderer computes no corpus figures of its own (R05's "the renderer never computes"). Every
count on the page — collision sections, disputed/confirmed review counts, table row/column
counts, deliverable counts — is read from `data["counts"]` or from a `data["tables"]`/
`data["deliverables"]` entry the extractor already measured; nothing here re-derives a number
from the source text. The one deliberate exception is the entry-page `{{FRAMING}}` block's fixed
epistemic-posture prose (the "first research memo" statement and the duplicate-discovery-rate
trend): those are quoted verbatim from `research/literature-review/CLAUDE.md` and from `REQ-027`
R06's own text, not measured by `tools/lit_report_extract.py`, because the extractor's `counts`
carries no duplicate-rate figure at all and the campaign's third measurement point (`phase-lit-09`,
6.4-7.7%) is recorded only in `docs/03-sessions/`, outside `research/literature-review/` and so
outside the extractor's corpus. The owner ruled on 2026-09-22 that the figure is kept rather than
dropped, because the falling trend is the campaign's actual finding and R06's point depends on all
three points — on condition that the page says plainly where it comes from. `REQ-027` R06 now
records this as a stated exception to R05, and `_render_framing()` emits a visible provenance line
naming the two session records. Nothing on the page presents this figure as measured.

The 2026-09-22 owner ruling on `05_critical_collisions.md`'s stale preamble ("24 rows" against a
measured 30 `collision_sections`) is implemented narrowly: the prose renders verbatim like every
other deliverable, and `_editorial_note_05()` adds one `{{EDITORIAL_NOTES}}` note stating the
measured count — read from `data["counts"]["collision_sections"]`, never a literal — and that the
file's own preamble states a different figure. `research/literature-review/` is read-only; nothing
here writes there.

Markdown deliverables render through `markdown-it-py`'s CommonMark preset with `table` and
`strikethrough` enabled — the combination verified against all eleven Markdown deliverables,
including `05` and `06`'s YAML-block hard cases (05/06 carry `evidence: >`-style YAML fenced code
that must stay inside `<pre>`, not leak out as literal `- ` text).

    from tools.lit_report_render import render_report
    from tools.lit_report_extract import extract
    pages = render_report(extract())   # {"index.html": "<!DOCTYPE html>...", "05_..." : ...}
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_HTML = ROOT / "templates" / "html"
TEMPLATES_STYLES = ROOT / "templates" / "styles"

SITE_TITLE = "D-System Literature-Review Campaign Report"

#: The 05_critical_collisions.md preamble's own stated figure — a literal quote of the file's
#: stale prose, not a measurement. The correct, measured figure (30) always comes from
#: data["counts"]["collision_sections"]; see _editorial_note_05().
STALE_05_PREAMBLE_ROW_COUNT = "24"

#: A template's leading `<!-- token contract -->` doc comment mentions every {{TOKEN}} name it
#: documents as literal text. Left in place, a naive global {{TOKEN}} replace would also match
#: those mentions and corrupt the comment with substituted content — the same problem
#: tools/generate_overview.py's _read() solves the same way. templates/styles/lit-report.css is
#: read as a substitution *value* (INLINE_STYLES) and is never itself filled, so this comment
#: stripping alone would leave its own /* */ comments in place -- see _CSS_COMMENT below for why
#: those are stripped too.
_LEADING_HTML_COMMENT = re.compile(r"^\s*<!--.*?-->\s*", re.DOTALL)

#: Every `/* ... */` block in templates/styles/lit-report.css, stripped when the stylesheet is
#: loaded for inlining. Two reasons: page weight (the CSS is inlined into all fifteen pages, so
#: every byte of comment is paid fifteen times over), and false positives in prose that scans
#: rendered pages for a literal string -- the CSS's own header comment mentions "<table>" and
#: "lr-editorial-note" as documentation, which would otherwise make every page look like it has
#: a table or an editorial note by construction, regardless of its actual content.
_CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)

_TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

#: CommonMark plus tables and strikethrough, verified against all eleven Markdown deliverables.
#:
#: `html=False` is the one departure from the bare "commonmark" preset, and it is deliberate.
#: CommonMark passes raw HTML through untouched, so a literal `<script>` in a deliverable would
#: render as a live script tag — breaking `REQ-027` R08's self-containment guarantee, on a page
#: generated from files this module trusts completely. No deliverable contains raw HTML today,
#: so escaping instead of passing through changes nothing in the rendered output; it means a
#: deliverable that grew one later would show it as text rather than execute it.
_MARKDOWN_IT = (
    MarkdownIt("commonmark", {"html": False}).enable("table").enable("strikethrough")
)


def load_template(name: str) -> str:
    """A template's text, by filename alone.

    `name` ending in `.css` is read from `templates/styles/` with every `/* ... */` comment
    stripped (it is inlined as a substitution value, never filled itself, so its rules are what
    matters -- not its prose). Anything else is read from `templates/html/` with its leading
    `<!-- token contract -->` doc comment stripped, so that comment's own literal `{{TOKEN}}`
    mentions cannot be corrupted by `fill()`.
    """
    if name.endswith(".css"):
        raw = (TEMPLATES_STYLES / name).read_text(encoding="utf-8")
        return _CSS_COMMENT.sub("", raw)
    text = (TEMPLATES_HTML / name).read_text(encoding="utf-8")
    return _LEADING_HTML_COMMENT.sub("", text, count=1)


def fill(template: str, tokens: dict[str, str]) -> str:
    """Plain `{{TOKEN}}` string substitution, strict in both directions.

    Raises `ValueError` if `tokens` supplies a key the template does not declare (a token the
    template writer renamed or dropped, caught immediately rather than silently ignored) and
    raises `ValueError` if the template declares a `{{TOKEN}}` no value was supplied for (a token
    the caller forgot to fill) — the two failure modes a half-filled page could hide.

    Both checks compare *placeholder names*, found in `template` before any substitution runs,
    against the keys of `tokens` — never by re-scanning the substituted output for a stray `{{`.
    A substituted *value* is free to contain literal `{{...}}` text of its own (before the CSS
    comment strip in `load_template()`, `templates/styles/lit-report.css`'s own header comment
    mentioned `{{INLINE_STYLES}}` as documentation, exactly as `templates/styles/overview.css`'s
    does) without that being mistaken for an unfilled placeholder in `template` itself.

    Substitution is a **single pass over the original template**, not a loop of `str.replace`
    over a growing result. A loop is order-dependent: a value substituted early that happens to
    contain a later token's `{{TOKEN}}` shape would have that shape replaced too, silently
    corrupting the value with no error raised, because the checks above look at `template` and
    never re-scan the output. Rendered Markdown is a substitution value here, so any deliverable
    that ever contained literal `{{FOOTER}}`-shaped text would hit exactly that. No deliverable
    does today; a single pass means it would not matter if one did.
    """
    declared = set(_TOKEN_RE.findall(template))
    supplied = set(tokens)
    unknown = supplied - declared
    if unknown:
        raise ValueError(
            f"fill(): token(s) not present in template: {', '.join(sorted(unknown))}"
        )
    unfilled = declared - supplied
    if unfilled:
        raise ValueError(f"fill(): unfilled token(s) remain: {', '.join(sorted(unfilled))}")
    rendered = _TOKEN_RE.sub(lambda match: tokens[match.group(1)], template)
    return rendered


def render_markdown(text: str) -> str:
    """One deliverable's Markdown source, rendered to HTML.

    `MarkdownIt("commonmark").enable("table").enable("strikethrough")` — verified against all
    eleven Markdown deliverables, `05`/`06`'s fenced-YAML hard cases included. Do not substitute a
    different preset without re-verifying against the whole corpus (dispatched hard constraint 1).
    """
    rendered: str = _MARKDOWN_IT.render(text)
    return rendered


def _output_path(filename: str) -> str:
    """The relative HTML path a deliverable's own filename renders to, e.g.

    "05_critical_collisions.md" -> "05_critical_collisions.html".
    """
    return f"{Path(filename).stem}.html"


def _title_from_slug(slug: str) -> str:
    """A deliverable's slug as sentence-case display prose, e.g. "critical_collisions" ->
    "Critical collisions"."""
    return slug.replace("_", " ").capitalize()


def _page_title(entry: dict[str, Any]) -> str:
    title = _title_from_slug(entry["slug"])
    return html.escape(f"{entry['number']} {title} — {SITE_TITLE}")


def _render_nav(deliverables: list[dict[str, Any]], active_href: str) -> str:
    """The sidebar `<li>` list every deliverable page and the entry page share.

    Every deliverable links directly to every other, so any deliverable is one click from any
    other and at most one click from the entry page — satisfying R01's two-click bound with room
    to spare.
    """
    items = []
    for entry in deliverables:
        href = _output_path(entry["filename"])
        classes = "lr__nav-link"
        if href == active_href:
            classes += " lr__nav-link--active"
        items.append(
            f'<li><a class="{classes}" href="{html.escape(href)}">'
            f"{html.escape(entry['filename'])}</a></li>"
        )
    return "".join(items)


def _render_breadcrumb(filename: str) -> str:
    return (
        '<a href="index.html">Report</a>'
        '<span class="lr__breadcrumb-sep">/</span>'
        f"{html.escape(filename)}"
    )


def _render_source_meta(entry: dict[str, Any]) -> str:
    parts = [f'<span>{entry["bytes"]:,} bytes</span>']
    if entry["format"] == "md":
        parts.append(f'<span>{entry["line_count"]:,} lines</span>')
    digest = html.escape(entry["sha256"])
    parts.append(f'<span><code>sha256:{digest[:12]}&hellip;</code></span>')
    return "".join(parts)


def _render_footer(filename: str | None) -> str:
    source = (
        f"research/literature-review/{filename}" if filename else "research/literature-review/"
    )
    escaped = html.escape(source)
    return (
        f"Rendered by <code>tools/lit_report_render.py</code> from <code>{escaped}</code>. "
        "No figure on this page is computed at render time (REQ-027 R05)."
    )


def _editorial_note_05(measured_collision_sections: int) -> str:
    """The one, narrow editorial note the 2026-09-22 owner ruling authorizes.

    `05_critical_collisions.md`'s own preamble says the file covers "24 rows"; the measured
    section count is `data["counts"]["collision_sections"]`, passed in here rather than a literal
    — the source file is never corrected, only annotated in the rendered output.
    """
    return (
        '<div class="lr-editorial-note">'
        f"<p>This file&rsquo;s own preamble states {STALE_05_PREAMBLE_ROW_COUNT} rows. "
        f"The measured collision-section count is <strong>{measured_collision_sections}</strong>, "
        "read from <code>04_evidence_matrix.csv</code>&rsquo;s "
        "<code>critical_collision: yes</code> rows. The source file is not corrected; this note "
        "records the discrepancy.</p>"
        "</div>"
    )


def _csv_placeholder(table: dict[str, Any]) -> str:
    """The three CSV deliverables' placeholder body for this phase.

    `phase-lrr-03` replaces this CONTENT with the interactive, sortable, free-text-filterable
    table `REQ-027` R03 requires (and, for the matrix, column visibility). Until then this states
    the table's column list and row count, both read from the extractor's own `tables` entry —
    nothing here is computed from the CSV directly.
    """
    columns = "".join(f"<li><code>{html.escape(c)}</code></li>" for c in table["columns"])
    return (
        "<!-- phase-lrr-03: replace this placeholder body with the interactive, sortable, "
        "free-text-filterable table (REQ-027 R03). The matrix view additionally needs "
        "column-visibility toggles. -->\n"
        "<p>This CSV deliverable becomes a browsable table in a later phase "
        f"(<code>phase-lrr-03</code>). For now: <strong>{table['row_count']:,}</strong> rows "
        f"&times; <strong>{table['column_count']}</strong> columns.</p>"
        f'<ul class="lr-csv-columns">{columns}</ul>'
    )


def _render_counts(counts: dict[str, Any], tables: dict[str, dict[str, Any]]) -> str:
    """The entry page's `{{COUNTS}}` block — every figure copied from `data["counts"]`."""
    parts = [
        "<p>"
        f"<strong>{counts['deliverables']}</strong> deliverables "
        f"(<strong>{counts['deliverables_markdown']}</strong> Markdown, "
        f"<strong>{counts['deliverables_csv']}</strong> CSV)."
        "</p>",
        '<ul class="lr__counts-list">',
    ]
    for key in sorted(tables):
        table = tables[key]
        parts.append(
            f"<li>{html.escape(table['filename'])}: "
            f"<strong>{table['row_count']:,}</strong> rows &times; "
            f"<strong>{table['column_count']}</strong> columns</li>"
        )
    verdicts = counts["collision_second_review"]
    parts.append(
        f"<li><strong>{counts['collision_sections']}</strong> critical-collision sections "
        f"(<strong>{verdicts['disputed']}</strong> disputed, "
        f"<strong>{verdicts['confirmed']}</strong> confirmed on independent second review)</li>"
    )
    parts.append(f"<li><strong>{counts['hypothesis_blocks']}</strong> hypothesis blocks</li>")
    parts.append("</ul>")
    return "".join(parts)


def _render_framing(counts: dict[str, Any]) -> str:
    """The entry page's `{{FRAMING}}` block — `REQ-027` R06's and R07's posture, stated plainly.

    The memo statement is quoted from `research/literature-review/CLAUDE.md` section 18. The
    disputed/total collision counts are `data["counts"]["collision_second_review"]`, never a
    literal. The duplicate-discovery-rate trend is the one deliberate exception to "every figure
    comes from data['counts']" this module makes — see the module docstring's explanation of why
    (the extractor carries no duplicate-rate figure, and the third data point is recorded only in
    `docs/03-sessions/`, outside the corpus the extractor reads).
    """
    verdicts = counts["collision_second_review"]
    return (
        "<p>This report is a <strong>first research memo</strong>, not a final novelty claim "
        "(<code>research/literature-review/CLAUDE.md</code> &sect;18: &ldquo;This produces a "
        "first research memo. It does not establish final novelty.&rdquo;).</p>"
        "<p><strong>Saturation was measured and is explicitly not demonstrated.</strong> The "
        "campaign&rsquo;s duplicate-discovery rate fell across three measurement points &mdash; "
        "20.0% (<code>phase-lit-06</code>) &rarr; 15.0% (<code>phase-lit-08</code>) &rarr; "
        "6.4&ndash;7.7% (<code>phase-lit-09</code>) &mdash; a trend toward more new material "
        "being found, not toward exhaustion. No page in this report asserts the saturation stop "
        "condition holds, and the verdict <code>NOVEL</code> is not available to any hypothesis "
        "in this campaign.</p>"
        "<p class=\"lr-provenance\">Provenance of the three figures: 20.0% and 15.0% are stated "
        "in the campaign deliverables this report renders. <strong>6.4&ndash;7.7% is not.</strong> "
        "It is recorded only in the campaign&rsquo;s session records "
        "<code>SESS-2026-09-19-08</code> and <code>SESS-2026-09-20-02</code>, outside the corpus "
        "this report is generated from, and is reproduced here as a cited figure rather than a "
        "measured one (<code>REQ-027</code> R06&rsquo;s stated exception to R05).</p>"
        f"<p>Of the <strong>{counts['collision_sections']}</strong> critical collisions, "
        f"<strong>{verdicts['disputed']}</strong> are recorded <code>disputed</code> on "
        "independent second review; per check-in ruling 1, no score or flag was changed on "
        "review.</p>"
    )


def _render_deliverable_index(
    deliverables: list[dict[str, Any]], tables: dict[str, dict[str, Any]]
) -> str:
    """The entry page's `{{DELIVERABLE_INDEX}}` — every deliverable, one click away."""
    table_by_filename = {table["filename"]: table for table in tables.values()}
    items = []
    for entry in deliverables:
        href = _output_path(entry["filename"])
        if entry["format"] == "md":
            description = f"{entry['line_count']:,} lines"
        else:
            table = table_by_filename[entry["filename"]]
            description = f"{table['row_count']:,} rows &times; {table['column_count']} columns"
        items.append(
            '<li class="lr__index-item">'
            f'<a href="{html.escape(href)}">{html.escape(entry["filename"])}</a>'
            f"<p>{description}</p>"
            "</li>"
        )
    return "".join(items)


def render_report(data: dict[str, Any]) -> dict[str, str]:
    """The full fifteen-page mapping: `index.html` plus one page per deliverable.

    A pure function of `data` (from `tools.lit_report_extract.extract()`) and the on-disk
    `templates/html/lit-report-*.html` + `templates/styles/lit-report.css` family. No figure here
    is computed from the corpus; every count comes from `data["counts"]` or from the
    `deliverables`/`tables` entries the extractor already measured.
    """
    page_template = load_template("lit-report-page.html")
    index_template = load_template("lit-report-index.html")
    css = load_template("lit-report.css")

    deliverables: list[dict[str, Any]] = data["deliverables"]
    tables: dict[str, dict[str, Any]] = data["tables"]
    counts: dict[str, Any] = data["counts"]
    table_by_filename = {table["filename"]: table for table in tables.values()}

    pages: dict[str, str] = {}
    for entry in deliverables:
        href = _output_path(entry["filename"])

        editorial_notes = ""
        if entry["format"] == "md":
            content = render_markdown(entry["markdown"])
            if entry["filename"] == "05_critical_collisions.md":
                editorial_notes = _editorial_note_05(counts["collision_sections"])
        else:
            content = _csv_placeholder(table_by_filename[entry["filename"]])

        pages[href] = fill(
            page_template,
            {
                "PAGE_TITLE": _page_title(entry),
                "INLINE_STYLES": css,
                "SITE_TITLE": html.escape(SITE_TITLE),
                "BREADCRUMB": _render_breadcrumb(entry["filename"]),
                "NAV": _render_nav(deliverables, href),
                "SOURCE_FILENAME": html.escape(entry["filename"]),
                "SOURCE_META": _render_source_meta(entry),
                "EDITORIAL_NOTES": editorial_notes,
                "CONTENT": content,
                "FOOTER": _render_footer(entry["filename"]),
            },
        )

    pages["index.html"] = fill(
        index_template,
        {
            "PAGE_TITLE": html.escape(SITE_TITLE),
            "INLINE_STYLES": css,
            "SITE_TITLE": html.escape(SITE_TITLE),
            "FRAMING": _render_framing(counts),
            "COUNTS": _render_counts(counts, tables),
            "DELIVERABLE_INDEX": _render_deliverable_index(deliverables, tables),
            "FOOTER": _render_footer(None),
        },
    )

    return pages
