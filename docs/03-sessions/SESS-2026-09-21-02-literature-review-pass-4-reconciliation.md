---
schema_version: 1
id: doc-session-literature-review-pass-4-reconciliation
code: SESS-2026-09-21-02
title: Literature review Pass 4 reconciliation — 09-13 reconciled against the retired H4 split, populations re-measured, the campaign's last phase closed
kind: session
status: active
owner: repository-owner
created: '2026-09-21'
updated: '2026-09-21'
systems:
- sys-research
depends_on:
- doc-lit-campaign
---

# Literature review Pass 4 reconciliation
## Phase

`phase-lit-07` — Literature review Pass 4: synthesis, adversarial synthesis review and validated
bibliography. Resumed under `agent-lit`, which has held the phase throughout. This session ran no
searches and wrote no new synthesis; it is the reconciliation pass the close review of 2026-09-21
required before the phase could close.

`phase-lit-07` is the campaign's last open phase. `phase-lit-01` through `06`, `08` and `09` are
all `complete`, verified from the backlog at session start.

## Verification

Run in the worktree at `0c6636e`:

```
$ uv run python -m src.governance
Governance OK: 35 systems, 304 documents, 28 memories, 292 backlog phases
EXIT=0

$ uv run pytest
651 passed, 2 warnings in 51.44s
EXIT=0
```

`uv run python tools/check_no_private_content.py` reported
`OK (759 tracked files, 0 identifiers checked)` in the worktree. **That is not a passing content
verification** — `_private/portfolio/` is gitignored and never travels to a worktree, so the tool
builds an empty identifier list and passes by not looking. The run that checks content happens in
the primary checkout and is recorded below.

## Acceptance

1. **All seven synthesis deliverables exist; every synthesis claim traces to a primary source with
   a locator; `08` lists only distinctions surviving `07`'s strongest decomposition argument —
   Met.** `07`–`13` present. The three defects that failed this condition on 2026-09-21 are closed:
   `09`–`12` reconciled to `06`'s single H4 status token, `13` complete by its own definition at 48
   Part A entries with zero cited sources missing and zero entries outside the matrix, and every
   stale population figure re-measured across `06`–`13`. Three fabricated or overclaimed
   quotations were removed. The independent review re-derived each check and judged the condition
   **HOLDS**.
2. **The `A` review ran and its findings are applied or recorded; the final gate takes all eight
   stop-condition measurements against the files as they stand, each population named, saturation
   reported as a trend with no assertion — Met.** `LIT-07 A` ran 2026-09-14 with 9 findings, all
   addressed in one fix cycle. All eight measurements were taken against current files, every
   population named, and saturation reported as a falling trend and explicitly **not**
   demonstrated. The independent review judged the condition **HOLDS**.

## Backlog

`phase-lit-07` is the campaign's last open phase; `01`–`06`, `08` and `09` are all `complete`.

Written to `backlog.yaml` this run: `status: active`, `agent: agent-lit`, holding
`sys-research`. `phase-lit-07` is not in `next_up`, so nothing was pruned.

Completion follows `GOV-003`'s three conditions: the verification commands are green with real
output recorded above, the independent adversarial review has run and returned **safe to mark
complete**, and the third condition — **integration onto `dev` with the owner's approval** — is
unchanged and is asked for every phase. The completion edit is one small commit on `dev`
immediately after that integration, and not before.

## Unresolved

- **Saturation is measured and explicitly not demonstrated.** Unchanged by this session and not
  addressable by more searching, per rulings 9 and 10.
- **The duplicate-rate tokenisation gap** — idea `000289`, now joined by `000307` and `000308`.
  All three need their own requirement and plan; a governed evidence contract is not amended
  mid-campaign.
- **Two duplicate inventory rows and two near-duplicate pairs**, deliberately unrepaired.
- **18 of 30 critical-collision flags are recorded `disputed`.** Under check-in ruling 1 nothing was
  applied. Whether that changes the campaign's headline collision count remains the owner's scoping
  decision, unchanged by this session.
- **`06` cites a commit hash that does not exist on the branch** — the preamble names `7141767` for
  `H4R`; a rebase rewrote it. Carried from `phase-lit-09` and still unfixed, since a hash cited
  inside a file on a rebasing branch drifts again.
- **The branch-naming gap**, recorded above.

## The branch and worktree were gone, and were recreated from `dev`

