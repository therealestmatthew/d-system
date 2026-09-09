"""Tests for raw-only capture intake — REQ-002 R1/R2/R5/R9/R12, ADR-007 sections 1-2.

phase-cap-04 builds two channels, both writing through the single `write_raw_capture`
function phase-cap-03's schema already governs: the CLI (`tools/capture.py`) and the inbox
scanner (`src.capture.raw.scan_inbox`). Neither interprets a capture — that is
phase-cap-05's job — so these tests care about fidelity (byte-identical, never mutated,
never lost to a bad neighbour) and the write boundary (nothing lands outside
`_capture/raw/`), not about meaning.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "capture.schema.json").read_text(encoding="utf-8"))

from src.capture import raw as capture_raw  # noqa: E402


def _load(name: str) -> Any:
    """Import a tools/ script by path — tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


capture_cli = _load("capture")


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    return tmp_path / "raw"


@pytest.fixture
def inbox_dir(tmp_path: Path) -> Path:
    return tmp_path / "inbox"


def _records(raw_dir: Path) -> list[dict[str, Any]]:
    return [
        json.loads(path.read_text(encoding="utf-8")) for path in sorted(raw_dir.glob("*.json"))
    ]


# --- write_raw_capture: R1 (byte-identical), R2 (never mutated) --------------------------


def test_write_raw_capture_stores_content_byte_identical(raw_dir: Path) -> None:
    content = "Call John about the Q3 deliverable by Friday."
    record = capture_raw.write_raw_capture(content, channel="cli", raw_dir=raw_dir)

    assert record["content"] == content
    stored = _records(raw_dir)
    assert len(stored) == 1
    assert stored[0]["content"] == content


def test_write_raw_capture_preserves_special_characters_unchanged(raw_dir: Path) -> None:
    """Backticks, `$(...)`, quotes and non-ASCII survive JSON round-tripping unchanged."""
    content = "Body with `backticks`, $(subst), \"quotes\", 'quotes',\na newline, Ünïcødé 日本語."
    capture_raw.write_raw_capture(content, channel="cli", raw_dir=raw_dir)

    assert _records(raw_dir)[0]["content"] == content


def test_write_raw_capture_produces_a_valid_id_and_timestamp(raw_dir: Path) -> None:
    record = capture_raw.write_raw_capture("text", channel="cli", raw_dir=raw_dir)

    assert Draft7Validator(SCHEMA).is_valid(record)


def test_two_captures_never_collide_and_never_rewrite_each_other(raw_dir: Path) -> None:
    first = capture_raw.write_raw_capture("first", channel="cli", raw_dir=raw_dir)
    first_path = raw_dir / f"{first['id']}.json"
    before = first_path.read_text(encoding="utf-8")

    second = capture_raw.write_raw_capture("second", channel="cli", raw_dir=raw_dir)

    assert first["id"] != second["id"]
    assert first_path.read_text(encoding="utf-8") == before, "an existing raw record changed"
    assert len(_records(raw_dir)) == 2


def test_write_raw_capture_rejects_empty_content_and_writes_nothing(raw_dir: Path) -> None:
    with pytest.raises(capture_raw.CaptureError, match="refusing to write"):
        capture_raw.write_raw_capture("", channel="cli", raw_dir=raw_dir)

    assert not raw_dir.exists() or not list(raw_dir.iterdir())


def test_write_raw_capture_rejects_unknown_channel(raw_dir: Path) -> None:
    with pytest.raises(capture_raw.CaptureError, match="channel"):
        capture_raw.write_raw_capture("text", channel="email", raw_dir=raw_dir)


# --- R12: nothing written outside _capture/raw/ -------------------------------------------


