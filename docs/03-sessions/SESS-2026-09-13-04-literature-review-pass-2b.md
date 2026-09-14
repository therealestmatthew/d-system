---
schema_version: 1
id: doc-session-literature-review-pass-2b
code: SESS-2026-09-13-04
title: Literature review Pass 2b — fifth execution session of the adversarial campaign
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

# Literature review Pass 2b — fifth execution session of the adversarial campaign

## Phase

`phase-lit-05` — Literature review Pass 2b: forward chaining on the strongest collisions and the
deep read of foundational works, bringing the evidence matrix to the methodology's 20–30 deeply
compared sources. Claimed by `agent-lit`, the fifth execution session of the campaign
([PLAN-023](../01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md)).

The phase is left `active`. Only the owner's `/session-close` moves a phase to `complete`.

## Verification

The phase's three `verification` entries, run in this worktree after the final rebase onto `dev`.

`uv run python -m src.governance`:

```text
Governance OK: 20 systems, 194 documents, 22 memories, 133 backlog phases
exit 0
```

`uv run python tools/check_no_private_content.py` with the changes staged:

```text
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (551 tracked files, 0 identifiers checked)
exit 0
```

**This worktree run is vacuous and is not recorded as a passing verification.** `_private/` is
gitignored and absent here, so the tool builds an empty identifier list (idea `000150`). The real
check ran in the primary checkout at this session's integration, with the live identifier list:
`check_no_private_content: OK (550 tracked files, 31 identifiers checked)`.

Third entry — run delegation-pack section `LIT-05 G` and record real output. Run twice (the first
run failed measurement 3; a fix cycle to `S1` closed it). Final measurements, each independently
re-measured by the coordinator against the files before being accepted:

```text
1. Matrix rows .................. 30 data rows                         PASS (gate 20-30)
2. Blank required fields ........ 0 across 43 fields x 30 rows = 1,290 cells   PASS (gate 0)
3. B+C ledger coverage .......... 24 qualifying rows of 30;
                                  B coverage 24/24, C coverage 24/24   PASS (gate 0 missing)
4. hypotheses_challenged ........ H9:18 H2:13 H7:10 H3:9 H5:7 H8:4
                                  H6:3 H10:3 H11:2 H1:1 H4:0
                                  zero challengers: H4
                                  non-hypothesis tokens: NOT_DETERMINABLE_FROM_ACCESS x1
5. derivative_ancestor filled ... 0 blank across 30 rows               PASS (gate 0 blank)
```

## Acceptance

- **"The evidence matrix holds 20–30 fully populated rows and both chaining directions are logged
  for the strongest collision candidates."** — **Met.** Gate measurements 1 and 2 show 30 rows with
  0 blanks across 1,290 cells; measurement 3 shows B 24/24 and C 24/24 over the 24 qualifying rows.
- **"Derivative-ancestry lineage is recorded wherever multiple sources inherit one mechanism."** —
  **Met.** Gate measurement 5 shows `derivative_ancestor` filled on all 30 rows, 0 blank and 0
  literal `none`. Shared lineages are recorded as one ancestor plus derivatives: PROV-O 2013 across
  three rows, Perry & Wolf 1992 and Snodgrass 1999 across two each.

## Backlog

- `status`: **`active`** — unchanged. Only the owner's `/session-close` may move it to `complete`.
- `next_action`: All five `phase-lit-05` work items are complete and gate-measured, with all five
  `LIT-05 G` gates passing after one fix cycle on `S1`. Awaiting the owner's `/session-close` and
  its independent review. `phase-lit-06` (Pass 3 — adversarial hypothesis testing and the 16
  pending collision second reviews) continues on `agent/lit-campaign`, numbering from
  `LIT-06-S001`. `LIT-05 G` measurement 4 reports **H4 with zero challengers**, H1 with one and H11
  with two — that is where `LIT-06 S1` must dig. Open for the owner, none blocking: ideas
  `000217`–`000220`.
- `session`: `doc-session-literature-review-pass-2b`.
- `completion_evidence`: `research/literature-review/04_evidence_matrix.csv` (30 rows),
  `research/literature-review/00_search_ledger.csv` (967 rows, `LIT-05-S001`–`S079`),
  `research/literature-review/03_source_inventory.csv` (1,108 rows), and this record.
- `next_up`: not pruned — `phase-lit-05` is not in `next_up`, and nothing in it became complete this
  session.

## Unresolved

