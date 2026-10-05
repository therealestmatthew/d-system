"""When a requirement document is mandatory for a plan (REQ-015 R01-R03).

The rule (recorded in GOV-001's "When a requirement document is mandatory" section): a plan needs
a standalone `requirement`-kind document once it is registered as more than one phase in
`docs/09-backlog/backlog.yaml` — more than one item whose `plan` field names it. A plan realized as
zero or one backlog phase keeps its acceptance in its own body.

Enforcement is forward-only. `GRANDFATHERED_PLAN_IDS` is the fixed list of plan ids that, at the
time this rule was written (classified by `unpaired_mandatory_plans()` against the corpus on
`dev`), met the mandatory condition and had no paired requirement. Enforcing the rule against them
immediately would turn `dev` red on work written before the rule existed, so they are exempt by id,
permanently, rather than by a blanket "existing plan" carve-out that would also cover a plan
created tomorrow.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

# Classified 2026-10-05 against the corpus on `dev` at commit 72e405b (phase-dgov-01). A plan
# leaves this list only by gaining a paired requirement document, never by editing the list.
GRANDFATHERED_PLAN_IDS: frozenset[str] = frozenset(
    {
        "doc-agent-memory",
        "doc-mini-systems",
        "doc-reliability-follow-up",
        "doc-confidentiality-sweep",
        "doc-session-lifecycle",
        "doc-terminology-system",
        "doc-tooling-documentation",
        "doc-governance-model",
        "doc-idea-record-system",
        "doc-standalone-explorations-housekeeping",
        "doc-html-00-overview",
        "doc-lit-campaign",
    }
)


def phase_counts(items: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    """How many backlog items register each plan id, keyed by the item's `plan` field."""
    counts: dict[str, int] = {}
    for item in items:
        plan = item.get("plan")
        if plan:
            counts[plan] = counts.get(plan, 0) + 1
    return counts


def requirement_mandatory(count: int) -> bool:
    """The rule itself: more than one registered phase makes a requirement mandatory."""
    return count > 1


def is_paired(depends_on: Iterable[str], documents: Mapping[str, Mapping[str, Any]]) -> bool:
    """A plan is paired when it depends on at least one `requirement`-kind document."""
    return any(documents.get(dep, {}).get("kind") == "requirement" for dep in depends_on)


def unpaired_mandatory_plans(
    documents: Mapping[str, Mapping[str, Any]],
    items: Iterable[Mapping[str, Any]],
) -> list[tuple[str, Mapping[str, Any]]]:
    """Every plan meeting the mandatory condition with no paired requirement document.

    Returns `(plan_id, plan_document)` pairs, sorted by plan id, regardless of grandfathering —
    this is the classification REQ-015 R02 asks for. Callers that enforce (R03) filter out
    `GRANDFATHERED_PLAN_IDS` themselves.
    """
    counts = phase_counts(items)
    results: list[tuple[str, Mapping[str, Any]]] = []
    for plan_id, meta in documents.items():
        if meta.get("kind") != "plan":
            continue
        count = counts.get(plan_id, 0)
        if not requirement_mandatory(count):
            continue
        if is_paired(meta.get("depends_on", []), documents):
            continue
        results.append((plan_id, meta))
    return sorted(results, key=lambda pair: pair[0])


def inspect_requirement_pairing(
    documents: Mapping[str, Mapping[str, Any]],
    items: Iterable[Mapping[str, Any]],
) -> list[str]:
    """Enforcement errors (REQ-015 R03): unpaired mandatory plans, minus the grandfathered list."""
    errors = []
    for plan_id, meta in unpaired_mandatory_plans(documents, items):
        if plan_id in GRANDFATHERED_PLAN_IDS:
            continue
        errors.append(
            f"{meta['path']}: plan {plan_id} is registered as more than one backlog phase and "
            "needs a standalone requirement document (depends_on a `requirement`-kind document); "
            "see GOV-001's requirement-mandatory rule"
        )
    return errors


def render_classification(
    documents: Mapping[str, Mapping[str, Any]],
    items: Iterable[Mapping[str, Any]],
) -> str:
    """Human-readable classification output for `--classify-requirements` (REQ-015 R02)."""
    unpaired = unpaired_mandatory_plans(documents, items)
    lines = ["# Plans requiring a requirement document with none paired", ""]
    if not unpaired:
        lines.append("None.")
    else:
        for plan_id, meta in unpaired:
            grandfathered = " (grandfathered)" if plan_id in GRANDFATHERED_PLAN_IDS else ""
            lines.append(f"- {plan_id} ({meta['path']}){grandfathered}")
    lines += ["", f"Unpaired mandatory plans: {len(unpaired)}."]
    return "\n".join(lines)
