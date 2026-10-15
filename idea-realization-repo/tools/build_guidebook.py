#!/usr/bin/env python3
"""Generate the developer guidebook, `docs/guidebook.html`, from the repository's own documents.

`tools/guidebook.yaml` lists the chapters in order and, for each, the documents (or a heading
range of a document) it is built from. This script converts that Markdown into one
self-contained HTML page styled with the ui-kit bundle (`ui-kit/dist/ui.css`, inlined), with a
table of contents and a Sources appendix that gives each input file's SHA-256, so a stale page is
visible. The page carries no script and makes no request.

The Markdown converter covers the subset the documents use: ATX headings, paragraphs, bullet and
ordered lists (nested, tight and loose), fenced code, tables, blockquotes, rules, and inline code,
bold, italic, links and autolinks. Every text node is escaped. A construct outside that subset
(raw HTML, images, setext headings, indented code, reference links) is rendered as visible text
or code and listed as a warning; nothing is dropped silently.

Links: a relative Markdown link to a document the page includes from its start becomes an in-page
link; any other relative link is shown as its text followed by the repository path. An inline
code span that is exactly such a document's path or its front-matter code (`OPS-004`) also links
to it in the page.

Determinism: no clock, environment or git state is read; chapters and sources keep manifest
order; output is LF-terminated UTF-8.

    uv run python tools/build_guidebook.py            # rewrite docs/guidebook.html
    uv run python tools/build_guidebook.py --check    # exit 1 if it is stale
    uv run python tools/build_guidebook.py --strict   # exit 1 if any conversion warning
"""

from __future__ import annotations

import argparse
import hashlib
import html
import posixpath
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = Path("tools") / "guidebook.yaml"
CSS = Path("ui-kit") / "dist" / "ui.css"
GENERATOR = "tools/build_guidebook.py"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


class GuidebookError(Exception):
    """A manifest or source problem that stops the build."""


# ---------------------------------------------------------------- manifest


@dataclass(frozen=True)
class SourceSpec:
    path: str
    start_at: str | None = None
    stop_before: str | None = None


@dataclass(frozen=True)
class Chapter:
    id: str
    title: str
    intro: str
    sources: tuple[SourceSpec, ...]


@dataclass(frozen=True)
class KnownIssue:
    id: str
    severity: str
    text: str


@dataclass(frozen=True)
class KnownIssues:
    as_of: str
    source: str
    items: tuple[KnownIssue, ...]


@dataclass(frozen=True)
class Manifest:
    title: str
    output: str
    lede: str
    chapters: tuple[Chapter, ...]
    known_issues: KnownIssues | None = None


