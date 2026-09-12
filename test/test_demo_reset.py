"""Tests for tools/demo_reset.py -- the demo rehearsal gate's reset tool (PROMPT-017).

Every test builds a `demo_reset.Paths` pointed at a temporary tree so nothing here ever
touches the real `_data/ideas.jsonl`, the real `.claude/skills/d-system-overview/`, or the
real `_public/overview/index.html` -- the same isolation `test_ideas.py` uses for
`tools/append_idea.py`'s writer functions. `tools/generate_overview.py` itself always reads
the real repository's idea log, backlog and systems registry (it takes no path overrides), so
these tests redirect only its `--out` file, never its inputs.
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


demo_reset = _load("demo_reset")


def _make_paths(
    tmp_path: Path, skill_content: str = "original skill content\n"
) -> demo_reset.Paths:
    skill_dir = tmp_path / "skills" / "d-system-overview"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")
    return demo_reset.Paths(
        root=ROOT,
        idea_log=tmp_path / "ideas.jsonl",
        skill_dir=skill_dir,
        parked_skill_dir=tmp_path / "skills" / "_parked" / "d-system-overview",
        scratch_dir=tmp_path / "demo-scratch",
        overview_out=tmp_path / "overview" / "index.html",
        generate_overview_script=ROOT / "tools" / "generate_overview.py",
        append_idea_script=ROOT / "tools" / "append_idea.py",
    )


def _events(log: Path) -> list[dict[str, object]]:
    if not log.exists():
        return []
    lines = log.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


# --- The allowlist is enforced in code, not left as a comment ------------------------------


def test_guard_accepts_a_path_inside_its_allowed_root(tmp_path: Path) -> None:
    target = tmp_path / "scratch" / "leftover.txt"
    resolved = demo_reset._guard(target, allowed_roots=[tmp_path / "scratch"])
    assert resolved == target.resolve()


def test_guard_refuses_the_idea_log(tmp_path: Path) -> None:
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset._guard(ROOT / "_data" / "ideas.jsonl", allowed_roots=[tmp_path])


def test_guard_refuses_anything_under_docs(tmp_path: Path) -> None:
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset._guard(ROOT / "docs" / "09-backlog" / "backlog.yaml", allowed_roots=[tmp_path])


def test_guard_refuses_private(tmp_path: Path) -> None:
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset._guard(ROOT / "_private" / "anything", allowed_roots=[tmp_path])


def test_guard_refuses_dot_agents_and_dot_codex(tmp_path: Path) -> None:
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset._guard(ROOT / ".agents" / "anything", allowed_roots=[tmp_path])
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset._guard(ROOT / ".codex" / "anything", allowed_roots=[tmp_path])


def test_guard_refuses_agents_md_and_claude_md(tmp_path: Path) -> None:
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset._guard(ROOT / "AGENTS.md", allowed_roots=[tmp_path])
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset._guard(ROOT / "CLAUDE.md", allowed_roots=[tmp_path])


def test_guard_refuses_a_path_outside_the_supplied_allowlist_even_when_harmless(
    tmp_path: Path,
) -> None:
    other = tmp_path / "not-allowed"
    other.mkdir()
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset._guard(other / "file.txt", allowed_roots=[tmp_path / "scratch"])


def test_forbidden_paths_win_even_if_an_ancestor_is_passed_as_allowed(tmp_path: Path) -> None:
    """A caller passing REPO ROOT as an allowed root still may not reach _data/ideas.jsonl."""
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset._guard(ROOT / "_data" / "ideas.jsonl", allowed_roots=[ROOT])


# --- prepare -> restore round-trip returns the skill to its original content ---------------


def test_prepare_parks_the_skill_and_restore_returns_it_byte_identical(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    original = (paths.skill_dir / "SKILL.md").read_bytes()

    demo_reset.prepare(paths)
    assert not paths.skill_dir.exists()
    assert paths.parked_skill_dir.exists()
    assert (paths.parked_skill_dir / "SKILL.md").read_bytes() == original

    demo_reset.restore(paths)
    assert paths.skill_dir.exists()
    assert not paths.parked_skill_dir.exists()
    assert (paths.skill_dir / "SKILL.md").read_bytes() == original


def test_prepare_report_names_the_park_action(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    report = demo_reset.prepare(paths)
    assert report.skill_park == "parked"
    assert report.overview_regenerated is True
    assert report.scratch_cleared is True


def test_restore_report_names_the_restore_action(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    demo_reset.prepare(paths)
    report = demo_reset.restore(paths)
    assert report.skill_restore == "restored"


# --- prepare clears scratch state ------------------------------------------------------------


def test_prepare_clears_pre_existing_scratch_content(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    paths.scratch_dir.mkdir(parents=True)
    leftover = paths.scratch_dir / "leftover-from-a-prior-rehearsal.txt"
    leftover.write_text("stale", encoding="utf-8")

    demo_reset.prepare(paths)

    assert paths.scratch_dir.exists()
    assert not leftover.exists()
    assert list(paths.scratch_dir.iterdir()) == []


# --- no-duplicate-seed check -----------------------------------------------------------------


def test_prepare_seeds_the_fallback_idea_exactly_once(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)

    first_report = demo_reset.prepare(paths)
    assert first_report.idea_seed == "seeded"
    events_after_first = _events(paths.idea_log)
    fallback_events = [
        e for e in events_after_first
        if e.get("event") == "created" and e.get("title") == demo_reset.FALLBACK_SEED_TITLE
    ]
    assert len(fallback_events) == 1

    # A second prepare must not append a second created event for the same fallback idea, even
    # though the skill is already parked by now (proving the seed check is independent of the
    # park state).
    second_report = demo_reset.prepare(paths)
    assert second_report.idea_seed == "already seeded"
    events_after_second = _events(paths.idea_log)
    assert events_after_second == events_after_first


def test_prepare_does_not_seed_when_the_fallback_title_was_recorded_by_hand(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    append_idea = _load("append_idea")
    append_idea.add(
        demo_reset.FALLBACK_SEED_TITLE, "recorded independently of demo_reset", paths.idea_log
    )

    report = demo_reset.prepare(paths)
    assert report.idea_seed == "already seeded"
    events = _events(paths.idea_log)
    created = [e for e in events if e.get("event") == "created"]
    assert len(created) == 1


# --- both subcommands' double-run idempotence -------------------------------------------------


def test_prepare_twice_in_a_row_is_safe(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)

    first = demo_reset.prepare(paths)
    second = demo_reset.prepare(paths)

    assert first.skill_park == "parked"
    assert second.skill_park == "already parked"
    assert first.idea_seed == "seeded"
    assert second.idea_seed == "already seeded"
    # No error, and the skill is still parked exactly once -- not deleted or duplicated.
    assert paths.parked_skill_dir.exists()
    assert not paths.skill_dir.exists()


def test_restore_twice_in_a_row_is_safe(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    demo_reset.prepare(paths)

    first = demo_reset.restore(paths)
    second = demo_reset.restore(paths)

    assert first.skill_restore == "restored"
    assert second.skill_restore == "already in place"
    assert paths.skill_dir.exists()
    assert not paths.parked_skill_dir.exists()


# --- restore is a real, separately invokable operation ----------------------------------------


def test_restore_without_a_prior_prepare_refuses_cleanly(tmp_path: Path) -> None:
    """Neither the skill nor a parked copy exists -- restore must refuse, not silently succeed."""
    paths = demo_reset.Paths(
        root=ROOT,
        idea_log=tmp_path / "ideas.jsonl",
        skill_dir=tmp_path / "skills" / "d-system-overview",
        parked_skill_dir=tmp_path / "skills" / "_parked" / "d-system-overview",
        scratch_dir=tmp_path / "demo-scratch",
        overview_out=tmp_path / "overview" / "index.html",
        generate_overview_script=ROOT / "tools" / "generate_overview.py",
        append_idea_script=ROOT / "tools" / "append_idea.py",
    )
    with pytest.raises(demo_reset.DemoResetError):
        demo_reset.restore(paths)


def test_restore_regenerates_the_overview_output_file(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    demo_reset.prepare(paths)
    assert paths.overview_out.exists()
    paths.overview_out.unlink()

    demo_reset.restore(paths)

    assert paths.overview_out.exists()
    assert paths.overview_out.read_text(encoding="utf-8")


# --- help text carries the "pre-built state" contract ------------------------------------------


def test_help_text_states_the_page_regeneration_contract(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        demo_reset.main(["--help"])
    out = capsys.readouterr().out
    assert "pre-built state" in out
    assert "not the contract" in out or "NOT the contract" in out
