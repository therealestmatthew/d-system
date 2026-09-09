---
schema_version: 1
id: doc-adr-multi-agent-concurrency
code: ADR-003
title: 'ADR-003: Worktree-isolated concurrent agents over a disjoint backlog'
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems: [sys-backlog, sys-governance, sys-delivery]
depends_on: [doc-adr-session-backlog]
---

# ADR-003: Worktree-isolated concurrent agents over a disjoint backlog

## Context

[ADR-002](ADR-002-session-backlog.md) permitted exactly one active phase and named its own revisit
trigger: "One-active-phase enforcement can be revisited when the user explicitly adopts multiple
simultaneous work streams." The user has now adopted them. Several autonomous agents should be able
to execute different backlog phases at the same time.

Two distinct hazards appear at that point, and they need different mechanisms.

The first is **filesystem collision**. A single checkout has one working tree, one `data/d_system.duckdb`,
one `.venv` and one set of dev-server ports. Agents that share it by switching branches overwrite each
other's edits mid-test, invalidate a peer's rebuild, and produce test results that describe a tree
nobody intended. Branches alone do not solve this, because a branch is a name for a commit, not an
isolated directory.

The second is **logical collision**. Two agents can hold physically separate directories and still
produce diffs that cannot be reconciled, or produce a green result that stops being true once merged.
Git reports the textual half of this at merge time, which is far too late for an autonomous worker
that has already claimed a session and written a completion record.

The repository already carries the material needed to detect logical collision in advance: `systems.yaml`
declares component boundaries with owners and paths, and every backlog phase declares the `systems` it
touches, its `deliverables` paths and its `depends_on` prerequisites.

## Decision

**Isolation.** Every agent claiming a phase works in its own `git worktree` on branch `agent/<phase-id>`,
checked out at a sibling path `../d-system-worktrees/<phase-id>` with its own `.venv` and its own derived
DuckDB file. Worktrees live outside the repository directory so that no tool operating on the primary
checkout — `pytest`, `ruff`, `mypy`, or the governance Markdown scanner — ever walks a second copy of the
repository. `_worktrees/` is gitignored as a guard against a misplaced worktree being committed, not as a
sanctioned second location.

**Claiming.** `docs/09-backlog/backlog.yaml` on `dev` — the integration branch — is the lock table. A
claim is a small commit on `dev` that sets one phase to `active` and names its `agent`; the governance validator run against that
commit is the lock check. Because the claim is serialized through `dev` rather than held on the agent's
own branch, two agents cannot both believe they hold the same work, and a losing race surfaces as an
ordinary non-fast-forward push.

**Safety rule.** `inspect_backlog` replaces the hardcoded single-active constraint with a bounded,
declaration-driven check. A new optional top-level `max_active` caps simultaneous claims — default `1`,
so the constraint is unchanged for anyone who does not opt in; this repository sets `3`. Beyond the cap,
every pair of active phases must be disjoint in three independent respects:

| Rule | Rejects | Rationale |
|---|---|---|
| Disjoint `systems` | Two phases naming the same `sys-*` ID | The registry is the declared ownership boundary; sharing one means sharing responsibility for the same behavior |
| Disjoint `deliverables` paths | Equal or nested declared paths | Disjoint systems can still both target a shared file such as `src/api/__init__.py`; this is the textual-conflict predictor |
| No transitive `depends_on` link | An active phase reachable from another active phase | A dependent phase would be built against an unfinished, unmerged prerequisite |

A new optional `agent` field carries the claim identity, is required on every active phase once
`max_active` exceeds `1`, is limited to one active phase per agent, and must be released when a phase
returns to `queued`. The generated `--ready` and `--backlog` reports gained an active-claims table and a
per-phase conflicts column, so an agent selecting work sees which systems are already locked before it
commits a claim.

**Handoff.** Completion is unchanged in substance and stricter in sequence: verification commands run in
the worktree, a dated session record is written to `docs/03-sessions/`, the phase records `session`,
`completion_evidence` and `result`, the branch is rebased onto current `dev`, and the full governance
command is re-run *after* the rebase before the branch is integrated. The re-run is the point of the
whole design — it is what proves the phase is still valid alongside the peers that merged during the
session.

## Alternatives

| Alternative | Tradeoff |
|---|---|
| Branches in one shared checkout | Free to set up, but agents overwrite each other's working files, and a test result describes whichever branch was last checked out rather than the one under test |
| Full clone per agent | Equivalent isolation, but duplicates history and object storage per agent and loses the shared ref namespace that makes claims visible |
| Keep one active phase; serialize agents | Preserves today's guarantees exactly, and forfeits the concurrency the user asked for |
| Optimistic concurrency; resolve at merge | Detects only textual conflict, only after an agent has finished work and written completion evidence |
| Also reject adjacency in the `systems.yaml` dependency graph | With fourteen systems, an active `sys-projection` phase would block `sys-retrieval`, `sys-signals` and more; the practical result is agents under-declaring `systems` to escape the check, which defeats the mechanism the safety rule depends on |
| A lock file separate from the backlog | A second state authority to keep synchronized with the phase status it duplicates |

## Consequences

Up to three agents can work simultaneously, and the validator states mechanically why a fourth claim or
an overlapping claim is refused. Concurrency is bounded by how finely the backlog is decomposed: phases
that name broad `systems` lists serialize against each other, which is a real incentive to keep phase
scope narrow and is deliberately not worked around.

The mechanism trusts declarations. A phase that edits files outside its declared `systems` and
`deliverables` defeats the check, and no validator can detect that before the diff exists — it remains a
review responsibility, now with a specific thing to look for. Adjacency in the systems graph is likewise
uncontrolled: an agent working `sys-html` while a peer changes `sys-api` must treat the upstream contract
as frozen at the commit it branched from, and the protocol says so, but nothing enforces it.

`backlog.yaml` becomes the most contended file in the repository. Its conflicts are near-always
mechanical — two agents appending unrelated item edits — and the resolution rule is to keep both sides
rather than to choose one. Collisions that require an actual choice are recorded in
[GOV-003-backlog-decisions.md](../08-governance/GOV-003-backlog-decisions.md).

This ADR amends only the concurrency clause of ADR-002. Everything else there — one-session sizing,
derived readiness, evidence-backed completion, no external tracker — stands unchanged, and ADR-002
remains accepted rather than superseded. Revisit if agents routinely stall waiting for a lock (decompose
phases or raise `max_active`), or if merges keep conflicting despite disjoint declarations (the
declarations are wrong, not the rule).
