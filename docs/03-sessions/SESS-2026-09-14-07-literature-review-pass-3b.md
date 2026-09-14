---
schema_version: 1
id: doc-session-literature-review-pass-3b
code: SESS-2026-09-14-07
title: Literature review Pass 3b — targeted collision search for H1, H4 and H11, and the dispatch mapping the pack did not carry
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

# Literature review Pass 3b — targeted collision search for H1, H4 and H11

The campaign's seventh execution session. Claimed by `agent-lit`, working in
`../d-system-worktrees/lit-campaign` on `agent/lit-campaign`.

## Phase

`phase-lit-08` — Literature review Pass 3b: targeted collision search for H1, H4 and H11.
Numbered 08 but runs **before** `phase-lit-07`, which depends on it.

## The blocking finding this session opened with

**`PROMPT-029` has no `LIT-08` section, and no ruling mapped the phase onto existing ones.**
Verified rather than assumed: `grep -rn "LIT-08" docs/ research/` returns exactly one hit, and it
is not a prompt — it is the phase's own verification line naming a `LIT-08-S` ledger prefix
(`backlog.yaml:6513`). The pack runs `LIT-01` through `LIT-07` and stops.

`PROMPT-031`'s pre-synthesis check-in carries eight rulings and **none maps this phase**, which it
could not have: the check-in was held in [SESS-2026-09-14-01](SESS-2026-09-14-01-literature-review-pass-3.md),
and `phase-lit-08` was created afterwards in [SESS-2026-09-14-04](SESS-2026-09-14-04-lit-06-followups.md).

Per the pack's own rule the coordinator stopped and asked. **The owner ruled the mapping**, which is
now recorded as its own dated section in `PROMPT-031` — deliberately not folded into the
pre-synthesis check-in section, so a reader looking for what that check-in decided does not find a
later, unrelated ruling mixed into it.

Every item dispatched was existing pack text with a narrowed payload. **No section was authored.**

| Item | Model | Section dispatched | Narrowing |
|---|---|---|---|
| `K` | Haiku | `LIT-06 K` | claims `phase-lit-08` |
| `S1`/`S2`/`S3` | Sonnet | `LIT-06 S1` (Block C + S) | one dispatch per hypothesis; search and log only |
| `X1`/`X2`/`X3` | Sonnet | Block C + **Block D** | deep-extract what the paired `S` nominated |
| `R` ×5 | Sonnet | `LIT-06 R` verbatim | one per new `critical_collision: yes` row |
| `X4` | Sonnet | `LIT-06 X2` | folds the five new verdicts |
| `X5` | Sonnet | `LIT-06 X1` | **H1, H4, H11 blocks only**; `05` half skipped |
| `G` | Haiku | Block G | measures this phase's four acceptance conditions |

The owner's three mapping choices and their reasons are in `PROMPT-031`. The substantive one:
extraction is a **separate Block D dispatch** rather than inline in `S`, because an `S` dispatch
assembles Block C + Block S and never receives Block D — so the read-disclosure requirement added by
check-in ruling 5 would not have reached the agent doing the extraction. A searcher scoring its own
finds is the configuration that produced Pass 2's one-directional depth defect.

## Verification

`uv run python -m src.governance`, after rebasing onto `dev`

```text
Governance OK: 20 systems, 218 documents, 24 memories, 150 backlog phases
exit 0
```

`uv run pytest`, after the rebase

```text
580 passed, 2 warnings
```

`uv run python tools/check_no_private_content.py`, with changes staged

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is
expected in CI / a fresh clone)
check_no_private_content: OK (607 tracked files, 0 identifiers checked)
exit 0
```

**This is not a passing verification.** `_private/` is gitignored and absent from a worktree, so the
tool builds an empty identifier list and reports `0 identifiers checked`. Idea `000150` records
this. The real check runs in the primary checkout.

**Ledger, matrix and inventory integrity** — the phase's third verification entry, written in prose
rather than as a command. Measured by the coordinator directly against the files, and independently
by `LIT-08 G`:

```text
00_search_ledger.csv:    1080 lines, 1080 CRLF, 0 LF-only; 1079 data rows; 15 fields on every row
                         LIT-08-S001..S082 contiguous, no gaps; every LIT-08 row pass=3
