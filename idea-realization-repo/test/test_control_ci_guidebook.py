"""Control CI fails when docs/guidebook.html is stale against the documents it is built from."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

IRR = Path(__file__).resolve().parent.parent
CONTROL_CI = IRR / ".github" / "workflows" / "control-ci.yml"
COMMAND = "uv run python tools/build_guidebook.py --check"


def steps() -> list[dict[str, Any]]:
    workflow = yaml.safe_load(CONTROL_CI.read_text(encoding="utf-8"))
    return [step for job in workflow["jobs"].values() for step in job["steps"]]


def test_a_step_runs_the_guidebook_staleness_check() -> None:
    names = [step.get("name") for step in steps()]
    matching = [step for step in steps() if COMMAND in str(step.get("run", ""))]
    assert len(matching) == 1, f"no single step runs {COMMAND!r}: {names}"
    step = matching[0]
    assert "working-directory" not in step, "the generator runs from the repository root"
    assert not step.get("continue-on-error"), "a stale guidebook must fail the job"
    install = names.index("Install dependencies")
    assert names.index(step.get("name")) > install, "the check needs the installed dependencies"
