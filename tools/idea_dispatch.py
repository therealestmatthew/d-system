#!/usr/bin/env python3
"""Stopgap triage dispatch: a post-append hook plus a reconciling sweep.

`tools/append_idea.py` is never edited — this is a separate watcher script (owner ruling,
`phase-irs-01`'s batch open) that reads the idea log through `fold()` the same way every other
consumer does and dispatches the `idea-triage` role (`GOV-014`) headlessly for ideas the writer
appended. It is the stopgap named by `PLAN-039.01` SS10: `phase-irs-04`'s daemon absorbs this duty
into its own reconcile loop and retires this tool (see `docs/08-governance/OPS-016-idea-dispatch.md`
for the interim declaration).

**Three entry points, one shared core:**

- `watch` — the genuine automatic trigger (`REQ-022` R06). A long-running loop that polls the
  idea log every `--interval` seconds (default `DEFAULT_POLL_INTERVAL`, a few seconds) and
  dispatches each newly-created idea it finds, with no human action once the loop is started.
  Built on `poll_once`, the same seam a test drives directly to exercise one tick without a real
  sleep loop. Checks the halt flag before every individual dispatch attempt, not just once per
  tick, and isolates a failing or raising dispatch so the loop keeps running.
- `dispatch` — the one-shot form of the same core, meant to run right after
  `tools/append_idea.py add` succeeds if an operator prefers per-append invocation over `watch`
  (wire it into whatever calls the writer; nothing here modifies the writer to call it
  automatically, per the owner ruling that the writer must succeed even when dispatch fails).
  Finds every idea created after the install watermark that this tool has not yet dispatched,
  and dispatches each.
- `sweep` — the reconciling pass. Trusts only `fold()`'s status, never this tool's own memory of
  what it thinks it already sent: any post-watermark idea still `open` gets re-dispatched,
  whether the prior attempt failed, was killed mid-run, or the hook invocation was skipped
  entirely. This is what keeps R07 true — the stopgap degrades to the batch `/idea-triage` path
  and never to silent loss.

**Watermark**: install-time high-water mark on idea id, recorded in a gitignored state file
(`_working/idea-dispatch-state.json`, ephemeral and ungoverned per `PLAN-015`). Ideas at or below
the watermark are the pre-existing population the batch `/idea-triage` skill already covers; only
ideas created after install are this tool's responsibility. The watermark is a value captured
once at install time, not a live count — the phase note that "41 pre-existing open ideas" stay on
the batch path is a snapshot at the time that line was written; the repo's actual open-idea count
drifts independently of it, and this tool's behavior does not depend on the number at all.

**Budget ceiling**: `GOV-014`'s per-dispatch token ceiling default, 300,000 tokens, threaded
through as `TRIAGE_TOKEN_CEILING` and passed to every dispatch call. This tool does not meter or
enforce it — `phase-irs-11` builds enforcement against the ledger; this stopgap only carries the
number so the dispatch contract already matches what the daemon will enforce later.

**Kill switch**: `_working/orchestrator-halt` (`PLAN-039.01` SS9) is checked, stat-only, before
every dispatch attempt in both entry points. Its presence blocks all dispatch from this tool with
no other state change; removing it restores dispatch immediately. This is what keeps the kill
switch's "halts all pipeline dispatch" claim literally true while this stopgap is the only thing
doing the dispatching.

**Dispatch is encapsulated behind a callable** (`DispatchFn`) so tests substitute a stub and never
spawn a real agent. The default implementation shells out to the `claude` CLI headlessly,
scoping the `/idea-triage` skill to one idea id — the same skill the batch path already uses, so
a single idea dispatched through this tool and a single idea covered by a batch run go through
identical triage behavior.

Usage:
    uv run python tools/idea_dispatch.py install
    uv run python tools/idea_dispatch.py watch [--interval SECONDS]
    uv run python tools/idea_dispatch.py dispatch
    uv run python tools/idea_dispatch.py sweep
    uv run python tools/idea_dispatch.py status
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT))

from src.db.ideas import fold, load_events  # noqa: E402

#: Gitignored, ephemeral state (PLAN-015) — never the source of truth for idea status, only for
#: this tool's own watermark and its best-effort memory of what it has already sent.
STATE_FILE = ROOT / "_working" / "idea-dispatch-state.json"

#: The kill switch (PLAN-039.01 SS9). A stat-only check with no dependency on daemon code.
HALT_FLAG = ROOT / "_working" / "orchestrator-halt"

#: GOV-014's per-dispatch token ceiling default for the triage role. Cited, not enforced, here —
#: phase-irs-11 builds enforcement against the run ledger.
TRIAGE_TOKEN_CEILING = 300_000


@dataclass
class DispatchResult:
    """What one dispatch attempt produced, for the caller to log or assert on."""

    idea: str
    ok: bool
    detail: str


#: `(idea_id, title, body, budget_tokens) -> DispatchResult`. Tests pass a stub; production code
#: uses `default_dispatch`.
DispatchFn = Callable[[str, str, str, int], DispatchResult]


def halted(halt_flag: Path = HALT_FLAG) -> bool:
    """The kill switch: a stat-only check, no daemon import, no other side effect."""
    return halt_flag.exists()


def _load_state(state_file: Path = STATE_FILE) -> dict[str, Any]:
    if not state_file.exists():
        return {}
    return json.loads(state_file.read_text(encoding="utf-8"))


def _save_state(state: dict[str, Any], state_file: Path = STATE_FILE) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def install(log: Path | None = None, state_file: Path = STATE_FILE) -> dict[str, Any]:
    """Record the creation watermark: the highest idea id present right now.

    Idempotent to call again — a re-install simply moves the watermark forward to whatever the
    log currently holds, which only ever narrows this tool's future responsibility, never widens
    it past what a human intended by running `install`.
    """
    ideas = fold(load_events(log)) if log is not None else fold(load_events())
    watermark = max((int(idea_id) for idea_id in ideas), default=0)
    state = {"watermark": watermark, "dispatched": []}
    _save_state(state, state_file)
    return state


def default_dispatch(idea: str, title: str, body: str, budget_tokens: int) -> DispatchResult:
    """Invoke the `idea-triage` role headlessly via the `claude` CLI, scoped to one idea.

    Runs the same `/idea-triage <id>` skill the batch path uses, so triage behavior does not
    fork between the stopgap and the batch workflow. `budget_tokens` is passed through for
    parity with the eventual daemon dispatch contract; the `claude` CLI itself is not asked to
    enforce it here (see module docstring — enforcement is `phase-irs-11`'s job).
    """
    del title, body  # the skill reads the idea's effective state itself via fold(); not needed here
    try:
        proc = subprocess.run(
            ["claude", "-p", f"/idea-triage {idea}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=1800,
        )
    except Exception as exc:  # noqa: BLE001 - a dispatch failure must never propagate past the hook
        return DispatchResult(idea, False, f"dispatch raised: {exc}")
    if proc.returncode != 0:
        return DispatchResult(idea, False, proc.stderr[-2000:] or "non-zero exit, no stderr")
    return DispatchResult(idea, True, proc.stdout[-2000:])


def _post_watermark_ids(ideas: dict[str, dict[str, Any]], watermark: int) -> list[str]:
    return sorted((idea_id for idea_id in ideas if int(idea_id) > watermark), key=int)


def dispatch(
    log: Path | None = None,
    state_file: Path = STATE_FILE,
    halt_flag: Path = HALT_FLAG,
    dispatch_fn: DispatchFn = default_dispatch,
    budget_tokens: int = TRIAGE_TOKEN_CEILING,
) -> list[DispatchResult]:
    """The post-append hook. Dispatch every post-watermark idea this tool has not yet sent.

    Meant to be run right after `tools/append_idea.py add` succeeds — a separate process
    invocation, never a call inside the writer itself. Never installed automatically: a log with
    no watermark state yet is installed from its own current contents on first call, so a first
    `dispatch` right after the tool is wired in does not retroactively sweep every idea already
    in the log.
    """
    if halted(halt_flag):
        return []
    state = _load_state(state_file)
    if "watermark" not in state:
        state = install(log, state_file)
    watermark = int(state["watermark"])
    already_dispatched = set(state.get("dispatched", []))

    ideas = fold(load_events(log)) if log is not None else fold(load_events())
    candidates = [
        idea_id
        for idea_id in _post_watermark_ids(ideas, watermark)
        if idea_id not in already_dispatched
    ]

    results: list[DispatchResult] = []
    for idea_id in candidates:
        entry = ideas[idea_id]
        result = dispatch_fn(idea_id, entry["title"], entry["body"], budget_tokens)
        results.append(result)
        if result.ok:
            already_dispatched.add(idea_id)

    state["dispatched"] = sorted(already_dispatched)
    _save_state(state, state_file)
    return results


#: Default polling interval, in seconds, for the `watch` loop. A few seconds is enough to make
#: an append feel immediate without hammering the log file.
DEFAULT_POLL_INTERVAL = 5.0


def poll_once(
    log: Path | None = None,
    state_file: Path = STATE_FILE,
    halt_flag: Path = HALT_FLAG,
    dispatch_fn: DispatchFn = default_dispatch,
    budget_tokens: int = TRIAGE_TOKEN_CEILING,
) -> list[DispatchResult]:
    """One polling iteration of the `watch` loop's core: the same work `dispatch` does, except
    the halt flag is re-checked immediately before every individual dispatch attempt (not just
    once at entry), because a long-running watcher can have the flag dropped in mid-batch, and a
    failed or raising `dispatch_fn` call is isolated here so it never kills the loop that calls
    this repeatedly.

    This is the seam `watch` calls on every tick, and the same seam a test can call directly to
    drive one poll iteration without spinning up a thread or a real sleep loop. Semantics match
    `dispatch` exactly otherwise: same watermark self-install, same not-yet-dispatched filter,
    same watermark/dispatched-ids state advance.
    """
    if halted(halt_flag):
        return []
    state = _load_state(state_file)
    if "watermark" not in state:
        state = install(log, state_file)
    watermark = int(state["watermark"])
    already_dispatched = set(state.get("dispatched", []))

    ideas = fold(load_events(log)) if log is not None else fold(load_events())
    candidates = [
        idea_id
        for idea_id in _post_watermark_ids(ideas, watermark)
        if idea_id not in already_dispatched
    ]

    results: list[DispatchResult] = []
    for idea_id in candidates:
        if halted(halt_flag):
            break
        entry = ideas[idea_id]
        try:
            result = dispatch_fn(idea_id, entry["title"], entry["body"], budget_tokens)
        except Exception as exc:  # noqa: BLE001 - one bad dispatch must never kill the watcher
            result = DispatchResult(idea_id, False, f"poll_once: dispatch_fn raised: {exc}")
        results.append(result)
        if result.ok:
            already_dispatched.add(idea_id)
            state["dispatched"] = sorted(already_dispatched)
            _save_state(state, state_file)

    return results


def watch(
    log: Path | None = None,
    state_file: Path = STATE_FILE,
    halt_flag: Path = HALT_FLAG,
    dispatch_fn: DispatchFn = default_dispatch,
    budget_tokens: int = TRIAGE_TOKEN_CEILING,
    interval: float = DEFAULT_POLL_INTERVAL,
    max_iterations: int | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> None:
    """The genuine automatic trigger: a long-running loop that calls `poll_once` every
    `interval` seconds, forever (or `max_iterations` times, for tests).

    This is what makes R06 ("a test idea appended to the log is triaged with no human action")
    literally true in operation: an operator starts `watch` once, and every idea appended after
    that — by anyone, at any time — is picked up on the next tick with no per-append step. A
    failed or raising dispatch inside one tick never stops the loop (`poll_once` isolates it);
    the next tick, and the `sweep` command run on its own schedule, remain the recovery path for
    anything a tick's dispatch attempt did not resolve.
    """
    iterations = 0
    while max_iterations is None or iterations < max_iterations:
        poll_once(
            log=log,
            state_file=state_file,
            halt_flag=halt_flag,
            dispatch_fn=dispatch_fn,
            budget_tokens=budget_tokens,
        )
        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
        sleep_fn(interval)


def sweep(
    log: Path | None = None,
    state_file: Path = STATE_FILE,
    halt_flag: Path = HALT_FLAG,
    dispatch_fn: DispatchFn = default_dispatch,
    budget_tokens: int = TRIAGE_TOKEN_CEILING,
) -> list[DispatchResult]:
    """The reconciling sweep. Re-dispatch every post-watermark idea `fold()` still shows `open`.

    Ground truth is the idea log's own status, never this tool's `dispatched` memory — a dispatch
    killed mid-run may have already been recorded as sent, or may not have; either way, if the
    idea is still `open`, it is re-dispatched. This is what keeps R07 true: a killed or missed
    dispatch degrades to a retry through this sweep, never to silent loss.
    """
    if halted(halt_flag):
        return []
    state = _load_state(state_file)
    watermark = int(state.get("watermark", 0))

    ideas = fold(load_events(log)) if log is not None else fold(load_events())
    stuck = [
        idea_id
        for idea_id in _post_watermark_ids(ideas, watermark)
        if ideas[idea_id]["status"] == "open"
    ]

    results: list[DispatchResult] = []
    already_dispatched = set(state.get("dispatched", []))
    for idea_id in stuck:
        entry = ideas[idea_id]
        result = dispatch_fn(idea_id, entry["title"], entry["body"], budget_tokens)
        results.append(result)
        if result.ok:
            already_dispatched.add(idea_id)

    state["dispatched"] = sorted(already_dispatched)
    _save_state(state, state_file)
    return results


def _status(state_file: Path = STATE_FILE, halt_flag: Path = HALT_FLAG) -> str:
    state = _load_state(state_file)
    if "watermark" not in state:
        return "not installed"
    lines = [
        f"watermark: {state['watermark']:06d}",
        f"dispatched so far: {len(state.get('dispatched', []))}",
        f"halted: {halted(halt_flag)}",
    ]
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Stopgap triage dispatch: a post-append hook plus a reconciling sweep. "
            "Never edits tools/append_idea.py or the idea log's writer contract."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install", help="record the creation watermark from the log's current state")
    sub.add_parser("dispatch", help="dispatch triage for every post-watermark idea not yet sent")
    sub.add_parser("sweep", help="re-dispatch every post-watermark idea fold() still shows open")
    watch_parser = sub.add_parser(
        "watch",
        help="long-running loop: poll for new ideas and dispatch each with no human action",
    )
    watch_parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_POLL_INTERVAL,
        help=f"seconds between polls (default {DEFAULT_POLL_INTERVAL})",
    )
    sub.add_parser("status", help="print the watermark, dispatch count and halt state")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "install":
        state = install()
        print(f"watermark set to {state['watermark']:06d}")
        return 0
    if args.command == "dispatch":
        results = dispatch()
        for result in results:
            print(f"{'ok' if result.ok else 'FAILED'} {result.idea}")
        if not results:
            print("nothing to dispatch" if not halted() else "halted — dispatched nothing")
        return 0
    if args.command == "sweep":
        results = sweep()
        for result in results:
            print(f"{'ok' if result.ok else 'FAILED'} {result.idea}")
        if not results:
            print("nothing stuck" if not halted() else "halted — dispatched nothing")
        return 0
    if args.command == "watch":
        print(f"watching (poll interval {args.interval}s) — Ctrl-C to stop")
        try:
            watch(interval=args.interval)
        except KeyboardInterrupt:
            print("watch stopped")
        return 0
    print(_status())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
