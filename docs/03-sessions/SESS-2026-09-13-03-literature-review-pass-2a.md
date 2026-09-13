---
schema_version: 1
id: doc-session-literature-review-pass-2a
code: SESS-2026-09-13-03
title: Literature review Pass 2a — fourth execution session of the adversarial campaign
kind: session
status: active
owner: repository-owner
created: '2026-09-13'
updated: '2026-09-13'
systems:
- sys-research
depends_on:
- doc-lit-campaign
- doc-research-protocol
---

# Literature review Pass 2a — fourth execution session of the adversarial campaign

## Phase

`phase-lit-04` — Literature review Pass 2a, the deep read of the top collision candidates. Claimed
by `agent-lit`, the fourth execution session of the campaign
([PLAN-023](../01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md)). This is the
first phase that builds the evidence matrix
([PLAN-023.03](../01-plans/PLAN-023-literature-review-campaign/PLAN-023.03-evidence-contract.md)
deliverable 04); the three Pass 1 phases produced the ledger, terminology map, domain map and
source inventory it reads from.

The phase is left `active`. Only the owner's `/session-close` moves a phase to `complete`.

## Verification

The phase's three `verification` entries, run in the worktree after the final rebase onto `dev`.

`uv run python -m src.governance`:

```text
Governance OK: 20 systems, 193 documents, 22 memories, 133 backlog phases
exit 0
```

