---
schema_version: 1
id: doc-session-literature-review-pass-4-close
code: SESS-2026-09-20-01
title: Literature review Pass 4 close — the owner's closing ruling recorded, 07 reconciled and the final gate re-measured
kind: session
status: active
owner: repository-owner
created: '2026-09-20'
updated: '2026-09-20'
systems:
- sys-research
depends_on:
- doc-lit-campaign
---

# Literature review Pass 4 close — the owner's closing ruling recorded, 07 reconciled and the final gate re-measured

## Phase

`phase-lit-07` — Literature review Pass 4: synthesis, adversarial synthesis review and validated
bibliography. Re-claimed under `agent-lit`, which holds the phase's history; it had been released
to `queued` at `phase-lit-09`'s close with nobody working it.

Work ran on `agent/lit-campaign` in the retained `lit-campaign` worktree, on the owner's direction
— the campaign convention every `phase-lit-*` has used. The branch had nothing ahead of `dev` and
the rebase fast-forwarded it. This does not match `AGENTS.md`'s `agent/<phase-id>` rule, and that
mismatch is the known open gap `SESS-2026-09-19-01` recorded; it is not resolved here.

## What this session did

The phase's remaining work was three edits, not a search or synthesis pass. The synthesis
deliverables `07`–`13` were written at the 2026-09-14 session and stand.

1. **The owner's 2026-09-20 closing ruling written into `PROMPT-031`** as rulings 9 and 10, its
   authoritative home. The full reasoning was recorded in `SESS-2026-09-19-08`'s addendum, which
   names writing it into the kick-off record as the first work of whichever session claims the
   phase — a per-campaign ruling that lives only in one session record among 120 is a ruling
   nobody finds.
2. **`phase-lit-07`'s acceptance amended** so its stop-conditions half requires the measurement
   rather than the condition. Scope and acceptance condition 1 are untouched.
3. **`07_anti_novelty_case.md` reconciled** to `06`'s and `08`'s unified H4 status.

### Where the ruling was filed, and why not where the addendum said

The addendum asked for the ruling "alongside check-in rulings 1-8". It was filed as its own dated
section, `## How phase-lit-07 closes (owner ruling, 2026-09-20)`, immediately before the kick-off
paragraph, rather than appended to the pre-synthesis check-in list.

`PROMPT-031`'s `phase-lit-08` section states the convention explicitly: a later ruling gets its own
section "so a reader looking for what the check-in decided does not find an unrelated ruling mixed
into it". The check-in was held on 2026-09-14; filing a 2026-09-20 ruling inside it would misdate
it. Check-in ruling 8 gained a forward pointer, so a reader arriving at ruling 8 — the one this
ruling extends — finds the extension without reading to the end. **Flagged for the owner:** if
"alongside" meant literally inside the numbered list, this is a one-line move.

## Verification

### `uv run python -m src.governance`

```
Governance OK: 35 systems, 297 documents, 26 memories, 288 backlog phases
```

Exit code 0.

### `uv run python tools/check_no_private_content.py` with changes staged

In the worktree the content half does not run, because `_private/portfolio/` is gitignored and
never travels to a worktree:

```
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (739 tracked files, 0 identifiers checked)
```

The run that actually checks content happened in the primary checkout, where `_private/` exists:
`check_no_private_content: OK (739 tracked files, 31 identifiers checked)`. A worktree-only run
would have passed by not looking, which is the failure mode `AGENTS.md` names.

## `LIT-07 G` — the final gate, re-measured 2026-09-20

Dispatched per `PROMPT-029` Block G + the `LIT-07 G` section, Haiku, payload narrowed only. The
2026-09-14 run measured against a 1,095-row ledger and a 49-row matrix; `phase-lit-08` and
`phase-lit-09` have since run, so every measurement was re-taken against the files as they stand.
**One fix cycle of the two available was used.** Populations are named per Block G.

| # | Stop condition | Measurement | Population |
|---|---|---|---|
| 1 | Domain coverage | **Met.** 0 domains below 2 distinct queries; min D48 = 6, max D38 = 42. Variants 337/339 literal, **339/339 substantive** | 72 D-domains; 339 mandated variants from the Pass 1 `S` payloads |
| 2 | Chaining | **Met.** 0 missing `strategy_phase: B`, 0 missing `strategy_phase: C` | 53 matrix rows with either overlap score ≥ 3 |
| 3 | Challengers | **Met.** All 11 carry a named strongest challenger and a permitted status; no `NOVEL` verdict | H1–H11 in `06_hypothesis_tests.md` |
| 4 | Matrix completeness | **Blanks met; band exceeded.** 0 blank cells; 67 rows against a 20–30 band | 43 required fields × 67 rows = 2,881 cells |
| 5 | Saturation | **Measured, NOT demonstrated.** 20.0% → 15.0% → 6.4–7.7%, falling | `phase-lit-06` 44/220, `phase-lit-08` 58/387, `phase-lit-09` 25–30/392 |
| 6 | Second review | **Met.** 0 pending — 12 confirmed, 18 disputed | 30 `critical_collision: yes` rows |
| 7 | Deliverables | **Met.** 14 files present, `00` through `13` | `research/literature-review/` |
| 8 | A-review findings | **Met.** 0 unaddressed-and-unrecorded; all 3 blocking findings addressed | `LIT-07 A`, 2026-09-14 |

