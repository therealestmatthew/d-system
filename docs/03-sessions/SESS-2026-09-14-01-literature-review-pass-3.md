---
schema_version: 1
id: doc-session-literature-review-pass-3
code: SESS-2026-09-14-01
title: Literature review Pass 3 — adversarial hypothesis testing and nineteen independent collision reviews
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-research
- sys-backlog
depends_on:
- doc-lit-campaign
- doc-prompt-literature-review-delegation-pack
- doc-prompt-literature-review-coordinator
- doc-prompt-literature-review-kickoff
---

# Literature review Pass 3 — adversarial hypothesis testing and nineteen independent collision reviews

The campaign's sixth execution session. Claimed by `agent-lit`, working in
`../d-system-worktrees/lit-campaign` on `agent/lit-campaign`.

## Phase

`phase-lit-06` — Literature review Pass 3: adversarial hypothesis testing H1–H11 and the
independent second review of every critical collision.

## Verification

`uv run python -m src.governance`

```text
Governance OK: 20 systems, 195 documents, 22 memories, 133 backlog phases
exit 0
```

`uv run python tools/check_no_private_content.py`, with changes staged

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is
expected in CI / a fresh clone)
check_no_private_content: OK (556 tracked files, 0 identifiers checked)
exit 0
```

**This is not a passing verification.** `_private/` is gitignored and absent from a worktree, so
the tool builds an empty identifier list and reports `0 identifiers checked`. Idea `000150`
records this. The real check runs in the primary checkout.

`uv run pytest`

```text
580 passed, 2 warnings
```

### Delegation-pack section `LIT-06 G` — the phase gate

Run on Haiku, one fix cycle spent (see below). Corrected output:

**Measurement 1 — every H1–H11 has a challenger block with a permitted status. Gate: 11 of 11.
PASS.** Population: all eleven hypothesis blocks in `06_hypothesis_tests.md`.

| | status | challengers |
|---|---|---|
| H1 | KNOWN_COMPONENT_NEW_INTEGRATION | 2 |
| H2 | LIKELY_ALREADY_KNOWN | 13 |
| H3 | KNOWN_COMPONENT_NEW_INTEGRATION | 9 |
| H4 | INSUFFICIENT_EVIDENCE | 1 |
| H5 | KNOWN_COMPONENT_NEW_INTEGRATION | 8 |
| H6 | KNOWN_COMPONENT_NEW_INTEGRATION | 3 |
| H7 | LIKELY_ALREADY_KNOWN | 10 |
| H8 | LIKELY_ALREADY_KNOWN | 4 |
| H9 | LIKELY_ALREADY_KNOWN | 18 |
| H10 | KNOWN_COMPONENT_NEW_INTEGRATION | 4 |
| H11 | INSUFFICIENT_EVIDENCE | 2 |

Triggers tested: all eleven carry a status from the permitted vocabulary; none carries `NOVEL`;
all eleven name a non-empty `strongest_challenger`. **Zero `POTENTIALLY_DISTINCT`.**

**Measurement 2 — every `critical_collision: yes` row has `second_review` set. Gate: 0 pending.
PASS.** Population: 19 rows of 34 in `04_evidence_matrix.csv`. Classified by the value's leading
token.

```text
disputed   13
confirmed   6
pending     0
```

**Measurement 3 — ledger rows carrying a hypothesis id as `domain_id`, all phases. Gate: ≥ 2
each. PASS.** Population: 997 ledger rows.

```text
H1 3   H2 2   H3 2   H4 15   H5 2   H6 2
H7 2   H8 2   H9 2   H10 2   H11 4
```

Distinct-query count equals row count for every hypothesis — no hypothesis reaches its floor by
logging one query twice. Before this phase, **only H4 had any such rows (8)**; the other ten
stood at zero.

**Measurement 4 — duplicate rate in this phase's searches, the saturation signal. 20.0%.**
Numerator 44, denominator 220: result identifiers from the 30 `LIT-06-*` ledger rows, resolved
against the pre-phase inventory's `url_or_doi` column. The coordinator recomputed this
independently and reproduced 44/220 exactly, and re-ran it resolving against `source_id` **or**
`url_or_doi` with an identical result — `result_ids` genuinely carries identifiers, so the
mixed-form hazard of `000147` does not bite this column. On a distinct-identifier basis, 36/208
= 17.3%.

**The campaign is not saturated.** Four results in five were new. The methodology's stop
condition is that additional searches "mostly yield duplicates or clearly adjacent work"; 20% is
not that. A saturation claim at `LIT-07`'s final gate is not supportable from this number.

## Acceptance

- **`06_hypothesis_tests.md` gives every H1–H11 a strongest challenger, evidence, assessment and
  a status from the permitted vocabulary, each traceable to evidence-matrix rows** — **Met, after
  the close review failed it once and the reconciliation ran.** The first close review judged it
  Not met: H11's and H1's named challengers rested on descriptions the second reviews showed to
  misread the source, with no in-document flag. The owner directed the fix be made here rather
  than deferred, `LIT-07 X1`'s item-0 text was dispatched early as the work, and an independent
  re-review confirmed the condition now holds — verifying `burns-groth`'s §2 and §6 against the
  primary PDF itself rather than against `05`'s account of it. Eleven blocks, five keys each,
  every status permitted, all thirteen cited `source_id`s present in the matrix, and a dated
  reconciliation note at the head of the file. See `## Review`.