At session start `../d-system-worktrees/lit-campaign` did not exist and there was no local
`agent/lit-campaign`. Nothing was lost: `origin/agent/lit-campaign` was 0 ahead of `dev` and 497
behind, and all fourteen deliverables plus the frozen baseline were already on `dev`. The owner
directed recreation from `dev`, and the worktree was rebuilt at `7ab8cb8` with its own `.venv`.

The campaign's branch-naming gap is unchanged and unresolved: `agent/lit-campaign` does not match
`AGENTS.md`'s `agent/<phase-id>` rule, so the stale-claim signal reports "no evidence" for this
claim. Recorded in `SESS-2026-09-19-01`; it belongs to a follow-up, not to this phase.

## Preflight

```
Governance OK: 35 systems, 303 documents, 28 memories, 292 backlog phases   (exit 0)
Active claims: 1 of 3 — phase-lit-07 / agent-lit / sys-research
git status --short — clean
```

**Baseline integrity verified against `PROMPT-031`'s pinned identity**, not merely asserted: the
frozen baseline is last touched by commit `b2b564b`, `research/pre-literature-baseline.md` is blob
`635bcfa`, `research/pre-literature-hypotheses.yaml` is blob `a53ecdb`, and
`research/adversarial-codebase-review/` is unmodified. All three match the pinned values exactly.

No peer claim overlaps `sys-research`. `phase-lrr-01` declares `sys-research` and therefore shows
`phase-lit-07` in its Conflicts column; it was not claimed, and nothing in this session touched it.

## What this session did

The close review of 2026-09-21 judged acceptance condition 1 **not met** on three counts. All three
were re-measured by the coordinator before any dispatch, and all three reproduced:

| Finding | Coordinator's own measurement |
|---|---|
| Deliverables carry "49 rows, 24 flagged" | matrix measures **67 rows, 30 flagged** |
| `09`/`12` say `06`'s H4 block reads `KNOWN_COMPONENT_NEW_INTEGRATION` | `06:793` reads **`LIKELY_ALREADY_KNOWN`**, one token |
| `12:19` quotes a sentence attributed to `06` | **0 occurrences** of that string in `06` |
| Two sources `07` cites are absent from `13` | **0 occurrences** each in `13`, 1 each in `07` |

The stale coverage caveat was **wider than the close review recorded** — present in seven files
(`07`–`13`) plus `06:1243`. The owner ruled that `06`'s caveat was in scope under `LIT-07 X1` item
0's existing authority over that file, with nothing else in `06` touched.

### Dispatches

Every dispatch was an existing pack section with a narrowed payload, under the pack's idempotency
rule. **No section was authored.** No searches were run and no ledger rows were logged in this
session — the ledger stands at 1,200 rows, unchanged.

| Item | Model | Section | Payload |
|---|---|---|---|
| `X1` | Sonnet | `LIT-07 X1` | Coverage-caveat figures in `06`, `07`, `08` |
| `X1` fix 1 | Sonnet | same | Name the two unread top-band sources |
| `X1` fix 2 | Sonnet | same | Stale H2/H7 per-hypothesis tallies in `08` |
| `X2` | Sonnet | `LIT-07 X2` | H4 split, Experiment 2 withdrawal, populations in `09`–`12` |
| `X3` | Sonnet | `LIT-07 X3` | Missing Part A entries and re-derived counts in `13` |
| `G` | Haiku | `LIT-07 G` | Final gate, eight stop conditions |

Both of `X1`'s fix cycles were used; `X2` and `X3` needed none. `LIT-07 A` was **not** re-dispatched
— see *The A review was not re-run* below.

## The band figure: a measurement that varies with an unwritten rule

`X1` measured the top prescore band honestly and produced a figure that contradicted a ruling
committed the previous day. The coordinator verified both readings before escalating.

The two top-band sources measuring as "never deep-read" are
`dhar-vaidhyanathan-varma-agenticakm-2026` and `epistemic-sybil-resistance-multiplying-agents-2026`
— precisely the two documented near-duplicate pairs the campaign carries deliberately unrepaired.
**Both underlying works were deep-read**, under the partner ids
`dhar-vaidhyanathan-varma-agenticakm-2026-arxiv` and `epistemic-sybil-resistance-bara-2026`, and
both partners are in the matrix.

| Rule | Pool | Never deep-read | Top band | Band unread |
|---|---|---|---|---|
| A — exact `source_id` only | 400 | 336 | 32 | **2** |
| B — collapse the near-duplicate pairs | 398 | 334 | 31 | **0** |
| `PROMPT-031` ruling 10, committed 2026-09-20 | — | — | 32 | **0** |

