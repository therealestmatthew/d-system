---
schema_version: 1
id: doc-session-literature-review-research-pack
code: SESS-2026-09-12-04
title: Manufacture the literature-review research pack — GOV-009's first end-to-end execution
kind: session
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems:
- sys-research
- sys-governance
- sys-backlog
depends_on:
- doc-research-protocol
- doc-lit-campaign
---

# Manufacture the literature-review research pack — GOV-009's first end-to-end execution

## Phase

**No phase was claimed, and none reached `status: complete` in this session.** That is correct
rather than a gap: pack manufacturing under the research pack protocol
([GOV-009](../08-governance/GOV-009-research-protocol.md)) writes governed documents and claims
no phase, the same way the idea-batching pack planning recorded in `SESS-2026-09-12-03` claimed
none. The seven phases this session *created* (`phase-lit-01`–`phase-lit-07`) all enter the
backlog `queued`; the campaign they describe has not started.

The one active claim throughout was a peer's — `phase-demo-07` (`agent-demo-glossary`), locking
`sys-brain` and `sys-portfolio`, which this session never touched.

Because no phase was claimed, there are no backlog `verification` or `acceptance` lists to
recompute. The protocol's own gates played that role, and the independent review in `## Review`
below was run against the session's diff instead of against a phase's acceptance conditions.

## Verification

Run at close, in the primary checkout on `dev`:

```text
$ uv run python -m src.governance
Governance OK: 19 systems, 182 documents, 20 memories, 129 backlog phases

$ uv run python tools/check_no_private_content.py
check_no_private_content: OK (522 tracked files, 31 identifiers checked)

$ uv run python -m pytest -q
578 passed, 2 warnings

$ diff <(uv run python -m src.governance --catalog) docs/08-governance/catalog.md
(no output — the committed catalog matches regenerated output)

$ git status --short
(clean)
```

The queue, confirming the campaign is promoted but not prioritised:

```text
$ uv run python -m src.governance --ready
Queued to the front: phase-wb-07, phase-port-02, phase-ses-01, phase-lit-01.
| phase-lit-01 | Literature review Pass 1a — broad map of knowledge
  representation, provenance and epistemics domains | 4 | 3 | ready | — | — |
```

## Acceptance

No phase, therefore no `acceptance` list. What stands in its place is `GOV-009`'s eight stages,
each of which either passed an owner gate or an adversarial review:

| Stage | Artifact | State |
|---|---|---|
| 1 | Prompt A — pre-plan package (`PROMPT-027`) | Owner-ratified, seven decisions |
| 2 | Prompt B — pack factory (`PROMPT-028`) | Drafted by executing Prompt A |
| 3 | Adversarial review of Prompt B | 14 findings, 4 blocking; all applied; owner signed off |
| 4 | The pack (`PLAN-023` + `.01`–`.03`, `PROMPT-029`, 7 phases) | Written after owner confirmed the plan |
| 5 | Adversarial audit of the pack | 11 findings, 3 blocking; all applied; 4 owner rulings |
| 6 | Coordinator prompt (`PROMPT-030`) | Generic and idempotent by design |
| 7 | Owner sign-off on the coordinator | Given; optional adversarial review declined |
| 8 | Kick-off record (`PROMPT-031`) | Four deltas ratified; kick-off paragraph delivered |

## Backlog

Seven phases added, all `status: queued`, each declaring `systems: [sys-research]` only:

- `phase-lit-01` … `phase-lit-07`, dependency-chained `01 → 02 → … → 07` so Pass 1 → 2 → 3 → 4
  is forced and no synthesis phase can become ready while an evidence phase is open.
- `phase-lit-01` was appended to `next_up` on the owner's ruling to promote it — in **last**
  position, behind `phase-wb-07`, because ratified decision 4 gives demo work precedence. It is
  promoted, not prioritised.
- `phase-lit-07` carries a stated entry condition: it may not start until `PROMPT-031` holds a
  dated `pre-synthesis check-in held: <date>, ruling: proceed` entry.

No phase's `status`, `session`, `completion_evidence` or `result` was set to a completion claim.

## Unresolved