`uv run python tools/check_no_private_content.py` with the changes staged:

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (550 tracked files, 0 identifiers checked)
```

**0 identifiers checked is not a passing confidentiality gate.** `_private/` is gitignored and
absent from a worktree, so the tool builds an empty identifier list (idea `000150`). The real check
ran in the primary checkout on the catalog commit `2ea3080` and reported **31 identifiers checked**.

Delegation-pack section `LIT-04 G` (`PROMPT-029`), all four measurements — see
[Gate measurements](#gate-measurements--lit-04-g-real-output) below for the full output and the
coordinator's independent re-measurement of each. Summary: **4 of 4 PASS** — 20 of 20 assigned batch
ids present, 0 blank required fields, 0 `critical_collision: yes` rows lacking
`second_review: pending`, 0 deep-read sources without a `strategy_phase: B` ledger row.

The full test suite, run for the rebase check `AGENTS.md` requires before a branch may integrate:

```text
uv run pytest    → 578 passed, 2 warnings
```

The **pre-rebase** run of that suite failed on
`test_committed_catalog_matches_regenerated_output`. That failure is recorded rather than elided; it
was diagnosed and fixed in `2ea3080`, not retried until quiet. See
[Findings](#the-claim-commit-left-dev-red-and-the-documented-regeneration-command-does-not-write).

Deliverable integrity re-measured after the rebase: ledger 889 CRLF lines with 0 bare LF; matrix 20
rows with 0 blank fields across all 43 columns; inventory 20 rows at `status: deep_read`.

## Acceptance

**Met** — The evidence matrix exists with a fully populated row for each deep-read candidate; no
required field is blank and every row carries an evidence locator to primary material.
`04_evidence_matrix.csv` holds 20 rows, one per assigned batch id, every row exactly 43 fields. A
scan of all 43 columns x 20 rows found **0 blanks**; `NOT_APPLICABLE` (212 uses) and
`NOT_DETERMINABLE_FROM_ACCESS` (40 uses) appear as the contract's permitted values, always with an
explanatory reason rather than bare. `evidence_locator` is populated on all 20 rows, none shorter
than 40 characters.

**Met** — Every CRITICAL_COLLISION flag traces to the scoring rules and backward chaining is logged
in the ledger for each deep-read source. Checking every row against the contract's flag rules
(component overlap ≥ 4, or architecture overlap ≥ 4) gives **0 mismatches in either direction**: all
14 `yes` rows clear a score threshold, and all 6 `no` rows fall below both. All 14 carry
`second_review: pending`. The ledger holds **20 `strategy_phase: B` rows**, one per deep-read
source, each with that source's id in `subject_source_id` — measurement 4 of the gate, which
measured 1 missing on first pass and 0 after fix cycle 1.

## Backlog

`phase-lit-04` — `status: active`, left active deliberately: all work items are complete and
gate-measured, but only the owner's `/session-close`, after its own independent review, may mark a
phase `complete`.

`next_action`: Phase work is complete and all four `LIT-04 G` gates pass; the phase awaits the
owner's `/session-close` review. `phase-lit-05` (Pass 2b) is unblocked and continues on
`agent/lit-campaign`, numbering its searches from `LIT-05-S001`.

`session`: `doc-session-literature-review-pass-2a`.
`completion_evidence`: `research/literature-review/04_evidence_matrix.csv`,
`research/literature-review/00_search_ledger.csv`,
`docs/03-sessions/SESS-2026-09-13-03-literature-review-pass-2a.md`.
`result`: 20 sources deeply compared into a new 43-field evidence matrix; 44 ledger rows
(`LIT-04-S001`–`S044`, 24 verification + 20 backward-chaining); 14 rows flagged
`critical_collision: yes` with `second_review: pending`; all four gate measurements PASS after one
fix cycle.

`next_up` was not pruned — `phase-lit-04` is not in it, and nothing else completed this session.

## Unresolved

- **`AGENTS.md` and `CLAUDE.md` both document the catalog regeneration without the redirect that
  makes it write** (idea `000208`). Neither file was edited; that needs the owner's explicit
  approval for the specific change. Note that `.claude/skills/checkpoint/SKILL.md` already carries
  the correct form, so the repository contradicts itself on this command.
- **The inventory and the matrix now disagree on bibliographic fact** for at least five sources, and
  the contract names no authority for `LIT-07 X3`'s validated bibliography (idea `000209`).
- **`solozobov-verify-gated-completion-admission-control-2026` names the wrong author** in a stable
  identifier already referenced from four files; renaming is the owner's call (idea `000210`).
- **No gate measures ledger well-formedness**, and five malformed rows shipped this phase before a
  worker's voluntary audit caught them (idea `000211`).
- **Line endings remain unspecified** across the three deliverables (idea `000212`).
- **The top-20 dedup gap** that put one paper in two slots is resolved for this phase by owner
  ruling but not as a mechanism (idea `000213`).
- **`LIT-04 G` reported PASS on blank fields having checked 4 of 43** (idea `000214`). The verdict
  held only because the coordinator's independent measurement covered all 43; the LIT-05, LIT-06 and
  LIT-07 gates re-measure the same condition over a larger matrix.

## Preflight

| Check | Result |
|---|---|
| `uv run python -m src.governance` | exit 0 — `Governance OK: 20 systems, 192 documents, 22 memories, 133 backlog phases` |
| Campaign worktree | `../d-system-worktrees/lit-campaign` present, on `agent/lit-campaign`, clean |
| Baseline integrity | `research/pre-literature-baseline.md` = `635bcfa`, `research/pre-literature-hypotheses.yaml` = `a53ecdb`, last touched by `b2b564b` — matches the pinned identity in `PROMPT-031` exactly |
| Prior evidence present | `00_search_ledger.csv`, `01_terminology_map.md`, `02_domain_map.md`, `03_source_inventory.csv` all present; none recreated |
| Peer claims | `phase-demo-07` (`agent-demo-glossary`) holding `sys-brain`, `sys-portfolio` — no overlap with `sys-research` |
| Current phase | `phase-lit-04`, `ready`, prerequisite `phase-lit-03` complete, Conflicts `—` |

## Owner rulings taken before dispatch

**Deep-read marking (idea `000202`).** The evidence contract's inventory `status` field
(`candidate` / `deep_read` / `excluded`) is the campaign's only deep-read mark, and `LIT-03 C` was
forbidden to set it, so the ranked top-20 list in `02_domain_map.md` carried the designation
instead. Ruling: **the top-20 list is authoritative for batch selection; each `X` dispatch sets
`status: deep_read` on a source's inventory row after it has actually deep-read that source.** No
contract amendment, no new column, no bulk marking at kickoff. `LIT-04 G` measures the result.

**The top-20 carried one paper twice.** `dhar-vaidhyanathan-varma-agenticakm-2026` (a ResearchGate
record, `source_type: conference`) and `dhar-vaidhyanathan-varma-agenticakm-2026-arxiv`
(`arxiv:2602.04445`, preprint) are the same AgenticAKM paper by Dhar, Vaidhyanathan and Varma —
identical pre-scores 5/4, same domain D39, both `dedup_of: none`, both tied at rank 1. Deep-reading
both would have spent two of twenty slots on one mechanism and seeded the matrix with two rows for
it, inflating apparent prior art in the direction that flatters H0. Ruling: **keep the arXiv row,
drop the ResearchGate row, promote the row the alphabetical tie-cut dropped at rank 21.**

The coordinator re-derived the ranking independently from the inventory before dispatching: the
twelve remaining `component=5, architecture=4` rows plus the complete eight-row `4/4` tie —
including `zep-graphiti-temporal-kg-agent-memory-2025`, which `02_domain_map.md` names as the row
its cut dropped — give exactly twenty distinct sources. `02_domain_map.md` was **not** rewritten;
the substitution is recorded here. Raised as idea `000213`.

## What was dispatched

Sections from the delegation pack
([PROMPT-029](../02-prompts/PROMPT-029-literature-review-delegation-pack.md)), verbatim, one at a
time, assembled per its dispatch rules, in the order the pack lists them. Models per the pack:
`K` and `G` on Haiku, `X` on Sonnet.

| Item | Model | Outcome |
|---|---|---|
| `LIT-04 K` | Haiku | Claimed `phase-lit-04` on `dev` (`3414226`); created `04_evidence_matrix.csv` with the contract's 43-field header, LF-only, no data rows (`523f7cc`); split the twenty ids 7/7/6 |
| `LIT-04 X1` | Sonnet | 7 sources, `LIT-04-S001`–`S014`, 7 commits |
| `LIT-04 X2` | Sonnet | 7 sources, `LIT-04-S015`–`S030`, 7 commits |
| `LIT-04 X2` fix cycle 1 | Sonnet | 1 missing backward-chaining ledger row, `LIT-04-S031` (`0909865`) |
| `LIT-04 X3` | Sonnet | 6 sources, `LIT-04-S032`–`S044`, 6 commits |
| `LIT-04 G` | Haiku | All four gate measurements |

One fix cycle was spent, of the two the pack allows per work item. `X2`'s transcript could not be
resumed, so the fix was dispatched as a fresh agent scoped to the single source.

Standing dispatch addressing carried into every `X`: `EnterWorktree`/`ExitWorktree` forbidden by
name with `cd <path> && <command>` substituted (idea `000196`), abandon-and-report any tool call not
returning in ~60 seconds, commit after every source, verify bibliographic identity at the source
rather than the aggregator (idea `000203`), the ledger's CRLF hazard, and canonical identifier form
(idea `000147`).

## Gate measurements — `LIT-04 G`, real output

Every measurement was also taken independently by the coordinator against the same files. Both
agree.

| # | Measurement | Gate | Measured | Result |
|---|---|---|---|---|
| 1 | Matrix row for every batch id `K` assigned | all present | 20 of 20, no extras, no omissions | **PASS** |
| 2 | Blank required fields across this phase's rows | 0 | 0 | **PASS** |
| 3 | `critical_collision: yes` rows lacking `second_review: pending` | 0 | 0 (14 rows flagged `yes`, all `pending`) | **PASS** |
| 4 | Deep-read sources with no `strategy_phase: B` ledger row carrying their id in `subject_source_id` | 0 | 0 | **PASS** |

Supporting counts: 20 matrix rows, every row exactly 43 fields, LF-only. 889 ledger lines, every
row exactly 15 fields, CRLF throughout with zero bare LF and zero bare CR. 44 rows with `search_id`
starting `LIT-04-`, contiguous `S001`–`S044` with no duplicates and no gaps, of which 24 are
`strategy_phase: D` and **20 are `strategy_phase: B`** — one backward-chaining row per deep-read
source. Inventory unchanged at 1091 rows with exactly 20 now `status: deep_read`.

```text
Governance OK: 20 systems, 192 documents, 22 memories, 133 backlog phases
exit 0
```

**The private-content check verifies nothing in this worktree, and is recorded as such.** Its
verbatim output:

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (548 tracked files, 0 identifiers checked)
```

