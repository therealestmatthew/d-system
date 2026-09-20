---
schema_version: 1
id: doc-session-literature-review-pass-3c
code: SESS-2026-09-19-08
title: Literature review Pass 3c — chaining completion, top-band deep reads and the clean-room H4 re-derivation
kind: session
status: active
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-19'
systems:
- sys-research
depends_on:
- doc-lit-campaign
---

# Literature review Pass 3c — chaining completion, top-band deep reads and the clean-room H4 re-derivation

## Phase

`phase-lit-09` — Literature review Pass 3c: chaining completion, top-band deep reads and the
clean-room H4 re-derivation. Claimed under `agent-lit-3c`; `agent-lit` still holds `phase-lit-07`'s
history but its claim was released to `queued` to free `sys-research` (see `## Unresolved`).

## Verification

`uv run python -m src.governance`

```text
Governance OK: 35 systems, 295 documents, 26 memories, 288 backlog phases
```

Exit code 0.

`uv run python tools/check_no_private_content.py` with the changes staged, run in the worktree:

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (736 tracked files, 0 identifiers checked)
```

Exit code 0. **This is a path check and not a content verification** — `_private/` is gitignored and
absent from a worktree, so the tool built an empty identifier list. The real check ran in the
primary checkout on both `dev` commits this session and reported `OK (736 tracked files, 31
identifiers checked)`.

The phase gate, run per the `PROMPT-031` `phase-lit-09` mapping as item `G` on Haiku, measurements
below with their populations named. `G` needed one fix cycle: its first measurement 2 reported FAIL
after deduplicating on the `dedup_of` column, which is `none` on every row in that population and so
removed nothing. Re-measured across three identity keys it passes. The first figure is recorded here
as an artifact of the measurement rather than a defect in the files.

| Gate measurement | Population | Result |
|---|---|---|
| Chaining coverage | 53 matrix rows scoring >= 3 on either overlap scale, of 67 | 0 lacking `strategy_phase: B`; 0 lacking `strategy_phase: C` |
| Top-band coverage | 32 inventory rows, `collision_candidate: yes`, max prescore 5 | 30 resolved by `source_id`, 1 by normalised identifier, 1 by citation identity; 0 genuinely lacking a matrix row |
| Blank cells | 43 fields x 67 rows = 2,881 cells | 0 blank |
| Second reviews | 30 `critical_collision: yes` rows | 12 confirmed, 18 disputed, 0 pending |
| Duplicate rate | 392 result identifiers across 105 `LIT-09` searches, against the pre-phase inventory of 1,123 rows | 25-30/392 = 6.4-7.7% (see the correction below) |
| Ledger integrity | 1,200 data rows | field counts `{15: 1200}`; 1,201/1,201 CRLF; `LIT-09-S001`-`S105` contiguous |
| Matrix integrity | 67 data rows | field counts `{43: 67}`; LF throughout, 0 CRLF |
| Inventory integrity | 1,154 data rows | field counts `{13: 1154}` |
| Hypothesis blocks | H1-H11 in `06_hypothesis_tests.md` | 11 present, each with a permitted status; summary table matches every block |

`LIT-07 G` measurements 2, 4 and 5, re-measured against the updated files for the owner's revisit of
`phase-lit-07`'s close:

- **Measurement 2** — strongest collisions carry both chaining phases: **0 missing**, against the 15
  lacking phase C and 5 lacking phase B that `phase-lit-07`'s gate measured.
- **Measurement 4** — matrix rows 20-30, no blank required fields: the matrix holds **67 rows**, past
  the 20-30 band, with **0 blanks across 2,881 cells**. The band was `phase-lit-05`'s stop condition
  and the campaign has continued past it; the real count is reported rather than the band's expectation.
- **Measurement 5** — saturation trend: **20.0% (`phase-lit-06`) -> 15.0% (`phase-lit-08`) -> 6.4-7.7%
  (this phase)**. The rate is **falling**. Per check-in ruling 8 the trend is reported and saturation
  is not asserted; on this evidence it is not demonstrated either, and more than nine results in ten
  were new.

Close gates, not part of the phase's `verification` list but required by `/session-close` step 7:

```text
uv run python -m src.governance      -> Governance OK: 35 systems, 296 documents, 26 memories, 288 backlog phases   (exit 0)
uv run pytest                        -> 638 passed, 2 warnings                                                      (exit 0)
```

## Acceptance

1. **Met.** Every matrix row scoring >= 3 on either overlap scale, including the 18 added this phase,
   carries both a `strategy_phase: B` and a `strategy_phase: C` ledger row with its id in
   `subject_source_id` — 0 missing on each across 53 rows, per the gate's chaining measurement.
2. **Met.** All 32 top-band candidates resolve to a full 43-field matrix row once identity is resolved
   across `source_id`, normalised identifier and citation identity; 0 blank cells across 2,881; every
   new `critical_collision: yes` row carries a recorded second review, 0 pending.
3. **Met.** H4 was re-derived by item `H4R` under a clean-room protocol, its derivation recorded before
   any prior H4 narrative was opened, with the reasoning written into the block. Status moved from
   `KNOWN_COMPONENT_NEW_INTEGRATION` with an `INSUFFICIENT_EVIDENCE` split to a single
   `LIKELY_ALREADY_KNOWN`. The caveat is resolved and propagated into `08_surviving_distinctions.md`,
   where H4 now sits as one Category 1 entry instead of two entries split across Categories 2 and 3.
4. **Met, after a correction the close review forced.** The rate as first recorded — 67/642 = 10.4% —
   was wrong: `G` split the ledger's `result_ids` on commas as well as semicolons, manufacturing
   tokens out of author lists and titles inside a single identifier. The delimiter is the semicolon
   alone, and `phase-lit-08`'s close review had already diagnosed this exact defect. Corrected, the
   denominator is **392**; the numerator is 25 or 30 depending on how a prose-wrapped identifier is
   resolved, giving **6.4-7.7%**, measured against the pre-phase inventory of 1,123 rows and reported
   against `phase-lit-08`'s 58/387 = 15.0% as a trend. No saturation assertion is made in either
   direction, per check-in ruling 8. The correction lowers the rate rather than reversing its
   direction: duplicates are rarer than first reported, so saturation is further from demonstrated,
   not closer.
5. **Met.** `LIT-07 G` measurements 2, 4 and 5 are re-measured against the updated files and recorded
   in `## Verification` above. Measurement 5 carries the corrected duplicate rate; measurements 2 and
   4 were confirmed unchanged by the independent close review's own reruns.

