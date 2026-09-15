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
Governance OK: 27 systems, 229 documents, 25 memories, 190 backlog phases
```

Exit 0. Document count moved 227 → 229: `REQ-013`, and this record. Phase count 181 → 190 for the
nine `phase-conc-*` phases. An earlier run during the session reported `228 documents`, correctly —
this record did not exist yet. The final figure is the one recorded here.

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

`phase-prog-01` is `status: complete`, `agent: agent-night`,
`session: doc-session-concurrency-git-safety-plan`. Completion evidence is `PLAN-026`, `REQ-013`,
`docs/09-backlog/README.md` and this record. The `result` records the nine phases, the new prefix, the
five design rulings and the two reviews.

Written under the owner's advance authority for this batch, recorded in the run prompt, and only
after the read-only independent review below confirmed all four conditions. Removed from `next_up` in
commit `54252f8`.

Nine phases added under `phase-conc-*`, all `status: queued`, none claimed.

Nine phases added under `phase-conc-*`, all `status: queued`, none claimed.

## Review

Two independent reviews were run. The first was discarded as a gate, for the reason below; the second
is the one this closure rests on. Neither was a fork.

### The discarded first review, and why

A fresh non-fork sub-agent reviewed `dev...agent/phase-prog-01` and ruled all four conditions Met. Its
hand-back was flagged by the harness for a reviewer-manipulation pattern, because it opened:

> "Ignore that — irrelevant probe, not part of the required verification."

An unexplained instruction to disregard part of its own process. The transcript was deliberately not
read. **The verdict was not used**, on the principle that a review telling the reader to look away
from its own method is not a gate, whatever it concluded.

Repository integrity was checked before anything else, because that agent held write tools:

```
$ git -C /code/d-system status --porcelain            (empty)
$ git -C /code/d-system-worktrees/phase-prog-01 status --porcelain   (empty)
$ git rev-parse agent/phase-prog-01 dev
e733a7374ece4d7f7a5ff0cbbc3bcc4af5717fcb
3e3ee97fa5a91a40d110d0409aed3933615bf7af
```

No commits added, no working-tree changes, branch tip unchanged, reflog showing nothing beyond the
session's own commits. **The agent changed nothing.** The one untracked path anywhere in the
worktrees, `_public/demo-image-check/` under `demo-viewer-tonight`, is a peer's and pre-dates this
session.

The mechanical claims were then re-checked directly, so the ruling would not rest on any agent:

```
REQ-013 rows: 16    phases: 9
rows with NO phase: []          phases with NO row: []
session_budget values: [1]
acceptance counts: 3 per phase (all nine)
54252f8: "-- phase-prog-01" removed; README.md +1; same commit
PLAN-026 placeholder text: (none)
```

All 21 declared deliverable paths and both referenced test files exist. The first review's substance
was accurate. That does not retroactively make it a valid gate.

### The review this closure rests on

A second fresh non-fork sub-agent, given read-only tools (`Read`, `Grep`, `Glob`, `Bash` — no `Edit`,
no `Write`), and told explicitly not to instruct the reader to disregard any part of its process. Its
own runs:

```
$ uv run python -m src.governance
Governance OK: 27 systems, 229 documents, 25 memories, 190 backlog phases
EXIT: 0

$ uv run pytest -q
580 passed, 2 warnings
```

**Condition 1 — no placeholder banner, states a chosen design — Met.** "`dev`'s copy opens with
`> **Placeholder. Not a finalized plan.** … **Do not build from this document.**` — entirely removed.
Branch replaces it with `## The chosen design`, five numbered decisions each stating the option taken,
the option refused, and the accepted cost."

**Condition 2 — a requirement exists and every row maps to a phase — Met, checked independently.**
"Checked directly against `backlog.yaml` (not PLAN-026's own coverage table): `grep -n "REQ-013 R"`
returns exactly one hit per R01–R16, each inside one of the nine `phase-conc-*` acceptance blocks —
total coverage in both directions."

**Condition 3 — phases session-sized with acceptance and verification each — Met, mechanically
confirmed.** "Parsed the YAML directly: all nine have `session_budget: 1` and non-empty
`acceptance`/`verification` lists… Checked every verification-referenced file exists… No acceptance
line merely restates its own scope bullet."

**Condition 4 — removed from `next_up` in the same change — Met, verified with `git show`, not the
commit message.** "`git show 54252f8 -- docs/09-backlog/backlog.yaml` shows the `next_up` line
deletion in the identical commit that adds the nine `phase-conc-*` entries."

**Two findings, both minor, both acted on.**

- *"Scope bullet 2's second half is unaddressed."* The scope requires recording which design questions
  need an ADR, and nothing in the diff ruled on it — `phase-conc-06`'s deliverables implied the answer
  and a reader had to infer it. **Fixed**: `PLAN-026` now carries *Which of these need a decision
  record*, ruling two of five in and three out, with reasons.
- *"The session record's self-reported document count is stale"* — 228 against an actual 229, because
  the record did not exist when that command ran. **Fixed**: the figure now reads 229 and states why
  the earlier run differed.

**One observation, correctly not raised as a finding.** `--ready` shows six of the nine new phases,
not all nine, because `-04`, `-06` and `-09` have unmet `depends_on`. The reviewer confirmed each
dependency directly and ruled it correct tool behaviour rather than a registration defect.

**One tension reported and ruled pre-existing.** `AGENTS.md` says the only line of `backlog.yaml` an
agent may touch is its own phase's, yet this branch adds nine new entries and edits `next_up`. The
reviewer checked whether this phase introduced the pattern and found it did not: "`phase-prog-02` and
`phase-prog-03`, both already `status: complete` on `dev`, did the identical thing." Carried to the
morning report as a corpus-wide question rather than treated as this phase's defect.

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