`_private/` is gitignored and absent from a worktree, so the tool builds an empty identifier list.
**0 identifiers checked is not a passing confidentiality gate** (idea `000150`). The real check ran
in the primary checkout on the catalog commit below and reported **31 identifiers checked**.

### Gate method defect — a false PASS that happened to be right

`LIT-04 G` reported measurement 2 as PASS having checked **four** fields — `source_id`, `citation`,
`source_type`, `research_domain` — of the contract's **43**. The contract is explicit that every
field is required and that blank is never permitted. The verdict was correct only because the
coordinator's independent measurement across all 43 fields x 20 rows found 0 blanks; a blank in any
of the other 39 would have been reported as PASS.

This is the campaign's third gate-method failure and the first in the silent direction. `LIT-01 G`
reported 435 missing sources against a true 0; `phase-lit-03`'s gate produced a false FAIL with five
phantom variants. Both were loud and self-announcing. A false PASS opens no fix cycle. Raised as
idea `000214`, whose general point is that a gate reporting only a numerator cannot be
distinguished from a gate that measured the wrong population.

## Findings

### The claim commit left `dev` red, and the documented regeneration command does not write

`uv run python -m src.governance --catalog` **prints** the catalog to stdout; it does not write
`docs/08-governance/catalog.md`. Run bare it exits 0 and changes nothing, so the natural
confirmation — run it, then check `git status` — reports a clean tree unconditionally and can never
fail.

