---
schema_version: 1
id: doc-prompt-literature-review-kickoff
code: PROMPT-031
title: Literature-review campaign kick-off record — the pinned starting state, the owner's per-campaign deltas, and the kick-off paragraph
kind: prompt
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-20'
systems:
- sys-research
- sys-backlog
depends_on:
- doc-prompt-literature-review-coordinator
- doc-lit-campaign
- doc-research-protocol
---

# Literature-review campaign kick-off record

The kick-off record for the adversarial D-System literature-review campaign
([GOV-009](../08-governance/GOV-009-research-protocol.md) stage 8). It pins the state the
campaign starts from, carries the owner's per-campaign rulings, and ends with the kick-off
paragraph.

**Precedence: where this record and the coordinator prompt
([PROMPT-030](PROMPT-030-literature-review-coordinator.md)) differ, this record wins.** The
coordinator prompt is generic and reusable across every session; this record is specific to this
campaign and is the later, narrower instrument.

## Pinned starting state (2026-09-12)

- **Repository**: branch `dev` at `74fbeae`, clean tree, governance exits 0 (19 systems, 181
  documents, 129 backlog phases), 578 tests passing.
- **The campaign branch does not exist yet.** `phase-lit-01`'s kickoff creates
  `agent/lit-campaign`; every phase commits to that one branch thereafter.
- **Queue**: `phase-lit-01` is in `next_up`, in **last** position — behind `phase-wb-07`,
  `phase-port-02` and `phase-ses-01`. It is promoted, not prioritised: ratified decision 4 gives
  demo work precedence, and `phase-wb-07` is demo work.
- **Peer claims**: one active claim, `phase-demo-07` (`agent-demo-glossary`), locking `sys-brain`
  and `sys-portfolio`. No overlap with the campaign's `sys-research`. One of three claim slots in
  use.
- **Phase state**: all seven `phase-lit-01`–`phase-lit-07` are `queued`, each declaring
  `systems: [sys-research]`, dependency-chained so Pass 1 → 2 → 3 → 4 is forced.
- **The frozen baseline's identity**, as the campaign must find it:
  - last modified by commit `b2b564b` (2026-09-09) — nothing has touched it since;
  - `research/pre-literature-baseline.md` = blob `635bcfa`;
  - `research/pre-literature-hypotheses.yaml` = blob `a53ecdb`;
  - `research/adversarial-codebase-review/` — the twelve-file audit, unmodified.
  A baseline whose identity differs from this is a blocking finding, not something to restore.
- **Deadline**: none. The live demo is the week of 2026-09-15 and the campaign is not
  demo-critical; it runs alongside demo prep and yields to it (ratified decision 4). Runway is
  seven sessions, range six to eight.
- **No campaign deliverable exists yet.** `research/literature-review/` holds only the
  methodology (`CLAUDE.md`) and the handoff note; `00_search_ledger.csv` and everything numbered
  `01`–`13` are created by the campaign itself.

## The owner's per-campaign deltas (ratified 2026-09-12)

These four are this campaign's deltas on the standing rules. Prompt A's seven ratified decisions
([PROMPT-027](PROMPT-027-literature-review-pre-plan-package.md)) remain in force and are not
restated here.

1. **Gate check-in cadence: one pause, before synthesis.** The evidence phases run through
   without waiting. The campaign pauses once, after `phase-lit-06`'s gate and before
   `phase-lit-07` starts. `phase-lit-07` may not start until this record carries a dated entry of
   the form `pre-synthesis check-in held: <date>, ruling: proceed` — appended to the section at
   the end of this document, which is empty by construction until the check-in happens. That
   pause is also the first of the two owner integrations of `agent/lit-campaign` into `dev`.

   A critical issue outside that gate — a collision that falsifies scope, a methodology defect
   invalidating collected evidence — gets `GOV-009`'s dual adversarial review first, and pauses
   the campaign only if it survives that review unresolved.

2. **Descope authority: rung 1 is autonomous; rungs 2–5 are not.** The coordinator may take
   **rung 1** (fold near-synonym domains into their parents for Pass 1 breadth, with that rung's
   gate re-parameterization) on its own judgment if Pass 1 overruns, and reports it afterward in
   the session record. Every other rung needs the owner's explicit direction. This is the stated
   exception `GOV-009` permits a kick-off record to grant; it does not extend to any other rung,
   and a rung taken without its gate re-parameterization is a defect, not a descope.