def test_write_raw_capture_touches_only_the_raw_directory(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    capture_raw.write_raw_capture("text", channel="cli", raw_dir=raw_dir)

    assert [p.name for p in tmp_path.iterdir()] == ["raw"]
    assert not (tmp_path / "staging").exists()
    assert not (tmp_path / "_data").exists()


# --- scan_inbox: file-shaped input becomes a raw record, source_path is relative ---------


def test_scan_inbox_converts_every_file_and_records_relative_source_path(
    inbox_dir: Path, raw_dir: Path
) -> None:
    inbox_dir.mkdir(parents=True)
    (inbox_dir / "note.md").write_text("A pasted note.", encoding="utf-8")
    (inbox_dir / "transcript.txt").write_text("A call transcript.", encoding="utf-8")

    records, failures = capture_raw.scan_inbox(inbox_dir=inbox_dir, raw_dir=raw_dir)

    assert failures == []
    assert {r["source_path"] for r in records} == {"note.md", "transcript.txt"}
    assert {r["channel"] for r in records} == {"inbox"}
    stored_content = {r["content"] for r in _records(raw_dir)}
    assert stored_content == {"A pasted note.", "A call transcript."}


def test_scan_inbox_moves_converted_files_to_processed(inbox_dir: Path, raw_dir: Path) -> None:
    inbox_dir.mkdir(parents=True)
    (inbox_dir / "note.md").write_text("content", encoding="utf-8")

    capture_raw.scan_inbox(inbox_dir=inbox_dir, raw_dir=raw_dir)

    assert not (inbox_dir / "note.md").exists()
    assert (inbox_dir / "processed" / "note.md").read_text(encoding="utf-8") == "content"


def test_scan_inbox_never_recaptures_a_processed_file(inbox_dir: Path, raw_dir: Path) -> None:
    inbox_dir.mkdir(parents=True)
    (inbox_dir / "note.md").write_text("content", encoding="utf-8")

    first_records, _ = capture_raw.scan_inbox(inbox_dir=inbox_dir, raw_dir=raw_dir)
    second_records, _ = capture_raw.scan_inbox(inbox_dir=inbox_dir, raw_dir=raw_dir)

    assert len(first_records) == 1
    assert second_records == []
    assert len(_records(raw_dir)) == 1


def test_scan_inbox_skips_hidden_files(inbox_dir: Path, raw_dir: Path) -> None:
    inbox_dir.mkdir(parents=True)
    (inbox_dir / ".DS_Store").write_text("junk", encoding="utf-8")

    records, failures = capture_raw.scan_inbox(inbox_dir=inbox_dir, raw_dir=raw_dir)

    assert records == [] and failures == []
    assert (inbox_dir / ".DS_Store").exists(), "a hidden file must not be moved or captured"


def test_scan_inbox_missing_directory_is_empty_not_an_error(tmp_path: Path) -> None:
    records, failures = capture_raw.scan_inbox(
        inbox_dir=tmp_path / "does-not-exist", raw_dir=tmp_path / "raw"
    )
    assert records == [] and failures == []


# --- R9: one bad inbox file never blocks the others ---------------------------------------


def test_scan_inbox_a_bad_file_is_left_in_place_and_does_not_block_the_rest(
    inbox_dir: Path, raw_dir: Path
) -> None:
    inbox_dir.mkdir(parents=True)
    (inbox_dir / "empty.md").write_text("", encoding="utf-8")
    (inbox_dir / "good.md").write_text("A good note.", encoding="utf-8")

    records, failures = capture_raw.scan_inbox(inbox_dir=inbox_dir, raw_dir=raw_dir)

    assert len(records) == 1 and records[0]["source_path"] == "good.md"
    assert len(failures) == 1 and failures[0][0] == inbox_dir / "empty.md"
    assert (inbox_dir / "empty.md").exists(), "a failed file must not be moved to processed/"
    assert not (inbox_dir / "processed" / "empty.md").exists()


# --- The real CLI entry point: R5 (single command), stdin safety --------------------------


def test_cli_writes_a_raw_record_from_the_positional_argument(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(capture_cli, "RAW_DIR", raw_dir)

    exit_code = capture_cli.main(["Call John about the Q3 deliverable by Friday."])

    assert exit_code == 0
    stored = _records(raw_dir)
    assert len(stored) == 1
    assert stored[0]["content"] == "Call John about the Q3 deliverable by Friday."
    assert stored[0]["channel"] == "cli"
    assert "captured raw-" in capsys.readouterr().out


def test_cli_reads_dangerous_text_from_stdin_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The safe route: text piped on stdin never passes through a shell as an argument."""
    raw_dir = tmp_path / "raw"
    dangerous = "Body with `backticks`, $(subst), \"quotes\" and a newline.\nSecond line."
    monkeypatch.setattr(capture_cli, "RAW_DIR", raw_dir)
    monkeypatch.setattr(sys, "stdin", io.StringIO(dangerous))

    exit_code = capture_cli.main([])

    assert exit_code == 0
    assert _records(raw_dir)[0]["content"] == dangerous


def test_cli_refuses_empty_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(capture_cli, "RAW_DIR", raw_dir)
    monkeypatch.setattr(sys, "stdin", io.StringIO("   \n"))

    exit_code = capture_cli.main([])

    assert exit_code == 1
    assert not raw_dir.exists() or not list(raw_dir.iterdir())


def test_cli_inbox_flag_scans_and_reports_each_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    raw_dir = tmp_path / "raw"
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    (inbox_dir / "note.md").write_text("A pasted note.", encoding="utf-8")
    monkeypatch.setattr(capture_cli, "RAW_DIR", raw_dir)
    monkeypatch.setattr(capture_cli, "INBOX_DIR", inbox_dir)

    exit_code = capture_cli.main(["--inbox"])

    assert exit_code == 0
    assert "captured raw-" in capsys.readouterr().out
    assert _records(raw_dir)[0]["content"] == "A pasted note."


def test_cli_inbox_flag_rejects_text_argument(tmp_path: Path) -> None:
    exit_code = capture_cli.main(["--inbox", "some text"])
    assert exit_code == 1


def test_cli_inbox_flag_reports_failures_with_nonzero_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    raw_dir = tmp_path / "raw"
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()
    (inbox_dir / "empty.md").write_text("", encoding="utf-8")
    monkeypatch.setattr(capture_cli, "RAW_DIR", raw_dir)
    monkeypatch.setattr(capture_cli, "INBOX_DIR", inbox_dir)

    exit_code = capture_cli.main(["--inbox"])

    assert exit_code == 1
    assert "error:" in capsys.readouterr().err
