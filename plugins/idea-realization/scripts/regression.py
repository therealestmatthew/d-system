# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
"""Fail when a phase silently leaves ``status: complete`` in the backlog.

Every other backlog rule reads the current catalog alone, so none of them can see a phase moving
backwards — a backlog rewritten from a stale copy, reverting finished phases and deleting their
``session``, ``completion_evidence`` and ``result``, passes them all. This check compares the
current catalog with a prior committed state.

**Two bases, two severities:**

- ``HEAD`` catches a bad edit before it is committed, in the tree that makes it. A finding here
  is an **error**.
- The integration branch catches the same regression arriving by rebase or merge, which
  ``HEAD`` structurally cannot see. It cannot be a hard failure: every branch that legitimately
  completes a phase differs from the integration branch by exactly the transition this check
  looks for. A finding here is a **warning** that never changes the exit code.

**The escape hatch is a grep, not a parse** (``is_recorded``): the check looks for the phase id
as a whole identifier in the working copy of the decisions document and not in the version
committed at the comparison ref — i.e. the entry was added by this change. The goal is to force
the reason for a reopen to be written down somewhere durable, not to validate its shape.

**The decisions document is the one the catalog's ``decision_record`` names**, resolved to a
path by the caller through the document scan, never a literal filename. A catalog without
``decision_record`` has no escape hatch, so the caller does not run this check and says so.

**An unreadable prior state is not a failure.** ``git show <ref>:<path>`` fails during a rebase,
in a shallow clone, on the initial commit, or when ``ref`` itself does not exist. All of these
mean no comparison is possible: skip that base, note it in one line, and let the other base run.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

#: The fields that record a phase is finished. Losing any of them from a phase that stays
#: `complete` is itself a regression, independent of whether `status` also moved.
EVIDENCE_FIELDS = ("session", "completion_evidence", "result")


def bases(integration_branch: str) -> tuple[tuple[str, str], ...]:
    """`(git ref, severity)` pairs this check runs: the hard failure first."""
    return (("HEAD", "error"), (integration_branch, "warning"))


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
    """Phases present in both states that left `complete` or kept it while losing evidence that
    it happened. A phase absent from either state is not this check's concern — that is an
    addition or a removal, not a regression."""
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


#: An HTML/markdown comment. Stripped before searching so a phase id hidden inside one — an
#: entry nobody would actually see rendered — cannot satisfy the escape hatch invisibly.
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

#: Characters that continue an identifier for the purpose of `_mentions`. Phase ids are
#: `[a-z]+` and digits joined by hyphens, so a hyphen counts as a "word" character here —
#: unlike `\b` in the `re` module, which treats `-` as a boundary and would let an id match
#: inside a longer hyphenated identifier that starts with it.
_ID_CHAR = re.compile(r"[A-Za-z0-9-]")


def _mentions(text: str, phase_id: str) -> bool:
    """Whether `phase_id` appears in `text` as a whole identifier, not as a piece of a longer
    one. Comments are stripped first (see `_COMMENT`). Guards the escape hatch against a
    decisions entry that merely contains the target as a prefix or suffix of a different
    phase id: an id one digit longer must not silence this one."""
    text = _COMMENT.sub("", text)
    start = 0
    while True:
        index = text.find(phase_id, start)
        if index == -1:
            return False
        before = text[index - 1] if index > 0 else ""
        after = text[index + len(phase_id)] if index + len(phase_id) < len(text) else ""
        if not _ID_CHAR.match(before) and not _ID_CHAR.match(after):
            return True
        start = index + 1


def is_recorded(prior_decisions: str | None, working_decisions: str, phase_id: str) -> bool:
    """The reversal is permitted when this change adds a decisions entry naming `phase_id`.

    A whole-identifier search, not a parse, by design (see module docstring) — deliberately
    loose about the *shape* of the entry, so an ordinary sentence naming the phase counts, but
    strict about *which* identifier it names: `phase_id` must appear as itself, not as a
    substring of a different phase id, and not only inside a comment. `prior_decisions` of
    `None` means the decisions document did not exist, or was unreadable, at the comparison
    ref; that is treated as "not previously mentioned", so any mention in the working copy
    counts as this change having recorded it.
    """
    if not _mentions(working_decisions, phase_id):
        return False
    if prior_decisions is None:
        return True
    return not _mentions(prior_decisions, phase_id)


def check(
    root: Path, ref: str, severity: str, catalog: Any, working_decisions: str,
    backlog_path: str, decisions_path: str,
) -> tuple[list[str], list[str]]:
    """Run the regression check against one base. Returns `(errors, warnings)`; only one side is
    ever non-empty for a single call, depending on `severity`. Both paths are relative to
    `root`, in git's forward-slash form."""
    prior_text = read_text_at(root, ref, backlog_path)
    if prior_text is None:
        return [], [
            f"status-regression: {ref} is unreadable, skipping the {ref}-relative comparison"
        ]
    try:
        prior = yaml.safe_load(prior_text)
    except yaml.YAMLError as exc:
        return [], [f"status-regression: {ref}'s backlog did not parse ({exc}), skipping"]
    findings = find_regressions(_phase_map(prior), _phase_map(catalog))
    if not findings:
        return [], []
    prior_decisions = read_text_at(root, ref, decisions_path)
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


def audit(
    root: Path, catalog: Any, backlog_path: str, decisions_path: str, integration_branch: str
) -> tuple[list[str], list[str]]:
    """Run the check against both bases: `HEAD` errors, the integration branch warns."""
    decisions_file = root / decisions_path
    working_decisions = (
        decisions_file.read_text(encoding="utf-8") if decisions_file.is_file() else ""
    )
    errors: list[str] = []
    warnings: list[str] = []
    for ref, severity in bases(integration_branch):
        ref_errors, ref_warnings = check(root, ref, severity, catalog, working_decisions,
                                         backlog_path, decisions_path)
        errors.extend(ref_errors)
        warnings.extend(ref_warnings)
    return errors, warnings
