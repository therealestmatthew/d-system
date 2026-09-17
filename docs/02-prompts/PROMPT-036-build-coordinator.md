---
schema_version: 1
id: doc-build-coordinator
code: PROMPT-036
title: Build coordinator for the queued phase batches
kind: prompt
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-backlog, sys-governance]
depends_on: [doc-prompt-pack-protocol, doc-backlog-decisions, doc-irs-orchestrator-design, doc-idea-realization-system-plan]
---

# Build coordinator for the queued phase batches

The owner's kickoff prompt for a session that **builds** queued backlog phases, one batch at a
time, through dispatched agents, while the session itself stays a minimal-context coordinator.

It is deliberately **generic and idempotent**: the same prompt runs every batch, and every re-run
is a resume. The batch number is named at kickoff; nothing else changes between runs. A batch
interrupted halfway is resumed by pasting the same prompt with the same number — the tracker, not
the session's memory, carries state.

Revised 2026-09-16 against an adversarial review (2 blockers, 2 majors, 1 minor — all integrated)
and the owner's rulings on worktree granularity, the claim gate and blocker escalation.

The reasoning behind this pack's shape — why one worktree per phase, why questions are batched at
the open, why a blocker goes to an agent first — is recorded in
[GOV-013](../08-governance/GOV-013-coordinator-protocol.md), the coordinator protocol. Read that
before *changing* this pack; you do not need it to *run* the pack.

Paste everything below the rule into a fresh session in this repository, naming the batch.

---

## Mission

Build every phase in the named batch, in the listed order, to the point where each is verified,
integrated and complete. You are the **coordinator**: you sequence, you dispatch, you verify
evidence, and you hold almost nothing in your own context. **You build nothing yourself.**

## The batches

Twenty-nine phases in six batches. Each batch is dependency-closed — nothing in it depends on
anything in a later batch — and within a batch the listed order is a valid build order.

| Batch | Phases, in build order |
|---|---|
| 1 | `phase-part-02`, `phase-port-02`, `phase-ses-01`, `phase-irs-03`, `phase-irs-01` |
| 2 | `phase-auto-01`, `phase-auto-02`, `phase-irs-04`, `phase-irs-16`, `phase-part-03` |
| 3 | `phase-irs-14`, `phase-irs-11`, `phase-idg-01`, `phase-idg-10`, `phase-idg-11` |
| 4 | `phase-dgov-01`, `phase-idg-12`, `phase-irs-05`, `phase-irs-06`, `phase-irs-07` |
| 5 | `phase-irs-13`, `phase-irs-08`, `phase-irs-09`, `phase-irs-15`, `phase-agx-03` |
| 6 | `phase-irs-10`, `phase-irs-02`, `phase-irs-12`, `phase-irs-17` |

`phase-lit-09` sits in `next_up` and is **excluded from every batch** by the owner's instruction of
2026-09-16: it belongs to the literature-review campaign, has its own coordinator (`PROMPT-030`)
and resume command, and conflicts with `phase-lit-07`. Do not claim it. Do not remove it from
`next_up`.

**This partition was checked by script against `docs/09-backlog/backlog.yaml` when written, and
independently re-checked by a reviewer who wrote their own script rather than trusting this
sentence.** Both runs agreed: every one of the twenty-nine non-`phase-lit-09` `next_up` entries
appears exactly once, in `next_up`'s own order; every phase was `status: queued`; and every
`depends_on` edge resolved to an earlier or same-position phase in the global batch order, with the
two external dependencies (`phase-port-01`, `phase-part-01`) already `complete`.

**Verify the batch against the repository before starting anyway.** A phase already `complete` is
skipped and reported; a phase a peer has claimed is skipped and reported. The table is what was
true when written, not a promise about now.

**What the first run is for.** Five phases per batch is an estimate of what one coordinator can
carry, not a measured figure, and the unit run below has never been executed. Batch 1 is the
evidence for both. Record in the close-out what the batch size should actually be, and every place
the unit run did not survive contact with the real commands.

## Preflight

1. **Read all four of `AGENTS.md`'s *Concurrent agents* sections and `GOV-006`** before anything
   else — claim a phase, work in a worktree, complete and hand off, **and resolve collisions**. This
   run executes their hand-off procedure by hand, and the fourth section is the one you will need
   when a rebase fails or two phases touch `backlog.yaml`: nothing in this pack restates it.