All five conditions are met on the evidence recorded here, condition 4 only after the correction the
independent review forced. With the owner's approval for integration given on 2026-09-20, all three
`GOV-003` coordinator-completion conditions hold and the phase reached `status: complete`.

## Backlog

`phase-lit-09` — `status: complete`, `agent: agent-lit-3c`, removed from `next_up` in the same
change. Completed under `GOV-003`'s coordinator-completion rule, all three conditions holding:
verification green with real output recorded above; an independent non-fork review run, whose one
blocking finding was fixed and whose findings are recorded verbatim in `## Review`; and integration
onto `dev` with the owner's approval, given 2026-09-20.

`next_action`: All five acceptance conditions measured Met; ready for the owner's `/session-close`
review. Two open findings are recorded below and are not this phase's to fix: ten stale H4 references
in `07_anti_novelty_case.md`, and two duplicate inventory rows. `phase-lit-07` was released to
`queued` this session and awaits the owner's scoping decision, now informed by this phase's
re-measures.

`completion_evidence`: `research/literature-review/00_search_ledger.csv` (1,200 rows,
`LIT-09-S001`-`S105`), `03_source_inventory.csv` (1,154 rows), `04_evidence_matrix.csv` (67 rows),
`05_critical_collisions.md` (30 sections), `06_hypothesis_tests.md` (11 blocks),
`08_surviving_distinctions.md` (H4 in Category 1).

