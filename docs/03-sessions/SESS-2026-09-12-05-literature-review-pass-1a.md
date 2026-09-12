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
`../d-system-worktrees/lit-campaign`. A worktree is required because a peer holds an active
claim (`phase-demo-07`, `agent-demo-glossary`); `PLAN-023` fixes the branch but is silent on
worktrees, so there is no conflict with its branch model.

## Verification

Run at checkpoint, in the primary checkout on `dev`:

```text
$ uv run python -m src.governance
Governance OK: 19 systems, 184 documents, 20 memories, 129 backlog phases
(exit 0)

$ uv run python tools/check_no_private_content.py    # changes staged
check_no_private_content: OK (524 tracked files, 31 identifiers checked)
```

The document count reads 184 here and 183 in the worktree below: this record is itself a
governed document, and it exists on `dev` but not on the campaign branch. Both figures are
correct for the tree that produced them.

Run in the campaign worktree, where the deliverables live:

```text
$ uv run python -m src.governance
Governance OK: 19 systems, 183 documents, 20 memories, 129 backlog phases
(exit 0)

$ uv run python tools/check_no_private_content.py
note: _private/portfolio/ not found — content check skipped (path check still ran; this is
expected in CI / a fresh clone)
check_no_private_content: OK (526 tracked files, 0 identifiers checked)
(exit 0)
```

**The third verification entry — delegation-pack section `LIT-01 G` — has not run.** It is the
phase gate and cannot run until every `S`/`X` pair is complete; `S3` is in flight and `X3`,
`S4/X4`, `S5/X5`, `S6/X6` are queued. Recording it as not yet run rather than as a pass.

Coordinator measurements taken directly from the deliverables, independently of any worker's
report, covering the eight domains swept so far:

```text
ledger rows: 98 | range LIT-01-S001..LIT-01-S098 | unique 98
sequence contiguous, no gaps: True

domain | rows | distinct q | gate(>=2 rows, >=2 distinct)
D01    |   12 |         11 | PASS        D06    |   11 |         11 | PASS
D02    |   11 |         11 | PASS        D30    |    9 |          9 | PASS
D03    |    9 |          9 | PASS        D31    |   11 |         11 | PASS
D04    |   10 |         10 | PASS
D05    |    9 |          9 | PASS

mandated variant coverage: D01 6/6, D02 6/6, D03 8/8, D04 5/5, D05 5/5, D06 6/6,
                           D30 5/5, D31 5/5
pre-crafted collision queries: 9 of 9 logged verbatim

inventory rows: 139 | status {'candidate': 131, 'excluded': 8}
collision_candidate: {'yes': 32, 'no': 107}
GATE 1 excluded rows missing exclusion_reason (must be 0): 0
GATE 2 strict (literal match)            kept-but-uninventoried: 26
GATE 2 normalized (doi:/arxiv: stripped) kept-but-uninventoried: 0
```

## Acceptance

- **"The ledger and source inventory exist at the evidence contract's paths and every matrix
  domain D01-D06, D07-D20, D28-D32 has at least two ledger rows with distinct terminology
  variants."** — **Not met.** Both files exist at the contract's paths and every domain swept
  so far clears the floor, but only 8 of the 25 domains in scope have been swept (D01–D06,
  D30–D31). D07–D11 are in flight; D12–D20, D28–D29 and D32 are queued.
- **"Candidate sources for these domains are in the inventory with inclusion or exclusion
  rationale; no evidence row cites a generated summary as evidence."** — **Not met**, for the
  same reason: true of the 139 rows written so far (all 8 excluded rows carry a reason, and
  every kept identifier resolves to an inventory row), but the remaining 17 domains have no
  inventory rows yet.

## Backlog

`phase-lit-01` stays `status: active`, `agent: agent-lit`. No `completion_evidence` or
`result` is claimed: the phase gate has not run, so there is no measured outcome to record.
`next_up` is unchanged — the phase is not complete and was not pruned.

`next_action`: Resume `phase-lit-01` mid-phase. Sections `K`, `S1`, `X1`, `S2`, `X2` are
complete and verified; `S3` (D07–D11) is in flight. Dispatch the remainder of the delegation
pack's LIT-01 section in order — `X3`, `S4/X4`, `S5/X5`, `S6/X6`, then `G` — from
`PROMPT-029`, assembled per its dispatch rules, on the campaign branch `agent/lit-campaign`.

## Unresolved

- **The phase gate has not run**, so the phase's own acceptance is unmeasured. 17 of 25
  domains remain.
- **The private-content check cannot see the campaign's content.** `_private/` is gitignored
  and therefore absent from every worktree, so `check_no_private_content.py` runs there with
  **0 identifiers checked** — the path check runs, the content check silently skips. The tool
  resolves its root from its own location and takes no path argument, so it cannot be pointed
  at the campaign branch from the primary checkout. Every campaign deliverable is committed on
  `agent/lit-campaign`, which means no campaign content has been checked against the 31 real
  identifiers, and none will be until the branch reaches a checkout that has `_private/` — the
  owner's integration, which `PLAN-023` schedules only twice. `AGENTS.md` warns that this gate
  "passes by not looking"; this is a second way for that to happen, and it was not anticipated
  when the branch model was chosen.
- **The ledger's `kept` column has no fixed identifier format**, and two dispatches used two
  conventions: 26 rows carry a `doi:` prefix that the inventory's `url_or_doi` does not. A
  literal string match for the phase gate's third measurement reports 26 kept-but-uninventoried
  sources; resolving the identifier reports 0, and 0 is the true figure. The evidence contract
  ([PLAN-023.03](../01-plans/PLAN-023-literature-review-campaign/PLAN-023.03-evidence-contract.md))
  specifies the column's meaning but not its format. Left as a finding rather than repaired,
  because normalising it means rewriting committed evidence rows to a convention the contract
  does not state.
- **The evidence contract's `source_type` enum has no bucket for a patent.** `uspto:11544323`
  was filed under `tech report`. Its `strategy_phase` enum likewise has no value for
  bibliographic verification of an already-kept source; 13 such lookups were logged under `D`
  (system search) as the closest fit.
- **Two of the three fix cycles spent this session were evidence-hygiene failures, not
  research failures** — a stale catalog and thirteen unlogged searches. In both cases the
  substantive work was correct and the record of it was skipped. `GOV-009`'s gates measure the
  record, so a campaign that searches well and logs badly fails its own completion gate.
- **One source identity is unconfirmed.** The HDP-P working paper appears under a Zenodo DOI
  (`10.5281/zenodo.19332440`) and an SSRN DOI (`10.2139/ssrn.6494358`). Recorded as open in the
  ledger rather than asserted; it becomes a dedup decision when the evidence matrix is built.
- **Provider access is uneven.** `api.semanticscholar.org` returned HTTP 429 throughout;
  `export.arxiv.org` was intermittent (429 in the first dispatch, 200 in the second). OpenAlex
  and Crossref worked directly throughout. Rate-limited attempts are logged as real zero-yield
  ledger rows, and the affected coverage was obtained through domain-scoped web search instead.
