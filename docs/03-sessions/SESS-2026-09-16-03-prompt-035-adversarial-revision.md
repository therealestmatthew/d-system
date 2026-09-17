---
schema_version: 1
id: doc-session-prompt-035-adversarial-revision
code: SESS-2026-09-16-03
title: PROMPT-035 adversarial review and revision
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-backlog, sys-governance]
depends_on: [doc-prompt-queued-phase-review-pack]
---

# PROMPT-035 adversarial review and revision

Owner-directed session with no backlog phase — **unclaimed**, branch `agent/prompt-035-rev`,
worktree `../d-system-worktrees/prompt-035-rev`. Continues `SESS-2026-09-16-02`.

## What the session did

1. **Ran the owner-requested Opus adversarial review** of `PROMPT-035`: 4 blockers, 11
   majors, 7 minors, all accepted. The blockers: every path was relative across two checkouts
   that both contain them (an enhancement agent could edit `backlog.yaml` on `dev`); pass 2
   granted itself a ~23-phase edit right `AGENTS.md` withholds; the scope derivation mixed
   `--ready` (which hides `waiting` phases — half the mission) with `next_up`; and positional
   scope ("position 5") breaks the moment a peer completes a front-of-queue phase. Majors
   included a self-contradictory grouping rule, two wrong and four missing reading
   assignments, a ~10x-oversized `phase-irs` dispatch, absent house conventions (idempotency
   sentence, truncation-resume, agent charter, `GOV-008` model policy), incoherent
   parallelism, evidence destroyed by worktree removal, no out-of-scope-defect rule, missing
   catalog/`updated`/pytest gates, a `GOV-006`-violating question format, and an
   `AskUserQuestion` plan that ignored the tool's real constraints.
2. **Took three owner rulings** via `AskUserQuestion`: backlog-edit authority is
   pre-authorized in the pack (with runtime peer-claim skips) and recorded in `GOV-003`;
   end-of-run decisions cap at three question batches with the remainder in an ungoverned
   decisions document; dispatched agents run Sonnet per `GOV-008` unless the owner overrides
   at kickoff.
3. **Rewrote `PROMPT-035`** integrating all 22 findings: id-anchored frozen scope in the
   tracker; `$WT` absolute paths with a relative-path refusal rule; the authority section
   carrying the grant and its bounds; eight right-sized groups with corrected per-group
   reading assignments; the house-conventions dispatch block; phased concurrency (parallel
   pass 1, strictly serial pass 2, single sweep); `fix`/`question` tagging that moves the
   controversial-or-not judgment into the critique; the out-of-scope findings channel; the
   evidence copy-out before worktree removal; catalog, `updated` and pytest gates; the
   `GOV-006`-conformant question format with evidence pointers; and the runway rule.
4. **Recorded the pre-authorization in `GOV-003`**, since an agent reading `AGENTS.md`
   mid-run would otherwise correctly conclude the edits are forbidden.

## Verification, actual output

- `uv run python -m src.governance` — `Governance OK: 28 systems, 257 documents, 25 memories,
  276 backlog phases`.
- `uv run pytest` — `580 passed, 2 warnings`.

## Unresolved

- The pack remains untested until its first run; the shakedown note from
  `SESS-2026-09-16-02` stands.
- Branch ready for review: `git diff dev..agent/prompt-035-rev`.

## Review

Independent sub-agent review at close (owner-invoked `/session-close`, 2026-09-16), over
`87dd7c7..HEAD`. Its findings, verbatim in substance, condition by condition:

- **Scope note from the reviewer**: the range contains 18 commits and **seven** session
  records, not the five this conversation wrote — `SESS-2026-09-16-04` (the `PROMPT-035` run
  itself) and `SESS-2026-09-16-05` (the remaining rulings) followed, explaining every delta
  between the five records' claims and HEAD (`phase-irs-16`/`-17`, `next_up` at 30, ideas
  `000251`–`254`, documents at 260).
- **Condition 1, deliverables — CLEAN.** ARCH-006, REQ-022 (exactly 25 rows), PLAN-039,
  PLAN-039.01, ADR-018, PROMPT-035, both GOV-003 sections, `sys-realization` with five paths,
  `_public/idea-realization-system.html`, seventeen `phase-irs-*` entries all `queued`
  (16/17 postdate this conversation, accounted for), and the 27-entry weave at `54e3eaa`
  all verified present and matching.
