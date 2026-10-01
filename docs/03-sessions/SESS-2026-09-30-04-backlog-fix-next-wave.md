---
schema_version: 1
id: doc-session-backlog-fix-next-wave
code: SESS-2026-09-30-04
title: Queued-phase review fixes for sch-03, ret-08 and lrr-03
kind: session
status: active
owner: repository-owner
created: '2026-09-30'
updated: '2026-09-30'
systems: [sys-backlog]
depends_on: []
---

# Queued-phase review fixes for sch-03, ret-08 and lrr-03

## Phase

Unclaimed: owner-directed work with no backlog phase. `backlog-fix-next-wave` applies the fixes from
the 2026-09-29 PROMPT-035 pass 1 reviews of `phase-sch-03` (frontend lint and test gate),
`phase-ret-08` (code-graph tool evaluation) and `phase-lrr-03` (browsable literature-review tables)
to their backlog lines. The owner approved it on 2026-09-30, and the Session Manager relayed it. The
work edits phase definitions only and builds nothing. The reviews are kept under
`_working/session-manager/reviews/`.

## What changed

- `phase-sch-03`: script naming and lint-baseline rulings in scope; the first frontend test is named
  as new; `npm run lint` and `npm test` added to verification; a self-check acceptance line, with a
  verification line saying it is checked by reading the session record; `next_action` line numbers
  brought current (ci.yaml 45-46).
- `phase-ret-08`: LadybugDB named, citing the existing successor survey; a try-then-fall-back rule in
  which a blocked run leaves R11 recorded as not met; verification says plainly that no command
  observes R11; deliverable narrowed from `docs/00-working/` to
  `docs/00-working/code-graph-retrieval-evaluation.md`; `next_action` points at the survey.
- `phase-lrr-03`: `_csv_placeholder()` named as the seam; an `{{INLINE_SCRIPT}}` token filled by the
  renderer, including the stale header comment; Playwright in-page timing by `demo-validator-web`;
  deliverables widened from one file to the seven the scope touches; stale "Blocked" `next_action`
  replaced.
- `GOV-003`: a new entry recording the owner's rulings and the alternatives declined.
- `backlog.yaml` top-level `updated` set to 2026-09-30.

Owner rulings, all given in this session on 2026-09-30 through AskUserQuestion: `lint` becomes eslint
and the type-check moves to `typecheck`; fix what a default ruleset flags; LadybugDB; try, then fall
back; state plainly that no command observes R11; the renderer inlines the script; Playwright
in-page timing.

Review findings left unchanged because the reviews recommended no change: sch-03 Q4 and Q5, ret-08 Q6
and Q7, lrr-03 Q5 to Q8. `phase-conc-05` and `phase-irs-13` are outside this branch.

## Review

Independent READY review by a fresh `demo-adversary` sub-agent over `be4ab36..54c1b5b`. Verdict:
**HOLDS-WITH-FIXES**, with no blockers. It confirmed the line numbers, scripts, seam, survey content
and the absence of deliverable collisions, and `--ready` lists all three phases ready with no
conflicts.

1. **(major)** The new sch-03 self-check acceptance line had no verification line saying how it is
   observed. **Fixed:** a verification line now says it is checked by reading the session record.
2. **(minor)** The GOV-003 entry names "a `<script>` block carried by the table template" as a
   declined alternative that neither the review nor the ruling mentions. **Accepted, no change:** it
   was one of the two options the owner was shown in this session and declined. The reviewer was
   given the rulings but not the options.
3. **(minor)** The ret-08 acceptance line "records the tool's version, the commands run and their real
   output" matches no review finding. **Accepted, no change:** it is the content of the verification
   option the owner chose ("state it plainly", which named tool, version, commands and output).
4. **(minor)** `templates/html/lit-report-page.html:49` says "no script tag", which the new token
   makes stale. **Fixed:** the lrr-03 scope now asks for that comment to be updated.

## Verification

Recorded in the READY report after the post-rebase runs: governance, pytest, ruff and mypy in this
worktree. The worktree skips the private-content scan because `_private/portfolio/` is absent, so the
changed files were scanned from the primary checkout: 31 identifiers loaded, 0 hits.

## Left undone

- The reviews' out-of-scope notes on `phase-conc-05` (shares `ci.yaml`) and
  `phase-irs-13` (whole-`ts/` deliverable) are not acted on here.
