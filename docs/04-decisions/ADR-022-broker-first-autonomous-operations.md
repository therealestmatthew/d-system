---
schema_version: 1
id: doc-broker-first-autonomous-operations
code: ADR-022
title: Build the capability broker before the gateway, ledger or worker
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-22'
updated: '2026-09-22'
systems: [sys-api, sys-delivery, sys-governance]
depends_on: [doc-autonomous-agent-operations-requirements, doc-autonomous-agent-operations, doc-adr-multi-agent-concurrency]
---

# Build the capability broker before the gateway, ledger or worker

## Context

`REQ-017` (`doc-autonomous-agent-operations-requirements`) and `PLAN-032`
(`doc-autonomous-agent-operations`) cover four ideas describing infrastructure for running agent
work with no chat session open: an external trigger gateway (`000028`), a durable run ledger
(`000029`), a supervised worker (`000030`), and a capability and approval broker (`000031`). The
partition that grouped these four ideas sequenced them `000028` → `000029` → `000030`, with `000031`
described only as "required before anything runs unsupervised" — a precondition attached at the end,
not a build order.

This phase (`phase-auto-01`) is the design pass PLAN-032 reserves for evaluating the four components
independently rather than building the partition's sequence unexamined. Two questions had to be
answered before any of the three build phases (`phase-auto-02` through `phase-auto-04`) could be
scoped: which order to build in, and whether to defer any component.

### The evidence available

Four of the five ideas in this group came from a research pass, not an incident, and the plan says
so rather than implying an evidence base it lacks. There is exactly one real data point: the
unattended run of 2026-09-15, which executed a batch of programme-finalize phases with no chat
session driving each step, using none of this infrastructure — no gateway, no ledger, no worker, no
broker. What made that run safe to leave unattended was a person granting a bounded, written
capability set in advance (merge locally but never push; write these phases complete and no others;
never touch `ts/` or `src/`; never write to the idea log) and an agent choosing to comply with it,
recording every departure for review.

That is a data point about which of the four pieces is load-bearing, and it points at the broker, not
at the gateway, ledger or worker. A trigger gateway has nothing to normalize until something outside
a chat session wants to start a run. A run ledger has nothing to persist until a run exists to
persist. A worker has nothing to drain — `000030`'s own body calls it "a scheduling daemon with
nothing to schedule" without the other two. None of the three has an unattended-safety argument for
existing first. The broker does: it is the only one of the four whose absence is dangerous rather
than merely incomplete, because its job is to refuse, and there is nothing to refuse until an agent
tries to act.

## Decision

**The capability and approval broker (`000031`) is built first, ahead of the trigger gateway
(`000028`), the run ledger (`000029`) and the supervised worker (`000030`), inverting the partition's
stated ordering.**

This is a decision with a reason, not a restatement of the partition's own gate note. Read as a
precedence note — "the broker is required before anything runs unsupervised" — the ordering is
satisfiable by building the gateway, ledger and worker first and adding the broker afterward, before
switching anything on. That reading fails in the specific way a safety gate usually fails: a gate
built after the things it gates has never gated anything. The window between "the worker can drain
queued runs" and "the broker denies capabilities" is exactly the period in which an unattended run
happens with nothing authorizing it. `REQ-017` `R01` is written to make the ordering itself the
observable requirement, not a property of the finished system — "the broker gates before anything
runs unattended", verified by attempting an unattended run before the broker exists and confirming
it is refused. That requirement is only satisfiable by an ordering where the broker exists first;
`phase-auto-01` rules the ordering itself rather than leaving it implicit in prose.

The cost of this ordering is accepted deliberately: the broker will be the least immediately useful
of the four components, because with no gateway, ledger or worker generating capability requests,
there is nothing yet for it to authorize. It will look like over-engineering for as long as the rest
of the programme is unbuilt. That is the correct shape for a component whose entire purpose is to
deny by default before anything exists to trust.

### The broker ships as an enforcement point with a permissive default

Building the broker first does not mean designing its full capability taxonomy first. `REQ-017`
allows either shape to satisfy `R01` — a full-policy broker (capability set, approval path and
decision record specified now) or an enforcement point with a permissive default (the tool-boundary
mechanism and refusal path built and wired, policy deferred). **This design finds it is guessing at
the capability taxonomy, and ships the permissive-default shape.** The only real precedent for scoped
capability enforcement in this repository — the 2026-09-15 unattended run described above — was a
person writing situational grants for that one run ("merge locally but never push", "write these ten
phases complete and no others", "never touch `ts/` or `src/`"), not a set drawn from a pre-declared,
general-purpose taxonomy. With the gateway and ledger both deferred (see
[ARCH-011](../07-architecture/ARCH-011-autonomous-operations-architecture.md)), there is no second
source of real capability requests to check a named taxonomy against before it ships.

`phase-auto-02` therefore builds the tool-boundary enforcement mechanism, wires it into every agent
action, defaults to denying nothing, and audits every call it sees. This satisfies `REQ-017` `R01`
(the ordering) and `R03` (enforcement at the tool boundary). It does **not** satisfy `R02` (every
agent run carries an explicit, narrow, named capability set) or `R04` (anything sensitive routes
through an approval request carrying scope, reason, expiry and an immutable decision record) — per
`REQ-017`'s own qualification that a design shipping the permissive shape leaves those two open until
real capability requests exist to write them against. **`R02` and `R04` are recorded here as open,
not claimed.** They are answered once the gateway, the ledger, or continued direct use of the broker
inside chat sessions produces real requests to design a named taxonomy and an approval path against.
`REQ-017` itself is not edited to reflect this — it is not a declared deliverable of this phase — so
this decision states the fact in place of that edit.
[ARCH-011](../07-architecture/ARCH-011-autonomous-operations-architecture.md) carries the fuller
reasoning for this ruling and the per-component build/defer ruling on the gateway, ledger and worker;
it does not contradict this decision.

### Nothing here becomes a second authority over phase claims

`REQ-017` `R16` requires that nothing in this programme duplicate the claim protocol that already
works. This decision introduces no lock table, no claim mechanism and no coordination surface of its
own. `docs/09-backlog/backlog.yaml` remains the lock table for phase claims, and the governance
validator (`uv run python -m src.governance`) remains the lock check — the protocol
[ADR-003](ADR-003-multi-agent-concurrency.md) established. The broker built under this decision
governs what an agent may *do* once it is running a task; it has no bearing on, and makes no claim
over, which agent is entitled to *run* a given phase, which stays exactly where `ADR-003` and
`backlog.yaml` put it.

## Consequences

- `phase-auto-02` (build the broker) has no dependency on `phase-auto-03` or `phase-auto-04` and can
  proceed once `phase-auto-01` closes. `phase-auto-03` (gateway) and `phase-auto-04` (ledger) both
  depend on `phase-auto-02`, not on each other — they are siblings, not a chain, because the gateway
  normalizes events and the ledger persists runs and neither needs the other to be testable.
- `phase-auto-05` (worker) depends on both `phase-auto-03` and `phase-auto-04`, matching `000030`'s
  own statement that it has no purpose until both exist.
- No unattended run is safe to authorize until `phase-auto-02` ships, regardless of what order the
  other three land in afterward. Any future phase that proposes running agent work unattended before
  the broker exists contradicts this decision and needs a new one to override it, not a scope note.
- The build/defer ruling on the gateway, ledger and worker themselves — as opposed to the ordering
  decided here — is recorded in
  [ARCH-011](../07-architecture/ARCH-011-autonomous-operations-architecture.md).
