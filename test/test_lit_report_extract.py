"""Tests for tools/lit_report_extract.py -- determinism and independent recomputation.

Two things anchor this file, following `test_overview_tools.py`'s pattern for the same reasons.

First, `REQ-027` R05: two runs against an unchanged tree must produce byte-identical output, both
as a subprocess (the way the tool is actually run) and as a direct `render()` call (the way it is
easiest to assert). The one determinism risk the `overview_*` precedent never had to carry is
`Path.glob()`, whose order is the filesystem's, not the tool's -- so it gets its own test against
a deliberately reversed glob rather than being covered only by the happy path, which would pass
on any machine whose filesystem happens to sort.

Second, every figure the tool reports is recomputed here from the files rather than compared to a
literal. `phase-lrr-01`'s acceptance cites 1200, 1154 and 67, and hardcoding those would make the
suite fail the day the corpus changes for a reason that has nothing to do with the extractor. The
counts are checked against an independent read of the same CSVs; the shape assertions -- fourteen
deliverables, 30 collisions, `H1`-`H11` -- are checked against the corpus, and the few genuinely
fixed facts (the hypothesis range, the `[0-9][0-9]_*` glob's exclusion of `CLAUDE.md`) are
asserted as the structural claims they are.

The two duplicate inventory rows and the stale inventory `status` field (idea `000308`) are known
defects in the corpus, not in the extractor. `test_known_defects_are_reported_not_repaired` pins
that the tool surfaces them and leaves them alone.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "research" / "literature-review"


def _load(name: str) -> Any:
    """Import a tools/ script by path -- tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


lit_report_extract = _load("lit_report_extract")


@pytest.fixture(scope="module")
def data() -> dict[str, Any]:
    """The extraction, once per module -- it reads 3.4MB of corpus and builds a 4MB dict."""
    return lit_report_extract.extract()  # type: ignore[no-any-return]


def _read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    """An independent read of one CSV, so the tool's counts are compared to something."""
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        columns = next(reader)
        return columns, [row for row in reader]


# --- Determinism (REQ-027 R05) ------------------------------------------------------------


def test_two_render_calls_produce_byte_identical_output() -> None:
    first = lit_report_extract.render(lit_report_extract.extract())
    second = lit_report_extract.render(lit_report_extract.extract())
    assert first == second


def test_two_subprocess_runs_produce_byte_identical_stdout() -> None:
    first = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "lit_report_extract.py")],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    second = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "lit_report_extract.py")],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    assert first.stdout == second.stdout
    assert json.loads(first.stdout)["counts"]["deliverables"] == 14