- **`LIT-05 K`'s candidate arithmetic never closed.** Both fix cycles were spent; 35 candidates were
  expected against 34 listed, one unaccounted. Reported rather than looped on, per the pack's
  two-cycle limit. It does not affect the matrix, which reached its ceiling from the ranked tier.
- **Four findings are open for the owner**, none blocking `phase-lit-06`: ideas `000217`
  (branch-model/claim-protocol collision, which will recur at `phase-lit-06`'s claim), `000218`
  (`LIT-05`'s item order defeats its own gate measurement 3), `000219` (a gate silently dropping
  unexpected tokens), `000220` (mention-counting producing H0-flattering false shared ancestors).
  `000218`–`000220` are linked `relates_to` `000218` as one campaign-instrument batch.
- **`phase-lit-07` remains barred.** `PROMPT-031`'s pre-synthesis check-in section is still empty by
  construction.
- **The branch is not integrated.** `agent/lit-campaign` is 39 commits ahead of `dev`; integration
  is the owner's call.

## The claim required an unscheduled integration, on the owner's ruling

Preflight found the two lock tables disagreeing. On `dev`, `phase-lit-04` still read
`status: active, agent: agent-lit`; on `agent/lit-campaign` the owner's `/session-close` (commit
`e9b32ab`) had marked it `complete`. The branch was 31 commits ahead of `dev` and `dev` 0 ahead,
so this was withheld integration rather than divergence — `PLAN-023`'s branch model schedules the
next integration at the pre-synthesis check-in after `phase-lit-06`.

The consequence was concrete: `LIT-05 K` is instructed to claim the phase per `AGENTS.md`, and
that claim fails the governance check at `src/governance/backlog.py:67`, because `agent-lit` would
hold two active phases. The owner ruled: integrate now, then claim normally.

`agent/lit-campaign` was fast-forwarded into `dev` (a true fast-forward; `dev` was a strict
ancestor). The integration-time confidentiality check ran in the primary checkout against the live
identifier list — `check_no_private_content: OK (550 tracked files, 31 identifiers checked)` — a
real 31-identifier run, not the vacuous worktree run idea `000150` records. `phase-lit-05` was then
claimed on `dev` in commit `32d530e`.

**This will recur.** The campaign's branch model and the claim protocol collide structurally: any
phase claimed after an un-integrated close hits the two-active-phases error, because `dev`'s lock
table cannot see a close that lives only on the branch. Raised as idea `000217`.

## What was dispatched

Item order `K` → `S1` → `X1` → `X2` → `G`, from
[PROMPT-029](../02-prompts/PROMPT-029-literature-review-delegation-pack.md), each section verbatim
with its shared blocks (`K` self-contained; `S1` = C+S+section; `X1`/`X2` = C+D+section; `G` =
G+section). Models as the pack fixes them: `K` and `G` on Haiku, `S1`/`X1`/`X2` on Sonnet.

### `LIT-05 K` — kickoff (Haiku), 2 of 2 fix cycles spent, partially unresolved

Its measurements were confirmed exactly against the files. Its X1 batch naming was defective twice.

Fix cycle 1: the candidate list contained works that were already matrix rows
(`jansen-bosch-…-2005` is row 7, `zep-…-2025` is row 20) despite asserting it excluded them; it
claimed every candidate had inheritance count 1, contradicted by Perry & Wolf 1992 appearing in two
rows; and it ordered by "discovery order in matrix file" and called that a rank.

Fix cycle 2: **the corrected list ranked a withdrawn claim as the matrix's strongest shared
lineage.** `K` counted *mentions* of a work in `derivative_ancestor` as *inheritance*. Both
`Digital Engineering Strategy` and `Global Horizons` are mentioned in rows 16 and 19; both cannot
be shared ancestors of both rows. Row 16 carries `phase-lit-04 X3`'s correction stating the two
sources cite "two different, both DoD-adjacent, named documents for the same term, **not one shared
ancestor**". `K` read that sentence and scored it as a shared ancestor, ranking DAU/DoD 2018 first.

A mention-counting method manufactures shared ancestors, and a shared ancestor is evidence *for*
H0 — so every error it makes points the same way. This specific claim had already been withdrawn
once in Pass 2a by an agent that read the primary source, and was re-entering through the ranking.
Raised as idea `000220`.

Two further errors: `K` merged Kruchten 1995 (4+1 View Model) and Kruchten 2004 (decision ontology)
into one candidate on the shared surname — a shared name treated as a shared work; and it missed
PROV-O 2013, named in three rows, filing it in the count-1 remainder. Surviving unresolved: its
candidate arithmetic does not close (37 − 2 reported as 33, later 35 expected against 34 listed).
Fix cycles were exhausted, so this is reported rather than looped on, per the pack.

