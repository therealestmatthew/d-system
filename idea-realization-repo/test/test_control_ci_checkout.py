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