3. **The single Opus escalation is the coordinator's to spend, documented.** `GOV-009` allows at
   most one Opus escalation per campaign, never pre-assigned. The coordinator may spend that one
   on its own judgment where a judgment-heavy step genuinely needs it, and must name it in the
   session record — which work item, why, and what it changed. A second escalation needs the
   owner.

4. **Start: `phase-lit-01` is promoted to `next_up` now**, in last position (see the pinned state
   above). The campaign begins whenever a session picks it up; nothing further is needed from the
   owner to start it.

## What this record deliberately does not do

It does not restate the content methodology, the phase graph, the delegation-pack sections or the
completion gate. Those live in the campaign plan
([PLAN-023](../01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md)), the
delegation pack ([PROMPT-029](PROMPT-029-literature-review-delegation-pack.md)) and the
coordinator prompt. A kick-off record that duplicates them becomes a second source of truth to
keep consistent, which is the failure `GOV-009`'s precedence rule exists to contain.

## Pre-synthesis check-in

The coordinator appends the dated ruling here when the check-in is held, and `LIT-07 K` reads
this section to decide whether synthesis may start. A description of the planned pause is not a
held check-in.

```text
pre-synthesis check-in held: 2026-09-14, ruling: proceed
```

Held after `phase-lit-06`'s gate, by the owner, in the session recorded as
[SESS-2026-09-14-01](../03-sessions/SESS-2026-09-14-01-literature-review-pass-3.md). Eight
rulings, anchored on idea `000230`. They are recorded here because this record wins over the
coordinator prompt; where a ruling changes how a gate or a dispatch behaves it was also written
into the document that gate or dispatch actually reads, as noted.

1. **The nineteen critical-collision flags stand.** Six reviewers re-derived a score one level
   lower and concluded no trigger fires; those are recorded as `disputed` in `second_review` and
   in `05_critical_collisions.md`, and no score, `critical_collision` or `hypotheses_challenged`
   value was changed. `LIT-06 G`'s measurement 2 therefore needs no re-run. Idea `000229`.
2. **A patent's whole published disclosure is prior art** — specification and claims together.
   Written into `PLAN-023.03`. This rejects the claims-only re-derivation applied to
   `us20250165226a1-ai-digital-thread-patent` during `phase-lit-06` as using the wrong standard;
   that row's architecture overlap of 4 and its flag both stand. Idea `000227`.
3. **"Adjacent" in the fourth flag trigger means contiguous** — four consecutive stages, no gap.
   Written into `PLAN-023.03`. Idea `000228`.
4. **`LIT-07 X1` reconciles `06_hypothesis_tests.md` against the corrected matrix before writing
   anything else**, as its item 0. Written into `PROMPT-029`. H11's and H1's named challengers
   are known to need it. Idea `000225`.

   **Superseded at `phase-lit-06`'s close, same day.** The independent close review judged the
   phase's first acceptance condition **Not Met** on exactly this gap — `06` presented two of
   eleven verdicts on evidence the campaign's own adversarial control had shown to misread the
   source, with no in-document flag. The owner then directed that the reconciliation run inside
   `phase-lit-06` rather than wait for `LIT-07`, so the phase could close on an accurate
   deliverable. The item-0 text was dispatched early, verbatim, as the work.

   `LIT-07 X1` item 0 **remains in the pack and is not removed**. Every pack section is
   idempotent by design — output that already exists is verified against its contract and
   extended from the first missing item, never re-created — so on re-dispatch it verifies a
   reconciliation that has already happened. That is the intended behaviour, not a redundancy.
5. **No row is re-read.** The 42 factual corrections already landed and the scores stand under
   ruling 1. Instead `Block D` now requires a deep-extraction dispatch to declare what it
   actually read and what it could have read but did not. Written into `PROMPT-029`. Idea
   `000226`.
6. **The five recommended narrowings of `hypotheses_challenged` are recorded, not applied** —
   consistent with ruling 1. `LIT-07 X1` weighs them when it reconciles 06.
7. **Rulings that change behaviour are written into the documents that govern it**, not only
   here, because `LIT-07 G` reads the evidence contract and the dispatches read the pack.