2. In the primary checkout `/code/d-system`, on `dev`:
   `git status --short` (must be empty — never stash a peer's work), `git branch --show-current`,
   `git pull`, then `uv run python -m src.governance` and `uv run pytest`. **If the tree is dirty
   or either check is red, stop and report.** Building on a broken tree buries whose failure is
   whose.
3. Create `/code/d-system/_working/build-b<N>/` — gitignored, ungoverned, and **not** repository
   content — holding:
   - `tracker.md` — the run's memory: the batch list, then one line per phase (id, state
     `pending / claimed / built / verified / reviewed / merged / complete / skipped / blocked`, and
     a one-line verdict). **Re-read it instead of remembering.** A dead session resumes from it.
   - `decisions.md` — accumulated owner decisions (format below).
   - One evidence file per phase, `<phase-id>.md`, written by agents, never by you.
4. **Resume check.** If `tracker.md` exists, this is a resume: read it, confirm its claims against
   the repository, and continue from the first phase not `complete`. Never restart a phase the
   tracker says is built.

## Where work happens

**You have no worktree.** You run from the primary checkout on `dev`, which is where claim and
completion commits must land anyway, and you never switch its branch. Every worktree belongs to a
phase.

Per phase, exactly as `AGENTS.md` and `/session-start` require: branch **`agent/<phase-id>`**,
worktree **`../d-system-worktrees/<phase-id>`** — a sibling of the repository, never nested. Set up
its environment (`uv venv && uv sync --extra dev`, then `uv run python tools/rebuild_db.py`); never
symlink a peer's. If a phase needs a dev server, give it an explicit free port.

**Every path you hand an agent is absolute**, prefixed with that phase's worktree path. A relative
path in a dispatch is a defect: the primary checkout and every worktree contain the same paths, so
a relative reference can silently target the wrong tree — including the lock table on `dev`. Tell
every agent: *if you receive a relative repository path, stop and report it.*

## Authority, and four stated deviations

Nothing here is assumed. Each deviation is recorded, and each names what it displaces.

- **Completion.** You may mark a phase `complete` under `GOV-003`'s 2026-09-16 entry, *Coordinator
  completion replaces owner-invoked /session-close*, which superseded the earlier owner-only rule
  repository-wide. Its three conditions are restated in the unit run and are not optional.
- **`.claude/commands/session-close.md` and `.claude/skills/checkpoint/SKILL.md` still say a phase
  may only be completed by the owner.** That text is **knowingly superseded** by the same `GOV-003`
  entry, which names both documents as needing the owner's decision on their wording. Do not treat
  their contrary text as a blocker, and do not edit either file.
- **The per-phase claim gate.** `/session-start` step 2 requires an `AskUserQuestion` before every
  claim, stopping until answered. Per the same `GOV-003` entry, **the owner's approval of this
  batch is the claim approval for its phases.** You still check `max_active` and Conflicts
  numerically before each claim. Questions that gate would have raised are batched **before the
  first claim** — see *Open the batch* below.
- **`GOV-008` says the coordinator claims nothing and authors no prompts.** Here it claims, because
  that clause is written for packs with sub-orchestrators and this run has none, and the claim is a
  three-line lock edit that must be exact. And the **dispatch templates below are the prompts** —
  you instantiate a template against a phase's own fields, never compose one freehand. If a phase's
  entry cannot fill a template, that is a blocking finding, exactly as `GOV-008` intends.

**Unchanged and not yours:** the merge onto `dev` requires the owner's explicit yes, every phase,
with the diff in front of them. `next_up` ranking is the owner's — never reorder, add or remove.
You edit only the claimed phase's own backlog line plus the catalog `updated` date; a defect in
another phase or a governed document is a **decision for the owner**, never an edit.

## Agent hygiene

`GOV-008`'s *Agent hygiene* governs this run, in full force:

- Claim budgets and path locks checked **numerically** before claiming — the Conflicts column says
  nothing about the budget.
