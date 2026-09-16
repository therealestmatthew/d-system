---
schema_version: 1
id: doc-irs-orchestrator-design
code: PLAN-039.01
title: Orchestrator design (daemon and watcher)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-16'
systems: [sys-realization]
depends_on: [doc-idea-realization-system-plan, doc-idea-realization-system, doc-idea-realization-system-requirements, doc-adr-langgraph-orchestration]
parent: doc-idea-realization-system-plan
---

# Orchestrator design (daemon and watcher)

Child plan of [PLAN-039](PLAN-039-idea-realization-system.md), designing the LangGraph
orchestrator that `phase-irs-04` builds and that `phase-irs-08`, `-11`, `-13`, `-14` and `-15`
extend. The process model is the owner's round-3 ruling on idea `000247`: a **persistent daemon
with watchers**. This revision (2026-09-16) integrates the full adversarial audit of the first
draft — eleven blockers and seventeen majors, all accepted — and the owner's round-4 rulings:
**strict broker-first**, a **tracked run ledger**, a **standalone stopgap** restored, and
**daemon proposes, human commits** for every write to `dev`. The remote/MCP future for ledger
and write mediation is idea `000250`, out of scope here.

## 1. The pipeline is four run kinds, not one long run

`ARCH-006` draws nine stages as one flow, but the flow changes cardinality twice: many ideas
feed one partition, one partition yields many tracks and therefore many plans, one plan yields
many phases. The orchestrator therefore runs **four graph kinds**, composed through the
repository's records rather than through graph state:

| Run kind | Covers | One run per | Starts when | Ends when |
|---|---|---|---|---|
| `intake` | Stage 2 | idea | The tick sees a `created` event newer than the intake watermark (stage 1 and G1 happen in conversation, before any graph — a declined capture writes no event and no run exists) | The idea leaves `open` by any legal transition — `triaged`, `reviewing`, `promoted`, or `discarded` |
| `batch` | Stages 3–7, gates G2–G3 | partition run, **fanning out to one branch per accepted track** | The owner asks, or a stated threshold of triaged ideas is met once the owner sets one (on-demand only until then) | Every accepted track's plan has its phases registered with a ratified ordering, or the track's branch ends rejected |
| `unit` | Stage 8, gates G4–G5 | backlog phase | The phase is startable under §6's capacity rules **and** its claim commit is on `dev` (human-committed; the daemon only proposes) | The phase is integrated and completion-reviewed; or parked `blocked` with reason and resume condition; or abandoned — claim released, phase returned to `queued` |
| `realization` | Stage 9, gate G5 | delivered idea | A `unit` run completes for a phase whose plan traces to the idea (§8's trace procedure) | The idea reaches its terminal delivered state (in whichever form `phase-irs-09`'s ruling gives it — new status or annotation pattern; §3 carries both branches), or the shortfall is a recorded finding |

Fan-in and fan-out live in the records and, inside a `batch` run, in LangGraph's `Send`
fan-out: G3 is **per plan**, so each track is its own branch with its own G3 interrupt and its
own revise loop, and a slow track never blocks a fast one. No run holds a reference to another
run — only to record state. Phase statuses `deferred` and `cancelled` end or preclude a `unit`
run exactly as `complete` does: the record wins.

## 2. Process model: one daemon, one lock, and a tick that works alone

One daemon process:

```
uv run python -m src.orchestrator start | stop | status | tick | gate | halt | resume-dispatch
```

- **`start`** runs the loop: watchers wake it, and every wake executes one **tick**.
- **`tick`** is the whole scheduler as one callable: reconcile against the records, start runs
  whose start condition holds, advance every non-interrupted run, and write ledger entries.
  The command form runs one tick with no daemon — the degraded mode and the test surface.
  **The tick takes the same lock the daemon holds**: a manual tick while the daemon is alive
  waits or exits with "daemon holds the lock", never runs concurrently. One tick executes at a
  time, ever; run starts are additionally idempotent by natural key (§4).
- **`status`** renders the run table and the gate queue, decision-ready, and names the lock
  holder's pid and freshness.
- **`gate`** records an owner decision and marks the target run for resumption at the next tick.
- **`halt` / `resume-dispatch`** operate the kill switch (§9) — first-class verbs, not a
  `touch` command.