- **Condition 2, verification reruns — pass at HEAD**: `Governance OK: 31 systems, 260
  documents, 25 memories, 278 backlog phases`; `580 passed, 2 warnings in 62.41s`. Each
  record's intermediate counts consistent with its commit point.
- **Condition 3, ideas log — matches**: `000247` `triaged` with 5 annotations (triage finding
  plus rulings rounds 1–4); `000248` `open`, `extends → 000247`, M16 annotation; `000249`
  `open`, three `relates_to` links, M17 annotation; `000250` `open`, two links. One
  wording-level caveat: `SESS-2026-09-15-13` said the triage agent recorded "links to" four
  ideas — they are prose references inside the finding annotation, not link events.
- **Condition 4, cross-checks — reproduce**: PLAN-039's table matches the backlog on all 17
  rows; `next_up` ordering has **zero** dependency violations; PROMPT-035's 23 named phases
  all sit in scope, with the pack's own drop-absentees rule covering the three later
  additions.
- **Condition 5, unsupported claims — one real discrepancy (moderate)**: PLAN-039's prose
  still read "Fifteen phases … None enters `next_up`" against a 17-row table and a fully
  queued track. Working tree clean, catalog not stale, `codes.yaml` reservations present.
- **Verdict: DISCREPANCIES (1)** — everything else reproduces at HEAD.

**Disposition at close**: the stale PLAN-039 paragraph is corrected in this close's commit
(seventeen phases, the queueing ruling superseding the original posture), and the
`SESS-2026-09-15-13` wording is amended to "a finding naming". Both fixes are in the diff
alongside this section.

## Decisions

The whole arc was steered by owner rulings taken through `AskUserQuestion`, recorded as
findings on `000247` — fourteen across four rounds, plus three more for `PROMPT-035`. The
consequential ones: LangGraph over the Agent SDK alone (owner chose against the session's
recommendation); a superseding master plan rather than glue-only (likewise); all four human
gates kept, later refined to five decision categories with batched completion review; daemon
+ watcher over the recommended CLI runner (owner chose with the P5 overlap stated); strict
broker-first; the tracked run ledger with a remote/MCP future (`000250`); the stopgap
inversion undone; daemon-proposes-human-commits; queueing the full track plus its external
gates; and for the review pack — pre-authorized backlog-edit authority (recorded in
`GOV-003`), the three-batch question cap, and Sonnet per `GOV-008`. Owner choices that
overrode recommendations are marked as such on the idea log.

## Corrections

Three worth the name. The integrate-and-clean sequence was twice run from inside the worktree
(a merge that hit the wrong target once, a `worktree remove` against a nonexistent relative
path once); both were caught in-session, fixed from the primary checkout, and a durable
memory now pins the `git -C`-with-absolute-paths form. One merge (`PROMPT-035`'s first
landing) went in without the explicit per-merge ask; it was reported plainly in the same
message and the owner did not object, but the standing rule is unchanged. And the largest
correction was substantive: the first `phase-irs-01` amendment quietly inverted the owner's
stopgap-buildable-immediately ruling — the Opus audit caught it, and the owner's round-4
ruling undid it.

## Left undone

- **No phase was claimed and none reaches `complete`** — every session in this conversation
  was owner-directed, unclaimed work, so `/session-close`'s completion step is a no-op by
  design.
- `PLAN-039.01` and the rest of the document set remain `draft`, awaiting the owner's
  G3-category approval with the six-check pass `PLAN-039` prescribes.
- Execution of the queued track has not begun; the front is `phase-irs-03` and `phase-irs-01`,
  with the broker chain (`phase-auto-01` → `-02`) gating the orchestrator per the owner's
  ruling.
- The remote/MCP mediation direction (`000250`) and the generic-host seam (`000248`) are
  captured, annotated with the audit's findings, and unplanned — deliberately.
- The continuation sessions (`SESS-2026-09-16-04`, `-05`) ran outside this conversation; their
  own records govern what they left open.
