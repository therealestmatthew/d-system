---
schema_version: 1
id: doc-prompt-queued-phase-review-pack
code: PROMPT-035
title: Queued phase review pack
kind: prompt
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-backlog, sys-governance]
depends_on: [doc-idea-realization-system-plan, doc-irs-orchestrator-design, doc-idea-realization-system-requirements]
---

# Queued phase review pack

The owner's kickoff prompt for a session that reviews, critiques and enhances every queued
phase in the idea-realization build queue, through a sequence of dispatched agents, while the
session itself acts as a **minimal-context orchestrator**. Written 2026-09-16, when `next_up`
carried four standing entries followed by the 23-phase realization queue (`phase-irs-*`, the
broker chain, the P1 foundations, `phase-agx-03`, `phase-part-03`). Re-derive the actual list
from `next_up` at run time; do not trust this paragraph over the file.

Paste everything below the rule into a fresh session in this repository.

---

## Mission

Review, critique and enhance **every queued phase from position 5 of `next_up` onward** (the
idea-realization build queue — skip the four standing entries ahead of it, and skip nothing
else). For each phase: an independent critique, then concrete enhancement of the phase's
backlog entry, then accumulation of every question that needs my decision. You are the
**orchestrator**: you dispatch agents, track their state, and hold almost nothing in your own
context. You do not review any phase yourself.

## Session mechanics (do these first)

1. Run `/session-start`. This is owner-directed work with no backlog phase: **unclaimed**,
   branch and worktree `agent/phase-review`. All edits happen in the worktree.
2. Create the working directory `_working/phase-review/` (gitignored, ungoverned) with:
   - `tracker.md` — one line per phase: id, dispatch state (`pending / reviewing / enhanced /
     blocked`), agent used, and a one-line verdict. This file is your memory; keep your
     context window nearly empty by re-reading it instead of remembering.
   - `questions.md` — the accumulating decision list (format below).
   - One file per phase, `<phase-id>.md`, written by the agents, never by you.
3. Derive the phase list: `uv run python -m src.governance --ready` plus the `next_up` block
   of `docs/09-backlog/backlog.yaml`. Write the list into `tracker.md`, in queue order, before
   dispatching anything.

## Orchestrator discipline — minimal context

- **Never read a plan, requirement or phase body yourself.** Agents read; you route. The only
  files you open are `tracker.md`, `questions.md`, and agents' returned summaries.
- **Agents return at most 15 lines** in their final report: verdict, counts, and the path to
  the full file they wrote under `_working/phase-review/`. If an agent returns more, use the
  file, not the transcript.
- **Update `tracker.md` after every dispatch completes**, before starting the next. If the
  session dies, the next session resumes from `tracker.md` with zero loss.
- **Batch by parent plan.** Dispatch one reviewer per plan-group, not per phase: the
  `phase-irs-*` group (its members that are queued), the broker pair (`phase-auto-01`,
  `-02`), the P1 group (`phase-idg-01`, `-10`, `-11`, `-12`), and the singletons
  (`phase-agx-03`, `phase-part-03`). A group's phases share sources; one agent reading them
  once is cheaper than six agents reading them six times. Process groups **in queue order**.
- Run dispatches for independent groups in parallel where the tool allows; never two agents
  on the same group.

## The agent sequence, per group

**Pass 1 — critique (read-only agent, one per group).** The agent reads each phase in the
group against: its `plan` document, its `sources`, `REQ-022` and `ARCH-006` (for `phase-irs-*`
and the broker pair), `PLAN-039.01` (for `phase-irs-01`, `-04`, `-08`, `-11`, `-14`, `-15`),
and the governance rules in `AGENTS.md`. For each phase it answers, with file-and-line
evidence:

- Is the scope actually one session? What would realistically not fit?
- Is every acceptance condition observable by a listed verification command? Name any that
  nothing can check.
- Do the deliverables cover what the scope requires — and nothing a peer's phase owns?
- Are `depends_on` and `systems` right? Anything missing, anything over-locked?
- Does the phase contradict its plan, its requirement rows, or a newer document?
- What detail is missing that the executing agent would have to invent? (This is the
  enhancement backlog.)
- What genuinely needs the owner's decision rather than a fix? (This feeds `questions.md`.)

The agent writes the full critique to `_working/phase-review/<group>.md` and returns the
15-line summary. It edits nothing.

**Pass 2 — enhance (write agent, one per group, after its critique returns).** The agent
receives the critique file's path and applies the **uncontroversial** fixes directly to
`docs/09-backlog/backlog.yaml` in the worktree: sharper scope bullets, missing acceptance
checks, corrected deliverables, added detail the critique named. Rules:

- It touches only the group's phases' lines. Never `next_up` order, never another phase,
  never a status field, never `AGENTS.md`/`CLAUDE.md`.
- Anything the critique marked as an owner decision is **left unchanged** and appended to
  `questions.md` instead — enhancement never resolves a question by picking an answer.
- After its edits: `uv run python -m src.governance` must exit 0. A validator rejection is
  fixed or the edit reverted; never left red.
- It appends its diff summary to the group's file and returns the 15-line summary.

**Pass 3 — adversarial sweep (one agent, at the end, across all groups).** After every group
is enhanced, dispatch one fresh read-only adversary across the full set of enhanced phases:
its brief is to find where the enhancements broke cross-phase coherence — duplicated
deliverables, dependency edges the edits invalidated, acceptance conditions two phases now
both claim. Findings go into `questions.md` if owner-level, or back to a targeted pass-2
re-dispatch if mechanical.

## The questions file

`questions.md` accumulates every owner decision, grouped by phase, each entry three lines:

```
### <phase-id> — <five-word topic>
Decision needed: <one sentence, concrete>
Options seen: <a> / <b> (recommended: <x> because <one clause>)
```

Do not interrupt me mid-run for any of these unless a question **blocks** an enhancement pass
(a genuine blocker: proceed-vs-stop, not preference). At the end, present the accumulated
questions through `AskUserQuestion` in batches of at most four, one batch at a time, ordered
by how much each answer changes — queue-order and dependency questions first, wording
questions last. Every batch carries recommendations.

## Verification and close

1. `uv run python -m src.governance` and `uv run pytest` in the worktree — both green, real
   output kept.
2. Staged run of `tools/check_no_private_content.py`.
3. A session record (`--next-code session`) summarizing: phases reviewed, phases enhanced,
   question count, and the tracker's final state. `_working/phase-review/` is referenced, not
   copied — it is gitignored and stays local; nothing in it is deleted without my approval.
4. Commit narrow diffs on the branch; **ask me before integrating into `dev`**, presenting
   `git diff dev..agent/phase-review --stat` and the questions batches. Marking any phase
   complete, and every `next_up` change, is mine alone.

## Hard boundaries

- No phase status changes, no claims, no `next_up` edits, no document-code allocation beyond
  the session record, no edits to governed documents other than `backlog.yaml` — if a critique
  finds a defect in a plan or requirement document, that is a **question**, not an edit.
- No agent dispatches another agent.
- If two agents would touch `backlog.yaml` at once, serialize them — pass 2 runs one group at
  a time.
- If the governance check is red at session start, stop and report; do not review on a broken
  tree.
