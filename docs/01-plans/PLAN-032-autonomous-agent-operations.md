---
schema_version: 1
id: doc-autonomous-agent-operations
code: PLAN-032
title: Autonomous agent operations (P5)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-15'
systems: [sys-api, sys-delivery, sys-governance]
depends_on: [doc-autonomous-agent-operations-requirements, doc-adr-multi-agent-concurrency]
---

# Autonomous agent operations (P5)

## Summary

Programme `P5` of the twelve. Five ideas in one fine group, all assuming the system operating with no
chat session open. All four partition analysts placed them together, control included — the strongest
membership signal in the partition, because it cannot be inherited framing.

| Group | Ideas | What it covers |
|---|---|---|
| `G24` Gateway, ledger, worker, broker, librarian | `000028`, `000029`, `000030`, `000031`, `000020` | The ingress boundary, the durability layer, the supervisor, the authorisation gate, and a heavier coordination proposal already ruled on |

Partition-time sizing was "4 phases + design" at group level and "10+ phases if built in full" at
programme level, with the note that this is **the most speculative programme here**. This plan lands
**six**, and treats the speculation as the thing to state rather than hide.

## The evidence problem, stated plainly

Four of these five ideas describe infrastructure for a mode of operation this repository has barely
exercised. They came from a research pass, not from incidents. That is not a reason to refuse to plan
them, but it is a reason to say so, because a plan that reads like the other eleven implies an
evidence base this one does not have.

There is exactly one real data point, and it arrived while this plan was being written. **The
unattended run of 2026-09-15 executed a batch of programme-finalize phases with no chat session
driving each step, and used none of this infrastructure.** No gateway, no ledger, no worker, no
broker. What it used instead was a person granting scoped advance authority in writing — naming what
was permitted, what was not, and what to do on failure — and an agent recording every departure from
it for review.

Two things follow, and both shape this plan.

**The authorisation gate is the piece that was actually load-bearing.** The thing that made that run
safe to leave unattended was a bounded capability set: merge locally but never push, write these ten
phases complete and no others, never touch `ts/` or `src/`, never write to the idea log. That was
enforced by an agent choosing to comply, which is precisely the enforcement `000031` calls
insufficient. It held, and it held because one agent read carefully — which is not a mechanism.

**The other three are less urgent than their sizing suggests.** A run that completes in one sitting
needs no ledger; a batch a person starts deliberately needs no gateway; work nobody queues needs no
worker. They become necessary when runs are frequent, unattended and triggered by something other
than a person deciding to start one. None of those is true yet.

## The chosen design

### 1. The broker is built first, inverting the partition's ordering

The partition sequences `000028` → `000029` → `000030`, "with `031` required before anything runs
unsupervised". **Ruled: `000031` is built first, ahead of all three.**

Stated as a precedence note, the gate is satisfiable by building the gateway, ledger and worker and
then adding the broker before switching anything on. That reading is wrong in the way gates are
usually wrong: a gate constructed after the things it gates has never gated anything, and the window
between "the worker drains queued runs" and "the broker denies capabilities" is exactly the period in
which an unattended run happens with nothing authorising it.

`R01` therefore makes the ordering itself the observable — the only row in `REQ-017` that describes a
sequence rather than a component. It is also the phase's acceptance condition, which asks for the
`000031` gate to be stated as a precondition for anything running unsupervised. Stating it in prose
would satisfy the letter; building it first is what satisfies the intent.

The cost accepted: the broker is the least immediately useful of the four, because with nothing
running unattended there is nothing to authorise. It will look like over-engineering for as long as
the rest of the programme is unbuilt. That is the correct shape for a safety gate.

**But the ordering does not force the broker's full policy up front, and that distinction matters.**
Building it first means designing a capability taxonomy against zero real capability requests — the
gateway and ledger are what would generate the requirements it authorises. So `phase-auto-01`'s
design decides which of two shapes ships:

- **A full policy broker** — the capability set, the approval path and the decision record all
  specified up front, if the design can name the capabilities from what already exists.
- **An enforcement point with a permissive default** — the tool-boundary mechanism and the refusal
  path built and wired, with a policy that denies nothing until real requests exist to write it
  against.

Either satisfies `R01`, because both put a working refusal path ahead of every unattended component.
The second is the honest choice if the design finds it is guessing at the taxonomy, and it preserves
the gate without paying for a policy nobody has requirements for. The ruling is *broker first*, not
*complete broker first*.