Measurement 5 is reported as a trend and **not asserted**, per check-in ruling 8 and ruling 9. On
this evidence saturation is not demonstrated: more than nine results in ten are new. Recording it
unmet is the required outcome under the amended acceptance, not a gate failure.

### The gate mismeasured three times, and the coordinator's recomputation caught it

This is the third consecutive campaign gate to report a false result from a method error, and the
pattern is worth naming rather than filing as three incidents.

- **Measurement 1 first half — false FAIL.** The gate restricted the row population to
  `strategy_phase: A` and reported D48 and D57 failing with 1 query each. The measurement states no
  phase restriction. Over all ledger rows D48 has 6 distinct queries and D57 has 10, and no domain
  is below 2. Corrected in fix cycle 1; the gate reproduced 0 failures.
- **Measurement 1 second half — not taken.** The first run audited 12 of 72 domains and reported
  "full 72-domain variant audit not completed". An unmeasured condition is neither a pass nor a
  fail, and the amended acceptance requires it measured. Completed in fix cycle 1.
- **Measurement 4 — narrowed scope, PASS on 16% of the population.** The gate read "rows 20–30" as
  a line range and measured 11 rows × 43 fields = 473 of 2,881 cells. This is the identical error
  the 2026-09-14 gate made and that its own fix cycle 1 corrected; it recurred with the contract
  text unchanged. The full-matrix re-measure holds at 0 blanks, so the conclusion survives — but it
  was a PASS reported on the part it skipped, which is the failure Block G names in writing.
- **Measurement 1 variant coverage — false FAIL surviving fix cycle 1.** The re-run failed D21 and
  D33 for missing `cognitive architecture (SOAR, ACT-R)` and `goal-oriented RE (KAOS, i*)`. Those
  parentheticals are notation for "these examples", not query strings to reproduce verbatim. D21's
  ledger carries `working/long-term memory taxonomy cognitive architecture SOAR/ACT-R` and D33's
  carries `goal-oriented RE KAOS/i* framework comparison`; every component appears. Settled by the
  coordinator's own verification rather than the second fix cycle, per Block G's rule that what
  survives a cycle is reported, not looped on.

Measurements 2, 4, 6 and 7 were independently recomputed by the coordinator before the gate
reported, and 1's two halves afterward. Every number in the table above was reproduced
independently. **The gate's unreviewed output would have failed this phase on two conditions that
are met.**

## A finding the coordinator's own recomputation produced

**The duplicate rate rests on a tokenisation rule that is not written down**, and the "settled
denominator" language carried from `SESS-2026-09-19-08` overstates what is settled.

Recomputing `phase-lit-09`'s denominator from the ledger gives **402 result identifiers, 387
distinct**, against the **392** that record calls settled. The comma-split defect would give 652,
so this is not that defect recurring. The cause is that `result_ids` holds free-text citations
alongside source ids — 136 of the distinct tokens are strings like
`Salton, G., Buckley, C. (1988) Term-Weighting Approaches in Automatic Text Retrieval...` and
`dawid-skene-1979-observer-error-em (not in inventory)`. Under different defensible tokenisation
rules the denominator is 387, 392 or 402.

This is idea `000289`, captured last session and deliberately not fixed: amending a governed
evidence contract mid-campaign needs its own requirement and plan. What is settled is the
**direction** — under every tokenisation the rate lands far from "mostly duplicates". The precise
figure is not settled, and the campaign should stop describing it as though it were. This
strengthens ruling 10 rather than weakening it.

## `07_anti_novelty_case.md` — what the reconciliation changed

Dispatched as `LIT-07 X1` with a narrowed payload under the pack's idempotency rule: `06` and `08`
already existed and were current, so they were read-only and the write scope was `07` alone.
Nine of the ten recorded stale lines changed; **line 168 needed no change** — it restates the
hypothesis and carries no status claim, so it was left byte-identical.

- **§6 Truth Discovery.** Previously split H4 by phrasing — general at
  `KNOWN_COMPONENT_NEW_INTEGRATION`, graph-topological at `INSUFFICIENT_EVIDENCE` — and carried the
  `phase-lit-08` pre-framing caveat. Now reports `06`'s H4 block, re-derived clean-room by
  `LIT-09 H4R`, placing **both phrasings at `LIKELY_ALREADY_KNOWN`**, and records the caveat as
  resolved along with the split. The four evidence bullets (Dong 2009, Goldman 2001, DIVE 2020,
  Bara 2026) are untouched.
