---
schema_version: 1
id: doc-session-langgraph-orchestrator-skeleton
code: SESS-2026-09-23-01
title: LangGraph orchestrator skeleton with interrupt gates and the thin-state rule
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems:
- sys-realization
depends_on:
- doc-irs-orchestrator-design
- doc-idea-realization-system-requirements
- doc-idea-realization-system
- doc-adr-langgraph-orchestration
---

# LangGraph orchestrator skeleton with interrupt gates and the thin-state rule

## Phase

`phase-irs-04` — LangGraph orchestrator skeleton with interrupt gates and the thin-state rule.
Claimed as `agent-coord`, worked on `agent/phase-irs-04` in
`/code/d-system-worktrees/phase-irs-04`, per `PLAN-039.01` and `REQ-022`. Two step dispatch:
step 1 allocated the two `OPS-*` codes this phase's writers needed before the deliverables list
could name them; step 2 built the phase once the coordinator declared those paths.

## What was built

`src/orchestrator/` (ADR-018, PLAN-039.01):

- `state.py` — the three-field thin graph state (`run_id`, `kind`, `refs`) and per-kind
  re-derivation. Only `intake` is implemented (`derive_intake_position`: `open` →
  `dispatch_gate`, every other legal idea status → `done`); `batch`/`unit`/`realization` raise
  `NotImplementedError` naming which later phase owns them, rather than guessing at
  re-derivation rules against records (partition records, phase status, evidence annotations)
  this phase does not build the graphs to read.
- `gates.py` — `gate_node()`, the entire body of a gate node (its `interrupt()` call and
  nothing else, per PLAN-039.01 §7), and `resume_command()`.
- `dispatch.py` — the `Dispatcher` protocol and `DispatchResult`, `unimplemented_dispatcher`
  (refuses rather than guessing at a real Claude Agent SDK binding), and the kill switch's flag
  file (`halt()`/`resume_dispatch()`/`is_halted()` over `_working/orchestrator-halt`).
  Enforcement of the flag before every dispatch is `phase-irs-11`'s; the verbs ship now per
  PLAN-039.01 §9.
- `ledger.py` — the run ledger's read/write path: `start` (natural-key idempotency, refuses a
  second non-terminal run under the same key), `record` (follow-on events), `reconstruct` (one
  run's summary from its own events alone, no checkpoint), `fold`, `active_natural_keys`.
- `decisions.py` — the decision inbox's read/write path: `decide` (computes `decision_seq`
  automatically, refuses a stale explicit one — the dedup key), `load_decisions`, `for_gate`,
  `latest_for_gate`.
- `graphs/intake.py` — the intake graph: `assemble → dispatch_gate →(approve) triage → done`,
  `→(anything else) done`. `build_graph(checkpointer, dispatcher)`.
- `tick.py` — `open_checkpoint_store()` (recreates a missing or corrupt SQLite store, moving a
  corrupt file aside with a timestamp rather than deleting it outright), the watermark
  read/write helpers, and `tick()` — reconcile, start, advance in one callable, with every gate
  resumption gated behind an explicit `dispatch: bool`.
- `__main__.py` — the CLI: `tick [--dispatch]`, `gate <run_id> --gate --decision --by
  [--notes]`, `halt`, `resume-dispatch`. Not `start`/`stop`/`status` or the `flock` lock —
  `phase-irs-16`'s.

Schemas and sanctioned writers, the idea log's own append-only discipline (`OPS-005`) applied to
the orchestrator's records (PLAN-039.01 §5, §7): `schemas/run.schema.json` and
`schemas/gate-decision.schema.json`; `tools/append_run.py` and `tools/append_decision.py`
(thin CLIs over `ledger.py`/`decisions.py`); `OPS-022` and `OPS-023` document them.

`pyproject.toml`/`uv.lock`: pinned `langgraph==1.2.12` and `langgraph-checkpoint-sqlite==3.1.1`
via `uv add`, confining LangGraph's import surface to `src/orchestrator/` (verified by the
adversary: exactly three `import langgraph`/`from langgraph` matches repo-wide, all inside
`gates.py`, `tick.py`, `graphs/intake.py`).