- **Every CRITICAL_COLLISION in `05_critical_collisions.md` carries a recorded independent second
  review; disagreements are recorded, not averaged away** — **Met.** 19 sections, 19 dated review
  subsections, 0 pending, each recording the first assessment's position and the reviewer's
  separately. Verified by the coordinator against the files, not relayed from a worker.

## Backlog

`phase-lit-06` — `status: active`, `agent: agent-lit`. Left active deliberately: only the
owner's `/session-close` moves a phase to `complete`, and the campaign's one scheduled pause
falls immediately after this gate.

`next_action`: None outstanding for this phase. The pre-synthesis check-in was held later in this
same session and `PROMPT-031` now carries the dated entry, so `phase-lit-07` is unblocked; it was
deliberately not started. `phase-lit-06` awaits the owner's `/session-close`.

`completion_evidence` (files that exist now):

- `research/literature-review/05_critical_collisions.md`
- `research/literature-review/06_hypothesis_tests.md`
- `research/literature-review/04_evidence_matrix.csv`
- `research/literature-review/00_search_ledger.csv`

## Unresolved

**Five of the seven items below were ruled on at the pre-synthesis check-in, held by the owner
later in this same session — see *The pre-synthesis check-in* at the end of this record. They are
left here as written, with the ruling noted, so the finding and its resolution stay together.**

- **`06_hypothesis_tests.md` is stale against the matrix it cites, and no dispatch owns it.** The
  pack gives `X2` the matrix `second_review` field and `05`; nothing updates `06` after the
  second reviews land. H11's named strongest challenger
  (`burns-groth-agentic-ontological-notebook-memory-2026`) was found to describe a mechanism the
  paper's own §6 calls future work, and H1's (`eywa-provenance-grounded-memory-joshi-2026`) rests
  on "three orthogonal dimensions" a reviewer showed are one axis restated. `05`'s preamble now
  states plainly that `06` was not updated by this phase. `LIT-07` rebuilds from the matrix, so
  the error does not propagate into synthesis — but `06` must not be read as current.
- **Six flags are disputed to the point of not standing, and the count stays at 19 pending the
  owner's ruling.** Reviewers found no trigger fires under their own re-derivation for
  `em-llm`, `tgms`, `burns-groth`, `eywa`, `memtx` and `us20250165226a1`. `X2` recorded these as
  disputes and changed no score, no `critical_collision` value and no `hypotheses_challenged`
  value — verified by a field-level diff across all 34 rows. Accepting them would drop the count
  19 → 13 and change the population measurement 2 ranged over.
- **Patents have no scoring rule in any governed document.** The patent review reached its
  verdict on a "score the claims, not the specification" instruction the **coordinator**
  introduced, not the evidence contract — which is silent on patents and whose `source_type`
  enum still has no patent bucket (`000148`). The reviewer flagged this itself. Recorded in `05`
  with that provenance caveat; not folded in as settled.
- **`PLAN-023.03`'s fourth flag trigger is ambiguous.** "Spans at least four **adjacent** stages"
  does not say whether *adjacent* means contiguous. Reviewers reached different counts under the
  two readings; on `evidence-graphs-fair` the trigger fires under one and not the other. Recorded
  in `05` as an open contract question. The contract was not edited.
