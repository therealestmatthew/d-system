---
schema_version: 1
id: doc-session-literature-review-pass-4
code: SESS-2026-09-14-08
title: Literature review Pass 4 — synthesis, adversarial synthesis review and the final gate
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

# Literature review Pass 4 — synthesis, adversarial synthesis review and the final gate

The campaign's eighth execution session, at the top of the owner-accepted six-to-eight range.
Claimed by `agent-lit`, working in `../d-system-worktrees/lit-campaign` on `agent/lit-campaign`.

## Phase

`phase-lit-07` — Literature review Pass 4: synthesis, adversarial synthesis review and validated
bibliography. The campaign's final phase.

## Verification

`uv run python -m src.governance`

```text
Governance OK: 20 systems, 219 documents, 24 memories, 150 backlog phases
exit 0
```

`uv run python tools/check_no_private_content.py`, with all changes committed

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is
expected in CI / a fresh clone)
check_no_private_content: OK (617 tracked files, 0 identifiers checked)
exit 0
```

**This is not a passing verification.** `_private/` is gitignored and absent from a worktree, so
the tool builds an empty identifier list and reports `0 identifiers checked`. Idea `000150`
records this. The real check runs in the primary checkout.

`uv run pytest`

```text
580 passed, 2 warnings
```

### Delegation-pack section `LIT-07 G` — the final gate, the campaign's stop conditions measured

Run on Haiku, one fix cycle spent (the first run mismeasured two conditions through its own method
errors; see Corrections). Every figure below was independently reproduced by the coordinator
against the files before being recorded here, and every headline number was re-measured at close
after the last commit.

**Measurement 1 — all 72 domains searched, ≥2 distinct-query rows, full mandated-variant
coverage. PASS.** Population: 1,095 ledger rows across 72 domain ids plus H1–H11. Every domain
has 6–31 distinct-query rows (minimum D48 at 6); zero uncovered mandated variants, where a
domain's mandated variants are the items its Pass 1 `S` payload lists after "variants:". The
first run failed D18 by treating the domain *title* as a seventh variant; the corrected
measurement passes, and the coordinator spot-checked all six D18 variants directly (17 D18 rows;
each variant present in 1–4 queries).

**Measurement 2 — strongest collisions have backward (`B`) and forward (`C`) chaining rows in
`subject_source_id`. FAIL: 15 missing against a gate of 0.** Population: 39 matrix rows with
either overlap score ≥ 3. Reproduced exactly by the coordinator's own computation. The 15:

```text
B=0 C=0: epistemic-sybil-resistance-bara-2026, eywa-provenance-grounded-memory-joshi-2026,
         dong-berti-equille-srivastava-truth-discovery-copying-detection-2009,
         memtx-transactional-belief-commit-2026, goldman-experts-which-ones-should-you-trust-2001
B>0 C=0: toki (B=2), mythologiq (B=1), subit-wiki (B=1), barakat (B=3),
         extending-nanopublications (B=1), provenance-based-interpretation-2020 (B=1),
         reliability-testimonial-norms (B=1), runtime-verification-2023 (B=1),
         souza-awareness-requirements-seams-2011 (B=1), requirement-evolution-seams-2012 (B=1)