`LIT-04 K` reported regenerating the catalog with the claim, and the coordinator verified by that
same method. Both were wrong. The claim commit `3414226` shipped with the `PLAN-023` rollup reading
`4 queued / 0 active / 3 complete` against a live backlog of `3 / 1 / 3`, and `dev` was red on
`test_committed_catalog_matches_regenerated_output` from that commit until the phase boundary.

Caught here by running the full suite after the rebase, diagnosed by deliberately corrupting the
row and observing that `--catalog` left the corruption in place, and fixed in `2ea3080` on `dev`
with `uv run python -m src.governance --catalog > docs/08-governance/catalog.md`. `AGENTS.md` names
the catalog regeneration a claim forces as permitted primary-checkout work and requires it to be
committed with the claim, which is the authority under which that commit was made. Raised as idea
`000208`.

`AGENTS.md` and `CLAUDE.md` both give the command without the redirect. **Neither file was edited**
— that needs the owner's explicit approval for the specific change, and the proposed wording is in
`000208`.

### Bibliographic corrections land in the matrix while the inventory keeps the wrong values

Verifying identity at the source rather than the aggregator (idea `000203`) found errors at a higher
rate than that idea anticipated — five inventory-versus-source disagreements in `X1`'s seven sources
alone. Confirmed cases: EM-LLM is an ICLR 2025 conference paper, not a preprint; Evidence Graphs is
IPAW 2021 (Springer LNCS 12839); Keim & Kaplan is an accepted ICSE-C 2026 Companion paper; the de
Boer dissertation is a joint thesis with Rik Farenhorst per its own acknowledgments; the patent
application `US20250165226A1` has since granted as `US12461717B2`.