SEVERITIES = {"blocker": "err", "major": "warn", "minor": "info"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def _str(value: object, where: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise GuidebookError(f"{where} must be a non-empty string")
    return value.strip()


def _keys(data: dict[str, Any], allowed: set[str], where: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise GuidebookError(f"{where}: unknown key(s) {', '.join(unknown)}")


def load_manifest(path: Path) -> Manifest:
    if not path.is_file():
        raise GuidebookError(f"manifest {path} does not exist")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise GuidebookError(f"manifest {path} is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise GuidebookError(f"manifest {path} must be a mapping")
    manifest_keys = {"schema_version", "title", "output", "lede", "chapters", "known_issues"}
    _keys(data, manifest_keys, "manifest")
    if data.get("schema_version") != 1:
        raise GuidebookError("manifest schema_version must be 1")
    chapters_raw = data.get("chapters")
    if not isinstance(chapters_raw, list) or not chapters_raw:
        raise GuidebookError("manifest chapters must be a non-empty list")
    chapters: list[Chapter] = []
    seen: set[str] = set()
    for n, raw in enumerate(chapters_raw, 1):
        where = f"chapter {n}"
        if not isinstance(raw, dict):
            raise GuidebookError(f"{where} must be a mapping")
        _keys(raw, {"id", "title", "intro", "sources"}, where)
        cid = _str(raw.get("id"), f"{where} id")
        assert cid is not None
        if not ID_RE.match(cid):
            raise GuidebookError(f"{where} id {cid!r} must be lower-case letters, digits, hyphens")
        if cid in seen:
            raise GuidebookError(f"{where} id {cid!r} is used twice")
        seen.add(cid)
        sources_raw = raw.get("sources")
        if not isinstance(sources_raw, list) or not sources_raw:
            raise GuidebookError(f"chapter {cid}: sources must be a non-empty list")
        sources: list[SourceSpec] = []
        for m, src in enumerate(sources_raw, 1):
            swhere = f"chapter {cid} source {m}"
            if not isinstance(src, dict):
                raise GuidebookError(f"{swhere} must be a mapping")
            _keys(src, {"path", "start_at", "stop_before"}, swhere)
            spath = _str(src.get("path"), f"{swhere} path")
            assert spath is not None
            sources.append(
                SourceSpec(
                    spath,
                    _str(src.get("start_at"), f"{swhere} start_at", optional=True),
                    _str(src.get("stop_before"), f"{swhere} stop_before", optional=True),
                )
            )
        chapters.append(
            Chapter(
                cid,
                _str(raw.get("title"), f"{where} title") or "",
                _str(raw.get("intro"), f"{where} intro") or "",
                tuple(sources),
            )
        )
    return Manifest(
        _str(data.get("title"), "manifest title") or "",
        _str(data.get("output"), "manifest output") or "",
        _str(data.get("lede"), "manifest lede") or "",
        tuple(chapters),
        load_known_issues(data.get("known_issues")),
    )


def load_known_issues(raw: object) -> KnownIssues | None:
    """The optional dated list of known issues shown under the page header."""
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise GuidebookError("known_issues must be a mapping")
    _keys(raw, {"as_of", "source", "items"}, "known_issues")
    as_of_raw = raw.get("as_of")
    as_of = _str(None if as_of_raw is None else str(as_of_raw), "known_issues as_of") or ""
    if not DATE_RE.match(as_of):
        raise GuidebookError("known_issues as_of must be a YYYY-MM-DD date")
    source = _str(raw.get("source"), "known_issues source") or ""
    items_raw = raw.get("items")
    if not isinstance(items_raw, list) or not items_raw:
        raise GuidebookError("known_issues items must be a non-empty list")
    items: list[KnownIssue] = []
    for n, item in enumerate(items_raw, 1):
        where = f"known_issues item {n}"
        if not isinstance(item, dict):
            raise GuidebookError(f"{where} must be a mapping")
        _keys(item, {"id", "severity", "text"}, where)
        severity = _str(item.get("severity"), f"{where} severity") or ""
        if severity not in SEVERITIES:
            raise GuidebookError(f"{where} severity must be one of {', '.join(SEVERITIES)}")
        items.append(
            KnownIssue(
                _str(item.get("id"), f"{where} id") or "",
                severity,
                _str(item.get("text"), f"{where} text") or "",
            )
        )
    return KnownIssues(as_of, source, tuple(items))


# ---------------------------------------------------------------- source files

Line = tuple[int, str]  # (1-based line number in the file, text)

FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
ATX_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")


@dataclass(frozen=True)
class SourceFile:
    path: str  # repository-relative, POSIX
    raw: bytes
    title: str
    code: str | None
    body: tuple[Line, ...]  # front matter removed

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()

    @property
    def label(self) -> str:
        return f"{self.title} ({self.code})" if self.code else self.title


def heading_lines(body: Sequence[Line]) -> list[tuple[int, int, str]]:
    """(index into body, level, raw heading text) for each ATX heading outside fenced code."""
    found: list[tuple[int, int, str]] = []
    fence: str | None = None
    for i, (_, text) in enumerate(body):
        m = FENCE_RE.match(text)
        if fence is not None:
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence):
                if not m.group(3).strip():
                    fence = None
            continue
        if m and not (m.group(2)[0] == "`" and "`" in m.group(3)):
            fence = m.group(2)
            continue
        h = ATX_RE.match(text)
        if h:
            found.append((i, len(h.group(1)), (h.group(2) or "").strip()))
    return found


def read_source(root: Path, rel: str) -> SourceFile:
    path = root / rel
    if not path.is_file():
        raise GuidebookError(f"source {rel} does not exist")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GuidebookError(f"source {rel} is not UTF-8: {exc}") from exc
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    numbered = [(n, line.expandtabs(4)) for n, line in enumerate(lines, 1)]
    front: dict[str, Any] = {}
    if numbered and numbered[0][1].strip() == "---":
        end = next((i for i in range(1, len(numbered)) if numbered[i][1].strip() == "---"), None)
        if end is None:
            raise GuidebookError(f"source {rel}: front matter is not closed")
        try:
            loaded = yaml.safe_load("\n".join(t for _, t in numbered[1:end]))
        except yaml.YAMLError as exc:
            raise GuidebookError(f"source {rel}: front matter is not valid YAML: {exc}") from exc
        front = loaded if isinstance(loaded, dict) else {}
        numbered = numbered[end + 1 :]
    title = front.get("title") if isinstance(front.get("title"), str) else None
    if title is None:
        h1 = next((t for _, lvl, t in heading_lines(numbered) if lvl == 1), None)
        title = plain_text(h1) if h1 else rel
    code = front.get("code") if isinstance(front.get("code"), str) else None
    return SourceFile(rel, raw, str(title), code, tuple(numbered))


def find_heading(src: SourceFile, text: str, key: str, chapter: str) -> int:
    hits = [i for i, _, t in heading_lines(src.body) if t == text]
    if not hits:
        raise GuidebookError(
            f"chapter {chapter}: {key} heading {text!r} not found in {src.path}"
        )
    if len(hits) > 1:
        raise GuidebookError(
            f"chapter {chapter}: {key} heading {text!r} matches {len(hits)} headings in "
            f"{src.path}"
        )
    return hits[0]


def extract(src: SourceFile, spec: SourceSpec, chapter: str) -> tuple[Line, ...]:
    start = find_heading(src, spec.start_at, "start_at", chapter) if spec.start_at else 0
    stop = (
        find_heading(src, spec.stop_before, "stop_before", chapter)
        if spec.stop_before
        else len(src.body)
    )
    if stop <= start:
        raise GuidebookError(
            f"chapter {chapter}: in {src.path}, stop_before {spec.stop_before!r} does not come "
            f"after start_at {spec.start_at!r}"
        )
    return src.body[start:stop]


# ---------------------------------------------------------------- Markdown blocks


@dataclass
class Heading:
    level: int
    text: str
    line: int
    id: str = ""


@dataclass
class Paragraph:
    text: str
    line: int


@dataclass
class CodeBlock:
    info: str
    text: str


@dataclass
class ListBlock:
    ordered: bool
    start: int
    items: list[list[Block]]
    loose: bool


@dataclass
class Table:
    header: list[str]
    aligns: list[str]
    rows: list[list[str]]
    line: int


@dataclass
class Quote:
    children: list[Block]


@dataclass
class Rule:
    pass


@dataclass
class Unsupported:
    """Text kept verbatim (escaped) because its construct is outside the supported subset."""

    text: str


Block = Heading | Paragraph | CodeBlock | ListBlock | Table | Quote | Rule | Unsupported

BULLET_RE = re.compile(r"^( {0,3})([-*+])( +|$)(.*)$")
ORDERED_RE = re.compile(r"^( {0,3})(\d{1,9})([.)])( +|$)(.*)$")
RULE_RE = re.compile(r"^ {0,3}([-*_])(?: *\1){2,} *$")
DELIM_RE = re.compile(r"^ {0,3}\|? *:?-+:? *(?:\| *:?-+:? *)*\|? *$")
QUOTE_RE = re.compile(r"^ {0,3}> ?(.*)$")
HTML_BLOCK_RE = re.compile(r"^ {0,3}<(?:!--|[A-Za-z/?!])")
REFDEF_RE = re.compile(r"^ {0,3}\[[^\]]+\]:\s")
SETEXT_RE = re.compile(r"^ {0,3}(=+|-+) *$")


def blank(text: str) -> bool:
    return not text.strip()


def indent_of(text: str) -> int:
    return len(text) - len(text.lstrip(" "))


@dataclass(frozen=True)
class Marker:
    ordered: bool
    char: str  # bullet character or ordered delimiter
    start: int
    content_indent: int
    rest: str


def list_marker(text: str) -> Marker | None:
    m = BULLET_RE.match(text)
    if m and not RULE_RE.match(text):
        lead, char, gap, rest = m.group(1), m.group(2), m.group(3), m.group(4)
        width = len(gap) if 1 <= len(gap) <= 4 else 1
        return Marker(False, char, 1, len(lead) + 1 + width, rest)
    m = ORDERED_RE.match(text)
    if m:
        lead, num, delim, gap, rest = m.groups()
        width = len(gap) if 1 <= len(gap) <= 4 else 1
        return Marker(True, delim, int(num), len(lead) + len(num) + 1 + width, rest)
    return None


def is_table_start(lines: Sequence[Line], i: int) -> bool:
    return (
        "|" in lines[i][1]
        and i + 1 < len(lines)
        and "|" in lines[i + 1][1]
        and DELIM_RE.match(lines[i + 1][1]) is not None
    )


def split_row(text: str) -> list[str]:
    s = text.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells: list[str] = []
    cur: list[str] = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if s[i] == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(s[i])
        i += 1
    cells.append("".join(cur).strip())
    return cells


class BlockParser:
    def __init__(self, path: str, warn: Callable[[str, int, str], None]) -> None:
        self.path = path
        self.warn = warn

    def interrupts(self, lines: Sequence[Line], i: int) -> bool:
        """Whether line i starts a block that ends a paragraph or a lazy continuation."""
        text = lines[i][1]
        if FENCE_RE.match(text) or ATX_RE.match(text) or RULE_RE.match(text):
            return True
        if QUOTE_RE.match(text) or is_table_start(lines, i):
            return True
        marker = list_marker(text)
        if marker and marker.rest.strip() and (not marker.ordered or marker.start == 1):
            return True
        return False

    def parse(self, lines: Sequence[Line]) -> list[Block]:
        out: list[Block] = []
        i = 0
        n = len(lines)
        prev_blank = True
        while i < n:
            ln, text = lines[i]
            if blank(text):
                i += 1
                prev_blank = True
                continue
            fence = FENCE_RE.match(text)
            if fence and not (fence.group(2)[0] == "`" and "`" in fence.group(3)):
                i = self.fenced(lines, i, fence, out)
            elif (h := ATX_RE.match(text)) is not None:
                out.append(Heading(len(h.group(1)), (h.group(2) or "").strip(), ln))
                i += 1
            elif RULE_RE.match(text):
                out.append(Rule())
                i += 1
            elif QUOTE_RE.match(text):
                body: list[Line] = []
                while i < n and (q := QUOTE_RE.match(lines[i][1])) is not None:
                    body.append((lines[i][0], q.group(1)))
                    i += 1
                out.append(Quote(self.parse(body)))
            elif is_table_start(lines, i):
                i = self.table(lines, i, out)
            elif list_marker(text) is not None:
                i = self.list_block(lines, i, out)
            elif indent_of(text) >= 4 and prev_blank:
                code: list[str] = []
                while i < n and (blank(lines[i][1]) or indent_of(lines[i][1]) >= 4):
                    code.append(lines[i][1][4:])
                    i += 1
                while code and not code[-1].strip():
                    code.pop()
                self.warn(self.path, ln, "indented code block (rendered as code)")
                out.append(CodeBlock("", "\n".join(code)))
            elif (
                HTML_BLOCK_RE.match(text) and not AUTOLINK_RE.match(text.lstrip())
            ) or REFDEF_RE.match(text):
                kind = "reference link definition" if REFDEF_RE.match(text) else "raw HTML"
                raw: list[str] = []
                while i < n and not blank(lines[i][1]):
                    raw.append(lines[i][1])
                    i += 1
                self.warn(self.path, ln, f"{kind} (rendered as text)")
                out.append(Unsupported("\n".join(raw)))
            else:
                i = self.paragraph(lines, i, out)
            prev_blank = False
        return out

    def fenced(self, lines: Sequence[Line], i: int, m: re.Match[str], out: list[Block]) -> int:
        lead, fence, info = len(m.group(1)), m.group(2), m.group(3).strip()
        body: list[str] = []
        i += 1
        closed = False
        while i < len(lines):
            text = lines[i][1]
            c = FENCE_RE.match(text)
            if c and c.group(2)[0] == fence[0] and len(c.group(2)) >= len(fence):
                if not c.group(3).strip():
                    closed = True
                    i += 1
                    break
            strip = min(lead, indent_of(text))
            body.append(text[strip:])
            i += 1
        if not closed:
            self.warn(self.path, lines[i - 1][0], "fenced code block is not closed")
        out.append(CodeBlock(info.split()[0] if info else "", "\n".join(body)))
        return i

    def table(self, lines: Sequence[Line], i: int, out: list[Block]) -> int:
        ln = lines[i][0]
        header = split_row(lines[i][1])
        aligns = []
        for cell in split_row(lines[i + 1][1]):
            c = cell.strip()
            if c.startswith(":") and c.endswith(":"):
                aligns.append("center")
            elif c.endswith(":"):
                aligns.append("right")
            else:
                aligns.append("")
        if len(aligns) != len(header):
            self.warn(self.path, ln, "table delimiter row has a different column count")
        aligns = (aligns + [""] * len(header))[: len(header)]
        rows: list[list[str]] = []
        i += 2
        while i < len(lines) and not blank(lines[i][1]) and "|" in lines[i][1]:
            cells = split_row(lines[i][1])
            if len(cells) != len(header):
                self.warn(
                    self.path,
                    lines[i][0],
                    f"table row has {len(cells)} cells, header has {len(header)}",
                )
            rows.append((cells + [""] * len(header))[: len(header)])
            i += 1
        out.append(Table(header, aligns, rows, ln))
        return i

    def list_block(self, lines: Sequence[Line], i: int, out: list[Block]) -> int:
        first = list_marker(lines[i][1])
        assert first is not None
        items: list[list[Block]] = []
        loose = False
        n = len(lines)
        while i < n:
            marker = list_marker(lines[i][1])
            if marker is None or marker.ordered != first.ordered or marker.char != first.char:
                break
            indent = marker.content_indent
            item: list[Line] = [(lines[i][0], marker.rest)]
            i += 1
            while i < n:
                ln, text = lines[i]
                if blank(text):
                    item.append((ln, ""))
                    i += 1
                    continue
                if indent_of(text) >= indent:
                    item.append((ln, text[indent:]))
                    i += 1
                    continue
                if (
                    item[-1][1].strip()
                    and list_marker(text) is None
                    and not self.interrupts(lines, i)
                ):
                    item.append((ln, text.strip()))  # lazy continuation of a paragraph
                    i += 1
                    continue
                break
            trailing = 0
            while item and not item[-1][1].strip():
                item.pop()
                trailing += 1
            if any(not t.strip() for _, t in item):
                loose = True
            if trailing and i < n:
                nxt = list_marker(lines[i][1])
                if nxt and nxt.ordered == first.ordered and nxt.char == first.char:
                    loose = True
            items.append(self.parse(item))
            if trailing and i < n and list_marker(lines[i][1]) is None:
                break
        out.append(ListBlock(first.ordered, first.start, items, loose))
        return i

    def paragraph(self, lines: Sequence[Line], i: int, out: list[Block]) -> int:
        ln = lines[i][0]
        text = [lines[i][1].strip()]
        i += 1
        while i < len(lines) and not blank(lines[i][1]):
            if SETEXT_RE.match(lines[i][1]) and not list_marker(lines[i][1]):
                self.warn(self.path, lines[i][0], "setext heading underline (rendered as text)")
                text.append(lines[i][1].strip())
                i += 1
                continue
            if self.interrupts(lines, i):
                break
            text.append(lines[i][1].strip())
            i += 1
        out.append(Paragraph("\n".join(text), ln))
        return i


# ---------------------------------------------------------------- inline Markdown

PUNCT = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
AUTOLINK_RE = re.compile(r"<((?:https?|mailto):[^\s<>]+)>")
INLINE_HTML_RE = re.compile(
    r"</?(?:a|b|br|code|del|details|div|em|i|img|kbd|p|pre|span|strong|sub|summary|sup|table"
    r"|td|th|tr|u)(?:\s[^<>]*)?/?>|<!--",
    re.IGNORECASE,
)


def backtick_run(text: str, i: int) -> int:
    j = i
    while j < len(text) and text[j] == "`":
        j += 1
    return j - i


def find_code_close(text: str, i: int, run: int) -> int:
    """Index of the closing backtick run of exactly `run` length after i, or -1."""
    j = i
    while j < len(text):
        if text[j] == "`":
            r = backtick_run(text, j)
            if r == run:
                return j
            j += r
        else:
            j += 1
    return -1


def skip_code(text: str, j: int) -> int:
    """If a code span starts at j, the index after it; otherwise j + 1."""
    run = backtick_run(text, j)
    close = find_code_close(text, j + run, run)
    return close + run if close >= 0 else j + run


def find_delim(text: str, start: int, delim: str) -> int:
    """Index of a closing emphasis delimiter after start, skipping code spans and escapes."""
    j = start
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "`":
            j = skip_code(text, j)
            continue
        if text.startswith(delim, j) and j > start and not text[j - 1].isspace():
            after = text[j + len(delim)] if j + len(delim) < len(text) else ""
            if len(delim) == 1 and after == delim[0]:
                j += 2  # part of a double delimiter
                continue
            if delim[0] == "_" and after.isalnum():
                j += 1
                continue
            return j
        j += 1
    return -1


def find_bracket_close(text: str, i: int) -> int:
    depth = 0
    j = i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "`":
            j = skip_code(text, j)
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return -1


LinkResolver = Callable[[str], tuple[str | None, str | None]]
CodeLinker = Callable[[str], str | None]


@dataclass
class Inline:
    """Inline renderer for one source; `resolve` maps a link target to (href, shown path)."""

    path: str
    line: int
    warn: Callable[[str, int, str], None]
    resolve: LinkResolver = field(default=lambda dest: (None, dest))
    code_link: CodeLinker = field(default=lambda code: None)

    def render(self, text: str, *, in_link: bool = False) -> str:
        out: list[str] = []
        buf: list[str] = []

        def flush() -> None:
            if buf:
                out.append(esc("".join(buf)))
                buf.clear()

        i = 0
        n = len(text)
        while i < n:
            c = text[i]
            if c == "\\" and i + 1 < n and text[i + 1] in PUNCT:
                buf.append(text[i + 1])
                i += 2
                continue
            if c == "\\" and i + 1 < n and text[i + 1] == "\n":
                flush()
                out.append("<br>")
                i += 2
                continue
            if c == "`":
                run = backtick_run(text, i)
                close = find_code_close(text, i + run, run)
                if close < 0:
                    buf.append("`" * run)
                    i += run
                    continue
                flush()
                code = text[i + run : close].replace("\n", " ")
                if len(code) > 2 and code[0] == " " and code[-1] == " " and code.strip():
                    code = code[1:-1]
                tag = f"<code>{esc(code)}</code>"
                target = None if in_link else self.code_link(code)
                out.append(f'<a href="#{esc(target)}">{tag}</a>' if target else tag)
                i = close + run
                continue
            if c == "!" and i + 1 < n and text[i + 1] == "[":
                end = self._link(text, i + 1)
                if end is not None:
                    flush()
                    close = find_bracket_close(text, i + 1)
                    self.warn(self.path, self.line, "image (rendered as its alt text)")
                    out.append(self.render(text[i + 2 : close], in_link=True))
                    i = end
                    continue
            if c == "[" and not in_link:
                end = self._link(text, i)
                if end is not None:
                    flush()
                    close = find_bracket_close(text, i)
                    label = self.render(text[i + 1 : close], in_link=True)
                    parts = text[close + 2 : end - 1].split()
                    dest = parts[0] if parts else ""
                    href, shown = self.resolve(dest)
                    if href is not None:
                        out.append(f'<a href="{esc(href)}">{label}</a>')
                    else:
                        out.append(f"{label} (<code>{esc(shown or dest)}</code>)")
                    i = end
                    continue
            if c == "<":
                m = AUTOLINK_RE.match(text, i)
                if m and not in_link:
                    flush()
                    url = m.group(1)
                    out.append(f'<a href="{esc(url)}">{esc(url)}</a>')
                    i = m.end()
                    continue
                if INLINE_HTML_RE.match(text, i):
                    self.warn(self.path, self.line, "inline HTML (rendered as text)")
            if c in "*_":
                double = text.startswith(c * 2, i)
                delim = c * 2 if double else c
                start = i + len(delim)
                before = text[i - 1] if i > 0 else ""
                opens = start < n and not text[start].isspace()
                if c == "_" and before.isalnum():
                    opens = False
                if opens:
                    close = find_delim(text, start, delim)
                    if close > start:
                        flush()
                        inner = self.render(text[start:close], in_link=in_link)
                        tag = "strong" if double else "em"
                        out.append(f"<{tag}>{inner}</{tag}>")
                        i = close + len(delim)
                        continue
                buf.append(delim)
                i += len(delim)
                continue
            buf.append(c)
            i += 1
        flush()
        return "".join(out)

    @staticmethod
    def _link(text: str, i: int) -> int | None:
        """End index (after ')') of an inline link whose '[' is at i, or None."""
        close = find_bracket_close(text, i)
        if close < 0 or close + 1 >= len(text) or text[close + 1] != "(":
            return None
        depth = 0
        j = close + 1
        while j < len(text):
            if text[j] == "\\":
                j += 2
                continue
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    return j + 1
            elif text[j] == "\n":
                return None
            j += 1
        return None


def plain_text(markdown: str) -> str:
    """The visible text of an inline Markdown fragment."""
    rendered = Inline("", 0, lambda p, n, m: None).render(markdown)
    return html.unescape(re.sub(r"<[^>]+>", "", rendered))


def slugify(text: str) -> str:
    """GitHub-style heading slug: lower case, punctuation dropped, spaces to hyphens."""
    s = re.sub(r"[^\w\- ]", "", text.lower())
    return re.sub(r"-+", "-", s.replace(" ", "-")).strip("-") or "section"


# ---------------------------------------------------------------- the page model


@dataclass
class Part:
    """One source range placed in a chapter."""

    chapter: str
    spec: SourceSpec
    source: SourceFile
    blocks: list[Block]
    title_id: str | None  # id of the h3 source title, or None when it continues the last part


@dataclass
class Page:
    manifest: Manifest
    parts: list[Part]
    chapter_ids: dict[str, str]
    sources: dict[str, SourceFile]
    usage: dict[str, list[str]]  # path -> chapter titles, in order, without repeats
    file_anchor: dict[str, str]  # path -> id, for files included from their start
    code_anchor: dict[str, str]  # front-matter code -> id
    heading_anchor: dict[tuple[str, str], str]  # (path, slug) -> id
    warnings: list[str]


class Ids:
    def __init__(self) -> None:
        self.used: set[str] = set()

    def take(self, base: str) -> str:
        cand = base
        k = 2
        while cand in self.used:
            cand = f"{base}-{k}"
            k += 1
        self.used.add(cand)
        return cand


def build_page(root: Path, manifest: Manifest) -> Page:
    warnings: list[str] = []
    seen_warnings: set[str] = set()

    def warn(path: str, line: int, message: str) -> None:
        text = f"{path}:{line}: {message}"
        if text not in seen_warnings:
            seen_warnings.add(text)
            warnings.append(text)

    ids = Ids()
    for reserved in ("content", "contents", "sources"):
        ids.take(reserved)
    sources: dict[str, SourceFile] = {}
    usage: dict[str, list[str]] = {}
    parts: list[Part] = []
    chapter_ids: dict[str, str] = {}
    file_anchor: dict[str, str] = {}
    code_anchor: dict[str, str] = {}
    heading_anchor: dict[tuple[str, str], str] = {}
    for chapter in manifest.chapters:
        chapter_ids[chapter.id] = ids.take(chapter.id)
        previous: str | None = None
        for spec in chapter.sources:
            rel = posixpath.normpath(spec.path)
            if rel.startswith("../") or rel.startswith("/"):
                raise GuidebookError(
                    f"chapter {chapter.id}: source {spec.path} is outside the root"
                )
            if rel not in sources:
                sources[rel] = read_source(root, rel)
            src = sources[rel]
            lines = extract(src, spec, chapter.id)
            blocks = BlockParser(rel, warn).parse(lines)
            # The document's own h1 is replaced by the generated source title.
            blocks = [b for b in blocks if not (isinstance(b, Heading) and b.level == 1)]
            title_id = None if previous == rel else ids.take(f"{chapter.id}-{slugify(src.title)}")
            if spec.start_at is None and rel not in file_anchor:
                file_anchor[rel] = title_id or chapter_ids[chapter.id]
                if src.code and src.code not in code_anchor:
                    code_anchor[src.code] = file_anchor[rel]
            for block in walk(blocks):
                if isinstance(block, Heading):
                    slug = slugify(plain_text(block.text))
                    block.id = ids.take(f"{chapter.id}-{slug}")
                    heading_anchor.setdefault((rel, slug), block.id)
            parts.append(Part(chapter.id, spec, src, blocks, title_id))
            used = usage.setdefault(rel, [])
            if chapter.title not in used:
                used.append(chapter.title)
            previous = rel
    return Page(
        manifest,
        parts,
        chapter_ids,
        sources,
        usage,
        file_anchor,
        code_anchor,
        heading_anchor,
        warnings,
    )


def walk(blocks: Sequence[Block]) -> list[Block]:
    out: list[Block] = []
    for b in blocks:
        out.append(b)
        if isinstance(b, ListBlock):
            for item in b.items:
                out.extend(walk(item))
        elif isinstance(b, Quote):
            out.extend(walk(b.children))
    return out


# ---------------------------------------------------------------- rendering


class Renderer:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.warnings = page.warnings
        self.seen = set(page.warnings)

    def warn(self, path: str, line: int, message: str) -> None:
        text = f"{path}:{line}: {message}"
        if text not in self.seen:
            self.seen.add(text)
            self.warnings.append(text)

    def inline_for(self, path: str, line: int, *, links: bool = True) -> Inline:
        page = self.page

        def resolve(dest: str) -> tuple[str | None, str | None]:
            if re.match(r"^(?:https?|mailto):", dest):
                return dest, None
            target, _, frag = dest.partition("#")
            rel = path
            if target:
                rel = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
            if frag and (rel, slugify(frag)) in page.heading_anchor:
                return f"#{page.heading_anchor[(rel, slugify(frag))]}", None
            if rel in page.file_anchor:
                return f"#{page.file_anchor[rel]}", None
            return None, rel + (f"#{frag}" if frag else "")

        def code_link(code: str) -> str | None:
            if not links:
                return None
            return page.file_anchor.get(code) or page.code_anchor.get(code)

        return Inline(path, line, self.warn, resolve, code_link)

    def blocks(self, path: str, blocks: Sequence[Block], *, tight: bool = False) -> str:
        return "\n".join(self.block(path, b, tight=tight) for b in blocks)

    def block(self, path: str, b: Block, *, tight: bool = False) -> str:
        if isinstance(b, Heading):
            level = min(6, b.level + 2)
            inner = self.inline_for(path, b.line, links=False).render(b.text)
            return f'<h{level} id="{esc(b.id)}">{inner}</h{level}>'
        if isinstance(b, Paragraph):
            inner = self.inline_for(path, b.line).render(b.text)
            return inner if tight else f"<p>{inner}</p>"
        if isinstance(b, CodeBlock):
            lang = f' data-lang="{esc(b.info)}"' if b.info else ""
            return f"<pre{lang}><code>{esc(b.text)}</code></pre>"
        if isinstance(b, ListBlock):
            tag = "ol" if b.ordered else "ul"
            start = f' start="{b.start}"' if b.ordered and b.start != 1 else ""
            items = "\n".join(
                f"<li>{self.blocks(path, item, tight=not b.loose)}</li>" for item in b.items
            )
            return f"<{tag}{start}>\n{items}\n</{tag}>"
        if isinstance(b, Table):
            r = self.inline_for(path, b.line)

            def align(k: int) -> str:
                return f' data-align="{b.aligns[k]}"' if b.aligns[k] else ""

            head = "".join(
                f'<th scope="col"{align(k)}>{r.render(cell)}</th>'
                for k, cell in enumerate(b.header)
            )
            body = "\n".join(
                "<tr>"
                + "".join(f"<td{align(k)}>{r.render(cell)}</td>" for k, cell in enumerate(row))
                + "</tr>"
                for row in b.rows
            )
            return (
                '<div class="ui-table-wrap"><table class="ui-table">'
                f"<thead><tr>{head}</tr></thead>\n<tbody>\n{body}\n</tbody></table></div>"
            )
        if isinstance(b, Quote):
            return f'<blockquote class="gb-quote">\n{self.blocks(path, b.children)}\n</blockquote>'
        if isinstance(b, Rule):
            return "<hr>"
        return f'<pre class="gb-unsupported"><code>{esc(b.text)}</code></pre>'

    def part(self, part: Part) -> str:
        src = part.source
        spec = part.spec
        rng = []
        if spec.start_at:
            rng.append(f"from “{esc(plain_text(spec.start_at))}”")
        if spec.stop_before:
            rng.append(f"up to “{esc(plain_text(spec.stop_before))}”")
        where = (", " + " ".join(rng)) if rng else ", whole document"
        meta = (
            '<p class="gb-source__meta"><span class="ui-pill">Source</span> '
            f"<code>{esc(src.path)}</code><span>{where}</span></p>"
        )
        title = (
            f'<h3 id="{esc(part.title_id)}">{esc(src.label)}</h3>\n' if part.title_id else ""
        )
        body = self.blocks(src.path, part.blocks)
        return (
            f'<div class="gb-source">\n{title}{meta}\n'
            f'<div class="ui-prose gb-prose">\n{body}\n</div>\n</div>'
        )

    def known_issues(self, issues: KnownIssues | None) -> str:
        if issues is None:
            return ""
        inline = self.inline_for(MANIFEST.as_posix(), 0)
        rows = "\n".join(
            f'<li><span class="ui-pill" data-status="{SEVERITIES[i.severity]}">'
            f'<span class="ui-pill__dot"></span>{esc(i.severity)} {esc(i.id)}</span> '
            f"{inline.render(i.text)}</li>"
            for i in issues.items
        )
        return (
            '<section class="ui-card ui-card--accent gb-issues" aria-labelledby="known-issues">\n'
            f'<h2 class="ui-card__title" id="known-issues">Known issues as of {esc(issues.as_of)}'
            "</h2>\n"
            f'<p class="ui-card__meta">From {esc(issues.source)}. Each item is removed when its '
            "fix merges and this page is regenerated.</p>\n"
            f'<ul class="gb-issues__list">\n{rows}\n</ul>\n</section>'
        )

    def toc(self) -> str:
        page = self.page
        items = []
        for chapter in page.manifest.chapters:
            subs = [
                f'<li><a href="#{esc(p.title_id)}">{esc(p.source.label)}</a></li>'
                for p in page.parts
                if p.chapter == chapter.id and p.title_id
            ]
            sub = f'\n<ol class="gb-toc__sub">{"".join(subs)}</ol>' if subs else ""
            items.append(
                f'<li><a href="#{esc(page.chapter_ids[chapter.id])}">{esc(chapter.title)}</a>'
                f"{sub}</li>"
            )
        items.append('<li><a href="#sources">Sources</a></li>')
        return (
            '<nav class="gb-toc" aria-labelledby="contents">\n'
            '<h2 class="gb-toc__title" id="contents">Contents</h2>\n'
            f'<ol class="gb-toc__list">\n{chr(10).join(items)}\n</ol>\n</nav>'
        )

    def chapter(self, chapter: Chapter) -> str:
        cid = self.page.chapter_ids[chapter.id]
        intro = self.inline_for(str(MANIFEST), 0).render(chapter.intro)
        parts = "\n".join(self.part(p) for p in self.page.parts if p.chapter == chapter.id)
        return (
            f'<section class="gb-chapter" aria-labelledby="{esc(cid)}">\n'
            f'<h2 id="{esc(cid)}">{esc(chapter.title)}</h2>\n'
            f'<p class="gb-intro">{intro}</p>\n{parts}\n</section>'
        )

    def sources(self, manifest_sha: str, css_sha: str) -> str:
        rows = []
        for path, src in self.page.sources.items():
            rows.append(
                f"<tr><td><code>{esc(path)}</code></td>"
                f"<td>{esc(', '.join(self.page.usage[path]))}</td>"
                f'<td class="ui-table__id gb-hash">{src.sha256}</td></tr>'
            )
        rows.append(
            f"<tr><td><code>{esc(MANIFEST.as_posix())}</code></td><td>The chapter list</td>"
            f'<td class="ui-table__id gb-hash">{manifest_sha}</td></tr>'
        )
        rows.append(
            f"<tr><td><code>{esc(CSS.as_posix())}</code></td><td>The page styles</td>"
            f'<td class="ui-table__id gb-hash">{css_sha}</td></tr>'
        )
        return (
            '<section class="gb-chapter" aria-labelledby="sources">\n'
            '<h2 id="sources">Sources</h2>\n'
            '<p class="gb-intro">Each file this page was built from, with the SHA-256 of its '
            "content at the time the page was generated. If a file's hash no longer matches, "
            "the page is stale: regenerate it with <code>uv run python "
            f"{GENERATOR}</code>.</p>\n"
            '<div class="ui-table-wrap"><table class="ui-table">'
            '<thead><tr><th scope="col">File</th><th scope="col">Used in</th>'
            '<th scope="col">SHA-256</th></tr></thead>\n<tbody>\n'
            f"{chr(10).join(rows)}\n</tbody></table></div>\n</section>"
        )


PAGE_CSS = """
.gb-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--ui-space-7);
  align-items: start;
}
.gb-toc { font-size: var(--ui-fs-sm); line-height: var(--ui-lh-ui); }
.gb-toc__title {
  font-size: var(--ui-fs-xs);
  color: var(--ui-color-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-block-end: var(--ui-space-3);
}
.gb-toc ol { margin: 0; padding-inline-start: var(--ui-space-6); }
.gb-toc li + li { margin-block-start: var(--ui-space-2); }
.gb-toc__sub { margin-block-start: var(--ui-space-2); color: var(--ui-color-muted); }
.gb-toc__sub li + li { margin-block-start: var(--ui-space-1); }
.gb-toc a { color: var(--ui-color-text); text-decoration-line: none; }
.gb-toc__sub a { color: var(--ui-color-muted); }
.gb-toc a:hover { color: var(--ui-color-accent-hover); text-decoration-line: underline; }
@media (min-width: 64em) {
  .gb-layout { grid-template-columns: 16rem minmax(0, 1fr); }
  .gb-toc {
    position: sticky;
    inset-block-start: 0;
    max-block-size: 100vh;
    overflow-y: auto;
    padding-block: var(--ui-space-5);
    padding-inline-end: var(--ui-space-3);
    border-inline-end: 1px solid var(--ui-color-line);
  }
}
.gb-main:focus { outline: none; }
.gb-header h1 {
  font-size: var(--ui-fs-3xl);
  margin-block-end: var(--ui-space-4);
}
.gb-lede { max-inline-size: 72ch; }
.gb-issues { margin-block: var(--ui-space-6); }
.gb-issues__list { margin: var(--ui-space-3) 0 0; padding-inline-start: var(--ui-space-5); }
.gb-issues__list li + li { margin-block-start: var(--ui-space-2); }
.gb-chapter {
  margin-block-start: var(--ui-space-8);
  padding-block-start: var(--ui-space-7);
  border-block-start: 1px solid var(--ui-color-line-strong);
}
.gb-chapter > h2 { font-size: var(--ui-fs-2xl); }
.gb-intro {
  max-inline-size: 72ch;
  margin-block-start: var(--ui-space-3);
  color: var(--ui-color-muted);
}
.gb-source { margin-block-start: var(--ui-space-7); }
.gb-source > h3 { font-size: var(--ui-fs-xl); margin-block-end: var(--ui-space-3); }
.gb-source__meta {
  margin-block-end: var(--ui-space-4);
  color: var(--ui-color-muted);
  font-size: var(--ui-fs-sm);
}
.gb-prose { max-inline-size: none; }
.gb-prose > :is(p, ul, ol, blockquote, h4, h5, h6) { max-inline-size: 72ch; }
.gb-prose h4 { font-size: var(--ui-fs-lg); }
.gb-prose h5 { font-size: var(--ui-fs-lg); }
.gb-prose h6 { font-size: var(--ui-fs-md); color: var(--ui-color-muted); }
.gb-prose li > :is(ul, ol) {
  margin-block-start: var(--ui-space-2);
  padding-inline-start: var(--ui-space-6);
}
.gb-prose li > * + * { margin-block-start: var(--ui-space-3); }
.gb-prose :not(pre) > code {
  padding: 0 var(--ui-space-1);
  border-radius: var(--ui-radius-sm);
  background: var(--ui-color-surface-2);
  overflow-wrap: break-word;
}
.gb-prose pre {
  padding: var(--ui-space-4);
  border: 1px solid var(--ui-color-line);
  border-radius: var(--ui-radius-md);
  background: var(--ui-color-sunken);
  font-size: var(--ui-fs-sm);
  line-height: var(--ui-lh-ui);
}
.gb-prose pre code { font-size: inherit; }
.gb-unsupported { border-style: dashed; }
.gb-quote {
  padding: var(--ui-space-3) var(--ui-space-4);
  border-inline-start: var(--ui-space-1) solid var(--ui-color-line-strong);
  background: var(--ui-color-surface-2);
}
.gb-quote > * + * { margin-block-start: var(--ui-space-3); }
.gb-prose .ui-table td, .gb-chapter .ui-table td { vertical-align: top; }
.gb-prose .ui-table th { white-space: normal; }
.ui-table [data-align="right"] { text-align: end; }
.ui-table [data-align="center"] { text-align: center; }
.ui-table .gb-hash { white-space: normal; word-break: break-all; }
"""


def render(page: Page, css: str, manifest_sha: str, css_sha: str) -> str:
    css = css.replace("\r\n", "\n").rstrip("\n")
    r = Renderer(page)
    m = page.manifest
    chapters = "\n".join(r.chapter(c) for c in m.chapters)
    sources_html = r.sources(manifest_sha, css_sha)
    count = len(page.sources)
    return f"""<!doctype html>
<!-- GENERATED by {GENERATOR} from {MANIFEST.as_posix()} and the documents it lists.
     Do not edit by hand. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(m.title)}</title>
<style>
{css}
/* guidebook page layout */{PAGE_CSS}</style>
</head>
<body>
<a class="ui-skip-link" href="#content">Skip to the content</a>
<div class="ui-page gb-layout">
{r.toc()}
<main class="gb-main" id="content" tabindex="-1">
<header class="gb-header">
<h1>{esc(m.title)}</h1>
<p class="gb-lede">{r.inline_for(MANIFEST.as_posix(), 0).render(m.lede)}</p>
<p class="gb-intro">Built from {count} files by <code>{GENERATOR}</code>. The
<a href="#sources">Sources</a> list gives each file's hash, so a stale page can be seen.</p>
</header>
{r.known_issues(m.known_issues)}
{chapters}
{sources_html}
</main>
</div>
</body>
</html>
"""


def convert_markdown(
    text: str, path: str = "doc.md", *, included: dict[str, str] | None = None
) -> tuple[str, list[str]]:
    """Convert one Markdown text to HTML on its own, with no page around it.

    `included` maps repository paths to the in-page ids that links to them resolve to, standing
    in for the documents a guidebook would include. Returns the HTML and the warnings.
    """
    page = Page(
        Manifest("", "", "", ()), [], {}, {}, {}, dict(included or {}), {}, {}, []
    )
    blocks = BlockParser(path, Renderer(page).warn).parse(
        [(n, line.expandtabs(4)) for n, line in enumerate(text.split("\n"), 1)]
    )
    ids = Ids()
    for block in walk(blocks):
        if isinstance(block, Heading):
            block.id = ids.take(slugify(plain_text(block.text)))
    return Renderer(page).blocks(path, blocks), page.warnings


def build(root: Path, manifest_path: Path) -> tuple[str, Manifest, list[str]]:
    manifest = load_manifest(manifest_path)
    css_path = root / CSS
    if not css_path.is_file():
        raise GuidebookError(f"{CSS} is missing; run ui-kit/tools/build_css.py")
    css_raw = css_path.read_bytes()
    page = build_page(root, manifest)
    text = render(
        page,
        css_raw.decode("utf-8"),
        hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        hashlib.sha256(css_raw).hexdigest(),
    )
    return text, manifest, page.warnings


# ---------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the developer guidebook page.")
    parser.add_argument("--check", action="store_true", help="exit 1 if the output is stale")
    parser.add_argument("--strict", action="store_true", help="exit 1 on any conversion warning")
    parser.add_argument("--root", type=Path, default=None, help="repository root (default: here)")
    parser.add_argument("--manifest", type=Path, default=None, help="manifest (default: tools/)")
    parser.add_argument("--out", type=Path, default=None, help="output (default: from manifest)")
    args = parser.parse_args(argv)

    root: Path = (args.root or ROOT).resolve()
    manifest_path: Path = args.manifest or root / MANIFEST
    try:
        page, manifest, warnings = build(root, manifest_path)
    except GuidebookError as exc:
        print(f"build_guidebook: {exc}", file=sys.stderr)
        return 1
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    out: Path = args.out or root / manifest.output
    status = 1 if args.strict and warnings else 0
    if args.check:
        current = out.read_bytes().decode("utf-8") if out.is_file() else None
        if current != page:
            print(f"{out} is stale; run {GENERATOR}")
            return 1
        print(f"{out} matches its inputs")
        return status
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {out} ({len(warnings)} warning(s))")
    return status


if __name__ == "__main__":
    sys.exit(main())