### `LIT-05 S1` — forward chaining (Sonnet)

Population measured by the coordinator, not taken on trust: **17 of 30 matrix rows scored ≥ 3 on
either overlap scale, not the 18 the brief and `phase-lit-04`'s resume state both stated.** The
three below threshold are `keim-kaplan-…-2026` (2/2), `assumptions-management-…-2018` (2/1) and
`ibm-architectural-blueprint-…-2006` (1/1). `S1` independently re-derived the same 17.

Wrote `LIT-05-S001`–`S035`: 17 subjects, 2 rows each except `procko-provtracer` at 3, which is
indexed by no citation provider and needed a Crossref bibliographic proxy. All 35 rows
`strategy_phase: C`, `pass: 2`, no blank `subject_source_id`, `chain_decision` or
`duplicate_handling`.

Provider behaviour, logged as real zero-yield rows rather than omitted: Semantic Scholar 429 on 9
of 13 attempts, 200 on 3, 404 on 1. Several of the strongest collisions have zero confirmed
citations because they are 2026 preprints too recent to have any.

Eleven inventory rows added, two flagged low-confidence because the *citation link itself* was
unverified — `proper-…-2014` (OpenAlex misattributing unrelated same-repository dissertations as
citations) and `pina-et-al-dlprov-2025` (keyword overlap, not a confirmed citation). Flagging the
link rather than the content is the right unit: an unverified forward citation recorded as real
manufactures a lineage, the same failure `K` made.

The field-count-on-write rule (idea `000211`) caught a live `TypeError` on the em-llm row **before
a malformed row reached disk**.

### `LIT-05 X1` — deep read, foundational works (Sonnet)

Matrix 20 → 25. Batch taken from `K`'s corrected ranking, capped at 25 to reserve `X2`'s slots.

| Source | comp/arch | critical | access | confidence |
|---|---|---|---|---|
| `w3c-prov-o-2013` | 3/2 | no | full_text | high |
| `perry-wolf-foundations-software-architecture-1992` | 2/1 | no | full_text | high |
| `snodgrass-developing-time-oriented-database-applications-sql-1999` | 3/2 | no | full_text | high |
| `agm-partial-meet-contraction-revision-1985` | 3/1 | no | secondary_coverage | medium |
| `nii-blackboard-model-problem-solving-1986` | 2/2 | no | full_text | medium |

`X1` resolved the PROV-O question at **3 rows**, matching the coordinator's measurement against
`K`'s 2.

It also caught a **WebFetch summarization hallucinating a five-tuple** for Perry & Wolf 1992 —
`{Elements, Form, Rationale, Constraints, Context}` — where the `pdftotext`-recovered primary text
gives the actual three-tuple `{Elements, Form, Rationale}`. It used the primary text. Block C's
"generated summaries are leads, never evidence" caught a live fabrication.

Cleared the five known-wrong inventory rows from Pass 2a under the owner's `000209` ruling, each
re-verified at the source, every slug left unchanged per `000210`: EM-LLM to ICLR 2025 conference;
Evidence Graphs to IPAW 2021 with bare DOI `10.1007/978-3-030-80960-7_3`; Keim & Kaplan to accepted
ICSE-C '26; de Boer to joint authorship with Farenhorst; and the patent recorded as **granted
2025-11-04 as US12461717B2**.

### `LIT-05 X2` — deep read, forward finds (Sonnet)

Matrix 25 → 30, the methodology's ceiling, reached exactly.

| Source | comp/arch | critical | access | confidence |
|---|---|---|---|---|
| `burckhardt-et-al-durable-functions-stateful-serverless-2021` | 3/1 | no | full_text | high |
| `zimmermann-et-al-managing-architectural-decision-models-2009` | 4/3 | **yes** | full_text | high |
| `burns-groth-agentic-ontological-notebook-memory-2026` | 4/3 | **yes** | preprint_version | high |
| `levinson-et-al-fairscape-…-2021` | 3/3 | no | full_text | high |
| `capilla-et-al-web-based-tool-…-2006` | 2/2 | no | abstract_only | medium |

Resolved both of `S1`'s low-confidence citation links, in opposite directions and by method:
`proper-…-2014` **confirmed**, by checking Proper's own OpenAlex `referenced_works` — the forward
field — rather than the noisy reverse citing-works list; `pina-et-al-dlprov-2025` **disconfirmed**,
by reading DLProv's complete PMC full text, in which "Procko" and "ProvTracer" appear nowhere. Both
outcomes written back to the inventory's `exclusion_reason`.

