---
schema_version: 1
id: doc-session-prompt-planner-batch-opening-packs
code: SESS-2026-09-23-03
title: Prompt Planner session — the batch-003 and batch-004 opening question packs
kind: session
status: active
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-governance]
depends_on: []
---

# Prompt Planner session — the batch-003 and batch-004 opening question packs

## Phase

Unclaimed — owner-directed work, no backlog phase. `prompt-planner-session-record` — act as the
Prompt Planner under the multi-session coordination protocol (GOV-017), and prepare the opening
question packs for batch-003 and batch-004 that the Session Manager assigned with the owner's
approval.

## Verification

```
$ uv run python -m src.governance
Governance OK: 35 systems, 327 documents, 30 memories, 293 backlog phases
```

```
$ uv run pytest
871 passed, 1 skipped, 2 warnings
```

```
$ uv run python tools/check_no_private_content.py   # with this record staged
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (822 tracked files, 0 identifiers checked)
```

## Acceptance

Self-declared from the owner's instruction; no backlog acceptance list exists for this session.

- The batch-003 opening pack exists at `_working/session-manager/batch-003-opening-pack.md`: each
  decision is a multiple-choice question with its recommendation first, with evidence, and with
  nothing in a preview. — Met. The file exists, and the owner has answered it: the Session Manager
  appended an `OWNER ANSWERS` section.
- The batch-004 opening pack exists at `_working/session-manager/batch-004-opening-pack.md` in the
  same format, has a preconditions section, and folds in the batch-003 answers. — Met. The file
  exists with a preconditions section and a section headed "What changed from the batch-003
  answers".
- No tracked file changed except this record. — Met. Both packs are under the gitignored
  `_working/`. This record and its regenerated catalog row are the only changes on the branch.

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of backlog.yaml was changed.

## Unresolved

- This record reaches dev only through GOV-017's merge gate. The owner has said they will clear
  this session after close, so the merge will have to be done by whoever holds
  `agent/prompt-planner-session-record` at the time the Session Manager grants it.

## Review

**Skipped, by the owner's instruction.** The owner invoked `/session-close` with "but skip any
additional review agents". Step 3 of `session-close.md` says the independent review is never
skipped. The owner's direct instruction was followed. Because this session is unclaimed, the skip
does not change any completion decision: no phase was completed, and no backlog line was edited.

## Decisions

- **Every idea went to Ideation.** Under the coordination contract, ideas that came up went to the
  Ideation session and were not recorded here. One went: the catalog tests write to the tracked
  `catalog.md`, recorded as `000325`.
- **Batch-open commit (ruled by the owner).** I pointed out that PROMPT-036's commit opening a batch
  had no turn purpose under GOV-017, which allowed only `claim` and `idea` turns. The owner ruled
  that it gets its own turn, `TURN? batch <batch-id>`. I then pointed out that the ruling covered
  only the `status` line while PROMPT-036 also sets `updated`. The ruling was widened to cover both
  lines, and that change merged at `672a4d8`.
- **Batch-003 recommendations.** In the batch-003 pack I combined the two reviews' separate
  recommendations for irs-14 and irs-11 into one ordering: irs-11 first, tested against the intake
  graph. The owner chose that option.
- **Batch-004 reasoning after batch-003.** Two reviews had argued against adding a dependency
  because it would wait on unfinished work. Once batch-003 is complete, that argument no longer
  applies. For Q3 and Q4 I kept the reviews' recommendations and said which of their reasons still
  holds, rather than silently changing the recommendation.
- **Items settled without a question.** One batch-004 review item was resolved by checking instead
  of asking the owner: `phase-prog-06` did strike idea 000072's planner bullet (PLAN-031, lines 65
  and 271). One proposed fix was dropped, the idg-10 guard, because idg-10 is now complete.

## Corrections

- **Batch-003 precondition 3.** The batch-003 pack first said that edits to tracked files needed a
  primary-checkout turn. GOV-017 then limited turns to `claim` and `idea`, so I rewrote that
  precondition and Q8's recommended option to use a fixes branch merged through `READY`.
- **An ordering I made up.** A first draft of batch-003 precondition 4 put the batch-open turn after
  the fixes branch merged. Nothing states that order, so I removed it before sending.

## Left undone

- Both packs wait on batch-002, which is still `in_progress` (irs-04 and part-03). Batch-004 also
  waits on batch-003 and its fixes branch. Session 5 uses them at `NEXT-BATCH`.
- No PROMPT-NNN document was written this session. Nothing asked for one.
