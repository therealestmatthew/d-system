# System Boundary Study — System and Backlog Portfolio Review

## Baseline and method

This review is a read-only snapshot of commit `4f3848e71af81cc0aea06ec7b0c911c5d995a06e`
on 2026-09-26. It uses only tracked material and makes no registry, priority, queue, or lifecycle
change. The command results cited below are reproducible at that revision.

| Measure | Source command or tracked source | Observed result |
| --- | --- | --- |
| Registry size and maturity | `uv run python -m src.governance --inventory`; `docs/08-governance/systems.yaml` | 43 registered systems: 17 implemented, 4 scaffold, 21 planned, and 1 retired. |
| Registry domains | `docs/08-governance/systems.yaml` status/domain fields | 15 application, 11 delivery, 8 governance, 5 data, and 4 memory systems. |
| Plan coverage | `rg -n '^status:' docs/01-plans --glob '*.md'` | 77 plan documents: 38 draft, 25 approved, 11 active, and 3 complete. |
| Phase portfolio | `uv run python -m src.governance --backlog` | 323 one-session phases: 116 complete, 4 active, 195 queued, and 8 deferred; 84 were dependency-ready and 111 waiting. |
| Dependency depth | Iterative traversal of tracked `systems.yaml` and `backlog.yaml` `depends_on` fields | Longest registered-system chain is 5 nodes; longest phase chain is 14 nodes. |
| Active locks and collisions | `uv run python -m src.governance --backlog`; tracked backlog system lists | 4 of 4 active slots were occupied. The active locks covered `sys-backlog`, `sys-gov-docs`, `sys-plugin-backlog`, `sys-plugin-generators`, and `sys-plugin-ideas`. Of 84 dependency-ready queued phases, 10 intersected an active lock and 74 did not. |
| Document and retrieval signals | `uv run python -m src.governance --inventory`; `docs/08-governance/catalog.md`; `systems.yaml` entry for `sys-retrieval` | The catalog contains 377 governed documents and the inventory reports 32 memories. `sys-retrieval` is implemented and provides read-only keyword, project, type, and conjunctive-tag filtering. |

## Observations

### Registry maturity and ownership surface

The implemented portion of the registry is concentrated in the governance, data, retrieval, and
workbench surfaces, while planned systems outnumber implemented systems (21 to 17). The registry
therefore describes a portfolio that includes both operating components and intended future
components; a boundary decision must not assume that a planned system has a runtime interface or a
separate release need today.

The domain counts provide a useful but limited map of concern: application and delivery entries are
the largest groups, while governance is cross-cutting rather than a product surface. This is
consistent with the system inventory's candidate concerns, but this review does not change any
system's disposition or ownership.

### Plan and phase coverage

The plan corpus is predominantly prospective: 63 of 77 plans are draft or approved, while 14 are
active or complete. The backlog contains 207 unfinished phases (4 active, 195 queued, 8 deferred),
so document-level plan status should not be treated as evidence that a related system is shipped.

The phase report exposes both types of blocked work. At the baseline, 111 phases were waiting on
prerequisites, while 10 of the 84 dependency-ready queued phases conflicted with an active lock.
The latter is an execution-capacity and shared-surface signal, not an ordering recommendation.

### Dependency depth and work in progress

The longest system dependency path has five nodes, whereas the phase graph reaches fourteen. That
contrast indicates that execution sequencing adds material depth beyond the registered component
relationships. The four active claims consumed the entire configured capacity at this snapshot.
The review records this as an operational constraint; it neither reprioritises nor changes the
queue.

### Retrieval signals and limits

The repository has deterministic inventory and catalog entry points, and `sys-retrieval` supplies
structured filtering over the projected memory corpus. Those are availability signals, not measured
retrieval quality. The tracked inputs provide no query log, latency distribution, recall/precision
evaluation, failed-search corpus, or documentation-read path telemetry at this baseline. No claim
about discoverability effectiveness can therefore be made from this review.

## Analysis limits

- Counts are a point-in-time baseline, not a velocity or effort forecast.
- The dependency-ready calculation means every declared predecessor is complete; it does not model
  queue order, the four-slot cap, or non-declared human dependencies.
- Lock-collision counts are based on declared `systems` fields, so they cannot detect unrecorded
  file-path overlap or external coordination.
- Plan and phase status are governance metadata, not a runtime maturity measurement.
- No private content, runtime behaviour, or untracked worktree state was inspected.

## Questions for the boundary report

1. Which cross-cutting governance and backlog interfaces need a narrower contract before an
   independently released product boundary is practical?
2. Does the gap between the five-node system graph and the fourteen-node phase graph arise mainly
   from governance sequencing, shared documentation surfaces, or genuine runtime dependencies?
3. What retrieval evaluation would demonstrate that the current catalog and structured filters are
   adequate for a separated concern, rather than merely available?

These are evidence-backed questions for the owner decision report, not recommendations or backlog
changes.
