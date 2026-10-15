---
schema_version: 1
id: doc-planning-mode
code: OPS-002
title: Planning mode
kind: operation
status: draft
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: []
depends_on: []
---

# Planning mode

How a captured idea becomes an approved plan, registered backlog phases and a validated, assigned
batch. This guide gives the order of the steps, what each step takes and produces, and who decides
at each gate. The rules themselves are in the plugin's protocol documents, which this guide points
to rather than repeats:

- `plugins/idea-realization/docs/role-contracts.md`: what each role receives, produces and never
  does, and the decisions reserved to the owner (section 1);
- `plugins/idea-realization/docs/plan-review.md`: the plan review (sections 1 to 3);
- `plugins/idea-realization/docs/backlog-protocol.md`: phases, `next_up` and splitting
  (sections 2, 4, 5 and 14);
- `plugins/idea-realization/docs/batches.md`: batches and their check.

The one-page list of commands for this mode is in the mode cheat sheets (`OPS-009`). How the team's
day is organised around it is in the team workflow (`OPS-005`).

## Starting

Run `/start` and choose Planning. Then, in the control repository's primary checkout on `dev`:

1. `git pull` origin `dev`, before any work (`OPS-001`, section 2).
2. Load what is already decided: the `brain` skill, or
   `uv run plugins/idea-realization/scripts/brain.py load --kind decision`.

Plugin skills are invoked as `/idea-realization:<skill>`. Agents are dispatched by name as their own
agent type, never as a general-purpose agent. Scripts run from the control repository's root with
`IDEA_REALIZATION_ROOT` set to it (`OPS-008`, "check.py reports files from the wrong repository").

## Where the work is committed

| What | Where it goes |
|---|---|
| Idea log entries (new ideas, status moves, findings) | Directly on control `dev` and pushed at once. Idea commits are bookkeeping (`OPS-001`, section 3). |
| Accepted partition record, requirement, plan, new phases in `backlog/backlog.yaml`, batch record in `backlog/batches.yaml`, regenerated catalog | A control worktree on a branch `agent/<handle>-<slug>`, reaching control `dev` through a pull request merged with a merge commit (`OPS-001`, sections 1 and 4). |

## The steps

| # | Step | Tool | Input | Output | Who decides |
|---|---|---|---|---|---|
| 1 | Ideation | `idea` skill | An idea as someone states it | A new `open` entry in the idea log | Anyone records. Approving an idea is the owner's. |
| 2 | Triage | `idea-triage` skill, which dispatches the `idea-triage` agent | One `open` idea | A finding annotation on the idea; status `triaged` | No owner gate. The skill moves the idea only after it has verified the finding landed on the right idea. |
| 3 | Partition | `partition-ideas` skill, with the `partition-analyst` and `partition-adversary` agents | The triaged ideas | A proposed partition into tracks, then an accepted partition record under `ideas/partitions/` | The owner, at four stops: the open-set gate and gates 1, 2 and 3. Acceptance of the partition is the owner's. |
| 4 | Code reservation | `next-code` skill (`plan`, and `requirement` for a new plan) | An accepted track the owner sends to planning | Reserved codes | Whoever decided the track becomes a plan reserves the codes before the planner runs. Never choose a code by hand. |
| 5 | Planner | `idea-planner` agent (runs on Opus) | One accepted track, its disposition (new plan or amendment), the reserved codes | `status: draft` requirement and plan, with the phase table already split into one-session phases | No decision. The planner never approves its own draft. |
| 6 | Plan check | `plan-check` skill (`scripts/plan_check.py`) | The plan draft | Pass (exit 0) or returned (exit 1) with the missing sections | Mechanical. A plan returned twice goes to the owner. |
| 7 | Plan review | `plan-adversary` agent, once per altitude | The plan, its requirement, and the filled prompt from `plugins/idea-realization/docs/adversary-prompt.md` | Findings and a `VERDICT pass` or `VERDICT fail` line per altitude, recorded in the review record | The planner dispositions each finding. The owner rules on escalated findings and **approves the plan** (`status: approved`) at the plan-approval gate. |
| 8 | Phase split | `phase-splitter` agent | The approved plan and its dispositioned review record | A proposal under `<staging_dir>/phase-split/<plan-code>/`: candidate `backlog.yaml` and `batches.yaml`, and `proposal.md` with phases, stages and a proposed `next_up` | No decision. A phase it splits goes back to `plan-adversary` at the phase altitude. After a second check rejection it stops and goes to the owner. |
| 9 | Batch validation | `batch-validator` agent and `scripts/batch_check.py` | The batch id and the backlog and batches files (the candidates from step 8, or the real files) | Command output, ranked findings, `VERDICT pass <batch-id>` or `VERDICT fail <batch-id>` | No decision. A `pass` is evidence for the owner, not approval. |
| 10 | Assignment | The owner edits `backlog/backlog.yaml` and `backlog/batches.yaml` | The validated proposal | Phases registered; `next_up` ranked; `owner: <handle>` on each phase; batch `status: approved` with its check recorded | The owner. Composing a batch, ranking `next_up` and assigning developers are the owner's decisions. |

### 1. Ideation

`/idea-realization:idea` records the idea as given, through the plugin's writer, and re-renders the
idea view. Record one idea per distinct ask. Do not edit `ideas/ideas.jsonl` by hand, and read an
idea's current state with `uv run plugins/idea-realization/scripts/idea.py show <id>`, never from
the raw log.

### 2. Triage

`/idea-realization:idea-triage <id>` handles one open idea per run. If no id is given it lists the
open ideas and asks which one. It dispatches the `idea-triage` agent with the literal write command,
re-reads the idea to confirm the finding is on the right idea, and only then moves the idea to
`triaged`. It never moves an idea past `triaged`.

