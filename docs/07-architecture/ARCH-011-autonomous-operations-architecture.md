---
schema_version: 1
id: doc-autonomous-operations-architecture
code: ARCH-011
title: Autonomous operations architecture and build/defer ruling
kind: architecture
status: draft
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-api, sys-delivery, sys-governance]
depends_on: [doc-autonomous-agent-operations-requirements, doc-autonomous-agent-operations, doc-broker-first-autonomous-operations]
---

# Autonomous operations architecture and build/defer ruling

This document is the design pass PLAN-032 (`doc-autonomous-agent-operations`) reserves for
`phase-auto-01`: evaluate the four autonomous-operations components — the trigger gateway (`000028`),
the run ledger (`000029`), the supervised worker (`000030`) and the capability and approval broker
(`000031`) — each on its own, and rule what gets built now versus deferred. It also records which
shape the broker ships in. It is a design and ruling document, not an implementation plan; the three
components ruled for building still go through their own phases (`phase-auto-02` through
`phase-auto-04`) to be specified and built.

The broker-first ordering itself — building `000031` ahead of the other three — is a decision with
its own reasoning and is recorded separately in
[ADR-022](../04-decisions/ADR-022-broker-first-autonomous-operations.md). This document assumes that
ordering and rules on what follows from it.

## Evaluating each component alone

The four ideas were deliberately decomposed from one proposal "so each could be evaluated alone."
Evaluating each in isolation means asking, for each one: does it have a reason to exist before the
others do, and is there a real request it would be built against, or only an anticipated one.

### The broker (`000031`) — build now

The broker's job is to refuse. It needs no other component to have a reason to exist: an agent
running any task at all is already something the broker can gate, because the question "is this
agent allowed to do this" applies to every run, chat-driven or not. The evidence for building it now
is not anticipated — the unattended run of 2026-09-15 is a real instance of an agent being trusted
with unsupervised capability, and the thing that made it safe was exactly the kind of bounded,
written capability set this idea proposes to make mechanical rather than a matter of an agent's
compliance. Ruled: build now, first, per ADR-022. Its shape is ruled below.

### The trigger gateway (`000028`) — defer

The gateway's job is to accept and normalize events from outside a chat session — filesystem,
schedule, webhook, CLI — into one event shape. Evaluated alone, it has a real, narrow scope
(normalization and deduplication) that does not depend on the ledger or worker to be buildable or
testable: a fixture event can be submitted through each adapter and its normalized shape checked
without either.

What it lacks is a caller. Nothing in this repository currently needs an external trigger — every
agent workflow here starts because a person opens a chat session or runs a slash command. Building
the gateway now means building deduplication and event-shape normalization against event sources
that exist only in the idea's own description, not against a real integration this repository is
waiting to make. That is different from the ledger and worker's dependency problem (below): the
gateway is technically buildable and testable alone, but there is no consumer for its output yet,
because the ledger it would feed is also being deferred (see below) and no other consumer exists.

**Ruled: defer.** Reasoning attached, per the phase's requirement that a deferred component not be
dropped silently: the gateway is buildable in isolation but has no current caller and no downstream
ledger to feed. Building it now would be building an ingress boundary for a system that has nothing
behind it yet. It is not deprioritized because it is hard or because the partition sequenced it
after the broker — it is deprioritized because nothing in this repository currently produces the
events it would normalize.

### The run ledger (`000029`) — defer

The ledger's job is to persist a run's correlation id, triggering payload hash, model/tool versions,
context-pack hash, budget, timeout, retry count, checkpoints, produced artifacts and disposition, and
to support resuming an interrupted run without repeating completed side effects. `000029`'s own text
raises exactly the question that matters here: "how much of this is worth building before there's a
second real trigger-driven workflow to prove it against — a durability layer with one caller is hard
to validate." There is currently zero trigger-driven callers, not one, because the gateway that would
produce them is itself deferred above.

A resumability contract designed against no real interrupted run is a contract designed by guessing
at what actually needs to survive a crash. `PLAN-031`'s truncation-handling work (`phase-agx-01`) and
delegation methodology (`phase-agx-05`) — both in the P4 programme this repository sequences before
P5 — bear directly on what a run record needs to capture; building the ledger schema ahead of them
means guessing at fields that work has not yet settled.

**Ruled: defer.** Reasoning attached: the ledger's core design question (what must a checkpoint
capture to resume without repeating a side effect) cannot be answered well against zero real
interrupted runs, and the component it would primarily serve (the gateway) is also deferred. This is
not a statement that durability is unneeded — the 2026-09-15 run's own interruption is evidence it
eventually is — only that building the schema now is premature relative to the evidence available.

### The supervised worker (`000030`) — defer

`000030` names its own dependency condition without qualification: "this only makes sense once the
trigger gateway and run ledger ideas above exist; on its own it's a scheduling daemon with nothing to
schedule." Evaluated alone, it fails its own bar for existing — there is no queue for it to drain,
because nothing produces queued runs yet (the gateway is deferred) and nothing would record their
state (the ledger is deferred). Concurrency limits, quiet hours and heartbeat-based abandonment
detection are all meaningless against zero runs.

**Ruled: defer**, with the least argument required of the three: `000030`'s own body already makes
this case, and the ruling here is acting on stated fact rather than discovering it.

## What building only the broker leaves this programme able to do