All were recorded in the matrix and left uncorrected in the inventory, correctly under the
deep-read-marking ruling. The two deliverables therefore now disagree on fact, with the
better-verified value in the matrix, and the contract gives no reconciliation rule for
`LIT-07 X3`'s validated bibliography to follow. Raised as idea `000209`.

`X2` additionally found the Semantic Scholar record for the IBM blueprint carries a corrupted
doubled title with no author or year, and a second record misattributing sole authorship — a fourth
instance of the aggregator-corruption pattern.

### A `source_id` slug names the wrong author

`solozobov-verify-gated-completion-admission-control-2026` attributes the paper to "Solozobov" in
both the slug and the citation. The paper's title page names only Hai-Duong Nguyen and Xuan-The
Tran; "Solozobov" appears nowhere in its text. The slug is a stable identifier already referenced
from the ledger, the matrix, the inventory and `02_domain_map.md`, so renaming it is not an agent's
call. Raised as idea `000210`.

### Five malformed ledger rows shipped and were caught only by a post-hoc audit

`LIT-04 X2` appended five rows (`S016`, `S018`, `S020`, `S026`, `S027`) that silently dropped
`duplicate_handling` and/or `chain_decision`, because its append script validated CSV shape for the
matrix but not the ledger. It caught them in its own full-file audit and repaired them by
byte-level surgery before the gate; the coordinator re-audited independently and confirms all 889
rows are now 15 fields. No gate measures ledger well-formedness, so without the worker's voluntary
audit these would have entered the reproducibility record. Raised as idea `000211`.

### Line endings remain unspecified

The ledger is CRLF, the inventory and matrix are LF, and the contract specifies none of them. The
matrix was new this phase, so the convention had to be ruled in dispatch addressing — LF, by analogy
with the inventory — which is where a decision cannot be found again. Raised as idea `000212`.

## Substantive results

Twenty sources deeply compared. **14 of 20 flagged `critical_collision: yes`**, each carrying
`second_review: pending` for `LIT-06 X2`. Two rows hold the top score of 5/4:
`graph-native-cognitive-memory-belief-revision-semantics-2026` and
`jansen-bosch-architecture-as-decisions-wicsa-2005`.

**The deep read systematically deflated the Pass 1 pre-scores.** Every source entered pre-scored
5/4 or 4/4; after reading, 11 of the first 13 measured were revised down and none up, mean change
component **-1.31**, architecture **-1.46**. That runs against the campaign's own bias — the
pre-scores were the H0-flattering number — and is weak evidence the Pass 1 / Pass 2 separation is
doing real work rather than confirming a foregone conclusion.

**Two independently developed 2026 systems decline to claim novelty in their own text.** "The log
is the agent" calls itself a "recombination" of event sourcing, CQRS, reactive dataflow and 1980s
Blackboard coordination, and "less a new idea than a vindication of an old one". Kumiho
(`graph-native-cognitive-memory-...`) states "we contribute not novel individual components... but a
novel architectural synthesis". H0 predicts D-System is a recombination; the nearest neighbours
independently reaching that verdict about themselves is a stronger class of evidence than prior art
alone.

**The shared-name trap was avoided in practice, not only in principle.** LineageRAG fell 5/4 to 3/1
because its "lineage" is a within-inference provenance trace, not a cross-time knowledge-transition
history, despite the shared vocabulary. Keim & Kaplan fell 5/4 to 2/2 for proposing no mechanism.
`derivative_ancestor` collapsed apparent independence in several places: de Boer 2009 and Jansen &
Bosch 2005 both resolve to Perry & Wolf 1992; Aporia self-describes as an application of QOC (1991);
EM-LLM names Event Segmentation Theory and the Temporal Context Model; Evidence Graphs traces to
Dung 1995 and Toulmin 1958.

