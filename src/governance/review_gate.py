"""The S3 `next_up` rule: a queued phase needs a dispositioned review record (REQ-028 R12).

A phase in `next_up` passes only when a `GOV-018` review record under
`docs/08-governance/reviews/` lists it in `target.phases` or `target.later_added_phases`, has
`status: dispositioned`, and has no finding whose current (last) disposition is `escalated-g3`
(PLAN-045 D11). Records are matched by phase id, which the owner's standing rule on id reuse
makes safe (PLAN-045 OQ8).

Only the record files directly in that directory are read. Its subdirectories hold build-review
verdicts and sampler draws (`REQ-030`), which are a different record and list no plan's phases.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

REVIEWS_DIR = "docs/08-governance/reviews"

# The 19 phases in next_up on dev at f1b891d, exempt by the owner's ruling on idea 000394 and
# listed in REQ-028 R12. A literal set, so the exemption cannot grow without an edit here that a
# reviewer sees.
EXEMPT = frozenset(
    {
        "phase-part-03",
        "phase-cap-08",
        "phase-irs-14",
        "phase-irs-11",
        "phase-idg-01",
        "phase-idg-11",
        "phase-dgov-01",
        "phase-idg-12",
        "phase-irs-05",
        "phase-irs-07",
        "phase-irs-13",
        "phase-irs-08",
        "phase-irs-09",
        "phase-irs-15",
        "phase-agx-03",
        "phase-irs-10",
        "phase-irs-02",
        "phase-irs-12",
        "phase-irs-17",
    }
)


def listed_phases(record: Mapping[str, Any]) -> set[str]:
    """The phases a record reviewed, at either altitude."""
    target = record.get("target") or {}
    return set(target.get("phases") or []) | set(target.get("later_added_phases") or [])


def escalated(record: Mapping[str, Any]) -> list[str]:
    """Ids of the findings whose current (last) disposition is escalated-g3."""
    found = []
    for finding in record.get("findings") or []:
        dispositions = finding.get("dispositions") or []
        if dispositions and dispositions[-1].get("value") == "escalated-g3":
            found.append(str(finding.get("id")))
    return found


def refusal(path: str, record: Mapping[str, Any]) -> str | None:
    """Why a record that lists the phase does not clear it, or None when it does."""
    if record.get("status") != "dispositioned":
        return f"{path} is {record.get('status')}"
    ids = escalated(record)
    if ids:
        return f"{path} has {', '.join(ids)} escalated-g3"
    return None


def inspect_review_gate(
    next_up: Iterable[str], records: Mapping[str, Mapping[str, Any]]
) -> tuple[list[str], dict[str, int]]:
    """Return one error per refused next_up phase, and the counts that show what was checked."""
    errors: list[str] = []
    checked = exempted = 0
    for phase in next_up:
        if phase in EXEMPT:
            exempted += 1
            continue
        checked += 1
        reasons = []
        for path, record in sorted(records.items()):
            if phase not in listed_phases(record):
                continue
            reason = refusal(path, record)
            if reason is None:
                break
            reasons.append(reason)
        else:
            detail = "; ".join(reasons) if reasons else "no record lists it"
            errors.append(
                f"next_up: {phase} has no dispositioned review record under {REVIEWS_DIR}/ "
                f"without an escalated-g3 finding ({detail}) (REQ-028 R12)"
            )
    counts = {"records": len(records), "phases_checked": checked, "phases_exempt": exempted}
    return errors, counts
