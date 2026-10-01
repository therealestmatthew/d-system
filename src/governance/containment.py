"""Diff a phase's change set against its declared systems and deliverables (REQ-015 R12, R13).

Two modes share one classifier:

- **Completed phase.** The change set is every file touched on `dev`'s first-parent history from
  the phase's claim commit through its completion commit. Both commits are located from the
  phase's own `status` in `backlog.yaml`: the claim is the last change to `active` before the last
  change to `complete`. Commit subjects are not used, because many claims were never committed
  under a subject naming them. A commit in that range is dropped when its message names another
  phase that was active at that commit and does not name this one: that is a peer's interleaved
  work (owner ruling, 2026-10-01, narrowing REQ-015 R12's "names a different phase id" so a phase's
  own registering commits, which name the phases they register, are kept).
- **Active branch.** The change set is `dev...agent/<phase-id>`, so a READY can carry the output.

Writes every phase makes are not findings: its own `backlog.yaml` entry, the catalog, its session
record and the idea-log captures. A `backlog.yaml` edit counts only when it changes another phase's
entry. The check reports and never blocks, and it writes nothing: whether a finding is a
declaration that was too narrow or work that strayed is for a person to judge, so each finding
carries the evidence for that judgement (whether the file sits inside one of the phase's declared
systems) rather than a verdict.

Read-only: it runs `git log`, `git show`, `git diff` and `git merge-base`, and changes no file
and no ref.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

BACKLOG = "docs/09-backlog/backlog.yaml"
SESSIONS = "docs/03-sessions/"
# Protocol writes every phase makes, whatever it declares (REQ-015 R12).
EXEMPT_FILES = {"docs/08-governance/catalog.md", "_data/ideas.jsonl", "docs/00-working/ideas.md"}

PHASE_ID = re.compile(r"phase-[a-z]+-[0-9]{2}")
ENTRY = re.compile(r"^- id: (phase-[a-z]+-[0-9]{2})\s*$", re.M)
STATUS = re.compile(r"^  status: (\w+)\s*$", re.M)


@dataclass
class Commit:
    """One commit on `dev`'s first-parent history, oldest first."""

    sha: str
    names: set[str]
    files: list[str]
    # Phases whose backlog entry this commit changed, added or removed.
    entries: set[str] = field(default_factory=set)
    # Phases active immediately before and after this commit.
    active: set[str] = field(default_factory=set)


@dataclass
class Located:
    claim: str
    completion: str
    commits: list[Commit]
    dropped: list[Commit]


@dataclass
class Report:
    phase: str
    mode: str
    span: str
    files: list[tuple[str, str]] = field(default_factory=list)
    entries: list[str] = field(default_factory=list)
    note: str = ""


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    ).stdout


def entry_blocks(text: str) -> dict[str, str]:
    """Each phase's entry text in one backlog.yaml revision, keyed by phase id."""
    starts = [(match.start(), match.group(1)) for match in ENTRY.finditer(text)]
    ends = [start for start, _ in starts[1:]] + [len(text)]
    return {key: text[start:end] for (start, key), end in zip(starts, ends, strict=True)}


def entry_status(block: str) -> str | None:
    match = STATUS.search(block)
    return match.group(1) if match else None


