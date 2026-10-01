---
schema_version: 1
id: doc-session-idea-set-aside-status
code: SESS-2026-09-30-01
title: The set-aside idea status and the partition hold-out field
kind: session
status: active
owner: repository-owner
created: '2026-09-30'
updated: '2026-09-30'
systems: [sys-contracts, sys-portfolio]
depends_on: [doc-idea-graph-lifecycle]
---

# The set-aside idea status and the partition hold-out field

## Phase

`phase-idg-19` — Add the set-aside status and the partition hold-out field.

Claimed on dev at `49d0cf3` by agent-builder-b (Session 2 - Builder B), inside a turn granted by
Session Manager. Work is on `agent/phase-idg-19` in `../d-system-worktrees/phase-idg-19`.

Approvals behind the claim:
- The owner approved the claim in this session (AskUserQuestion, 2026-09-29), after Session Manager
  relayed an overnight pre-approval. The relay was not treated as the approval.
- The owner approved, in this session, widening the deliverables with `tools/overview_metrics.py`,
  `src/orchestrator/state.py` and `agent-workflows/idea.md`. These are strictly needed: the first
  two raised `KeyError` and `ValueError` on any status they did not list.
- The owner ruling, relayed by Session Manager: narrow the `test/` deliverable to `test/test_ideas.py`,
  `test/test_overview_tools.py`, `test/test_orchestrator.py` and `test/test_idea_partition_record.py`,
  so the claim no longer overlaps phase-gov-01's `test/test_backlog.py`.
- During the build the owner chose, in this session, to narrow again: the help-text edit to
  `tools/append_idea.py` and the lifecycle edit to `agent-workflows/idea.md` were reverted, because
  their generated copies (`docs/08-governance/OPS-005-append-idea.md`, `.claude/commands/idea.md`,
  `.agents/skills/idea/SKILL.md`) are outside the claim.

## Verification

```
$ uv run pytest
1187 passed, 1 warning
```

```
$ uv run python -m src.governance
Governance OK: 43 systems, 409 documents, 34 memories, 347 backlog phases
```

Supporting checks, run in the same state:

```
$ uv run python tools/generate_agent_workflows.py --check
16 workflow adapter(s) current
```

The owner regenerated `.agents/skills/partition-ideas/SKILL.md` in this worktree (generator exit 0,
"wrote 16 workflow adapter(s)"), and it is committed as `e47439f`. The private-content check was
re-run with the identifiers from the primary checkout's `_private/portfolio/`. This worktree has
none, so the pre-commit hook had checked 0 identifiers. Result: 1100 tracked files, 31 identifiers,
0 violations.

## Acceptance

- The set-aside status (placeholder name `set_aside`) is legal from triaged, is not terminal, and
  accepts a later transition to triaged or to reviewing; the writer rejects it from any other status.
  **Met.** Covered by the `set_aside` tests in `test/test_ideas.py`, which pass in the run above.
- A partition record carrying an owner hold-out in the new field validates against
  `schemas/idea-partition-record.schema.json`, and the accepted 2026-09-23 partition record still
  validates unchanged. **Met.** Covered by `test/test_idea_partition_record.py`, which passes.
- Verification as a whole: **Met.** Both commands are green above.

## Backlog

`phase-idg-19`: `status: active`, `agent: agent-builder-b`. `next_action`: all acceptance conditions
met and verification green on `agent/phase-idg-19`; awaiting the `/session-close` independent review,
READY to Session Manager, and the owner's merge approval. The phase stays active until the merge.

## Unresolved

- `agent-workflows/idea.md` still describes the old lifecycle, with no `set_aside` and none of the
  closing states. A follow-up idea should update it, together with its generated adapters and
  `OPS-005`.
- The name `set_aside` is a placeholder until idea 000453 (disposition terminology) is ruled on.
- Follow-ups already recorded by Ideation: 000516 (workbench precedence map and explorer status
  list) and 000517 (plugin writer parity).