- **The campaign has not run.** Seven queued phases, nothing claimed, no campaign deliverable
  written. `GOV-009` remains methodology with one manufacturing run behind it and no executed
  campaign — the stage templates and the `K`/`S*`/`X*`/`R`/`G`/`A` shape are still untested
  against real search work.
- **`000146`** — `SESS-2026-09-11-01` still states that the literature-review handoff note
  requires an external review of the codebase audit before the campaign. It does not. The owner
  ruled the paraphrase an error while ratifying `PROMPT-027`, so nothing is blocked, but the
  record still carries the claim and this repository has no convention for amending a closed
  session record. The convention question is the part worth settling.
- **Two proposals were ratified at the stage-5 gate rather than re-examined afterwards** — the
  descope ladder's order and the kind mapping. Both stand on the auditor's recommendation plus
  the owner's ruling; neither has been tested by use.

## Review

An independent sub-agent, started with no context from this session, reviewed the eight commits
against the claims made for them. Its findings, verbatim:

### Verdicts on the eight claims put to it

1. **All eight `GOV-009` stages represented — CONFIRMED, with one evidentiary caveat.** Every
   artifact carries the template appendix's required sections: Prompt A all seven, Prompt B all
   five, the coordinator all five, the kick-off record all three; delegation-pack sections carry
   `K`/`S*`/`X*`/`R`/`G`/`A`, and phases without `R`/`A` state why. Caveat: *"the stage-3 and
   stage-5 adversarial reviews left no committed artifact. GOV-009 does not require one, and I
   verified the stage-5 fixes directly against `git show efba8f3:...` vs. `cf96d00`. The stage-3
   review's '14 findings' are **not independently verifiable** — PROMPT-027 and the
   already-revised PROMPT-028 landed in the same commit (0dd6d0a), so no pre-review draft exists
   in git. That is an account in a commit message, not evidence."*

2. **Pack complete and internally consistent — CONFIRMED except the deliverable-ownership
   wording.** 72 table rows, 72 unique ids `D01`–`D72`, no duplicates or gaps, partition
   25 + 20 + 27, names matching the methodology item-for-item; the `depends_on` chain is strictly
   linear and verified mechanically (*"only phase-lit-01 is `ready`; 02–07 are `waiting`"*).
   **Discrepancy:** *"'each owned by exactly one phase's `deliverables`': false as stated.
   `03_source_inventory.csv` is in the `deliverables` of phase-lit-01, -02 **and** -03;
   `04_evidence_matrix.csv` is in phase-lit-04 **and** -05. PLAN-023's 'Deliverable coverage'
   section explains this deliberately … So the pack is coherent; the session's claim overstates
   it."*

3. **The three blocking stage-5 findings — CONFIRMED as changes, but (c) only partly applied.**
   (a) nine "same procedure as" references before, zero after; shared blocks genuinely
   self-contained, the two survivors being pointers to a claiming step, *"not dangling in any
   load-bearing sense"*. (b) `subject_source_id` added and threaded into LIT-04 G, LIT-05 S1,
   LIT-05 G, LIT-07 G and the coordinator's completion gate — *"Count before: 0. Genuinely
   computable now."* (c) real change in the delegation pack, *"**But see independent finding
   F1**"*.

4. **Four owner rulings recorded where they operate — CONFIRMED.** Ladder heading changed from
   proposal to ratified, all five rungs carry a gate re-parameterization clause, and the reorder
   is real (seed validation moved from rung 5 to rung 3, ahead of forward chaining). Branch model
   *"consistent everywhere"*. Seven `- sys-backlog` deletions. `phase-lit-01` present in
   `next_up`.

5. **`phase-lit-01` last in `next_up` — CONFIRMED.** *"It is behind phase-wb-07 and also behind
   two others the claim does not name."*

6. **Nothing under `research/` touched except the one deletion — CONFIRMED.** *"exactly one path
   under `research/`: `D research/CLAUDE.literature-review.md` in 0b8d9ca"*; the frozen baseline
   files *"were all last touched by `b2b564b` ('Initial commit') and appear in no commit of the
   eight."*

7. **`PROMPT-031`'s pinned facts — CONFIRMED, and the `74fbeae` pin is correct, not a defect.**
   Both blob hashes reproduced by `git hash-object`; the peer-claim pin exact; *"PROMPT-030's
   preflight never compares `HEAD` to a pinned commit … Correct as a historical pin."*