8. **Saturation is not demonstrated and `phase-lit-07` must not claim it.** `LIT-06 G` measured
   a 20.0% duplicate rate (44/220), recomputed independently and reproduced exactly. Four
   results in five were new. The methodology's stop condition is that additional searches
   "mostly yield duplicates or clearly adjacent work"; 20% is not that. `LIT-07 G`'s saturation
   measurement reports the trend and must not assert the condition holds.

   **Extended, not overturned, by the 2026-09-20 ruling below** (*How `phase-lit-07` closes*):
   saturation still may not be asserted, and `phase-lit-07` may now close while reporting that it
   is unmet.

Not a ruling, recorded because it bears on the runway: the campaign has used six sessions of a
seven-session estimate, against an owner-accepted range of six to eight. `phase-lit-07` is the
seventh.

## The `phase-lit-08` dispatch mapping (owner ruling, 2026-09-14)

A separate, later ruling — **not part of the pre-synthesis check-in above**, which was held
before `phase-lit-08` existed. It is recorded in its own section so a reader looking for what
the check-in decided does not find an unrelated ruling mixed into it.

`phase-lit-08` (Pass 3b, the targeted collision search for H1, H4 and H11) was created after the
check-in, in [SESS-2026-09-14-04](../03-sessions/SESS-2026-09-14-04-lit-06-followups.md). The
delegation pack ([`PROMPT-029`](PROMPT-029-literature-review-delegation-pack.md)) has no
`LIT-08` section, and the pack's own rule makes a missing prompt a blocking finding for the
owner rather than something a coordinator improvises. The coordinator stopped on that finding
and the owner ruled the mapping below rather than have a new section authored mid-campaign.

**Every item is existing pack text with a narrowed payload. No section was authored.**

| Item | Model | Pack section dispatched | Payload narrowing |
|---|---|---|---|
| `K` | Haiku | `LIT-06 K` | Claims `phase-lit-08`; item order as below |
| `S1`, `S2`, `S3` | Sonnet | `LIT-06 S1` (Block C + Block S) | **One dispatch per hypothesis** — `S1`=H1, `S2`=H4, `S3`=H11. Search and log only |
| `X1`, `X2`, `X3` | Sonnet | Block C + **Block D** + the source ids its paired `S` nominated | Deep-extraction of genuinely new strong candidates only |
| `R` ×n | Sonnet | `LIT-06 R`, verbatim | One per **new** `critical_collision: yes` row; none if none flags |
| `X4` | Sonnet | `LIT-06 X2` | Folds the new `R` verdicts only; runs only if `R` ran |
| `X5` | Sonnet | `LIT-06 X1` | **Restricted to the H1, H4 and H11 blocks** of `06_hypothesis_tests.md`; the other eight are untouched, and the `05_critical_collisions.md` drafting half is skipped because `05` already exists and is fully reviewed |
| `G` | Haiku | Block G | Measurements are `phase-lit-08`'s four acceptance conditions |

Item order: `K → S1 → X1 → S2 → X2 → S3 → X3 → R×n → X4 → X5 → G`.

The three choices the owner made, and why each was a choice rather than a default:

1. **`X5` is `LIT-06 X1`, not `LIT-06 X2`.** `X1` authored `06_hypothesis_tests.md` and knows its
   block format and its saturation rule. `X2`'s charter was deliberately kept narrow at
   `phase-lit-06` — it writes review outcomes and nothing else — and re-deriving a hypothesis
   status is a judgment, not a review outcome. Widening `X2` would undo the separation that made
   nineteen rows tractable.
2. **Three `S` dispatches, one per hypothesis, not one across all three.** `LIT-06 S1` dispatched
   once across all eleven hypotheses and produced 30 rows — two or three per hypothesis. That
   dilution is the reason this phase exists, so reproducing its shape would reproduce its result.
3. **Extraction is a separate Block D dispatch, not inline in `S`.** `LIT-06 S1`'s own text folds
   extraction into the search dispatch, but an `S` dispatch assembles Block C + Block S and never
   receives Block D — so the read-disclosure requirement added by check-in ruling 5 would not
   reach the agent doing the extraction. A searcher scoring its own finds is the configuration
   that produced Pass 2's one-directional depth defect.

Check-in rulings 1, 2, 3, 5 and 8 bind this phase unchanged. Ruling 8 in particular: this phase
**reports its duplicate rate against `phase-lit-06`'s 44/220 (20.0%) as a trend and may not
assert saturation**, whatever the number comes out at.

