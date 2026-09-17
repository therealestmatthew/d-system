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

Start `watch` once — at boot, or whenever this tool is first wired in — and leave it running. It
polls the idea log every `--interval` seconds (default 5) and dispatches each newly created idea
it finds, with **no per-append human step**: this is what makes `REQ-022` R06 ("a test idea
appended to the log is triaged with no human action") hold in operation, not just inside a test
harness. `install` runs itself on first tick if it was never run explicitly, so starting `watch`
cold does not retroactively sweep the pre-existing backlog — but it does print a warning listing
every open idea that self-install is thereby excluding (see "Cold start" below); run `install`
explicitly first if you would rather set the watermark quietly, on your own terms.

`dispatch` still exists as the one-shot form of the same core, for an operator who prefers to
invoke it by hand right after `tools/append_idea.py add` rather than run `watch` continuously —
but it is no longer the primary path; `watch` is. Run `sweep` on a schedule, or whenever a
dispatch is suspected to have failed or been interrupted, to reconcile any idea this tool should
have dispatched but that is still sitting `open` (`REQ-022` R07). The sweep remains the recovery
path regardless of which trigger — `watch` or manual `dispatch` — is in use: a dispatch that
failed, raised, or was killed mid-tick never stops `watch`'s loop, and never gets silently lost,
because the idea it touched is still `open` for the next sweep to pick up. Run `install` once,
when first wiring this tool in, only if you want to set the watermark ahead of starting `watch`.

`tools/append_idea.py` — the only sanctioned writer for `_data/ideas.jsonl` — is never edited by
this tool. It is a separate watcher script invoked after the writer, never from inside it, per the
owner ruling that opened this phase: the writer must succeed even when dispatch fails.

## Command

```bash
uv run python tools/idea_dispatch.py install               # record the creation watermark, once
uv run python tools/idea_dispatch.py watch                 # the automatic trigger — run once, keep it running
uv run python tools/idea_dispatch.py watch --interval 10    # override the poll interval (seconds)
uv run python tools/idea_dispatch.py dispatch               # manual one-shot form of the same core
uv run python tools/idea_dispatch.py sweep                  # the reconciling sweep
uv run python tools/idea_dispatch.py status                 # print watermark, dispatch count, halt state
```

## Expected result

`install` records the highest idea id currently in the log as the watermark, in a gitignored
state file (`_working/idea-dispatch-state.json`, ephemeral and ungoverned per `PLAN-015`). Ideas
at or below the watermark are **not** this tool's responsibility — they are the pre-existing
population the batch `/idea-triage` skill already covers. At the time this phase was built the
repository held 41 pre-existing open ideas per the phase's scope note; by the time this tool
shipped the actual count had drifted to 43. Neither number matters to the tool's behavior: the
watermark is an install-time snapshot of the log's own state, not a count carried in code.

`watch` runs `poll_once` on a loop, sleeping `--interval` seconds (default 5) between ticks. Each
tick does what `dispatch` does — find every post-watermark idea not yet sent, dispatch the
`idea-triage` role for each — but re-checks the halt flag immediately before every individual
dispatch attempt (not just once per tick), and isolates a dispatch that fails or raises so the
loop keeps ticking; that idea simply stays `open` for the next tick or the next `sweep` to pick
up. `dispatch` finds every idea created after the watermark that this tool has not yet sent, and
dispatches the `idea-triage` role for each — the same `/idea-triage <id>` skill the batch path
uses, scoped to one idea, so a single idea triaged through this tool and one triaged in a batch
run go through identical behavior. A successful dispatch results in a `finding` annotation and a
`triaged` status move, exactly as the batch skill produces.

`sweep` re-dispatches every post-watermark idea that `fold()` still shows as `open` — trusting
only the idea log's own status, never this tool's memory of what it thinks it already sent. This
is what keeps `REQ-022` R07 true: a dispatch that failed outright, was killed mid-run, or was
never invoked because the hook step was skipped, all converge on the same recoverable state — an
idea sitting `open` past the watermark — and the sweep brings each one to `triaged`.

**In-flight claim guard.** Before calling the dispatch callable for an idea, `dispatch`,
`poll_once`, and `sweep` all atomically create a per-idea claim file
(`_working/idea-dispatch-claims/<idea>.claim`, `O_CREAT | O_EXCL`) and remove it once the call
returns — this works across processes, since `watch` and `sweep` are separate invocations with no
shared memory. If a claim already exists and is not stale, that idea is skipped for this round
rather than dispatched a second time: this is what stops `watch`/`sweep`, or two concurrent
`watch`es, from both firing on the same idea while a prior dispatch for it is still in flight. A
claim older than `CLAIM_STALE_SECONDS` (one hour) is presumed to belong to a dispatch whose process
died mid-run and is taken over rather than honored, so `REQ-022` R07 keeps holding: a crashed
dispatch's claim never permanently blocks the sweep that is supposed to recover it.

`watch`, `dispatch`, and `sweep` all check `_working/orchestrator-halt` (`PLAN-039.01` SS9's kill
switch) before every dispatch attempt — a stat-only file existence check, with no import of or
dependency on any daemon code — once at entry, and again immediately before each individual idea
inside their loops, so a flag dropped mid-batch stops the rest of the batch, not just the next
invocation. With the flag present, all three commands dispatch nothing and report (or, for
`watch`, simply tick with) that they are halted; removing the flag restores dispatch on the next
attempt, with no other state change (the watermark and the dispatched-ids record are untouched by
the halt/resume cycle itself).

**Budget ceiling.** `GOV-014`'s per-dispatch token ceiling default for the triage role is 300,000
tokens, recorded in code as `TRIAGE_TOKEN_CEILING` for traceability. `claude --help` exposes no
per-invocation token-budget flag — only `--max-budget-usd` (a dollar amount) and `--autocompact`
(a context-window size), neither of which is a token ceiling — so this tool does not pass the
number to the `claude` subprocess at all; `default_dispatch` takes no `budget_tokens` argument.
**The 300k ceiling is a contract obligation on the dispatched `idea-triage` agent itself, not
something this host process meters, enforces, or transmits.** `phase-irs-11` builds real
enforcement against the run ledger.

**Cold start.** `install`, run explicitly, is silent — an operator who runs it by hand already
knows it draws the line at the log's current contents. A first `dispatch`/`poll_once` (and hence
`watch`) that finds no state file self-installs the same way, but **prints a warning to stderr**
listing every currently-open idea it is thereby excluding from both future dispatch and `sweep`,
handing them to the batch `/idea-triage` path instead — because that exclusion is otherwise
invisible and permanent (those ideas never again look different from the pre-existing backlog).
Run `install` explicitly before starting `watch`/`dispatch` for the first time if you want to set
the watermark quietly and deliberately instead.