`result`: 105 searches logged, 19 top-band sources deep-read, 31 new inventory rows, 18 new matrix
rows, 6 independent second reviews. Chaining coverage closed to 0 missing on both phases. H4
re-derived clean-room to `LIKELY_ALREADY_KNOWN`. Duplicate rate 10.4%, falling.

## Unresolved

- **Ten stale H4 references in `07_anti_novelty_case.md`** — lines 168, 192, 195, 196, 198 and 202 in
  its Truth Discovery section, including a now-superseded caveat note, and lines 422, 453, 455 and 461
  in its synthesis summary, where a "nine of eleven" count and an item about "H4's graph-topological
  reading specifically" both describe a split that no longer exists. `07` is a `phase-lit-07`
  deliverable and was deliberately left outside this phase's declarations. Awaiting the owner's routing.
- **Two duplicate inventory rows, deliberately not repaired.**
  `epistemic-sybil-resistance-multiplying-agents-2026` duplicates
  `epistemic-sybil-resistance-bara-2026` (both `arxiv:2609.01873`), and
  `dhar-vaidhyanathan-varma-agenticakm-2026` duplicates `dhar-vaidhyanathan-varma-agenticakm-2026-arxiv`
  (same title and authors; a ResearchGate URL against `arxiv:2602.04445`). Both duplicates carry
  `status: candidate` while their matrix rows are `deep_read`. These made the unread top-band count
  read 20; the coordinator's dispatch-time derivation resolved one of the pair and put it at 19, and
  the independent close review established the genuinely-unread figure was **18**, since both pairs
  already carried matrix rows on `dev` before this phase began.
- **Nine identity-on-the-wrong-key defects were found this phase**, each reported and none repaired:
  the two duplicate pairs above; a matrix row citing a repository owner path that 404s; a row citing an
  arXiv record showing 0 citations where the published record shows 6; a `derivative_ancestor` naming
  a paper that does not exist as described; a Semantic Scholar record conflating a 1981 DBLP id with a
  1984 DOI; an inventory citation carrying a companion paper's five-author list against Crossref's
  four; a working-group page whose link to its own predecessor 404s; and a quoted sentence in a matrix
  field that appears nowhere in its source. Every one ran in the direction of making evidence look
  thinner or a lineage look cleaner than it is.
- **Five of six second reviews came back `disputed`, three concluding no trigger fires.** Under
  check-in ruling 1 no score, flag or `hypotheses_challenged` value was changed; the disputes are
  recorded with both positions visible. Whether those three flags should stand is the owner's, not
  this phase's.
- **`phase-lit-07` was released from `active` to `queued`** to free `sys-research`, with its scope,
  acceptance and `next_action` untouched. It had failed acceptance 2 at its 2026-09-14 close review
  and was awaiting an owner scoping decision with nobody working it; `AGENTS.md` returns such a phase
  to `queued` and releases the agent claim.
- **Saturation remains undemonstrated**, and this phase moved the number away from demonstrating it.

## Review

An independent, non-fork sub-agent reviewed the 24-commit range `dev...agent/lit-campaign` against
the phase's `acceptance` list, running every verification command itself. It was given the phase's
scope, acceptance and verification lists verbatim, the commit range, the session record, and an
explicit disclosure of all three deviations from written scope, with instructions to judge each on
its merits rather than accept the coordinator's framing. Its findings, condition by condition:

> Summary up front: **four of five acceptance conditions hold; the fifth does not, because the phase
> gate's headline number is wrong** — the same delimiter bug this campaign already found and fixed in
> `phase-lit-08` reappeared in `phase-lit-09`'s own gate and was not caught this time.

**Verification commands, rerun by the reviewer.** `uv run python -m src.governance` -> `Governance OK:
35 systems, 296 documents, 26 memories, 288 backlog phases`, exit 0. The record said 295 documents;
the reviewer traced the difference to the session-record commit itself adding one governed document
after the record's own measurement was taken, and judged it not a discrepancy. The private-content
check in the worktree returned `OK (737 tracked files, 0 identifiers checked)`, exit 0; the reviewer
additionally ran it from the primary checkout, where `_private/portfolio/` exists, and got
`OK (738 tracked files, 31 identifiers checked)`, corroborating the record's claim. Independently
computed file integrity: ledger 1,200 data rows, uniform 15 fields, 1,201/1,201 CRLF, 0 bare LF;
matrix 67 data rows, uniform 43 fields, 0 CR bytes.

