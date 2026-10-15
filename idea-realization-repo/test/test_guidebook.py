"""tools/build_guidebook.py: the developer guidebook generator and its page.

The tests build into temporary paths and never rewrite the real `docs/guidebook.html`.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_guidebook as gb  # noqa: E402

SCRIPT = ROOT / "tools" / "build_guidebook.py"
MANIFEST = ROOT / "tools" / "guidebook.yaml"
EXTERNAL = re.compile(
    r"<link\b|<script\b[^>]*\bsrc\s*=|<(?:img|iframe|source|video|audio|embed|object)\b"
    r"[^>]*\b(?:src|data)\s*=\s*[\"']?\s*(?:https?:)?//|url\(\s*[\"']?\s*(?:https?:)?//|@import",
    re.IGNORECASE,
)


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )


@pytest.fixture(scope="module")
def page() -> str:
    text, _, _ = gb.build(ROOT, MANIFEST)
    return text


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.tags: Counter[str] = Counter()
        self.html_attrs: dict[str, str | None] = {}
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags[tag] += 1
        d = dict(attrs)
        if tag == "html":
            self.html_attrs = d
        if tag == "title":
            self._in_title = True
        if d.get("id"):
            self.ids.append(str(d["id"]))
        if tag == "a" and d.get("href"):
            self.hrefs.append(str(d["href"]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def collect(text: str) -> Collector:
    c = Collector()
    c.feed(text)
    return c


def copy_inputs(dest: Path) -> Path:
    """Copy the manifest, every source it names and the stylesheet into a temporary root."""
    manifest = gb.load_manifest(MANIFEST)
    paths = {s.path for ch in manifest.chapters for s in ch.sources}
    paths |= {str(gb.MANIFEST), str(gb.CSS)}
    for rel in sorted(paths):
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dest / rel)
    return dest


# ---------------------------------------------------------------- the manifest


def test_every_manifest_source_exists_and_every_heading_resolves() -> None:
    manifest = gb.load_manifest(MANIFEST)
    assert manifest.chapters
    for chapter in manifest.chapters:
        for spec in chapter.sources:
            assert (ROOT / spec.path).is_file(), spec.path
    built = gb.build_page(ROOT, manifest)  # raises on a missing heading
    assert all(part.blocks for part in built.parts)


def test_manifest_has_the_chapters_in_order() -> None:
    titles = [c.title for c in gb.load_manifest(MANIFEST).chapters]
    assert titles[0] == "Onboarding"
    assert titles[-1] == "Day-one checklist"
    assert len(titles) == len(set(titles))


def write_manifest(root: Path, sources: str) -> Path:
    path = root / "tools" / "guidebook.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "schema_version: 1\ntitle: T\noutput: out.html\nlede: L\nchapters:\n"
        f"  - id: one\n    title: One\n    intro: I\n    sources:\n{sources}",
        encoding="utf-8",
    )
    (root / "ui-kit" / "dist").mkdir(parents=True, exist_ok=True)
    (root / "ui-kit" / "dist" / "ui.css").write_text("body { margin: 0; }\n", encoding="utf-8")
    return path


def test_a_missing_source_file_is_an_error(tmp_path: Path) -> None:
    write_manifest(tmp_path, "      - path: nowhere.md\n")
    result = run("--root", str(tmp_path))
    assert result.returncode == 1
    assert "source nowhere.md does not exist" in result.stderr
    assert not (tmp_path / "out.html").exists()


def test_a_missing_heading_is_an_error(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("# A\n\n## Real\n\ntext\n", encoding="utf-8")
    write_manifest(tmp_path, "      - path: a.md\n        start_at: Imagined\n")
    result = run("--root", str(tmp_path))
    assert result.returncode == 1
    assert "start_at heading 'Imagined' not found in a.md" in result.stderr


def test_an_ambiguous_heading_is_an_error(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("# A\n\n## Same\n\nx\n\n## Same\n\ny\n", encoding="utf-8")
    write_manifest(tmp_path, "      - path: a.md\n        stop_before: Same\n")
    result = run("--root", str(tmp_path))
    assert result.returncode == 1
    assert "matches 2 headings" in result.stderr


def test_a_heading_inside_fenced_code_is_not_a_heading(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("# A\n\n```bash\n# Comment\n```\n\n## Comment\n\nz\n")
    write_manifest(tmp_path, "      - path: a.md\n        start_at: Comment\n")
    result = run("--root", str(tmp_path))
    assert result.returncode == 0, result.stderr
    out = (tmp_path / "out.html").read_text(encoding="utf-8")
    assert ">Comment</h4>" in out and "# Comment" not in out


def test_an_unknown_manifest_key_is_an_error(tmp_path: Path) -> None:
    write_manifest(tmp_path, "      - path: a.md\n        from: X\n")
    result = run("--root", str(tmp_path))
    assert result.returncode == 1
    assert "unknown key(s) from" in result.stderr


# ---------------------------------------------------------------- determinism and staleness


def test_output_is_deterministic(tmp_path: Path) -> None:
    a, b = tmp_path / "a.html", tmp_path / "b.html"
    assert run("--out", str(a)).returncode == 0
    assert run("--out", str(b)).returncode == 0
    assert a.read_bytes() == b.read_bytes()
    assert b"\r\n" not in a.read_bytes()
    text, _, _ = gb.build(ROOT, MANIFEST)
    assert a.read_text(encoding="utf-8") == text


def test_check_reports_a_stale_output(tmp_path: Path) -> None:
    root = copy_inputs(tmp_path / "repo")
    out = root / "docs" / "guidebook.html"
    assert run("--root", str(root)).returncode == 0
    fresh = run("--root", str(root), "--check")
    assert fresh.returncode == 0, fresh.stdout + fresh.stderr

    onboarding = root / "ONBOARDING.md"
    onboarding.write_text(onboarding.read_text(encoding="utf-8") + "\nA new line.\n")
    stale = run("--root", str(root), "--check")
    assert stale.returncode == 1
    assert "is stale" in stale.stdout

    assert run("--root", str(root)).returncode == 0
    assert run("--root", str(root), "--check").returncode == 0
    out.unlink()
    assert run("--root", str(root), "--check").returncode == 1


def test_sources_appendix_lists_every_input_with_its_hash(page: str) -> None:
    manifest = gb.load_manifest(MANIFEST)
    paths = {s.path for ch in manifest.chapters for s in ch.sources}
    section = page[page.index('<h2 id="sources">') :]
    for rel in paths | {str(gb.MANIFEST), str(gb.CSS)}:
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        assert f"<code>{rel}</code>" in section, rel
        assert digest in section, rel


def test_strict_fails_on_a_conversion_warning(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("# A\n\n<div>raw</div>\n", encoding="utf-8")
    write_manifest(tmp_path, "      - path: a.md\n")
    loose = run("--root", str(tmp_path))
    assert loose.returncode == 0
    assert "a.md:3: raw HTML (rendered as text)" in loose.stderr
    assert run("--root", str(tmp_path), "--strict").returncode == 1


def test_the_real_sources_convert_without_warnings() -> None:
    _, _, warnings = gb.build(ROOT, MANIFEST)
    assert warnings == []


# ---------------------------------------------------------------- the page


def test_page_has_one_h1_a_language_and_a_title(page: str) -> None:
    c = collect(page)
    assert c.tags["h1"] == 1
    assert c.html_attrs.get("lang") == "en"
    assert c.title.strip()


def test_page_fetches_nothing_and_has_no_script(page: str) -> None:
    assert not EXTERNAL.search(page)
    assert "<script" not in page.lower()


def test_every_in_page_link_resolves(page: str) -> None:
    c = collect(page)
    ids = set(c.ids)
    internal = [h for h in c.hrefs if h.startswith("#")]
    assert internal
    missing = sorted({h for h in internal if h[1:] not in ids})
    assert missing == []
    assert all(h.startswith(("#", "http://", "https://", "mailto:")) for h in c.hrefs)


def test_every_id_is_unique(page: str) -> None:
    dupes = [i for i, n in Counter(collect(page).ids).items() if n > 1]
    assert dupes == []


def test_page_inlines_the_kit_stylesheet(page: str) -> None:
    css = (ROOT / gb.CSS).read_text(encoding="utf-8").rstrip("\n")
    assert css in page
    assert 'class="ui-page' in page and 'class="ui-prose' in page


def test_page_css_uses_tokens_not_colour_literals() -> None:
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(|\boklch\(", gb.PAGE_CSS)


def test_day_one_checklist_comes_from_onboarding(page: str) -> None:
    chapter = page[page.index('<h2 id="day-one">') : page.index('<h2 id="sources">')]
    assert "<code>ONBOARDING.md</code>" in chapter
    assert "First-day checklist" in chapter
    assert chapter.count("<li>") >= 10


# ---------------------------------------------------------------- Markdown conversion


def md(text: str, included: dict[str, str] | None = None) -> str:
    out, _ = gb.convert_markdown(text, included=included)
    return out


def test_headings_shift_below_the_chapter_and_source_titles() -> None:
    assert md("## Two `x`") == '<h4 id="two-x">Two <code>x</code></h4>'
    assert md("### Three") == '<h5 id="three">Three</h5>'
    assert md("##### Five") == '<h6 id="five">Five</h6>'


def test_paragraphs_and_inline_markup() -> None:
    out = md("One **bold** and *em* and _em2_ line\nwraps here.\n\nTwo.")
    assert out == (
        "<p>One <strong>bold</strong> and <em>em</em> and <em>em2</em> line\nwraps here.</p>\n"
        "<p>Two.</p>"
    )


def test_snake_case_and_lone_asterisks_stay_literal() -> None:
    assert md("a snake_case_name and 2 * 3") == "<p>a snake_case_name and 2 * 3</p>"


def test_script_in_text_is_escaped() -> None:
    out = md("Text <script>alert(1)</script> & more")
    assert "<script>" not in out
    assert "&lt;script&gt;alert(1)&lt;/script&gt; &amp; more" in out


def test_script_in_inline_code_is_escaped() -> None:
    assert md("Run `<script>x</script>` now") == (
        "<p>Run <code>&lt;script&gt;x&lt;/script&gt;</code> now</p>"
    )


def test_script_in_fenced_code_is_escaped() -> None:
    out = md("```html\n<script src=\"https://x\"></script>\n```")
    assert out == (
        '<pre data-lang="html"><code>&lt;script src=&quot;https://x&quot;&gt;'
        "&lt;/script&gt;</code></pre>"
    )


def test_inline_code_spans_lines_and_double_backticks() -> None:
    assert md("a `x\ny` b") == "<p>a <code>x y</code> b</p>"
    assert md("``a ` b``") == "<p><code>a ` b</code></p>"


def test_bullet_list_tight_with_nested_ordered_list() -> None:
    out = md("- one\n  1. a\n  2. b\n- two")
    assert out == "<ul>\n<li>one\n<ol>\n<li>a</li>\n<li>b</li>\n</ol></li>\n<li>two</li>\n</ul>"


def test_ordered_list_keeps_its_start_and_lazy_continuation() -> None:
    out = md("3. first\nlazy line\n4. second")
    assert out == '<ol start="3">\n<li>first\nlazy line</li>\n<li>second</li>\n</ol>'


def test_loose_list_wraps_paragraphs_and_keeps_code_in_the_item() -> None:
    out = md("1. **Step.**\n\n   ```bash\n   ls\n   ```\n\n2. Next")
    assert out == (
        '<ol>\n<li><p><strong>Step.</strong></p>\n<pre data-lang="bash"><code>ls</code></pre>'
        "</li>\n<li><p>Next</p></li>\n</ol>"
    )


def test_a_sibling_item_is_not_swallowed_by_a_nested_list() -> None:
    out = md("1. A\n   - x\n2. B")
    assert out == "<ol>\n<li>A\n<ul>\n<li>x</li>\n</ul></li>\n<li>B</li>\n</ol>"


def test_table_with_inline_code_and_escaped_pipe() -> None:
    out = md("| A | B |\n|---|--:|\n| `x` | a \\| b |")
    assert '<table class="ui-table">' in out and '<div class="ui-table-wrap">' in out
    assert '<th scope="col">A</th><th scope="col" data-align="right">B</th>' in out
    assert '<td><code>x</code></td><td data-align="right">a | b</td>' in out


def test_blockquote() -> None:
    out = md("> **Note.** One\n> two")
    assert out == (
        '<blockquote class="gb-quote">\n<p><strong>Note.</strong> One\ntwo</p>\n</blockquote>'
    )


def test_rule() -> None:
    assert md("a\n\n---\n\nb") == "<p>a</p>\n<hr>\n<p>b</p>"


def test_links_inside_and_outside_the_guidebook() -> None:
    included = {"docs/guides/OPS-001.md": "branching-ops-001"}
    out, warnings = gb.convert_markdown(
        "See [the guide](../guides/OPS-001.md), [plan](../plans/PLAN-1.md) and "
        "[site](https://example.com).",
        "docs/sessions/x.md",
        included=included,
    )
    assert '<a href="#branching-ops-001">the guide</a>' in out
    assert "plan (<code>docs/plans/PLAN-1.md</code>)" in out
    assert '<a href="https://example.com">site</a>' in out
    assert warnings == []


def test_code_span_naming_an_included_document_links_to_it() -> None:
    out = md("Read `docs/a.md` first.", included={"docs/a.md": "ch-a"})
    assert out == '<p>Read <a href="#ch-a"><code>docs/a.md</code></a> first.</p>'


def test_autolink_and_escaped_attribute_in_href() -> None:
    assert md("<https://example.com/a?b=1&c=\"2\">") == (
        '<p><a href="https://example.com/a?b=1&amp;c=&quot;2&quot;">'
        "https://example.com/a?b=1&amp;c=&quot;2&quot;</a></p>"
    )


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("<div>x</div>", "raw HTML (rendered as text)"),
        ("<!-- note -->", "raw HTML (rendered as text)"),
        ("![alt](x.png)", "image (rendered as its alt text)"),
        ("para\n\n    indented", "indented code block (rendered as code)"),
        ("Title\n=====", "setext heading underline (rendered as text)"),
        ("[x]: https://example.com", "reference link definition (rendered as text)"),
        ("a <br> b", "inline HTML (rendered as text)"),
        ("```\nnever closed", "fenced code block is not closed"),
    ],
)
def test_unsupported_constructs_are_warned_and_kept_visible(source: str, message: str) -> None:
    out, warnings = gb.convert_markdown(source, "w.md")
    assert any(message in w for w in warnings), warnings
    assert all(w.startswith("w.md:") for w in warnings)
    assert out.strip()
    assert "<div>" not in out and "<br>" not in out and "<img" not in out


def test_known_issues_render_and_validate(tmp_path: Path) -> None:
    """The dated known-issues list renders each item with its severity, and bad input is refused."""
    manifest = gb.load_manifest(MANIFEST)
    assert manifest.known_issues is not None
    html_text = (ROOT / manifest.output).read_text(encoding="utf-8")
    assert 'id="known-issues"' in html_text
    for item in manifest.known_issues.items:
        assert f"{item.severity} {item.id}</span>" in html_text
    with pytest.raises(gb.GuidebookError, match="severity"):
        gb.load_known_issues(
            {"as_of": "2026-10-15", "source": "s", "items": [{"id": "X", "severity": "odd",
                                                              "text": "t"}]}
        )
    with pytest.raises(gb.GuidebookError, match="date"):
        gb.load_known_issues({"as_of": "soon", "source": "s",
                              "items": [{"id": "X", "severity": "minor", "text": "t"}]})
    assert gb.load_known_issues(None) is None