**Zep and TGMS were recorded as one lineage, not two confirmations.** TGMS names Snodgrass 1999 as
the classical valid-time/transaction-time ancestor; `X3` read Zep's full 28-entry reference list and
found Zep cites no classical temporal-database work at all, framing bi-temporality as "a novel
advancement" — true only relative to prior LLM/RAG memory systems. Recorded as one shared 1999
ancestor with two LLM-era derivatives.

**`X3` withdrew one of its own inferences.** Having written that both digital-thread sources trace
to the 2013 USAF *Global Horizons* report, it read the patent, found it cites the DoD Digital
Engineering Strategy (2018) instead, and edited the already-committed row. The diff is exactly one
field, and it withdraws a shared-ancestor claim rather than adding one.

Two sources were genuinely unobtainable and recorded honestly rather than retried into silence: the
Procko dissertation sits behind a Cloudflare challenge no headless client passes
(`access_limitation: abstract_only`, confidence capped at `medium`, supplemented by the author's own
implementation repository), and the IBM blueprint resisted seven access routes including four
`archive.org` 429s (`secondary_coverage` via an SEI/CMU technical report, confidence `medium`).

## Spend posture

- **Searches this phase**: 44 ledger rows, `LIT-04-S001`–`S044` — 24 bibliographic-verification
  rows filed under `strategy_phase: D` (the enum has no verification value; the mismatch is noted in
  each row, per idea `000149`) and 20 backward-chaining rows under `strategy_phase: B`.
- **Sources deep-read**: 20, the phase's full assignment. Campaign matrix total: 20 of the
  methodology's 20–30 stop condition, which `phase-lit-05` completes.
- **Opus escalation**: none spent, in this phase or the campaign to date. The kick-off record's
  single documented escalation remains available.
- **Descope rungs**: none taken.
- **Fix cycles**: 1 of the 2 allowed on `LIT-04 X2`; none on `X1`, `X3` or `G`.
- **Sessions**: 4 of a seven-session runway, range six to eight.

## Resume state

- **Current phase**: `phase-lit-04`, left `active`, all work items complete and gate-measured. Only
  the owner's `/session-close`, after its own independent review, may mark it `complete`.
- **Next phase**: `phase-lit-05` — Pass 2b, forward chaining and the foundational works that bring
  the matrix to the methodology's 20–30 deeply compared sources. Its items are `K` → `S1` → `X1` →
  `X2` → `G`.
- **Search ids**: `LIT-05` numbers from **`LIT-05-S001`**. The contract numbers them
  `LIT-<phase>-S<seq>`, monotonic per phase; they do not continue from `LIT-04-S044`.
- **`LIT-05 S1` operates on** every matrix row with either overlap score ≥ 3 — 18 of the 20 rows
  qualify. `LIT-05 G` additionally reports which of H1–H11 have zero challengers, which is what
  tells `phase-lit-06` where to dig.
- **A fresh session must read**: `AGENTS.md`, `GOV-006`, `PROMPT-031` (the kick-off record, which
  wins over the coordinator prompt), `PROMPT-030` in full, and this record. The pre-synthesis
  check-in section of `PROMPT-031` is still empty by construction, so `phase-lit-07` remains barred.
- **Open for the owner**, none blocking `phase-lit-05`: ideas `000208`–`000214`, and in particular
  `000208` (the `--catalog` wording in `AGENTS.md` and `CLAUDE.md`, which no agent may change) and
  `000210` (whether the misattributed `source_id` slug is renamed).
- **Integration**: `agent/lit-campaign` is rebased onto `dev`, green, and **not** integrated. Per
  `PLAN-023`'s branch model the next owner integration is at the pre-synthesis check-in, after
  `phase-lit-06`. The diff is `git diff dev..agent/lit-campaign`.