### 3. Partition

`/idea-realization:partition-ideas` builds the corpus, dispatches two analysts and two audits, and
writes one proposed partition. It stops for the owner:

- at the open-set gate, when open ideas exist: triage them first, or partition without them;
- at gate 1, after the analysts report;
- at gate 2, after the first audit;
- at gate 3, where the owner accepts or corrects the partition and rules on each decline candidate.

Only on the owner's acceptance does `idea_corpus.py accept` copy the record into the partitions
directory with `state: accepted`. The skill moves no idea's status. Each accepted track carries a
disposition: a new plan, or an amendment to a named existing plan.

### 4 and 5. Codes, then the planner

Reserve the codes first with `/idea-realization:next-code plan` (and `requirement` for a new plan).
Then dispatch the `idea-planner` agent with the accepted track and the reserved codes. It refuses to
work from a partition still in proposal, from a track without a disposition, or without a reserved
code. It writes the requirement under `docs/requirements/` and the plan under `docs/plans/`, both
`status: draft`, and runs the plan check on its own draft before it reports.

### 6 and 7. Plan check and plan review

`/idea-realization:plan-check <plan path>` is the entry check: it reads headings only. On a pass,
dispatch `plan-adversary` with the prompt from `adversary-prompt.md`, once per altitude, every
placeholder filled with an absolute path:

- **plan**: the plan against its requirement;
- **phase**: each queued or blocked phase of the plan, in isolation;
- **later-added-phase**: phases added after the plan's original set, against the plan as it stands.
  Once any later-added phase exists this altitude runs even when the other two came back clean.

The session that dispatches the review records every finding, unchanged, in its session record
under `## Review` (`plan-review.md`, section 3, steps 4 and 5). The planner writes a disposition on
each: `fixed`, `accepted-no-change`, `rejected` or `escalated`. There is one revision cycle; a
blocker still open after it is escalated.

**Gate: plan approval.** The owner reads the plan, the review record and the escalated findings,
writes dispositions on the escalated ones, and approves the plan by setting `status: approved`.
Nothing later in this guide runs on a draft plan.

### 8. Phase split

Dispatch the `phase-splitter` agent with the repository root, the approved plan's code and path,
its requirement, the dispositioned review record and the output directory
`<staging_dir>/phase-split/<plan-code>/` (`paths.py` prints `staging_dir`; it is gitignored). It:

- reuses existing phases that already cover part of the plan;
- writes one-session phases with every field the backlog schema requires, `status: queued`, no
  `agent`, and `owner` set to the plan's owner;
- maps `depends_on`, computes stages, and records prerequisites outside the plan as
  `external_dependencies`;
- runs `check.py` and `batch_check.py` against its candidate files and pastes their output into
  `proposal.md`.

It never edits the real backlog or batches file, never ranks `next_up` and never assigns a
developer. Phases it split go back to `plan-adversary` at the phase altitude before step 9.

### 9. Batch validation

Dispatch the `batch-validator` agent with the root, the batch id and, for a proposal, the
candidate files from step 8. It runs, from the root with `IDEA_REALIZATION_ROOT` set to it:

```bash
uv run plugins/idea-realization/scripts/batch_check.py --backlog-path <candidate backlog> \
  --batches <candidate batches> <batch-id>
uv run plugins/idea-realization/scripts/check.py --feature backlog --feature batches \
  --backlog-path <candidate backlog>
```

`batch_check.py` exits 0 when the composition is clean, 1 when it lists problems, and 2 when a file
could not be read or the batch does not exist. The agent then judges what the script does not: that
the batch record restates no phase content, that each stage boundary rests on a real edge or
collision, that a stage wider than the free active slots will run serially, and that each phase
fits one session. It ends with `VERDICT pass <batch-id>` or `VERDICT fail <batch-id>`.

### 10. Assignment

The owner, on the planning branch:

1. Copies the accepted phases into `backlog/backlog.yaml` (only the new phases, not the candidate
   file as a whole) and the batch into `backlog/batches.yaml`.
2. Ranks `next_up`. The splitter's order is a proposal only (`backlog-protocol.md`, section 4).
3. Sets `owner: <handle>` on each phase to assign it to a developer. Anyone may still claim the
   phase; the check prints a warning when the claimant is not the phase's owner and never refuses
   the claim (`OPS-005`, "Assignment").
4. Sets the batch's `status: approved` and adds an entry to its `checks` list from a fresh run of
   `batch_check.py <batch-id>` against the real files: `date`, `result`, `backlog_commit` and the
   output verbatim. The batch-validator never writes this entry; the planning session does.
5. Runs `/idea-realization:catalog`, then
   `IDEA_REALIZATION_ROOT=$PWD uv run plugins/idea-realization/scripts/check.py`, and inspects plan
   coverage with `uv run plugins/idea-realization/scripts/cli.py ready --all` (its "Source plan
   coverage" table): every draft, approved or active plan is covered by at least one phase.

The branch then goes to control `dev` through a pull request (`OPS-001`, section 4).

## When planning mode ends

Planning mode for a plan ends when all of these hold:

- the plan is `status: approved`, with every review finding dispositioned;
- its phases are registered in `backlog/backlog.yaml` on control `dev`;
- `check.py` passes on control `dev`;
- each batch is `status: approved` in `backlog/batches.yaml`, with a recorded passing check;
- each phase the owner wants built next is in `next_up` with an `owner: <handle>`.

From there the work moves to implementing mode (`OPS-003`).

## What planning mode never does

- No agent approves an idea, accepts a partition, approves a plan, ranks `next_up`, composes a
  batch or assigns a developer. Those are the owner's (`role-contracts.md`, section 1).
- No step chooses a document code by hand.
- No step claims a phase. Claiming happens in implementing mode.