04_evidence_matrix.csv:  50 lines, 0 CRLF; 49 data rows; 43 fields on every row; 0 blank cells
03_source_inventory.csv: 1124 lines, 0 CRLF; 1123 data rows; 13 fields on every row; 0 blank cells
```

The ledger carries 2 blank cells on one pre-existing Pass 1b row (`LIT-02-S045`, fields `kept` and
`inclusion_rationale`), present since before this phase and **not** a contract violation — see
Corrections.

### Delegation-pack section `LIT-08 G` — the phase gate

Run on Haiku. **All eight measurements PASS.** Every figure below was independently reproduced by
the coordinator against the files before being recorded here.

**Measurement 1 — per-hypothesis ledger coverage. Gate: ≥2 more distinct-query rows than
`phase-lit-06` left. PASS.** Population: ledger rows matching `domain_id` **exactly** (a substring
match on `H1` also catches `H10` and `H11`, and would be wrong).

| | before | after | added | distinct queries |
|---|---|---|---|---|
| H1 | 3 | **27** | +24 | 27 |
| H4 | 15 | **47** | +32 | 47 |
| H11 | 4 | **30** | +26 | 30 |

Every row is a distinct query; no hypothesis reaches its floor by logging one query twice.

**Measurement 2 — evidence-matrix integrity. PASS.** 43 fields × 49 rows = 2,107 cells, **0 blank**.

**Measurement 3 — second reviews. Gate: 0 pending. PASS.** 24 `critical_collision: yes` rows, 0
pending; 11 `confirmed`, 13 `disputed`.

**Measurement 4 — statuses. Gate: 11 of 11 permitted, no `NOVEL`. PASS.** 4
`LIKELY_ALREADY_KNOWN`, 5 `KNOWN_COMPONENT_NEW_INTEGRATION`, 2 `INSUFFICIENT_EVIDENCE`, **0
`POTENTIALLY_DISTINCT`, 0 `NOVEL`.**

**Measurement 5 — this phase's duplicate rate, the saturation signal. 15.0%.** Numerator 58,
denominator 387: `result_ids` of all 82 `LIT-08-*` rows resolved against the pre-phase inventory at
`83fb42b^`, matching on `source_id` **or** `url_or_doi`. Distinct-identifier basis: 37/347 = 10.7%.

**The rate FELL, from `phase-lit-06`'s 44/220 = 20.0%.** Reported as a trend only, per ruling 8. No
saturation is claimed and none is demonstrable. The honest reading is stronger than "unproven": a
targeted search into three neglected hypotheses surfaced *more* new material than the broad sweep
before it, which is evidence the campaign's coverage was **uneven rather than near-complete**.

**Measurement 6 — line endings. PASS.** Ledger 1080 lines, 1080 CRLF. Matrix 50 lines, 0 CRLF.
Inventory 1124 lines, 0 CRLF.

**Measurement 7 — ledger structure. PASS.** 15 fields on all 1,079 rows; `LIT-08-S001`–`S082`
contiguous with no gaps; every `LIT-08` row carries `pass: 3`.

**Measurement 8 — `05_critical_collisions.md`. PASS.** 24 sections against 24
`critical_collision: yes` rows; every flagged row has one.

## Acceptance

- **Each of H1, H4 and H11 has ≥2 further distinct-query ledger rows beyond `phase-lit-06`'s
  counts** — **Met.** +24, +32 and +26 against a floor of +2, all distinct queries. Verified by the
  coordinator against the ledger, not relayed.
- **Every new matrix row is a full 43-field row with zero blanks, and every one flagged
  `critical_collision: yes` carries a recorded independent second review** — **Met.** 15 new rows,
  43 fields each, 0 blanks across 2,107 cells; 5 flagged `yes`, all 5 independently reviewed, 0
  pending.
- **`06_hypothesis_tests.md` states for each of H1, H4 and H11 whether the further search changes
  its status, and says so explicitly where it does not** — **Met.** H1 and H11 re-examined and
  explicitly unchanged with stated reasons; H4 moved. See below.
- **This phase's duplicate rate is measured and reported against 44/220 as a trend, never asserted
  as saturation** — **Met.** 58/387 = 15.0%, reported as a falling trend, no saturation claimed.

## Backlog

`phase-lit-08` — `status: complete`, `agent: agent-lit`. Closed by the owner's `/session-close` on
2026-09-14, after an independent review confirmed all four acceptance conditions against its own
reruns.

`next_action`: None. Two items pass to `phase-lit-07` rather than remaining open here: H4's status
rests on a dispatch framing the worker flagged as steering and the close review judged a real,
contestable risk (see Review and Corrections); and 20 of 32 top-band collision candidates remain
unread (see below), which a synthesis phase cannot close.

`completion_evidence` (files that exist now):

- `research/literature-review/00_search_ledger.csv`
- `research/literature-review/03_source_inventory.csv`
- `research/literature-review/04_evidence_matrix.csv`
- `research/literature-review/06_hypothesis_tests.md`
- `research/literature-review/05_critical_collisions.md`

`next_up`: unchanged. `phase-lit-08` was never in it, and nothing else became `complete` this
session, so there was nothing to prune.

## Unresolved

- **H4's status may be contaminated by a coordinator dispatch framing**, which `X5` flagged
  unprompted. H1 and H11 are unaffected. A re-derivation by an agent that never saw the framing is
  the owner's call at `/session-close`. See Corrections.
- **20 of 32 top-band collision candidates have never been deep-read** — 62.5% of the strongest
  band, and three of this phase's strongest finds came from that unread set. `phase-lit-07` is
  synthesis, not search, so it cannot close this itself. (Figures corrected at close after the
  independent review refuted the first ones; see Corrections item 3.)
- **Two duplicate `source_id` rows in the inventory**, pre-dating this phase, found by the close
  review: `memtx-transactional-belief-commit-2026` and
  `semantically-seeded-graph-propagated-impact-analysis-vision-2026`. No acceptance condition is
  affected, but the inventory's row count is not a distinct-source count.
- **The campaign is further from saturation than it looked.** The duplicate rate fell 20.0% → 15.0%
  when searches were aimed at neglected ground.
- **Three fetch-tool fabrications and one uncritically-inherited self-reported metric** were caught
  this phase, all by workers re-reading primary text. No governed rule currently requires that
  re-verification; Block C's "summaries are leads" is the nearest thing and it is advisory.
- **Carried from earlier phases**: `000221` (contract names `LIT-06 X2` as `second_review`'s sole
  writer while the flagging dispatch writes `pending`), `000148` (the `source_type` enum, now
  demonstrably short a bucket for live repositories), `000224` (a phase silently regressing from
  `complete` still fails no check; `phase-gov-05` is queued for it).

## What the evidence phase found

**The campaign gained no surviving distinction. It still holds zero `POTENTIALLY_DISTINCT` and zero
`NOVEL`.** One hypothesis moved, and it moved *toward* H0.

- **H1 — `INSUFFICIENT_EVIDENCE`, unchanged, explicitly re-examined.** Its four new candidates are
  weeks-old, single-author, unreviewed repositories, or — for `toki` — a rigorous proof of an
  unrelated triple.
- **H4 — `INSUFFICIENT_EVIDENCE` → `KNOWN_COMPONENT_NEW_INTEGRATION`.** Not because the search
  failed to find anything, but because it found `goldman-experts-which-ones-should-you-trust-2001`:
  a peer-reviewed, closed-form Bayesian proof that a blind follower adds zero evidential weight,
  agent-model-agnostic, 25 years before `bara-2026`. A positive match, not an absence. The status
  carries the **review-instructions general phrasing**; the frozen register's graph-topological
  phrasing remains `INSUFFICIENT_EVIDENCE` and that argument is preserved in full inside
  `assessment`, per the file's own primacy rule and the H8 precedent.
- **H11 — `INSUFFICIENT_EVIDENCE`, unchanged, explicitly re-examined.** Uniquely among the three it
  found a genuinely mature comparator family — the 2010–2023 awareness-requirements lineage — but
  its best-implemented member (`EvoReqs`) closes a loop over a hand-authored rule vocabulary with no
  provenance. Every candidate aimed at H11's actual mechanism states it as unbuilt.

**`toki` was in the inventory for four phases and was never opened.** `LIT-08 S1` surfaced it only
because a dedicated H1 search went looking. The deep read then settled it as a different mechanism —
isolation/schema/provenance, write-time concurrency control, no ontological-type or lifecycle axis.

## The finding that outgrows this phase

**62.5% of the campaign's top-band collision candidates have never been deep-read.** Measured across
the whole inventory at close. "Read" means the `source_id` has a row in `04_evidence_matrix.csv`;
the band is `max(component_prescore, architecture_prescore)`:

| prescore | candidates | deep-read | share |
|---|---|---|---|
| 5 | 32 | 12 | **37.5%** |
| 4 | 200 | 24 | 12.0% |
| 3 | 152 | 8 | 5.3% |
| 2 | 3 | 3 | 100% |

**340 of 387** `collision_candidate: yes` rows have no matrix row. Triage was directionally sound —
the read rate rises with prescore — but **20 of 32 top-band candidates were never opened.**

*(These figures were corrected at close. The independent review refuted the coordinator's first
numbers, which were measured after `X1` but before `X2` and `X3` added nine inventory rows and
eleven matrix rows, and whose table silently omitted the prescore-2 band — so its columns summed to
380 against a headline of 382. Banding by `component_prescore` alone rather than the max gives
32/197/153 candidates and the identical totals, so the choice of band definition does not affect the
finding. See Corrections.)*

This is not an abstract risk. **Three of this phase's strongest finds came from that unread set**:
`toki` (H1), `barakat` at prescore 5/3 (H4), and the entire awareness-requirements family at 4/3
(H11) — eight sources whose own inventory rationale, in one case, names H11 by id.

The methodology's stop condition is "the strongest 20–30 sources deeply compared". At 49 matrix rows
that is satisfied **by count**. It is not satisfied by **coverage of the strongest band**, and
nothing in the campaign measures the difference. `phase-lit-07` needs this before it characterises
what remains.

Two duplicate `source_id` rows exist in the inventory — `memtx-transactional-belief-commit-2026` and
`semantically-seeded-graph-propagated-impact-analysis-vision-2026` — found by the close review. Both
pre-date this phase and affect no acceptance condition, but they mean the inventory's row count is
not a distinct-source count, and whoever acts on the coverage finding should dedupe first.

## What was dispatched

Item order `K → S1 → X1 → S2 → X2 → S3 → X3 → R×5 → X4 → X5 → G`, per the owner's ruling. Checked
before dispatching for the shape `000218` describes: every row the reviews and the gate must cover
exists before either runs.

**`K` (Haiku).** Claimed `phase-lit-08` on `dev` in `f8e817b` with the catalog regeneration the
claim forces, in the primary checkout — the only work `AGENTS.md` permits there. Verified prior
evidence rather than recreating it. Its report omitted a confirmation it had been asked for, which
is how the peer-file question below came to be checked.

**`S1` (Sonnet), H1.** 20 rows, `LIT-08-S001`–`S020`, all distinct queries. Took H1 from 3 to 24
rows. Surfaced `toki` from the inventory.

**`X1` (Sonnet), H1.** 4 matrix rows; 2 flagged. Deviated from the commit-per-source rule, batching
all four into one commit, and disclosed it. Not sent back: the resumability that rule protects is
moot once a run has completed, and rewriting the commits buys nothing.

**`S2` (Sonnet), H4.** 22 rows, `S025`–`S046`. Surfaced `barakat` from the inventory.

**`X2` (Sonnet), H4.** 5 matrix rows — four from the payload plus `goldman`, found by chasing a
footnote. 3 flagged. Committed per source.

**`S3` (Sonnet), H11.** 20 rows, `S057`–`S076`.

**`X3` (Sonnet), H11.** 6 matrix rows, **all `critical_collision: no`**. Self-caught a 14-field
ledger row on write and fixed it in its own commit (`52dc19d`) — the on-write validation rule
working as designed.

**`R` (Sonnet ×5).** One dispatch per new flagged row, each freshly spawned, each receiving exactly
two inputs: the source, and a file containing that row's 43 fields and nothing else, with `05` and
`06` explicitly off-limits. **5 confirmed, 0 disputed.** Every reviewer re-derived both scores
independently and matched; every flag stood on the component-overlap trigger alone.

**`X4` (Sonnet).** Five verdicts into `second_review`, five dated sections into `05` (19 → 24), and
the factual corrections below. **Changed no score, no `critical_collision`, no
`hypotheses_challenged`** — verified by a coordinator-run field-level diff across all 49 rows.

**`X5` (Sonnet), one fix cycle.** Re-derived H1, H4 and H11. Fix cycle 1: H4's `status` carried a
compound string naming two permitted tokens, violating its own section's explicit four-value
constraint and risking both this gate's classification and `LIT-07 G`'s downstream counts. Sent back
for conformance to the file's own H8 precedent — a bare token in `status`, the split preserved in
`assessment` — and **not** told which reading to make primary. The other eight blocks verified
byte-identical before and after.

**`G` (Haiku).** All eight measurements passed, no fix cycle. It exceeded a mechanical gate's brief
once, by interpreting the ledger's blank cells against the contract rather than only reporting them
— and was right to; see Corrections.

## Spend posture

- **Searches**: 82 this phase (`LIT-08-S001`–`S082`); ledger now 1,079 rows.
- **Sources deep-read**: 15 new matrix rows; matrix now 49 rows × 43 fields, 0 blanks.
- **Independent reviews**: 5, each a full source re-read; one executed the source's test suite.
- **Fix cycles**: 1, against `X5`, well inside the cap of two.
- **Opus escalation**: none spent, in this session or the campaign.
- **Descope rung**: none taken.
- **Runway**: 7 of 7 estimated sessions used, against an owner-accepted range of six to eight.
  `phase-lit-07` is the eighth and would sit at the top of that range.

## Corrections

**The coordinator got two numbers wrong, and both were caught by cross-checking rather than by
trusting.** Recorded here because the standing rule is to verify every claim against the file, and
these are the cases where the coordinator's own output needed the same treatment.

1. **H11's ledger count was reported as 4 → 24 (+20). It is 4 → 30 (+26).** The figure was measured
   immediately after `S3` committed and not re-measured after `X3` appended six backward-chaining
   rows (`LIT-08-S077`–`S082`, all `domain_id: H11`). It reached the `X5` dispatch in that state.
   `X5` caught it. **`X5`'s stated reason was itself wrong** and was not adopted: it attributed the
   gap to embedded newlines defeating a naive parse, but the ledger has **0 rows with an embedded
   newline in any field** and the original count came from a real CSV parse. The cause was
   staleness. A false account of why a number was wrong is worse than the wrong number, because the
   next person applies the wrong remedy.
2. **The coordinator's independent duplicate-rate figure (59/389) was wrong; `X5`'s and `G`'s
   agreeing 58/387 is right.** The coordinator split `result_ids` on commas as well as semicolons,
   fragmenting two identifiers that contain parenthetical commas (`…(paywalled, 303 redirect…)` and
   `…(open mirror, 26pp)`) into four tokens and inventing one spurious duplicate. The delimiter is
   the semicolon alone.

3. **The coverage finding's numbers were stale and its table was internally inconsistent. Caught by
   the close review, not by the coordinator.** Recorded as 346 of 382 unread with a 36.4% top-band
   read rate; correct at close is **340 of 387 unread with a 37.5% top-band read rate, 20 of 32
   never opened**. The figures were measured after `X1` but before `X2` and `X3` added nine
   inventory rows and eleven matrix rows. The table also silently omitted the prescore-2 band, so
   its columns summed to 380 against a headline of 382 — the reviewer spotted that arithmetic gap
   from the record alone. The qualitative finding is unchanged and marginally worse than recorded.

**All three coordinator errors this session share one root cause: a figure measured mid-phase and
not re-measured at close.** H11's ledger count, and twice over in the coverage finding. The
duplicate-rate error was different in kind (a tokenizer bug), but the pattern in the other two is a
habit worth naming — a number taken while dispatches are still writing to the files it counts is a
number with a shelf life, and nothing in the campaign's process forces a re-measure before it is
written down. The gate re-measures the gate's own quantities; nothing re-measures the coordinator's
narrative ones.

**The coordinator called two ledger blank cells a defect. They are not a contract violation.** The
"blank is not permitted" rule at `PLAN-023.03:75` governs the **evidence matrix**, not the ledger,
and line 194 explicitly contemplates the case: "a failed collision search is a ledger row with its
queries and empty `kept`." `LIT-08 G` read the contract and got this right where the coordinator had
not. What survives is smaller: `LIT-02-S045` is the **only** row of 1,079 leaving `kept` empty while
**412 rows write the literal token `none`** — a lone convention deviation that makes the row
invisible to any consumer testing for the token. A consistency note, not a defect.

**A dispatch framing may have steered `X5`'s H4 verdict, and `X5` said so.** The dispatch's context
section stated that Goldman "satisfies a general reading and fails the register's graph-topological
reading" — a relay of what `X2` had already reported, but a substantive conclusion placed into a
dispatch whose job was to reach conclusions about that evidence. `X5` flagged it unprompted: it
introduced the general/topological split "since the dispatch text explicitly named Goldman as
satisfying the general reading." H1 and H11 are unaffected, and `X5` declined to extend an analogous
move to H11 despite a real implemented system sitting there, which is evidence of independent
judgment rather than compliance. **The H4 split should not be treated as uncontaminated**, and a
re-derivation by an agent that never saw the framing is the owner's call at `/session-close`.

## Findings raised

**Three fetch-tool fabrications, caught by three different dispatches.** Each was found only because
a worker re-fetched and read primary text instead of trusting a summary:

- `X2` — a WebFetch summary produced a **verbatim quote attributed to Kuter & Golbeck 2007 that
  appears nowhere in that paper**. Logged at `LIT-08-S054`.
- `X3` — a WebFetch summary **invented a "Taiga tool" and a "meeting room management system" case
  study** for Souza et al. 2011; the real implementation is EEAT with an Ambulance Dispatch System.
  Not used in any scored field.
- `S3` — a suspected fabricated claim attributed to an MDPI paper, excluded rather than credited.

A fourth, separate tool artifact: WebFetch reported the SEAMS 2012 PDF as "corrupted/unreadable"
when it was not — `curl` plus local `pdftotext` read it in full. A fetch failure message is not
evidence that a source is unreachable.

**A new variant of the same class: a source's self-reported metric adopted without check.** The
`mythologiq` row recorded "359+ merged PRs", taken from the repository's **own internal governance
ledger**, authored by an internal project role, describing itself as "an existing mature
repository". GitHub's API gives **223 merged / 239 total** — roughly 60% inflation. The row also
credited a "Code Reality Graph" as implemented, which the repository's own maturity document marks
`declared… no module has been built yet`, and framed a **single-author** project (745 of 748 commits
by one person, zero external contributors, ten weeks old) with language implying institutional
weight. Scores unaffected; the maturity narrative corrected by `X4`.

**Block D's read-disclosure requirement caught a contradiction it was built to catch.** The
`subit-wiki` row claimed a file was "read in full" while the row's own `evidence_locator` disclosed
only "first ~60 lines" — and the claim built on that partial read (that the source omits
attribution) was false; the file cites Rabiner 1989 and Forney 1973 in its references. **Owner ruling
5 is what made this visible.**

**One reviewer executed the source's test suite**, establishing something neither a read nor a score
could: `subit-wiki`'s Viterbi decoder is provably correct (9/9, including a brute-force
cross-check), while its self-evolving feedback mechanism **fails 2 of its own 9 tests**. Specified
and coded, imperfectly demonstrated.

**The `source_type` enum gap widened** (`000148`). It has no bucket for a live software repository;
three were filed under `OSS`, which now conflates a mature released library with an
actively-developed governance system and a single-commit abandoned dump.

**The one-directional error pattern persists, but has shrunk and is being caught by controls rather
than by luck.** All three errors the reviews found ran the same way `phase-lit-06`'s did — toward
crediting a collision — in a campaign whose null hypothesis is that collisions exist. But the
profile inverted: **5 confirmed / 0 disputed** here against 6 confirmed / 13 disputed there. The
likely reason is that these rows were written *after* Block D's read-disclosure requirement landed,
by dispatches holding it.

## Review

An independent sub-agent reviewed `dev...agent/lit-campaign` (30 commits) at close, starting with no
context from this session, and ran every verification command itself. Its findings, verbatim.

### The four acceptance conditions

> **1. ≥2 further distinct-query ledger rows per hypothesis — Met.** Exact `domain_id` match (not
> substring) gives H1 3→27 (+24), H4 15→47 (+32), H11 4→30 (+26). All 82 `LIT-08-S001`–`S082` rows
> carry `pass: 3`, contiguous, no gaps. Reproduced myself with a script, not taken from the record.
>
> **2. Full 43-field matrix rows, second reviews for all `critical_collision: yes` — Met.** Matrix:
> 49 rows × 43 fields, 0 blank cells across 2,107 cells (verified by direct cell scan). 24 rows
> flagged `critical_collision: yes`, 0 pending, 11 confirmed / 13 disputed — exact match to the
> record. The five new reviews from this phase are all `confirmed`, 0 disputed.
>
> **3. `06_hypothesis_tests.md` states whether status changed, explicitly — Met.** 11 `status:`
> lines, values restricted to the four permitted tokens […]; `NOVEL` appears only in rule prose.
> H1/H11 = `INSUFFICIENT_EVIDENCE`, H4 = `KNOWN_COMPONENT_NEW_INTEGRATION`. All three blocks are
> substantive re-derivations, not pro forma.
>
> **4. Duplicate rate reported as trend only, never saturation — Met.** I reproduced 58/387 = 15.0%
> and 37/347 = 10.7% independently […] No saturation assertion found anywhere in the deliverables.

### On the protected-field claim, and the duplicate rate

> **Five new second reviews changed no score** — confirmed by my own field-level diff of the matrix
> between the commit before `X4`'s first commit and `X4`'s last commit: `component_overlap_score`,
> `architecture_overlap_score`, `critical_collision`, `hypotheses_challenged` are unchanged across
> all 49 rows.

> **Duplicate rate 58/387=15.0%, 37/347=10.7%** — **independently reproduced exactly** […] This is
> the strongest positive confirmation in the whole review — my number-for-number match on first
> attempt corroborates both the number and the documented comma-splitting pitfall.

> **Eight non-H1/H4/H11 blocks byte-identical to `dev`** — confirmed. Extracted H2, H3, H5–H10 from
> both versions; identical line-for-line.

> **No fabricated material in any committed deliverable** — confirmed. Searched for "Taiga tool,"
> "meeting room management system" (neither appears anywhere), and the Kuter & Golbeck material
> (appears only in `05_critical_collisions.md` and the ledger as documentation of the fabrication
> being caught and discarded, never credited as fact). The MDPI incident is also present exactly as
> described, at `LIT-08-S065`, explicitly flagged as an unverified tool-generated claim "not to be
> mistaken for a confirmed finding."

### The one claim it refuted

> **Coverage finding (346/382, 21/33 top-band unread, 36.4%)** — **not reproduced.** My own
> computation from the current committed files gives different numbers by every method I tried […]
> Neither method reproduces the record's 346/382 or its per-band breakdown, though both land in the
> same neighborhood and support the same qualitative conclusion (severe undercoverage of the top
> band). Note also that the record's own table is internally inconsistent — the three band totals in
> its text sum to 380, not the 382 asserted in the headline sentence […] This looks like arithmetic
> drift in the record's own count, not a fabrication — the direction and rough magnitude of the
> finding hold up — but the specific numbers should not be trusted at face value.

**Acted on.** The coordinator recomputed at close, confirmed the reviewer, and corrected the figures
and the method statement above. See Corrections item 3.

### Its judgement on the two substantive questions

> **Is acceptance 3 genuinely satisfied in substance?** Yes. I read the full H1 and H11 blocks. Both
> name the specific searches run, list every new candidate with its overlap scores and why it falls
> short, and explicitly apply the file's own two-condition saturation-adjacent rule […] A reader
> would genuinely learn that the search was re-run in earnest and found nothing sufficient, not just
> that a status line stayed the same.

> **Does H4's verdict stand on the evidence, or on the dispatch framing?** Mixed, genuinely
> contestable. The evidentiary content is real: Goldman (2001) is a peer-reviewed, 25-year-old,
> closed-form proof that dependent ("blind follower") agreement adds no evidential weight while
> independent agreement does — a substantive match to H4's general phrasing regardless of how it was
> described to the worker. The two-phrasing split itself also isn't invented for H4; it follows an
> existing documented convention already used for H8 earlier in the same file. But the coordinator's
> dispatch text told the worker, before it reached its own conclusion, that Goldman "satisfies a
> general reading and fails the register's graph-topological reading" — handing the worker the exact
> two-way split and exactly how to characterize the key source. `X5` disclosed this unprompted,
> which is a point in favor of process integrity, but disclosure doesn't remove the risk: I cannot
> rule out that a neutrally-framed dispatch would have produced a more conservative single verdict
> (e.g., treating the ambiguity as reason to stay `INSUFFICIENT_EVIDENCE` overall) rather than
> actively promoting one reading to the primary status token. The session record's own flag on this
> is fair and should not be waved off at `/session-close`.

### Its bottom line

> All four acceptance conditions hold under my own reruns. Eight of the nine specific claims I
> checked reproduce exactly or are directly confirmed by the diff. The ninth — the
> coverage/undercoverage finding — does not reproduce under any matching method I tried, though the
> qualitative conclusion […] is directionally correct […] The H4-framing risk the record itself
> raises is real and warrants the owner's attention at close, not dismissal.

It also noted governance reporting 219 documents against the record's 218 — background drift on
`dev` since that run, not this phase's doing — and the two duplicate inventory `source_id`s recorded
above.

## Decisions

**The coordinator stopped on the missing prompt rather than improvising one.** `phase-lit-08`'s
`scope` gestures at reuse — "per the `LIT-06 R` section", "strategy Phase E collision searches" —
and it would have been easy to read that as a mapping and proceed. It is not one: choosing which
sections to reuse, how to narrow their payloads, and what the gate measures *is* authoring a
dispatch mapping. The owner ruled it instead, and every item dispatched is existing pack text.

**The `X2` charter line was held exactly where `phase-lit-06` drew it.** `X4` writes review outcomes
and factual corrections and touches no score, no flag, no `hypotheses_challenged` — even where a
correction made a row's maturity picture look materially weaker. Asked whether the line sits in the
right place, `X4` said it does, and named the one borderline case: whether "make the single-author
context explicit" is a descriptive correction or a reframing. It affected no protected field either
way.

**The `X5` fix cycle was opened for conformance, not for direction.** H4's compound status violated
an explicit constraint of its own section text. The dispatch back said so, cited the file's own H8
precedent, and stated plainly that which reading is primary remained `X5`'s call. This is the same
shape as `phase-lit-06`'s fix cycle, which was sent back for inconsistency rather than for the
direction it had chosen.

## Left undone

**`phase-lit-07` inherits a coverage problem this phase could only measure, not fix.** 21 of 33
top-band collision candidates remain unread. Reading them is not a paragraph in the synthesis phase;
it is search-and-extraction work, and `phase-lit-07` is neither.

**The H4 split rests on a dispatch framing the worker flagged as steering.** See Corrections.

**The campaign is further from saturation than it looked, not closer.** The duplicate rate fell
20.0% → 15.0% when searches were aimed at neglected ground. `phase-lit-07` is synthesis, not search,
so the number will not improve there; ruling 8 continues to forbid claiming otherwise.

**Findings that outlive this phase**: `000221` (the contract still names `LIT-06 X2` as
`second_review`'s sole writer while the flagging dispatch writes `pending`), `000148` (the
`source_type` enum, now demonstrably short a bucket for live repositories), `000224` (a phase
silently regressing from `complete` still fails no check; `phase-gov-05` is queued for it).

## Resume state

**Current phase**: `phase-lit-08`, `active`, gate-measured and passing on all eight measurements,
left active for the owner's `/session-close`. An agent never marks a phase complete.

**Next**: `phase-lit-07` — Pass 4, synthesis. Its `depends_on` names `phase-lit-08`, so it unblocks
when this phase closes. `PROMPT-031` already carries the dated pre-synthesis check-in entry
`LIT-07 K` requires. `LIT-07`'s item order is `K → X1 → X2 → X3 → A → G`, and `X1`'s item 0
verifies the `06` reconciliation rather than redoing it — that reconciliation ran in `phase-lit-06`
and this phase rewrote three of its blocks on new evidence.

**A fresh session must read**: `AGENTS.md`, `GOV-006`, `PROMPT-031` — including both its
pre-synthesis check-in rulings and the `phase-lit-08` dispatch-mapping section — then `PROMPT-030`,
then [SESS-2026-09-14-01](SESS-2026-09-14-01-literature-review-pass-3.md) for the campaign's state,
then this record.

**Three things `phase-lit-07` must not do**: claim saturation (ruling 8, and the trend now runs
against it); represent the matrix's 49 rows as covering the strongest candidates without naming the
63.6% unread top band; or treat H4's status as settled without noting the dispatch-framing caveat.

**Branch**: `agent/lit-campaign`, rebased onto `dev` at this boundary, clean, governance exit 0, 580
tests passing, 28 commits ahead. **Not integrated** — the second of the two owner integrations
`PLAN-023` schedules falls at campaign close, and this is not it. Review with
`git diff dev..agent/lit-campaign`.

**The `lit-campaign` worktree must be retained.** `phase-lit-07` commits to this same branch, and
removing the worktree destroys its gitignored `.venv` and `data/`, which no merge carries.