The Liu Springer CCIS chapter was genuinely unobtainable after five providers returned paywall,
bot-wall, 404 and quota errors. Recorded honestly and correctly did not consume a matrix slot.

## `LIT-05 G` — the phase gate

Run twice. Every measurement was independently re-measured by the coordinator against the files
before being relayed; all figures below matched.

**First run — 4 PASS, 1 FAIL.**

| # | Measurement | Population | Result |
|---|---|---|---|
| 1 | Matrix rows | 30 parsed data rows | PASS (20–30) |
| 2 | Blank required fields | 43 contract fields × 30 rows = 1,290 cells | PASS (0) |
| 3 | B+C ledger coverage | 24 qualifying rows of 30 | **FAIL** |
| 4 | `hypotheses_challenged` | 30 rows, `;`-separated | see below |
| 5 | `derivative_ancestor` | 30 rows | PASS (0 blank) |

Measurement 3 measured B coverage 24/24 and **C coverage 17/24**. The seven rows missing `C` were
exactly those created after `S1` ran: `w3c-prov-o-2013`, `snodgrass-1999`, `agm-1985`,
`zimmermann-2009`, `burns-groth-2026`, `burckhardt-2021`, `levinson-2021`.

**This was a sequencing property of the phase's own item order, not a worker defect.** `S1 → X1 →
X2 → G` runs forward chaining before the deep reads that create new qualifying rows, so those rows
structurally cannot carry a `C` row. Raised as idea `000218`.

Routed as fix cycle 1 of 2 to the responsible section (`S1`), per Block G. `S1` wrote
`LIT-05-S069`–`S079`, 11 rows covering all seven subjects. Its handling of the three canonical
works is the part that mattered: PROV-O (232 citations), AGM 1985 (3,241 citations) and Snodgrass
(no indexed work_id) were each **declined with a recorded `chain_decision`** rather than enumerated,
on the ground that their campaign-relevant descendants are already matrix rows. Eleven honest rows
rather than several thousand manufactured ones.

`S1` also caught and corrected its own fabrication before it reached disk: its first draft of the
Plataniotis row carried an invented author list written from memory
(`van der Linden, Hoppenbrouwers, Lartseva, Proper`). The Crossref verification lookup it ran
immediately after (`LIT-05-S076`, filed under `strategy_phase: D` per idea `000149`) returned the
real authors (Plataniotis, de Kinderen, Proper); it fixed the citation, renamed the `source_id`, and
logged the mismatch in the verification row. Second hallucination caught at the source in one
session, after `X1`'s Perry & Wolf tuple.

It declined a JMIR scoping review surfaced from the FAIRSCAPE chain, on the ground that a Phase-A
survey is not a Phase-C mechanism collision — refusing the easy row that would have inflated
apparent prior art.

**Re-run — all 5 PASS.** Measurement 3: 24 qualifying rows, B coverage 24/24, C coverage 24/24, 0
missing.

### Measurement 4 — where `phase-lit-06` must dig

```text
H9: 18   H2: 13   H7: 10   H3: 9   H5: 7
H8:  4   H6:  3   H10: 3   H11: 2  H1: 1
H4:  0   <-- zero challengers
```

**H4 is the only hypothesis with zero challengers.** Two observations beyond that: H1 has exactly
one challenger and H11 two, thin enough that `phase-lit-06` should treat them as near-gaps rather
than covered — a single challenger is one deep read away from zero. And the distribution is
lopsided: H9 and H2 carry 31 of the 70 challenge records between them, so the evidence is
concentrated on traceability and typed transitions while the actor and convergence hypotheses are
thinly served.

One non-hypothesis token appears in the field: `NOT_DETERMINABLE_FROM_ACCESS`, on
`capilla-et-al-web-based-tool-…-2006`, which is `abstract_only`. The value is contract-correct. The
gate's first run silently dropped it despite being instructed to name unexpected tokens; the re-run
reported it. Raised as idea `000219`.

## Substantive results

**The deep read scored down again, on exactly the sources most likely to be scored up.** Pass 2a
revised 11 of its first 13 sources downward (mean −1.31 component, −1.46 architecture) and none
upward. `X1` then took five canonical foundational works — the ancestors H0 predicts D-System
recombines — and scored every one at 2–3 with no critical collision. If the campaign were
confirming its own thesis, old famous works whose vocabulary D-System echoes, read by an agent told
the campaign supports H0, is precisely where it would show. They scored low. That is weak evidence
the Pass 1 / Pass 2 separation is doing real work, reproduced on a different class of source by a
different worker than Pass 2a's.

**Forward chaining found very little downstream work, and that is a result.** The strongest
collisions are 2026 preprints with zero confirmed citations; Semantic Scholar rate-limited 9 of 13
attempts; one source is indexed by no provider at all. Recorded as real zero-yield rows with their
queries rather than omitted, which is what lets `phase-lit-07` distinguish "nothing exists" from
"nothing was found".

**Two new critical collisions**, both from `X2`, now carrying `second_review: pending` for
`phase-lit-06`: `zimmermann-et-al-…-2009` (outcome-status lifecycle, a formally-proved `triggers`
transition, per-outcome `changedBy` provenance — the strongest match yet to D-System's
decision/transition layer) and `burns-groth-…-2026` (the strongest H11 runtime-to-knowledge match
found so far, with a real benchmark). Matrix total: **16 `critical_collision: yes`, 16
`second_review: pending`**.

**One genuinely new cross-domain contact** the campaign's own domain sweep had not reached:
`burckhardt-et-al-durable-functions-stateful-serverless-2021`, durable-execution and
checkpoint-replay semantics from the serverless-workflow tradition, colliding with LangGraph's
checkpoint mechanism and so with H8. Its chain produced two further leads (`netherite-2022`,
`halfmoon-…-2023`).

## Evidence state at close

- `research/literature-review/04_evidence_matrix.csv` — **30 rows**, 43 fields, LF, **0 blank cells
  across 1,290**; 16 `critical_collision: yes`.
- `research/literature-review/00_search_ledger.csv` — **967 rows**, 15 fields, CRLF throughout (968
  CRLF, 0 bare LF), **0 malformed**; `LIT-05-S001`–`S079` contiguous.
- `research/literature-review/03_source_inventory.csv` — **1,108 rows**, 13 fields, LF.

## Spend posture

- **Searches this phase**: 79 ledger rows, `LIT-05-S001`–`S079` — 45 forward-chaining (`C`), 5
  backward-chaining (`B`), 29 under `D` (bibliographic verification and source access, the enum
  having no verification value, per idea `000149`).
- **Sources deep-read**: 10. Campaign matrix total **30 of the methodology's 20–30** — the ceiling,
  reached exactly. Pass 2 is complete.
- **Opus escalation**: none spent, in this phase or the campaign to date. The kick-off record's
  single documented escalation remains available.
- **Descope rungs**: none taken.
- **Fix cycles**: `K` 2 of 2 (exhausted, partially unresolved); `S1` 1 of 2; `X1`, `X2`, `G` none.
- **Sessions**: 5 of a seven-session runway, range six to eight.

## Resume state

- **Current phase**: `phase-lit-05`, left `active`, all five work items complete and gate-measured
  with all five gates passing. Only the owner's `/session-close`, after its own independent review,
  may mark it `complete`.
- **Next phase**: `phase-lit-06` — Pass 3, adversarial hypothesis testing H1–H11 and the collision
  second reviews. Its items are `K` → `S1` → `X1` → `R` (one dispatch per critical collision, to
  agents that produced neither the collision's matrix row nor phases 05/06) → `X2` → `G`.
- **Search ids**: `LIT-06` numbers from **`LIT-06-S001`**, monotonic per phase; they do not continue
  from `LIT-05-S079`.
- **`phase-lit-06`'s inputs**: 16 rows carry `second_review: pending`. `LIT-06 S1` must dig where
  `LIT-05 G` measured thin — **H4 has zero challengers**, H1 has one, H11 has two.
- **Leads carried forward, in the inventory but not the matrix** (the matrix is at its 30-row
  ceiling): `plataniotis-…-decision-design-graphs-2013`, `burckhardt-…-netherite-2022`,
  `qi-liu-jin-halfmoon-…-2023`, and the confirmed `proper-…-2014`.
- **A fresh session must read**: `AGENTS.md`, `GOV-006`, `PROMPT-031` (the kick-off record, which
  wins over the coordinator prompt), `PROMPT-030` in full, and this record.
- **`phase-lit-07` remains barred.** `PROMPT-031`'s pre-synthesis check-in section is still empty by
  construction. A kick-off paragraph describing the planned pause is not a held check-in.
- **Open for the owner**, none blocking `phase-lit-06`: ideas `000217`–`000220`.
- **Integration**: `agent/lit-campaign` was integrated into `dev` at the *start* of this session on
  the owner's ruling, to free the claim slot. It is now 38 commits ahead again and **not**
  integrated. The diff is `git diff dev..agent/lit-campaign`.
