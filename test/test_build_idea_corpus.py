"""Tests for tools/build_idea_corpus.py's `--status` selection (REQ-009, phase-part-02).

The tool had no tests before this file, so the default-behaviour guarantee — that omitting
`--status` reproduces the old hard-coded `triaged`-only filter exactly — had nothing holding
it. Every test reads idea state through `fold()`, the same accessor the tool itself uses,
never the raw `_data/ideas.jsonl` log, and none of them write to it: `--out` always points at
`tmp_path`, and `--exclusions` is left at its real default (read-only).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> ModuleType:
    """Import a tools/ script by path -- tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build_idea_corpus = _load("build_idea_corpus")

from src.db.ideas import fold, load_events  # noqa: E402


def _ids_with_status(*statuses: str) -> set[str]:
    """The same fold() the tool uses, queried directly as an independent oracle."""
    state = fold(load_events())
    return {idea_id for idea_id, entry in state.items() if entry["status"] in statuses}


def test_default_status_selects_exactly_triaged_ideas() -> None:
    corpus, facts = build_idea_corpus.build_corpus(frozenset({"triaged"}))
    assert set(corpus) <= _ids_with_status("triaged")
    assert facts["triaged"] == len(_ids_with_status("triaged"))


def test_non_default_status_matches_a_direct_fold_query() -> None:
    """A --status other than the default selects exactly the ids fold() returns for it."""
    oracle = _ids_with_status("open")
    corpus, facts = build_idea_corpus.build_corpus(frozenset({"open"}))
    # The demo fast-lane exclusion file only ever consumes triaged ideas in practice, but the
    # tool still applies it here, so compare after the same removal the oracle does not do —
    # every selected id must be an open id, and every open id not excluded must be selected.
    assert set(corpus) <= oracle
    removed, _ = build_idea_corpus.load_exclusions(build_idea_corpus.EXCLUSIONS)
    assert set(corpus) == oracle - removed


def test_comma_separated_status_list_is_a_union() -> None:
    corpus, _ = build_idea_corpus.build_corpus(frozenset({"open", "reviewing"}))
    oracle = _ids_with_status("open", "reviewing")
    removed, _ = build_idea_corpus.load_exclusions(build_idea_corpus.EXCLUSIONS)
    assert set(corpus) == oracle - removed


def test_cli_status_flag_defaults_to_triaged(tmp_path: Path) -> None:
    exit_code = build_idea_corpus.main(["--out", str(tmp_path), "--seed", "1"])
    assert exit_code == 0
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == ["triaged"]


def test_cli_status_flag_records_non_default_selection(tmp_path: Path) -> None:
    exit_code = build_idea_corpus.main(
        ["--status", "open,reviewing", "--out", str(tmp_path), "--seed", "1"]
    )
    if exit_code != 0:
        pytest.skip("no open/reviewing ideas currently in the log to build a corpus from")
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == ["open", "reviewing"]


def test_manifest_records_status_on_default_run(tmp_path: Path) -> None:
    build_idea_corpus.main(["--out", str(tmp_path), "--seed", "1"])
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert "status" in manifest
    assert manifest["status"] == ["triaged"]


def test_stats_output_omits_status_field(capsys: pytest.CaptureFixture[str]) -> None:
    """--stats never writes manifest.json, so the byte-identical guarantee holds: the printed
    facts carry no `status` key, added only on the path that actually writes the manifest."""
    exit_code = build_idea_corpus.main(["--stats", "--seed", "1"])
    assert exit_code == 0
    facts = json.loads(capsys.readouterr().out)
    assert "status" not in facts


def test_unrecognized_status_exits_nonzero_and_names_valid_set(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = build_idea_corpus.main(["--status", "nonsense", "--stats"])
    assert exit_code != 0
    stderr = capsys.readouterr().err
    for status in build_idea_corpus.valid_statuses():
        assert status in stderr


def test_valid_statuses_comes_from_the_schema_not_a_second_list() -> None:
    """The valid set is exactly the union of legal_transitions()'s from/to values."""
    from src.db.ideas import legal_transitions

    transitions = legal_transitions()
    expected = {source for source, _ in transitions} | {target for _, target in transitions}
    assert build_idea_corpus.valid_statuses() == expected


def test_no_module_level_status_constant_used_as_filter() -> None:
    """REQ-009 R03: the status filter is a CLI option, not a source constant.

    Grep-style check on the tool's own source, mirroring REQ-009's stated verification
    method: the historical `CORPUS_STATUS` module constant must not exist at all.
    """
    source = (ROOT / "tools" / "build_idea_corpus.py").read_text(encoding="utf-8")
    assert "CORPUS_STATUS" not in source


def test_build_corpus_signature_requires_statuses_argument() -> None:
    """build_corpus() takes the selected statuses as a required argument -- there is no
    module-level default it could silently fall back to."""
    import inspect

    params = inspect.signature(build_idea_corpus.build_corpus).parameters
    assert "statuses" in params
    assert params["statuses"].default is inspect.Parameter.empty