**The lock** is `flock` on `data/orchestrator/lock`, with the holder's pid and start time
written into the file for `status` to report. `flock` releases on process death, so a
`SIGKILL`'d daemon never wedges the next start; a stale pid in the file is informational only.
`stop` signals the daemon (SIGTERM), which finishes the current tick and releases the lock.

**Watchers** are repo-internal only, per the round-3 ruling's boundary: the idea log, the
decision inbox, and a periodic timer. A watcher is **only a wake-up** — it carries no payload
and no offset. Every tick re-reads state through the sanctioned readers (`load_events()` /
`fold()` for ideas), so partial-line reads, editor rewrites, rebases and merges of the tracked
log cannot corrupt anything: if a read raises mid-write, the tick logs it, skips that source
this tick, and the timer retries. No byte offsets exist anywhere; the intake watermark (§4) is
an event timestamp, not a file position. External triggers remain `phase-auto-03`'s territory;
`000249` records that an external gateway would need its own neutral inbox with writer
discipline, since the idea log's sanctioned-writer rule (`OPS-005`) forbids anyone else
writing there.

**Where the daemon runs**: the **primary checkout only**. Worktrees each carry their own copy
of the tracked logs and their own gitignored `data/`; a daemon started in one watches a copy
and loses its state at `git worktree remove`. Startup refuses to run if
`git rev-parse --git-common-dir` shows a linked worktree. This is a deliberate, recorded
exception to the every-session-works-in-a-worktree rule: the daemon is not a session — it
edits nothing and commits nothing (§6) — and the one thing it must watch, the lock table on
`dev`, exists only in the primary checkout.

**Attended-only until the broker.** Per the owner's round-4 ruling and `PLAN-032`'s
broker-first requirement (`REQ-017` R01), the orchestrator dispatches **no agent unattended**
until the capability broker (`phase-auto-02`) exists and gates it. Until then `start` still
watches and maintains the queue, but every dispatch batch requires an owner-initiated tick
with an explicit `--dispatch` flag. `phase-irs-04` therefore depends on `phase-auto-02` in the
backlog. The standalone stopgap (`phase-irs-01`, §10) is likewise owner-visible triage-only
dispatch and carries its own bound.

## 3. Graph state and the re-derivation rule

Each run's graph state is **three fields**: `run_id`, `kind`, `refs` (idea ids, document
codes, phase id, branch name, track key inside a batch fan-out). Nothing else — no attempt
counters, no budget totals. `attempts` and `budget` are read from the **run ledger** (§5),
which is what makes `ADR-018`'s disposability claim true: delete `checkpoints.sqlite` and
nothing resets, because nothing lived there.

**Re-keying, not rewinding.** LangGraph offers no API that moves a thread's cursor to an
arbitrary stage; `update_state` forks history and cannot cross an `interrupt()`. The reconcile
step therefore never edits a checkpointed thread: when a checkpoint and the repository
disagree, **the thread is abandoned and a new `thread_id` is opened whose initial state names
the re-derived position**. Thin state is what makes this cheap — the new thread needs only
`run_id, kind, refs`, and the ledger carries continuity (§5). The same mechanism implements
G3's *amend* verb (§7).

Re-derivation per kind — the authoritative record and the rule:

