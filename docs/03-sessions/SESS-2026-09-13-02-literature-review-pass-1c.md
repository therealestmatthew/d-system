---
schema_version: 1
id: doc-session-literature-review-pass-1c
code: SESS-2026-09-13-02
title: Literature review Pass 1c — third execution session of the adversarial campaign; Pass 1 closed
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

# Literature review Pass 1c — third execution session of the adversarial campaign; Pass 1 closed

## Phase

`phase-lit-03` — Literature review Pass 1c, the broad map of digital-thread, specification and
agentic-SE domains (D46–D72, 27 domains — the campaign's largest phase), closing Pass 1 with the
finalized terminology map, the 72-domain map and the ranked top-20 collision-candidate list.
Claimed by `agent-lit`, the third execution session of the campaign
([PLAN-023](../01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md)).

Work ran on the long-lived campaign branch `agent/lit-campaign` in the worktree
`../d-system-worktrees/lit-campaign`. All seventeen delegation-pack sections for this phase were
dispatched verbatim from [PROMPT-029](../02-prompts/PROMPT-029-literature-review-delegation-pack.md),
one at a time, in pack order: `K` → `S1/X1` … `S7/X7` → close-out `C` → `G`. Models as the pack
fixes them: `K` and `G` on Haiku, every `S`, `X` and `C` on Sonnet. **No Opus escalation was
spent** and **no descope rung was taken.** Per owner direction for this session, every dispatch
forbade `EnterWorktree` by name (idea `000196`), required abandon-and-report on any tool call not
returning in ~60 seconds, and required a commit per domain so a truncated run resumes rather than
re-runs; no dispatch hung and no run needed resuming.

## Verification

The phase's three `verification` entries, run in the worktree at checkpoint.

```text
$ uv run python -m src.governance
Governance OK: 20 systems, 191 documents, 22 memories, 137 backlog phases
(exit 0)

$ uv run python tools/check_no_private_content.py        # in the worktree, tree clean
note: _private/portfolio/ not found — content check skipped (path check still ran; this is
expected in CI / a fresh clone)
check_no_private_content: OK (546 tracked files, 0 identifiers checked)
(exit 0)
```

**The worktree private-content run verified nothing** — `_private/` is gitignored and absent
here, so the identifier list was empty (idea `000150`, owner-accepted gap). The real check
happens in the primary checkout at integration time.

### The phase gate — delegation-pack section `LIT-03 G`, real output

`G` ran twice. Its first run reported Gates 1a/1b/2/3/4/5 PASS and **Gate 1c (mandated-variant
coverage) FAIL with 5 uncovered variants** (D03: `prov:Agent`, `prov:Entity`; D12: `argument
support`; D34: `forward traceability`, `pre-RS traceability`). The coordinator verified all five
against the pack text and the ledger before acting: every one is a fragment of a compound
slash-token the pack lists as a single comma-separated item, and every compound is covered
verbatim in the ledger (`prov:activity/agent/entity` at `LIT-01-S001`, `argument attack/support`
at `LIT-01-S266`, `forward/backward traceability` and `pre/post-rs traceability` in D34 rows).
The FAIL was an artifact of the gate's own derivation method — the same class as `LIT-01 G`'s
slug-column artifact — and went back as a fix cycle. Second run, corrected derivation
(comma-separated item = one variant, slashes preserved):

```text
Gate 1a  PASS — all 72 domains ≥2 ledger rows (narrowest: D11 and D48 at 6 rows)
Gate 1b  PASS — all 72 domains ≥2 distinct queries
Gate 1c  PASS — 339 mandated variants derived from PROMPT-029 (LIT-01: 132, LIT-02: 91,
                LIT-03: 116); 339 covered, 0 uncovered.
                LIT-02 subtotal reproduces the 91 that phase's gate and independent review
                both derived — the anchor check the fix cycle required.
Gate 2   PASS — 1,038 status: candidate inventory rows across all domains (floor: 75)
Gate 3   PASS — 01_terminology_map.md and 02_domain_map.md exist; domain map has all 72
                entries and a ranked top-20 list
Gate 4   PASS — inventory: 1,091 rows (1,038 candidate, 53 excluded), 0 excluded rows
                missing an exclusion_reason
Gate 5   PASS — 0 of 572 kept-bearing ledger rows name a source absent from the inventory
                (resolved against url_or_doi, SICI-aware split)
H-id rows: 8 (H4), reported separately, excluded from the 72-domain gates
governance exit 0; check_no_private_content exit 0 (0 identifiers checked, see above)
```

### Coordinator measurements, taken independently of the gate

Every worker claim below was verified against the files before being relayed or acted on; the
gate's corrected figures reproduce the coordinator's own counts.

```text
ledger:    845 lines total (header + 844 rows), 845/845 CRLF, 0 bare LF, all rows 15 fields
           283 rows this phase, LIT-03-S001..S283, contiguous
inventory: 1,092 lines (header + 1,091 rows), 0 CR (pure LF), all rows 13 fields,
           0 duplicate source_ids
           265 rows naming D46–D72 (253 candidate, 12 excluded), 92 collision_candidate: yes
           in scope; 366 yes across the whole inventory, 365 of them status: candidate
maps:      01_terminology_map.md 1,305 lines (LF) — all 72 domain sections plus the §6 index
           02_domain_map.md 1,026 lines (LF, new) — 72 entries plus the ranked top-20
kept:      all 260 distinct kept identifiers from LIT-03 rows resolve byte-exactly to
           inventory url_or_doi values
```

## Acceptance

- **"Every one of the 72 matrix domains has at least two ledger rows with distinct terminology
  variants, measured from the ledger's domain-id column, and the candidate inventory holds at
  least 75 sources across all domains."** — **Met.** Gate 1a/1b: all 72 domains clear the
  two-distinct-query floor (narrowest at 6 rows). Gate 1c: 339 of 339 mandated variants covered,
  re-derived from `PROMPT-029` itself after the first run's derivation artifact. Gate 2: 1,038
  candidate rows against the 75 floor.
- **"01_terminology_map.md and 02_domain_map.md are complete for all 72 domains and the top-20
  collision candidate list exists with component/architecture pre-scores."** — **Met.** Both
  files exist; the domain map carries all 72 entries (verified by the coordinator and the gate
  independently) and a ranked top-20 with pre-scores and one-line reasons, its ranking rule and
  status-filter decision recorded in its own preamble.

Both conditions were recomputed at checkpoint against the repository as it stands.

## Backlog

`phase-lit-03` remains `status: active`, `agent: agent-lit` — checkpoint never completes a
phase; that is the owner's `/session-close` after its independent review. `session`,
`completion_evidence` and `result` are recorded incrementally on the active phase. The phase was
never in `next_up`; nothing to prune.

`next_action`: All acceptance conditions measured met; awaiting the owner's `/session-close`
review. `phase-lit-04` (Pass 2a, deep reading the top collision candidates) is next in the
campaign and continues on the same branch.

## Unresolved

- **The section/contract conflict on `deep_read` marking, reported by `LIT-03 C` and left for
  the owner.** The evidence contract's only deep-read mechanism is `status: deep_read` — exactly
  the field the pack section forbids changing at this stage ("status stays `candidate` until
  LIT-04 actually reads them"), and the 13-column schema has no other field. Per the
  no-improvisation rule nothing was invented: the inventory is untouched, the domain map's
  ranked top-20 list is the de-facto deep-read designation, and the conflict is recorded in that
  file's preamble. `LIT-04 K` needs a ruling on how deep-read candidacy is marked.
- **The top-20 ranking's status-filter gap (idea `000199`) was decided and recorded, not
  silently absorbed.** `LIT-03 C` ranked only `status: candidate` rows, excluding the one
  deliberate `excluded`+`yes` row (`structured-belief-state-llm-memory-benchmark-2026-d22-recur`,
  the preserved D22/D30 cross-phase scoring dispute) on the stated ground that promoting an
  excluded row to deep-read would pre-empt the Pass 2 adjudication it exists to receive. The
  dispute itself still stands for `phase-lit-04`.
- **Two ties in the top-20 are disclosed rather than hidden.** A 13-way tie at pre-score sum 9
  (ranks 1–13) and an 8-way tie at sum 8, cut to 20 alphabetically with the cut row named
  (`zep-graphiti-temporal-kg-agent-memory-2025`). `phase-lit-04`'s batching should treat the
  rank boundary as soft.
- **The pack's variant-token grammar is ambiguous, and both misreadings have now occurred.**
  Pass 1b's coordinator relayed 76 variants against a true 91 (under-derivation); this phase's
  gate first derived 346 by splitting slash compounds (over-derivation). The comma-item rule the
  fix cycle applied reproduces the independently reviewed 91 anchor and should be written into
  the instrument rather than rediscovered per phase. Recorded as an idea (see below).
- **OpenAlex served mistitled/mis-DOI'd records at least three times this session** (SWE-bench
  retitled "Persistent memory for AI coding agents...", a GPT-4-report record at `LIT-03-S142`,
  and relevance-search misses on known-correct targets). Every keep survived because workers
  verified identity at the source; Pass 2's deep reads inherit this trap. Recorded as an idea
  (see below).
- **A phase-wide provider outage continued from Pass 1b.** `export.arxiv.org` failed on
  effectively every direct attempt across the phase (HTTP 429, curl timeouts, one 503, one
  redirect-timeout — a new signature); `api.semanticscholar.org` was 429 throughout except two
  200s, one of which served paper-mill noise that was excluded with rationale. Every attempt is
  a logged zero-yield row. Coverage rests on web search, OpenAlex and Crossref, with the same
  caveat Pass 1b recorded.
- **Ideas are appended only after the final rebase onto `dev`** (owner direction for this
  session, after the id race fired twice in Pass 1b). At checkpoint time the appends have not
  yet happened; the session's close-out appends them and cites the ids in the final report.

## Fix cycles and worker-issued repairs

Three coordinator-issued fix cycles, all closed on the first cycle; no work item reached its
two-cycle limit:

1. **`S3` fix cycle 1** — ledger row `LIT-03-S094` kept two arXiv identifiers in the
   non-canonical `10.48550/arxiv.*` DOI form; canonicalized to `arxiv:NNNN.NNNNN` to restore the
   byte-exact ledger↔inventory match (commit `6ae10f6`).
2. **`S4` fix cycle 1** — two defects in one cycle: `LIT-03-S121` kept two identifier forms for
   one source (the AGENTS.md standard; reduced to the inventory's canonical `agents.md`), and
   `LIT-03-S104`'s exclusion rationale deferred a keep decision to the extraction dispatch. The
   reconsideration was actually made — all four ids excluded on abstract review, logged as
   verification rows `LIT-03-S155`–`S158` — and the rationale rewritten to record a decision
   rather than a deferral (commit `2ee335d`).
3. **`G` fix cycle 1** — the gate's first run split compound variant tokens and reported a false
   FAIL (5 phantom uncovered variants); the corrected derivation passes with 339/339 covered and
   reproduces Pass 1b's independently reviewed 91-variant anchor.

Worker-issued repairs, both verified by the coordinator after the fact:

- **`X6` closed a kept-field omission** — `LIT-03-S215` narrated Fickas & Feather 1995 as the
  domain's foundational keep but its `kept` field read `none`; X6 closed the record with a fresh
  verification lookup (`LIT-03-S235`) and built the inventory row's provenance from that row
  rather than fabricating it for the earlier one.
- **`S7` self-caught two append defects before committing** — a partially written short row and
  a duplicated pair from a failed script run, both repaired at byte level and reverified
  (duplicate-id scan, CRLF count, 15-field parse) before the domain commit. `X6` and the `S4`
  fix worker each also self-caught a CSV-quoting mistake (nested double quotes; extra field) via
  the same post-append parse check before committing.

## Corrections

- **The relay discipline Pass 1b demanded held: no worker claim was relayed or acted on without
  a file check, and the checks caught real report errors.** X4's report described `LIT-03-S104`'s
  note inaccurately (the row's rationale, read directly, carried a genuine deferred decision);
  S6's narrative placed a retried search in the wrong id range; X6's D64 commit message
  miscounted its own candidate rows ("3 candidate" for 7 — flagged by the worker itself, left
  unamended by policy); X7's narrative used the phrase "clears the CRITICAL_COLLISION threshold",
  which the 13-column inventory cannot and does not record — the file carries only
  `collision_candidate: yes` with pre-scores, verified. None of these reached the record or a
  later dispatch.
- **The gate was sent back rather than reinterpreted, and the direction of the error was
  unfavourable this time.** Pass 1b's gate error produced a false-clean number inside a PASS;
  this phase's produced a false FAIL. The response was the same both times: verify the
  measurement against the files, then fix the instrument, not the data.

## Spend posture

- **Searches:** 283 ledger rows this phase (`LIT-03-S001`–`S283`; 844 across the campaign),
  including 15 logged bibliographic-verification lookups and 45 zero-yield rows with their
  queries. No source was deep-read; Pass 1 is triage by design.
- **Dispatches:** 17 pack sections + 3 fix cycles = 20 dispatches, all on the pack's fixed
  models. **No Opus escalation** (0 of 1 spent campaign-wide). **No descope rung.**
- **Sessions:** 3 of the 7-session runway used (range six to eight). Pass 1 — the three-phase
  broad map — is complete on schedule.

## Left undone

**Everything after Pass 1.** `phase-lit-04` (Pass 2a) deep-reads the top collision candidates
into the evidence matrix; it needs the deep-read-marking ruling above. No collision has been
adjudicated, and none should have been: the top-20 pre-scores are triage. The strongest new
Pass 1c signals for Pass 2, recorded not resolved: the IBM MAPE-K architectural blueprint
(4/4, the only new 4/4 alongside the AI digital-thread patent family and LangGraph's checkpoint
library), the FORMS reference model, VeriSpecGen's requirement-level traceable synthesis, the
AGENTS.md open standard as a direct convention collision, and the D72 sweep's three-way
PROV-O/SLSA/in-toto provenance cluster converging with Pass 1a material — the campaign's
clearest saturation evidence yet, with cross-domain recurrences (Calinescu ×3, Gotel &
Finkelstein, PROV-O ×3 across phases) logged in `duplicate_handling` for the final gate's
saturation measurement.