## The `phase-lit-09` dispatch mapping (owner ruling, 2026-09-14)

A third, still later ruling, separate from both sections above. Made at the close of
`phase-lit-07` (the session recorded as
[SESS-2026-09-14-13](../03-sessions/SESS-2026-09-14-13-literature-review-pass-4.md)), when the
owner approved a ninth session — one past the seven-session estimate, at the top of the accepted
six-to-eight range — to close the three evidence gaps that session's final gate measured, plus
the clean-room H4 re-derivation the owner elected to include. `phase-lit-09` carries the scope
and acceptance; this section carries the dispatch mapping, because the pack has no `LIT-09`
section and nothing is authored mid-campaign.

**Every item is existing pack text with a narrowed payload. No section was authored.**

| Item | Model | Pack section dispatched | Payload narrowing |
|---|---|---|---|
| `K` | Haiku | `LIT-06 K` | Claims `phase-lit-09` under a distinct agent id (`agent-lit` still holds `phase-lit-07`); verifies prior evidence; item order as below |
| `C1` | Sonnet | `LIT-05 S1` (forward chaining) | Payload = every matrix row with either overlap score ≥ 3 lacking a `strategy_phase: C` row carrying its id in `subject_source_id`, derived from the files at dispatch (15 at ruling time) |
| `B1` | Sonnet | Block C + Block D | Payload = the ids lacking `strategy_phase: B` rows (5 at ruling time). Idempotent re-dispatch: the matrix rows exist and are verified; the work extends from the first missing item — the backward-chaining rows. No re-scoring |
| `X1`/`X2`/`X3` | Sonnet | Block C + Block D (as `LIT-04 X1`–`X3`) | Payload = the unread top-band candidates in rank order — `collision_candidate: yes`, max of the two prescores = 5, no matrix row, deduplicated (20 at ruling time), split roughly evenly. Commit per source |
| `R` ×n | Sonnet | `LIT-06 R`, verbatim | One per **new** `critical_collision: yes` row; none if none flags |
| `X4` | Sonnet | `LIT-06 X2` | Folds the new verdicts only; runs only if `R` ran |
| `X5` | Sonnet | `LIT-06 X1` | Restricted to hypothesis blocks the new evidence bears on; explicit statement where a status does not change; other blocks byte-identical |
| `H4R` | Sonnet | `LIT-06 X1` | Restricted to the **H4 block only**, dispatched to a fresh agent. **The dispatch carries no coordinator characterization of any source** — nothing about any specific challenger, nothing about a general/topological split: Block C, the section text and file paths, nothing else. Resolves the `phase-lit-08` framing caveat in whichever direction the evidence supports |
| `G` | Haiku | Block G | Measurements are `phase-lit-09`'s five acceptance conditions plus ledger/matrix integrity re-measures, populations named |

Item order: `K → C1 → B1 → X1 → X2 → X3 → R×n → X4 → X5 → H4R → G`.

Operational facts that bind, carried from the session records rather than re-derived: the
ledger's `result_ids` delimiter is the semicolon alone; ledger rows are CRLF-terminated and this
phase's `search_id`s are `LIT-09-S001` onward, numbered per phase; the inventory carries two
known duplicate `source_id` rows and four rows still `status: candidate` despite having matrix
rows — payload derivations dedupe, and nobody "fixes" the inventory. Check-in rulings 1, 2, 3, 5
and 8 bind unchanged. Ruling 8 in particular: this phase **reports its duplicate rate against
`phase-lit-08`'s 58/387 (15.0%) as a trend and may not assert saturation**, whatever the number
comes out at. `phase-lit-07` remains `active` under `agent-lit` throughout and is revisited by
the owner after this phase's gate re-measures `LIT-07 G`'s measurements 2, 4 and 5.


## How `phase-lit-07` closes (owner ruling, 2026-09-20)

A fourth ruling, later than all three sections above and separate from each. It gets its own
section for the reason the `phase-lit-08` mapping gives: a reader looking for what the
pre-synthesis check-in decided on 2026-09-14 must not find a 2026-09-20 ruling mixed into it. It
**extends check-in ruling 8 rather than overturning it** — saturation is still not demonstrated and
still may not be asserted.

