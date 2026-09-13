---
schema_version: 1
id: doc-session-literature-review-pass-1b
code: SESS-2026-09-13-01
title: Literature review Pass 1b — second execution session of the adversarial campaign
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

# Literature review Pass 1b — second execution session of the adversarial campaign

## Phase

`phase-lit-02` — Literature review Pass 1b, the broad map of agent memory, decision intelligence,
requirements engineering and rationale-capture domains (D21–D27, D33–D45). Claimed by `agent-lit`,
the second execution session of the campaign
([PLAN-023](../01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md)).

Work runs on the long-lived campaign branch `agent/lit-campaign`, in the worktree
`../d-system-worktrees/lit-campaign`. All twelve delegation-pack sections for this phase were
dispatched verbatim from [PROMPT-029](../02-prompts/PROMPT-029-literature-review-delegation-pack.md),
one at a time, in pack order: `K` → `S1/X1` → `S2/X2` → `S3/X3` → `S4/X4` → `S5/X5` → `G`. Models
were as the pack fixes them — `K` and `G` on Haiku, every `S` and `X` on Sonnet. **No Opus
escalation was spent** and **no descope rung was taken.**

## Verification

The phase's three `verification` entries, re-run at close against the merged state — the branch
rebased onto `dev` at `93802e7` and fast-forwarded in at `da88ece`.

```text
$ uv run python -m src.governance
Governance OK: 20 systems, 191 documents, 22 memories, 137 backlog phases
(exit 0)

$ uv run python tools/check_no_private_content.py        # in the worktree
note: _private/portfolio/ not found — content check skipped (path check still ran; this is
expected in CI / a fresh clone)
check_no_private_content: OK (545 tracked files, 0 identifiers checked)
(exit 0)

$ uv run python tools/check_no_private_content.py        # in the primary checkout, post-merge
check_no_private_content: OK (545 tracked files, 31 identifiers checked)
(exit 0)

$ uv run python -m pytest -q
578 passed, 2 warnings
(exit 0)
```

**The worktree run verified nothing, and its `OK` must not be read as a pass.** `_private/` is
gitignored and therefore absent from every worktree, so the tool built an empty identifier list and
reported success for having compared zero identifiers against 545 files. The verification entry says
"with the changes staged"; the tree was clean, so there was nothing to stage, and the pre-commit hook
ran the same vacuous check at each commit. This is idea `000150`, on which the owner ruled on
2026-09-12 to accept the gap and rely on the integration-time check.

**The integration-time check is the one that verified anything, and it passed.** Run in the primary
checkout immediately after the merge, with the live identifier list: **31 identifiers checked**
against 545 tracked files, exit 0. No confidential identifier reached any campaign deliverable. The
independent review reproduced this figure on its own run.

### The phase gate — delegation-pack section `LIT-02 G`, real output

`G` ran twice. Its first run reported every gate as PASS but carried two wrong numbers, one of them
serious; the second run corrected both. **No gate condition ever failed.**

First run, Measurement 2 (wrong):

```text
Total inventory rows: 41 | Kept rows: 0 | Excluded rows: 41
```

That is the count of every `status: excluded` row in the whole 826-row inventory, including
`phase-lit-01`'s. The gate filtered on status and not on domain, then reported the result as the
domain-scoped total. "Zero kept rows" for a phase that inventoried 358 candidates is the shape the
dispatch had explicitly warned about — a measurement that condemns substantially all of its input.
Measurement 3 separately reported the naive distinct count (371) alongside the SICI-aware absent
count (0), conflating the two methods.

Second run, after the fix cycle:

```text
Gate 1a  PASS — all 20 domains ≥2 rows with distinct queries; narrowest D43 at 8 rows / 8 queries
Gate 1b  PASS — 91/91 mandated variants covered verbatim, 0 uncovered
Gate 2   PASS — 388 inventory rows for the target domains (358 candidate, 30 excluded),
                0 excluded rows missing an exclusion_reason
Gate 3   PASS — naive split: 371 distinct, 2 missing
                SICI-aware split: 370 distinct, 0 missing  ← the true measurement
governance exit 0; check_no_private_content exit 0 (0 identifiers checked, see above)
```

