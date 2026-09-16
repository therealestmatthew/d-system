---
schema_version: 1
id: doc-irs-orchestrator-design
code: PLAN-039.01
title: Orchestrator design (daemon and watcher)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-realization]
depends_on: [doc-idea-realization-system-plan, doc-idea-realization-system, doc-idea-realization-system-requirements, doc-adr-langgraph-orchestration]
parent: doc-idea-realization-system-plan
---

# Orchestrator design (daemon and watcher)

Child plan of [PLAN-039](PLAN-039-idea-realization-system.md), designing the LangGraph
orchestrator that `phase-irs-04` builds and that `phase-irs-01`, `-08`, `-11` and `-13` extend.
The process model is the owner's round-3 ruling on idea `000247`: a **persistent daemon with
watchers**, chosen on 2026-09-15 with the P5 overlap explicitly in view. This document turns
that ruling and [ADR-018](../04-decisions/ADR-018-langgraph-orchestration.md)'s thin-state rule
into a buildable design.

## 1. The pipeline is four run kinds, not one long run

`ARCH-006` draws nine stages as one flow, but the flow changes cardinality twice: many ideas
feed one partition, one partition yields many tracks, one plan yields many phases. A single
graph per idea would either block for weeks at the partition threshold or misrepresent the
fan-in. The orchestrator therefore runs **four graph kinds**, composed through the repository's
records rather than through graph state:

| Run kind | Covers | One run per | Starts when | Ends when |
|---|---|---|---|---|
| `intake` | Stages 1–2 | idea | The watcher sees a new `add` event in `_data/ideas.jsonl` | The idea is `triaged` (or capture was declined and no run starts) |
| `batch` | Stages 3–7, gates G2–G3 | partition run | The triaged-idea threshold is met, or the owner asks | Every produced phase is registered with a ratified ordering |
| `unit` | Stage 8, gates G4–G5 | backlog phase | The phase is ready under queue rules and dispatch capacity exists | The phase is integrated and completion-reviewed, or parked `blocked` |
| `realization` | Stage 9, gate G5 | delivered idea | A `unit` run integrating work that traces to the idea completes | The idea is `delivered` with evidence, or the shortfall is a recorded finding |

Fan-in and fan-out live in the records: a `batch` run selects its ideas from the log by status,
and a `unit` run exists because a `batch` run registered its phase. No run holds a reference to
another run — only to record state. This is the thin-state rule doing structural work: killing
every checkpoint loses no linkage, because the linkage was never in the graph.

## 2. Process model: one daemon, watchers, and a tick that works alone

One daemon process, single-instance by a lock under `data/orchestrator/`:

```
uv run python -m src.orchestrator start | stop | status | tick | gate ...
```

- **`start`** runs the loop: watchers wake it, and every wake executes one **tick**.
- **`tick`** is the whole scheduler as one callable: reconcile against the records, start runs
  whose start condition holds, advance every non-interrupted run to its next gate or terminal
  state, and write ledger entries. The command form runs one tick with no daemon — that is the
  degraded mode, the test surface, and the guarantee that nothing requires the daemon to be
  alive. A dead daemon means latency, never loss.
- **`status`** renders the run table and the gate queue, decision-ready.
- **`gate`** records an owner decision (approve / amend / reject, with a note) and resumes the
  interrupted run on the next tick.

**Watchers** are repo-internal only, per the round-3 ruling's boundary: a file watcher on
`_data/ideas.jsonl` (append-only, so new bytes are new events), one on the gate-decision inbox,
and a periodic timer that fires a reconciling tick. External triggers — webhooks, schedules,
anything arriving from outside the repository — remain `phase-auto-03`'s territory and are out
of scope here; if that gateway is built, it injects events by writing where the watchers
already look, not by reaching into the daemon.

**Sweep is not a separate mechanism.** `phase-irs-01`'s reconciling sweep is the tick's
reconcile step: every tick begins by re-deriving what should exist from the records (ideas
`open` with no live `intake` run, phases ready with no `unit` run), so a missed watcher event
is corrected at the next tick from any source. This resolves `phase-irs-01`'s open
next-action — the dispatch mechanism is the watcher-plus-tick, the writer stays wholly
independent of the orchestrator, and `phase-irs-01` builds the intake watcher and reconcile
step as the daemon's first working slice rather than a throwaway script the daemon later
absorbs. `phase-irs-01` therefore gains `depends_on: [phase-irs-04]` — an amendment applied in
the same change that adds this plan, so the two land together or not at all.

## 3. Graph state and the re-derivation table

Each run kind's state is a small typed object: `run_id`, `kind`, `refs` (idea ids, document
codes, phase id, branch name), `attempts` (per revise loop), `budget` (tokens granted and
spent). Nothing else. Stage position is LangGraph's own cursor; content lives in the records.

Repo-wins reconciliation, per kind — how a resumed or doubted run re-derives its position:

| Run kind | Authoritative record | Re-derivation |
|---|---|---|
| `intake` | The idea's folded status | `open` → dispatch triage; `triaged`+ → run is complete regardless of checkpoint |
| `batch` | Partition record; existence of REQ/PLAN docs; phases in `backlog.yaml`; gate decisions | The furthest artifact that exists wins; a checkpoint claiming an earlier stage is fast-forwarded, one claiming a later stage is rolled back to what the records prove |
| `unit` | The phase's `status`, branch existence, `_tmpagent`/claim state, merge state on `dev` | Same rule; a phase `complete` on `dev` ends the run whatever the checkpoint says |
| `realization` | Evidence annotations and terminal status on the idea | `delivered` ends the run; an unresolved finding re-queues the check |

## 4. Gates as interrupts, decisions as events

G2 and G3 are `interrupt()` nodes in `batch` runs; G4 and G5 in `unit` runs (G5 also in
`realization`). An interrupted run parks in the checkpointer and appears in the gate queue.

Decisions arrive as one append each to `data/orchestrator/decisions.jsonl` — written by the
`gate` subcommand today, by `phase-irs-13`'s queue surface later. The decision event is
operational plumbing; the **repository artifact the decision produces** (a status change, a
GOV-003 entry, a merge, a `/session-close` record) is the durable truth, and reconciliation
reads the artifact, not the inbox. The owner-only actions stay owner-performed: the daemon
never merges (G4 runs through the capability broker once `phase-auto-02` lands; until then the
daemon stops before the merge and the queue names the command for the owner to run) and never
invokes `/session-close` — G5 items wait until the owner's batched close session has produced
the records, which the next tick then observes.

## 5. Dispatch adapter

One module owns every agent invocation: it binds the role contract (`phase-irs-03`) to the
prompt, checks the kill switch and the run's remaining budget **before** each dispatch, records
the dispatch and its outcome in the ledger, and enforces the contract's never-do column by tool
policy where the SDK supports it rather than by prose alone. Developer agents in `unit` runs
are dispatched into worktrees exactly per `ADR-003` — the adapter shells the same commands the
protocol prescribes and never invents a second isolation scheme.

## 6. Operational files and the ledger boundary

Everything operational lives under gitignored `data/orchestrator/`: the instance lock,
`checkpoints.sqlite` (SQLite checkpointer), `decisions.jsonl`, `ledger.jsonl`, and the kill
switch (`halt` — its presence stops all dispatch; `phase-irs-11` gives it its command and
tests). All of it is disposable by construction except `ledger.jsonl`, which is the audit
trail; **interim**, like the stopgap: when P5's durable run ledger (`phase-auto-04`) lands,
the daemon writes that contract instead and this file becomes a migration source. The boundary
against `phase-auto-05` restates the ruling: the supervised worker, if built, hosts *execution
agents*; the graph and its scheduler are the daemon's and stay here.

## 7. Package layout and testing

```
src/orchestrator/
  __main__.py     # CLI: start/stop/status/tick/gate
  daemon.py       # lock, watchers, loop → tick
  tick.py         # reconcile + start + advance; the only scheduler
  graphs/         # intake.py, batch.py, unit.py, realization.py
  state.py        # typed run state; re-derivation per kind
  dispatch.py     # SDK adapter: contracts, budget, kill switch, ledger
  gates.py        # queue rendering, decision intake
  ledger.py       # append + read; the P5 migration seam
```

LangGraph imports are confined to `graphs/` and `tick.py`; `pyproject.toml` pins `langgraph`
and the SQLite checkpointer. Tests run the tick, never the daemon: a stub dispatcher plays
every agent, tmp-path fixtures fake the records, and the forced-failure drill (`phase-irs-12`)
drives each failure edge — revise, escalate, park — through the tick command alone. The daemon
loop adds only watchers over the tick and gets a thin start/stop/single-instance test.

## 8. What this changes in the backlog, and what it does not

- `phase-irs-04` builds `__main__.py`, `daemon.py`, `tick.py`, `state.py`, `gates.py`,
  `ledger.py` and the `intake` graph skeleton against this design; its backlog entry now names
  this plan as its `plan`, since this document is what it builds.
- `phase-irs-01` builds the intake watcher and the reconcile step's idea half; its
  `depends_on: [phase-irs-04]` is applied alongside this plan.
- `phase-irs-08` fills `dispatch.py`'s developer/validator loop and the `unit` graph;
  `phase-irs-11` the budget and kill-switch enforcement; `phase-irs-13` replaces the `status`
  rendering with the real queue surface. No other phase's scope moves.

## Open questions, stated rather than hidden

1. **Watcher library or poll.** `watchfiles` is another dependency; a 2-second poll of two
   file mtimes is trivially cheap at this scale. The build phase decides; the design works
   identically either way.
2. **Where the partition threshold N lives.** A constant in the daemon is easiest; the owner
   may prefer it in a config the workbench can edit. Deferred to `phase-irs-04` with a default
   of on-demand-only until set.
