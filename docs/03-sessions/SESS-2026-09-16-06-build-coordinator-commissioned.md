---
schema_version: 1
id: doc-session-build-coordinator-commissioned
code: SESS-2026-09-16-06
title: Build coordinator commissioned and the queue partitioned into six batches
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-backlog, sys-governance]
depends_on: [doc-build-coordinator, doc-coordinator-protocol, doc-backlog-decisions, doc-prompt-pack-protocol, doc-session-phase-review-remaining-decisions]
---

# Build coordinator commissioned and the queue partitioned into six batches

Unclaimed, owner-directed work following `SESS-2026-09-16-04` and `-05`, which reviewed and
enhanced the twenty-nine queued phases. This session commissioned the coordinator that will build
them: [PROMPT-036](../02-prompts/PROMPT-036-build-coordinator.md), plus the governance decision it
depends on.

## The partition

Twenty-nine phases in six dependency-closed batches of five (the last, four). Each batch's internal
order is a valid build order, and nothing in a batch depends on anything in a later one — verified
programmatically against `backlog.yaml`, not asserted.

`phase-lit-09` is excluded by the owner's instruction: it belongs to the literature-review campaign,
has its own coordinator and resume command, and conflicts with `phase-lit-07` while that is active.
It stays in `next_up`; the coordinator simply never claims it.

## What the constraints forced

The partition was designed twice. The first attempt used contiguous queue prefixes of five to seven
phases. Research into the governing documents then established three facts that broke it:

- `/session-close` was owner-only and the only path to `status: complete`.
- `max_active` is 3 (`src/governance/backlog.py:55-64`).
- A coordinator that cannot complete phases therefore **accumulates claims** and stalls at three.

Under those rules a batch could only ever be three mutually non-conflicting, dependency-independent
phases — and `collisions()` showed how scarce those are: of the twelve then-claimable phases, most
pairs collide on a shared system or a shared deliverable path. The owner's pre-approval of
completion removed the cap, which is what let the partition return to following the queue.

## The governance decision

`GOV-003` gained *Coordinator completion replaces owner-invoked /session-close*, which **supersedes
the session-close clause** of the 2026-09-16 master-plan ruling — "no standing owner-only rule is
delegated: `/session-close` remains owner-invoked per phase, batched but never automated". That
clause was recorded for this very pipeline, and the owner was shown it before ruling against it.
The same ruling's other half stands untouched: `next_up` ranking remains the owner's.

The replacement follows the demo track's proven pattern rather than plain pre-approval: a
coordinator may complete a phase only after green verification with output captured, an independent
adversarial review resolved, and owner-approved integration. Unlike the demo and workbench
exceptions, each confined to a phase prefix, this one is **repository-wide and standing** at the
owner's direction.

A second entry followed the same shape: the per-phase claim gate in `/session-start` step 2 is
covered by the owner's approval of the batch, with questions batched before the first claim instead
of raised phase by phase, and **a blocker given to an agent to resolve before it halts the run**.

The entry names the two documents that now contradict it — `.claude/commands/session-close.md`'s
owner-only section and the checkpoint skill's never-complete rule. **Neither was edited.** Their
wording is a decision for the owner, and `PROMPT-036` tells the coordinator they are knowingly
superseded so it does not stall on reading them.

## The adversarial review

`PROMPT-036` was reviewed before being committed: 2 blockers, 2 majors, 1 minor, all integrated.

- **Blocker.** The draft put a whole batch on one shared branch and worktree, contradicting
  `AGENTS.md:249` and `session-start.md:103-104` — both say the branch is *always* `agent/<phase-id>`
  and the worktree *always* `../d-system-worktrees/<phase-id>` — and colliding with the hand-off
  step that bundles `git worktree remove` and `git branch -d` into the merge. A coordinator
  following the protocol literally would have deleted the worktree after the first phase and left
  the second with nowhere to build. The owner independently raised the same question. Fixed by
  going per-phase, which dissolves the conflict entirely: the bundled cleanup then works as written.
- **Blocker.** The draft claimed each phase on a numeric check while `/session-start` step 2
  mandates an `AskUserQuestion` gate that stops until answered — silently overriding a documented
  stop-gate. Fixed by the owner's ruling and the `GOV-003` entry above, and stated in the prompt as
  a deviation rather than left implicit.
- **Major.** The prompt never mentioned the two documents `GOV-003` had flagged as contradicting
  it, so an agent reading them mid-run could have stalled. Now named explicitly.
- **Major.** Unlike both precedent coordinators, it never required reading `AGENTS.md` or `GOV-006`
  — while depending on the former's hand-off procedure. Now the first preflight step.
- **Minor.** Preflight lacked `git status --short` and `git branch --show-current`. Added.