**1. Chaining coverage — Met.** The reviewer computed the population itself: 53 of 67 rows scoring
>= 3 on either scale, joined against the ledger's `strategy_phase` and `subject_source_id`. 0 missing
`B`, 0 missing `C`. Matches the record exactly.

**2. Top-band coverage — Met.** Population of 32 computed directly from the inventory. The reviewer
resolved identity independently of the gate's method, having been warned the gate's first pass
deduplicated on `dedup_of`: 30 match by `source_id`, 1 only via shared `arxiv:2609.01873`, 1 via
same-paper/same-authors identity against a ResearchGate URL. 0 genuinely lacking — reproducing the
record's 30/1/1 split exactly. 0 blank cells across 2,881. 30 `critical_collision: yes`, 0 pending.

**3. Clean-room H4 — Met, with one recording defect.**

> The reasoning is written into the H4 block's `assessment` field in `06_hypothesis_tests.md` (lines
> 726-793), which is where the wording "reasoning recorded in the block" points — the attribution to
> `H4R` and its commit sits in the file's preamble instead, which is a defensible split given the
> acceptance text says nothing about where attribution must sit. The two sources credited with closing
> the gap ... are genuinely new to the matrix this phase — 0 occurrences in `dev`'s matrix, added via
> `LIT-09-S034/S035` and `LIT-09-S052/S053`, both dated 2026-09-19. The propagation into
> `08_surviving_distinctions.md` is real: H4 now appears once, in Category 1, and the old two-entry
> split is gone. **Defect I found that nobody flagged:** the file's own preamble cites the H4R commit
> as `7141767`, but that hash is not reachable from `HEAD` ... the actual commit on
> `agent/lit-campaign` is `8adc17c`.

**4. Duplicate-rate trend — Not Met as reported.**

> I reproduced the method phase-lit-08's own close review validated and "independently reproduced
> exactly" — split `result_ids` on the semicolon alone ... and it gives exactly **387** for the 82
> `LIT-08-*` rows, matching that phase's validated denominator precisely. Applying the identical
> method to the 105 `LIT-09-*` rows gives **392**, not 642. I then tested the hypothesis that
> `phase-lit-09`'s gate reintroduced the exact defect `phase-lit-08`'s close review had already found
> and named ... splitting `LIT-09`'s `result_ids` on **both** commas and semicolons gives **642**,
> exactly. ... The reported denominator is a reproduction of a previously-diagnosed bug, and the
> "falling trend" claim rests on it. I did not attempt to establish a fully authoritative corrected
> duplicate rate ... but 392 is the validated-methodology denominator, and 67/392 = 17.1% — which
> would reverse the claimed direction of the trend, not just its magnitude.

**5. LIT-07 G re-measures — Partially Met.** Measurements 2 and 4 independently confirmed exactly as
recorded. Measurement 5 inherits acceptance 4's defect.

**The three disclosed deviations — all judged legitimate.** `git show a69d8af` touches only `status`
and `agent` on `phase-lit-07`'s entry plus the catalog's agent column; scope, acceptance and
`next_action` byte-identical. `C2` and `P1` reuse existing pack sections, and
`git diff dev...HEAD -- docs/02-prompts/` is **empty** — no prompt file created or modified anywhere
on the branch. The deliverables-widening commit `9bba035` (23:24:26) precedes the first commit
touching `08`, `8d6287f` (23:37:59).

**Other findings nobody flagged.** The `H4R` hash self-citation above. The record's
"20 -> 19" arithmetic undercounts by one; the genuinely-unread figure was 18. A commit performing the
`X4` role is titled "phase-lit-09 X2", cosmetic only. And:

> The `04_evidence_matrix.csv` diff contains zero removed lines ... every second review this phase is
> additive-only, which is the strongest possible confirmation that no `component_overlap_score`,
> `architecture_overlap_score`, `critical_collision`, or `hypotheses_challenged` value was altered.

