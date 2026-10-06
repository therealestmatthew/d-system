---
schema_version: 1
id: doc-session-productivity-core-plan-resume
code: SESS-2026-10-06-03
title: Productivity core plan, resumed and parked again for the restart - owner rulings and resume point
kind: session
status: active
owner: repository-owner
created: '2026-10-06'
updated: '2026-10-06'
systems: [sys-portfolio, sys-backlog]
depends_on: [doc-backlog-decisions, doc-three-altitude-review-procedure]
---

# Productivity core plan, resumed and parked again for the restart

## Phase

Unclaimed: owner-approved planning work with no backlog phase. Session 1 - Builder A, assigned by
the Session Manager on 2026-10-06 to resume the productivity core plan parked on
`agent/plan-productivity-core` (`68ef945`, based on `4f01363`). That branch and its worktree are
not modified (owner's decision). Its session record, `SESS-2026-09-23-08`, exists only on that
branch and holds the owner's Q1 to Q10 answers, the three wind-down requirements and the sixteen
review findings this record refers to.

The owner asked on 2026-10-06 to wrap up sessions for a restart, so this session stopped after the
owner's rulings and before writing the plan. Nothing else is written on this branch.

## Owner rulings, 2026-10-06 (given in this session)

1. **Wind-down requirement 1 (partition sweep) is met by the accepted 2026-09-23 partition**
   (`docs/00-working/idea-partition-2026-09-23.json`). No new sweep runs. It places 000257 to
   000267, 000364 and 000365 in "Organisational entity model and its plan"; 000360 to 000363 in
   "Portfolio core-entity productivity gaps"; 000366 and 000367 in "Idea ontology, tags, link
   vocabulary and lifecycle status"; 000255 and 000256 unbatched. Background: `/partition-ideas`
   selects by status only, so a run on 2026-10-06 would have covered all 565 triaged ideas.
2. **Priority: realization first.** Q2 (weekly-review path directly after seeding, ahead of
   realization) no longer stands. The productivity path queues after the realization phases.
3. **Builders only for seeding and the specification phases** (finding 1). Batch tables keep
   build-only phases; `phase-cap-08`, `phase-conc-07` and every specification phase go to Builders.
4. **Project tags on ideas that name real projects live under the private data root, for now**
   (finding 2). The owner added that Postgres or another database may be wanted for scalability
   later; sent to Ideation as an idea.
5. **Backup first:** `phase-conc-07` runs before `phase-cap-08` (finding 14), so `phase-cap-08`
   gains a `depends_on` edge to `phase-conc-07`.
6. **000367 (link ideas to templates) is decided in ARCH-010's Idea lineage gate**, in the last
   organisational-model design phase. Its earlier home, `phase-idg-01`, completed without it.
7. **Queue position: backup and seeding move behind the realization phases** in `next_up`, with
   the rest of the productivity path.

Ideas recorded through Ideation in this session: 000597 (record who created each idea on its
created event), 000598 (an owner review session over every triaged idea). The Postgres idea was
sent; its id was not yet confirmed when this record was written.

## What changed on dev since 2026-09-23 (checked against b7e7fe8a)

- `phase-html-01` to `phase-html-10` are cancelled, so Q4 is moot. `phase-syn-05` still depends on
  the cancelled `phase-html-10`; the plan should flag it.
- `batch-007` is now run budgets and the batch graph; the new tables need ids from `batch-008`.
- Finding 15 is fixed on dev: `phase-irs-14` depends on `phase-irs-11`.
- `phase-rel-01`, `-02`, `-03`, `-08`, `phase-part-03`, `phase-des-01`, `phase-idg-01` are complete.
  `phase-cap-08`, `phase-conc-07`, `phase-rel-04` to `-07`, `phase-sig-*`, `phase-syn-*`,
  `phase-idg-04` are queued. Finding 11 is moot (`phase-idg-01` complete).
- 000345 still holds: neither `sql/001_schema.sql` nor `tools/rebuild_db.py` mentions `repository`.
- Codes via `--next-code` only: the plan becomes `PLAN-053` (the allocator takes the highest number
  plus one and does not refill `PLAN-044`), and the prompt document, if kept, `PROMPT-045`. Both
  were allocated on 2026-10-06; re-run `--next-code` on resume, since a reservation expires.

## To resume

1. Rebase onto dev. Re-run `--next-code` for the plan, the prompt and (if not merged with this
   record) nothing else.
2. Write the plan with every `GOV-010` section (it is created after 2026-09-22, so the `GOV-018`
   entry check applies). `AGENTS.md` rule 3 calls for a requirement document as well.
3. Re-add `phase-pc-01` to `phase-pc-09` from the parked branch, fixing the sixteen findings with
   the rulings above; split the parked `phase-pc-09` into the four remaining gates and a separate
   requirement-plan-review phase (finding 9); add 000367 to the Idea lineage gate phase; add the
   000366 line to `phase-idg-04` with ruling 4; add the `phase-conc-07` edge to `phase-cap-08`;
   run `--check-ideas`/`--backfill-ideas` after phase text edits.
4. Compose one build-only batch (`batch-008`) with `src.governance.backlog.collisions`, with
   `phase-cap-08` in `external_depends_on`, sequenced after the realization batches.
5. `next_up`: `phase-cap-08` is exempt from the review gate (`src/governance/review_gate.py`);
   `phase-conc-07` and any new phase are not, so they enter `next_up` only after a dispositioned
   `GOV-018` record lists them.
6. Record the rulings in `GOV-003`, regenerate the catalog, then stop before G3: the `GOV-018`
   review comes through the Session Manager (REVIEW-REQUEST) from a dedicated reviewer type.