- **A one-directional depth defect in the Pass 2 deep reads.** Seven of nineteen rows were found
  to have scored at or near the rubric's ceiling while their own locators stopped short of the
  material that decides the question — `memtx` recorded `abstract_only` when the full text was
  one click away on the same arXiv page; `aporia`'s locators capped at page 4 and its
  `actor_model` consequently says "a single coding agent" where §3.3 describes three; `em-llm`
  never cited the retrieval section that is the only section bearing on its H5 claim. Two worse
  cases are not depth at all: `tgms` reported "100% detection" from four of eight mutation
  classes, omitting the two at 36% and 0% that the source itself discloses, and
  `evidence-graphs-fair` attributed a 2005 citation that appears nowhere in the source's 73-item
  bibliography. **No reviewer found a row that understated a collision.** The error is
  one-directional, toward finding collisions, in a campaign whose null hypothesis is that
  collisions exist. Every instance was caught by the control built to catch it.
- **A peer commit clobbered the campaign's backlog state; restored on this branch.** See below.

## The backlog regression on `dev`

Commit `5ecb203` ("Adopt the owner's command and skill rosters") rewrote
`docs/09-backlog/backlog.yaml` from a stale copy. Its intended change — `scope`, `acceptance`
and `verification` on `phase-kit-01`, `phase-kit-02` and `phase-kit-04` — is correct and was
left untouched. The same write also rolled four `phase-lit-*` entries back to their state before
Pass 1c closed:

```text
phase-lit-03  complete -> active,  session/completion_evidence/result deleted
phase-lit-04  complete -> queued,  same, agent cleared
phase-lit-05  complete -> queued,  same, agent cleared
phase-lit-06  active   -> queued,  agent cleared (this session's claim)
```

The tell is `phase-lit-03`'s restored `next_action` — "Dispatch delegation-pack section LIT-03
after phase-lit-02 completes" — last true three phases earlier. `next_up` was unchanged and no
phase was added or removed, so this was collateral from a whole-file write rather than a
decision.

**Governance exits 0 either way.** The validator checks claim conflicts, `max_active` and
dependency chains; a `complete` phase silently becoming `queued` breaks none of them. It
surfaced only because this session rebased onto `dev` at the phase boundary and found its own
claim missing — an unplanned detection, not a check.

Restored in `b319b7a` from `7ff3421`, the commit immediately before the regression. Verified
afterwards that the four restored phases equal their pre-regression state exactly and every
other phase in the file equals current `dev`, the three kit phases included. Restoring phases
beyond this session's own was the owner's explicit call, taken after the finding was reported
rather than worked around.

The evidence was never at risk: it lives on this branch and came through the rebase byte-intact.

## What was dispatched

Item order `K → S1 → X1 → R×19 → X2 → G`, as `LIT-06 K` specifies. Checked before dispatching
for the shape `000218` describes — `phase-lit-05`'s order made its own gate unsatisfiable. It
does not recur here: the only dispatch that adds matrix rows is `S1`, and `S1` runs first, so
every row `R` and `X2` must cover exists before either runs.

**`K` (Haiku).** Claimed `phase-lit-06` on `dev` in `7ff3421`, with the catalog regeneration the
claim forces, in the primary checkout — the only work `AGENTS.md` permits there. Verified prior
evidence rather than recreating it.

**`S1` (Sonnet), one fix cycle.** 30 ledger rows, `LIT-06-S001`–`S030`, contiguous, all
`pass: 3`, 15 fields on every row, CRLF preserved across all 998 lines. Four new matrix rows.
Took H4 off zero: `epistemic-sybil-resistance-bara-2026` formalises a provenance DAG with a
closed-form discount for corroboration sharing an evidentiary root. Also ran the deliberate
negative on the nearest prior-art family — `dong-berti-equille-srivastava-2009`, truth discovery
and copy detection — which came back component 3, not a collision. Fix cycle 1: one row wrote
prose into `hypotheses_challenged` and `second_review` where every other row carries a token;
since `LIT-07 G` computes challenger counts from that field, a consumer would have read "H3 and
H4" out of a sentence whose point was that the source challenges neither, inflating H4 in the
direction that flatters H0.

**`X1` (Sonnet).** `06_hypothesis_tests.md` with eleven blocks, and `05_critical_collisions.md`
with 19 sections. Statuses: 4 `LIKELY_ALREADY_KNOWN`, 5 `KNOWN_COMPONENT_NEW_INTEGRATION`,
2 `INSUFFICIENT_EVIDENCE`, **0 `POTENTIALLY_DISTINCT`**. H8 records the review-instructions
verdict as primary with the frozen register's consolidation-half split inside `assessment`,
which is what the scope record requires.

