"""The partition sweep: its corpus, its pack, its record schema and where it may write."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import idea
import idea_corpus
import paths
import pytest
from conftest import PLUGIN_ROOT
from idea_corpus import CorpusError, Layout
from jsonschema import Draft7Validator
from test_no_source_references import scan

SKILL = PLUGIN_ROOT / "skills" / "partition-ideas" / "SKILL.md"
PACK = PLUGIN_ROOT / "docs" / "partition-pack.md"
SCHEMA = PLUGIN_ROOT / "schemas" / "idea-partition-record.schema.json"
STAGING = ".idea-realization/staging"


def iid(n: int) -> str:
    """An idea id, built rather than written, so no six-digit literal appears in the suite."""
    return f"{n:06d}"


def a_date() -> str:
    """A corpus date, built rather than written as a calendar date."""
    return dt.date(2030, 1, 2).isoformat()


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No configured value from the calling shell reaches a test."""
    for name in list(os.environ):
        if name.startswith(("IDEA_REALIZATION_", "CLAUDE_PLUGIN_OPTION_", "CLAUDE_PROJECT_DIR")):
            monkeypatch.delenv(name)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), "-c", "user.name=fixture", "-c", "user.email=fixture@example",
         *args], capture_output=True, text=True, check=True).stdout


def repository(path: Path, ignore_staging: bool = True) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q")
    if ignore_staging:
        (path / ".gitignore").write_text(f"/{STAGING}/\n")
    git(path, "add", "-A")
    git(path, "commit", "-q", "--allow-empty", "-m", "fixture")
    return path


def config_for(root: Path) -> paths.Config:
    return paths.resolve({"root": str(root)}, env={})


def fixture_log(root: Path) -> Path:
    """Four ideas: two triaged (one with two findings), one open, one discarded."""
    log = config_for(root).path("ideas_path")
    for n in range(1, 5):
        idea.add(f"Idea {n}", f"Body of idea {n}.", log)
    for n in (1, 2):
        idea.change_status(iid(n), "triaged", log=log)
    idea.annotate(iid(1), "agent-scout", "finding", "Relates to the export work.", log)
    idea.annotate(iid(1), "agent-scout", "finding", "A second, contradicting account.", log)
    idea.annotate(iid(2), "agent-scout", "finding", "Stands alone.", log)
    idea.change_status(iid(4), "discarded", log=log)
    return log


@pytest.fixture
def root(tmp_path: Path) -> Path:
    path = repository(tmp_path / "repo")
    fixture_log(path)
    return path


@pytest.fixture
def where(root: Path) -> Layout:
    return idea_corpus.layout(config_for(root))


# --- the corpus ------------------------------------------------------------------------------


def test_status_open_selects_open_ideas_and_the_manifest_records_it(where: Layout) -> None:
    facts = idea_corpus.build(where.idea_log, where.corpus, frozenset({"open"}), seed=7)
    manifest = json.loads((where.corpus / "manifest.json").read_text())
    assert manifest["status"] == ["open"]
    assert manifest["corpus_size"] == 1 == facts["corpus_size"]
    assert re.findall(r"^## (\d{6}) — ", (where.corpus / "corpus-R1.md").read_text(), re.M) \
        == [iid(3)]


def test_default_status_is_triaged_through_the_command_line(where: Layout, root: Path) -> None:
    assert idea_corpus.main(["build", "--root", str(root), "--seed", "3"]) == 0
    manifest = json.loads((where.corpus / "manifest.json").read_text())
    assert manifest["status"] == ["triaged"]
    assert manifest["corpus_size"] == 2
    assert manifest["layered_evidence"] == [iid(1)]
    assert manifest["exclusion_file"] is None and manifest["excluded"] == []


def test_the_control_corpus_never_mentions_findings(where: Layout) -> None:
    idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}), seed=1)
    control = (where.corpus / "corpus-R4.md").read_text()
    reader = (where.corpus / "corpus-R1.md").read_text()
    assert "finding" not in control.lower() and "LAYERED" not in control
    assert "A second, contradicting account." in reader and "LAYERED EVIDENCE" in reader


def test_an_exclusion_file_is_optional_and_leaves_its_ids_out(where: Layout,
                                                             tmp_path: Path) -> None:
    exclusions = tmp_path / "exclude.txt"
    exclusions.write_text(f"# not this one\n{iid(2)}\n\n")
    facts = idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}), exclusions)
    assert facts["excluded"] == [iid(2)] and facts["corpus_size"] == 1
    exclusions.write_text("not-an-id\n")
    with pytest.raises(CorpusError, match="not a six-digit idea id"):
        idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}), exclusions)


def test_an_unknown_status_and_an_empty_selection_are_refused(where: Layout) -> None:
    with pytest.raises(CorpusError, match="unrecognised status"):
        idea_corpus.parse_statuses("triaged,finished")
    with pytest.raises(CorpusError, match="nothing to build"):
        idea_corpus.build(where.idea_log, where.corpus, frozenset({"promoted"}))