**Gate 3's two figures are both real and the difference is the point.** The `kept` column is
`;`-separated and rows `LIT-02-S225`/`S228` carry a Wiley SICI DOI containing a literal semicolon
(`10.1002/(sici)1097-4571(198905)40:3<200::aid-asi11>3.0.co;2-u`). A naive split shreds it into two
fragments that exist nowhere, producing four phantom pair-misses. The DOI is correct and the
inventory carries it in full; the data was deliberately not rewritten. Recorded as idea `000200`.

### Coordinator measurements, taken independently of the gate

```text
ledger:    561 rows total | 294 this phase, LIT-02-S001..LIT-02-S294, contiguous
           562 CRLF line terminators, 0 bare LF
           strategy_phase distribution: {'A': 97, 'D': 162, 'E': 35}  (sums to 294)
           86 zero-yield rows, every provider failure among them logged with its query
inventory: 826 rows total | 388 in scope for D21-D27, D33-D45
           358 candidate, 30 excluded (every one with a reason)
           115 collision_candidate: yes in scope; 274 across the whole inventory
           0 CRLF, 827 bare LF — the inventory is LF where the ledger is CRLF
map:       741 lines, sections for all 20 domains of this phase
```

## Acceptance

- **"Every matrix domain D21-D27 and D33-D45 has at least two ledger rows with distinct terminology
  variants."** — **Met.** All 20 domains clear the floor, the narrowest being D43 at 8 rows with 8
  distinct queries, and `LIT-02 G` measured 91 of 91 mandated minimum variants appearing verbatim in
  a logged query for their own domain, with none uncovered. The variant lists were re-derived by the
  gate from `PROMPT-029` itself rather than taken from the coordinator, which mattered: the
  coordinator's dispatch stated 76 variants and the true figure is 91.
- **"Candidate sources for these domains are in the inventory with inclusion or exclusion
  rationale."** — **Met.** 388 inventory rows for the target domains, all 30 exclusions carrying a
  reason, and every one of the 370 distinct kept identifiers resolving to an inventory row under the
  SICI-aware split. No row cites a generated summary as evidence; vendor material encountered in
  D26/D27 was either excluded under §7 or typed `lead`.

Both conditions were recomputed at checkpoint against the repository as it stands after the rebase.

## Backlog

`phase-lit-02` is `status: complete`, `agent: agent-lit`, with `session`, `completion_evidence` and
`result` set to what exists now and was actually measured. It was never in `next_up`, so there was
nothing to prune.

The phase reached `complete` through the owner's `/session-close`, after the independent review
recorded below — not by an agent's own judgement that the work looked finished.

`next_action`: None outstanding. `phase-lit-03` (Pass 1c, D46–D72) is unblocked and continues on the
same campaign branch.

## Unresolved

- **Integrated on the owner's direction at this phase boundary**, as at `phase-lit-01`'s and earlier
  than the pre-synthesis check-in `PLAN-023` schedules. `agent/lit-campaign` was rebased onto `dev`
  at `93802e7` and fast-forwarded in at `da88ece`: 8 files, 1561 insertions. The branch and worktree
  were deliberately **not** deleted — `PLAN-023`'s branch model has every campaign phase commit to
  that one branch, and `phase-lit-03` continues on it.

  **The confidentiality gate cleared it with a real check.** Immediately after the merge, in the
  primary checkout with the live identifier list:
  `check_no_private_content: OK (545 tracked files, 31 identifiers checked)`, exit 0. Every
  worktree run this session reported `0 identifiers checked` and verified nothing.

  An earlier draft of this bullet said the branch diff was "three files … and nothing else." That
  was wrong and the review caught it. At the tip it described, `git diff f400737..054eae7` carried
  **twelve** files: the three research deliverables plus nine belonging to a peer's
  `log-anti-patterns` workflow, which the campaign branch had rebased on top of but which `dev` did
  not yet carry. The three research line counts (294 / 401 / 388) were right; the claim about what
  integrating would bring in understated it by nine files. No harm followed — `dev` fast-forwarded
  to `93802e7` before the campaign merge — but the sentence as written was false.