**`R` (Sonnet ×19).** One dispatch per `critical_collision: yes` row — 19, not the 16 the phase
brief anticipated, because `S1` added three. Each reviewer received exactly two inputs: the
source, and a file containing that row's 43 fields and nothing else. None could reach the first
assessment's rationale through the dispatcher, and all were freshly spawned, so none had
produced the row or `05`/`06`. **6 confirmed, 13 disputed. All 19 answered "no" to whether their
source materially subsumes a hypothesis — no `GOV-009` escalation.**

**`X2` (Sonnet), one fix cycle.** 19 verdicts into `second_review` and 19 dated subsections in
`05`, plus 42 factual corrections across 15 rows. Changed no score, no `critical_collision` and
no `hypotheses_challenged` — verified by field-level diff. Fix cycle 1: `X1`'s preamble claimed
`X2` folds reviewer findings into `06_hypothesis_tests.md`, which is both untrue and the
writer-gap stated as though resolved.

**`G` (Haiku), one fix cycle.** Fix cycle 1: measurement 2's breakdown was reported as 10
confirmed / 9 disputed against a true 6 / 13. The PASS was correct — the gate tests `0 pending` —
but the split inverts the phase's central finding.

## Spend posture

- **Searches**: 30 this phase (`LIT-06-S001`–`S030`); ledger now 997 rows.
- **Sources deep-read**: 4 new matrix rows this phase; matrix now 34 rows × 43 fields, 0 blanks.
- **Independent reviews**: 19, each a full source re-read.
- **Fix cycles**: 4, one each against `S1`, `X2`, `G`, and none exceeding the cap of two.
- **Opus escalation**: none spent, in this session or the campaign.
- **Descope rung**: none taken.
- **Runway**: 6 of 7 sessions used, against an owner-accepted range of six to eight.

## Review

An independent sub-agent reviewed the range `dev..HEAD` (20 commits) at close, starting with no
context from this session. Its findings, condition by condition.

### Acceptance 1 — **Not Met**

> Formally this holds: all 11 `## H1`–`## H11` blocks exist in
> `research/literature-review/06_hypothesis_tests.md`, each with `strongest_challenger`,
> `evidence`, `assessment`, and a `status` from the permitted vocabulary (verified statuses match
> the gate table exactly: H1/H3/H5/H6/H10 `KNOWN_COMPONENT_NEW_INTEGRATION`, H2/H7/H8/H9
> `LIKELY_ALREADY_KNOWN`, H4/H11 `INSUFFICIENT_EVIDENCE`). No `NOVEL`, no "no prior work exists"
> anywhere in the three deliverables.
>
> But I read the H1 and H11 blocks against their named challengers' second-review subsections in
> `05_critical_collisions.md` myself (lines 662–719 and 19–72 of `06`, against lines 1046–1105 and
> 921–989 of `05`), and the defect is not a disputed score threshold — it is a documented
> misreading of the source:
>
> - **H11**'s strongest challenger, `burns-groth-agentic-ontological-notebook-memory-2026`, is
>   presented in `06` as "a named, working, demonstrated closed loop... with a public benchmark."
>   The independent reviewer, reading the same paper end to end, found its own §6 states plainly:
>   *"Our future work focuses on developing the virtuous cycle..."* — the mechanism `06` calls
>   demonstrated is the paper's own future work.
> - **H1**'s strongest challenger, `eywa-provenance-grounded-memory-joshi-2026`, is presented in
>   `06` as independently tracking "three orthogonal dimensions." The independent reviewer read all
>   29 pages and found each of the five object types carries a deterministic one-to-one mapping to
>   tier and lifecycle — one axis restated, not three independent ones — and that the word
>   "orthogonal" never appears in the paper.
>
> `05`'s preamble states plainly that `06` was not updated by this phase; `06` itself carries no
> such disclaimer anywhere in its own text. A reader of `06` alone — the artifact this acceptance
> condition evaluates — has no way to know two of its eleven verdicts rest on evidence the
> campaign's own adversarial control has already shown to be inaccurate. Nine of eleven hold up
> cleanly; two do not, in substance rather than form. I judge the condition **Not Met** as
> written, though I note the countervailing case: the owner was informed of exactly this gap and
> ruled to defer the fix to `LIT-07 X1` item 0 rather than block on it — a reasonable process
> call, but a different question from whether the acceptance text is satisfied today.

### Acceptance 2 — **Met**

