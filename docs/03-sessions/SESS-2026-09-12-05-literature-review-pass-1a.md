---
schema_version: 1
id: doc-session-literature-review-pass-1a
code: SESS-2026-09-12-05
title: Literature review Pass 1a — first execution session of the adversarial campaign
kind: session
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-12'
systems:
- sys-research
depends_on:
- doc-lit-campaign
- doc-research-protocol
---

# Literature review Pass 1a — first execution session of the adversarial campaign

## Phase

`phase-lit-01` — Literature review Pass 1a, the broad map of knowledge representation,
provenance and epistemics domains (D01–D20, D28–D32). Claimed by `agent-lit`; the first
execution session of the campaign the research pack ([PLAN-023](../01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md))
describes, and therefore the first real test of the research protocol
([GOV-009](../08-governance/GOV-009-research-protocol.md)).

Work runs on the long-lived campaign branch `agent/lit-campaign`, in the worktree
`../d-system-worktrees/lit-campaign`. All fourteen delegation-pack sections for this phase
were dispatched verbatim from [PROMPT-029](../02-prompts/PROMPT-029-literature-review-delegation-pack.md),
one at a time, in pack order: `K` → `S1/X1` → `S2/X2` → `S3/X3` → `S4/X4` → `S5/X5` →
`S6/X6` → `G`. Models were as the pack fixes them — `K` and `G` on Haiku, every `S` and `X`
on Sonnet. **No Opus escalation was spent** and **no descope rung was taken.**

## Verification

The phase's three `verification` entries, run after the rebase onto `dev` — the run
`AGENTS.md` says decides whether a branch may integrate.

```text
$ uv run python -m src.governance
Governance OK: 19 systems, 184 documents, 20 memories, 129 backlog phases
(exit 0)

$ uv run python tools/check_no_private_content.py
note: _private/portfolio/ not found — content check skipped (path check still ran; this is
expected in CI / a fresh clone)
check_no_private_content: OK (527 tracked files, 0 identifiers checked)
(exit 0)

$ uv run python -m pytest -q
578 passed, 2 warnings
(exit 0)
```

**The private-content check verified nothing, and its `OK` must not be read as a pass.**
`_private/` is gitignored and therefore absent from every worktree, so the tool built an empty
identifier list and reported success for having compared zero identifiers against 527 files.
The same command in the primary checkout reads `31 identifiers checked`. Recorded as idea
`000150`; the owner ruled on 2026-09-12 to accept the gap and rely on the integration-time
check, which does have the list.

### The phase gate — delegation-pack section `LIT-01 G`, real output

`G` ran twice. **Its first run failed two gates, and both failures were real results rather
than noise** — one a genuine evidence gap, one a defect in the gate's own method.

First run:

```text
Gate 1  FAIL — D12 uncovered mandated variant "argument attack/support"
               D17 uncovered mandated variant "multi-agent beliefs"
Gate 2  PASS — 0 excluded rows missing exclusion_reason
Gate 3  FAIL — 435 kept-but-uninventoried sources
```

Gate 1's two failures were verified independently and were genuine: the concepts were covered
(D12 across 7 queries, D17 across 10) but neither exact mandated string appeared in any logged
query. `LIT-01 S4` closed them with two supplementary searches, which is the remedy it had
already applied to itself for D14's `dependence-aware fusion` at `LIT-01-S193`.

Gate 3's 435 was a **measurement defect in the gate, not a data failure**. The gate compared
the ledger's `kept` identifiers against the inventory's `source_id` column — human-readable
slugs — instead of `url_or_doi`, which holds the identifiers. Measured both ways:

```text
matched against source_id  -> 435 missing (of 441 kept pairs: substantially all)
matched against url_or_doi ->   0 missing
LIT-01-S001  arxiv:2302.11509  -> inventory row kg-construction-state-challenges-2023
LIT-01-S002  10.1145/3060586   -> inventory row deepdive-cacm-2017
```

The gate was sent back with the diagnostic principle rather than the answer — a measurement
condemning substantially all of its input is suspect before it is reported — and re-derived
the correct column itself, stating its reasoning.

Second run, after the two supplementary searches and the extraction that inventoried their six
new sources:

