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
FAILED test/test_agent_workflows.py::test_committed_adapters_match_canonical_sources
1 failed, 1180 passed, 1 warning
```

The one failure is `.agents/skills/partition-ideas/SKILL.md`, a declared deliverable, which is stale
against its canonical source `agent-workflows/partition-ideas.md`
(`uv run python tools/generate_agent_workflows.py --check` reports it). Agents are denied writes
under `.agents/`, so the owner must regenerate it.

```
$ uv run python -m src.governance
Governance OK: 43 systems, 398 documents, 34 memories, 341 backlog phases
```

## Acceptance

- The set-aside status (placeholder name `set_aside`) is legal from triaged, is not terminal, and
  accepts a later transition to triaged or to reviewing; the writer rejects it from any other status.
  **Met.** Covered by the `set_aside` tests in `test/test_ideas.py`, which pass in the run above.
- A partition record carrying an owner hold-out in the new field validates against
  `schemas/idea-partition-record.schema.json`, and the accepted 2026-09-23 partition record still
  validates unchanged. **Met.** Covered by `test/test_idea_partition_record.py`, which passes.
- Verification as a whole: **Not met.** `uv run pytest` has one failure until the `.agents` adapter
  is regenerated.

## Backlog

`phase-idg-19`: `status: active`, `agent: agent-builder-b`. `next_action`: the owner regenerates
`.agents/skills/partition-ideas/SKILL.md`; then commit it, re-run the full suite, run
`/session-close` through its independent review, and send READY.

## Unresolved

- `.agents/skills/partition-ideas/SKILL.md` needs regenerating by the owner. From the worktree:
  `uv run python tools/generate_agent_workflows.py`, then `--check` to confirm.
- `agent-workflows/idea.md` still describes the old lifecycle, with no `set_aside` and none of the
  closing states. A follow-up idea should update it, together with its generated adapters and
  `OPS-005`.
- In this worktree the pre-commit private-content check ran with 0 identifiers, because
  `_private/portfolio/` is absent here; only paths were checked. Run it against the branch from the
  primary checkout before READY.
- The name `set_aside` is a placeholder until idea 000453 (disposition terminology) is ruled on.
- Follow-ups already recorded by Ideation: 000516 (workbench precedence map and explorer status
  list) and 000517 (plugin writer parity).
