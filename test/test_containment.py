"""Exercise the containment check (REQ-015 R12, R13) against small git repositories."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.governance import containment
from src.governance.__main__ import ROOT, audit, audit_backlog

SYSTEMS = [
    {"id": "sys-app", "paths": ["src/app"]},
    {"id": "sys-docs", "paths": ["docs/guides"]},
]


def phase(key: str, status: str, **changes: Any) -> dict[str, Any]:
    return {
        "id": key,
        "systems": ["sys-app"],
        "status": status,
        "deliverables": ["src/app/main.py"],
        **changes,
    }


class Repo:
    """A throwaway repository whose `dev` history is built one commit at a time."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.git("init", "-q", "-b", "dev")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        ).stdout

    def commit(
        self, message: str, files: dict[str, str], items: list[dict[str, Any]] | None = None
    ) -> str:
        if items is not None:
            files = {
                **files,
                containment.BACKLOG: yaml.safe_dump({"items": items}, sort_keys=False),
            }
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD").strip()


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    """phase-app-01 is claimed, works and completes while phase-peer-01 runs alongside it."""
    repo = Repo(tmp_path)
    queued = [phase("phase-app-01", "queued"), phase("phase-peer-01", "queued")]
    repo.commit("Register the phases", {"README.md": "x\n"}, queued)
    # An older phase that entered the backlog already complete has no claim to bound it.
    items = [*queued, phase("phase-old-01", "complete")]
    repo.commit("Record phase-old-01 as already complete", {}, items)
    items = [phase("phase-app-01", "active"), items[1], items[2]]
    repo.commit("Take it", {"docs/08-governance/catalog.md": "1\n"}, items)
    items = [items[0], phase("phase-peer-01", "active"), items[2]]
    repo.commit("Claim phase-peer-01", {}, items)
    repo.commit("Build the app", {"src/app/main.py": "ok\n", "src/app/extra.py": "x\n"})
    repo.commit("Peer work (phase-peer-01)", {"src/peer.py": "peer\n"})
    repo.commit("A note nobody labelled", {"docs/guides/note.md": "n\n"})
    # A registering commit names the phase it adds; that phase is not active, so it is kept.
    items = [*items, phase("phase-new-01", "queued")]
    repo.commit("Register phase-new-01", {}, items)
    repo.commit(
        "Record the session", {"docs/03-sessions/SESS-app.md": "s\n", "_data/ideas.jsonl": "{}\n"}
    )
    items = [phase("phase-app-01", "complete", session="doc-session-app"), *items[1:]]
    repo.commit("Complete phase-app-01", {"docs/08-governance/catalog.md": "2\n"}, items)
    return repo


DOCUMENTS = {"doc-session-app": {"path": "docs/03-sessions/SESS-app.md"}}


def completed(repo: Repo, key: str) -> containment.Report:
    commits, changes = containment.history(repo.root)
    items = {
        item["id"]: item
        for item in yaml.safe_load((repo.root / containment.BACKLOG).read_text())["items"]
    }
    return containment.completed_report(items[key], commits, changes, SYSTEMS, DOCUMENTS)


def test_completed_mode_names_the_phase_and_its_undeclared_files(repo: Repo) -> None:
    """REQ-015 R12, completed-phase mode: a known undeclared path is named with its phase."""
    report = completed(repo, "phase-app-01")
    assert report.phase == "phase-app-01"
    assert dict(report.files) == {
        "src/app/extra.py": "inside declared system sys-app: declaration may be too narrow",
        "docs/guides/note.md": "outside declared systems; owned by sys-docs",
    }
    # Another phase's backlog entry counts; the phase's own status edits do not.
    assert report.entries == ["phase-new-01"]
    # The peer's claim commit and its work commit both name phase-peer-01 while it is active.
    assert "2 dropped as a peer's" in report.span


def test_peer_commits_and_protocol_writes_are_not_findings(repo: Repo) -> None:
    paths = {path for path, _ in completed(repo, "phase-app-01").files}
    assert "src/peer.py" not in paths  # names phase-peer-01, active at the time
    assert not paths & {
        "docs/08-governance/catalog.md",
        "_data/ideas.jsonl",
        "docs/03-sessions/SESS-app.md",
        containment.BACKLOG,
        "src/app/main.py",
    }


def test_the_claim_is_found_from_status_not_from_a_subject(repo: Repo) -> None:
    """The claim commit's subject ("Take it") names no phase; the status change locates it."""
    commits, changes = containment.history(repo.root)
    found = containment.locate("phase-app-01", commits, changes)
    assert isinstance(found, containment.Located)
    assert repo.git("log", "-1", "--format=%s", found.claim).strip() == "Take it"


def test_a_phase_with_no_claim_on_history_is_reported_not_guessed(repo: Repo) -> None:
    report = completed(repo, "phase-old-01")
    assert report.note == (
        "not locatable: entered the backlog already complete, with no claim on this history"
    )
    assert not report.files


