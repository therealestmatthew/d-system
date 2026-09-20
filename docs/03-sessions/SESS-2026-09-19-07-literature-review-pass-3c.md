---
schema_version: 1
id: doc-session-literature-review-pass-3c
code: SESS-2026-09-19-07
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
| Duplicate rate | 642 result identifiers across 105 `LIT-09` searches, against the pre-phase inventory of 1,123 rows | 67/642 = 10.4% |
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
- **Measurement 5** — saturation trend: **20.0% (`phase-lit-06`) -> 15.0% (`phase-lit-08`) -> 10.4%
  (this phase)**. The rate is **falling**. Per check-in ruling 8 the trend is reported and saturation
  is not asserted; on this evidence it is not demonstrated either, and close to nine results in ten
  were new.

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
4. **Met.** The duplicate rate was measured against the pre-phase inventory of 1,123 rows and reported
   against `phase-lit-08`'s 58/387 = 15.0% as a trend. No saturation assertion was made, in either
   direction, per check-in ruling 8's standing form.
5. **Met.** `LIT-07 G` measurements 2, 4 and 5 are re-measured against the updated files and recorded
   in `## Verification` above.

All five conditions are met on the evidence recorded here. The phase stays `active`: only the owner's
`/session-close`, after its own independent review, moves a phase to `complete`.

## Backlog

`phase-lit-09` — `status: active`, `agent: agent-lit-3c`.

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
  read 20 when the true figure was 19.
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
