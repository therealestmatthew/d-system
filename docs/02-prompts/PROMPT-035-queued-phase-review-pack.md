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
depends_on: [doc-idea-realization-system-plan, doc-irs-orchestrator-design, doc-idea-realization-system-requirements, doc-backlog-decisions]
---

# Queued phase review pack

The owner's kickoff prompt for a session that reviews, critiques and enhances every queued
phase in the idea-realization build queue, through dispatched agents, while the session acts
as a **minimal-context orchestrator**. First written 2026-09-16 and revised the same day
against an adversarial review (4 blockers, 11 majors, 7 minors — all integrated) and three
owner rulings: backlog-edit authority is **pre-authorized by this pack's approval** and
recorded in `GOV-003`; end-of-run decisions are **capped at three question batches** with the
remainder in a decisions document; dispatched agents run on **Sonnet per `GOV-008`** unless
the owner says otherwise at kickoff.

Paste everything below the rule into a fresh session in this repository.

---

## Mission

Review, critique and enhance the idea-realization build queue: **every entry in `next_up`
from `phase-irs-03` onward, identified by id, not by position**. For each phase: an
independent critique, then enhancement of its backlog entry, then accumulation of every
question that needs my decision. You are the **orchestrator**: you dispatch agents, track
their state, and hold almost nothing in your own context. You do not review any phase
yourself.

## Session mechanics (do these first)

1. Run `/session-start`. Owner-directed work, no backlog phase: **unclaimed**. Branch
   `agent/phase-review`, worktree `../d-system-worktrees/phase-review` (the sibling-directory
   convention — never a nested path). All edits happen in the worktree.
2. Preflight in the worktree: `uv run python -m src.governance` **and** `uv run pytest`. If
   either is red, stop and report — reviewing on a broken tree buries whose failure is whose.
3. Compute the worktree's absolute path once: `WT=$(git rev-parse --show-toplevel)`. **Every
   path you hand an agent is absolute, prefixed with that value** — `$WT/docs/09-backlog/backlog.yaml`,
   `$WT/_working/phase-review/…`. A relative path in a dispatch is a defect: the primary
   checkout and the worktree both contain every one of these paths, and a relative reference
   can silently target the wrong tree — including editing the lock table on `dev`. Tell every
   agent: *if you receive a relative repository path, stop and report it.*
4. Create `$WT/_working/phase-review/` (gitignored, ungoverned) with:
   - `tracker.md` — the run's memory: the frozen scope list, then one line per phase (id,
     group, state `pending / critiqued / enhanced / skipped-peer-claimed / blocked`, and a
     one-line verdict). Re-read it instead of remembering; a dead session resumes from it
     with zero loss.
   - `questions.md` — the accumulating decision list (format below).
   - One critique file per **group**, `<group>.md`, written by agents, never by you.
     `tracker.md` maps each phase to its group file.
5. **Freeze the scope**: read the `next_up` block of `$WT/docs/09-backlog/backlog.yaml` and
   write into `tracker.md` every entry from `phase-irs-03` onward, in order. That frozen list
   is the run's scope; nothing later re-derives it. Do **not** use `--ready` for scope — it
   hides `waiting` phases, which are half the mission.

## Authority — granted, bounded, re-checked

The owner pre-authorized this run, in approving this pack on 2026-09-16 (recorded in
`GOV-003`), to edit the backlog lines of the in-scope phases despite `AGENTS.md`'s
only-your-own-line rule — an unclaimed session touching ~23 unclaimed phases. The grant is
conditional on its safeguards:

- Before **each** pass-2 dispatch, re-run `uv run python -m src.governance --ready`. Any
  in-scope phase a peer has claimed since the freeze is marked `skipped-peer-claimed` in
  `tracker.md` and left untouched; skips are reported in the close-out.
- The grant covers in-scope phases' lines, the `backlog.yaml` top-level `updated` date (once,
  at the end), and the catalog regeneration those edits force. Nothing else: no `next_up`
  edits, no status or `agent` fields, no other phase, no other governed document — a defect
  found in a plan or requirement document is a **question**, never an edit. The session
  record and the decisions document (below) are the two documents this session may create.

## Orchestrator discipline — minimal context

- **Never read a plan, requirement or phase body yourself.** Agents read; you route. You open
  only `tracker.md`, `questions.md`, and agents' returned summaries.
- **Agents return at most 15 lines**: verdict, counts, and the path of the file they wrote.
  If a return is longer, use the file. If an agent stops with **no file written**, treat it
  as truncated: **resume that agent, never restart it** — a fresh agent re-pays the whole
  reading bill.
- **Update `tracker.md` after every dispatch completes.** You are `tracker.md`'s only
  writer; agents write only their own group file, and `questions.md` is written during the
  serialized passes, so no two writers ever share a file.
- **Dispatch conventions** (house style, per `PROMPT-034`): every dispatch opens with the
  idempotency sentence — *"Assess the current state of the repository against the
  deliverables below; do only what is missing; report what already existed."* — names its
  agent charter (`general-purpose`), runs on **Sonnet** per `GOV-008` unless I said otherwise
  at kickoff, and carries absolute paths only.

## Groups and order

Group by **governing document set and dependency tier** — the `phase-irs-*` track alone is
far too large for one dispatch. As of writing (verify each phase is in the frozen scope; drop
absentees silently):