8. **Repository green — CONFIRMED.** Governance exit 0, catalog diff empty, `578 passed, 2
   warnings`. The only untracked file was this session record mid-write.

### Independent findings

- **F1 — material.** *"The evidence contract still assigns the `second_review` write to R, and by
  the pack's own precedence rule it wins."* Field 43 read *"filled only by the independent R
  reviewer"*, while `PROMPT-029` states that on schema fields the contract wins. *"A dispatched
  LIT-06 R agent following the precedence rule would conclude it is the one who fills it, which is
  the exact behaviour blocking finding (c) existed to stop. Blocking finding (c) is applied in the
  delegation pack and unapplied in the document that outranks it."*
- **F2 — moderate, a regression introduced by the fix commit.** LIT-04 K demanded a 44-field
  evidence-matrix header against a 43-field contract; the pre-fix text correctly said 43. *"A
  Haiku kickoff told to produce a 44-column header against a 43-field contract has no correct
  output."*
- **F3 — moderate.** `phase-lit-07`'s verification demanded *"all nine"* gate measurements where
  LIT-07 G now lists eight, the ninth having been correctly hoisted into Block G. *"The stale
  number sits in a phase acceptance condition a gate agent will read and cannot satisfy."*
- **F4 — minor internal contradiction.** `PLAN-023` said campaign phases *"are never added to
  `next_up`"* while `635b7bc` added one. *"The following clause sanctions the owner's promotion, so
  this is self-resolving on a careful read, but the sentence is absolute as written."*
- **F5 — minor contradiction.** The coordinator's preflight required being on the campaign branch
  with no phase-one carve-out, while the kick-off record pins that the branch does not exist yet.
  *"The coordinator prompt as written fails its own preflight on session one."*
- **F6 — minor.** `PROMPT-028`'s preflight `cmp` and its mandated up-front question lost their
  subject when the duplicate was deleted. *"0dd6d0a's message lists 're-run idempotency' among the
  stage-3 findings fixed; this particular hole survived."*
- **F7–F9 — observations.** A frozen inventory (`research/evidence/repository-inventory.md`) still
  cites the deleted file; the pack is split across two `systems` declarations because
  `sys-research` did not exist when the first two documents were written; all four `PLAN-023`
  documents are `status: draft` while `phase-lit-01` is promoted and `ready` — *"not a violation,
  only a state a future consistency check would flag."*
- **Idea `000146` verified independently:** the handoff note contains no "external review" text
  and the session record does carry the claim.
- **No governance or schema rule bent.** *"The eight commits touch no `AGENTS.md`, `CLAUDE.md`, or
  `_private/` path."*

### Overall verdict, verbatim

> The protocol was genuinely executed, not narrated: every stage has a real artifact with
> GOV-009's required sections, the 72-domain partition is exact and matches the methodology
> source, the dependency chain mechanically enforces the pass order, all four owner rulings are
> recorded where they operate, and the three blocking stage-5 findings produced real diffs rather
> than claims of diffs — I checked each against the pre-fix blob. The pinned starting state is
> accurate to the byte. Against that, the fix commit `cf96d00` carries three real consistency
> defects of its own: the evidence contract still assigns the `second_review` write to the R
> reviewer, which by PROMPT-029's own precedence rule defeats blocking finding (c) at the point of
> dispatch (**F1** — the one finding I would call material); the evidence-matrix header count was
> changed from a correct 43 to an unsupported 44 (**F2**); and `phase-lit-07`'s verification still
> demands nine gate measurements where eight now exist (**F3**). All three are single-line edits,
> and all three are the same failure mode the session itself recorded a procedure about — a
> downstream count or ownership statement left stale after the upstream thing it describes was
> rewritten. The repository is green, the tree is clean apart from the session's own in-progress
> record, and nothing under the frozen baseline was touched.

### What was done in response, at close

Five of the findings were fixed before this record was committed; the rest are recorded rather
than actioned.

- **F1** — `PLAN-023.03` field 43 now reads *filled only by `LIT-06 X2`, from the independent R
  reviewer's report*, and states that the reviewer writes no repository file and never opens `05`
  or `06`. The contract now agrees with the delegation pack instead of outranking it.