- **The idea-id race fired twice in this session, the second time onto the ids that fixed the
  first.** Occurrence one: this session allocated `000156`–`000160` on the unintegrated campaign
  branch while two peer commits allocated `000156`–`000194` on `dev`; all five collided. Occurrence
  two, about eight minutes later: a peer allocated `000195` on `dev` while that renumbering was
  being committed, so the freshly renumbered `000195` collided immediately. Both were resolved by
  `1a4dd1b`'s procedure — the idea commits were dropped during the rebase rather than hand-edited,
  and the set was re-appended through the writer, finally as `000196`–`000200`. **Renumbering is a
  retry, not a fix, and it loses to a peer that is still allocating.** Each cycle cost a rebase,
  five re-appends, three re-links, two re-annotations and an edit to every document citing the old
  ids. The recovery is also lossy: the annotation this session placed on `000147` was destroyed with
  the dropped commits both times and reconstructed from the transcript, which a fresh session could
  not have done. Both occurrences are recorded on `000158`, which already held the finding; the peer
  independently annotated the same idea within minutes, and those two annotations merged cleanly —
  the same append-only property that would have merged two `created` events for one id silently.
- **Five instrument gaps recorded as ideas `000196`–`000200`.** A background subagent calling
  `EnterWorktree` hangs silently and forever; the campaign's deliverables disagree on line endings
  (ledger CRLF, inventory and map LF) so the standing CRLF warning is wrong for the file an
  extraction writes; the governance check passes with a stale catalog and `--catalog` prints instead
  of writing; `collision_candidate` is undefined on a duplicate row while `LIT-03 C` ranks the
  top-20 without filtering on `status`; and a `;`-separated `kept` column cannot hold a SICI DOI.
  `000197`, `000199` and `000200` are linked to `000147`.
- **A cross-phase scoring disagreement stands unresolved and is `phase-lit-03`'s to settle.**
  `structured-belief-state-llm-memory-benchmark-2026` is scored `collision_candidate: no` by
  `phase-lit-01` at D30 and `yes` by this phase at D22, with identical pre-scores (3/2). It is
  deliberately the only excluded row in the inventory carrying `yes`, which makes it findable.
  Averaging it away would resolve a dispute in favour of whichever phase ran first.
- **A phase-wide provider outage limits what the gate's coverage figures mean.** `export.arxiv.org`
  and `api.semanticscholar.org` failed on every attempt across every domain of this phase — curl
  exit 28 timeouts, HTTP 429 "Rate exceeded", and at `S271` a new signature where `-L` returned a
  stale cached feed for an unrelated query. Coverage for all 20 domains therefore rests on web
  search, OpenAlex and Crossref. Every attempt is a real zero-yield ledger row, so the record is
  honest, but a passing variant-coverage gate does not mean the provider mix delivered what it
  would have with those two endpoints live.
- **Nine fix cycles, eight issued by the coordinator and one a worker issued to itself; all nine
  closed.** The coordinator's eight: `K` left the catalog stale after the claim, putting `dev` red;
  `S1` twice, for a false "reconsidered there" claim in `LIT-02-S002` that never happened and for an
  author/implementation search it ran but did not log; `X1` twice, for the inventory row the first
  fix created and for four dedup rows double-counting in the top-20; `X2` for two PMC years left
  `n.d.` that a lookup settled; `X4` for a truncated identifier failing a byte-exact gate match; and
  `G` for Measurement 2's population. The ninth is `X3`'s own, committed in `add600b`, correcting
  `collision_candidate` on three dedup rows to the convention it had just worked out.

  An earlier draft said "seven … across K, S1, X1, X2, X4 and G" — a number that contradicted its
  own list of eight and omitted `X3`'s entirely. The review caught it. Only seven commits carry the
  literal words "fix cycle" (`S1`×2, `X1`×2, `X2`, `X3`, `X4`); `K`'s fix was folded into the
  amended claim commit and `G` writes no repository file at all, which is how the miscount survived.
  The error understated this session's own defect rate, which is the direction that matters.
  None was cosmetic.