```

The pattern is structural, not sloppy: all 15 entered the matrix in `phase-lit-06` or
`phase-lit-08`, after the campaign's chaining passes (`phase-lit-04`/`phase-lit-05`) had already
run, and no later phase re-ran forward chaining over the additions. Chaining is search work; no
`LIT-07` section performs searches, so this failure is recorded, not fixed.

**Measurement 3 — every H1–H11 has ≥1 serious challenger with a permitted status in
`06_hypothesis_tests.md`. PASS: 11 of 11**, statuses 4 `LIKELY_ALREADY_KNOWN`, 5
`KNOWN_COMPONENT_NEW_INTEGRATION`, 2 `INSUFFICIENT_EVIDENCE` (H1, H11), 0 `POTENTIALLY_DISTINCT`,
0 `NOVEL`.

**Measurement 4 — matrix rows 20–30, no blank required fields. Split.** Blank cells: **0 across
49 rows × 43 fields = 2,107 cells — PASS.** Row count: **49, above the stated 20–30 band.** The
methodology's stop condition "strongest 20–30 sources deeply compared" is exceeded on count. The
owner-ruled caveat stands and is carried verbatim: the condition is met by COUNT and not by
COVERAGE of the top prescore band — 340 of 387 collision candidates were never deep-read,
including 20 of 32 in the top band. Both facts are reported; neither is asserted away. (The first
gate run instead tested rows *indexed* 20–30 for two fields that exist only in the inventory and
reported 22 blanks in nonexistent columns; see Corrections.)

**Measurement 5 — saturation, the trend reported and nothing asserted (ruling 8).** Recorded,
twice-independently-reproduced figures: `phase-lit-06` 44/220 = 20.0%
([SESS-2026-09-14-01](SESS-2026-09-14-01-literature-review-pass-3.md)), `phase-lit-08` 58/387 =
15.0% ([SESS-2026-09-14-07](SESS-2026-09-14-07-literature-review-pass-3b.md)). The trend across
the last two search phases is FALLING, the opposite of "rising duplicates = saturation
demonstrated". **The stop condition is not demonstrated, and per ruling 8 this phase does not
claim it.** This phase itself ran only 16 bibliographic-verification lookups (2 of 19 kept
identifiers already in the inventory), which are not collision searches and carry no saturation
signal.

**Measurement 6 — every critical collision second-reviewed. PASS.** Population: 24
`critical_collision: yes` rows of 49. 0 pending; 11 confirmed, 13 disputed.

**Measurement 7 — deliverables. PASS: 14 of 14 present** (`00_search_ledger.csv` through
`13_validated_bibliography.md`), the thirteen numbered deliverables plus the ledger.

**Measurement 8 — A-review blocking findings. PASS: 0 unaddressed-and-unrecorded.** 3 blocking
findings, all addressed in `LIT-07 X1` fix cycle 1 (commits `c24a8ee`, `0a15400`, `e7e2828`) and
verified in the files by the gate and the coordinator separately; 1 observation (four inventory
rows still `status: candidate` despite having matrix rows) recorded here for the owner rather
than fixed — no dispatch in this phase owns the inventory.

## Acceptance

- **All seven synthesis deliverables (07–13) exist; every synthesis claim traces to a primary
  source with a locator, and 08 lists only distinctions that survive 07's strongest decomposition
  argument** — **Met.** The seven files exist (verified at close). Traceability was audited
  adversarially by `LIT-07 A` against the matrix, which confirmed the status vocabulary clean
  (no `NOVEL`, no "no prior work exists"), the three synthesis categories kept separate, and
  `08`'s placements matching `06`'s eleven verdicts one-for-one; the representation gaps it did
  find (three blocking, three should-fix) were fixed in one X1 fix cycle and verified in the
  files by the coordinator.
- **The A review ran against the evidence matrix and its findings are applied or recorded; the
  final gate measurements show the methodology's stop conditions met against the ledger and
  matrix, demonstrated rather than declared** — **Not met, in its second half.** The A review ran
  and every finding is applied or recorded (measurement 8: 0 unaddressed-and-unrecorded). But the
  gate does not show all stop conditions met, and saying otherwise would be the declaration the
  condition forbids: measurement 2 fails outright (15 of 39 strong collisions lack chaining
  rows), measurement 5's saturation is not demonstrated (the duplicate rate is falling, and
  ruling 8 forbids asserting the condition), and measurement 4's count is outside the stated band
  with the count-versus-coverage caveat standing. The synthesis work is complete; the campaign's
  stop conditions are measured and not all hold.

## Backlog

`phase-lit-07` — `status: active`, `agent: agent-lit`. Left active for the owner's
`/session-close`; an agent never marks a phase complete.

`next_action`: as written to `backlog.yaml` this run — the owner's `/session-close`, with three
campaign-level facts the close must weigh: the gate's measurement 2 fails (15 late-added strong
collisions never chained, a search gap no synthesis dispatch can close); saturation is not
demonstrated and ruling 8 forbids claiming it (duplicate rate fell 20.0% → 15.0%); the "strongest
20–30 deeply compared" condition is met by count, not by coverage (20 of 32 top-band candidates
never deep-read). Whether any of the three warrants a ninth session is the owner's call — the
runway estimate of seven sessions is already exceeded by one, inside the accepted range's top end.

`completion_evidence` (files that exist now): the fourteen files of
`research/literature-review/` — ledger, inventory, matrix, terminology and domain maps,
`05`–`13`.

`next_up`: unchanged; nothing became `complete` this session.

## Unresolved

- **Measurement 2's real failure**: 15 of 39 strong-collision sources have no forward-chaining
  ledger rows, 5 of them no backward-chaining rows either. All 15 post-date the chaining passes.
- **Saturation is not demonstrated** and the trend runs away from it. `phase-lit-07` was
  synthesis; the number could not improve here and did not.
- **The top-band coverage gap stands**: 340 of 387 collision candidates never deep-read, 20 of 32
  in the top prescore band. Recorded in every synthesis deliverable's coverage caveat.
- **H4's `KNOWN_COMPONENT_NEW_INTEGRATION` status is carried, not settled.** The dispatch-framing
  caveat from `phase-lit-08` travels through `06`, `08`, `11` and `12`; a clean-room re-derivation
  remains the owner's call.
- **Inventory hygiene, from the A review**: four rows are `status: candidate` despite having
  matrix rows, so a naive inventory-status recount of "never deep-read" gives 341 against the
  recorded 340 (a method difference, not an authoring error); and two duplicate `source_id` rows
  (`memtx-transactional-belief-commit-2026`,
  `semantically-seeded-graph-propagated-impact-analysis-vision-2026`) mean the inventory's row
  count is not a distinct-source count. Both pre-date this phase.
- **Two bibliography seeds failed verification** and are recorded with the failing step named in
  `13_validated_bibliography.md`: the Context Objects SSRN paper (primary page returns HTTP 403)
  and The Loom (`jpwinans/the-loom` does not exist on the account, confirmed by full API
  enumeration).
- **Carried from earlier phases**: `000221` (the evidence contract still names `LIT-06 X2` as
  `second_review`'s sole writer), `000148` (the `source_type` enum gaps), `000224` (a phase
  silently leaving `complete` fails no check; `phase-gov-05` is queued for it).

## What was dispatched

Item order `K → X1 → X2 → X3 → A → G`, per `LIT-07 K`. All models per the pack: `K` and `G` on
Haiku, the rest on Sonnet.

**`K` (Haiku).** Confirmed the dated check-in entry in `PROMPT-031` (held 2026-09-14, ruling:
proceed) before anything else was dispatched. Claimed `phase-lit-07` on `dev` in `9ea0eaf` with
the catalog regeneration the claim forces — the only work `AGENTS.md` permits in the primary
checkout — then rebased `agent/lit-campaign` onto the claim. Verified prior evidence by line
count rather than recreating anything.

**`X1` (Sonnet), one fix cycle.** Item 0 executed as a verification, not a redo: the `06`
reconciliation ran in `phase-lit-06` and `phase-lit-08` rewrote the H1/H4/H11 blocks; `X1` read
all 24 dated review subsections in `05` against the blocks, found no undisclosed undercutting
beyond the two already handled, and committed nothing for item 0. Then `07_anti_novelty_case.md`
(`dfad39f`, 474 lines — the §14 fourteen-component decomposition, ~38 matrix sources with
locators) and `08_surviving_distinctions.md` (`c9260e1`, 252 lines — all eleven readings sorted
into the methodology's three categories, H4 and H8 kept split by phrasing). The fix cycle came
later, from the A review (below).

**`X2` (Sonnet).** `09_reuse_recommendations.md` (`bffd069`, 11 recommendations each traced to
matrix rows), `10_architecture_implications.md` (`85f8dd2`, recorded implications only),
`11_open_research_questions.md` (`741a7b7`, 12 questions), `12_experiment_proposals.md`
(`4b8de26`, 3 experiments, all tied to `INSUFFICIENT_EVIDENCE` readings since nothing ended
`POTENTIALLY_DISTINCT`; for H4 it read the block's own assessment and tied Experiment 2 to the
frozen-register graph-topological phrasing specifically, reasoning documented in the file).

**`X3` (Sonnet).** `13_validated_bibliography.md` (`6cd44aa`, 327 lines): 45 of the matrix's 49
rows confirmed cited by the synthesis (the 4 unused named and excluded), plus the nine
`research/sources/` seeds through the contract's five steps — 6 promoted, 1 promoted with a
recorded step-3 caveat, 2 failed with the failing step named. 16 verification lookups logged as
`LIT-07-S001`–`S016` (`strategy_phase: D`, the enum-gap convention from `phase-lit-01`), appended
in binary mode: the ledger left at 1,095 data rows, 1,096 lines, all CRLF, 15 fields on every
row, verified whole-file by the coordinator.

**`A` (Sonnet, fresh agent).** Received the four pack-named inputs and none of the authors'
reasoning. 9 findings: 3 blocking (H2/H7/H9 cite two "ceiling score 5" rows whose
`second_review` disputes re-derive them to 4/3 and 3/2 with no in-block disclosure; a stale
"34 rows" denominator against the 49-row matrix; H3 counting 9 challengers against 11 tagged,
omitting a row whose automated conflict-resolution mechanism bears on H3's central claim),
3 should-fix (H5 count, H10's `abstract_only` mislabel against the matrix's `full_text`,
absolute language exceeding the coverage caveat), 3 observations (a misquote in `07` §8, the
inventory-status hygiene gap, a Snodgrass shared-ancestry cross-reference). Its vocabulary,
category-separation, ruling-compliance and arithmetic checks all came back clean. The
coordinator verified every blocking finding against the files before opening the fix cycle.

**`X1` fix cycle 1 (of 2).** All findings addressed across `06`/`07`/`08` (`c24a8ee`,
`0a15400`, `e7e2828`): disputes disclosed with scores left standing per ruling 1, denominators
corrected to 49, H3 reworked to 11 rows with both added rows argued through — its status held at
`KNOWN_COMPONENT_NEW_INTEGRATION` under the block's own stated rule, with the reasoning in the
file — H5 and H10 corrected, the quotation's invented second typo fixed back to the paper's
actual one, absolute phrasing softened, the ancestry cross-reference added. Zero `status:`
tokens changed anywhere (verified by diff); H1/H4/H6/H8/H11 blocks byte-identical before and
after.

**`G` (Haiku), one fix cycle.** First run: 5 of 8 pass, 3 fail. The coordinator verified all
three failures before acting — two were the gate's own method errors (measurement 1 counted
D18's domain title as a mandated variant; measurement 4 read "rows 20–30" as an index range and
tested two inventory-only field names against the matrix, reporting 22 blanks in columns that do
not exist), one was real and reproduced exactly (measurement 2). Fix cycle 1 re-took
measurements 1 and 4 with the corrected method and corrected a misattribution in its
measurement-8 note. Final: measurements 1, 3, 5-as-trend, 6, 7, 8 pass; measurement 2 fails;
measurement 4 splits (blanks pass, count above band with the caveat carried).

## Coordinator decisions

**Two gate failures were not sent back and one was.** `phase-lit-01` produced one real gate
failure and one artifact of the gate's own method, needing different responses; this gate
produced one real failure and two artifacts. The artifacts went back as a fix cycle because the
responsible section for a mismeasurement is the gate itself. The real failure (measurement 2) was
not looped on: chaining is search work, no `LIT-07` section runs searches, and a missing prompt
is a blocking finding, never something to improvise — so it is recorded for the owner instead.

**The A findings went to `X1` as one fix cycle, direction withheld.** The dispatch stated the
defects verbatim and did not say which way to resolve; `X1`'s item-0 rule governed whether any
status changed. None did, and the H3 judgment call — the new automated-conflict-resolution row
reinforces rather than overturns the block's reading — is argued in the file, not asserted.

**The `LIT-07 A` assembly reading.** The pack's dispatch-rules list gives no explicit assembly
for `A`; it was assembled as Block C + the section, the same shape as an `R` review dispatch,
since `A` is a review. Recorded here because it is an interpretation, however small.

## Corrections

**The gate's first run got three things wrong; all three were caught by verification, none
propagated.** The D18 variant-list error and the measurement-4 contract error are described
above. Its measurement-8 note also attributed the recorded inventory-status finding to idea
`000150`, which concerns the private-content check and is unrelated; the finding is recorded in
this session record. The fix cycle corrected all three.

**No coordinator number is known to be wrong at close.** Every figure in this record was
re-measured after the final commit, per the standing rule from `phase-lit-08`'s three
mid-phase-measurement errors; the coordinator's independent computation of measurement 2
reproduced the gate's 15/39 exactly, and its measurement-4 and measurement-1 checks are what
exposed the gate's artifacts.

## Owner-directed side work in this session

Recorded here because it happened within this session, on its own branch, not the campaign's.
The owner asked whether the campaign keeps saved copies of referenced sources (it does not), then
directed the ask be captured and planned. On `agent/source-archival` (unclaimed, per `AGENTS.md`'s
owner-directed-work rule, worktree `../d-system-worktrees/source-archival`): idea `000232`
(archive referenced literature sources) recorded via the sanctioned writer (`ae8f155`), triaged by
the idea-triage agent — no existing plan, phase or document covers it — and moved to `triaged`
(`9297200`); then the source-archival plan (`PLAN-039`,
`docs/01-plans/PLAN-039-literature-review-source-archival.md`) written with one queued
requirements-and-design phase, `phase-arc-01` (`aedcd9b`). Governance exits 0 on that branch.
Promotion of `000232` onto `PLAN-039` and integration of the branch are the owner's.

## Spend posture

- **Searches**: 16 this phase, all bibliographic-verification lookups
  (`LIT-07-S001`–`S016`); ledger now 1,095 rows. No collision searches — this phase is synthesis.
- **Sources deep-read**: 0 new matrix rows; the matrix closes at 49 rows × 43 fields, 0 blanks.
- **Fix cycles**: 2 — one against `X1`, one against `G`, each the first of its work item's two.
- **Opus escalation**: none spent, in this session or the campaign. The campaign ends with its
  one escalation unused.
- **Descope rung**: none taken, in this session or the campaign.
- **Runway**: 8 of 8 sessions used — the top of the owner-accepted six-to-eight range, one past
  the seven-session estimate (`phase-lit-08` was the unplanned addition). The campaign has no
  further phases; anything more is new scope for the owner to direct.

## Resume state

**Current phase**: `phase-lit-07`, `active`, all six items dispatched and verified, left active
for the owner's `/session-close`. Acceptance 1 Met; acceptance 2 Not met in its
stop-conditions half, for the reasons measured above — that is a fact about the campaign's
evidence, not unfinished synthesis work.

**The campaign is at its end.** No `phase-lit-*` phase remains after this one. What remains is
the owner's:

1. `/session-close` on `phase-lit-07`, weighing whether acceptance 2's unmet half blocks
   completion or is recorded as the campaign's honest result — the deliverables themselves state
   it either way.
2. The second owner integration of `agent/lit-campaign` into `dev`, scheduled by `PLAN-023` at
   campaign close. The branch is rebased, clean, governance 0, 580 tests passing, 11 commits
   ahead of `dev` (the claim commit `9ea0eaf` is already on `dev`; the 11 are this session's
   work and record). Review with `git diff dev..agent/lit-campaign`.
3. Whether measurement 2's chaining gap, the undemonstrated saturation, or the top-band coverage
   gap warrants a ninth session of search work — `11_open_research_questions.md` Q11–Q12 and the
   coverage finding in [SESS-2026-09-14-07](SESS-2026-09-14-07-literature-review-pass-3b.md)
   carry the material a planning decision needs.
4. On the side branch: promotion of `000232` to `PLAN-039`, and integration of
   `agent/source-archival` (3 commits — idea, triage, plan).

**The `lit-campaign` worktree must be retained until integration** — removing it destroys its
gitignored `.venv` and `data/`, which no merge carries. The same holds for
`../d-system-worktrees/source-archival` until that branch integrates.

**A fresh session picking any of this up must read**: `AGENTS.md`, `GOV-006`, `PROMPT-031` (both
the check-in section and the `phase-lit-08` mapping section), `PROMPT-030`, then this record.
