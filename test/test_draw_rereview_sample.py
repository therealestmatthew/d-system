"""Tests for tools/draw_rereview_sample.py, the re-review sampler (REQ-030 R07, phase-asr-03).

Each test builds its own verdict and draw records in a temporary root holding a copy of the real
schema, then calls the tool's functions or its `main` against that root.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHA = "0123456789abcdef" * 4


def _load_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "draw_rereview_sample", ROOT / "tools" / "draw_rereview_sample.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["draw_rereview_sample"] = module
    spec.loader.exec_module(module)
    return module


tool = _load_tool()


def verdict(phase: str, reviewer: str = "demo-adversary", result: str = "pass",
            day: str = "2026-10-02", gating: bool = True) -> dict[str, Any]:
    return {
        "verdict_id": f"{day}-{phase}-{reviewer}",
        "date": day,
        "phase": phase,
        "reviewed_commit": "a" * 40,
        "reviewer": {"type": reviewer, "definition_sha256": SHA},
        "model": "claude-opus-5-5",
        "verdict": result,
        "gating": gating,
        "findings": [],
        "raw_reply_sha256": SHA,
        "outcomes": [],
    }


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "schemas").mkdir()
    shutil.copy(ROOT / tool.SCHEMA, tmp_path / tool.SCHEMA)
    (tmp_path / tool.VERDICTS).mkdir(parents=True)
    return tmp_path


def write(root: Path, record: dict[str, Any]) -> None:
    is_draw = "draw_id" in record
    directory, key = (tool.DRAWS, "draw_id") if is_draw else (tool.VERDICTS, "verdict_id")
    (root / directory).mkdir(parents=True, exist_ok=True)
    (root / directory / f"{record[key]}.json").write_text(json.dumps(record), encoding="utf-8")


def passes(n: int) -> list[dict[str, Any]]:
    return [verdict(f"phase-t-{i:02d}") for i in range(1, n + 1)]


def sample_of(verdicts: list[dict[str, Any]], seed: int) -> list[tuple[str, str]]:
    considered = tool.unconsidered(verdicts, [])
    return [(d.verdict_id, d.reason) for d in tool.draw(verdicts, considered, seed)]


# --- the three acceptance fixtures -------------------------------------------------


def test_the_same_seed_gives_the_same_sample() -> None:
    verdicts = passes(25)
    assert sample_of(verdicts, 4021) == sample_of(verdicts, 4021)
    drawn_by_seed = {tuple(sample_of(verdicts, seed)) for seed in range(50)}
    assert len(drawn_by_seed) > 1, "the seed must change the draw"


@pytest.mark.parametrize("seed", range(20))
def test_a_once_rejected_phase_is_always_in_the_sample(seed: int) -> None:
    rejected = verdict("phase-t-50", result="reject", day="2026-10-01")
    passed = verdict("phase-t-50", day="2026-10-02")
    drawn = sample_of([*passes(30), rejected, passed], seed)
    assert (passed["verdict_id"], "rejected-before-pass") in drawn


def test_the_original_reviewer_type_is_excluded_as_re_reviewer() -> None:
    passed = verdict("phase-t-01")
    shadow = verdict("phase-t-01", reviewer="review-judge", result="reject", gating=False)
    drawn = tool.draw([passed, shadow], [passed["verdict_id"]], seed=1)
    assert len(drawn) == 1
    assert drawn[0].excluded_reviewer_types == ("demo-adversary", "review-judge")


# --- how many are drawn ------------------------------------------------------------


@pytest.mark.parametrize(("n", "k"), [(1, 1), (3, 1), (10, 1), (11, 2), (25, 3)])
def test_one_in_ten_rounded_up(n: int, k: int) -> None:
    drawn = sample_of(passes(n), seed=7)
    assert len(drawn) == k
    assert all(reason == "one-in-ten" for _, reason in drawn)


def test_rejected_reviews_are_considered_but_never_drawn() -> None:
    rejected = verdict("phase-t-01", result="reject")
    assert tool.unconsidered([rejected], []) == [rejected["verdict_id"]]
    assert sample_of([rejected], seed=1) == []


def test_a_rejection_after_the_pass_does_not_count() -> None:
    passed = verdict("phase-t-01", day="2026-10-02")
    later = verdict("phase-t-01", reviewer="demo-validator-code", result="reject", day="2026-10-05")
    assert sample_of([passed, later], seed=3) == [(passed["verdict_id"], "one-in-ten")]


# --- which verdicts are considered -------------------------------------------------


def test_shadow_verdicts_are_never_considered() -> None:
    shadow = verdict("phase-t-01", reviewer="review-judge", gating=False)
    assert tool.unconsidered([shadow], []) == []


def test_a_shadow_rejection_does_not_count_as_rejected_before_pass() -> None:
    shadow = verdict(
        "phase-t-01", reviewer="review-judge", result="reject", day="2026-10-01", gating=False
    )
    passed = verdict("phase-t-01")
    drawn = tool.draw([shadow, passed], [passed["verdict_id"]], seed=1)
    assert [d.reason for d in drawn] == ["one-in-ten"]


def test_verdicts_an_earlier_draw_considered_are_skipped() -> None:
    old, new = verdict("phase-t-01"), verdict("phase-t-02")
    earlier = {"considered": [old["verdict_id"]]}
    assert tool.unconsidered([old, new], [earlier]) == [new["verdict_id"]]


def test_a_rejection_in_an_earlier_draw_still_counts() -> None:
    rejected = verdict("phase-t-01", result="reject", day="2026-10-01")
    passed = verdict("phase-t-01", day="2026-10-03")
    earlier = {"considered": [rejected["verdict_id"]]}
    considered = tool.unconsidered([rejected, passed], [earlier])
    drawn = tool.draw([rejected, passed], considered, seed=9)
    expected = [(passed["verdict_id"], "rejected-before-pass")]
    assert [(d.verdict_id, d.reason) for d in drawn] == expected


# --- main: writing, dry run, replay, refusal --------------------------------------


def test_main_writes_a_valid_draw_and_the_next_draw_starts_after_it(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    for record in passes(12):
        write(root, record)
    assert tool.main(["--seed", "4021"], root=root, today="2026-10-09") == 0
    path = root / tool.DRAWS / "2026-10-09-01.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["seed"] == 4021
    assert len(record["considered"]) == 12
    assert len(record["sample"]) == 2
    assert tool.load_draws(root) == [record]  # it validates against definitions/draw

    write(root, verdict("phase-t-40"))
    assert tool.main(["--seed", "1"], root=root, today="2026-10-09") == 0
    second = json.loads((root / tool.DRAWS / "2026-10-09-02.json").read_text(encoding="utf-8"))
    assert second["considered"] == ["2026-10-02-phase-t-40-demo-adversary"]

    assert tool.main([], root=root, today="2026-10-09") == 0
    assert "nothing drawn and nothing written" in capsys.readouterr().out
    assert len(list((root / tool.DRAWS).glob("*.json"))) == 2


def test_dry_run_writes_nothing(root: Path) -> None:
    write(root, verdict("phase-t-01"))
    assert tool.main(["--dry-run", "--seed", "5"], root=root, today="2026-10-09") == 0
    assert not (root / tool.DRAWS).exists()


def test_a_fresh_seed_is_recorded(root: Path) -> None:
    write(root, verdict("phase-t-01"))
    assert tool.main([], root=root, today="2026-10-09") == 0
    record = json.loads((root / tool.DRAWS / "2026-10-09-01.json").read_text(encoding="utf-8"))
    assert 0 <= record["seed"] < tool.SEED_BOUND


def test_replay_matches_a_recorded_draw(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    for record in passes(15):
        write(root, record)
    assert tool.main(["--seed", "77"], root=root, today="2026-10-09") == 0
    capsys.readouterr()
    assert tool.main(["--replay", "2026-10-09-01"], root=root) == 0
    assert "replays" in capsys.readouterr().out


def test_replay_of_an_edited_draw_fails(root: Path) -> None:
    for record in passes(15):
        write(root, record)
    assert tool.main(["--seed", "77"], root=root, today="2026-10-09") == 0
    path = root / tool.DRAWS / "2026-10-09-01.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    drawn = {e["verdict_id"] for e in record["sample"]}
    swap = next(v for v in record["considered"] if v not in drawn)
    record["sample"][0]["verdict_id"] = swap
    path.write_text(json.dumps(record), encoding="utf-8")
    assert tool.main(["--replay", "2026-10-09-01"], root=root) == 1


def test_replay_of_an_unknown_draw_is_refused(root: Path) -> None:
    assert tool.main(["--replay", "2026-10-09-01"], root=root) == 2


def test_an_invalid_verdict_record_is_refused(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = verdict("phase-t-01")
    del broken["model"]
    write(root, broken)
    assert tool.main(["--seed", "1"], root=root, today="2026-10-09") == 2
    assert "'model' is a required property" in capsys.readouterr().err
    assert not (root / tool.DRAWS).exists()


def test_a_record_not_named_by_its_id_is_refused(root: Path) -> None:
    record = verdict("phase-t-01")
    (root / tool.VERDICTS / "renamed.json").write_text(json.dumps(record), encoding="utf-8")
    assert tool.main(["--seed", "1"], root=root, today="2026-10-09") == 2


def test_seed_and_replay_together_are_refused(root: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        tool.main(["--seed", "1", "--replay", "2026-10-09-01"], root=root)
    assert exc.value.code == 2


def test_a_seed_out_of_range_is_refused(root: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        tool.main(["--seed", "-1"], root=root)
    assert exc.value.code == 2
