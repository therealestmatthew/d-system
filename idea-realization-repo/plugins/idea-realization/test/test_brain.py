"""The shared memory: one-step capture as the current developer, loading, and its check."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import paths
import pytest
import scaffold
import yaml
from checks import brain as feature
from conftest import as_developer

import brain


@pytest.fixture
def config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> paths.Config:
    for key in ("IDEA_REALIZATION_ROOT", "CLAUDE_PROJECT_DIR"):
        monkeypatch.delenv(key, raising=False)
    team = {"repository-owner": "Owner.",
            "ana": {"description": "Ana.", "emails": ["ana@example.com"],
                    "approves": ["procedures"]},
            "ben": {"description": "Ben.", "emails": ["ben@example.com"]}}
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "systems.yaml").write_text(yaml.safe_dump({"owners": team}))
    as_developer(monkeypatch, "ana")
    configured = paths.resolve({"root": str(tmp_path)}, env={})
    scaffold.scaffold(configured, ["brain"])
    return configured


def record(config: paths.Config, kind: str = "decision", title: str = "Use one profile per role",
           **extra: list[str]) -> Path:
    return brain.new(config, kind, title, "Because roles bound what an agent can do.",
                     extra.get("tags", []), extra.get("links", []), extra.get("sources", []))


def test_a_scaffolded_brain_is_clean(config: paths.Config) -> None:
    assert feature.check(config) == []


def test_new_records_an_entry_as_the_current_developer(config: paths.Config) -> None:
    path = record(config, tags=["cloud"], sources=["https://example.com/doc"])
    assert path.parent.name == "decisions"
    entry, _ = brain.parse(path)
    assert entry is not None
    assert entry.meta["author"] == "ana" and entry.meta["kind"] == "decision"
    assert feature.check(config) == []


def test_each_kind_lands_in_its_folder(config: paths.Config) -> None:
    for kind, folder in brain.FOLDERS.items():
        assert record(config, kind, f"A {kind} entry").parent.name == folder
    assert feature.check(config) == []


def test_a_second_entry_with_the_same_title_is_refused(config: paths.Config) -> None:
    record(config)
    with pytest.raises(ValueError, match="is taken by"):
        record(config)


def test_a_link_to_an_unknown_entry_is_refused_at_capture(config: paths.Config) -> None:
    with pytest.raises(ValueError, match="unknown"):
        record(config, links=["no-such-entry"])


def test_the_author_comes_from_the_git_identity(config: paths.Config,
                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    as_developer(monkeypatch, "ana", "ben@example.com")
    with pytest.raises(Exception, match="belongs to 'ben'"):
        record(config)


def test_check_catches_a_stale_index(config: paths.Config) -> None:
    path = record(config)
    path.write_text(path.read_text().replace("Use one profile per role", "Renamed"))
    assert any("index.md is stale" in line for line in feature.check(config))


def test_check_catches_a_broken_link_and_a_wrong_folder(config: paths.Config) -> None:
    path = record(config)
    text = path.read_text().replace("status: active", "status: active\nlinks:\n- missing")
    moved = path.parent.parent / "concepts" / path.name
    moved.write_text(text)
    path.unlink()
    brain.write_index(config.path("brain_root"))
    problems = feature.check(config)
    assert any("links to unknown entry missing" in line for line in problems)
    assert any("belongs in decisions/" in line for line in problems)


def test_check_catches_bad_front_matter_and_an_unknown_author(config: paths.Config) -> None:
    root = config.path("brain_root")
    (root / "concepts" / "loose.md").write_text("no front matter\n")
    day = date(2030, 1, 5).isoformat()
    (root / "concepts" / "stranger.md").write_text(
        f"---\nid: stranger\nkind: concept\ntitle: T\nauthor: zed\ncreated: '{day}'\n"
        f"updated: '{day}'\nstatus: active\n---\nBody.\n")
    brain.write_index(root)
    problems = feature.check(config)
    assert any("loose.md: has no YAML front matter" in line for line in problems)
    assert any("author 'zed'" in line for line in problems)


def test_load_filters_by_kind_tag_query_and_link(config: paths.Config) -> None:
    root = config.path("brain_root")
    record(config, "concept", "Sandbox profile", tags=["cloud"])
    record(config, "decision", "Use the deploy role only for deploys", links=["sandbox-profile"])
    record(config, "note", "Demo dry run", tags=["demo"])
    entries, _ = brain.load_entries(root)
    titles = lambda chosen: sorted(e.meta["title"] for e in chosen)  # noqa: E731
    assert titles(brain.select(entries, kind="concept")) == ["Sandbox profile"]
    assert titles(brain.select(entries, tag="demo")) == ["Demo dry run"]
    assert titles(brain.select(entries, query="DEPLOY role")) == [
        "Use the deploy role only for deploys"]
    assert titles(brain.select(entries, link="sandbox-profile")) == [
        "Sandbox profile", "Use the deploy role only for deploys"]
    context = brain.render_context(root, brain.select(entries, kind="concept"))
    assert "## [concept] Sandbox profile" in context and "author ana" in context


def test_superseded_entries_are_left_out_unless_asked(config: paths.Config) -> None:
    path = record(config)
    path.write_text(path.read_text().replace("status: active", "status: superseded"))
    entries, _ = brain.load_entries(config.path("brain_root"))
    assert brain.select(entries) == []
    assert len(brain.select(entries, include_superseded=True)) == 1


def test_the_cli_records_loads_and_checks(config: paths.Config,
                                          capsys: pytest.CaptureFixture[str]) -> None:
    root = ["--root", str(config.root)]
    assert brain.main(["new", "lesson", "--title", "Rebase before review", "--body", "Why.",
                       *root]) == 0
    assert brain.main(["load", "--kind", "lesson", *root]) == 0
    assert "Rebase before review" in capsys.readouterr().out
    assert brain.main(["check", *root]) == 0


def test_no_brain_is_clean(tmp_path: Path) -> None:
    assert feature.check(paths.resolve({"root": str(tmp_path)}, env={})) == []


def write(root: Path, folder: str, name: str, **meta: object) -> None:
    day = date(2030, 1, 5).isoformat()
    front = {"id": name, "title": "T", "author": "ana", "created": day, "updated": day,
             "status": "active", **meta}
    (root / folder / f"{name}.md").write_text(f"---\n{yaml.safe_dump(front)}---\nBody.\n")
    brain.write_index(root)


def test_only_an_approver_records_a_procedure(config: paths.Config,
                                              monkeypatch: pytest.MonkeyPatch) -> None:
    as_developer(monkeypatch, "ben")
    with pytest.raises(ValueError, match="approving procedures"):
        record(config, "procedure", "Rebase before review")
    as_developer(monkeypatch, "ana")
    entry, _ = brain.parse(record(config, "procedure", "Rebase before review"))
    assert entry is not None and entry.meta["approved_by"] == "ana"
    assert feature.check(config) == []


def test_a_hand_written_procedure_needs_an_approvers_approval(config: paths.Config) -> None:
    root = config.path("brain_root")
    write(root, "learnings", "unapproved", kind="procedure")
    day = date(2030, 1, 5).isoformat()
    write(root, "learnings", "approved-by-ben", kind="procedure", approved_by="ben",
          approved_on=day)
    problems = feature.check(config)
    assert any("unapproved.md" in line and "approved_by" in line for line in problems)
    assert any("approved-by-ben.md" in line and "not listed" in line for line in problems)


def test_an_id_taken_in_another_folder_is_refused(config: paths.Config) -> None:
    record(config, "concept", "Sandbox profile")
    with pytest.raises(ValueError, match="taken by concepts/sandbox-profile.md"):
        record(config, "decision", "Sandbox profile")


def test_an_overlong_title_is_bounded(config: paths.Config) -> None:
    path = record(config, "note", "x" * 400)
    assert len(path.stem) <= brain.MAX_SLUG
    assert feature.check(config) == []


def test_a_title_with_no_ascii_words_gets_a_hashed_id(config: paths.Config) -> None:
    first = record(config, "concept", "\u30c7\u30e2")
    second = record(config, "concept", "\u4f8b")
    assert first.stem.startswith("entry-") and first.stem != second.stem


def test_a_role_key_is_not_an_author(config: paths.Config) -> None:
    write(config.path("brain_root"), "concepts", "by-a-role", kind="concept",
          author="repository-owner")
    assert any("not a developer" in line for line in feature.check(config))