def test_stats_writes_nothing(where: Layout) -> None:
    facts = idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}), stats=True)
    assert facts["corpus_size"] == 2 and not where.corpus.exists()


# --- where the sweep may write ---------------------------------------------------------------


def test_a_staging_directory_that_is_not_gitignored_stops_the_sweep_before_writing(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = repository(tmp_path / "repo", ignore_staging=False)
    fixture_log(root)
    where = idea_corpus.layout(config_for(root))
    assert idea_corpus.main(["locate", "--root", str(root)]) == 1
    assert "not gitignored" in capsys.readouterr().err
    assert idea_corpus.main(["build", "--root", str(root)]) == 1
    with pytest.raises(CorpusError, match="not gitignored"):
        idea_corpus.prompt(where, "R1")
    assert not where.staging.exists()


def test_a_staging_directory_outside_any_checkout_stops_the_sweep(
        root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A staging directory outside the repository is refused when the configuration is read,
    before the sweep's own gitignore check: exit 2, naming the option, and nothing written."""
    outside = tmp_path / "outside"
    args = ["--root", str(root), "--staging-dir", str(outside)]
    assert idea_corpus.main(["locate", *args]) == 2
    assert "staging_dir" in capsys.readouterr().err
    assert idea_corpus.main(["build", *args]) == 2
    assert not outside.exists()


def test_writing_the_corpus_leaves_the_primary_checkout_status_unchanged(where: Layout) -> None:
    before = idea_corpus.status_digest(where.primary)
    idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}))
    idea_corpus.prompt(where, "R1")
    assert idea_corpus.status_digest(where.primary) == before


def test_from_a_worktree_the_sweep_writes_into_the_primary_checkout(root: Path,
                                                                    tmp_path: Path) -> None:
    worktree = tmp_path / "worktrees" / "session"
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "log")
    git(root, "worktree", "add", "-q", "-b", "session", str(worktree))
    where = idea_corpus.layout(config_for(worktree))
    assert where.primary == root.resolve()
    assert where.staging == root.resolve() / STAGING
    assert where.partitions == worktree.resolve() / "ideas" / "partitions"


# --- the pack --------------------------------------------------------------------------------


def test_every_section_extracts_and_fills_completely(where: Layout) -> None:
    pack = PACK.read_text()
    draft = where.staging / f"idea-partition-{a_date()}.md"
    values = idea_corpus.prompt_values(where, draft)
    for section in idea_corpus.SECTIONS:
        text = idea_corpus.fill(idea_corpus.extract(pack, section), values)
        assert not idea_corpus.PLACEHOLDER.search(text), section
        assert text.startswith("Assess the current state") or section == "S", section


def test_a_missing_placeholder_value_is_refused() -> None:
    with pytest.raises(CorpusError, match="no value for {draft}"):
        idea_corpus.fill("read {draft}", {})


def test_the_control_section_never_mentions_findings() -> None:
    assert "finding" not in idea_corpus.extract(PACK.read_text(), "R4").lower()


def test_the_second_audit_names_the_draft_by_its_absolute_primary_checkout_path(
        root: Path, tmp_path: Path) -> None:
    worktree = tmp_path / "worktrees" / "session"
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "log")
    git(root, "worktree", "add", "-q", "-b", "session", str(worktree))
    where = idea_corpus.layout(config_for(worktree))
    idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}))
    with pytest.raises(CorpusError, match="needs --draft"):
        idea_corpus.prompt(where, "A2")
    _, markdown, _ = idea_corpus.name(where, a_date())
    markdown.write_text("draft")
    text = idea_corpus.prompt(where, "A2", markdown)
    primary = git(worktree, "worktree", "list", "--porcelain").splitlines()[0].split(" ", 1)[1]
    assert str(Path(primary).resolve() / STAGING / markdown.name) in text
    assert (where.corpus / "dispatch-A2.txt").read_text() == text
    stray = worktree / markdown.name
    stray.write_text("draft")
    with pytest.raises(CorpusError, match="not in the primary checkout's staging"):
        idea_corpus.prompt(where, "A2", stray)


def test_the_skill_does_not_stop_for_a_ruling_before_the_second_audit() -> None:
    text = SKILL.read_text()
    audit = text.split("## 6. Audit 2", 1)[1].split("\n## ", 1)[0]
    assert "**Stop.**" not in audit and "ruling" not in audit.replace("a ruling of its own", "")
    assert "prompt A2 --draft" in audit and "absolute" in audit


def test_the_source_reference_check_fails_on_a_pack_that_names_a_source_document(
        tmp_path: Path) -> None:
    assert scan(PACK.parent, set()) == []
    copy = tmp_path / "docs"
    copy.mkdir()
    shutil.copy(PACK, copy / PACK.name)
    with (copy / PACK.name).open("a") as handle:
        handle.write("\nExtracted from " + "PROMPT" + "-" + "34" + ".\n")
    assert [line.split(": ")[1] for line in scan(copy, set())] == ["document code"]