- Peers' claims and fenced paths are never touched; `AGENTS.md` and `CLAUDE.md` are never edited.
- **Validators receive the diff, the requirement text and the verification commands — never the
  creator's rationale, and never the creator's report.**
- Commit before validate; **truncated agents are resumed, not re-run**; an agent's assertion is
  verified against real output before you act on it.
- No agent dispatches another agent. No two agents write one file concurrently.

**Coordinator context discipline.** Never read a plan, requirement or phase body yourself. Agents
read; you route. You open only `tracker.md`, `decisions.md`, agents' returned summaries, and the
exact command output you must verify yourself. **Agents return at most 15 lines**: verdict, counts,
and the path of the file they wrote. If a return is longer, use the file.

## Cost protocols

Per `GOV-008`: **Haiku for mechanical gates. Sonnet is the standard model for judgment work. Opus
is never pre-assigned**, and is used at most as a single documented escalation for the whole batch,
only when absolutely necessary. **At most two fix cycles per phase** — what survives them is
reported, not looped on. The close-out reports spend posture: loop counts, any escalation, and
wall-clock against the runway.

## Open the batch

Before claiming anything, dispatch **one reconnaissance agent per phase, in parallel** — read-only,
each writing its phase's evidence file. Each reads its phase's entry and the documents its `plan`
and `sources` name, and reports: what the phase actually requires, whether every acceptance
condition is observable by a listed verification command, whether the deliverables cover the scope,
and **anything that would make a careful person decline to claim it**.

Then put every question they raise to the owner in **one batch** — `AskUserQuestion`, four at a
time, recommendation first in each option. This is the one scheduled interruption of the run. After
it, build.

## The unit run

For each phase in the batch, in order. This mirrors `PLAN-039.01` section 6, the design this loop
executes by hand until `phase-irs-08` builds it.

**1. Claim.** Re-run `uv run python -m src.governance --ready`. Check **numerically** that
`max_active` has room and the phase's Conflicts column is `—`. If a peer holds a conflicting system
or path, **skip the phase, mark it `skipped`, and move on** — the rejection is the answer, not an
obstacle. Otherwise claim it in the **primary checkout on `dev`**: edit only that phase's lines
(`status: active`, `agent: agent-<name>`), run `uv run python -m src.governance --catalog`, then
the validator, and commit claim and catalog together in one commit that changes nothing else.

**2. Cut the worktree.** `git worktree add -b agent/<phase-id> ../d-system-worktrees/<phase-id> dev`,
then set up its environment.

**3. Build.** Dispatch the **creator template**. It commits its own work on the branch.

**4. Validate.** Dispatch the **validator template** — the diff, the acceptance and the verification
commands, and nothing else. If it reports failures, re-dispatch the creator with the findings.
**Two fix cycles maximum**; what survives is recorded and reported, not looped on.

**5. Verify, yourself.** Run every command in the phase's `verification` list and keep the **real
output**. A failing check is a result to record, not a step to retry until quiet. An agent's claim
that a command passed is not evidence that it passed.

**6. Adversarial review.** Dispatch the **adversary template**. This is a `GOV-003` condition for
completion, not an optional extra. Its findings are fixed — within the two-cycle cap — or explicitly
reported as accepted, in the evidence file and the close-out.

**7. Hand off.** Write the phase's session record in its worktree (`--next-code session`), release
every `_tmpagent/` claim opened for it, then `git rebase dev` and re-run governance and `pytest`.
**This post-rebase run, against peers' merged work, is what decides whether the branch may
integrate.** Run `tools/check_no_private_content.py` with changes staged.

**8. Ask the owner to merge.** Present `git diff dev..agent/<phase-id> --stat`, the green
post-rebase output, the adversary's verdict, and the phase id. **Wait.** An unanswered question is
not a yes.

**9. Integrate, complete, clean up.** After the owner's yes: **copy any gitignored evidence out of
the worktree first**, then `git merge --ff-only agent/<phase-id>`, `git worktree remove`,
`git branch -d`. Then set `status: complete` on that phase on `dev`, regenerate the catalog, and
commit the two together as one small commit. Confirm all three `GOV-003` conditions held — green
verification with captured output, adversarial review resolved, owner-approved integration — and
record that in the tracker.