**Ruling 10's figure reproduces under neither consistent rule.** It takes the band size from A and
the unread count from B. The owner ruled that the deliverables carry reading A — the mechanically
reproducible one — and **name both sources** so the figure cannot mislead, and that `PROMPT-031` is
left untouched, with the discrepancy recorded here as a finding rather than resolved by an agent
editing a record of the owner's rulings.

Ruling 10's substance is unaffected: its conclusion is that no tenth search session should be
commissioned, and the deep-read coverage conclusion holds under both readings.

Captured as idea `000307`, linked `relates_to` idea `000289`, which records the same class of
unwritten-rule ambiguity for `result_ids` tokenisation.

## The A review was not re-run

`LIT-07 A` ran on 2026-09-14 with 9 findings, all addressed in one fix cycle. It was not
re-dispatched this session, on the owner's explicit ruling. Its declared inputs are `07`, `08`,
`06` and `04`; this session changed `07` and `08` only in corrected population figures, and `A`
never covered `09`–`13` at all. The pack's idempotency rule covers the rest: output that already
exists is verified against its contract rather than re-created.

Re-running it would have meant widening a section's declared inputs mid-campaign, which is a
departure from dispatching it verbatim, and would have put a met acceptance condition back at risk
on inputs that changed only in corrected numbers.

## Scope

The diff touches two paths outside the phase's declared `deliverables` list, both deliberate and
both recorded here rather than left for a reviewer to discover:

- **`06_hypothesis_tests.md`** — one line, its coverage caveat. Inside the phase's declared
  `systems: [sys-research]`, and `LIT-07 X1` item 0 already gives a dispatch write authority over
  `06`. The owner approved its inclusion explicitly. No status token, hypothesis block or evidence
  bullet in `06` was touched.
- **`_data/ideas.jsonl`** — two ideas captured through the sanctioned writer, per `GOV-006`'s
  standing requirement to capture findings as ideas immediately.

## Findings

1. **`PROMPT-031` ruling 10's "0 of 32" is not reproducible.** Recorded above. Idea `000307`.
   Deliberately not fixed: an agent does not edit a record of the owner's rulings.
2. **The source inventory's `status` field is stale for 16 rows** that have evidence-matrix rows.
   Measured independently twice, reproducing exactly: 51 rows marked `deep_read`, 67 matrix rows,
   16 matrix `source_id`s unmarked. **Every previous count of this drift was wrong** — `PROMPT-031`'s
   `phase-lit-09` section records "four", and the 2026-09-21 close review records "17". Neither
   reproduces. Idea `000308`. The inventory was not repaired; it is evidence.
3. **`SESS-2026-09-20-02` misnames the two duplicate inventory rows.** Its *Unresolved* section
   names `epistemic-sybil-resistance-*` and `dhar-vaidhyanathan-varma-agenticakm-*`. The actual
   duplicate `source_id` values — the same id on two rows — are
   `memtx-transactional-belief-commit-2026` and
   `semantically-seeded-graph-propagated-impact-analysis-vision-2026`, which is what `13`'s caveat
   correctly says. The pair that record names are two *distinct* ids describing the same work, which
   is a different defect. Both facts are true and they are about different things; `13`'s caveat was
   reworded to state the distinction explicitly.
4. **`13` was missing a third source the close review never caught** —
   `maclean-young-bellotti-moran-qoc-design-space-analysis-1991`, cited by author name rather than
   slug in `07` and `09`. Found by `X3`'s own author-name cross-check and added. A slug-only match
   undercounts, which is why the method matters.
6. **Commit `6936b98` carries an inaccurate message.** It reads "Annotate 000289: the recorded
   saturation trend line is not reproducible" — a claim withdrawn later the same session (see
   *Measurement 5* above) — and it also swept this session record into the same commit, which the
   message does not mention. The repository's `pre-commit` hook runs only
   `check_no_private_content.py` and stages nothing, so the cause is not established. History was
   deliberately **not** rewritten to fix it: a dispatched agent was committing to the same branch
   at the time, and rewriting under it risks losing its work. The message is wrong, the record
   says so, and that is the honest resolution.
7. **The independent close review ran against a moving target, and that was the coordinator's
   error.** Commits landed and the session record grew while the review was in flight, and the
   review said so as a blocking procedural finding. It was right. A second review was run against
   a frozen diff; see *Review* below.