**Reviewer's verdict.**

> **This phase should not reach `status: complete` until acceptance condition 4 (and the LIT-07
> measurement-5 re-measure that depends on it) is recomputed with the semicolon-only method and
> re-reported, honestly, whichever way the number now falls.**

### What happened after the review

`G` was sent back for fix cycle 2 of 2 and recomputed under semicolon-only tokenisation: denominator
**392**, numerator **30**, rate **7.7%**. The coordinator recomputed independently against `dev`'s
1,123-row pre-phase inventory and got numerator **25**, rate **6.4%**. The denominator is settled;
the numerator is the identity-resolution judgment the reviewer explicitly declined to settle, and the
honest figure is a range of **6.4-7.7%**.

**The reviewer's inference that the correction might reverse the trend does not survive.** It carried
the old numerator of 67 forward to get 17.1%, having flagged that it had not re-derived it. Under
semicolon-only tokenisation the numerator falls with the denominator, because most of the 67 were
comma-split fragments of single identifiers. The direction is falling on every method tried. The
correction makes duplicates **rarer** than first reported, which moves saturation further out of
reach, not closer.

## Decisions

**Released `phase-lit-07`'s claim to take `sys-research`.** The phase's scope said `phase-lit-07`
stays `active`, but the governance check refuses two active phases sharing a system, so
`phase-lit-09` was unclaimable as written. The owner approved releasing it to `queued` with scope,
acceptance and `next_action` untouched. This matches what `AGENTS.md` already prescribes for a phase
whose acceptance failed and which nobody is working: return it to `queued` and release the claim.
`phase-lit-07` had failed acceptance 2 at its 2026-09-14 close review and only the claim release had
been missed.

**Added two items to the owner's ruled item order.** `C2` re-dispatched `LIT-05 S1` after `X3`,
because acceptance 1 covers "rows added this phase" and Block D runs backward chaining but not
forward — so every strong row the deep reads added had a `B` row and no `C` row, with `C1` long
finished. This is the same defect the backlog already records against `phase-lit-05`, whose item
order defeated its own gate. `P1` dispatched `LIT-07 X1` step 2 to write `08`. Both reuse existing
pack text with narrowed payloads; the review confirmed no prompt file changed anywhere on the branch.

**Widened the declared deliverables rather than writing outside them.** Acceptance 3 required
propagation into `08_surviving_distinctions.md`, a `phase-lit-07` deliverable. `AGENTS.md` requires
the declaration change first, on `dev`, so peers see the wider lock. The owner approved; the commit
ordering was verified by the review.

**Kept `H4R` uncontaminated at some cost.** By the time `H4R` was dispatched the coordinator knew a
great deal about the strongest H4 challengers — that PACT's sources are exclusively machine, that its
own section 2.2 credits precedents 16 to 18 years older, that one row called it "exactly" H4's claim.
None of it went into the dispatch, which carried Block C, the section text and file paths only, per
the mapping. `H4R` reached the same territory independently and changed H4's status. Had any of that
framing been passed, the re-derivation would have been worthless as evidence.

**Ran the six `R` reviews in parallel.** The pack dispatches sections one at a time, but `R`
dispatches write no repository file — their entire output is a report — so they cannot collide.
Serial execution would have cost roughly five times the wall-clock for no isolation benefit.

**Did not spend the Opus escalation.** One is available per campaign at the coordinator's judgment.
No step demanded it; the `R` dispatches, which are the campaign's own analogous independent reviews,
run on Sonnet by the pack's own staffing rule, and the close review was run on Sonnet for the same
consistency.

## Corrections

**The duplicate rate was reported wrong, twice, and the coordinator did not catch it.** `G` computed
its denominator by splitting `result_ids` on commas as well as semicolons. The rule — the delimiter
is the semicolon alone — was diagnosed by `phase-lit-08`'s close review, and the coordinator passed
it verbatim into every dispatch this phase, including `G`'s. The coordinator then verified the
chaining measurement, the blank-cell count and `G`'s measurement-2 failure by re-running each, and
took the duplicate rate on trust. A falling rate was the comfortable number and it is the one that
went unchecked. The independent review caught it. Corrected: 6.4-7.7%, not 10.4%.

