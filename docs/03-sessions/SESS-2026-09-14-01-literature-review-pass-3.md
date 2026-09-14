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
Governance OK: 20 systems, 194 documents, 22 memories, 133 backlog phases
exit 0
```

`uv run python tools/check_no_private_content.py`, with changes staged

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is
expected in CI / a fresh clone)
check_no_private_content: OK (555 tracked files, 0 identifiers checked)
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
  a status from the permitted vocabulary, each traceable to evidence-matrix rows** — **Met at the
  time of writing, now qualified.** Gate measurement 1 confirms all eleven blocks with permitted
  statuses and non-empty challengers. But the second reviews that ran afterwards materially
  undercut two of those challengers (H11's and H1's), and no dispatch in this phase owns `06`.
  See *Unresolved*.
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
`05`, plus 42 factual corrections across 16 rows. Changed no score, no `critical_collision` and
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