With the broker built and the other three deferred, this repository gains a mechanical enforcement
point at the tool boundary and nothing else from this programme. No trigger source exists yet.
Nothing is unattended in a way that would call the broker outside of a chat session today — the
broker's near-term use is enforcing capability bounds inside agent sessions that already run today
(the pattern the 2026-09-15 run improvised by hand), not gating a trigger-driven system that does not
exist yet. That is accepted: PLAN-032 states this plainly as the most speculative programme in the
partition, and a design phase that cannot recommend building less than the partition sized is a
design phase in name only. `phase-auto-03` through `phase-auto-05` were already `status: queued` in
`docs/09-backlog/backlog.yaml`, gated by their `depends_on` on `phase-auto-01`, before this phase
ran, and this phase makes no edit to that file — they remain `queued` rather than returning to it.
This document records the reasoning for deferring the three components; it is not dropped from the
backlog, and this document is the reasoning a reader of the backlog should be pointed to, but nothing
here or in `backlog.yaml` itself currently cites it.

## Which shape the broker ships in

`REQ-017` gives two shapes that both satisfy `R01`:

- **A full-policy broker** — the capability set, the approval path and the decision record all
  specified now, if the design can name the capabilities from what already exists.
- **An enforcement point with a permissive default** — the tool-boundary mechanism and refusal path
  built and wired, with a policy that denies nothing until real capability requests exist to write it
  against.

**This design finds it is guessing at the capability taxonomy, and ships the permissive-default
shape.** The evidence: the only real instance of scoped capability enforcement this repository has —
the 2026-09-15 run — was bounded by a person writing specific, situational grants ("merge locally but
never push", "write these ten phases complete and no others", "never touch `ts/` or `src/`", "never
write to the idea log") for that run, not by a pre-declared, general-purpose capability catalog. A
named taxonomy written now (`repository-read`, `source-mutation`, `external-network`, `publication`,
as `000031`'s own body suggests) would be an extrapolation from one instance, not a set drawn from
multiple real requests. With the gateway and ledger both deferred, there is no second source of
capability requests to check that taxonomy against before it ships. Naming a fixed set now risks
either being too coarse to be useful (a `source-mutation` capability covering both a one-line docs fix
and a schema rewrite) or too narrow to survive contact with the next real request.

The permissive-default shape does not weaken `R01`, because `R01` asks for a working refusal path
ordered ahead of anything unattended, not a complete rule set — REQ-017 states this explicitly: "R01
does not require a complete policy... a design that ships the permissive shape leaves R02 and R04
open until there are real requests to write them against." What `phase-auto-02` builds is:

- A tool-execution boundary that every agent action routes through, capable of denying a call before
  it reaches the tool (satisfies `R03`'s enforcement-at-the-boundary requirement structurally,
  independent of what the policy behind it says).
- A default policy of **deny nothing** — the boundary exists and is wired, but no capability is
  currently refused, because no real capability request has yet been observed to write a refusal
  against.
- An audit record of every call the boundary sees, whether allowed or (once policy exists) denied,
  so that the first real denial has a boundary already proven to work rather than one built at the
  same time as the policy it is meant to enforce.

### R02 and R04 are recorded as open, not claimed

Per `REQ-017`'s own qualification, choosing the permissive-default shape means `R02` ("every agent
run carries an explicit, narrow capability set — named actions, not a role") and `R04` ("anything
sensitive routes through an approval request carrying scope, reason, expiry and an immutable decision
record") are **not** satisfied by this design and are **not** ruled for building as part of
`phase-auto-02`. They remain open, to be answered once the gateway or ledger (or continued direct use
of the broker inside chat sessions) produces real capability requests to design a named set and an
approval path against. `R01` and `R03` are the rows `phase-auto-02` is scoped to satisfy; `R02` and
`R04` are carried forward, not claimed.

`REQ-017` itself is not edited by this document to mark `R02`/`R04` open — `REQ-017` is not a
declared deliverable of this phase (its deliverables are `docs/04-decisions/` and
`docs/07-architecture/` only), and this document records the open status here instead. Whether
`REQ-017`'s own row table should be updated to reflect this ruling is a decision for whoever owns
that file; this document states the fact so that decision can be made without re-deriving it.

## Nothing here becomes a second authority over phase claims

`REQ-017` `R16` requires that nothing in this programme duplicate the claim protocol that already
works. This design introduces no lock table, no claim mechanism and no coordination surface of its
own. `docs/09-backlog/backlog.yaml` remains the lock table for phase claims, and the governance
validator (`uv run python -m src.governance`) remains the lock check — the same protocol
[ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md) established. The capability broker
ruled above governs what an agent may *do* once it is running a task; it has no bearing on and makes
no claim over which agent is entitled to *run* a given phase, which stays exactly where `ADR-003` and
`backlog.yaml` put it. This is the same boundary `000020`'s MCP-mediated coordination proposal was
found to cross (it would have replaced both the lock table and the lock check), which is part of why
that idea is sequenced behind `000128` rather than built — a ruling this document carries rather than
re-opens, per `phase-auto-01`'s scope.

## Summary ruling

| Component | Ruling | Reason |
|---|---|---|
| `000031` broker | Build now, first | Only component with an unattended-safety argument for existing before the others; the 2026-09-15 run is real evidence it is load-bearing |
| `000028` gateway | Defer | Buildable and testable alone, but no current caller and no ledger to feed |
| `000029` ledger | Defer | Core design question (what a checkpoint must capture) unanswerable against zero real interrupted, trigger-driven runs; primary consumer (gateway) also deferred |
| `000030` worker | Defer | Its own stated dependency on both gateway and ledger is unmet; a scheduling daemon with nothing to schedule |

Broker shape: **enforcement point with a permissive default**, not full policy. `R01` and `R03` are
satisfied by `phase-auto-02`'s scope; `R02` and `R04` are recorded open, not claimed.
