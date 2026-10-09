# Build batch tables

A batch table is one dependency-closed group of backlog phases, in the order a coordinator builds
them. [`schemas/batch.schema.json`](../../../schemas/batch.schema.json) is the contract;
[PROMPT-036](../../02-prompts/PROMPT-036-build-coordinator.md) is the coordinator that selects one
and runs it. [GOV-016](../../08-governance/GOV-016-batch-orchestration-protocol.md) is the protocol
governing how tables are composed, verified, sequenced, selected and superseded — read it before
writing one.

These tables hold **grouping, sequencing and parallelism only**. Every phase fact — scope,
acceptance, verification, `systems`, `deliverables`, `depends_on` — lives in
[`backlog.yaml`](../backlog.yaml) and is never restated here. A `title` is copied into a table for
readability; the backlog is authoritative when the two disagree.

| Table | Status | Seq | What it builds |
|---|---|---|---|
| `batch-001` | complete | 1 | Partition close, portfolio move, session lifecycle, first two realization foundations |
| `batch-002` | complete | 2 | Two governance guards, the autonomous-operations broker, the orchestrator skeleton |
| `batch-003` | complete | 3 | Where a promoted plan lives (its other phases were split out or completed elsewhere on 2026-09-27) |
| `batch-004` | in_progress | 4 | Mandatory-requirement ruling, idea planner agent, first three pipeline phases |
| `batch-007` | queued | 5 | Run budgets, hard caps and the kill switch, then the batch graph (split from `batch-003`) |
| `batch-005` | queued | 6 | Gate queue, execution-loop harness, delivered status, anti-pattern store |
| `batch-006` | queued | 7 | Learning loop, Gate 2 consolidation, trace baselines, forced-failure drill |
| `batch-009` | queued | 8 | Workbench duplication and structure audits, performance baseline and caching, port and process manager |
| `batch-010` | queued | 9 | Slot-model follow-ons: panel identity, slot geometry, sub-app contract and first sub-app, maximize and collapse, sys-ui retirement |
| `batch-011` | queued | 10 | Terminal panel reliability: drop diagnosis, session survival, start-failure reasons, loopback origin check |
| `batch-012` | queued | 11 | Truncation detection, transcript review, shared state model, delegation methodology, anti-pattern rules |
| `batch-013` | queued | 12 | Agent engineering guides and orchestration, lifecycle roster, expander, minimalist and arbiter |
| `batch-014` | queued | 13 | Idea terminal-state authority process, then the five idea-log backfills |
| `batch-015` | queued | 14 | Idea capture subagent, classification, tagging, decomposition, connections, metrics command, sessionless capture |
| `batch-016` | queued | 15 | Portable framework document templates and schemas |
| `batch-017` | queued | 16 | Portable framework content extraction |
| `batch-018` | queued | 17 | Prioritised search order, then deterministic search |
| `batch-019` | queued | 18 | Retrieval-failure collection and the gate record correction (waits on the unscheduled phase-mem-10 chain) |
| `batch-020` | queued | 19 | ADR-001 revisit, retrieval surveys, documentation-retrieval decision, code-graph evaluation |
| `batch-021` | queued | 20 | Memory staleness and confidence, then provenance |
| `batch-022` | queued | 21 | Claim recovery, branch protection, backup posture, enforcement placement, pull-request protocol rewrite |
| `batch-023` | queued | 22 | Index widths, document staleness, backlog archive, backlog review procedure |

`batch-008` is reserved for PLAN-053 and is not yet written.

## Status, and who moves it

`queued` — runnable and unstarted. `in_progress` — a coordinator run is open; it is resumed, never
restarted. `complete` — every phase reached `complete`. `superseded` — the composition was replaced
and the table is kept for history; it is never selected to run, and names its replacement in
`superseded_by`.

The coordinator moves `queued` → `in_progress` when it opens a run, and `in_progress` → `complete`
when the last phase completes. Composing a new table, and superseding an old one, is the owner's.

## Stages

Stages run in order; a stage begins only when every phase in the one before is complete and
integrated. Phases inside a stage carry no dependency edge between them and no shared system or
overlapping deliverable path, so the claim validator will admit them at once.

`parallel: true` is a **permission, not an instruction**. The coordinator still checks `max_active`
and the Conflicts column numerically before every claim, and a stage of three runs one at a time
when the budget has room for one. `conflicts_with` on a phase records why a phase with no
dependency can still be forced into a later stage — the reason is a lock, not an ordering.

## Selecting a table

PROMPT-036 picks the lowest-`sequence` table that is `in_progress`, else the lowest-`sequence`
`queued` one, and asks the owner when that is ambiguous. The rule and its ambiguity cases are
stated in the prompt.

Nothing validates these tables yet — idea `000316` holds the governance check that would, and
`000317` the protocol that would govern how they are authored.
