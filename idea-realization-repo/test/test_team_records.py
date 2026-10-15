"""The shipped control repository names a decision record, so the status-regression check runs."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import yaml

IRR = Path(__file__).resolve().parent.parent


def test_the_backlog_names_the_team_decisions_log() -> None:
    backlog = yaml.safe_load((IRR / "backlog" / "backlog.yaml").read_text(encoding="utf-8"))
    assert backlog.get("decision_record") == "doc-team-decisions"
    record = next((IRR / "docs" / "governance").glob("GOV-*-team-decisions.md"))
    assert "id: doc-team-decisions" in record.read_text(encoding="utf-8")


def test_the_check_runs_the_status_regression_check() -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("IDEA_REALIZATION_",
                                                                     "CLAUDE_PLUGIN_OPTION_"))}
    env["IDEA_REALIZATION_ROOT"] = str(IRR)
    result = subprocess.run(["uv", "run", "plugins/idea-realization/scripts/check.py"], cwd=IRR,
                            env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "status-regression not run" not in result.stdout + result.stderr