The reviewer verified the batch table programmatically and found it sound: all twenty-nine
non-`phase-lit-09` entries appear exactly once, in `next_up` order, every phase `status: queued`,
every dependency resolving to an earlier or same-position phase.

## Four stated deviations

`PROMPT-036` records each rather than leaving it to be discovered: the coordinator claims (against
`GOV-008`'s "claims nothing", written for packs with sub-orchestrators this run does not have); the
dispatch templates are the prompts and are instantiated against each phase's own reviewed backlog
entry rather than composed freehand (against "authors no prompts"); the claim gate; and the two
superseded completion documents.

## Verification

- `Governance OK: 31 systems, 263 documents, 25 memories, 278 backlog phases`
- `580 passed, 2 warnings`
- `check_no_private_content: OK (670 tracked files, 0 identifiers checked)`, staged

## The coordinator protocol

The design knowledge behind `PROMPT-036` was extracted into
[GOV-013](../08-governance/GOV-013-coordinator-protocol.md) at the owner's request, so a future
coordinator-planning session inherits it rather than rediscovering it. It carries the constraint
questions that must be answered before any partition is drawn, the completion trap, the four ways a
shared batch worktree fails, questions-at-the-open, resolver-before-escalation, the
name-every-deviation rule, the check-the-decision-record rule, context and cost discipline, and a
nine-step checklist.

It was fact-checked before commit: 0 blockers, 4 majors, 5 minors — no false claims, every
quotation and all four cited incidents substantiated against the record. The majors were worth the
pass:

- **It violated its own rule.** `GOV-013` makes adversarial review of a coordinator prompt
  mandatory, while `GOV-008`'s stage-7 gate and `GOV-009`'s equivalent make it "optional and run
  only if the owner specifically requests it" — and `GOV-013` had not named that as a deviation,
  two sections after requiring every deviation be named. Now named, with the reasoning: the optional
  clause rests on an earlier pack audit having covered the substance, which does not reach a
  coordinator prompt written outside that methodology. Where one *is* produced by `GOV-008`'s full
  pipeline, its clause governs and `GOV-013` yields.
- **It required of `PROMPT-036` two things `PROMPT-036` did not do** — state that the partition was
  verified programmatically, and name which parameter the first run tests. Both claims lived only in
  this session record. Added to the pack, which is where a reader looks.
- **Cost and context discipline were in the pack but never extracted**, so a planning session
  reading only `GOV-013` would have missed the model-assignment rules, the fix-cycle cap, the
  descope ladder and selective injection. Both sections added.

The minors were a title breaking the siblings' convention, a gloss that undersized `GOV-008`, "days
earlier" where the record says one day, an unexplained deviation count, and the omitted
fixed-port-per-worktree rule. All corrected.

## Review

Independent pre-merge review by a fresh non-fork sub-agent, given the commit range and told to
verify the documents' claims for itself rather than accept them. **0 blockers, 1 major, 2 minors;
four of six areas clean.** Its findings, as returned:

> **major — PROMPT-036's preflight miscounts a document it tells the coordinator to read.**
> `PROMPT-036:63` says "Read `AGENTS.md`'s three *Concurrent agents* sections and `GOV-006`."
> `AGENTS.md` actually has four: `:182` (claim a phase), `:218` (work in a worktree), `:269`
> (complete and hand off), `:309` (resolve collisions). The omitted fourth section covers exactly
> what a coordinator running many concurrent claims/merges needs — `backlog.yaml` conflict
> resolution, duplicate-code collisions, source conflicts, post-rebase failures — and nothing else
> in `PROMPT-036` or `GOV-013` restates it.
>
> **minor — GOV-003's new entry cites the wrong section title for what it supersedes.** It says it
> supersedes the ruling "recorded above under 'the master plan and its sub-programmes'." No such
> heading exists; the actual heading is `## The idea realization system re-frames four programmes
> as sub-programmes` (`GOV-003:392`). Substance is right, label is wrong.
>
> **minor — the "verified programmatically" claim's method is unconfirmable from the repo, though
> its result is true.** No script or saved output exists in the diff. I independently wrote and ran
> the check: **the partition is in fact correct** — all 29 non-`phase-lit-09` entries appear exactly
> once in `next_up`'s own order, every phase is `status: queued`, every batch is dependency-closed,
> within-batch order is valid, and both external deps are genuinely `complete`. The claim's content
> holds; the methodological assertion is unsourced, not wrong.
>
> **Clean — GOV-003 supersession scope.** Displaces only the session-close half; the
> `next_up`-ranking half is left untouched and matches word-for-word.
>
> **Clean — PROMPT-036 / GOV-013 agreement.** Every rule in `GOV-013` cross-checked against
> `PROMPT-036`. No contradiction found; the four named deviations match.
>
> **Clean — session record's numbers.** Re-ran fresh: governance, pytest and the private-content
> check all match the cited figures exactly. All cited incidents check out verbatim.
>
> **Clean — diff scope.** The branch contains exactly two commits touching exactly the five
> described files. Nothing out of scope.
>
> **Verdict: safe to merge to `dev` as it stands.**

**All three findings were fixed before the merge**, not deferred: the preflight now names all four
sections and says why the fourth matters; the `GOV-003` citation now quotes the real heading; and
the partition claim now states it was script-checked when written *and* independently re-checked by
a reviewer who wrote their own script — which is sourced, because the review above is the source.

The review also surfaced, in passing, that `dev` had moved: another session committed `7830868`
while this one worked, diverging the branch. That is why the integration below rebases first.

## Decisions

**Completion authority moved, and the owner was shown the contrary ruling first.** The owner
pre-approved coordinator-invoked completion. `GOV-003` already held the opposite for this exact
pipeline, recorded the day before. Rather than act on the newer instruction, the earlier ruling was
put in front of them, along with the two prior exceptions that had granted something similar under
conditions. They chose the demo track's pattern — an adversarial gate substituting for synchronous
judgement — and chose to make it repository-wide rather than scoped to a prefix, which is broader
than either precedent.

**Per-phase worktrees, against the first draft.** The draft put a whole batch on one branch and
worktree. The owner questioned it and an adversarial review independently rated it a blocker, for a
reason neither had stated: `AGENTS.md` bundles worktree removal into the merge action, so the
shared worktree would have been deleted after the first phase. Going per-phase restored the
documented convention and dissolved the conflict.

**Questions batched at the open, blockers to an agent first.** The owner's ruling on the claim gate
produced a shape neither the command nor the first draft had: a reconnaissance pass over every unit
before any claim, one batch of questions, then autonomous running — with a resolver agent standing
between an obstacle and the owner's attention.

**`GOV-013` was written because the owner asked for the reasoning to be durable**, not just the
prompt. It is deliberately organised as design rules with incidents as evidence, so a future
planning session inherits the constraints rather than rediscovering them.

## Corrections

Four, all mine, all caught by checking rather than by being told:

- **The remaining-decisions count.** Reported as "15 of 46"; the verified figure was 23. The first
  number was an estimate never checked.
- **`phase-idg-08`'s tracking reference.** Reported as sitting behind idea `000253`. It was not:
  `000253` covers `phase-auto-03`/`-04`, and no idea mentioned `phase-idg-08` at all. The phase had
  neither a fix nor a record until ruling R48 closed it.
- **An impossible option offered as a recommendation.** `phase-irs-12`'s sizing was put to the owner
  with "raise `session_budget` to 2" recommended. `backlog.schema.json` enforces `const: 1` across
  all phases. The applying agent tried it, governance rejected it, and it reverted rather than
  editing the schema — which is the only reason a bad instruction did not become a repository-wide
  change. R52 replaced it with the split that R5 had already established as correct.
- **R18 reported as a clean fix.** It had left `phase-idg-10` and `phase-idg-11` colliding with each
  other on the new `sys-gov-docs` id. Applying R49 then found the front is narrower still than
  either diagnosis: only `phase-idg-01`, `-06` and `-10` are mutually disjoint.

One process deviation worth naming rather than hiding: **this session ran unclaimed throughout**,
across three session records and four commits to `dev`. The `PROMPT-035` run was unclaimed by
design, and the work that followed simply continued in the same conversation. Peers held no lock
against any of it. `brain/procedures/session-close-with-no-active-phase.md` describes the adjacent
pattern — a phase closes and work continues — and its standing view applies here: the fix is
claiming earlier, not manufacturing a checkpoint afterwards.

## Left undone

- **`.claude/commands/session-close.md` and `.claude/skills/checkpoint/SKILL.md` still tell an agent
  it may never complete a phase.** `GOV-003` now says otherwise, repository-wide. Both were left
  untouched deliberately — their wording is the owner's decision, and `CLAUDE.md`'s discipline about
  proposing rather than editing governing text applies. `PROMPT-036` tells the coordinator they are
  knowingly superseded so it does not stall. **This is the highest-value loose end**: an agent
  reading either file mid-run has a real contradiction in front of it.
- **Batch 1 has not been run.** Five per batch is an estimate; the unit run has never been executed
  against the real commands. `PROMPT-036` now says so and names both as what the first run measures.
- **`phase-lit-09`** stays in `next_up`, excluded from every batch, awaiting the owner's return to
  the literature-review campaign.

## Unresolved

- `.claude/commands/session-close.md` and `.claude/skills/checkpoint/SKILL.md` still tell an agent
  it may never complete a phase. `GOV-003` now says otherwise, repository-wide. The owner has been
  offered the choice and has not yet ruled on their wording.
- Batch 1 has not been run. The five-per-batch size is an estimate of what one coordinator can
  carry; the first run is the evidence that confirms or corrects it.