- **F2** — LIT-04 K corrected to 43 fields.
- **F3** — `phase-lit-07`'s verification corrected to eight measurements.
- **F4** — `PLAN-023` now says no *agent* adds a phase to `next_up`, and records that the owner
  promoted `phase-lit-01` behind the existing entries.
- **F5** — the coordinator's branch bullet gained the phase-one carve-out its adjacent ledger
  bullet already had.
- **F6** — `PROMPT-028` gained a dated note that the ruling was made and the file deleted, so the
  stale `cmp` and question read as history rather than instruction.
- **F7, F8, F9** and the claim-2 overstatement are left as recorded observations. The frozen
  inventory is deliberately not edited; the split `systems` declarations are historically
  explicable; the plan-status question belongs to the open `phase-idea-05`. The
  deliverable-ownership wording in this record was corrected rather than defended — the claim
  should have been *owned by the completing phase*, which is what `PLAN-023` itself says.
- **The stage-3 caveat stands and cannot be retired.** No pre-review draft of `PROMPT-028` exists
  in git, so that review's 14 findings are an account rather than evidence. Future packs should
  commit the pre-review draft first so the gate leaves a verifiable trace.

## Decisions

**The campaign's scope was frozen before any drafting started.** The owner ratified H0 and
H1–H11 exactly as the content methodology defines them, the full thirteen deliverables, and
web-search-plus-free-APIs as the provider envelope. Those went into Prompt A marked
do-not-re-ask, which is what kept four subsequent agents from relitigating them.

**The session record that produced `GOV-009` was found to misstate its own source.** It claims
the handoff note requires external review of the codebase audit first; the note says nothing of
the kind. The owner ruled the paraphrase an error and the codebase review a frozen input with no
precondition, which unblocked the campaign before it was planned.

**The spend estimate was allowed to exceed its envelope rather than be compressed.** Prompt A
estimated four to six sessions; the factory's honest design came to seven (range six to eight),
because 72 domains with real variant coverage will not fit in two Pass 1 phases and 20–30 deep
reads with a 43-field schema will not fit in one Pass 2 phase. The owner accepted seven. The
compression alternative was rejected on the grounds that it traded away precisely the variant
depth and deep-read quality the adversarial posture depends on — ratified decision 7 already said
runway is whatever the passes need, and four-to-six was an estimate rather than a cap.

**One long-lived campaign branch, not seven.** The stage-5 audit found that per-phase branches
would make every phase boundary depend on an owner integration the pack never mentioned — seven
approvals, and an unspecified failure if one were missing. The owner chose a single
`agent/lit-campaign` branch with integration at exactly two points, which also keeps the ledger
present for each next kickoff without cross-branch archaeology.

**`sys-backlog` was dropped from the campaign phases.** Four unrelated open phases declare it, so
its presence would let any of them block the campaign on system overlap — none of them being the
demo work that ratified decision 4 actually privileges.

**The descope ladder was ratified with the auditor's amendments, against the drafter's order.**
Each rung now states the gate re-parameterization it implies, because a rung taken without one
leaves the campaign unable to close its own final gate; and restricting seed validation moved
ahead of dropping forward chaining, on the argument that uncited seed validation carries almost
no synthesis weight while forward chaining is what surfaces recent systems in the fastest-moving
domains, where the anti-novelty case is most likely to be decided.

**Two owner rulings expanded agent discretion deliberately.** Descope rung 1 may be taken
autonomously if Pass 1 overruns, and the single Opus escalation is the coordinator's to spend if
documented. Both are recorded in the kick-off record as stated exceptions, which is the only
place `GOV-009` permits them.

**`phase-lit-01` went to the back of `next_up`, not the front.** The owner's ruling was to
promote it; ratified decision 4 says demo work wins. Appending rather than fronting satisfies
both, and the session record says so explicitly so the next reader does not "fix" the ordering.

## Corrections

**A verification was written that could not fail.** Checking whether a backlog edit had moved the
generated catalog, this session copied `catalog.md` aside, ran `--catalog` with output discarded,
and diffed the copy against the original — a file compared against a copy of itself, guaranteed
to pass. It rested on an unverified assumption that `--catalog` writes the file; it prints. The
check reported "CATALOG UNCHANGED" and meant nothing. The catalog was in fact fine, confirmed by
the suite's own `test_committed_catalog_matches_regenerated_output` — so the only real
verification came from a test that would have run anyway. Recorded as
`brain/procedures/a-check-that-cannot-fail-is-not-a-check.md`, because the generalisable error is
structural rather than situational: ask what failure would look like before running a check.

