---
schema_version: 1
id: doc-session-concurrency-git-safety-plan
code: SESS-2026-09-15-02
title: Finalize the concurrency, git safety and enforcement plan (P3)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-governance, sys-backlog, sys-delivery]
depends_on: [doc-concurrency-git-safety]
---

# Finalize the concurrency, git safety and enforcement plan (P3)

## Phase

`phase-prog-01` — Finalize the concurrency, git safety and enforcement plan (P3).

First phase of an unattended overnight batch of ten programme finalize phases, run by `agent-night`
under the owner's advance authority recorded in
[`docs/00-working/overnight-run-prompt-2026-09-15.md`](../00-working/overnight-run-prompt-2026-09-15.md).

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 228 documents, 25 memories, 190 backlog phases
```

Exit 0. Document count moved 227 → 228 for `REQ-013`; phase count 181 → 190 for the nine
`phase-conc-*` phases.

`uv run python -m src.governance --ready`

```
active: 2, complete: 73, deferred: 5, ready: 44, waiting: 66
Active claims: 2 of 3 allowed.

| phase-conc-01 | Define the stale-claim signal and report it in --ready | — | 1 | ready | — | phase-prog-01 |
| phase-conc-02 | Refuse integration over a dirty primary checkout | — | 1 | ready | — | phase-prog-01 |
| phase-conc-03 | Make document-code allocation collision-proof across concurrent sessions | — | 1 | ready | — | phase-prog-01 |
| phase-conc-05 | Decide and apply branch protection on main, with the settings record | — | 1 | ready | — | phase-prog-01 |
| phase-conc-07 | Decide the backup posture for non-git state and verify it by restoring | — | 2 | ready | — | phase-prog-01 |
| phase-conc-08 | Write the enforcement-placement rule, apply it, and audit .claude/ settings | — | 2 | ready | — | phase-prog-01 |
```

Six of the nine are `ready`; `phase-conc-04`, `-06` and `-09` are `waiting` on their declared
prerequisites, which is correct. The `Conflicts` column shows `phase-prog-01` against each because
this phase still holds `sys-governance` while the record is being written; it clears on merge.

`uv run pytest` — not in the phase's `verification` list, run because the post-rebase run decides
whether the branch may integrate.

```
580 passed, 2 warnings
```

`uv run python tools/check_no_private_content.py`, staged, in the worktree:

```
check_no_private_content: OK (631 tracked files, 0 identifiers checked)
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
```

Recorded as observed, not as a pass. This is the exact weakness `REQ-013` R08 asserts as a standing
check, reproduced while writing the requirement that names it. The full check ran in the primary
checkout against the merged result and reported `31 identifiers checked`.

## Acceptance

- **`PLAN-026` carries no placeholder banner and states a chosen design.** Met. The banner is gone
  and the document's `status` moved `draft` → `active`. Five numbered decisions under *The chosen
  design*, each stating the option taken, the option refused, and the cost accepted — not a summary
  of the open questions.
- **A requirement document exists for P3 and every row maps to at least one phase.** Met. `REQ-013`
  carries sixteen rows. The *Requirement coverage* table maps each to a phase, and the mapping is
  total in both directions: every row has a phase and every one of the nine phases carries at least
  one row.
- **The implementation phases are session-sized with acceptance and verification each.** Met. Nine
  phases, each with three acceptance conditions and at least one runnable verification command, all
  validating against `schemas/backlog.schema.json` — governance exits 0, which is what rejects a
  malformed item.
- **`phase-prog-01` is removed from `next_up` in the same change that completes it.** Met. Removed in
  commit `54252f8`, the same commit that registered the track. `next_up` now opens
  `phase-part-02, phase-port-02, phase-ses-01, phase-prog-04, …`.

## Backlog

`phase-prog-01` is `status: active`, `agent: agent-night`, pending the independent review below. All
four acceptance conditions read Met against the verification above, which is what makes the phase a
candidate for closure — not closure itself. `status: complete`, `session`, `completion_evidence` and
`result` are written only if the review confirms every condition, under the owner's advance authority
for this batch.

Nine phases added under `phase-conc-*`, all `status: queued`, none claimed.

## Decisions

**The stale-claim question was ruled toward reporting rather than automatic release**, and this is
the one ruling in the phase that a reasonable reader could take the other way. `000025` leaves it
open. The argument for a check that releases is that a dead claim otherwise blocks its systems until
a human looks; the argument against, which won, is that the evidence a check can gather is about the
branch and the worktree, never about the agent, and a false "abandoned" hands a second agent a phase
someone is actively writing — `000041` with extra steps. The cost is written into the decision rather
than hidden, and `R02` requires the definition to state what staleness does not prove.

**The clobber guard was placed at integration rather than on `git stash`.** The obvious reading of
`000041` is "forbid `git stash`". That fails twice: git has no stash hook, so the rule would be the
unenforceable prose this programme exists to replace, and stashing your own work in your own worktree
is ordinary and safe. The hookable moment is landing work on the trunk across someone else's
uncommitted changes.

**`phase-conc-03` was kept inside `G09` rather than split out.** The session-code collision reads as
incidental to the stash incident. It is the same failure: a shared resource allocated by inspecting
state that has not merged yet. `AGENTS.md` already documents a hand-reservation workaround, which is
a convention protecting against a mechanism defect.

**The partition's precedence note was not followed, deliberately.** It says `G09` should land after
`G10`'s document rewrite because both touch the same `AGENTS.md` passages. Splitting `G09` into
mechanism (`-01` to `-03`, no `AGENTS.md` prose) and procedure (`-04`) makes the precedence apply
only to the procedure, which depends on `phase-conc-01` instead. The plan states this rather than
leaving the departure to be noticed.

**`000012` was given a disposition instead of a phase.** Its blocker is gone — the remote and CI both
exist — but its value is a function of suite runtime, and the suite runs 580 tests in about a minute.
Building a provenance check to save sixty seconds is not work this programme can justify. Recorded in
`phase-conc-08`'s scope so the next reader does not re-derive it.

**`phase-conc-09` is declared owner-executed.** Two independent reasons, and either alone is
sufficient: `.claude/settings.json` hard-denies `Edit(AGENTS.md)`, and `AGENTS.md`'s own standing rule
forbids any agent editing it. The phase's acceptance is written so an agent can verify the result
without being able to produce it.

## Corrections

**`phase-prog-01`'s `deliverables` list omitted `docs/09-backlog/README.md`**, while its `scope`
required registering a new prefix there. `phase-prog-03` declares the file; `phase-prog-01` and
`phase-prog-02` did not. Rather than write outside the declared lock, the declaration was widened on
`dev` first, in commit `3e3ee97`, and the branch rebased onto it. The same omission is present on the
nine remaining `phase-prog-*` phases and will be fixed in each claim commit rather than after the
fact.

## Unresolved

Recorded rather than asked, per the run's standing instruction. Each names the options weighed and
the assumption the work proceeded on.

**Whether `phase-prog-01` should have been claimed at all, given the queue.** `next_up` opens with
`phase-part-02`, and `AGENTS.md` says to take the first ready phase in the rendered order. The run
prompt names `phase-prog-01` first. Options: follow the queue and start with `phase-part-02`, or
follow the prompt. **Proceeded on the prompt**, because it is the owner's direct and recent
instruction naming ten specific phases in a stated order, which is a stronger signal than the queue's
default. `phase-part-02` is untouched and still at the front.

**Whether the backup posture is the owner's to choose before the phase is sized.** `phase-conc-07`
offers three options — encrypted off-machine copy, second local disk, recorded acceptance of the risk
— and `R11` treats all three as satisfying. Options: rule now on the owner's behalf, or size the
phase to put the question to them. **Proceeded by sizing the phase to ask**, because the choice turns
on how much the owner values `_private/portfolio/` against the cost of maintaining a backup, which is
not a fact in the repository. The phase's `next_action` says so explicitly.

**Whether `G10`'s pull-request gate should also cover `agent/*` → `dev`.** Ruled no, in design
decision 3, on the argument that it would hold claims open across sessions. The counter-argument not
taken: it would give every change a review surface, which is the actual point of a gate. **Proceeded
on the narrower gate**, because the claim model in `ADR-003` assumes synchronous merges and breaking
that assumption costs more than the review gains while the repository is single-owner. If the
repository gains collaborators, this ruling is the first one to revisit.

**Whether writing `docs/00-working/overnight-*` files is inside this phase's lock.** They are not in
any `phase-prog-*` phase's `deliverables`. Options: widen the declaration, or treat the run prompt's
instruction as the authority. **Proceeded on the instruction** and did not widen the lock, because
`docs/00-working/` is ungoverned staging by `ADR-010` and the files are the run's own reporting
surface rather than this phase's deliverable.

## Left undone

**Every one of the nine phases.** This phase finalizes a plan and builds nothing, by design. The
programme's own work — the stale-claim signal, the integration guard, the allocator fix, the branch
protection, the backup posture, the placement rule — is entirely ahead.

**`phase-conc-05`'s remote half cannot be verified by an agent under this run's authority.** `R06`
requires observing that `main` rejects a direct push and that a failing check blocks a merge. Both
are observations against `origin`, and this run has no push authority. The phase is sized on the
assumption that whoever claims it does have it; if that is not true, the phase splits into a local
half (fixing the private-content check's silent pass) and an owner-executed remote half.

**The `0 identifiers checked` weakness was recorded, not fixed.** It belongs to `phase-conc-05`,
which declares `tools/check_no_private_content.py`. Fixing it here would have been work outside this
phase's scope on a file it does not declare.
