---
schema_version: 1
id: doc-ops-idea-dispatch
code: OPS-016
title: Dispatch idea triage on append, and sweep for missed or failed dispatches
kind: operation
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-portfolio, sys-realization]
depends_on: [doc-governance-operations, doc-idea-realization-system-plan, doc-irs-orchestrator-design, doc-realization-role-contracts]
---

# Dispatch idea triage on append, and sweep for missed or failed dispatches

## Status: interim

**This tool is interim.** It exists only until `phase-irs-04`'s daemon lands and absorbs its duty
into the daemon's own reconcile loop, at which point this tool retires — deleting it deletes no
part of the daemon, because the two were built with no dependency in either direction
(`PLAN-039.01` SS10). The separate question of whether triage should eventually be dispatched
through an external gateway rather than the `claude` CLI is not decided here — `phase-auto-01`
rules that question on its own.

## Trigger

Run `dispatch` right after `tools/append_idea.py add` succeeds, so a newly created idea is triaged
without further human action (`REQ-022` R06). Run `sweep` on a schedule, or whenever a dispatch is
suspected to have failed or been interrupted, to reconcile any idea this tool should have
dispatched but that is still sitting `open` (`REQ-022` R07). Run `install` once, when first
wiring this tool in, to set the creation watermark.

`tools/append_idea.py` — the only sanctioned writer for `_data/ideas.jsonl` — is never edited by
this tool. It is a separate watcher script invoked after the writer, never from inside it, per the
owner ruling that opened this phase: the writer must succeed even when dispatch fails.

## Command

```bash
uv run python tools/idea_dispatch.py install     # record the creation watermark, once
uv run python tools/idea_dispatch.py dispatch    # the post-append hook
uv run python tools/idea_dispatch.py sweep       # the reconciling sweep
uv run python tools/idea_dispatch.py status       # print watermark, dispatch count, halt state
```

## Expected result

`install` records the highest idea id currently in the log as the watermark, in a gitignored
state file (`_working/idea-dispatch-state.json`, ephemeral and ungoverned per `PLAN-015`). Ideas
at or below the watermark are **not** this tool's responsibility — they are the pre-existing
population the batch `/idea-triage` skill already covers. At the time this phase was built the
repository held 41 pre-existing open ideas per the phase's scope note; by the time this tool
shipped the actual count had drifted to 43. Neither number matters to the tool's behavior: the
watermark is an install-time snapshot of the log's own state, not a count carried in code.

`dispatch` finds every idea created after the watermark that this tool has not yet sent, and
dispatches the `idea-triage` role for each — the same `/idea-triage <id>` skill the batch path
uses, scoped to one idea, so a single idea triaged through this tool and one triaged in a batch
run go through identical behavior. A successful dispatch results in a `finding` annotation and a
`triaged` status move, exactly as the batch skill produces.

`sweep` re-dispatches every post-watermark idea that `fold()` still shows as `open` — trusting
only the idea log's own status, never this tool's memory of what it thinks it already sent. This
is what keeps `REQ-022` R07 true: a dispatch that failed outright, was killed mid-run, or was
never invoked because the hook step was skipped, all converge on the same recoverable state — an
idea sitting `open` past the watermark — and the sweep brings each one to `triaged`.

Both `dispatch` and `sweep` check `_working/orchestrator-halt` (`PLAN-039.01` SS9's kill switch)
before every dispatch attempt — a stat-only file existence check, with no import of or dependency
on any daemon code. With the flag present, both commands dispatch nothing and report that they
are halted; removing the flag restores dispatch on the next invocation, with no other state
change (the watermark and the dispatched-ids record are untouched by the halt/resume cycle
itself).

Each dispatch is passed a budget ceiling of 300,000 tokens — `GOV-014`'s per-dispatch default for
every pipeline role, including triage. This tool threads the number through so its dispatch
contract already matches what the eventual daemon will enforce; it does not itself meter or
enforce the ceiling — `phase-irs-11` builds enforcement against the run ledger.

## Failure and recovery

A dispatch that fails (the `claude` CLI exits non-zero, raises, or is killed) leaves the idea
`open` and is reported as `FAILED` — it never partially advances the idea's status or writes a
malformed annotation, because `tools/append_idea.py`'s own validation is what the triage role
calls, and that validation is untouched by this tool. Nothing here retries automatically inside
one `dispatch` call; recovery is the `sweep` command's job, run separately, exactly as `REQ-022`
R07's verification method describes: kill a dispatch mid-run, run the sweep, confirm the idea
reaches `triaged`.

A dispatch already recorded as sent is not re-sent by a later `dispatch` call, even if it silently
failed without reporting `FAILED` (a killed process, for instance) — that gap is exactly what
`sweep` exists to close, by checking the idea's actual status rather than this tool's dispatch
record.

<!-- generated:tool-reference:start -->

### Reference: `tools/idea_dispatch.py`

Stopgap triage dispatch: a post-append hook plus a reconciling sweep.

`tools/append_idea.py` is never edited — this is a separate watcher script (owner ruling,
`phase-irs-01`'s batch open) that reads the idea log through `fold()` the same way every other
consumer does and dispatches the `idea-triage` role (`GOV-014`) headlessly for ideas the writer
appended. It is the stopgap named by `PLAN-039.01` SS10: `phase-irs-04`'s daemon absorbs this duty
into its own reconcile loop and retires this tool (see `docs/08-governance/OPS-016-idea-dispatch.md`
for the interim declaration).

**Two entry points, one shared core:**

- `dispatch` — meant to run right after `tools/append_idea.py add` succeeds (wire it into
  whatever calls the writer; nothing here modifies the writer to call it automatically, per the
  owner ruling that the writer must succeed even when dispatch fails). Finds every idea created
  after the install watermark that this tool has not yet dispatched, and dispatches each.
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
    uv run python tools/idea_dispatch.py dispatch
    uv run python tools/idea_dispatch.py sweep
    uv run python tools/idea_dispatch.py status

No CLI arguments.

Exit codes found in source: 0.

<!-- generated:tool-reference:end -->
