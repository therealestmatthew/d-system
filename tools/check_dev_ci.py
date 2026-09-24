#!/usr/bin/env python3
"""Report whether CI passed on `dev`'s head commit, so the Session Manager grants on a green `dev`.

The Session Manager runs this before it grants a `claim`, `dryrun` or `merge` turn in the primary
checkout (GOV-017's lock section, PROMPT-037 item 1):

    uv run python tools/check_dev_ci.py                 # dev's head, one query
    uv run python tools/check_dev_ci.py --wait 600      # poll until green or red, up to 10 minutes
    uv run python tools/check_dev_ci.py --commit <sha>  # any commit pushed to dev

It asks `gh run list --workflow ci.yaml --commit <sha>` for the runs of that commit and keeps
only `push` runs on the `dev` branch whose head is exactly that commit, so a `pull_request` run
or a second workflow cannot satisfy the check. It then reads the most recent completed run:

- exit 0: that run's conclusion is `success`;
- exit 1: it is `failure`, `timed_out` or `startup_failure`; the run's URL is printed;
- exit 2: the result is not known. No completed run exists for the commit (CI not started or
  still running), the latest completed run was `cancelled`, `skipped` or `neutral` or has a
  conclusion this script does not recognise, local `dev` differs from `origin/dev` (dev is not
  pushed), or `git` or `gh` failed.

Exit 2 fails closed: no grant while the result is unknown, unless the owner rules otherwise for
that grant. The conclusion mapping and the choice of gated turns are owner rulings of 2026-09-24.
With `--wait`, the script re-queries every `--interval` seconds while the answer is exit 2 and
stops at the first 0 or 1; a timeout exits 2.

The commit defaults to `git rev-parse dev`, not `HEAD`, so the answer is the same from a worktree
as from the primary checkout. With `--commit`, the pushed-dev comparison is skipped and the value
is expanded to a full SHA with `git rev-parse`.

See REQ-028 R06 and PLAN-045 D6 (docs/01-plans/PLAN-045-deterministic-guards.md), phase-grd-02.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent

WORKFLOW = "ci.yaml"
BRANCH = "dev"
EVENT = "push"
JSON_FIELDS = "databaseId,status,conclusion,url,headSha,event,headBranch,workflowName,createdAt"

GREEN = {"success"}
RED = {"failure", "timed_out", "startup_failure"}
# cancelled, skipped, neutral and anything unrecognised: not known, so exit 2.

Runner = Callable[[list[str]], "subprocess.CompletedProcess[str]"]


@dataclass(frozen=True)
class Verdict:
    code: int
    message: str


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)


def _rev_parse(ref: str, run: Runner) -> str | None:
    try:
        result = run(["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"])
    except OSError:
        return None
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def resolve_commit(run: Runner) -> tuple[str | None, Verdict | None]:
    """Return dev's head, or a verdict of 2 when git fails or dev is not pushed."""
    local = _rev_parse(BRANCH, run)
    if local is None:
        return None, Verdict(2, f"unknown: git could not resolve {BRANCH}")
    remote = _rev_parse(f"origin/{BRANCH}", run)
    if remote is None:
        return None, Verdict(2, f"unknown: git could not resolve origin/{BRANCH}")
    if local != remote:
        return None, Verdict(
            2,
            f"unknown: dev is not pushed ({BRANCH} is {local[:7]}, origin/{BRANCH} is "
            f"{remote[:7]}); push dev, then wait for its CI run",
        )
    return local, None


def query_runs(commit: str, run: Runner) -> tuple[list[dict[str, Any]] | None, str]:
    """Return gh's run list for the commit, or None and the reason gh failed."""
    args = ["gh", "run", "list", "--workflow", WORKFLOW, "--commit", commit,
            "--limit", "50", "--json", JSON_FIELDS]
    try:
        result = run(args)
    except OSError as exc:
        return None, f"gh could not run: {exc}"
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip() or f"exit {result.returncode}"
        return None, f"gh failed: {detail}"
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, f"gh returned invalid JSON: {exc}"
    if not isinstance(data, list):
        return None, "gh returned JSON that is not a list"
    return [r for r in data if isinstance(r, dict)], ""


def judge(commit: str, runs: list[dict[str, Any]]) -> Verdict:
    """Map the runs for one commit to 0, 1 or 2."""
    short = commit[:7]
    relevant = [
        r for r in runs
        if r.get("headSha") == commit and r.get("event") == EVENT and r.get("headBranch") == BRANCH
    ]
    completed = [r for r in relevant if r.get("status") == "completed"]
    if not completed:
        pending = [r for r in relevant if r.get("status") != "completed"]
        if pending:
            latest = max(pending, key=lambda r: str(r.get("createdAt", "")))
            return Verdict(
                2, f"unknown: CI for {short} is {latest.get('status')}: {latest.get('url')}"
            )
        return Verdict(2, f"unknown: no {EVENT} run of {WORKFLOW} on {BRANCH} for {short}")
    latest = max(completed, key=lambda r: str(r.get("createdAt", "")))
    conclusion = str(latest.get("conclusion", ""))
    url = latest.get("url")
    if conclusion in GREEN:
        return Verdict(0, f"green: CI succeeded for {short}: {url}")
    if conclusion in RED:
        return Verdict(1, f"red: CI {conclusion} for {short}: {url}")
    ended = conclusion or "without a conclusion"
    return Verdict(2, f"unknown: CI for {short} ended {ended}: {url}")


def check(commit: str | None, run: Runner = _run) -> Verdict:
    """One query: resolve the commit unless given, ask gh, and judge the result."""
    if commit is None:
        commit, early = resolve_commit(run)
        if early is not None:
            return early
    else:
        # gh reports full SHAs, so a short one given on the command line is expanded first.
        full = _rev_parse(commit, run)
        if full is None:
            return Verdict(2, f"unknown: git could not resolve {commit}")
        commit = full
    assert commit is not None
    runs, error = query_runs(commit, run)
    if runs is None:
        return Verdict(2, f"unknown: {error}")
    return judge(commit, runs)


def check_with_wait(
    commit: str | None,
    wait: float,
    interval: float,
    run: Runner = _run,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> Verdict:
    """Re-check while the answer is 2, until a 0 or 1 or until `wait` seconds have passed."""
    deadline = clock() + wait
    verdict = check(commit, run)
    while verdict.code == 2 and clock() + interval <= deadline:
        sleep(interval)
        verdict = check(commit, run)
    if verdict.code == 2 and wait > 0:
        return Verdict(2, f"{verdict.message} (still unknown after waiting {wait:g} s)")
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--commit",
                        help="check this commit instead of dev's head (skips the pushed-dev check)")
    parser.add_argument("--wait", type=float, default=0.0,
                        help="seconds to keep re-checking while the result is unknown (default 0)")
    parser.add_argument("--interval", type=float, default=30.0,
                        help="seconds between checks when --wait is set (default 30)")
    args = parser.parse_args(argv)
    if args.wait < 0 or args.interval <= 0:
        parser.error("--wait must be >= 0 and --interval > 0")
    verdict = check_with_wait(args.commit, args.wait, args.interval)
    print(verdict.message)
    return verdict.code


if __name__ == "__main__":
    sys.exit(main())