### 2. `000020` is not built, and this plan carries the owner's ruling rather than re-making it

The phase's scope asks for a ruling on `000020`, which the control analyst nominated for decline in
favour of `000128`. **The owner already ruled, on 2026-09-13: kept, sequenced behind `000128` — build
the light `_tmpagent/` mechanism first, revisit only if it proves insufficient.**

That ruling is recorded in the partition's own owner-rulings table and it stands. This plan's job is
to act on it, not to re-open it, so `phase-auto-06` is a **revisit phase with a precondition**, not a
build phase: it runs only after `phase-agx-07` has shipped the `_tmpagent/` extension and it has been
used, and `R15` requires the revisit to name cases where the light mechanism actually fell short. A
revisit concluding "still not needed" satisfies the row and is the expected outcome.

`R16` guards the part of `000020` that would do damage if it arrived by drift: its MCP server would
become a second authority over documents, claims and worktrees, replacing `backlog.yaml` as the lock
table and the governance validator as the lock check. Both work. Two authorities that can disagree is
the failure mode, and it is worth asserting rather than trusting.

The other two thirds of `000020` are elsewhere by prior placement: the vector database is `P6`'s
retrieval ground, and the Librarian's context-curation role overlaps both `P6` and `P4`'s lighter
mechanism.

### 3. The design phase comes first and is allowed to recommend building less

The partition sizes this group as "4 phases + design". The design phase is `phase-auto-01`, and it is
given an unusual remit: **it may conclude that some of `000028`, `000029` or `000030` should not be
built yet, and say so.**

This is not a licence to descope quietly. It is the recognition that the four components were
"deliberately decomposed from one proposal so each could be evaluated alone", and evaluating each
alone is work nobody has done. `000030` says of itself that it "only makes sense once the trigger
gateway and run ledger exist; on its own it's a scheduling daemon with nothing to schedule". A design
phase that cannot act on that observation is a design phase in name.

The three build phases are sized anyway, so the programme has a shape if the design confirms all
three. If it does not, they are returned to `queued` with the design's reasoning attached, which is
cheaper than discovering it mid-build.

### 4. Provider neutrality is asserted twice, deliberately

`R07` requires the gateway to be provider-neutral and `R10` requires the same of the execution
adapter. Both ideas state it independently, and the two are separable: a neutral gateway can feed a
provider-locked adapter, which is the likelier failure because the adapter is where a model's shape
leaks in. Asserting it once would leave the harder half unchecked.

### Which of these need a decision record

**One.** The broker-first inversion (decision 1) contradicts a sequencing the partition states
explicitly and that four analysts reviewed. A future reader finding the broker built first needs to
know that the ordering was chosen against the partition's own recommendation, and why.
`phase-auto-01` writes it as part of the design.

Decision 2 needs none — it is the owner's existing ruling, already recorded in the partition's
owner-rulings table, and duplicating it into an ADR would create a second place for it to drift.
Decisions 3 and 4 are recorded in `REQ-017`'s rows and in the phases' scopes.

## Implementation phases

Six phases under `phase-auto-*`, registered in [the backlog index](../09-backlog/README.md).

| Phase | Title | Depends on |
|---|---|---|
| `phase-auto-01` | Design the autonomous-operations architecture and rule what to build | — |
| `phase-auto-02` | Build the capability and approval broker, enforced at the tool boundary | `01` |
| `phase-auto-03` | Build the external trigger gateway with deduplicated events | `01`, `02` |
| `phase-auto-04` | Build the durable run ledger with resumable steps | `01`, `02` |
| `phase-auto-05` | Build the supervised worker, watchdog and abandoned-run review | `03`, `04` |
| `phase-auto-06` | Revisit `000020` against the delivered `_tmpagent` mechanism | `phase-agx-07` |

### Sizing against the partition

Group-level sizing was "4 phases + design"; this plan lands **six**, which is that plus the `000020`
revisit the owner's ruling requires. Programme-level sizing was "10+ phases if built in full", and
this plan does not reach it because it does not commit to building in full — `phase-auto-01` is
empowered to recommend less, and the three build phases are sized rather than guaranteed.

