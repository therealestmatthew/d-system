---
schema_version: 1
id: doc-session-plugin-absolutes-part-two
code: SESS-2026-09-27-01
title: The plugin's governance documents as absolutes, part two
kind: session
status: active
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-27'
systems: [sys-plugin-absolutes]
depends_on: [doc-idea-realization-plugin-absolute-documents-two]
---

# The plugin's governance documents as absolutes, part two

## Phase

`phase-plug-09` — Governance documents as absolutes, part two: methodology, role contracts and
review, multi-session coordination.

## Verification

Run in the worktree on `agent/phase-plug-09` at `b480618`, rebased on `dev` at `30b443c`, which
includes the merged partition sweep.

```
$ cd plugins/idea-realization && uv run pytest
496 passed

$ claude plugin validate plugins/idea-realization --strict
✔ Validation passed

$ uv run python tools/check_no_private_content.py
check_no_private_content: OK (1050 tracked files, 0 identifiers checked)

$ uv run python -m src.governance
Governance OK: 43 systems, 387 documents, 33 memories, 323 backlog phases
```

The worktree has no `_private/portfolio/`, so the content half of the private-content check did
not run there. The branch diff's added lines were scanned separately against the 34 project
identifiers in the primary checkout's portfolio, without printing them: 0 hits.

The R02 scan (`test_no_source_references.scan`) on a fixture naming a prompt code:
`["x.md:1: document code: 'PROMPT-0'"]`, so a document naming a source-repository prompt code
fails.

The post-rebase gate the Session Manager requires, in the worktree: `uv run pytest` 1115 passed,
1 warning; `uv run ruff check src/ test/` All checks passed; `uv run mypy src/` no issues found in
46 source files; `git diff --exit-code docs/08-governance/catalog.md` clean.

## Acceptance

- The R02 check and `test_no_history.py` pass over the plugin's `docs/` with the nine new documents
  present, and a document naming a source-repository prompt code fails the R02 check: **Met**. Both
  tests are in the 496 passing; the prompt-code fixture fails, as shown above. `partition-pack.md`,
  merged from the partition-sweep phase, passes too.
- Every rule in the trace table's source column is present in the named plugin document, checked
  by a reviewer reading both: **Met**. Four independent reviews, below, covered D1-D132, E1-E76,
  every plan-quality judgement against `GOV-010` itself, the Partition contract, and F1-F52. Their
  findings are fixed.
- The ledger's still-standing rules that amend the role contracts or the review procedure each
  appear in exactly one of the nine documents: **Met**. Reviews confirmed C14 in prompt-packs.md
  only, C16 in plan-review.md, C20-C23 in coordinator.md, C27 in role-contracts.md, and C29.1-C29.4,
  C30 and C31 in multi-session.md. The template restates them as its pasteable form, which the
  review judged legitimate.

## Backlog

`status: active`, `agent: agent-builder-a`. `next_action`: every acceptance condition is met and
the independent reviews are recorded here; the phase waits for the owner-approved merge, then the
completion edit on the integration branch.

## Unresolved

None.

## Review

Four independent `demo-adversary` reviews ran on `dev...HEAD`, one per family plus a follow-up.
The type follows the owner's choice for the plugin phases.

**Family D** (prompt-packs, research-packs, coordinator, batches; D1-D132 against `GOV-008`,
`GOV-009`, `GOV-013`, `GOV-016` in full):
- Major: the trace table's family D conflict item 13 still said the model names "are kept",
  against the owner's tier ruling that the documents follow. Fixed: item 13 now records the ruling.
- Minor: conflict item 6 described `protocol.md` §11's missing completion edit as an open gap,
  but this phase closes it. Fixed: it points to the fix.
- Otherwise: every D rule present and faithful; C14 and C20-C23 each in one document; no batch
  schema, directory or check claimed; no history or instances.

**Family E** (role-contracts, plan-review, adversary-prompt; stopped at its turn limit and
delivered on request):
- "No blocker or major findings survived the attack." One non-finding: an article change ("the"
  for "a" decision record) alongside a disclosed placeholder substitution.
- E1-E76, C16 and C27 checked; `adversary-prompt.md` diffed against `PROMPT-038` lines 46-138, with
  no undisclosed drift.