`docs/04-decisions/ADR-018-langgraph-orchestration.md`: `status: draft` → `accepted`, per its
own acceptance clause ("accepted when PLAN-039's orchestrator phase lands the first working
graph") — the intake graph runs end to end under `test/test_orchestrator.py`, including the
checkpoint-loss and killed-process resumption drills the clause names.

## Declaration history

The deliverables list was narrowed by the owner before this session started (per the coordinator's
dispatch), scoping the `src/`/`test/`/`schemas/`/`tools/`/`docs/08-governance/` globs down to this
phase's own orchestrator paths and replacing the generic test glob with the single file
`test/test_orchestrator.py`. Two `OPS-*` document codes (`OPS-022`, `OPS-023`) were allocated as
step 1 of this dispatch, via `uv run python -m src.governance --next-code operation` run twice with
distinct reservations confirmed in the shared git-common-dir reservation store; the coordinator then
declared `docs/08-governance/OPS-022-append-run.md` and `docs/08-governance/OPS-023-append-decision.md`
as deliverables on `dev` in commit `1285f93` before step 2 (the build) began.

## Scope reading

`phase-irs-04`'s own scope and `PLAN-039.01` §12 both read as "intake graph only": the phase
builds the `intake` graph fully plus the shared tick/state/gates/ledger machinery every run kind
will use, not all four graphs. `batch` (`phase-irs-14`) and `realization` (`phase-irs-15`) are
new, dependent phases per §12; the `unit` graph is a later backlog-phase deliverable. `state.py`'s
`IMPLEMENTED_KINDS = frozenset({"intake"})` and `derive_position()`'s `NotImplementedError` for
the other three kinds match this reading and are consistent with the current `backlog.yaml`
entry, which the adversary confirmed independently (see below).

## Verification

```
$ uv run python -m src.governance
Governance OK: 35 systems, 327 documents, 30 memories, 293 backlog phases
```
Exit 0.

```
$ uv run pytest
903 passed, 1 skipped, 1 warning in 66.45s
```
Exit 0. The one skip is a pre-existing, data-dependent idea-corpus test unrelated to this phase.

```
$ grep -rn "claim" src/orchestrator/ tools/append_run.py tools/append_decision.py
src/orchestrator/__init__.py:26:This package defines no claim-recovery logic (REQ-022 R19). Claim-protocol recovery is
src/orchestrator/__init__.py:28:retries or repairs a `_tmpagent/` claim.
```
Exit 0. Both matches are docstring prose in `src/orchestrator/__init__.py` stating the R19
boundary rule (what the package does *not* implement) — neither is claim-recovery logic. No
matches in `tools/append_run.py` or `tools/append_decision.py`. Locked in by
`test_r19_orchestrator_package_defines_no_claim_recovery_logic`, which re-runs the same grep
programmatically, allowlists only these two sentences, and fails on any new or unexplained match.

## Acceptance

- **REQ-022 R16 (as amended), R17, R18 hold** — Met.
  - R16 (checkpoint deletion/corruption → re-keyed thread at the re-derived position):
    `test_r16_checkpoint_deletion_rekeys_thread_at_rederived_position` and
    `test_r16_checkpoint_corruption_rekeys_thread_at_rederived_position`, both against a real
    SQLite file (not `:memory:`); the corruption test overwrites the main file *and* its
    `-wal`/`-shm` side files, after empirically confirming that leaving the WAL intact lets
    SQLite silently recover the pre-corruption state, which would have made the test a no-op.
  - R17 (a killed run resumes at its gate): `test_r17_killed_run_resumes_at_its_gate` — the
    first `SqliteSaver` connection is discarded with no reference kept, and a fresh connection
    to the same on-disk file stands in for the daemon's next process.
  - R18 (reconstruct one run from ledger entries alone):
    `test_r18_run_reconstructible_from_ledger_alone` — deletes the checkpoint file before
    calling `ledger.reconstruct()`, and checks the reconstructed summary against what the run
    actually did.
- **REQ-022 R19 holds: the orchestrator package contains no claim-recovery logic of its own** —
  Met. `test_r19_orchestrator_package_defines_no_claim_recovery_logic`, described above.
- **No agent dispatch occurs without the owner-initiated dispatch flag** — Met.
  `test_no_dispatch_without_the_owner_flag` (a spy dispatcher records zero calls with
  `dispatch=False` even with an `approve` decision already recorded) and
  `test_dispatch_flag_permits_resuming_into_dispatch` (one call with `dispatch=True`). The
  guarantee shipped is stricter than REQ-017 R01 requires: no gate resumes at all without the
  flag, not only one that would reach a dispatch — simpler to state and to verify, at the cost
  of also deferring a `reject` decision's resumption until a `--dispatch` tick.

## Reviews

**Validator** (`/code/d-system/_working/build-batch-002/phase-irs-04-validation.md`): **PASS**.
Independently re-ran all three verification commands against the rebased head (`e348000` on
`dev` `271d614`) and confirmed each acceptance row against the named tests by reading them, not
just by trusting the grep count.

**Adversary** (`/code/d-system/_working/build-batch-002/phase-irs-04-adversary.md`): one
**MEDIUM** finding, confirmed. `graphs/intake.py` adds an interrupt gate
(`GATE_NAME = "dispatch-authorization"`) that PLAN-039.01's run-kind table and §7's gate list do
not assign to `intake` — the plan's own attended-only mechanism is the tick-level `--dispatch`
flag alone (§2), not a per-idea gate. As shipped, each intake run additionally needs its own
recorded `approve` decision before the tick-level flag can let it dispatch, a materially heavier
operational model than the design specifies. The adversary noted this was deliberate and
self-aware (the gate exists in part because R17's "resumes at its gate" acceptance text needs a
real gate to demonstrate against the one graph this phase builds), not an oversight, and flagged
it for the owner's judgment rather than calling it a defect outright. Everything else the
adversary checked — the intake-graph-only scope reading, dispatch-flag enforcement under
mutation, re-derivation logic under mutation, the langgraph import-surface confinement, gitignore
correctness for runtime state paths, R19, and edits outside declared deliverables — held.

**Owner's ruling**: keep the gate, as an owner-approved deviation from `PLAN-039.01`. No code
change made in response to this finding. An idea to amend `PLAN-039.01` §1 (the run-kind table)
and §7 (the gate list) to name the intake gate has been sent to Ideation, so the design document
and the shipped behavior stop disagreeing.

## Unresolved

`PLAN-039.01` does not yet name the `dispatch-authorization` gate — the amendment idea sent to
Ideation is the open thread; this session makes no edit to the plan document itself (per the
"ask, don't assume, and don't turn a judgment call into a standing edit of a governed document
without approval" rule — the owner's ruling was to keep the *code*, not to authorize this session
rewriting the plan).

## Backlog

`phase-irs-04` stays as the coordinator finds it; this session does not edit
`docs/09-backlog/backlog.yaml`. The completion edit, and the integration decision, are the
coordinator's to make on `dev`.