- **The coordinator's relayed claims were wrong four times while the evidence was sound.** A
  DOI/dissertation conflation passed from `S4`'s report into `X4`'s dispatch; a non-existent
  Antoniol row in D34 passed from `S5`'s report into `X5`'s dispatch; a mandated-variant count of 76
  against a true 91 went into `G`'s dispatch; and an early catalog check was misread as clean. Three
  were caught by workers reading the files rather than the report, and the fourth by instructing the
  gate to derive the number from `PROMPT-029` instead of trusting it. The pattern is one-directional:
  worker *outputs* were verified against files throughout, worker *narrative* was relayed forward
  without the same check.
- **Two sources remain unresolved and are named rather than dropped.** A coding-agent
  requirements-churn paper on `pith.science` (`S160`) returned empty content on fetch, and an
  Academia.edu "Supporting Requirements Traceability with Rationale" paper (`S136`/`S142`) has no
  resolvable identifier via Crossref. Neither was fabricated into a kept row.
- **One identifier does not resolve, and it is a registration lag rather than a fabrication.**
  `10.1145/3774904.3792665` returns 404 from both Crossref and `doi.org`, and no ACM registration is
  findable. It was not invented: `LIT-02-S058`'s `result_ids` records the search returning
  `dl.acm.org/doi/10.1145/3774904.3792665` for "Dynamics of Human-AI Collective Knowledge on the
  Web", an ACM Web Conference 2026 paper whose DOI Crossref has not yet activated. It sits on
  `dynamics-human-ai-collective-knowledge-web-2026-acm-doi-dup`, which is `status: excluded` and
  `dedup_of` the canonical arXiv row `arxiv:2601.20099` — independently verified real, with matching
  title and authors. No fix cycle was dispatched: the identifier is genuine as encountered, the row
  carries no evidential weight, and the place this gets settled is `phase-lit-07`'s
  `13_validated_bibliography.md`, whose seed-source promotion procedure requires bibliographic
  identity to be verified per source. Flagged here so it is not rediscovered as a surprise.

## Review

An independent sub-agent, started fresh with no context from this session and explicitly not a fork,
reviewed the 49-commit range `1e7a36e^..da88ece` against the phase's acceptance conditions. It was
told the range is interleaved with peer work from this session's rebases and given the subject and
path filters to isolate the phase's own commits. It re-derived the mandated variant lists from
`PROMPT-029` itself, re-ran the verification commands, and externally verified 36 sampled
identifiers. Its findings, verbatim:

> **Acceptance condition 1 — HOLDS.** I re-transcribed the mandated minimum variants myself from
> `PROMPT-029` lines 336–445 (`LIT-02 S1`–`S5`), independently of the session record. My count:
> **91 variants across 20 domains** (D21:5, D22:6, D23:5, D24:6, D25:4, D26:4, D27:5, D33:6, D34:5,
> D35:4, D36:4, D37:4, D38:3, D39:4, D40:5, D41:5, D42:3, D43:4, D44:4, D45:5). That independently
> confirms 91 and the record's statement that the coordinator's relayed figure of 76 was wrong.
>
> ```text
> GATE 1a  PASS (narrowest D43 = 8 rows / 8 queries)
> GATE 1b  91/91 covered, uncovered=0 -> PASS
> ```
>
> Every variant appears as a literal case-insensitive substring of some `query` in a row whose
> `domain_id` is that variant's domain. No domain has a duplicate query (rows == distinct queries in
> all 20). The scope-domain row counts sum to exactly 294, which equals the LIT-02 row count — so
> every LIT-02 row sits in a scope domain and no other phase's rows contribute.
>
> I also tested a **stricter** reading of the condition — ≥2 *rows* each carrying a *distinct*
> mandated variant, not merely distinct queries. All 20 domains pass that too.
>
> I checked whether the coverage was gamed by stuffing variants into token queries. It was not. The
> awkward compound variants resolve to real search strings, e.g. `LIT-02-S002` = `working/long-term
> memory taxonomy cognitive architecture SOAR/ACT-R`, `LIT-02-S119` = `pre/post-RS traceability
> Gotel Finkelstein 1994 analysis requirements traceability problem`, `LIT-02-S244` =
> `"superseded decisions" architecture decision record status lifecycle`.
>
> **Acceptance condition 2 — HOLDS.**
>
> ```text
> Measurement 2  total=388  candidate=358  excluded=30  excluded-missing-reason=0 -> PASS
> Measurement 3  naive ;-split    distinct=371  missing=2
>                SICI-aware split distinct=370  missing=0
> ```
>
> All 30 in-scope exclusions carry a substantive reason; the shortest is 217 characters, none is
> blank or `none`. 29 are dedups; exactly one is a merit exclusion. Every in-scope row's `found_by`
> resolves to a real ledger row. Every LIT-02 ledger row with a non-empty `kept` carries a non-empty
> `inclusion_rationale` — 0 exceptions. **Trap (a) confirmed as documented:** matching `kept` against
> `source_id` instead of `url_or_doi` yields a spurious 370–371 "missing" against a true 0.
>
> **On the SICI DOI — my independent judgement: leaving it unmodified was the right call.** I
> resolved it via Crossref: `10.1002/(SICI)1097-4571(198905)40:3<200::AID-ASI11>3.0.CO;2-U` →
> *"gIBIS: A tool for all reasons"*, Conklin & Begeman, **JASIS 1989**. It is a genuine registered
> DOI whose semicolon is structural to the SICI format. Truncating or re-encoding it would
> substitute a broken identifier for a correct one, and it is the only semicolon-bearing identifier
> in the entire 826-row inventory. The correct measurement is therefore the SICI-aware one; the
> naive split's 2 "misses" are fragments of one real DOI, not phantom sources.
>
> **Fabrication check — clean.** I independently verified **36 identifiers spanning all five
> dispatches**: 16 arXiv abstract pages, 15 DOIs via Crossref, 5 USPTO numbers via Google Patents.
> All 16 arXiv IDs resolve with matching titles, authors and dates, including every 2026-dated one I
> sampled. All 5 USPTO numbers are real with matching titles. 14 of 15 DOIs resolve. **The 2026
> dating is genuine, not invented.**
>
> One failure, which does not affect the evidence base: `10.1145/3774904.3792665` returns 404 from
> Crossref and `doi.org`. It sits on an `excluded` dedup row whose underlying paper is independently
> verified real (arXiv `2601.20099`). A non-resolving identifier on an excluded duplicate row for a
> real paper — worth correcting, not evidence-bearing.
>
> **Evidence hygiene — clean.** 0 ledger rows keep an AI-generated-summary identifier. 5 in-scope
> rows typed `lead` — exactly the sanctioned bucket. Vendor material appears in `result_ids` with
> explicit exclusion rationale, never kept as evidence. The provider outage is real and honestly
> logged: `arXiv API` 11 rows / **0** kept; `Semantic Scholar API` 10 rows / **0** kept; 86
> zero-yield rows, 0 with a blank query.
>
> **Scope discipline — clean.** The frozen baseline is untouched; every frozen path last changed in
> `b2b564b` ("Initial commit"). The deliverables are strictly append-only — `git diff --numstat` over
> the whole range: `294 0`, `401 0`, `388 0`. `phase-lit-01`'s rows were never modified. **No verdict
> language** across all 1083 added deliverable lines. Two passages use prior-art framing stronger
> than pure recording, both framed as collision candidates, which is precisely the Pass 1 artifact.
>
> **Every stated figure reproduces exactly** — 294 ledger rows; contiguous `LIT-02-S001..S294`; 561
> ledger / 826 inventory totals; `strategy_phase` A 97 / D 162 / E 35, **which does sum to 294**; 86
> zero-yield rows; 388 in scope; 115 `collision_candidate: yes` in scope and 274 overall; 91 mandated
> variants; 741-line terminology map; 562 CRLF / 0 bare LF; D43 narrowest at 8/8; 578 tests. Except
> for two things:
>
> **1. "The diff is three files … and nothing else" does not reproduce.** At the exact tip the record
> measured, `git diff f400737..054eae7` shows **12 files, not 3**. The nine extra belong to a peer's
> `log-anti-patterns` workflow. No harm resulted, but the claim as written is false.
>
> **2. The fix-cycle count contradicts its own enumeration and omits a real fix cycle.** The record
> says "seven … and all seven closed" and then lists **eight** items, omitting `add600b` "LIT-02 X3:
> … + fix cycle 1". The same wrong attribution is copied into `backlog.yaml`'s `result`. **The error
> direction is understating its own problems.**
>
> **The record's self-criticism — accurate, not inflated.** Everything I could check corroborates it:
> the 76-vs-91 miscount (I derive 91 independently); the non-existent Antoniol D34 row (all four
> Antoniol rows are in D44, none in D34); the idea-id race (`000158` carries two independent
> `annotated` events, one from `agent-lit` and one from the peer `agent-pack-factory`); the
> cross-phase scoring disagreement (**exactly one** excluded row in 826 carries
> `collision_candidate: yes`, as described and deliberately findable); and the two unresolved sources
> (`LIT-02-S160` and `S142` both have `kept: none`; neither was fabricated into an inventory row).
>
> **Independent judgement: nothing blocks completion.** Both acceptance conditions HOLD under
> measurements I derived myself, including under a stricter reading of condition 1 than the gate
> applies. The deliverables are append-only, scope-clean, verdict-free, and — on a 36-identifier
> sample spanning every dispatch — not fabricated. The two record errors are **reporting
> inaccuracies, not defects in the work**, and neither touches an acceptance condition.