5. **`check_no_private_content.py` verifies nothing in a worktree.** It reported
   `0 identifiers checked` on this branch. Not recorded as a passing content verification; the real
   run is in the primary checkout. Idea `000150`, unchanged.

## `LIT-07 G` — the final gate

Dispatched per Block G plus the `LIT-07 G` section, Haiku, payload narrowed only. **One fix cycle
of the two available was used.** Populations named per Block G.

| # | Stop condition | Measurement | Population |
|---|---|---|---|
| 1 | Domain coverage | **Met.** 0 domains below 2 distinct queries; min D48 = 6, max D38 = 42. 410/410 variant components covered | 72 D-domains; 339 mandated variants from `PLAN-023.02`, 410 components |
| 2 | Chaining | **Met.** 53/53 carry a `strategy_phase: B` row and 53/53 a `strategy_phase: C` row; 0 missing either | 53 matrix rows with `max(component, architecture) overlap ≥ 3` |
| 3 | Challengers | **Met.** All 11 carry a permitted status; **no `NOVEL`** | H1–H11 in `06_hypothesis_tests.md` |
| 4 | Matrix completeness | **Blanks met; band exceeded.** 0 blank cells; 67 rows against a 20–30 band | 43 fields × 67 rows = 2,881 cells |
| 5 | Saturation | **Measured, NOT demonstrated.** Duplicates falling | See below — the figure is rule-dependent |
| 6 | Second review | **Met.** 0 pending — 12 confirmed, 18 disputed | 30 `critical_collision: yes` rows |
| 7 | Deliverables | **Met.** 14 files present, `00` through `13` | `research/literature-review/` |
| 8 | A-review findings | **Met.** 0 unaddressed-and-unrecorded; 9 findings, all addressed in one fix cycle | `LIT-07 A`, 2026-09-14 |

Measurement 5 is reported as a trend and **not asserted**, per check-in ruling 8 as extended by
ruling 9. Recording it unmet is the required outcome under the amended acceptance, not a gate
failure.

### The gate mismeasured a fourth time, and the coordinator's recomputation caught it again

Three consecutive gates before this one reported false results. This is the fourth. **Every
measurement in the table above was independently recomputed by the coordinator — six of the eight
before the gate was even dispatched — and the gate's first run disagreed with three of them.**

- **Measurement 2 — false PASS on the wrong population.** The gate measured the 30
  `critical_collision: yes` rows. The condition names rows with **either overlap score ≥ 3**, which
  is 53 rows; the two sets are different and neither contains the other. The corrected run
  reproduces 0 missing across all 53.
- **Measurement 4 — narrowed scope, PASS on 16% of the population.** The gate chose 7 "required"
  fields and measured 469 of 2,881 cells. The matrix header carries 43 columns. **This is the third
  consecutive gate to make this exact error**, and this dispatch warned about it by name in
  writing. The corrected full-matrix measure holds at 0 blanks.
- **Measurement 1 second half — an assertion, not a measurement.** "Substantively covered" with no
  count, sourced from the domain map's `Tradition` fields rather than the variants the section
  names. Corrected to 410/410 components from `PLAN-023.02`.

The pattern is now four for four and is no longer attributable to any single gate. A gate trusted
without independent recomputation would have failed this phase on two conditions that are met.

### Measurement 5, and a coordinator error corrected before it reached a deliverable

The gate's measurement 5 disagreed with the campaign's recorded trend line, and the coordinator
initially concluded the recorded figures were unreproducible. **That conclusion was wrong and is
withdrawn.**

The rule is documented, in the campaign's own deliverable. `06_hypothesis_tests.md:72-79` states
it precisely: an identifier counts as a duplicate if it appears in `03_source_inventory.csv` **as
that file stood immediately before the phase began** — for `phase-lit-08`, commit `83fb42b^`, the
parent of the first `LIT-08` search, so no `LIT-08` row can add an entry to the inventory it is
checked against — matched on **either** the `source_id` column **or** `url_or_doi`.

Reproduced exactly under that rule: 82 `LIT-08` ledger rows, 387 raw identifiers, 347 distinct,
**58 duplicates = 15.0%**. Both the raw figure and the 347 distinct count match `06` to the digit.

The coordinator's error was procedural, not arithmetic: two rules the campaign never used were
tested — within-phase token collision, and recurrence against earlier ledger phases — and a defect
was asserted before reading the deliverable that states the method. Neither tested rule checked
`url_or_doi`; neither used a pre-phase snapshot. The figures they produced measure different
quantities, not the same one differently.

