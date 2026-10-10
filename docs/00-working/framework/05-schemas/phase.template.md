# Backlog phase template

<!--
A phase is one session of work taken from a plan. It is not a document of its own: it is one
item in the backlog file (backlog.yaml), and the backlog file is the lock table agents read
before claiming work. This template shows one item on its own so its shape can be stated and
checked without the rest of the backlog.

Checked by phase.schema.json via check_schemas.py: the keys in the YAML block below must all be
properties the schema knows, and every field the schema requires must appear. Values are
placeholders and are not validated here; the check validates real phases from backlog.yaml.
-->

Copy the block into the backlog file's `items:` list and replace every `<...>` placeholder.

```yaml
- id: <phase-id>
  title: <one concrete outcome achievable in one session>
  plan: <plan-document-id>
  sources:
  - <requirement-document-id>
  systems:
  - <system-id>
  owner: <who answers for this phase>
  status: queued
  priority: <1-4>
  session_budget: 1
  depends_on: []
  scope:
  - <one bounded step>
  acceptance:
  - <an observable condition that must hold at completion>
  verification:
  - <a command or concrete check that shows whether the acceptance holds>
  deliverables:
  - <repository/path/the/phase/creates/or/changes>
  next_action: <the first useful step for whoever picks this phase up>
```

## Required fields

These are what the concurrency check and the completion check need. A phase missing any of them
fails the schema.

| Field | What it holds |
|---|---|
| `id` | Stable identifier, never renumbered. Names the claiming session's branch and worktree. |
| `title` | One outcome, achievable in one session. |
| `plan` | The plan document the phase belongs to. Write the plan before the phase. |
| `status` | `queued`, `active`, `blocked`, `deferred`, `complete` or `cancelled`. "Ready" is not a status: a queued phase is ready when every `depends_on` phase is complete. |
| `systems` | System identifiers the phase changes. At least one. Two active phases sharing a system cannot run at once. |
| `depends_on` | Phases that must be complete first. `[]` when there are none. |
| `scope` | The bounded steps the phase carries out. |
| `acceptance` | Observable conditions that decide completion. |
| `verification` | Commands or checks that show whether each acceptance condition holds. |
| `deliverables` | Repository paths the phase plans to create or change. Two active phases sharing a path cannot run at once. |

`systems`, `deliverables` and `depends_on` are the three declarations the lock reads. A phase that
declares them too narrowly can run beside a phase it collides with, so declare every path the
work touches before claiming.

## Optional fields

The schema checks these when present. They are the fields d-system uses beyond the core.

| Field | What it holds |
|---|---|
| `sources` | Other documents the phase draws on, such as its requirement. |
| `owner` | Who answers for the phase, as distinct from the agent that claims it. |
| `priority` | Queue order; lower runs first. |
| `session_budget` | Sessions the phase is expected to take. d-system fixes it at 1. |
| `next_action` | The first useful step for the next session. |
| `ideas` | Identifiers of captured ideas the phase acts on. |

An adopting repository may add fields of its own; the schema allows them.

The core is deliberately looser than d-system's own phase definition, the `items` entry in
d-system's `schemas/backlog.schema.json`. That definition requires every field in the required-fields
table plus `sources`, `owner`, `priority`, `session_budget` and `next_action` (not `ideas`), fixes
the identifier patterns (`phase-xxx-NN`, `doc-...`, `sys-...`) and requires at least two acceptance
conditions; this schema requires one. Every phase in d-system's backlog validates against this
schema, and `check_schemas.py` checks that it still does.

## Fields that depend on status

The schema enforces these:

| Status | Must have | Must not have |
|---|---|---|
| `active` | — (see below) | — |
| `blocked` | `blocked_reason`, `resume_when` | — |
| `deferred` | `blocked_reason`, `resume_when` | `agent`, `completion_evidence`, `result` |
| `cancelled` | `blocked_reason` | `agent`, `completion_evidence`, `result` |
| `queued` | — | `agent`, `completion_evidence`, `result` |
| `complete` | `session`, `completion_evidence`, `result` | — |

- `agent` is the claim. The schema does not decide when an active phase must name one: that is
  the host repository's concurrency rule. d-system requires an agent on every active phase only when
  more than one phase may be active at once (`max_active` above 1).
- `session` names the session record that completed the phase.
- `completion_evidence` lists paths that exist and prove completion. It is kept separate from
  `deliverables`, which are planned.
- `result` states the verification outcome actually observed, not the outcome hoped for.