Both errors the review found were real and are corrected above: the branch-diff bullet now states
twelve files and names the nine that were a peer's, and the fix-cycle bullet now reads nine — eight
coordinator-issued plus `X3`'s own — with the reason the miscount survived. `backlog.yaml`'s
`result` field carries the same correction. The unresolvable ACM DOI is recorded in `## Unresolved`
with its provenance; it was not fabricated and no fix cycle was dispatched for it.

## Decisions

**The gate's own measurement was sent back rather than reinterpreted.** `LIT-02 G` reported every
gate as PASS on its first run, which is the outcome a coordinator wants and therefore the outcome
least likely to be checked. Its Measurement 2 said 41 inventory rows with **zero kept** for a phase
that had inventoried 358 candidates. Accepting a PASS carrying that number would have put a false
figure into the permanent record of a phase that passed anyway. The dispatch had warned the gate
that a measurement condemning substantially all of its input is suspect before it is reported; the
same standard had to apply when the verdict was favourable.

**The SICI DOI was not normalised, and the gate was taught instead.** A `;`-separated column cannot
hold a `;`-bearing DOI, and the cheap fix — rewrite the DOI — would have put a broken identifier in
the reproducibility record to make a parser happy. The data was left correct and the gate was told
how to split. `phase-lit-01` set this precedent from the opposite direction: there the owner ruled
to normalise 32 inconsistent cells *because* they were inconsistent, while deliberately leaving four
`semanticscholar.org` URLs alone because they already matched the inventory. The rule both cases
express is that the ledger and inventory must agree with each other, not with an abstract ideal.

**A cross-phase scoring disagreement was preserved rather than resolved.** `LIT-02 X1` scored a
source `collision_candidate: yes` at D22 that `phase-lit-01` had scored `no` at D30, with identical
pre-scores. When the dedup convention was later settled — the flag belongs to the canonical row —
four rows were corrected and this one deliberately was not, because flipping it would have resolved
a genuine disagreement in favour of whichever phase ran first. It is now the only excluded row in
826 carrying `yes`, which makes it findable by whoever adjudicates it.

**Ideas were re-appended through the writer twice rather than the log being hand-edited.** Both
idea-id collisions were resolved by dropping commits during a rebase and re-appending, per the
procedure `1a4dd1b` established, even though hand-editing two lines would have been faster. The
append-only log's value is that nothing in it was ever edited in place; one exception would end that
property permanently.

**The owner directed integration at this phase boundary**, as at `phase-lit-01`'s, rather than
waiting for the pre-synthesis check-in `PLAN-023` schedules. The branch and worktree were kept alive
because the campaign's branch model requires it.