# --- the record ------------------------------------------------------------------------------


def a_record(ids: list[str], markdown: str, manifest: dict[str, Any] | None = None,
             ) -> dict[str, Any]:
    manifest = manifest or {"corpus_size": len(ids), "status": ["triaged"], "shuffle_seed": 5}
    return {
        "schema_version": 1,
        "corpus_date": a_date(),
        "markdown": markdown,
        "manifest": {k: manifest[k] for k in ("corpus_size", "status", "shuffle_seed")},
        "state": "proposed",
        "tracks": [{"name": "Exports", "groups": [{"name": "Export formats", "ideas": ids[:1]}],
                    "disposition": None}],
        "unbatched": [{"id": i, "reason": "no confident home"} for i in ids[1:]],
        "decline_candidates": {
            "nominated_by_both": [],
            "nominated_by_one": [{"id": ids[-1], "reason": "stale", "nominated_by": "R4"}],
        },
    }


def validator() -> Draft7Validator:
    return Draft7Validator(json.loads(SCHEMA.read_text()))


def test_a_fixture_record_validates() -> None:
    record = a_record([iid(1), iid(2)], f".idea-realization/staging/idea-partition-{a_date()}.md")
    assert list(validator().iter_errors(record)) == []


def test_a_record_with_a_seven_digit_id_fails() -> None:
    record = a_record([iid(1), f"{1:07d}"], f"idea-partition-{a_date()}.md")
    errors = [e.message for e in validator().iter_errors(record)]
    assert errors and all("does not match" in e for e in errors)


def draft_pair(where: Layout, ids: list[str]) -> tuple[Path, Path]:
    manifest = idea_corpus.read_manifest(where.corpus)
    assert manifest is not None
    _, markdown, record_path = idea_corpus.name(where, a_date())
    markdown.write_text(idea_corpus.run_stamp(manifest) + "\n# Exports\n\n## Export formats\n\n"
                        + "\n".join(f"- {i}" for i in ids) + "\n")
    relative = markdown.relative_to(where.primary).as_posix()
    record_path.write_text(json.dumps(a_record(ids, relative, manifest)))
    return markdown, record_path


def test_the_pair_check_passes_a_complete_draft_and_names_a_missing_id(where: Layout) -> None:
    idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}))
    markdown, record = draft_pair(where, [iid(1), iid(2)])
    assert idea_corpus.check_pair(markdown, record, where.corpus) == []
    data = json.loads(record.read_text())
    data["unbatched"] = []
    data["decline_candidates"]["nominated_by_one"] = []
    record.write_text(json.dumps(data))
    assert f"missing from the record: {iid(2)}" in idea_corpus.check_pair(markdown, record,
                                                                          where.corpus)


def test_accept_copies_the_pair_into_the_partitions_directory(where: Layout) -> None:
    idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}))
    markdown, record = draft_pair(where, [iid(1), iid(2)])
    copied_md, copied_json = idea_corpus.accept(where, markdown, record)
    accepted = json.loads(copied_json.read_text())
    assert accepted["state"] == "accepted"
    assert accepted["markdown"] == f"ideas/partitions/{markdown.name}"
    assert idea_corpus.check_pair(copied_md, copied_json, where.corpus) == []
    assert json.loads(record.read_text())["state"] == "proposed"
    with pytest.raises(CorpusError, match="never replaced"):
        idea_corpus.accept(where, markdown, record)


# --- resume or start, and naming -------------------------------------------------------------


def test_start_resumes_a_stamped_sweep_and_moves_an_accepted_one_aside(where: Layout) -> None:
    assert idea_corpus.start(where) == ["NEW: no manifest"]
    idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}))
    reply = where.corpus.parent / "reply.md"
    reply.write_text("the report")
    idea_corpus.write_report(where, "R1", reply.read_text())
    lines = idea_corpus.start(where)
    assert lines[0].startswith("RESUME") and "report-R1.md" in lines[1]
    with pytest.raises(CorpusError, match="already holds"):
        idea_corpus.write_report(where, "R1", "again")

    markdown, record = draft_pair(where, [iid(1), iid(2)])
    idea_corpus.accept(where, markdown, record)
    lines = idea_corpus.start(where, today=a_date())
    assert lines[0].startswith("NEW: the manifest in place (accepted in")
    assert f"moved manifest.json -> previous-{a_date()}/manifest.json" in lines
    assert not (where.corpus / "manifest.json").exists()


def test_name_continues_this_sweeps_draft_and_suffixes_an_earlier_one(where: Layout) -> None:
    idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}), seed=1)
    markdown, _ = draft_pair(where, [iid(1), iid(2)])
    note, again, _ = idea_corpus.name(where, a_date())
    assert note is not None and note.startswith("CONTINUE") and again == markdown
    idea_corpus.build(where.idea_log, where.corpus, frozenset({"triaged"}), seed=2)
    note, fresh, _ = idea_corpus.name(where, a_date())
    assert note is None and fresh.name == f"idea-partition-{a_date()}-2.md"