Made at the owner's revisit of `phase-lit-07`'s close, after `phase-lit-09`'s gate re-measured
`LIT-07 G`'s measurements 2, 4 and 5. The full reasoning is in
[SESS-2026-09-19-08](../03-sessions/SESS-2026-09-19-08-literature-review-pass-3c.md)'s addendum;
this section is the authoritative copy, because `LIT-07 G` and any future coordinator read this
record and not one session record among 120.

9. **The campaign closes as a first research memo with saturation measured and explicitly not
   demonstrated.** `phase-lit-07` may close while reporting a stop condition it has not met,
   provided it reports it honestly and names the population each measurement was taken against.

   This is the permission ruling 8 withheld. Ruling 8 forbids *asserting* saturation and says
   nothing about closing without it, which left the phase's stop-conditions acceptance unclaimable
   as written — exactly the gap `phase-lit-07`'s 2026-09-14 close review found when it judged that
   half **Not Met**. The ruling closes the gap in the acceptance, not in the evidence.

   It introduces no new doctrine. [`PROMPT-030`](PROMPT-030-literature-review-coordinator.md)
   already states that the campaign "produces a **first research memo**. It does not establish
   final novelty, and no close-out may claim it does."

10. **Do not commission a tenth search session.** The duplicate rate has fallen at every
    measurement — **20.0% (`phase-lit-06`, 44/220) → 15.0% (`phase-lit-08`, 58/387) → 6.4–7.7%
    (`phase-lit-09`, 25–30/392)**. The methodology's stop condition is that additional searches
    "mostly yield duplicates or clearly adjacent work"; more than nine results in ten are new. On
    this trend a tenth session would lower the rate again — spending a session to move further from
    the condition it was spent to satisfy, and taking the campaign to ten sessions against an
    owner-accepted range of six to eight.

    `phase-lit-09` was the ninth session and closed two of the three gaps `LIT-07 G` measured:
    measurement 2 now measures 0 missing forward-chaining and 0 missing backward-chaining rows
    across 53 strong rows, against the 15 and 5 it recorded, and the deep-read condition is met by
    coverage with 0 of 32 top-band candidates unread rather than by count alone. Saturation is the
    one that remains, and it moved further out of reach.

**What this changes in the documents a gate reads.** `phase-lit-07`'s acceptance in
`docs/09-backlog/backlog.yaml` is amended in the same change that records this ruling, so its
stop-conditions half requires each condition **measured with its population named**, and saturation
**reported as a trend**, in place of requiring the conditions to hold. Its scope and its first
acceptance condition are unchanged. `LIT-07 G` itself is unchanged: it already takes eight
measurements and already reports saturation as a trend under ruling 8.

---

## The kick-off paragraph

Paste this into a fresh terminal session to run one session of the campaign. It is the one
artifact `GOV-009` never governs and never tracks; this record is its durable copy.

> Run one execution session of the D-System adversarial literature-review campaign. Read
> `AGENTS.md`, then `docs/08-governance/GOV-006-conversation-guidelines.md`, then the kick-off
> record `docs/02-prompts/PROMPT-031-literature-review-kickoff.md` — it carries the pinned
> starting state and the owner's four per-campaign deltas, and it wins wherever it differs from
> the coordinator prompt — and then the coordinator prompt
> `docs/02-prompts/PROMPT-030-literature-review-coordinator.md` in full.
>
> You are the coordinator. Run the preflight and record the real output. Determine the current
> phase from `docs/09-backlog/backlog.yaml` — the first `queued` `phase-lit-*` whose dependencies
> are complete, or the `active` one if this is a resume. Dispatch that phase's sections from the
> delegation pack `docs/02-prompts/PROMPT-029-literature-review-delegation-pack.md` verbatim, one
> at a time, assembled per its dispatch rules, in the order the pack lists them.
>
> You coordinate and verify. You do not search, read sources, score collisions, write
> deliverables or findings, author prompts, or fix a worker's output. A missing prompt is a
> blocking finding for the owner. A failing gate is a result to record, not a retry loop. The
> campaign works to support H0 — that D-System is primarily a recombination of known ideas — and
> no agent may mutate a hypothesis or rewrite scope to avoid a collision.
>
> Stop at the phase boundary: checkpoint, write the session record with the gate measurements and
> spend posture, state the resume state, and leave the tree clean with governance exiting 0. Do
> not mark the phase complete and do not integrate into `dev` — both are the owner's.