```text
Gate 1  PASS — all 25 target domains: >=2 rows with distinct queries, no uncovered variant
Gate 2  PASS — 425 inventory rows for target domains (415 candidate, 10 excluded), 0 missing
               an exclusion_reason
Gate 3  PASS — 0 kept-but-uninventoried sources
H4      8 rows, reported separately, correctly outside the {D01-D20, D28-D32} set
governance exit 0; check_no_private_content exit 0 (0 identifiers checked, see above)
```

### Coordinator measurements, taken independently of the gate

```text
ledger:    267 rows, LIT-01-S001..LIT-01-S267, contiguous, 268 lines all CRLF
           strategy_phase distribution: {'A': 77, 'D': 148, 'E': 42}  (sums to 267)
           of which the 8 H4 rows are all strategy E; excluding them: E = 34
           26 domain ids present: D01-D20, D28-D32, H4
inventory: 438 rows | 427 candidate, 11 excluded (every one with a reason)
           159 rows flagged collision_candidate: yes
           441 kept (row, source) pairs resolving to 434 distinct identifiers
terminology map: 26 domain sections
```

## Acceptance

- **"The ledger and source inventory exist at the evidence contract's paths and every matrix
  domain D01-D06, D07-D20, D28-D32 has at least two ledger rows with distinct terminology
  variants."** — **Met.** Both files exist at the contract's paths. All 25 domains clear the
  floor, the narrowest being D11 at 6 rows with 6 distinct queries, and `LIT-01 G` measured
  no uncovered mandated variant after the two supplementary searches closed D12 and D17.
- **"Candidate sources for these domains are in the inventory with inclusion or exclusion
  rationale; no evidence row cites a generated summary as evidence."** — **Met.** 438
  inventory rows, all 11 exclusions carrying a reason, and every one of the 434 distinct kept
  identifiers resolving to an inventory row. No row cites a generated summary: the one
  AI-generated topic-summary page encountered (`LIT-01-S266`) was excluded as a lead.

Both conditions were recomputed at close against the repository as it stands, and independently
corroborated by the sub-agent review in `## Review` below, which derived the mandated variant
lists from `PROMPT-029` itself rather than from this record.

## Backlog

`phase-lit-01` is `status: complete`, `agent: agent-lit`, with `session`,
`completion_evidence` and `result` set to what actually exists and was actually measured. It
was removed from `next_up` in the same change.

The phase reached `complete` through the owner's `/session-close`, after the independent review
recorded below — not by an agent's own judgement that the work looked finished.

`next_action`: Integrate `agent/lit-campaign` into `dev` — the first of the two integrations
`PLAN-023` schedules, and the owner's to perform. `phase-lit-02` (Pass 1b, D21–D27 and
D33–D45) is now unblocked.

## Unresolved

- **The campaign branch is unintegrated.** 48 commits on `agent/lit-campaign`, rebased onto
  `dev` at `33f931a`, tree clean, governance green, 578 tests passing. Integration is the
  owner's, at the point `PLAN-023` names.
- **The private-content gate verified nothing** — see `## Verification`. Idea `000150`.
- **Four instrument gaps were recorded as ideas** `000147`–`000150`, anchored on `000147`:
  the evidence contract fixes no identifier format for the ledger's `kept` column; its
  `source_type` enum has no bucket for a patent; its `strategy_phase` enum has no value for
  verifying an already-kept source; and the private-content check's silent no-op in a
  worktree. `000147` should absorb a fifth, closely related point surfaced by the gate itself
  (below), which is the same root cause one layer up.
- **`LIT-01 G`'s measurement 3 is under-specified, and the final gate inherits it.** The
  section says "names a source absent from the inventory" without naming which inventory
  column carries an identifier, and a Haiku gate picked the slug column, inverting the result
  from 0 to 435. The same wording governs `phase-lit-07`'s stop-condition gate, where a
  comparable slip would reach the research memo. A mechanical gate needs its measurement
  specified to the column.
- **Two ledger identifier conventions coexist deliberately.** After the owner-ruled
  normalisation, rows `S052`, `S062`, `S082` and `S093` still carry
  `semanticscholar.org/paper/...` URLs because the inventory carries those five sources under
  the identical URL form; rewriting them would have created the failure the normalisation
  removed. A later dispatch reported these as violations. They are not. The ledger is
  gate-correct but not internally uniform, and only the contract change in `000147` fixes
  that properly.
