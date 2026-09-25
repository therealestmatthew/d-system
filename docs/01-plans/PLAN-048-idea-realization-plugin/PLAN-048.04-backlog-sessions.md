---
schema_version: 1
id: doc-idea-realization-plugin-backlog-sessions
code: PLAN-048.04
title: Idea-realization plugin — backlog check, ready report and the session skills
kind: plan
status: approved
owner: repository-owner
created: '2026-09-25'
updated: '2026-09-25'
systems: [sys-plugin-backlog]
depends_on: [doc-idea-realization-plugin]
parent: doc-idea-realization-plugin
---

# Backlog check, ready report and the session skills

Child of [PLAN-048](PLAN-048-overview.md); delivered by `phase-plug-04`. Covers `REQ-031` R14
and R15.

## Context and scope

`src/governance/backlog.py` (376 lines) is pure: every rule takes dicts and returns errors, with
no file or git access (analysis 03 §1). The rules are listed as facts in analysis 03 §2. The
regression check (`regression.py`) hard-codes the decisions document's filename (§3). The session
procedures are `.claude/commands/session-start.md`, the `checkpoint` skill and
`.claude/commands/session-close.md`; the completion rule in force is coordinator completion under
three conditions (analysis 03 §2, "Completion is a separate, gated procedure").

## Decisions

- **`scripts/backlog.py` is `src/governance/backlog.py` with only the import line changed.**
  Rejected: re-deriving the rules. Cost: none; a test runs both over one fixture and compares the
  error lists while this repository's copy exists.
- **The regression check resolves the decisions document from the catalog's `decision_record`.**
  Rejected: the literal filename (silently compares nothing in a target that names it otherwise).
- **The session skills state the coordinator-completion rule as the current rule** and take the
  branch and worktree directory from `userConfig`. Rejected: the owner-only `/session-close`
  framing (superseded on 2026-09-16 here). Cost: none.
- **`decision_record` is optional in the plugin's backlog schema** (owner, 2026-09-25): the
  scaffold seeds no decisions document, and the regression check runs only when one is named.
  Rejected: seeding a placeholder decisions document (a governed document with nothing in it).
- **Phase ids stay a manual convention**, documented in the layout reference (`phase-plug-06`).
  Rejected: an allocator (new mechanism the source does not have).

## Work and dependencies

1. `scripts/backlog.py`, `scripts/regression.py`, the backlog half of `scripts/check.py`, the
   `ready` subcommand; copy `backlog.schema.json`.
2. Port `test/test_backlog.py` and `test_backlog_status_regression.py` to fixtures; drop the one
   test that reads this repository's backlog.
3. `skills/session-start`, `skills/checkpoint`, `skills/session-close`; `skills/backlog` (owner
   amendment 2026-09-25, R24): runs `check` and `ready`, orients on one phase, never claims.

Prerequisite: `phase-plug-05` (the document scan that supplies documents, systems and owners).

## Acceptance and verification

As the backlog entry states. The case that must fail: two active phases sharing a system fail
`check` naming both; a `checkpoint` skill that could write `status: complete`.

## Execution order

Runs after phase-plug-05, alongside phase-plug-03 and phase-plug-06 (wave 3). `scripts/checks/backlog.py` is its module of the check dispatcher; it shares no path with a peer.

## Out of scope

The batch table protocol's tooling (`schemas/batch.schema.json`, `batches/`) — its document is
rewritten in `phase-plug-07`, its mechanism is not ported; the multi-session lock relay.

## Open questions

- Whether `ready` also prints the stale-claim signal. Planner, in this phase; leans yes, since it is
  one column in the same report.
