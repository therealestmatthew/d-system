---
schema_version: 1
id: doc-session-procedure-handoff-step-5
code: SESS-2026-10-04-13
title: Record the skipped hand-off step 5 as a brain procedure
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-brain]
depends_on: []
---

# Record the skipped hand-off step 5 as a brain procedure

## Phase

Unclaimed: owner-directed work, no backlog phase. `procedure-handoff-step-5`. Record, through
`log-anti-patterns`, the repeated skip of `AGENTS.md` hand-off step 5 as a `brain/procedures/`
entry, and send the guard for it to Ideation as an idea.

## Verification

`uv run python -m src.governance`

```text
Governance OK: 44 systems, 436 documents, 37 memories, 347 backlog phases
```

`uv run pytest`

```text
1454 passed, 1 skipped, 1 warning
```

`uv run python tools/check_no_private_content.py`

```text
check_no_private_content: OK (1308 tracked files, 0 identifiers checked)
```

The worktree cannot see `_private/portfolio/`, so that check read no identifiers. The diff is one
procedure, one index line and this record, and holds no portfolio content.

## Acceptance

Self-declared from the owner's instruction; no backlog acceptance list exists for this session.

- A `brain/procedures/` entry records the slip and the rule: Met.
  `brain/procedures/earlier-steps-are-not-absorbed-by-a-later-one.md`, id
  `mem-proc-earlier-steps-are-not-absorbed-by-a-later-one`, is listed in `brain/index.md` under
  Procedures. The governance check counts 37 memories, up from 36.
- Its account matches the history: Met. On `phase-des-11` and `phase-des-01`, `session`,
  `completion_evidence` and `result` first appear in `8042375` and `7d06a7c`, the post-merge
  completion commits. This was checked with `git log -S` on `backlog.yaml`.
- The guard is captured as an idea, not written as a rule: Met. It was sent to Ideation, as the
  coordination contract requires, and recorded as idea `000581`.

## Backlog

Unclaimed — no backlog phase was claimed for this session; no line of backlog.yaml was changed.

## Unresolved

None.

## Decisions

The owner chose this destination in two steps:
- first, a procedure entry on its own branch, rather than session records only or a change to the
  coordinator's contract;
- then, when asked for a recommendation, both the procedure and a guard idea.

The slip recurred while the rule was already written down. A check that fails is what stops it
recurring.

`AGENTS.md` and `CLAUDE.md` were not edited. Step 5's rule there is correct; the slip was in
following it.
