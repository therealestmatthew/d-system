---
schema_version: 1
id: doc-backlog-status-regression-guard-plan
code: PLAN-038
title: Backlog status-regression guard — a monotonicity check in the governance validator
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-backlog, sys-governance]
depends_on: [doc-backlog-status-regression-guard, doc-adr-multi-agent-concurrency, doc-backlog-decisions]
---

# Backlog status-regression guard

Implements [REQ-010](../06-requirements/REQ-010-backlog-status-regression-guard.md): a check that
fails when a phase silently leaves `complete`, or keeps `complete` while losing the evidence for
it, unless the change is recorded as a decision in `GOV-003`.

## Context and scope

The governance validator today answers "is this backlog state internally consistent and are the
claims legal?" It does not answer "did this change destroy a record of finished work?" Those are
different questions, and only the first is currently asked. `5ecb203` passed the first and failed
the second, silently — the incident is described in `REQ-010` and in
[SESS-2026-09-14-01](../03-sessions/SESS-2026-09-14-01-literature-review-pass-3.md).

Scope is one new check in `src/governance/`, its tests, and an `OPS` note if the check grows its
own tool. It touches no existing validation rule and changes no schema.

## Approach

**A diff check, not a state check.** Every existing governance rule reads the current
`backlog.yaml` alone. This one is the first that needs a prior state, which is the only
genuinely new thing in the design. The prior state is `git show HEAD:docs/09-backlog/backlog.yaml`
— the committed version in the working tree's own branch.

`HEAD` is chosen over a `dev`-relative comparison deliberately. A `dev` comparison catches more —
including a regression arriving through a merge — but fires on every agent branch that
legitimately completes a phase, which is the normal case, and a check that cries wolf on correct
work is a check agents learn to ignore. `HEAD` catches the case that actually occurred: a bad
working-copy edit, before it is committed. `REQ-010` records this as an open question; the plan
proceeds on `HEAD` and the phase's acceptance can be re-parameterized if the owner rules
otherwise.

**Three comparisons, one per requirement.** For every phase id present in both states:

| | condition | requirement |
|---|---|---|
| 1 | `complete` → anything else | R1 |
| 2 | `complete` → `complete`, but `session`, `completion_evidence` or `result` lost | R2 |
| 3 | either of the above, with a `GOV-003` entry naming the phase in the same change | R3 — passes |

**The `GOV-003` escape is a grep, not a parse.** The check looks for the phase id as a literal
string in the working copy of `GOV-003-backlog-decisions.md` and not in its committed version —
i.e. the entry was added by this change. That is deliberately loose: the goal is to force the
author to write the reason down somewhere durable, not to validate the reason's shape. A stricter
parse would invite working around it.

**Failure output names the phases** (R4), because the incident cost hours partly because nothing
said which phases were affected.

## Risks and how they are handled

**A repository without git history, or a fresh clone mid-rebase.** `git show HEAD:...` can fail —
during a rebase, in a shallow clone, on the initial commit. The check treats an unreadable prior
state as *no comparison possible* and passes, printing a one-line note. A guard that hard-fails
when it cannot read history would block every rebase in the repository, which is a worse failure
than the one it prevents.

**False positives on a legitimate reopen.** Handled by R3. The reopen is permitted; it just has
to be written down. `GOV-003` already exists for this and is already where `AGENTS.md` sends a
collision resolution.

**It would not have caught `5ecb203` at merge time.** Stated plainly because it matters: this
guard fires at the moment the bad edit is made, in the tree that makes it. Once the regression is
committed on another branch and arrives by merge, the prior state on *this* branch already
contains it. Catching that case needs the `dev`-relative comparison the plan declined. If the
owner wants both, that is a second phase, not a widening of this one.

## Phases

One phase, `phase-gov-05`. It is small and self-contained: a check, its tests, and the failure
message. See `docs/09-backlog/backlog.yaml`.

## What this plan does not do

- It does not audit existing history for past regressions. The `phase-lit-03`/`04`/`05`/`06`
  reversal was repaired by hand in `b319b7a`; no other instance is known, and searching for more
  is a separate question from preventing the next one.
- It does not change `max_active`, claim validation, or any existing rule.
- It does not introduce a new command. `uv run python -m src.governance` gains a check; agents
  already run it before finishing (R5).
