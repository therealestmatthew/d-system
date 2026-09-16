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