**A gate measurement condemned its own input and was nearly believed.** `G`'s first measurement 2
reported FAIL on two top-band candidates lacking matrix rows, having "deduplicated" on the `dedup_of`
column, which is `none` on every row in that population. Both were identity duplicates already
deep-read. Caught by the coordinator before it reached the record, and fixed in `G`'s fix cycle 1.

**A coordinator block-segmentation check falsely flagged H11 as modified**, because it ran the last
hypothesis block to end-of-file and swept in the summary table that `X5` had been told to reconcile.
Re-measured with correct bounds, H11 is byte-identical at 12,083 bytes. Corrected before it was
reported as a defect in anyone's work.

**The unread top-band count was stated as 19 and is 18.** Both duplicate pairs already carried matrix
rows on `dev` before the phase began. The dispatch-time payload of 19 was right to dispatch, since one
duplicate was only discovered on reading, but the retrospective figure is 18.

**This record was renumbered from `SESS-2026-09-19-07` to `SESS-2026-09-19-08`.** A peer session
working `phase-tax-01` allocated the same code and integrated into `dev` first, while this phase was
in its close review. `AGENTS.md`'s rule is mechanical and left no judgment to exercise — codes are
free before merge and permanent after, so the agent integrating second renumbers. The document `id`
(`doc-session-literature-review-pass-3c`) is permanent and independent of the code, so it did not
change; the file name, the `code:` field and `phase-lit-09`'s own `next_action` reference did.
`phase-tax-01`'s reference to its own `SESS-2026-09-19-07` was left untouched.

No `GOV-003` entry accompanies this, because the collision was resolved by applying a stated rule
rather than by making a choice. What is worth noting is that both sessions allocated correctly:
`--next-code session` is not a reservation, and two agents calling it before either commits will
both be told the same number. Reserving the code in `codes.yaml` alongside the backlog claim, which
`AGENTS.md` already recommends, would have prevented it.

## Left undone

**Acceptance 4's numerator is a range, not a number.** 25 or 30 out of 392, depending on how a
prose-wrapped identifier is resolved. The reviewer declined to settle it and so does this record. The
denominator is settled and the direction is robust, but a campaign that reports duplicate rates across
phases should fix one tokenisation-and-matching rule in the evidence contract rather than leaving each
gate to invent one. That is a real gap in `PLAN-023.03` and it has now produced two wrong numbers in
two consecutive phases.

**`06_hypothesis_tests.md` cites a commit hash that does not exist on the branch.** The preamble names
`7141767` for `H4R`; the real commit is `8adc17c`, the first having been rewritten by a rebase. Left
unfixed because a hash cited inside a file on a rebasing branch will drift again; the durable fix is
to cite the dispatch and date rather than the hash, and that is the writing dispatch's judgment, not
the coordinator's.

**Ten stale H4 references in `07_anti_novelty_case.md`** — lines 168, 192, 195, 196, 198, 202, 422,
453, 455, 461. A `phase-lit-07` deliverable, deliberately left outside this phase's declarations on
the owner's direction, with the line numbers recorded here so the revisit does not have to re-find
them.

**Three critical-collision flags now fail every trigger under independent review** — `prov-agent-2025`,
`chianti-cia-tool-java-icse-2005` and `provenance-enhanced-statements-dec-2026`. Under check-in
ruling 1 nothing was applied. 18 of 30 standing flags are now recorded `disputed`. Whether that
changes the campaign's headline collision count is a scoping decision the owner has deferred.

**The `PLAN-023.03` tokenisation gap is captured as an idea** rather than fixed here, on the owner's
direction — amending a governed evidence contract mid-campaign needs its own requirement and plan.

**`phase-lit-07`'s scoping decision is deferred to a fresh session**, on the owner's direction, so it
is taken against the verified numbers rather than at the end of a long session.
