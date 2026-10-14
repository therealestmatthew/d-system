"""The plugin's documents state current rules, never the history behind them.

A governance document that says what a rule used to be, what incident produced it, or which
earlier rule it displaced makes the reader reconstruct the current rule. Every file under
``docs/`` is searched, case-insensitively and literally, for the words that mark that narrative.
"""

from __future__ import annotations

from pathlib import Path

from conftest import PLUGIN_ROOT

DOCS = PLUGIN_ROOT / "docs"

HISTORY_WORDS = ("incident", "until 20", "was broken", "replaces", "precedent")


def scan(root: Path) -> list[str]:
    found = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            for word in HISTORY_WORDS:
                if word in lowered:
                    found.append(f"{path.relative_to(root).as_posix()}:{number}: {word!r}")
    return found


def test_docs_carry_no_history() -> None:
    assert scan(DOCS) == []


def test_docs_directory_is_not_empty() -> None:
    assert any(p.is_file() for p in DOCS.rglob("*"))


def test_scan_catches_a_dated_rule(tmp_path: Path) -> None:
    (tmp_path / "rule.md").write_text("Claims lived on the old branch until 2026, then moved.\n")
    assert scan(tmp_path) == ["rule.md:1: 'until 20'"]


def test_scan_catches_an_incident(tmp_path: Path) -> None:
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "rule.md").write_text("Written after the Incident with the catalog.\n")
    assert scan(tmp_path) == ["nested/rule.md:1: 'incident'"]


def test_scan_catches_every_word(tmp_path: Path) -> None:
    for word in HISTORY_WORDS:
        (tmp_path / "rule.md").write_text(f"A sentence with {word} in it.\n")
        assert scan(tmp_path) == [f"rule.md:1: {word!r}"], word


def test_current_rules_pass(tmp_path: Path) -> None:
    (tmp_path / "rule.md").write_text("Every session works in its own worktree.\n")
    assert scan(tmp_path) == []
