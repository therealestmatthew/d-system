"""Control CI: every actions/checkout step leaves no credential in the checkout's git config."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

IRR = Path(__file__).resolve().parent.parent
CONTROL_CI = IRR / ".github" / "workflows" / "control-ci.yml"


def checkout_steps(text: str) -> list[dict[str, Any]]:
    workflow = yaml.safe_load(text)
    return [step for job in workflow["jobs"].values() for step in job["steps"]
            if str(step.get("uses", "")).startswith("actions/checkout@")]


def test_every_checkout_turns_off_persisted_credentials() -> None:
    steps = checkout_steps(CONTROL_CI.read_text(encoding="utf-8"))
    assert len(steps) == 2, "the control checkout and the read-only product checkout"
    for step in steps:
        assert (step.get("with") or {}).get("persist-credentials") is False, step


PRODUCT_CI = IRR / "templates" / "product-repo" / ".github" / "workflows" / "product-ci.yml"
PULL_REQUESTS_ONLY = "${{ github.event_name == 'pull_request' }}"


def test_every_product_checkout_turns_off_persisted_credentials() -> None:
    steps = checkout_steps(PRODUCT_CI.read_text(encoding="utf-8"))
    assert steps
    for step in steps:
        assert (step.get("with") or {}).get("persist-credentials") is False, step


def setup_uv_versions(path: Path) -> set[str]:
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {str(step["uses"]).split("@", 1)[1] for job in workflow["jobs"].values()
            for step in job["steps"] if str(step.get("uses", "")).startswith("astral-sh/setup-uv@")}


def test_both_workflows_pin_the_same_full_setup_uv_version() -> None:
    control, product = setup_uv_versions(CONTROL_CI), setup_uv_versions(PRODUCT_CI)
    assert len(control) == 1 and control == product, (control, product)
    assert next(iter(control)).count(".") == 2, "a full version, not a moving major tag"


def test_only_pull_request_runs_are_cancelled_in_both_workflows() -> None:
    """A newer push to a pull request makes its older run useless; a run on dev (bookkeeping
    commits land there back to back) or main must finish."""
    for path in (CONTROL_CI, PRODUCT_CI):
        concurrency = yaml.safe_load(path.read_text(encoding="utf-8"))["concurrency"]
        assert concurrency["cancel-in-progress"] == PULL_REQUESTS_ONLY, path.name
