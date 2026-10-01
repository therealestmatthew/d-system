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

## Review

Independent adversarial review by a `demo-adversary` sub-agent (fresh context, not a fork) over
`dev...agent/phase-idg-19` with dev at `8d1bfcf`, given the phase's scope, acceptance, verification
and deliverables. Its findings, condition by condition, as reported:

- **Acceptance 1** (set_aside legal from triaged only, non-terminal, returns to triaged or
  reviewing, writer rejects it elsewhere): **Met.** `legal_transitions()` has exactly three edges
  touching `set_aside`: triaged→set_aside, set_aside→triaged, set_aside→reviewing.
  `change_status` enforces transitions only through that schema-derived table. The new tests in
  `test/test_ideas.py` assert `IdeaError` and an unchanged log, so they do not pass trivially.
- **Acceptance 2** (hold-out field validates; the 2026-09-23 record still validates unchanged):
  **Met.** The reviewer validated `docs/00-working/idea-partition-2026-09-23.json` against the new
  schema with `jsonschema` itself: valid. The same record with a synthetic `held_out` entry is also
  valid. `held_out` reuses `reasoned_id`, the same shape as `unbatched`. The five malformed-entry
  tests correctly fail validation.
- **Verification:** `uv run pytest -q` → `1187 passed, 1 warning`; `uv run python -m src.governance`
  → `Governance OK: 43 systems, 409 documents, 34 memories, 347 backlog phases`.
- **Findings:** no blockers, no majors.
  - Minor, pre-existing and out of scope: `ts/src/stage/IdeaExplorerRegion.tsx:23` hardcodes the
    explorer's status-filter list, which already lacked the closing states and now also lacks
    `set_aside`. Unfiltered, a `set_aside` idea still renders and counts. The only loss is filtering
    to that status. The file is outside the deliverables, and the gap is tracked by idea 000516.
  - Confirmed safe: the workbench queue precedence map falls back to a documented unknown-status
    precedence rather than raising. `src/orchestrator/state.py` and `tools/overview_metrics.py` now
    read the schema's status enum instead of a stale restated list, with tests. The three
    partition-ideas copies match the generator (`16 workflow adapter(s) current`). GATE 3's
    embedded check counts `held_out` ids as placed. No file changed outside the deliverables and
    bookkeeping. The phase stays `active`.
  - Noted, not a finding: the plugin's own schema and writer under `plugins/idea-realization/` lack
    `held_out` and `set_aside`. The drift predates this phase and is tracked by idea 000517.
- **Session-record claims:** no discrepancy found between the record and the diff or reruns.
- **Worktree:** left clean, and the catalog shows no diff.
- **Coverage gap the reviewer declared:** it read but did not execute the `tools/append_idea.py`
  command line. I closed this after the review by running `main()` against a scratch log (the
  module's `LOG` patched; the real `_data/ideas.jsonl` hash unchanged). `status set_aside` from
  open: exit 1, "illegal transition … open -> set_aside". From triaged: exit 0. set_aside →
  discarded: exit 1, "Legal from set_aside: reviewing, triaged". set_aside → triaged and
  set_aside → reviewing: exit 0.

Disposition: the one minor finding is accepted as out of scope, tracked by 000516. Nothing to fix.

## Decisions

- The status is reachable from triaged only. This is the builder's reading of "reachable from
  triaged". The Session Manager accepted it and it is recorded in the phase scope. The owner has
  not ruled on it.
- `set_aside` is a placeholder name until idea 000453 (terminology for idea dispositions) is ruled
  on. Renaming it later touches the schema enum, the transition branches and the tests.
- The owner approved widening the deliverables with `tools/overview_metrics.py` and
  `src/orchestrator/state.py`, because both raised on a status they did not list. Both now read the
  schema's enum, which also fixes their silent omission of the closing states.
- The owner narrowed the claim during the build. The `tools/append_idea.py` help text and the
  `agent-workflows/idea.md` lifecycle edits were reverted, because their generated copies were
  outside the claim. The follow-up went to Ideation as an IDEA message on 2026-09-30.
- Agents cannot write under `.agents/`, so the owner ran `tools/generate_agent_workflows.py` in
  the worktree through Owner Terminal. Its output is committed as `e47439f`.

## Corrections

None in this session's work. The worktree's pre-commit private-content check ran with 0
identifiers because `_private/portfolio/` is absent there. It was re-run with the primary
checkout's identifiers rather than trusted: 1100 files, 31 identifiers, 0 violations.

## Left undone

- **Completion.** The phase stays `active`. Under the Session Manager contract, completion happens
  on dev after the owner approves the merge, with the catalog regenerated in the same commit.
- **Consumers outside the claim** that do not yet know `set_aside`:
  - the workbench queue precedence map and the explorer status list (000516);
  - the idea-realization plugin's writer and schema (000517);
  - the lifecycle text in `agent-workflows/idea.md` and `append_idea.py`'s help, with their
    generated copies (sent to Ideation).
  None of them raises on the new status. They omit it.
- **The name.** It waits on 000453.