| Run kind | Authoritative record | Rule |
|---|---|---|
| `intake` | The idea's folded status | `open` and created after the intake watermark → a run should exist; any other status (`triaged`, `reviewing`, `promoted`, `discarded`) → the run is complete or never needed. Ideas `open` from before the watermark are the batch `/idea-triage` command's business, or an owner-initiated dispatch — never reconcile's |
| `batch` | The partition record; REQ/PLAN document existence; registered phases in `backlog.yaml`; gate decisions' repository artifacts | Per track: the furthest artifact that exists is the position; a disagreeing thread is abandoned and re-keyed there |
| `unit` | The phase's `status` and `agent`, branch existence, `_tmpagent/` claim state, merge state on `dev` | Same rule; a phase `complete`, `deferred` or `cancelled` on `dev` ends the run whatever the checkpoint says; a released claim with the phase `queued` means abandoned — no run |
| `realization` | Evidence annotations and terminal delivered state on the idea (either form per `phase-irs-09`'s ruling) | Terminal state or a recorded shortfall finding ends the run; an unresolved check re-queues |

## 4. Reconcile, the watermark, and idempotent starts

Every tick begins by re-deriving what should exist. Two bounds keep this from ever becoming
unattended spend:

- **The intake watermark** — `data/orchestrator/watermark` records the timestamp of the last
  `created` event reconcile has considered (the idea log's event name is `created`; the writer
  subcommand is `add`, and the watcher must match the event, not the verb). On first start the
  watermark initializes to *now*: the 41 ideas currently `open` are deliberately not swept into
  dispatch. Pre-watermark open ideas remain reachable by the batch `/idea-triage` skill or an
  explicit owner dispatch.
- **Idempotent starts** — a run's natural key is `(kind, primary ref)`: one `intake` run per
  idea id, one `unit` run per phase id, one `batch` run per partition record, one
  `realization` run per idea id. Reconcile consults the ledger for an existing non-terminal
  run under the key before starting one, so two ticks (impossible while the lock holds, but
  cheap to guarantee anyway) or a re-keyed thread never double-start.

## 5. The run ledger: tracked, schema'd, sanctioned

Per the owner's round-4 ruling, the durable ledger is **`_data/runs.jsonl`** — the idea log's
own pattern applied to runs: append-only JSONL, a JSON Schema (`schemas/run.schema.json`), and
a single sanctioned writer (`tools/append_run.py`, with its `OPS-*` document). Events: run
started (with natural key and refs), stage transition, dispatch (agent, budget granted),
dispatch result (usage actually spent, outcome), gate reached, gate decision applied, revise
attempt, park, abandon, terminal. `REQ-022` R18's reconstruction and R24's metrics read this
file; `attempts` and `budget` are folds over it (§3).

A tracked file means commits. The daemon **never commits** (§6): ledger appends accumulate as
uncommitted modifications in the primary checkout, exactly like idea-log appends already do
between capture commits, and they are committed by the humans-in-the-loop at the natural
sittings — a gate decision, a session close, a capture commit. The `gate` and `status`
commands surface an uncommitted-ledger reminder. Losing uncommitted appends to a catastrophe
loses hours of operational detail, never truth: every entry's substance is re-derivable from
the repository artifacts the transitions produced — the ledger is the *indexed narrative*, the
records are the truth, which is the same relationship the ledger's future remote home
(`000250`) will preserve.

`data/orchestrator/` retains only genuinely disposable machinery: the lock, the checkpointer
(`checkpoints.sqlite`), and the watermark. The decision inbox and kill switch move out of it
(§7, §9), so nothing under `data/` is load-bearing — consistent with the repository's
"`data/` is derived" rule.

## 6. The daemon writes nothing to dev: propose, then observe

Per the owner's round-4 ruling, every `dev` write the pipeline needs is **proposed by the
daemon and committed by a human**. This resolves the audit's findings that honoring `ADR-003`
would otherwise have the daemon committing claims, parks and `blocked` states unattended:

- **Claims**: a `unit` run's first queue item names the exact claim edit (`status: active`,
  `agent`, catalog date) and the commands to commit it on `dev`. The run starts only when
  reconcile observes the claim on `dev`.
- **Capacity is the governance validator's own law**, computed before proposing, not invented:
  `max_active` (3), one phase per agent, the Conflicts rule (disjoint `systems`, deliverable
  paths and dependency chains — noting every `phase-irs-*` item shares `sys-realization`, so
  irs phases serialize against each other by construction), and `next_up` order overriding
  priority. The daemon proposes only claims the validator would accept, and re-checks after
  each observed `dev` change. Human sessions' claims are peers with priority: the daemon never
  proposes over one and drops proposals that a human claim supersedes.
- **Parks and abandons**: same pattern — the queue item names the `blocked` edit with
  `blocked_reason` and `resume_when` (which the validator requires), or the claim-release
  returning a phase to `queued`.
- **The unit run's hand-off duties are explicit steps, not assumptions.** Before a unit run
  reaches G4 its developer agent has: written the session record
  (`--next-code session`, in the worktree); released every `_tmpagent/` claim the run opened;
  and run `git rebase dev` followed by a green `uv run python -m src.governance` and
  `uv run pytest`. The G4 queue item presents that green post-rebase output as evidence and
  names the merge command as the owner's action — the rebase-then-green rule is the
  precondition the queue item proves, not a step the owner is left to remember. G5 items then
  have a session record for `/session-close` to finish, which is what makes batched
  completion review (`REQ-022` R02) actually closable.

## 7. Gates: interrupts that dispatch nothing, decisions with writer discipline