def history(root: Path, ref: str = "dev") -> tuple[list[Commit], dict[str, list[tuple[int, str]]]]:
    """`ref`'s first-parent history, oldest first, and each phase's status changes along it.

    The status changes map a phase id to `(commit index, new status)` pairs. `-m` with
    `--first-parent` diffs a merge against its first parent, so the one merge on `dev` lists the
    files it brought in rather than nothing.
    """
    raw = git(
        root,
        "log",
        "--first-parent",
        "-m",
        "--reverse",
        "--name-only",
        "--format=%x00%H%x01%B%x01",
        ref,
    )
    commits: list[Commit] = []
    for record in raw.split("\x00")[1:]:
        sha, message, names = record.split("\x01", 2)
        commits.append(
            Commit(
                sha=sha.strip(),
                names=set(PHASE_ID.findall(message)),
                files=[line for line in names.splitlines() if line.strip()],
            )
        )
    changes: dict[str, list[tuple[int, str]]] = {}
    previous: dict[str, str] = {}
    active: set[str] = set()
    for index, commit in enumerate(commits):
        before = set(active)
        if BACKLOG in commit.files:
            try:
                blocks = entry_blocks(git(root, "show", f"{commit.sha}:{BACKLOG}"))
            except subprocess.CalledProcessError:
                blocks = {}
            commit.entries = {
                key for key in set(blocks) | set(previous) if blocks.get(key) != previous.get(key)
            }
            for key in commit.entries:
                status = entry_status(blocks.get(key, ""))
                if status and status != entry_status(previous.get(key, "")):
                    changes.setdefault(key, []).append((index, status))
            previous = blocks
            active = {key for key, block in blocks.items() if entry_status(block) == "active"}
        commit.active = before | active
    return commits, changes


def locate(
    phase: str, commits: list[Commit], changes: dict[str, list[tuple[int, str]]]
) -> Located | str:
    """The phase's claim-to-completion range, or the reason it cannot be located."""
    steps = changes.get(phase, [])
    done = [index for index, status in steps if status == "complete"]
    if not done:
        return "never marked complete on this history"
    completion = done[-1]
    claims = [index for index, status in steps if status == "active" and index < completion]
    if not claims:
        prior = [status for index, status in steps if index < completion]
        how = f"went {prior[-1]} -> complete" if prior else "entered the backlog already complete"
        return f"not locatable: {how}, with no claim on this history"
    kept: list[Commit] = []
    dropped: list[Commit] = []
    for commit in commits[claims[-1] : completion + 1]:
        peers = (commit.names & commit.active) - {phase}
        (dropped if peers and phase not in commit.names else kept).append(commit)
    return Located(commits[claims[-1]].sha, commits[completion].sha, kept, dropped)


def glob_match(path: str, pattern: str) -> bool:
    """Match a repository path against a glob, segment by segment; `**` spans any depth."""

    def match(parts: list[str], pieces: list[str]) -> bool:
        if not pieces:
            return not parts
        if pieces[0] == "**":
            return any(match(parts[skip:], pieces[1:]) for skip in range(len(parts) + 1))
        return (
            bool(parts)
            and fnmatch.fnmatchcase(parts[0], pieces[0])
            and match(parts[1:], pieces[1:])
        )

    return match(path.split("/"), pattern.rstrip("/").split("/"))


def covers(declared: str, path: str) -> bool:
    """A deliverable covers a file exactly, as a directory prefix, or as a glob pattern."""
    if any(char in declared for char in "*?["):
        return glob_match(path, declared)
    head = PurePosixPath(declared).parts
    return PurePosixPath(path).parts[: len(head)] == head


def owners(path: str, systems: list[dict[str, Any]]) -> list[str]:
    return sorted(
        item["id"] for item in systems if any(covers(value, path) for value in item["paths"])
    )


def classify(
    item: dict[str, Any],
    files: set[str],
    entries: set[str],
    systems: list[dict[str, Any]],
    session_paths: set[str],
) -> tuple[list[tuple[str, str]], list[str]]:
    """Undeclared files, each with the evidence a person needs, and other phases' entries edited."""
    deliverables = item["deliverables"]
    declared_backlog = any(covers(value, BACKLOG) for value in deliverables)
    findings = []
    for path in sorted(files):
        if path in EXEMPT_FILES or path in session_paths or path == BACKLOG:
            continue
        if any(covers(value, path) for value in deliverables):
            continue
        owning = owners(path, systems)
        inside = sorted(set(owning) & set(item["systems"]))
        if inside:
            reason = f"inside declared system {', '.join(inside)}: declaration may be too narrow"
        elif owning:
            reason = f"outside declared systems; owned by {', '.join(owning)}"
        else:
            reason = "outside declared systems; no system owns it"
        findings.append((path, reason))
    others = [] if declared_backlog else sorted(entries - {item["id"]})
    return findings, others