## Failure and recovery

A dispatch that fails (the `claude` CLI exits non-zero, raises, or is killed) leaves the idea
`open` and is reported as `FAILED` — it never partially advances the idea's status or writes a
malformed annotation, because `tools/append_idea.py`'s own validation is what the triage role
calls, and that validation is untouched by this tool. Nothing here retries automatically inside
one `dispatch` call; recovery is the `sweep` command's job, run separately, exactly as `REQ-022`
R07's verification method describes: kill a dispatch mid-run, run the sweep, confirm the idea
reaches `triaged`.

A dispatch process itself dying mid-run — as opposed to a killed `claude` subprocess it launched,
which surfaces as an ordinary `FAILED` result — leaves its claim file behind under
`_working/idea-dispatch-claims/`. That claim blocks a fresh dispatch on the same idea only until
it goes stale (`CLAIM_STALE_SECONDS`, one hour); after that, `sweep` (or the next `dispatch`) takes
the claim over and re-dispatches normally. This is the mechanism that keeps the claim guard from
turning into its own silent-loss failure mode.

A dispatch already recorded as sent is not re-sent by a later `dispatch` call, even if it silently
failed without reporting `FAILED` (a killed process, for instance) — that gap is exactly what
`sweep` exists to close, by checking the idea's actual status rather than this tool's dispatch
record.

`watch` applies the same isolation per tick: if a `dispatch_fn` call fails or raises for one idea
mid-tick, that exception is caught inside the tick, the loop keeps running, and the idea is left
`open` — it does not stop `watch` from picking up the next idea on the same or a later tick, and
it does not block `sweep` from recovering it on its own schedule. A crashed `watch` process itself
(the loop's host process dying, as opposed to one dispatch failing inside it) is not something
this tool detects or restarts; that is an operator/process-supervision concern outside this tool's
scope, and `sweep` run on a schedule is the backstop for whatever a dead `watch` process leaves
`open`.

<!-- generated:tool-reference:start -->

### Reference: `tools/idea_dispatch.py`

Stopgap triage dispatch: a post-append hook plus a reconciling sweep.

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

**Budget ceiling**: `GOV-014`'s per-dispatch token ceiling default, 300,000 tokens, is recorded here
as `TRIAGE_TOKEN_CEILING` for traceability only. `claude --help` exposes no per-invocation
token-budget flag — only `--max-budget-usd` (a dollar figure) and `--autocompact` (a context-window
size), neither of which is a token ceiling — so this stopgap does not thread the number through to
the `claude` subprocess at all. The 300k ceiling is a contract obligation on the dispatched
`idea-triage` agent itself, not something this host process meters, enforces, or even transmits;
`phase-irs-11` builds real enforcement against the run ledger.

**Kill switch**: `_working/orchestrator-halt` (`PLAN-039.01` SS9) is checked, stat-only, before
every dispatch attempt — once at entry to `dispatch`/`sweep`/`poll_once`, and again immediately
before each individual idea inside their loops, so a flag dropped mid-batch stops the batch, not
just the next call. Its presence blocks all dispatch from this tool with no other state change;
removing it restores dispatch immediately. This is what keeps the kill switch's "halts all pipeline
dispatch" claim literally true while this stopgap is the only thing doing the dispatching.

**In-flight claim guard**: before calling `dispatch_fn` for an idea, `dispatch`/`sweep`/`poll_once`
atomically create a per-idea claim file (`O_CREAT | O_EXCL`) under `_working/idea-dispatch-claims/`
and remove it once the call returns — across processes, since `watch` and `sweep` are separate
invocations with no shared memory. A claim already held by another in-flight dispatch causes that
idea to be skipped this round, so `watch`/`sweep`, or two concurrent `watch`es, cannot both dispatch
the same idea at once. A claim older than `CLAIM_STALE_SECONDS` is presumed to belong to a dispatch
whose process died mid-run and is taken over rather than honored — this is what keeps `sweep`'s
R07 recovery working even in the presence of the guard: a crashed dispatch's claim never blocks its
own recovery.

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

| Flag | Help | Choices | Default | Required |
|---|---|---|---|---|
| `--interval` |  |  |  |  |

Exit codes found in source: 0.

<!-- generated:tool-reference:end -->