- **Synthesis grouping.** H4 moved into the `LIKELY_ALREADY_KNOWN` group. The **"nine of eleven"
  tally is unchanged** — H4 was already one of the nine, under the wrong group.
- **"Does not fully decompose" list: three items → two** (H1, H11). H4's item had no remaining
  subject. This now matches `08_surviving_distinctions.md`'s Category 3 exactly.

Traceability was checked rather than taken on trust. The two 2026 sources the reconciliation newly
names — `grading-narrators-isnad-rijal-claim-provenance-2026` and
`not-all-agreement-counts-as-corroboration-2026` — each carry a matrix row and are assessed in
`06`'s H4 block (11 and 6 references respectively).

## Acceptance

1. **All seven synthesis deliverables exist; every synthesis claim traces; 08 lists only
   distinctions surviving 07's strongest decomposition argument — Met.** `07`–`13` present
   (measurement 7). The 2026-09-14 close review judged this condition Met and audited traceability;
   this session's only change to a deliverable was `07`'s reconciliation, whose two new source
   claims were verified to trace. `08`'s Category 3 (H1, H11) now matches `07`'s list exactly,
   where before the reconciliation `07` carried a third item `08` did not.
2. **The A review ran and its findings are applied or recorded; the final gate takes all eight
   stop-condition measurements against the files as they stand, each population named, saturation
   reported as a trend with no assertion — Met.** The `A` review ran 2026-09-14 with 0
   unaddressed-and-unrecorded blocking findings (measurement 8). All eight measurements were taken
   against the current files with populations named, and saturation is reported as a falling trend
   and explicitly not demonstrated.

Condition 2 is met **as amended this session**. Against its pre-amendment wording it would fail, as
it did on 2026-09-14 — the amendment is the owner's ruling, not a reinterpretation by this session.

## Spend

One session. Three dispatches: `LIT-07 X1` re-dispatch (Sonnet), `LIT-07 G` (Haiku), `LIT-07 G`
fix cycle 1 (Haiku). One of two fix cycles used. **No Opus escalation spent** — the campaign's
single permitted escalation remains unspent. Nine sessions used against a seven-session estimate
and an owner-accepted range of six to eight; this is the tenth session but the first that ran no
searches, and ruling 10 forbids a tenth *search* session.

## Unresolved

- **The campaign's saturation stop condition is not met and will not be met by more searching.**
  Recorded per rulings 9 and 10.
- **The duplicate-rate tokenisation gap** (idea `000289`) — the denominator varies with an unwritten
  rule; see the finding above. Needs its own requirement and plan.
- **Two duplicate inventory rows**, carried from `phase-lit-09` and deliberately unrepaired:
  `epistemic-sybil-resistance-multiplying-agents-2026` / `epistemic-sybil-resistance-bara-2026`,
  and `dhar-vaidhyanathan-varma-agenticakm-2026` / `dhar-vaidhyanathan-varma-agenticakm-2026-arxiv`.
- **18 of 30 critical-collision flags are recorded `disputed`**, three of them concluding no trigger
  fires. Under check-in ruling 1 nothing was applied. Whether that changes the campaign's headline
  collision count remains the owner's scoping decision, unchanged by this session.
- **`06_hypothesis_tests.md` cites a commit hash that does not exist on the branch** — the preamble
  names `7141767` for `H4R`; a rebase rewrote it. Carried from `phase-lit-09` unfixed, since a hash
  cited inside a file on a rebasing branch drifts again.
- **The gate's recurring method errors** are a campaign-level pattern, not three incidents. Three
  consecutive gates have reported false results that only the coordinator's independent
  recomputation caught. A gate that is trusted without recomputation would have failed this phase
  twice on conditions that are met.
- **The branch-naming gap** — `agent/lit-campaign` does not match `agent/<phase-id>`, so the
  stale-claim signal reports "no evidence" for this claim. Recorded in `SESS-2026-09-19-01`;
  belongs to a follow-up.
- **40+ commits remain unpushed.** `git push origin dev` was refused by the environment's
  permission classifier last session and was not worked around. All nine sessions of campaign
  evidence exist on this machine only.

## Backlog

`phase-lit-07` stays `status: active` under `agent-lit`. **No phase was marked complete in this
session** — completion is the owner's `/session-close`, and an agent never invokes final closure
itself.

`next_action`: Both acceptance conditions measured Met against the amended acceptance; ready for
the owner's `/session-close` review and the second owner integration of `agent/lit-campaign` into
`dev`. The branch is green and rebased on `dev`; `git diff dev..agent/lit-campaign` shows it. If
the owner reads "alongside check-in rulings 1-8" as requiring the ruling inside the numbered
check-in list rather than its own dated section, that is a one-line move.