| Group | Phases | The agents read |
|---|---|---|
| A `PLAN-039.01` graphs | `phase-irs-04`, `-14`, `-15` | `PLAN-039.01`, `PLAN-039`, `REQ-022`, `ARCH-006` |
| B foundations | `phase-irs-03`, `-01`, `-11`, `-13` | `PLAN-039`, `REQ-022`, `ARCH-006`; plus `PLAN-039.01` for `-01` and `-11`, which source it |
| C pipeline | `phase-irs-05`, `-06`, `-07`, `-08`, `-09` | `PLAN-039`, `REQ-022`, `ARCH-006`; plus `PLAN-039.01` for `-08` |
| D tail | `phase-irs-10`, `-02`, `-12` | `PLAN-039`, `REQ-022`, `ARCH-006` |
| E broker pair | `phase-auto-01`, `-02` | `PLAN-032`, `REQ-017` |
| F P1 foundations | `phase-idg-01`, `-10`, `-11`, `-12` | `PLAN-029`, `REQ-014`, `ARCH-005` |
| G anti-pattern store | `phase-agx-03` | `PLAN-031`, `REQ-016` |
| H partition close | `phase-part-03` | `PLAN-025`, `REQ-009` |

Every agent also reads each phase's own `plan` and `sources` fields and follows them — the
table is the floor, not the ceiling. Process groups **in the order of each group's first
member in the frozen scope list** (as of writing: B, E, A, F, C, G, H, D).

## The passes

**Pass 1 — critique (read-only, one agent per group; independent groups may run in
parallel).** For each phase, with file-and-line evidence:

- Is the scope actually one session? What would realistically not fit?
- Is every acceptance condition observable by a listed verification command?
- Do the deliverables cover the scope — and nothing a peer's phase owns?
- Are `depends_on` and `systems` right? Missing edges, over-broad locks?
- Does the phase contradict its plan, its requirement rows, or a newer document?
- What missing detail would the executing agent have to invent?
- What genuinely needs the owner's decision rather than a fix?

**Every finding is tagged `fix` or `question`** — that tag, not pass 2's judgment, is what
separates them. A defect found in an **out-of-scope** phase or document goes into the
critique file's `out-of-scope` section, tagged `question`. The agent writes
`$WT/_working/phase-review/<group>.md`, edits nothing, returns ≤15 lines.

**Pass 2 — enhance (write agent, one per group; starts only after every pass-1 return;
strictly one pass-2 dispatch at a time).** The agent receives its group's critique file path
and applies the `fix`-tagged findings to the group's phases' lines in
`$WT/docs/09-backlog/backlog.yaml`. `question`-tagged findings are copied into
`questions.md`, untouched in the backlog — enhancement never resolves a question by picking
an answer. After edits: `uv run python -m src.governance` exits 0, or the edit is corrected
or reverted — never left red. The agent appends its diff summary to the group file and
returns ≤15 lines.

**Pass 3 — adversarial sweep (one read-only agent, after all pass 2).** A fresh agent reads
the enhanced in-scope entries across all groups and hunts what the enhancements broke
*between* phases: duplicated deliverables, invalidated dependency edges, acceptance
conditions two phases now both claim. Mechanical breakage goes back as one targeted pass-2
re-dispatch; owner-level findings join `questions.md`, and it also marks any earlier question
its evidence resolves.

**After the final pass**: set `backlog.yaml`'s top-level `updated` to today, run
`uv run python -m src.governance --catalog`, then the full check pair.

## The questions file, and how decisions reach me

Each `questions.md` entry (grouped by phase, `GOV-006` naming — title first, code as the
handle):

```
### <Phase title> (`<phase-id>`, <plan title>)
Decision needed: <one sentence, concrete>
Options: <a> / <b> — recommended <x>, because <one clause>
Evidence: <group>.md § <anchor>
```

At the end: merge duplicates across phases, drop what pass 3 resolved, rank by how much each
answer changes. **The top questions — at most three `AskUserQuestion` batches of four, one
batch at a time, recommendation first in each option** — come to me in-session. Everything
remaining goes to `docs/00-working/phase-review-decisions.md` (ungoverned staging, per
`ADR-010`), committed on the branch, for a dedicated sitting. Do not interrupt me mid-run
except for a genuine blocker — proceed-vs-stop, not preference.

## Verification and close

1. `uv run python -m src.governance` and `uv run pytest` in the worktree — both green, real
   output kept. A failure here is a result to report, not to retry until quiet.
2. Staged run of `tools/check_no_private_content.py`.
3. **Copy the evidence out before any cleanup**:
   `cp -r "$WT/_working/phase-review" /code/d-system/_working/phase-review` — the directory
   is gitignored, a merge never carries it and `git worktree remove` destroys it. The session
   record cites the primary-checkout copy. Nothing under `_working/` is ever deleted without
   my approval.
4. A session record (`--next-code session`): phases reviewed and enhanced, skips, question
   counts (asked vs. filed), and the tracker's final state.
5. Commit narrow diffs on the branch; **ask me before integrating into `dev`**, presenting
   `git diff dev..agent/phase-review --stat`, the three question batches, and the path of the
   decisions document.

## Hard boundaries

- No phase status changes, no claims, no `next_up` edits, no document-code allocation beyond
  the session record, no edits to any governed document except the authorized `backlog.yaml`
  lines. The session record and the ungoverned decisions document are the only files this
  session creates outside `_working/`.
- No agent dispatches another agent. No two agents write one file concurrently.
- **Runway**: if the session approaches its limits, finish the in-flight dispatch, bring
  `tracker.md` current, commit, and stop — the next session resumes from the tracker. An
  incomplete run that resumes cleanly beats a complete run that lost its state.