def test_deliverable_discovery_sorts_whatever_order_the_filesystem_yields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`Path.glob()` promises no order. Sorting is the tool's, not the filesystem's, to do.

    On a filesystem that already yields sorted names this would pass without `sorted()`, which is
    exactly why the glob is reversed here: the assertion has to be able to fail.
    """
    real_glob = Path.glob

    def reversed_glob(self: Path, pattern: str, *args: Any, **kwargs: Any) -> Any:
        return reversed(list(real_glob(self, pattern, *args, **kwargs)))

    monkeypatch.setattr(Path, "glob", reversed_glob)
    discovered = lit_report_extract.discover_deliverables(CORPUS)
    assert [path.name for path in discovered] == sorted(path.name for path in discovered)


def test_output_carries_no_wall_clock_reading() -> None:
    """R05's no-wall-clock rule, checked against the source rather than the output.

    A timestamp in the output would be caught by the byte-identical tests only if the two runs
    landed in different seconds, which is a race. Asserting the tool never imports the clock is
    the deterministic version of the same check.
    """
    source = (ROOT / "tools" / "lit_report_extract.py").read_text(encoding="utf-8")
    for forbidden in ("datetime.now", "time.time", "date.today", "utcnow"):
        assert forbidden not in source


# --- The deliverable set (REQ-027 R01) ----------------------------------------------------


def test_deliverable_set_equals_the_glob_on_disk(data: dict[str, Any]) -> None:
    on_disk = sorted(path.name for path in CORPUS.glob("[0-9][0-9]_*"))
    assert [entry["filename"] for entry in data["deliverables"]] == on_disk
    assert data["counts"]["deliverables"] == len(on_disk)


def test_campaign_working_files_fall_outside_the_deliverable_set(data: dict[str, Any]) -> None:
    """`CLAUDE.md` and `HANDOFF.md` live in the same directory and are not deliverables."""
    names = {entry["filename"] for entry in data["deliverables"]}
    assert (CORPUS / "CLAUDE.md").exists()
    assert (CORPUS / "HANDOFF.md").exists()
    assert "CLAUDE.md" not in names
    assert "HANDOFF.md" not in names


def test_markdown_deliverables_carry_their_source_and_csvs_do_not(data: dict[str, Any]) -> None:
    for entry in data["deliverables"]:
        path = CORPUS / entry["filename"]
        assert entry["bytes"] == path.stat().st_size
        if entry["format"] == "md":
            assert entry["markdown"] == path.read_text(encoding="utf-8")
            assert entry["line_count"] == len(entry["markdown"].splitlines())
        else:
            assert "markdown" not in entry


# --- The three tables (phase acceptance, REQ-027 R03) -------------------------------------


@pytest.mark.parametrize(
    ("key", "filename"),
    [
        ("ledger", "00_search_ledger.csv"),
        ("inventory", "03_source_inventory.csv"),
        ("matrix", "04_evidence_matrix.csv"),
    ],
)
def test_table_counts_match_an_independent_read(
    data: dict[str, Any], key: str, filename: str
) -> None:
    """Row and column counts recomputed from the CSV, not compared to 1200/1154/67.

    The phase's acceptance cites those figures; this asserts the tool measured rather than
    restated them, which is the property that survives the corpus changing.
    """
    columns, rows = _read_csv(CORPUS / filename)
    table = data["tables"][key]
    assert table["filename"] == filename
    assert table["columns"] == columns
    assert table["column_count"] == len(columns)
    assert table["row_count"] == len(rows)
    assert table["rows"] == rows
    assert data["counts"][f"{key}_columns"] == len(columns)
    assert data["counts"][f"{key}_rows"] == len(rows)


def test_csv_cells_stay_strings(data: dict[str, Any]) -> None:
    """A numeric-looking cell round-tripped through `float()` would rewrite the corpus.

    `04` as `4.0` and a leading-zero id as an int are silent edits to source data, so every cell
    is asserted to be the string the file holds.
    """
    for table in data["tables"].values():
        for row in table["rows"]:
            assert all(isinstance(cell, str) for cell in row)


def test_every_row_matches_the_header_width(data: dict[str, Any]) -> None:
    for table in data["tables"].values():
        assert all(len(row) == table["column_count"] for row in table["rows"])


# --- Collisions and hypotheses (phase acceptance: stable anchor ids) ----------------------


def test_collision_sections_match_the_headings_in_05(data: dict[str, Any]) -> None:
    source = (CORPUS / "05_critical_collisions.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## (\d+)\.\s+(\S+)\s*$", source, flags=re.M)
    # Every `## ` heading in `05` is a collision heading -- nothing is skipped by the pattern.
    assert [line for line in source.splitlines() if line.startswith("## ")] == [
        f"## {number}. {slug}" for number, slug in headings
    ]
    assert [(str(c["number"]), c["slug"]) for c in data["collisions"]] == headings
    assert data["counts"]["collision_sections"] == len(headings)


def test_collision_anchors_key_on_the_slug_not_the_number(data: dict[str, Any]) -> None:
    """Renumbering `05` must not break a link, and the slug is the join key to the matrix."""
    for collision in data["collisions"]:
        assert collision["anchor"] == f"collision-{collision['slug'].lower()}"
        assert str(collision["number"]) not in collision["anchor"].removeprefix("collision-")[:2]


def test_collision_slugs_are_a_bijection_with_the_matrix_collision_rows(
    data: dict[str, Any],
) -> None:
    """Every `05` section has a `critical_collision: yes` matrix row, and every such row a section.

    This is what `phase-lrr-04` will join on, and it is checked set-equal both ways so a slug
    present on one side only cannot hide behind a matching count.
    """
    columns, rows = _read_csv(CORPUS / "04_evidence_matrix.csv")
    source_id = columns.index("source_id")
    flag = columns.index("critical_collision")
    flagged = {row[source_id] for row in rows if row[flag].strip().lower() == "yes"}
    sections = {collision["slug"] for collision in data["collisions"]}
    assert sections == flagged
    assert data["known_defects"]["unmatched_collision_slugs"] == []


def test_second_review_verdicts_are_derived_and_the_prose_is_kept(data: dict[str, Any]) -> None:
    """`REQ-027` R07's count, recomputed -- and the commentary carried through untouched."""
    columns, rows = _read_csv(CORPUS / "04_evidence_matrix.csv")
    by_id = {row[columns.index("source_id")]: row for row in rows}
    review = columns.index("second_review")
    for collision in data["collisions"]:
        raw = by_id[collision["slug"]][review]
        assert collision["second_review"] == raw
        # Stated as a property rather than as a second copy of the parser: the prose the corpus
        # holds opens with the verdict the tool derived. The punctuation that follows varies --
        # `disputed:`, `confirmed,`, `confirmed;`, `disputed --` all occur -- so a test that
        # re-split on a fixed separator would only be testing its own guess at the separator.
        assert collision["second_review_verdict"] in ("confirmed", "disputed")
        assert raw.strip().lower().startswith(collision["second_review_verdict"])

    verdicts = data["counts"]["collision_second_review"]
    assert verdicts["disputed"] + verdicts["confirmed"] == len(data["collisions"])
    assert verdicts["unrecognised"] == 0


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("disputed: reviewer re-derives component_overlap to 3", "disputed"),
        ("confirmed, with one correction: temporal_model was miscoded", "confirmed"),
        ("confirmed; reviewer would in fact score H2 as a STRONG", "confirmed"),
        ("NOT_APPLICABLE", "not_applicable"),
        ("", "none"),
        ("   ", "none"),
        ("overturned by a later pass", "unrecognised"),
    ],
)
def test_second_review_classification(value: str, expected: str) -> None:
    """A verdict word this vocabulary does not know becomes `unrecognised`, never a guess."""
    assert lit_report_extract.classify_second_review(value) == expected