G2 and G3 are interrupts in `batch` runs (G3 once per track branch); G4 and G5 in `unit` runs;
G5 in `realization`. Two implementation rules from the audit:

- **A gate node contains the `interrupt()` and nothing else.** LangGraph replays the
  containing node from its start on resume, so all work — assembling the decision-ready
  proposal, dispatching any agent, writing the ledger entry — happens in the preceding node,
  checkpointed before the gate node begins. Resume re-executes an empty wrapper, costing
  nothing and duplicating nothing. One interrupt per node, always.
- **The decision inbox gets the idea log's discipline, scaled down.** It moves to
  **`_data/decisions.jsonl`** — tracked for the same reason the ledger is — with a schema
  (`schemas/decision.schema.json`), the `gate` subcommand as its sole sanctioned writer, and a
  dedup key `(run_id, gate, decision_seq)`. A second decision for an already-resumed gate is
  refused by the writer, not absorbed by the reader. The durable truth of a decision remains
  the repository artifact it produces; the inbox is how the resumption is requested.

**The three decision verbs.** *Approve* resumes the interrupted branch forward. *Reject*
resumes it down its failure edge (revise or terminal, per the stage's failure path). *Amend* —
the common G3 case — is **re-keying with the owner's artifact**: the owner's amendments are
applied to the repository artifact (the reordered `next_up` proposal, the edited phase set),
the branch's thread is abandoned, and reconcile opens a new thread at the position the amended
records prove. No graph surgery, same mechanism as §3.

## 8. Dispatch, budgets, and the realization trace

**Dispatch adapter.** One module owns every agent invocation: binds the role contract
(`phase-irs-03`), checks the kill switch and remaining budget before dispatch, records
dispatch and result in the ledger, and enforces never-do by tool policy where the SDK
supports it. Developer agents work in worktrees per `ADR-003` unchanged.

**Budget semantics** (`REQ-022` R20), stated so `phase-irs-04` invents nothing: the
authoritative counter is the Claude Agent SDK's reported usage on each dispatch result —
input plus output tokens, including subagent usage where reported — summed from the run's
ledger entries. The pre-dispatch check blocks a dispatch when spent ≥ cap. A single in-flight
dispatch can overshoot; each dispatch therefore carries its own per-dispatch ceiling
(configured per role contract) so the overshoot is bounded by one dispatch's ceiling, and the
overshoot is recorded. "Parks the run" means: the run takes a `parked: budget` ledger entry,
its thread is left interrupted at a synthetic budget gate, and it appears in the G-queue for
the owner to raise the cap or end the run. Spend persists across process death because it
lives in the ledger, not in memory or graph state.

**Realization trace** (audit M9): a `batch` run, at the moment it registers a plan's phases,
writes a ledger entry mapping `{plan doc id → [contributing idea ids]}` — it knows both ends
at that moment, and `fold()`'s `promoted_to` supplies the owner-visible half where promotion
events exist. A `realization` run starts from that ledger mapping when a `unit` run under the
plan completes, and its terminal write follows whichever form `phase-irs-09`'s ruling gives
delivered state. Ideas that entered work without promotion events (the historical majority)
are reachable because the mapping was recorded at registration time, not inferred later.

## 9. Kill switch and halt semantics

The kill switch is a flag file at **`_working/orchestrator-halt`** — gitignored but under the
never-deleted-without-approval protection, and outside `data/` so no rebuild or reset tool can
disarm it (the audit found `data/` is exactly what `rebuild_db.py` and `demo_reset.py` treat
as regenerable). `halt` writes it; `resume-dispatch` removes it; the dispatch path checks it
immediately before every dispatch, so it works while the daemon is wedged mid-loop —
dispatches in flight finish, nothing new starts. `phase-irs-11` builds the enforcement and its
tests; the verbs ship with the skeleton so the control is owner-operable from day one.

## 10. Package layout, the stopgap, and testing

```
src/orchestrator/
  __init__.py
  __main__.py     # CLI: start/stop/status/tick/gate/halt/resume-dispatch
  daemon.py       # lock, watchers, loop → tick
  tick.py         # reconcile + start + advance; the only scheduler
  graphs/         # intake.py, batch.py, unit.py, realization.py
  state.py        # the three-field run state; re-derivation per kind
  dispatch.py     # SDK adapter: contracts, budgets, kill switch, ledger
  gates.py        # queue rendering; builds resumes from decisions
  ledger.py       # reads _data/runs.jsonl through its sanctioned path
```

LangGraph's import surface is `graphs/`, `tick.py`, `state.py` (the State schema is LangGraph
API) and `gates.py` (`Command(resume=…)`); `pyproject.toml` pins `langgraph` and the SQLite
checkpointer, and nothing outside `src/orchestrator/` imports either.