**The recorded figures 20.0%, 15.0% and 6.4-7.7% are supported and need no correction in any
deliverable.** The finding annotation on idea `000289` has been amended to withdraw the claim.

What survives is narrower and real: **the rule lives in a deliverable rather than in the evidence
contract**, which is where a rule governing every phase's measurement belongs. A gate reading only
`PLAN-023.03` cannot find it — and `LIT-07 G` did exactly that, independently producing a
within-phase figure of 5.9% for `phase-lit-06` because the contract gave it no rule to apply. That
is the defect: not an unreproducible number, but a reproducible rule recorded in the wrong place.

## Spend

One session, no searches, no ledger rows added — the ledger stands at 1,200 rows. Six dispatches:
`X1` plus two fix cycles (Sonnet), `X2` (Sonnet), `X3` (Sonnet), `G` plus one fix cycle (Haiku),
and the independent close review (Sonnet). `X1` used both its fix cycles; `X2` and `X3` used none;
`G` used one of two.

**No Opus escalation was spent.** The campaign's single permitted escalation remains unspent
through all ten sessions.

Ten sessions against a seven-session estimate and an owner-accepted range of six to eight. This is
the second consecutive session to run no searches, and ruling 10 forbids only a tenth *search*
session.

## Review — independent adversarial close review

Required by `GOV-003`'s *Coordinator completion replaces owner-invoked /session-close*: a
coordinator may write `status: complete` only after an independent adversarial review of the
phase's diff against its acceptance.

**The review ran twice.** The first run was dispatched against a branch this session was still
committing to — a thirteenth commit landed and the session record grew while it was in flight. It
raised that as a blocking procedural finding and it was right; **the fault was the coordinator's.**
The branch was then frozen at `0c6636e` with a clean tree, and the review re-ran against
`git diff 7ab8cb8..0c6636e` with nothing touching the branch until it reported.

### First run — three blocking findings

1. The required final-gate re-run was absent from the reviewed diff. It had run, outside what the
   review was handed.
2. The diff was not stable. Correct, and the coordinator's error.
3. The saturation figures in six deliverables did not reproduce. **This finding originated in a
   coordinator error and both parties were wrong** — see *Measurement 5* above.

It also found one real defect the coordinator had not: a paraphrase presented inside quotation
marks as `06`'s text, at `10:49` and `11:90`.

### Second run — verdict

> **Acceptance condition 1 — HOLDS.** **Acceptance condition 2 — HOLDS**, measurement-taken as
> amended, with populations named and saturation reported as a trend and explicitly not asserted.
>
> **Safe to mark complete.**

On the saturation reproduction, which it was explicitly asked to attack rather than accept:

> I rebuilt it from scratch, not from your description of it. [...] This matches
> `06_hypothesis_tests.md:72–79`'s own stated method and its own stated result (58/387=15.0%,
> 37/347=10.7%) to the digit [...] **Your reproduction holds. My original finding 3 was wrong**,
> and specifically wrong in the way you diagnosed: I tested rules the campaign never used and
> never checked `url_or_doi` or a pre-phase snapshot.

It reproduced six of the eight gate measurements independently against current files, all matching,
and re-ran every condition-1 check against the frozen HEAD to look for damage from the late
commits `1d77db1` and `0c6636e`, finding none.

It named two things it verified by consistency rather than full independent rebuild, which is
recorded here rather than smoothed over: `phase-lit-06`'s 44/220 and `phase-lit-09`'s 25–30/392,
and measurement 1's "410/410 variant components" sub-claim.

### One reviewer correction that is itself wrong

The second run stated that `"known components, integrated"` — the third pseudo-quote the `X2` fix
cycle found at `10:37`, attributed to the methodology's §14 — is "real in
`research/literature-review/CLAUDE.md`", and therefore that the original text was not fabricated.

**It is not there.** Whitespace-normalised, the string `known components` appears nowhere in
`research/literature-review/CLAUDE.md` or in the root `CLAUDE.md`. The original attribution was a
pseudo-quote, the fix was correct, and the reviewer's correction of it is an error. Recorded
because a review that overturns a finding deserves the same scepticism as the finding.

The outcome is unaffected: the reviewer endorsed the resulting form either way, and `10:37` now
presents the point as paraphrase without quotation marks.