def test_hypothesis_blocks_cover_h1_through_h11(data: dict[str, Any]) -> None:
    source = (CORPUS / "06_hypothesis_tests.md").read_text(encoding="utf-8")
    ids = re.findall(r"^## (H\d+)\b", source, flags=re.M)
    assert [h["id"] for h in data["hypotheses"]] == ids
    assert ids == [f"H{n}" for n in range(1, len(ids) + 1)]
    assert data["counts"]["hypothesis_blocks"] == len(ids)


def test_hypothesis_summary_table_is_not_a_hypothesis_block(data: dict[str, Any]) -> None:
    """`06` ends with a `## Summary table` heading that the `H<n>` token must exclude."""
    source = (CORPUS / "06_hypothesis_tests.md").read_text(encoding="utf-8")
    assert "## Summary table" in source
    assert all(h["heading"] != "Summary table" for h in data["hypotheses"])
    assert len(data["hypotheses"]) == len(re.findall(r"^## ", source, flags=re.M)) - 1


def test_hypothesis_anchors_key_on_the_token_not_the_title(data: dict[str, Any]) -> None:
    """The descriptive title after the em dash can be rewritten without breaking a link."""
    for hypothesis in data["hypotheses"]:
        assert hypothesis["anchor"] == f"hypothesis-{hypothesis['id'].lower()}"
        assert hypothesis["title"]
        assert hypothesis["title"] not in hypothesis["anchor"]


def test_block_line_spans_and_markdown_agree_with_the_source(data: dict[str, Any]) -> None:
    """`line_start`/`line_end` are 1-based and inclusive, and bound exactly the emitted body."""
    for key, filename in (
        ("collisions", "05_critical_collisions.md"),
        ("hypotheses", "06_hypothesis_tests.md"),
    ):
        lines = (CORPUS / filename).read_text(encoding="utf-8").splitlines()
        for block in data[key]:
            span = lines[block["line_start"] - 1 : block["line_end"]]
            assert "\n".join(span) == block["markdown"]
            assert block["markdown"].startswith("## ")


