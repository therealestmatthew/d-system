---
schema_version: 1
id: doc-systems-review-prompt
code: PROMPT-003
title: Review every system for scope creep and unnecessary complexity
kind: prompt
status: active
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-backlog, sys-portfolio, sys-contracts]
depends_on: [doc-governance-protocol]
---

# Review every system for scope creep and unnecessary complexity

## How to use this

Open a fresh session in this repository and say:

> Read `docs/02-prompts/PROMPT-003-systems-review.md` and follow it.

The session's job is to **review and decide**, not to build. It ends with an ADR or two, backlog
phases for anything to be removed or simplified, and a written answer to each question below. It
should not end with new subsystems.

**Run [PROMPT-004](PROMPT-004-terminology-and-architecture.md) first.** This review argues about
complexity, and that argument needs shared vocabulary and an accurate map of what exists. Expect to
prune, consolidate or split some of what that session documents — that is the sequence working, not
duplicated effort.

**Then run this periodically** — after any stretch where several documents or systems were added, and
whenever the owner suspects the system is growing faster than the value it delivers.

## Why this exists

On 2026-09-06 a conversation about git internals produced course material, which acquired a project
record, a system entry, a plan document and two backlog phases inside a repository that exists to
manage consulting work. The course belonged in its own repository. It ended up governed here because
`schemas/backlog.schema.json` requires every item to carry a `plan`, a `systems` list, `verification`
and `deliverables` — so the only way to track the work was to manufacture the governance that made it
look native.

**The schema resisted, and the resistance was read as a cost rather than a signal.** That is the
failure mode this review exists to catch, and it will not be the last instance. See
[PLAN-015](../01-plans/PLAN-015-ephemeral-working-plans.md), which separates governed plans from
ephemeral ones.

## The standard to apply

For every system, document type, schema and folder, ask:

1. **What decision does it make cheaper?** A structure that organises without changing any decision
   is overhead wearing the costume of rigour.
2. **What breaks if it is deleted?** If the answer is "nothing, we would just have to remember", ask
   whether remembering was ever actually hard.
3. **Who is the audience?** Owner, agents, or a future reader. A document with no audience is
   ceremony.
4. **What did it cost to add, and what has it returned since?** Governance compounds — every new kind
   multiplies against every existing one.

Bias toward **removal**. This system is maintained by one person with agent help, not a team that
benefits from formalised handoffs.

## Part 1 — Explain the current system

Write these plainly, as if for someone who has never seen the repository. They are also the
explanation the owner has asked for, so accuracy matters more than brevity.

**The four content folders and why they differ:**

- `_data/` — git-tracked JSON, the source of truth for projects, people, commitments, tags.
  `tools/rebuild_db.py` projects it into `data/d_system.duckdb`, which is derived and gitignored. Currently holds the owner's
  real portfolio: named client engagements, personal finances, health.
- `_public/` — shareable outputs. Content intended to leave, or safe to.
- `_private/` — gitignored entirely. Credentials, raw dumps, personal notes. Never read or written
  unless the owner directs it.
- `_working/` — gitignored and **not scanned by governance**. Home for ephemeral working plans and
  task detail. Retained until the owner asks for it to go; no agent prunes it, per
  [PLAN-015](../01-plans/PLAN-015-ephemeral-working-plans.md).
- `_tmpagent/` — tracked and **not scanned by governance**. Files agents in sibling worktrees must
  read, since an ignored file never reaches a worktree. Read-only once active; claims are recorded
  and released in `_tmpagent/claims.jsonl` by convention, with no check enforcing it. Added
  2026-09-06 and holding no files yet — weigh it accordingly.

For each: state what decides whether a new file belongs there, and whether that rule is actually
unambiguous today. If two of these folders would accept the same file, say so.

**The backlog system:** `docs/09-backlog/backlog.yaml` holds phases, each carrying `plan`, `sources`,
`systems`, `status`, `priority`, `session_budget`, `depends_on`, `scope`, `acceptance`,
`verification`, `deliverables` and `next_action`. `next_up` overrides priority as an explicit queue.
Phases are grouped by track prefix (`cap`, `doc`, `gov`, `html`, `mem`, `priv`, `rel`, `scope`, `ses`, `sig`, `syn`, `term`, `tool`), glossed in
`docs/09-backlog/README.md` — confirm that list against the README rather than trusting this one.

Explain what a phase is *for*, why every field is required, and — the live question — whether the
required fields are right. Note that they make the backlog unable to hold anything that is not agent
work against a governed plan.

**The document system:** kinds, codes, series, the register in `codes.yaml`, the catalog, and the
governance check that enforces all of it.

## Part 2 — The questions to answer

Each needs a recommendation and a reason, not a survey.

1. **Where do the owner's personal action items live?** `SESS-2026-09-06-08` found that the backlog
   cannot hold them — no plan, no system, no deliverables — and that `schemas/task.schema.json`
   already covers the case with only `id`, `description`, `status` and `created` required. But
   `_data/tasks/` does not exist yet; it arrives with `phase-cap-07`. Confirm or reject that
   conclusion, and decide whether a task needs any parent at all.

2. **What belongs in this repository at all?** The git course did not. State the test. Candidate:
   *does this manage the owner's work, or is it work being managed?* Then apply it to everything
   currently here and name anything else that fails.

3. **Are nine document kinds too many?** `plan`, `adr`, `architecture`, `prompt`, `session`,
   `requirement`, `walkthrough`, `operation`, `governance`. For each, find a real instance and state
   what would have been lost had it been filed as something else. Kinds with no distinct instance are
   candidates for merging.

4. **Is the requirement-plan-phase chain earning its cost?** `AGENTS.md` requires a requirement
   document and a plan before non-trivial code. Several recent documents were written at direct
   owner instruction and recorded that deviation. If the process is routinely bypassed and the work
   is fine, the process is miscalibrated — decide whether to enforce it or narrow where it applies.

5. **Are sixteen systems tracking anything, or describing everything?** Several are `planned` or
   `scaffold` with no code. Decide whether `systems.yaml` is a live registry or an aspirational map,
   and prune to whichever it should be.

6. **What is the projection for?** DuckDB is rebuilt from JSON, but no application reads it — the
   FastAPI app is a stub and the React UI is a heading. Decide whether the query layer is earning its
   maintenance yet, or whether it is ahead of its consumers.

7. **Does the session-record practice pay for itself?** There are eight for one day. Ask what a
   future reader gets from them that `git log` does not.

## Part 3 — What to produce

- **An ADR per decision that changes the system.** Removal decisions get ADRs too; a thing deleted
  without a recorded reason gets re-added.
- **Backlog phases for the removals**, with the same rigour as additions.
- **A written answer to every Part 2 question**, including the ones where the answer is "leave it
  alone" — those are the ones that will be re-litigated otherwise.
- **A revision to `AGENTS.md`** if the review changes what agents must do.

## What this session must not do

- **Do not add a new system, kind, folder or schema.** If the review concludes something is missing,
  record it as a finding and let the owner decide in a separate session. A review that grows the
  system has failed at its own purpose.
- **Do not treat existing structure as load-bearing because it exists.** Age is not justification.
- **Do not defer to the volume of prior documentation.** That volume is the thing under review.
