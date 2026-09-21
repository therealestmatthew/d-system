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
5. **`check_no_private_content.py` verifies nothing in a worktree.** It reported
   `0 identifiers checked` on this branch. Not recorded as a passing content verification; the real
   run is in the primary checkout. Idea `000150`, unchanged.

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