**The stopgap is standalone again** (round-4 ruling undoing the inversion): `phase-irs-01`
ships a self-contained tool under `tools/` — a post-append dispatch hook plus a sweep command,
watermark-bounded and budget-capped like everything else — with no orchestrator dependency in
either direction. `phase-irs-04` absorbs its duty into reconcile when the daemon lands, and
the tool retires; its interim declaration is honorable because deleting it deletes no part of
the daemon.

**The generic-host seam `000248` wants does not exist yet** (audit M16): watchers and run
kinds are hardcoded in this design, and reconcile speaks pipeline vocabulary. Generalizing —
a watcher registry, a run-kind protocol — is that idea's future work, deliberately not
smuggled into the skeleton.

**Testing**: the pipeline logic is exercised entirely through `tick` — stub dispatcher,
tmp-path record fixtures, the forced-failure drill (`phase-irs-12`) driving every failure
edge. The daemon adds watchers, the lock and signal handling over the tick, and gets its own
narrow tests for exactly those: start/stop, lock contention (a manual tick against a live
daemon), and stale-lock recovery after a kill.

## 11. Failure paths of the orchestrator itself

The stages' failure paths live in `ARCH-006`; these are the machine's own, per the audit's
demand that no cell be blank:

| Failure | Behavior |
|---|---|
| Dispatch times out or the SDK errors | Ledger `dispatch failed`; one retry next tick; second failure follows the stage's failure path (revise/escalate/park) |
| A worktree the unit run needs already exists | Never reused and never removed: the run parks with the finding; a human resolves — it may be a peer's |
| Rebase conflicts in a unit run | The developer agent stops per `AGENTS.md`'s collision rules; the run parks with the conflict named; source conflicts are reported as declaration defects, not merged through |
| The idea log or a tracked input fails to parse mid-tick | That source is skipped this tick and retried on the timer; other run kinds proceed; `status` shows the skip |
| The checkpointer is corrupt or deleted | Threads are re-keyed from the records (§3); continuity re-derives from the ledger |
| The daemon crashes | `flock` releases; next `start` reports the stale pid and proceeds; the first tick reconciles |
| The ledger has uncommitted appends at a catastrophe | Operational narrative since the last commit is lost; truth re-derives from repository artifacts (§5) |

## 12. What this changes in the backlog

- `phase-irs-04` — scope rewritten against this revision (four-kinds skeleton: `intake` graph,
  tick, lock, state, gates, ledger reader, the CLI verbs including halt; attended-only);
  gains `depends_on: [phase-irs-03, phase-auto-02]` per the broker-first ruling; deliverables
  gain `schemas/` and `tools/` for the run-ledger and decision schemas and writers.
- `phase-irs-01` — restored standalone: `depends_on: []`, deliverables `tools/` and
  `docs/08-governance/` (the OPS document is again for a real tool), next_action updated to
  the ruled mechanism.
- **`phase-irs-14` (new)** — the `batch` graph: `Send` fan-out per track, per-track G3
  interrupts, the amend-as-re-key flow, the plan→ideas trace entry. Depends on `phase-irs-04`.
- **`phase-irs-15` (new)** — the `realization` graph against `phase-irs-09`'s landed ruling.
  Depends on `phase-irs-04`, `phase-irs-09`.
- `phase-irs-12` — gains `phase-irs-14` and `phase-irs-15` as dependencies; the end-to-end
  trace needs all four graphs.
- `REQ-022` R16's verification is amended (there is no cached field to corrupt in three-field
  state): the test deletes or corrupts the checkpoint store and confirms re-keyed threads
  resume at the re-derived position.

## Open questions

1. **Watcher library or poll.** `watchfiles` versus a short poll of two mtimes; behavior is
   identical either way. `phase-irs-04` decides.
2. **The partition threshold N.** On-demand-only until the owner states a threshold; where N
   lives (config file the workbench can edit, or a constant) is decided when the owner first
   sets it.