def test_branch_mode_names_the_undeclared_file(repo: Repo) -> None:
    """REQ-015 R12, active-branch mode: a scratch branch with one undeclared file names it."""
    repo.git("switch", "-q", "-c", "agent/phase-new-01")
    repo.commit("Work on the branch", {"src/app/main.py": "v2\n", "src/stray.py": "s\n"})
    repo.commit("Record its session", {"docs/03-sessions/SESS-new.md": "s\n"})
    repo.git("switch", "-q", "dev")
    report = containment.branch_report(repo.root, phase("phase-new-01", "active"), SYSTEMS)
    assert report.files == [("src/stray.py", "outside declared systems; no system owns it")]
    assert report.entries == []


def test_branch_mode_counts_another_phases_backlog_entry(repo: Repo) -> None:
    items = yaml.safe_load((repo.root / containment.BACKLOG).read_text())["items"]
    repo.git("switch", "-q", "-c", "agent/phase-new-01")
    items[-1]["status"] = "active"
    items[1]["deliverables"] = ["src/peer.py", "src/more.py"]
    repo.commit("Claim and widen a peer", {}, items)
    repo.git("switch", "-q", "dev")
    report = containment.branch_report(repo.root, items[-1], SYSTEMS)
    assert report.entries == ["phase-peer-01"]


def test_a_declared_backlog_makes_other_entries_declared(repo: Repo) -> None:
    item = phase("phase-x-01", "active", deliverables=["docs/09-backlog/backlog.yaml"])
    _, others = containment.classify(item, set(), {"phase-y-01"}, SYSTEMS, set())
    assert others == []


@pytest.mark.parametrize(
    ("declared", "path", "expected"),
    [
        ("src/app/main.py", "src/app/main.py", True),
        ("src/app/", "src/app/deep/file.py", True),
        ("src/app", "src/app/file.py", True),
        ("src/app", "src/application.py", False),
        ("docs/**/*.md", "docs/a/b/c.md", True),
        ("docs/**/*.md", "docs/c.md", True),
        ("docs/*.md", "docs/a/c.md", False),
        ("test/test_*.py", "test/test_codes.py", True),
    ],
)
def test_deliverables_match_exactly_by_prefix_and_by_glob(
    declared: str, path: str, expected: bool
) -> None:
    assert containment.covers(declared, path) is expected


def test_report_only_cli_exits_zero_on_findings_and_writes_nothing(
    repo: Repo, monkeypatch: Any, capsys: Any
) -> None:
    """REQ-015 R13: findings exit 0, and neither the tree nor any ref changes."""
    from src.governance import __main__ as cli

    catalog = yaml.safe_load((repo.root / containment.BACKLOG).read_text())
    result = {"systems": SYSTEMS, "documents": DOCUMENTS}
    before = (repo.git("status", "--porcelain"), repo.git("show-ref"))
    monkeypatch.setattr(cli, "ROOT", repo.root)
    monkeypatch.setattr(cli, "audit", lambda _: ([], [], result))
    monkeypatch.setattr(cli, "audit_backlog", lambda _root, _result: ([], catalog))
    monkeypatch.setattr(cli, "audit_idea_priority", lambda _: [])
    monkeypatch.setattr(cli, "audit_status_regression", lambda _root, _catalog: ([], []))
    monkeypatch.setattr("sys.argv", ["governance", "--containment"])
    assert cli.main() == 0
    out = capsys.readouterr().out
    assert "phase-app-01: (claim" in out
    assert "  src/app/extra.py - inside declared system sys-app" in out
    assert "phase-old-01: not locatable" in out
    assert (
        out.strip().splitlines()[-1].startswith("Containment: 2 phases, 1 checked, 1 not located")
    )
    assert (repo.git("status", "--porcelain"), repo.git("show-ref")) == before


def test_unknown_or_unready_phase_is_an_error(repo: Repo) -> None:
    catalog = yaml.safe_load((repo.root / containment.BACKLOG).read_text())
    with pytest.raises(ValueError, match="unknown phase"):
        containment.run(repo.root, catalog, SYSTEMS, DOCUMENTS, "phase-zzz-01")
    with pytest.raises(ValueError, match="queued; only complete or active"):
        containment.run(repo.root, catalog, SYSTEMS, DOCUMENTS, "phase-new-01")


def test_repository_history_reports_the_known_phase_prog_cases() -> None:
    """The first run's known case: each phase-prog-* phase registers other phases in backlog.yaml
    without declaring it, including phase-prog-04 (3da1295) and phase-prog-05 (744d4c8). Walks
    HEAD rather than dev, which a CI checkout may not have as a local branch."""
    errors, _, result = audit(ROOT)
    assert errors == []
    _, catalog = audit_backlog(ROOT, result)
    items = {item["id"]: item for item in catalog["items"]}
    commits, changes = containment.history(ROOT, "HEAD")
    reports = {
        key: containment.completed_report(
            items[key], commits, changes, result["systems"], result["documents"]
        )
        for key in ("phase-prog-04", "phase-prog-05")
    }
    assert "phase-idg-01" in reports["phase-prog-04"].entries
    assert "phase-dgov-06" in reports["phase-prog-05"].entries
    for key, report in reports.items():
        assert key not in report.entries
        found = containment.locate(key, commits, changes)
        assert isinstance(found, containment.Located)
        shas = {commit.sha[:7] for commit in found.commits}
        assert {"phase-prog-04": "3da1295", "phase-prog-05": "744d4c8"}[key] in shas
