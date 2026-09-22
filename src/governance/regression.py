"""Fail when a phase silently leaves `status: complete` in `backlog.yaml` (REQ-010).

`5ecb203` rewrote `docs/09-backlog/backlog.yaml` from a stale copy and reverted four unrelated
phases — three `complete` and one `active` — to a state three phases old, deleting their
`session`, `completion_evidence` and `result` along the way. `uv run python -m src.governance`
exited 0 on both sides of that change: every existing rule reads the *current* backlog alone, so
none of them can see a phase moving backwards. This module is the first governance check that
needs a prior state to compare against, which is the only genuinely new thing about it.

**Two bases, two severities** (REQ-010 R6, owner ruling 2026-09-14):

- `HEAD` catches a bad edit before it is committed, in the tree that makes it — exactly how
  `5ecb203` happened. A finding here is an **error**.
- `dev` catches the same regression arriving by rebase or merge, which `HEAD` structurally
  cannot see. It cannot be a hard failure: every agent branch that legitimately completes a
  phase differs from `dev` by exactly the transition this check looks for. A finding here is a
  **warning** that never changes the exit code.

**The escape hatch is a grep, not a parse** (`is_recorded`): the check looks for the phase id as a
literal string in the working copy of `GOV-003-backlog-decisions.md` and not in the version
committed at the comparison ref — i.e. the entry was added by this change. That is deliberately
loose. The goal is to force the reason for a reopen to be written down somewhere durable, not to
validate the reason's shape; a stricter parse would invite working around it instead.

**An unreadable prior state is not a failure.** `git show <ref>:<path>` fails during a rebase, in
a shallow clone, on the initial commit, or when `ref` itself does not exist (a detached worktree,
a clone without `dev`). All of these mean the same thing here — no comparison is possible — and
are treated identically: skip that base, note it in one line, and let the other base's check run
unaffected.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

#: Where the backlog and its decision record live, relative to the repository root.
BACKLOG_PATH = "docs/09-backlog/backlog.yaml"
DECISIONS_PATH = "docs/08-governance/GOV-003-backlog-decisions.md"

#: The fields that record a phase is finished. Losing any of them from a phase that stays
#: `complete` is itself a regression (R2), independent of whether `status` also moved.
EVIDENCE_FIELDS = ("session", "completion_evidence", "result")

#: `(git ref, severity)` pairs this check runs, in REQ-010 R6's order: the hard failure first.
BASES = (("HEAD", "error"), ("dev", "warning"))


def read_text_at(root: Path, ref: str, path: str) -> str | None:
    """Return `path` as committed on `ref`, or `None` if that comparison cannot be made.

    A non-zero `git show` covers every case this check treats as "no comparison possible": the
    ref doesn't exist, the path doesn't exist at that ref, the tree is mid-rebase, or the clone
    is too shallow to have the commit. They are indistinguishable from here and mean the same
    thing, so they get the same answer.
    """
    try:
        completed = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout


def _phase_map(catalog: Any) -> dict[str, dict[str, Any]]:
    """Best-effort `id -> phase` map. Malformed input yields an empty map rather than raising —
    a prior state that fails to parse into phases is exactly the "no comparison possible" case."""
    if not isinstance(catalog, dict):
        return {}
    items = catalog.get("items")
    if not isinstance(items, list):
        return {}
    return {
        item["id"]: item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def find_regressions(
    prior_phases: dict[str, dict[str, Any]], current_phases: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Phases present in both states that left `complete` (R1) or kept it while losing evidence
    that it happened (R2). A phase absent from either state is not this check's concern — that is
    an addition or a removal, not a regression."""
    findings = []
    for phase_id, prior in prior_phases.items():
        if prior.get("status") != "complete":
            continue
        current = current_phases.get(phase_id)
        if current is None:
            continue
        lost = [field for field in EVIDENCE_FIELDS if prior.get(field) and not current.get(field)]
        current_status = current.get("status")
        if current_status != "complete" or lost:
            findings.append(
                {"phase": phase_id, "from": "complete", "to": current_status, "lost": lost}
            )
    return findings


def is_recorded(prior_decisions: str | None, working_decisions: str, phase_id: str) -> bool:
    """R3: the reversal is permitted when this change adds a `GOV-003` entry naming `phase_id`.

    A substring search, not a parse, by design (see module docstring). `prior_decisions` of
    `None` means `GOV-003` did not exist, or was unreadable, at the comparison ref; that is
    treated as "not previously mentioned", so any mention in the working copy counts as this
    change having recorded it.
    """
    if phase_id not in working_decisions:
        return False
    if prior_decisions is None:
        return True
    return phase_id not in prior_decisions


def check(
    root: Path, ref: str, severity: str, catalog: Any, working_decisions: str
) -> tuple[list[str], list[str]]:
    """Run the regression check against one base. Returns `(errors, warnings)`; only one side is
    ever non-empty for a single call, depending on `severity`."""
    prior_text = read_text_at(root, ref, BACKLOG_PATH)
    if prior_text is None:
        return [], [
            f"status-regression: {ref} is unreadable, skipping the {ref}-relative comparison"
        ]
    try:
        prior = yaml.safe_load(prior_text)
    except yaml.YAMLError as exc:
        return [], [f"status-regression: {ref}'s backlog.yaml did not parse ({exc}), skipping"]
    findings = find_regressions(_phase_map(prior), _phase_map(catalog))
    if not findings:
        return [], []
    prior_decisions = read_text_at(root, ref, DECISIONS_PATH)
    messages = []
    for finding in findings:
        if is_recorded(prior_decisions, working_decisions, finding["phase"]):
            continue
        lost = ", ".join(finding["lost"]) if finding["lost"] else "none"
        messages.append(
            f"status-regression ({ref}): {finding['phase']} complete -> {finding['to']} "
            f"(lost: {lost})"
        )
    if not messages:
        return [], []
    if severity == "error":
        return messages, []
    return [], [f"{message} [{ref}-relative, non-blocking]" for message in messages]


def audit(root: Path, catalog: Any) -> tuple[list[str], list[str]]:
    """Run the check against both bases REQ-010 R6 names: `HEAD` errors, `dev` warns."""
    decisions_path = root / DECISIONS_PATH
    working_decisions = (
        decisions_path.read_text(encoding="utf-8") if decisions_path.is_file() else ""
    )
    errors: list[str] = []
    warnings: list[str] = []
    for ref, severity in BASES:
        ref_errors, ref_warnings = check(root, ref, severity, catalog, working_decisions)
        errors.extend(ref_errors)
        warnings.extend(ref_warnings)
    return errors, warnings
