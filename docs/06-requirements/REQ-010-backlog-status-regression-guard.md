---
schema_version: 1
id: doc-backlog-status-regression-guard
code: REQ-010
title: Backlog status-regression guard requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-backlog, sys-governance]
depends_on: [doc-adr-multi-agent-concurrency, doc-backlog-decisions]
---

# Backlog status-regression guard requirements

## Observed problem and scope

On 2026-09-14, commit `5ecb203` on `dev` rewrote `docs/09-backlog/backlog.yaml` from a stale
copy. Its intended change was correct and is not in question — `scope`, `acceptance` and
`verification` on `phase-kit-01`, `phase-kit-02` and `phase-kit-04`. The same write also reverted
four unrelated phases to a state three phases old:

```text
phase-lit-03  complete -> active,  session/completion_evidence/result deleted
phase-lit-04  complete -> queued,  same, agent cleared
phase-lit-05  complete -> queued,  same, agent cleared
phase-lit-06  active   -> queued,  agent cleared (a live claim)
```

**`uv run python -m src.governance` exits 0 on both sides of that change.** The validator checks
claim conflicts, locked systems, `max_active` and dependency chains. A phase that has reached
`complete` silently becoming `queued` breaks none of them, and neither does the deletion of its
`session`, `completion_evidence` and `result`. Three phases' completion records and one live
claim left the lock table with no check failing anywhere.

It was found only because the agent holding the erased claim rebased onto `dev` at its phase
boundary and noticed its own claim missing. That is luck, not a control. A session that did not
rebase, or rebased without looking, would have inherited the regression and integrated it — and
the next agent to run `--ready` would have seen three finished phases offered as available work.

This requirement covers the guard. It does **not** cover the human or agent behaviour that
produced the stale write; `AGENTS.md` already forbids resolving a `backlog.yaml` collision by
taking one side wholesale, and that rule was not the failure — nothing in the commit suggests a
conflict was resolved at all.

## Requirements

Each is an observable statement with a verification method.

### R1 — A phase that has been `complete` may not silently leave that state

**Statement.** The governance check fails when a phase's `status` moves from `complete` to any
other value between the committed `backlog.yaml` and the working copy, unless the change is
accompanied by an explicit recorded decision (below).

**Why not simply forbid it.** Reversals are legitimate and have happened: a phase can be found
incomplete after close, and `GOV-003` exists to record exactly that class of choice. The defect
is not that a phase moved backwards — it is that it moved backwards **silently**, inside a diff
about something else.

**Verification.** A test that constructs a prior and current `backlog.yaml` differing only in one
phase's `complete -> queued` transition and asserts the check exits non-zero, naming the phase.

### R2 — Completion evidence may not be dropped from a phase that keeps `status: complete`

**Statement.** The check fails when a phase is `complete` in both the prior and current state but
has lost `session`, `completion_evidence` or `result`.

**Why separately from R1.** The `5ecb203` regression did both, but they are independent failures.
A phase that keeps `complete` while losing the evidence for it is worse than one that reverts
honestly, because nothing about its rendered state looks wrong.

**Verification.** A test asserting non-zero exit when `completion_evidence` is removed from a
phase left at `complete`.

### R3 — A regression is permitted when it is recorded as a decision

**Statement.** The check passes a `complete -> queued`/`active` transition when the same change
adds an entry to `docs/08-governance/GOV-003-backlog-decisions.md` naming that phase id.

**Why.** `GOV-003` is already the standing record for "choices that resolve older plan conflicts"
and for decisions taken when resolving a collision. Reopening a completed phase is exactly such a
decision. This requirement routes the reversal through the record that already exists rather than
inventing a second mechanism, and it makes the guard a prompt to document rather than a
prohibition to work around.

**Verification.** A test asserting exit 0 when the same transition is accompanied by a
`GOV-003` entry naming the phase, and non-zero when the entry names a different phase.

### R4 — The check reports what regressed, not that something did

**Statement.** On failure the check names each affected phase id, the transition
(`from -> to`), and which of `session`, `completion_evidence`, `result` were lost.

**Why.** The regression was invisible for hours partly because no artifact said which phases were
affected; it took a YAML diff across two commits to establish the list. A guard that fails without
naming the phases would reproduce that cost on every trip.

**Verification.** A test asserting the failure output contains each affected phase id and its
transition.

### R5 — The check runs where `backlog.yaml` is written, not only in CI

**Statement.** The guard runs as part of `uv run python -m src.governance`, the command
`AGENTS.md` already requires before finishing any documentation change.

**Why.** `5ecb203` was made by a session that would have run the governance check before
committing. Placing the guard anywhere else — a CI-only job, a separate tool — means the agent
that causes the regression is not the one told about it.

**Verification.** `uv run python -m src.governance` against a working tree containing a seeded
regression exits non-zero.

## What this deliberately does not require

- **Not a general schema-diff check.** Comparing every field of every phase across commits would
  fail constantly on legitimate edits. The scope is the three fields that record a phase is
  finished, plus `status` itself.
- **Not a lock on `backlog.yaml`.** Concurrent edits to the file are normal and `AGENTS.md`
  already prescribes how to resolve them. This guard does not serialize access.
- **Not retroactive.** It compares the committed state against the working copy. It does not
  audit history, and it would not have caught `5ecb203` after the fact — it would have caught it
  at the moment it was made, which is the point.

## Open question for the owner

**What is the prior state compared against, in a worktree that has not fetched?** The natural
answer is `HEAD`, which catches a bad working-copy edit. It does not catch a regression that
arrives through a rebase or merge from another branch, because by then it is already committed on
the other side. A `dev`-relative comparison would catch more and would also fire on every agent
branch that legitimately completes a phase. `HEAD` is the narrower, quieter choice and is what
the plan assumes unless the owner says otherwise.