- **One source identity is unconfirmed.** The HDP-P working paper appears under a Zenodo DOI
  (`10.5281/zenodo.19332440`) and an SSRN DOI (`10.2139/ssrn.6494358`). Recorded as open in
  the ledger rather than asserted; it becomes a dedup decision when the evidence matrix is
  built in `phase-lit-04`.
- **Two USPTO patents were assessed from search snippets only.** `uspto:9472115` and
  `uspto:11244113` (evidence-corroboration grading, D18) have image-based PDFs that are not
  machine-readable. Recorded in the inventory as such, never as a full-text read.
- **A commit message carries a drafting artifact.** `f147b50` ("Extract LIT-01 X5 inventory
  rows for D18-D20") contains a stray fragment, `"(388 -> wait, 331+58=389 total)"`.
  Cosmetic, no content effect. The branch is unpushed, so amending is cheap until integration.
- **Provider access was uneven and is a spend factor for later phases.**
  `api.semanticscholar.org` returned HTTP 429 for most domains and HTTP 200 for a few;
  `export.arxiv.org` was intermittent and needs `-L`. OpenAlex and Crossref worked directly
  throughout. Every rate-limited attempt is a real zero-yield ledger row with its query, not
  an omission.

## Review

An independent sub-agent, started fresh with no context from this session and explicitly not a
fork, reviewed the 49-commit range `dev..agent/lit-campaign` (`33f931a`..`bd169ad`) against the
phase's acceptance conditions. It re-derived the mandated variant lists from `PROMPT-029`
itself rather than trusting this record, re-ran the verification commands, and externally
verified sampled citations. Its findings, verbatim:

> **Acceptance condition 1 — HOLDS.** Both files exist at the contract's paths, and both
> headers match the evidence contract's column lists verbatim. I independently transcribed the
> mandated minimum variant list for all 25 domains from PROMPT-029's S1–S6 payloads (not
> trusting the record's summary), then wrote a parser against the raw CSV. Result: all 25
> domains clear ≥2 rows with ≥2 distinct queries (narrowest: D11, 6 rows/6 distinct queries,
> matching the record), and every single mandated variant string appears verbatim
> (case-insensitive) in some logged query for its domain — including the two the gate's first
> run flagged as missing: D12's "argument attack/support" (only in `LIT-01-S266`'s query,
> verbatim with the slash — other D12 rows say "argument attack support" without it) and D17's
> "multi-agent beliefs" (only in `LIT-01-S267`, plural — other rows say singular "belief").
> This is a real, narrow gate distinction, not a data problem.
>
> **Acceptance condition 2 — HOLDS.** Inventory: 438 rows, 427 `candidate` + 11 `excluded`,
> and all 11 excluded rows carry a real (non-blank, non-"none") `exclusion_reason` — 0 missing.
> For the kept-column/inventory-linkage question: I judged `url_or_doi` the meaningful
> comparison column (`source_id` is a human-chosen slug that was never intended to equal a
> DOI/URL — comparing against it is what produced the gate's own false "435 missing" first-run
> result). Against `url_or_doi`: 441 ledger (row, source) kept pairs resolve to 434 distinct
> identifiers, and 0 of those 434 are absent from the inventory.
>
> **No evidence row cites a generated summary — HOLDS, more robustly than the record claims.**
> The record cites one instance (an emergentmind.com AI-topic-summary page at `S266`,
> excluded). I grepped the whole ledger for aggregator/blog/topic-summary signatures and found
> roughly ten instances (`nature.com/research-intelligence`, `nature.com/nature-index`,
> `medium.com`, multiple `emergentmind.com` pages) across rows `S026, S047, S074, S096, S116,
> S141, S175, S184, S217, S266`. In every single case the flagged item appears only in
> `result_ids` (inspected), never in `kept`, and consequently never entered the inventory at
> all. Only three vendor-domain pages made it into the inventory as rows, and all three are
> honestly typed `source_type: lead` (the contract's sanctioned bucket for exactly this) with
> low prescores; none is asserted as evidence for any verdict.
>
> **Fabrication check — NO FABRICATION FOUND.** I sampled 8+ ledger rows spanning every
> dispatch (S1 through S6) plus both supplementary rows, and verified 18 distinct cited
> identifiers by fetching arXiv abstract pages, resolving DOIs, and cross-checking USPTO patent
> numbers via web search. [Full list in the review: S001/S002, S057, S106, S201, S236, S078,
> S018, S247, S266, S267.] Zero fabrications, zero citation/identifier mismatches, across every
> dispatch and several 2026-dated (post-training-cutoff, pre-today) arXiv papers that could
> plausibly have been invented — none were.
>
> **S266/S267 — genuine searches, not manufactured.** Both rows carry substantive,
> cross-referenced dedup reasoning against earlier rows, real inclusion/exclusion rationale, and
> citations that verify externally. I also confirmed the counterfactual: removing S266/S267, no
> other row in D12 or D17 contains the exact mandated string — the gap was real, and the fix was
> a real search, not a string-matching trick.
>
> **Internal consistency — all claimed figures reproduce, with one real error and one resolved
> false alarm.** Confirmed exactly: 267 ledger rows (`S001`–`S267`, contiguous, no duplicates),
> 438 inventory rows, 427 candidate/11 excluded, 159 `collision_candidate: yes`, 26
> terminology-map sections (25 domains + H4), 441 kept pairs → 434 distinct identifiers.
> **Real error**: the record's strategy_phase distribution, `{'A': 77, 'D': 148, 'E': 34}`, is
> wrong — the ledger actually contains `{'A': 77, 'D': 148, 'E': 42}`. Notably the record's own
> printed numbers don't even sum to 267 (77+148+34=259); mine do (267). This is a
> transcription/arithmetic slip in the record's prose, not a defect in the deliverable itself.
> **Minor, stale citation**: the record's "Unresolved" section names commit
> `8bc8d24`/`1e7bcf1` as carrying a stray drafting fragment. That exact text does exist in the
> current range, but in commit `f147b50`, not `1e7bcf1` — the hash the record cites is stale.
> The underlying fact is true; the pointer to it is wrong.
>
> **Scope discipline — HOLDS.** The full 49-commit range touches exactly 5 files: the session
> record, `backlog.yaml`, and the three literature-review deliverables. `git diff --stat`
> against every frozen path returns empty — none touched. Searching the terminology map, ledger,
> and inventory for verdict-style language ("confirms H", "refutes", "falsifies", "H0
> is/true/false") returns zero hits.
>
> One soft observation, not a violation: the terminology map uses the phrase "flagged
> CRITICAL_COLLISION candidate" seven times — borrowing the name of a field that formally
> belongs to the downstream evidence matrix (LIT-04+), not Pass 1's schema. Every instance says
> "candidate," never asserts the flag as decided, so I don't read this as a scope violation —
> just a wording choice worth a raised eyebrow.
>
> **Overall judgement.** Both acceptance conditions hold, independently, and every one of the
> six specific scrutiny items the task named comes back clean or better than claimed — most
> importantly, the fabrication check (the one that would invalidate the phase outright) found
> zero problems across 18 externally-verified identifiers spanning every dispatch. The only
> defects I found are cosmetic and confined to the session record's own prose (a wrong
> strategy-phase count, a stale commit hash in a footnote) — none touch the deliverables, the
> gate logic, or either acceptance condition. **In my independent judgement: acceptance
> genuinely holds, and I found nothing that should block this phase from being marked
> complete.**

Both errors the review found were real and are corrected above: the strategy-phase distribution
now reads `{'A': 77, 'D': 148, 'E': 42}` and sums to 267, and the drafting-artifact footnote now
names `f147b50`. Neither correction touches a deliverable.

## Decisions

**The gate ran before the evidence was tidy, and the owner ruled to tidy it first.** Four
dispatches had written the `kept` column in four identifier conventions, so a literal gate
match reported 32 sources as missing that were all present. The coordinator proposed running
`G` and recording both figures; the owner ruled instead to normalise the 32 cells first. That
was the better call: the gate then passed mechanically instead of producing a failure needing
a paragraph of explanation to read, and a gate whose output needs interpretation is a gate
that will eventually be interpreted wrongly.

**Normalisation was scoped to the 32 failing cells, not applied uniformly.** Five further
provider-URL cells already matched the inventory and were deliberately left alone; normalising
them would have created the very failure being removed. This was verified against the
inventory before either fix cycle was dispatched.

**Two supplementary searches were run rather than the variant gaps being recorded as failures.**
The concepts were covered; only the exact mandated strings were absent. The searches were
required to be real searches with real results, on the explicit ground that a row manufactured
to satisfy a string match is worse than the uncovered variant it hides. Both found genuine
prior art — D12's turned up Cayrol & Lagasquie-Schiex (ECSQARU 2005), the foundational paper
pairing attack and support as independent relations, which is close prior art for a D-System
mechanism and was found only because a literal coverage floor forced a search nobody would
otherwise have run.

**The close-out moved into the worktree mid-phase.** The owner's worktree-everywhere ruling
(`33f931a`) landed while this phase was running and puts session records in the worktree. The
mid-phase checkpoint had already been committed to `dev`. Rather than fork a second copy of
this document, the branch was rebased onto `dev` at the phase boundary so the existing record
came into the worktree and the close-out extends it. The claim commit and its forced catalog
regeneration remain on `dev` as the rule's stated exception.

## Corrections

**The coordinator's own checks were the defective part three times, and the workers were right
each time.** A gate verifier was written with no collision queries transcribed for D07–D11, so
it printed nothing and the silence read as a pass; it now fails loudly on an unchecked domain,
and the guard was tested. A whole-line diff flagged ten "unexplained" changes in a
normalisation that was in fact correct — the agent had stripped `doi:` from `kept` only, as
instructed, leaving it in `result_ids` where it belongs, while the check stripped it
everywhere. A literal-match count of 118 was read as catastrophic when 112 of those were
simply identifiers awaiting an extraction that had not yet run. The common shape: a check
built quickly, producing a clean-looking number, measuring the wrong thing. Insisting on the
underlying file rather than the summary is what caught each one.

**The close-out record itself carried two errors, both caught by the independent review rather
than by this session.** The strategy-phase distribution was transcribed from a verifier whose
domain list deliberately excludes `H4`, so it reported `E: 34` for what the record presented as
a whole-ledger figure; the true count is 42, the eight H4 rows all being strategy E. The tell
was sitting in the record two lines above: the distribution summed to 259 against a stated 267
rows, and nobody added them up. And the drafting-artifact footnote cited a commit hash guessed
at from the pre-rebase history rather than looked up — `8bc8d24`/`1e7bcf1` instead of the actual
`f147b50`. The repository already has a standing rule against guessing an identifier when a tool
will produce it; that rule was written for idea ids and applies exactly as well to commit hashes.
Both are corrected in place.

**A false claim was made to a peer session and corrected.** This session told the peer that
its close review had recorded a worktree run of `check_no_private_content.py` as a passing
verification. It had not — `SESS-2026-09-12-04` line 47 records `31 identifiers checked` from
the primary checkout, and this session had already read that line before asserting its
opposite. The peer corrected it; the correction is recorded as an annotation on `000150`
rather than only in conversation, since a correction living in a closed transcript is not a
correction. The peer's sharper framing of the real defect was adopted: the tool fails silently
rather than loudly, the identifier count inside its own `OK` line is the only thing separating
a real run from a vacuous one, and the fix belongs in the tool rather than in every caller's
vigilance.

## Left undone

**Everything after Pass 1a.** Six phases remain. `phase-lit-02` and `phase-lit-03` finish the
Pass 1 broad map across D21–D27 and D33–D72; the terminology map, domain map and top-20
collision list are `phase-lit-03`'s to close.

**No collision has been adjudicated, and none should have been.** Pass 1 pre-scores are
triage. 159 rows carry `collision_candidate: yes`, and the strongest — an event-sourced
agentic architecture, AGM belief revision as graph-native agent memory, bi-temporal agent
memory systems, the bipolar argumentation framework — are recorded, not resolved. Whether any
shares D-System's actual mechanism is `phase-lit-04`'s deep reading to decide with the full
evidence matrix.

**The three-traditions problem is recorded but unresolved, and it cuts against H0.** "Evidence
graph" was coined independently by network forensics (ACSAC 2005), fact-verification NLP
(GEAR, ACL 2019) and the bioRxiv FAIR-computation paper; "evidence network" carries three
further senses including Wigmore's 1913 legal inference charts. Three papers sharing a name is
not three collisions. A campaign working to support H0 is most exposed exactly where the
evidence looks most favourable, and this is that place.

**Saturation is not yet demonstrable.** D20 produced a real signal — nine searches resolving
to five distinct sources, eight of nine rows converging on one canonical paper — and duplicate
rates were recorded rather than dropped for exactly this reason. But saturation is
`phase-lit-07`'s final gate to measure across the whole campaign, and one domain is not a
campaign.