def test_every_anchor_is_unique_and_html_id_safe(data: dict[str, Any]) -> None:
    anchors = [
        entry["anchor"]
        for entry in (
            *data["deliverables"],
            *data["collisions"],
            *data["hypotheses"],
            *data["tables"].values(),
        )
    ]
    assert len(anchors) == len(set(anchors))
    assert all(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", anchor) for anchor in anchors)


# --- Known corpus defects: reported, not repaired ------------------------------------------


def test_known_defects_are_reported_not_repaired(data: dict[str, Any]) -> None:
    """Idea `000308`'s duplicate inventory rows survive extraction and are named in the output.

    `PLAN-043` puts any edit to `research/literature-review/` out of scope, so the extractor's
    correct behaviour is to surface a duplicate and carry both rows through, never to collapse
    them.
    """
    columns, rows = _read_csv(CORPUS / "03_source_inventory.csv")
    index = columns.index("source_id")
    seen: dict[str, int] = {}
    for row in rows:
        seen[row[index]] = seen.get(row[index], 0) + 1
    duplicates = sorted(source_id for source_id, count in seen.items() if count > 1)

    assert duplicates, "the inventory's two duplicate source_id rows are expected to be present"
    assert data["known_defects"]["duplicate_inventory_source_ids"] == duplicates
    assert data["tables"]["inventory"]["row_count"] == len(rows)


# --- Failure modes -------------------------------------------------------------------------


def test_missing_corpus_directory_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(lit_report_extract.ExtractError, match="corpus directory not found"):
        lit_report_extract.extract(tmp_path / "nope")


def test_empty_corpus_directory_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(lit_report_extract.ExtractError, match="no files match"):
        lit_report_extract.extract(tmp_path)


def test_missing_csv_deliverable_is_an_error(tmp_path: Path) -> None:
    (tmp_path / "01_terminology_map.md").write_text("# x\n", encoding="utf-8")
    with pytest.raises(lit_report_extract.ExtractError, match="expected CSV deliverable"):
        lit_report_extract.extract(tmp_path)


def test_ragged_csv_row_is_an_error(tmp_path: Path) -> None:
    for name in ("00_search_ledger.csv", "03_source_inventory.csv"):
        (tmp_path / name).write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "04_evidence_matrix.csv").write_text("source_id,b\nx,2,3\n", encoding="utf-8")
    with pytest.raises(lit_report_extract.ExtractError, match="do not match the 2-column header"):
        lit_report_extract.extract(tmp_path)


def test_missing_source_id_column_is_an_error(tmp_path: Path) -> None:
    """A renamed or dropped `source_id` header must not escape as a raw `ValueError`.

    `OPS-017` promises every failure prints `error: <what>` and exits 1 with no traceback.
    `list.index` raises `ValueError`, which `main()` does not catch, so the guard is what makes
    that promise true for the one header the tool actually looks up by name.
    """
    (tmp_path / "00_search_ledger.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "03_source_inventory.csv").write_text("source_id,b\nx,2\n", encoding="utf-8")
    (tmp_path / "04_evidence_matrix.csv").write_text("renamed_id,b\nx,2\n", encoding="utf-8")
    (tmp_path / "05_critical_collisions.md").write_text("# c\n", encoding="utf-8")
    (tmp_path / "06_hypothesis_tests.md").write_text("# h\n", encoding="utf-8")
    with pytest.raises(lit_report_extract.ExtractError, match="required column 'source_id'"):
        lit_report_extract.extract(tmp_path)


def test_cli_reports_a_missing_column_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "00_search_ledger.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "03_source_inventory.csv").write_text("source_id,b\nx,2\n", encoding="utf-8")
    (tmp_path / "04_evidence_matrix.csv").write_text("renamed_id,b\nx,2\n", encoding="utf-8")
    (tmp_path / "05_critical_collisions.md").write_text("# c\n", encoding="utf-8")
    (tmp_path / "06_hypothesis_tests.md").write_text("# h\n", encoding="utf-8")
    assert lit_report_extract.main(["--corpus", str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "required column 'source_id'" in captured.err
    assert "Traceback" not in captured.err


def test_cli_writes_the_same_bytes_it_prints(tmp_path: Path) -> None:
    out = tmp_path / "extract.json"
    assert lit_report_extract.main(["--out", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == lit_report_extract.render(
        lit_report_extract.extract()
    )


def test_cli_reports_a_bad_corpus_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert lit_report_extract.main(["--corpus", str(tmp_path / "nope")]) == 1
    assert "corpus directory not found" in capsys.readouterr().err