The ordering differs from the partition's. `000031` moves from "required before anything runs
unsupervised" to first, per decision 1. `000028` and `000029` become siblings rather than a chain:
they were sequenced `028` → `029` in the partition, but neither depends on the other — the gateway
normalises events and the ledger persists runs, and each is testable without the other. Only
`000030` genuinely needs both, which its own body says.

## Execution order and real concurrency

`phase-auto-01` blocks everything except the `000020` revisit. After it, `phase-auto-02` is the
single gate. Then `phase-auto-03` and `phase-auto-04` can run **in parallel** — they are the only
genuine concurrency in this programme, and they are siblings precisely because the partition's chain
between them does not hold.

`phase-auto-06` depends on `phase-agx-07` in `P4` and on nothing in this programme. It is the third
cross-programme dependency this batch has produced.

The critical path is four deep: `01` → `02` → `03`/`04` → `05`.

**This programme should run after `P4`**, and not only for `phase-auto-06`. `P4`'s `phase-agx-01`
documents truncation handling and `phase-agx-05` writes the delegation methodology, both of which
bear directly on what a run ledger needs to record. Building the ledger first means guessing at them.

## Requirement coverage

Every row of `REQ-017` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 The broker gates before anything runs unattended | `phase-auto-01`, `phase-auto-02` |
| R02 Narrow, named capability sets per run | `phase-auto-02` |
| R03 Denials enforced at the tool boundary | `phase-auto-02` |
| R04 Approvals carry scope, reason, expiry, immutable decision | `phase-auto-02` |
| R05 Four trigger sources normalised to one event shape | `phase-auto-03` |
| R06 A duplicate trigger produces one run | `phase-auto-03` |
| R07 The gateway is provider-neutral | `phase-auto-03` |
| R08 Every field `000029` names, persisted per run | `phase-auto-04` |
| R09 An interrupted run resumes without repeating side effects | `phase-auto-04` |
| R10 The execution adapter is provider-neutral | `phase-auto-04` |
| R11 Concurrency limits and quiet hours enforced | `phase-auto-05` |
| R12 A stale heartbeat marks a run abandoned, never retried | `phase-auto-05` |
| R13 Kill and restart resumes queued work | `phase-auto-05` |
| R14 A review surface for abandoned runs | `phase-auto-05` |
| R15 `000020` revisited only on evidence | `phase-auto-06` |
| R16 Nothing becomes a second claim authority | `phase-auto-01`, `phase-auto-06` |

## Key references

- **The requirement** — [REQ-017](../06-requirements/REQ-017-autonomous-agent-operations.md).
- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P5`, and its owner-rulings table, which carries the `000020` ruling this plan acts on.
- **Multi-agent concurrency** ([ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md)) — the claim protocol `R16` protects from being replaced.
- **Agent engineering and delegation** ([PLAN-031](PLAN-031-agent-engineering-delegation.md)) — `phase-agx-07` is the `_tmpagent/` extension `phase-auto-06` waits on, and `phase-agx-01`/`-05` inform what the ledger records.
- **The prompt-pack protocol** ([GOV-008](../08-governance/GOV-008-prompt-pack-protocol.md)) — the cost and hygiene conventions an unattended run currently follows by convention rather than by enforcement.

## Known facts not to rediscover

- **The owner ruled on `000020` on 2026-09-13**: kept, sequenced behind `000128`, revisit only if the
  light mechanism proves insufficient. Do not re-argue it; `phase-auto-06` gathers evidence.
- **`000030` says of itself that it has no purpose until `000028` and `000029` exist.** Its own body
  calls it "a scheduling daemon with nothing to schedule" otherwise.
- **`000028` and `000029` do not actually depend on each other**, despite the partition's chain. Each
  is testable alone; only `000030` needs both.
- **`000029`'s persisted fields are a list, not a summary.** `R08` reproduces them exactly: ten
  fields as the idea writes them, with model and tool versions as the single comma-separated item it
  names rather than split into two.
- **This is the most speculative programme in the partition**, by the partition's own assessment.
  Four of its five ideas came from a research pass rather than an incident, and the plan says so
  rather than implying an evidence base it lacks.
- **The one real data point is the unattended run of 2026-09-15**, which operated with no chat session
  and none of this infrastructure, bounded instead by written advance authority an agent chose to
  honour. That is evidence about which piece matters most, and it points at `000031`.