> Confirmed directly: 19 `##` sections, 19 dated `### Review — 2026-09-14` subsections,
> `second_review` populated on all 19 `critical_collision: yes` matrix rows (0 pending; 13
> `disputed`, 6 `confirmed`). Sampled sections (aporia, burns-groth, eywa) show a consistent,
> honest pattern — "First assessment position" and "Independent reviewer position" stated
> separately, then a "Resolution" that explicitly states the score/flag/`hypotheses_challenged`
> value is "left exactly as scored" when disputed, never silently adjusted.

### Gate measurements — all independently reproduced

All four reproduced. On measurement 4 the reviewer added a caution worth keeping:

> a strict exact-string match of the 220 `LIT-06-*` `result_ids` against the pre-phase
> (`a00623f`) inventory's `url_or_doi` column gives **43/220**, one short. The 44th requires
> recognizing `plato.stanford.edu/entries/reasoning-defeasible` (no trailing slash […]) as the
> same source as `plato.stanford.edu/entries/reasoning-defeasible/` (with slash […]) — a
> normalization the ledger row's own annotation confirms is correct […]. With that one legitimate
> match, I reproduce **44/220 exactly**. I agree with the number; the method is sound in intent
> but mechanically fragile — a pure string-equality check under-reports by one without
> manual/semantic attention, and nothing in the pipeline normalizes URL forms across searches.

File integrity, the frozen baseline, the backlog restore and the governed-document amendments all
verified clean. On the restore:

> Result: `phase-lit-03/04/05/06` in `b319b7a` are byte-identical (as parsed structures) to their
> `7ff3421` state. Every other phase present in both `b319b7a` and current `dev` matches exactly,
> kit phases included. […] This is a clean, surgical restore exactly as claimed.

### Discrepancies it found

1. **The correction count was wrong in this record.** "42 factual corrections across 16 rows" —
   the cell count is right, the row count is **15**. Verified independently by the coordinator
   after the review and corrected above.
2. **Stale counts in the verification block** (194 documents / 555 tracked files), because those
   commands ran before this session's final commit added a document. Corrected above.
3. **The supplementary distinct-identifier figure** — the record gives 36/208 = 17.3%; the
   reviewer got 36/207 under stricter normalization. The coordinator re-ran it and reproduces
   36/208 with trailing-slash normalization, so this is a normalization difference rather than an
   error, and it illustrates the same fragility the reviewer flagged on the primary figure. Left
   as written, with the fragility recorded.

> No other discrepancies found — the backlog restore, the frozen-baseline check, the
> governed-document amendments, the file-integrity checks, and the four gate measurements' primary
> values all reproduced exactly against my own independent derivation.

### Its completion verdict

> If `/session-close` requires acceptance 1 to hold in substance, it does not yet — `06` needs the
> `LIT-07 X1` item-0 reconciliation (already written into `PROMPT-029`) before this phase's
> central deliverable can be called accurate. If the owner's standard is the literal text of the
> acceptance condition (challenger/evidence/assessment/status present and citing a real matrix
> row), it is satisfied today and the reconciliation is correctly a `LIT-07` concern. That is the
> owner's call to make, not mine to resolve on their behalf — but I would not represent acceptance
> 1 as unqualifiedly Met without naming this gap explicitly at the point of close.

### The reconciliation, and the re-review that cleared it

On the owner's direction the fix ran here rather than at `LIT-07`. The item-0 text already
written into `PROMPT-029` was dispatched verbatim as the work, so this executed a governed prompt
early rather than authoring one — the distinction the pack's no-mid-campaign-authoring rule
exists to protect.

**First pass (`0d44f51`)** dropped `burns-groth` as H11's challenger and `eywa`/`burns-groth` as
H1's, dropped `log-is-the-agent` from H5 per its reviewer's finding that the paper's own §8
rejects the memory-retrieval category, added caveats to H9, and moved **H1 and H11 to
`POTENTIALLY_DISTINCT`** — taking the campaign from zero surviving distinctions to two.

**The coordinator sent it back (fix cycle 1 of 2).** Not for the direction, which moved against
the campaign's own thesis and was well argued, but for consistency: H1, H4 and H11 were in
materially the same evidential position — every candidate found had been inspected and none
demonstrated the mechanism at full scope — yet carried two different statuses. H11's new
strongest challenger scored component overlap **1** and was not a critical collision. And the
pass's own sentence, that both verdicts were "open to reversal by a further, more targeted search
this reconciliation did not perform", describes insufficient evidence. The dispatch was told to
state its rule and apply it uniformly, and not told which way to resolve.

