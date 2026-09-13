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

The phase's three `verification` entries, run after the rebase onto `dev` at `920f1d3`.

```text
$ uv run python -m src.governance
Governance OK: 20 systems, 190 documents, 21 memories, 137 backlog phases
(exit 0)

$ uv run python tools/check_no_private_content.py
note: _private/portfolio/ not found — content check skipped (path check still ran; this is
expected in CI / a fresh clone)
check_no_private_content: OK (540 tracked files, 0 identifiers checked)
(exit 0)

$ uv run python -m pytest -q
578 passed, 2 warnings
(exit 0)
```

**The private-content check verified nothing, and its `OK` must not be read as a pass.** `_private/`
is gitignored and therefore absent from every worktree, so the tool built an empty identifier list
and reported success for having compared zero identifiers against 540 files. The verification entry
says "with the changes staged"; the tree is clean, so there was nothing to stage, and the pre-commit
hook ran the same vacuous check at each commit. This is idea `000150`, on which the owner ruled on
2026-09-12 to accept the gap and rely on the integration-time check in the primary checkout, which
does have the identifier list.

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

`phase-lit-02` remains `status: active`, `agent: agent-lit`, with `session`,
`completion_evidence` and `result` recorded incrementally as this checkpoint's observed state. It is
not in `next_up` and was not added to it.

`next_action`: All twelve work items are complete and every gate passes. The phase is ready for the
owner's `/session-close`, which is the only thing that may mark it `complete`, and for the owner's
decision on whether to integrate `agent/lit-campaign` into `dev` at this boundary as they did at
`phase-lit-01`'s. Nothing is outstanding within the phase itself.

## Unresolved

- **Not marked complete, and not integrated.** Both are the owner's. The branch is 47 commits ahead
  of `dev` at `f400737`, 0 behind, tree clean, governance exit 0, 578 tests passing. The diff is
  three files: `git diff dev..agent/lit-campaign` shows 294 ledger rows, 388 inventory rows and 401
  terminology-map lines added, and nothing else.
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
- **Seven fix cycles were issued and all seven closed.** `K` left the catalog stale after the claim,
  putting `dev` red; `S1` twice, for a false "reconsidered there" claim in `LIT-02-S002` that never
  happened and for an author/implementation search it ran but did not log; `X1` twice, for the
  inventory row the first fix created and for four dedup rows double-counting in the top-20; `X2`
  for two PMC years left `n.d.` that a lookup settled; `X4` for a truncated identifier failing a
  byte-exact gate match; and `G` for Measurement 2's population. None was cosmetic.
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