**10. Update `tracker.md`.** You are its only writer. Then take the next phase.

## Dispatch templates

Every dispatch opens with the idempotency sentence — *"Assess the current state of the repository
against the deliverables below; do only what is missing; report what already existed."* — names the
`general-purpose` charter, runs on **Sonnet** unless the owner said otherwise at kickoff, and
carries absolute paths only.

**Creator.** Give it: the phase id and title; the absolute path of `backlog.yaml` and the phase's
`- id:` anchor; absolute paths of the documents its `plan` and `sources` name; its `scope`,
`acceptance`, `deliverables` and `verification` verbatim; the worktree path; and the instruction to
commit its own work on the branch and stay strictly inside the declared `deliverables`. Tell it:
*if the work genuinely requires a file outside them, stop and report — never widen the declaration
yourself, and never edit a schema or a test to make a failing check pass.* ≤15-line return.

**Validator.** Give it: the worktree path, the commit range, and the phase's `acceptance` and
`verification` verbatim. **Nothing else** — not the creator's rationale, not its report. It runs
the commands, reads the diff against the acceptance, returns a ≤15-line verdict and its evidence
file path. It changes nothing.

**Adversary.** Give it: the worktree path, the commit range, the phase's `acceptance`, and the
instruction to assume the work is broken and hunt for where it fails when executed or merged —
acceptance satisfied in appearance only, deliverables overreaching the declaration, tests that
assert nothing, a green command that does not exercise the claim it stands for. Read-and-run only;
changes nothing; spawns no subagents. ≤15-line return plus its evidence file.

**Blocker resolver.** When the run meets a blocker, **give it to an agent before halting.** Hand it
the blocker, the evidence, the phase's entry and the relevant governing documents, and ask it to
establish what is actually true and what the options are. Only a blocker the resolver cannot settle
goes to the owner — with the resolver's findings attached.

## Decisions for the owner

When something needs a ruling rather than a fix, append it to `decisions.md`, grouped by phase,
`GOV-006` naming — title first, code as the handle:

```
### <Phase title> (`<phase-id>`, <plan title>)
Decision needed: <one sentence, concrete>
Options: <a> / <b> — recommended <x>, because <one clause>
Evidence: <phase-id>.md § <anchor>
```

**After the opening batch, do not interrupt the owner mid-run** except when a phase looks genuinely
wrong — an acceptance condition nothing can verify, a missing deliverable, an undeclared dependency
— or when a blocker survives the resolver. Everything else accumulates and comes at the end, ranked
by how much each answer changes. If the owner asks for decisions mid-run, present what has
accumulated and carry on.

## Runway and stopping

If the session approaches its limits: finish the in-flight phase through step 9, or stop cleanly
before step 1 of the next, bring `tracker.md` current, and stop. **An incomplete batch that resumes
cleanly beats a complete batch that lost its state.** Never leave a phase claimed-but-unbuilt
without saying so in the tracker — that is a lock nobody can see the reason for. If you must stop
with a claim held, say so explicitly in the report so the owner can release it.

## Close-out

1. `uv run python -m src.governance` and `uv run pytest` on `dev` — both green, real output kept.
2. Confirm no worktree or branch from this batch is left behind: `git worktree list`,
   `git branch --list 'agent/*'`.
3. Confirm every evidence file was copied out before its worktree was removed.
4. A batch session record: phases completed, skipped and blocked; decisions filed; spend posture
   per `GOV-008` — loop counts, any Opus escalation, wall-clock against runway.
5. Report to the owner: what completed, what did not and why, and the decisions awaiting them.

## Hard boundaries

- No `next_up` edits. No edits to another phase's backlog lines. No edits to `AGENTS.md`,
  `CLAUDE.md`, `session-close.md` or the checkpoint skill. No document-code allocation beyond the
  session records.
- Never integrate onto `dev` without the owner's explicit yes for that phase.
- Never mark a phase `complete` with any of `GOV-003`'s three conditions unmet.
- Never claim a phase whose Conflicts column is not `—`, and never claim past `max_active`.
- **Never edit a schema or a test to make a failing check pass.** A schema that rejects a change is
  telling you the change is wrong; report it.
- Never `git stash` a peer's uncommitted work, and never force an integration around it.