**Second pass (`9329436`)** stated the rule — `POTENTIALLY_DISTINCT` requires not only that found
candidates fail but that the search behind that finding approaches saturation — and **converged
downward**: H1 and H11 back to `INSUFFICIENT_EVIDENCE`, H4 unchanged with a stated reason. Its
argument for converging that way rather than elevating H4: `bara` genuinely instantiates H4's
mechanism, formally and in closed form, merely at narrower scope, which is a stronger match than
anything left standing for H1 or H11; H11's remaining candidate was never the target of dedicated
search and H1 has had none in six phases.

Final distribution: **4 `LIKELY_ALREADY_KNOWN`, 4 `KNOWN_COMPONENT_NEW_INTEGRATION`, 3
`INSUFFICIENT_EVIDENCE`, 0 `POTENTIALLY_DISTINCT`.** The campaign returns to zero surviving
distinctions — but now by a stated, checkable rule rather than by default, and with three
hypotheses honestly parked rather than two carrying verdicts their evidence did not support.

### Independent re-review of acceptance 1 — **Met**

A second fresh reviewer checked only the failed condition. It verified the primary source itself:

> I fetched the actual `burns-groth` PDF (CAIS '26, Burns & Groth) and read it in full. Section 2
> says exactly: *"We are developing a feedback loop for iterative refinement… This closes the loop
> between curation experience and ontological design"* (present-progressive), and Section 6
> states: *"Our future work focuses on developing the virtuous cycle…"* Section 4 (Demonstration:
> job-hunt, tech-recon, DisMech) contains no instance of this loop running. This is exactly what
> `06`'s H11 block and `05`'s source-16 review now say — the original review's objection is
> accurately corrected, not just asserted.

On the question the coordinator flagged for it — whether a rule pushing hypotheses away from
distinctness is a thumb on the scale for H0:

> it only demands search-saturation evidence for a *negative/absence* claim ("the mechanism
> doesn't exist elsewhere"). It does not retroactively question `LIKELY_ALREADY_KNOWN` or
> `KNOWN_COMPONENT_NEW_INTEGRATION` verdicts, which rest on *positive* claims […] That asymmetry
> is a standard, correct epistemological distinction, not a selectively-applied escape hatch — and
> note that of the two possible directions this rule could have moved things, it moved H1/H11
> *away* from a status hostile to H0 (`POTENTIALLY_DISTINCT`) toward a genuinely neutral hedge
> (`INSUFFICIENT_EVIDENCE`), not toward a status that affirmatively supports H0. […] Declaring
> distinctness on a two-candidate, non-saturated search would have been the actual overclaim;
> walking it back to "we don't know yet" is the more conservative, defensible call.

It confirmed eleven blocks with five keys each, every status permitted, `NOVEL` and "no prior work
exists" only in the file's own rule prose, all thirteen cited `source_id`s present in the matrix,
the dated reconciliation note present, and both fix commits touching `06` alone. **"No
discrepancies found that block acceptance."**

One rough edge it recorded, not blocking: the rule's illustrative phrase at
`06_hypothesis_tests.md:36-38` holds up H4's single Pass 3 collision search as the example of a
search that would satisfy saturation, while the H4 block then says that same search is "thinner,
not thicker" and insufficient. The enforced bar is consistent; the abstract statement of it is
looser than the bar. Worth tightening in `phase-lit-07`, not a defect in the verdicts.

## The pre-synthesis check-in

**Held by the owner on 2026-09-14, ruling: proceed**, after `phase-lit-06`'s gate and within this
same session. `PROMPT-031` now carries the dated entry `LIT-07 K` requires. Eight rulings,
anchored on idea `000230`, each recorded on the idea that raised it.

Where a ruling changes how a gate or a dispatch behaves it was written into the document that
gate or dispatch actually reads, not only into the kickoff record — `LIT-07 G` reads the evidence
contract and the dispatches read the pack. That was itself ruling 7.

1. **The nineteen flags stand.** The six disputes where a reviewer re-derived a score one level
   lower and found no trigger fires are recorded, not applied. No score, `critical_collision` or
   `hypotheses_challenged` value changed, so `LIT-06 G`'s measurement 2 needs no re-run and
   `LIT-07` inherits a population of 19. (`000229`)
2. **A patent's whole published disclosure is prior art**, specification and claims together.
   Written into `PLAN-023.03`. This rejects the claims-only re-derivation applied to the patent
   row during this phase as using the wrong standard — claims-only is the test for infringement
   and validity, not for prior-art disclosure — so `us20250165226a1`'s architecture overlap of 4
   and its flag both stand. The rule the coordinator improvised was wrong, and saying so is the
   point of recording it. (`000227`)
3. **"Adjacent" means contiguous** — four consecutive stages, no gap. Written into
   `PLAN-023.03`. The loose reading inflates the collision count toward H0. (`000228`)
4. **`LIT-07 X1` reconciles `06_hypothesis_tests.md` as its item 0**, before writing 07. Written
   into `PROMPT-029`, naming H11 and H1 as known cases and telling the dispatch not to assume
   they are the only two. (`000225`)
5. **No row is re-read.** `Block D` instead gains a read-disclosure requirement: declare the
   range read and anything available but unread, and never code
   `NOT_DETERMINABLE_FROM_ACCESS` when reachable material answers the field. Written into
   `PROMPT-029`. (`000226`)
6. **The five recommended narrowings of `hypotheses_challenged` are recorded, not applied**,
   consistent with ruling 1.
7. **Behaviour-changing rulings go into the governing documents**, not the kickoff record alone.
8. **`phase-lit-07` must not claim saturation.** `LIT-06 G` measured 20.0% (44/220), recomputed
   independently and reproduced exactly; four results in five were new. `LIT-07 G` reports the
   trend and must not assert the stop condition holds.

## Decisions

**The coordinator drew a line the pack does not draw, and the owner kept it.** When nineteen
reviews returned and six said a flag should not stand, nothing in `PROMPT-029` said whether `X2`
could act on that. The line taken was: `X2` writes `second_review`, corrects factual errors, and
touches no score, no `critical_collision` and no `hypotheses_challenged`, because a score is a
judgment and the pack gave no dispatch authority over one. `X2` was told to say if that line was
wrong and said it was right — that the clean separation made nineteen rows tractable without
guessing whether a given correction was "factual enough". The owner then ruled the same way at the
check-in. The result is that thirteen disputes sit recorded and unapplied, which looks like
inaction and is not: the disagreement is the evidence, and resolving it inside a worker dispatch
would have destroyed the record of it.

**The owner overrode the coordinator's recommendation once, and was right to.** Asked what should
happen to the six flags, the recommendation was to drop five and let the patent follow the
patent-scoring ruling. The owner kept all nineteen. That is the better answer: dropping five would
have changed the population `LIT-06 G` had already measured, forcing a gate re-run, in exchange
for a count that `LIT-07` will revisit anyway.

**The patent rule the coordinator invented was wrong, and the check-in reversed it.** "Score the
claims, not the specification" went into a review dispatch as addressing. It is the test for
infringement and validity; for prior art, a published application's whole disclosure is public
knowledge regardless of what was claimed. The reviewer working under that rule re-derived
`us20250165226a1`'s architecture overlap from 4 to 3 and concluded its flag should fall. Under the
owner's ruling that re-derivation is rejected as applying the wrong standard, and the rule now
lives in `PLAN-023.03` where the next person to score a patent will read it.

**Rulings went into the governing documents, not only the kickoff record.** `PROMPT-031` wins by
precedence, but `LIT-07 G` reads the evidence contract and dispatches read the pack — a ruling
recorded only in the kickoff record would never reach them. So `PLAN-023.03` gained the patent
rule and the contiguous definition of "adjacent", and `PROMPT-029` gained Block D's
read-disclosure requirement and `LIT-07 X1`'s item 0. Amending a pack mid-campaign is normally
forbidden; these are owner rulings, attributed as such in each passage.

**The backlog regression was reported, not worked around.** Finding four phases reverted by a peer
commit, the session stopped and asked rather than restoring on its own judgment, because
`AGENTS.md` forbids resolving a `backlog.yaml` collision by taking one side wholesale and three of
the four had reached `complete` through the owner's own `/session-close`. The owner directed the
full restore.

## Corrections

**A worker claim was relayed without being fully checked, and the close review caught it.** `X2`
reported "42 factual corrections across 16 rows". The cell count was verified; the row count was
not. It is 15 rows. This is the exact failure mode this session spent the day guarding against in
others — the standing rule was to verify every worker claim against the file, and on this one
number it was relayed instead. Corrected in `## What was dispatched`, and named here rather than
quietly fixed.

**Two stale numbers in the verification block.** Governance and tracked-file counts were captured
before the session's last commit added a document, so they read 194/555 against a true 195/556.
Corrected.

**A gate reported a breakdown that inverted the phase's central finding.** `LIT-06 G` gave
measurement 2 as 10 confirmed / 9 disputed against a true 6 / 13. Its PASS was correct — the gate
tests `0 pending` — but the split would have told a reader the second reviews broadly upheld the
first assessment when they broadly did not. Caught by re-measuring rather than by reading, and
fixed in one cycle.

**`X1` asserted a process that does not exist.** Its preamble in `05` said `LIT-06 X2` folds
reviewer findings into `06_hypothesis_tests.md`. Nothing does. That sentence stated the writer gap
as though it were resolved, and would have told `LIT-07` that `06` already reflected the reviews.
Corrected in a fix cycle; `05` now says the opposite explicitly.

**`S1` wrote prose into two enum-valued fields.** One row carried a sentence in
`hypotheses_challenged` whose content was that the source challenges neither H3 nor H4 — but
`LIT-07 G` computes challenger counts from that field, so a consumer would have extracted "H3" and
"H4" from it and credited both, inflating the campaign's thinnest hypothesis in the direction that
flatters H0. Caught before it could propagate.

## Left undone

**The rule's own worked example is looser than the bar it enforces.**
`06_hypothesis_tests.md:36-38` offers H4's single Pass 3 collision search as the example of a
search that would satisfy saturation, while H4's own block then says that same search is "thinner,
not thicker" and insufficient. The verdicts are applied consistently; only the abstract statement
drifts. Left for `phase-lit-07` rather than spending this work item's second fix cycle on wording.

**`LIT-07 X1`'s item 0 is now redundant in practice and was deliberately left in the pack.** Every
pack section is idempotent by design — output that already exists is verified against its contract
and extended from the first missing item, never re-created — so on re-dispatch it verifies a
reconciliation that has already happened. Removing it would have been the more fragile choice.

**Six flags stand that six reviewers say should not.** Recorded as disputes, unapplied, by ruling.
`LIT-07 X1` weighs them when building the anti-novelty case, and `LIT-07 G` counts a population of
19 rather than 13.

**The campaign is not saturated and the next phase cannot fix that.** 20.0% duplicate rate, four
results in five new. `phase-lit-07` is synthesis, not search, so the number will not improve;
ruling 8 forbids claiming otherwise. If saturation matters for the memo's standing, that is an
eighth session, not a paragraph.

**Three findings outlive this phase.** `000221` — the contract still names `LIT-06 X2` as
`second_review`'s sole writer while the flagging dispatch writes `pending`. `000148` — the
`source_type` enum has no bucket for a patent, dissertation, whitepaper or software library, all
of which are in the matrix. `000224` — the backlog regression is repaired on this branch, but a
phase silently dropping from `complete` to `queued` still fails no check, and the only reason this
one was found is that a session happened to rebase and notice its own claim missing.

## Resume state

**Current phase**: `phase-lit-06`, `active`, gate-measured and passing, left active for the
owner's `/session-close`. An agent never marks a phase complete.

**Next**: `phase-lit-07` — Pass 4, synthesis. It is **unblocked**: `PROMPT-031` carries the dated
check-in entry `LIT-07 K` refuses to dispatch without. It was deliberately not started in this
session; the owner directed that the check-in be resolved, not that synthesis begin.

**A fresh session must read**: `AGENTS.md`, `GOV-006`, `PROMPT-031` — including its check-in
entry and the eight rulings — then `PROMPT-030`, then this record. `LIT-07`'s item order is
`K → X1 → X2 → X3 → A → G`, and `X1` now begins by reconciling `06` rather than by writing 07.

**Still open, and not resolved by the check-in**:

- `000221` — the evidence contract still names `LIT-06 X2` as `second_review`'s sole writer while
  the flagging dispatch writes `pending`. Ruling 4 closed the writer gap for `06`, not this one.
- `000148` — the `source_type` enum still has no bucket for a patent, a dissertation, a
  whitepaper or a live software library, all of which appear in the matrix.
- `000224` — the backlog regression was restored on this branch, but nothing prevents a
  recurrence: a phase silently regressing from `complete` to `queued` fails no check.

**Branch**: `agent/lit-campaign`, rebased onto `dev` at this boundary, clean, governance 0, 580
tests passing. Not integrated — the first of the two owner integrations `PLAN-023` schedules
falls at this check-in and remains the owner's to make. Review with
`git diff dev..agent/lit-campaign`.