**A commit was made on a red tree.** Committing idea `000146`, the pytest invocation was piped
through `tail`, so the shell reported the pipeline's exit status instead of the test run's. One
test was genuinely failing — the ideas markdown projection needed regenerating — and the commit
proceeded anyway. Fixed in `32d03fc`, which says so in its own message. This is the same defect
class as the first correction, committed inside the very commit that recorded the procedure
warning against it.

**The stage-5 fix commit introduced three defects of its own, caught only by the close review.**
`cf96d00` applied eleven audit findings and, in doing so, left a field-count at 44 where the
contract says 43, a gate-measurement count at nine where eight remain, and — the material one —
the evidence contract still naming the R reviewer as the writer of `second_review`, which by the
delegation pack's own precedence rule would have defeated the very independence fix that commit
was making. All three are the failure mode this session had just written a procedure about: a
downstream count or ownership claim left stale after the thing it describes was rewritten. Fixed
at close, before the record was committed.

**A claim in this record was overstated and corrected.** It said each of the thirteen deliverables
is owned by exactly one phase's `deliverables` list. Three of them appear in three phases' lists
and one in two, because `01`–`03` are built incrementally — ownership is by *completing* phase,
which is what `PLAN-023` says and what this record should have said.

**A peer's correction was accepted on the catalog's inputs.** This session told a fix agent the
catalog needed no attention because no document was being added. That inference was unsound:
`render_catalog()` derives from the backlog as well as the document set, so a `backlog.yaml` edit
can move it. The peer caught it, the instruction was amended to verify rather than assume, and
the outcome was checked properly.

**Work was briefly committed onto a peer's branch.** A peer switched the shared checkout onto
`agent/demo-cut-pack-factory`, so `74fbeae` and `635b7bc` landed there rather than on `dev`. The
first was repaired by an owner-ratified fast-forward; the second was caught only because
`git branch -d` refused to delete an unmerged branch. Both are on `dev` now. During that window
both sessions also drew false conclusions from transient reads — this session briefly saw a
missing commit and a stale catalog count, and the peer nearly recorded a real ordering failure as
an intermittent test. The peer has since moved to its own worktree.

## Left undone

**The campaign itself.** Everything here manufactures the instrument; nothing uses it. The
deliberate stopping point is that `phase-lit-01` is queued and promoted, and the kick-off
paragraph in `PROMPT-031` is pasteable whenever the owner chooses to start. Demo week is
2026-09-15 and the campaign is not demo-critical, so starting it was never this session's call.

**`GOV-009`'s own validation.** The protocol now has one manufacturing run behind it, which
exercised stages 1–8 but not a single search. Whether the `K`/`S*`/`X*`/`R`/`G`/`A` shape
survives contact with real search work is still unknown, and the first execution session is what
will answer it. Two things are worth watching specifically: whether a one-session phase can
actually absorb six or seven search-and-extraction pairs, and whether the gates that now measure
against the ledger's domain and `subject_source_id` columns are as mechanical in practice as they
read on paper.

**`000146`'s underlying question.** Left as an idea rather than fixed, because correcting a
closed session record raises a convention this repository has not settled — whether such a record
is amended in place with a dated note, or left as the historical account it is. Fixing this one
instance without settling the convention would just move the question.

**The optional stage-7 adversarial review** of the coordinator prompt was declined by the owner,
per `GOV-009`'s default. If the first execution session finds the coordinator prompt awkward,
that review is the thing that was skipped.

**A gap in how `GOV-009`'s review gates leave evidence.** The stage-3 review of Prompt B is
unverifiable after the fact, because Prompt A and the already-revised Prompt B were committed
together — no pre-review draft exists in git, so the review's findings survive only as an account
in a commit message. The stage-5 review, by contrast, is fully checkable because the pack was
committed before the audit ran and the fixes landed in a separate commit. The cheap fix for future
packs is to commit the pre-review draft first; whether `GOV-009` should require it is the owner's
call and is not recorded as a rule here.