## Corrections

**Four relayed claims were wrong while the underlying evidence was sound, and the pattern is
one-directional.** A DOI/dissertation conflation went from `S4`'s report into `X4`'s dispatch; a
non-existent Antoniol row in D34 went from `S5`'s report into `X5`'s dispatch; a mandated-variant
count of 76 against a true 91 went into `G`'s dispatch; and an early catalog regeneration was
misread as clean because `--catalog` prints rather than writes and the output had been sent to
`/dev/null`. Worker *outputs* were verified against the files every time; worker *narrative* was
relayed forward without the same check. Three were caught by the next worker reading files instead
of prose, and the fourth by instructing the gate to derive the number from `PROMPT-029` rather than
trust the dispatch — the only one caught prospectively. Block C already imposes this discipline on
workers about their own sources: a summary is a lead, never evidence. It applies to the coordinator
reading worker reports.

**The session record itself carried two errors, both caught by the independent review rather than by
this session.** The branch-diff bullet claimed three files where the range carried twelve, and the
fix-cycle bullet said seven while listing eight and omitting a ninth. Both are corrected in place.
The second is the more interesting: it understated this session's own defect rate, and it survived
because only seven commits carry the words "fix cycle" — `K`'s was folded into an amended commit and
`G` writes no file at all. A count taken from commit subjects rather than from what actually
happened will always miss the work that left no artifact.

**A rebase-state check was written wrongly and reported the opposite of the truth.** A loop testing
`[ -d .git/rebase-merge ]` found nothing and printed "rebase complete" while the rebase was still in
progress with conflicts pending — in a worktree, `.git` is a file and the state lives under
`.git/worktrees/<name>/`. The same shape as the `--catalog` error: a check written quickly,
producing a clean-looking answer, measuring the wrong thing.

## Left undone

**Everything after Pass 1b.** Five phases remain. `phase-lit-03` sweeps D46–D72 — 27 domains, the
largest in the campaign — and closes Pass 1 by finalising the terminology map, writing
`02_domain_map.md` with all 72 domains, and producing the top-20 collision list. Its `search_id`s
start at `LIT-03-S001`; numbering is per-phase, not continuous.

**No collision has been adjudicated, and none should have been.** Pass 1 pre-scores are triage. 115
in-scope rows carry `collision_candidate: yes`, and the strongest — Aporia's decision-elicitation to
executable-test traceability at 5/4, ProvTracer's knowledge-graph-plus-LLM-plus-PROV-O dissertation
at 5/4, Jansen & Bosch's architecture-as-decisions reframing at 5/4, the de Boer vaporization
dissertation at 5/4 — are recorded, not resolved. Whether any shares D-System's actual mechanism is
`phase-lit-04`'s deep reading to decide with the full evidence matrix.

**The evidence in this phase is the least flattering to D-System's novelty the campaign has
produced, and that is the campaign working.** A standards body owns "architecture rationale"
(ISO/IEC/IEEE 42010). The failure mode D-System's provenance design targets was named "architectural
knowledge vaporization" in 2009. IBIS dates to Kunz & Rittel in 1970. DMN is a decade-old
multi-vendor standard for decision representation. None of this is adjudicated, but an honest sweep
of the rationale-capture traditions found what H0 predicts, and the interesting question is shifting
from whether any component is novel to whether the combination is — which is what `phase-lit-07`
exists to answer.

**Saturation is not yet demonstrable, but the first real signal appeared.** Two independent collision
queries, in different domains and different dispatches (`S3`'s D36/`S152` and `S5`'s D45/`S288`),
converged on the same paper. That is what saturation evidence looks like, and it was recorded as
recurrence rather than dropped. One convergence is not a campaign; `phase-lit-07`'s final gate
measures it across the whole corpus.

**Two instrument gaps are `phase-lit-03`'s to trip over if nobody acts first.** `LIT-03 C` builds the
top-20 list as "the inventory's `collision_candidate: yes` rows ranked" with no filter on `status`
(idea `000199`), and the `;`-separated `kept` column still cannot hold a SICI DOI (idea `000200`).
Neither blocks this phase; both are live for the next.