def completed_report(
    item: dict[str, Any],
    commits: list[Commit],
    changes: dict[str, list[tuple[int, str]]],
    systems: list[dict[str, Any]],
    documents: dict[str, Any],
) -> Report:
    found = locate(item["id"], commits, changes)
    if isinstance(found, str):
        return Report(item["id"], "completed", "", note=found)
    files = {path for commit in found.commits for path in commit.files}
    entries = {key for commit in found.commits for key in commit.entries}
    session = documents.get(item.get("session", ""), {}).get("path")
    findings, others = classify(item, files, entries, systems, {session} if session else set())
    span = (
        f"claim {found.claim[:7]}, completion {found.completion[:7]}; "
        f"{len(found.commits)} commits, {len(found.dropped)} dropped as a peer's"
    )
    return Report(item["id"], "completed", span, findings, others)


def branch_report(
    root: Path,
    item: dict[str, Any],
    systems: list[dict[str, Any]],
    documents: dict[str, Any] | None = None,
    base: str = "dev",
) -> Report:
    """Diff `base...agent/<phase-id>` against the phase's declaration.

    The phase's own session record is exempt: its recorded `session` path, or a record the branch
    adds, since an active phase's record is new on its branch. An edit to an existing session
    record is another session's record and is reported.
    """
    branch = f"agent/{item['id']}"
    status = git(root, "diff", "--name-status", "--no-renames", f"{base}...{branch}")
    changed = [line.split("\t", 1) for line in status.splitlines() if "\t" in line]
    files = {path for _, path in changed}
    entries: set[str] = set()
    sessions = {path for kind, path in changed if kind == "A" and path.startswith(SESSIONS)}
    own = (documents or {}).get(item.get("session", ""), {}).get("path")
    if own:
        sessions.add(own)
    if BACKLOG in files:
        fork = git(root, "merge-base", base, branch).strip()
        before = entry_blocks(git(root, "show", f"{fork}:{BACKLOG}"))
        after = entry_blocks(git(root, "show", f"{branch}:{BACKLOG}"))
        entries = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
    findings, others = classify(item, files, entries, systems, sessions)
    return Report(item["id"], "branch", f"{base}...{branch}", findings, others)


def render(reports: list[Report]) -> str:
    """Plain text: per phase, its span, then each finding; then the totals."""
    lines = []
    for report in reports:
        if report.note:
            lines.append(f"{report.phase}: {report.note}")
            continue
        if not report.files and not report.entries:
            lines.append(f"{report.phase}: no undeclared changes ({report.span})")
            continue
        lines.append(f"{report.phase}: ({report.span})")
        lines += [f"  {path} - {reason}" for path, reason in report.files]
        if report.entries:
            lines.append(
                f"  {BACKLOG} - edits {len(report.entries)} other phases' entries: "
                + ", ".join(report.entries)
            )
    checked = [report for report in reports if not report.note]
    flagged = [report for report in checked if report.files or report.entries]
    lines.append(
        f"Containment: {len(reports)} phases, {len(checked)} checked, "
        f"{len(reports) - len(checked)} not located, {len(flagged)} with findings "
        f"({sum(len(report.files) for report in flagged)} files, "
        f"{sum(1 for report in flagged if report.entries)} with other phases' backlog entries)"
    )
    return "\n".join(lines)


def run(
    root: Path,
    catalog: dict[str, Any],
    systems: list[dict[str, Any]],
    documents: dict[str, Any],
    phase: str = "",
) -> str:
    """Every completed phase, or one phase in the mode its status calls for."""
    items = {item["id"]: item for item in catalog["items"]}
    if phase and phase not in items:
        raise ValueError(f"unknown phase {phase}")
    if phase and items[phase]["status"] == "active":
        return render([branch_report(root, items[phase], systems, documents)])
    if phase and items[phase]["status"] != "complete":
        raise ValueError(f"{phase} is {items[phase]['status']}; only complete or active phases")
    commits, changes = history(root)
    chosen = [items[phase]] if phase else [i for i in items.values() if i["status"] == "complete"]
    return render([completed_report(item, commits, changes, systems, documents) for item in chosen])