- Not reached: the plan-quality judgements against `GOV-010` itself, and the Partition contract
  against its mechanism. Covered by the follow-up below.

**Follow-up** (plan-review.md §1-2 against `GOV-010`; the Partition contract against the
partition sweep):
- Major: plan-review.md sent readers to `protocol.md` §4 for accepted headings, which only
  `plan_check.py` lists. Fixed: it cites `scripts/plan_check.py` (`REQUIRED`).
- Major: plan-review.md dropped `GOV-010`'s staleness exclusion. Fixed: stated in §2's preamble.
- Blocker: the Partition contract said the sweep proposes a new-plan-or-amendment ruling per
  track, but the plugin's record leaves `disposition` null until the owner rules. Fixed: the
  contract says the ruling is the owner's, and the trace records the clause as not shipped.
- Major: the Partition contract promised a revision cycle after an adversary blocker, but the
  sweep has none. Fixed: the contract says the role never proceeds past a gate without the
  owner's answer, and the trace records the clause as not shipped.
- Otherwise: every P, Q and T judgement, the length rules and the optional sections restate
  `GOV-010` faithfully.

**Family F** (multi-session, session-manager-messages and the amendments; F1-F52, C29.1-C29.4,
C30, C31; plugin suite 496 passed and validation passed in its run):
- Blocker: a phase handed back after a red worktree preflight had no turn purpose, although §3
  calls its list complete. Fixed: the `claim` purpose covers a release. The contract line, the
  Builder template and the `session-start` clause say so.
- Major: the Standby Builder was pointed at `plan-review.md` §4, which grants edits but gives no
  review method. Fixed: it reviews against §3's phase-altitude checks and reports findings
  without dispositions; §4 bounds any backlog edit.
- Minor: the Ideation template dropped the source's out-of-turn scouting without recording it.
  Fixed: recorded in the trace, with the reason (the plugin's triage agent writes its finding in
  the same dispatch).
- Minor: the `backlog` skill's multi-session clause said nothing about a standalone run. Fixed: it
  skips the tests and says so.
- Re-check of the fixes: all four resolved. One residual ambiguity, whether the Standby Builder
  writes dispositions, is fixed by the follow-up commit.

**Disposition:** every finding is fixed; none is left open or merely accepted.

## Decisions

- Four analyst dispatches ran in parallel. The plan quality standard (`GOV-010`), which no family
  covered, became a separate dispatch within family E after the owner ruled its judgements belong
  in `plan-review.md`. Part one's trace table supplied the ledger classification; family C was not
  re-run.
- The owner ruled on six more points in this session:
  - The token ceiling is not shipped.
  - The plan-review record lives in the reviewing session's record.
  - Models are named by tier.
  - "No tests in the primary checkout" is scoped to multi-session operation, with the `backlog`
    and `session-start` skills amended.
  - A relayed `GRANTED merge` is the owner's approval, with `session-start` and `session-close`
    amended.
  - Under multi-session, Ideation triages only ideas the owner names.
  The amendments reached files outside the nine documents through a second widen: the three
  skills and part one's `protocol.md`, `backlog-protocol.md` and `reporting.md`. The same widen
  fixed `protocol.md` §11, which had omitted the completion edit from the primary-checkout work.
- The Partition contract ships because the partition sweep merged before this branch rebased. It
  states only what the sweep does; the two clauses without a mechanism are recorded as not
  shipped.
- The `batch` turn purpose and batch-table status lines (C29.5) are not shipped, because the
  plugin's batches have no status fields.
- The trace table took its own code, PLAN-048.11, and the file is named to match, as in part one.
  Its covering `sources` entry was committed on the branch in the same commit as the file.

## Corrections

- A commit of the skill amendments was refused by the pre-commit hook, because the untracked trace
  file in the tree failed governance. Nothing was committed and the hook was not bypassed. The
  trace file was moved out of the tree, the amendments committed, and the trace then committed
  with its covering source.
- The trace table carried two stale conflict notes from the analyst reports: the model-name item
  and the `protocol.md` §11 gap. The family D review caught them and both were corrected.

## Left undone

- The completion edit waits for the owner-approved merge.
