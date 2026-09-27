# Cloud prompt 1b: plan anatomy and plan folders, an investigation (idea 000505)

Run this in its own fresh cloud session, normally started by [`master-prompt.md`](master-prompt.md),
which picks it from [`status.md`](status.md). It is second in the order, after the planning protocol
document (prompt 1a) is merged into `dev`.

**Branch:** `agent/cloud-plan-anatomy` · **Handoff file:**
`docs/00-working/cloud-prompts/handoff-plan-anatomy.md`

## The task

A read-only investigation of how a plan is laid out today, followed by findings and a *proposed*
standard for plan folders. This is idea `000505` (re-investigate the anatomy of a plan and of a
plan folder). **Move, rename or delete no file.** The only files you add are under
`docs/00-working/plan-anatomy/`, plus the handoff file. Create no governed document and allocate
no code.

## Rules for a cloud session (read before anything else)

These rules hold for the whole session. Where this prompt and `AGENTS.md` disagree, `AGENTS.md`
wins, except where this prompt narrows what you may touch.

**What you can see.** You are working in a fresh clone of the repository from GitHub (`origin`).
You see only tracked files that have been pushed. You cannot see `_working/`, the local board, or
any other session, and you cannot message the Session Manager, Ideation or any other agent.
`_private/` is not in your clone. Never create, read or write anything under `_private/`.

**Setup.**

```bash
git fetch origin dev
git switch -c agent/cloud-plan-anatomy origin/dev
git config core.hooksPath tools/git-hooks     # the pre-commit hook does not install itself
command -v uv >/dev/null || pip install uv
uv sync --extra dev                           # without --extra dev the governance check cannot import jsonschema
uv run python -m src.governance               # baseline: must exit 0 before you change anything
```

Then check that every document this prompt names exists in your clone (`git ls-files | grep`). If
one is missing, `origin/dev` is behind the local `dev` this prompt was written against. Stop, ask
the owner (see *Questions*), and do not work from a guess.

**Where you work.** Your clone is your only checkout. Work on `agent/cloud-plan-anatomy` only. Never commit to
`dev`, never push `dev`, never merge anything into `dev`. Pushing `agent/cloud-plan-anatomy` to `origin` is
expected and needs no approval: `AGENTS.md` says backing up your own work is not publishing. Push
at least once before you finish.

**Tests.** Run `pytest`, `ruff`, `mypy` and the governance check only in this clone, on
`agent/cloud-plan-anatomy`. Never run them against the local primary checkout on `dev`; you have no access to it,
and nothing you write may tell anyone else to. Run one `pytest` at a time. Before each commit that
is not meant to change the catalog, run `git diff --exit-code docs/08-governance/catalog.md`. When
a commit does change governed documents or the backlog, regenerate the catalog with
`uv run python -m src.governance --catalog` and commit it in the same commit.

**Unclaimed work.** This is owner-directed work with no backlog phase. Make no claim commit and
change no existing phase's status. State at the top of every output document, and in the handoff
file, that the session ran unclaimed and no peer holds a lock against it.

**AGENTS.md applies.** In particular:

- Allocate every governed document's code with `uv run python -m src.governance --next-code <kind>`.
  Never pick a number by reading a directory. `--next-code` reserves codes only on the machine it
  runs on, so a local agent may take the same code before you merge. Name every code you
  allocated in the handoff file so the local Session Manager can check it against current `dev`.
- Never commit with `--no-verify`. If the pre-commit hook fails, fix the cause. If the check
  itself looks wrong, stop and put it in the handoff file as an open question.
- Never edit `AGENTS.md` or `CLAUDE.md`. If you think either is wrong, quote the passage and
  propose wording in the handoff file.
- Never write a confidential identifier into a tracked file. Run
  `uv run python tools/check_no_private_content.py` with your changes staged.
- Read `docs/08-governance/GOV-006-conversation-guidelines.md` once: name things before citing
  their codes, show real output when the output is the point, and say plainly when a correction
  is a correction.
- Write plainly. Say what you mean; no metaphor where a literal phrase exists.

**Ideas.** Do not record ideas. Do not run `tools/append_idea.py` and do not write
`_data/ideas.jsonl` by any route. When the owner names a new want, or you find one worth keeping,
add it to the handoff file's ideas list: one line each, bare, with the owner's own words in quotes
where they gave them. Local Ideation records them after the merge.

**Reading idea state.** Read ideas only through `fold()` in `src/db/ideas.py`, never from raw
`_data/ideas.jsonl`:

```bash
uv run python -c "
from src.db.ideas import fold, load_events; import json
s = fold(load_events())
for i in ['000505', '000501', '000502', '000500']: print(i, json.dumps(s.get(i), indent=1, default=str))"
```

**Questions.** Ask the owner with the AskUserQuestion tool, batched, one batch at a time, at the
point the work reaches the question. The owner may be on a phone: put drafts and long text in your
message, never in an option's preview. Ask when the answer changes what gets built. Otherwise
state the assumption, keep working, and list it in the handoff file. A question the owner has not
answered by the end goes in the handoff file's open-questions list.

**Adversarial review before you finish.** Dispatch the review on an agent type from
`.claude/agents/`, never `general-purpose`: `partition-adversary` unless this prompt names
another. Give it the brief this prompt specifies, with absolute paths in your clone
(`git rev-parse --show-toplevel`); in the briefs below, replace `{ABS}` with that path. Record every finding and its disposition (`fixed`,
`accepted-no-change` with the reason, `rejected` with evidence, or `escalated` for the owner). If
the agent type is not available in your session, do not substitute `general-purpose`. Say so in
the handoff file and leave the review as an open item.

**Gates at the end.** After your last content commit, bring the branch up to date and run all
four:

```bash
git fetch origin dev && git rebase origin/dev
uv run python -m src.governance        # must exit 0
uv run pytest                          # must pass
uv run ruff check src/ test/           # dev's baseline: 0 findings
uv run mypy src/                       # dev's baseline: 0 errors
```

A failing gate is a result. Record it with its output. Do not re-run a gate in the hope that it
passes. If you fix a cause and re-run, report both runs. If the rebase moved the catalog,
regenerate it and commit.

**Handoff file: this is your READY.** Finish by committing
`docs/00-working/cloud-prompts/handoff-plan-anatomy.md` on `agent/cloud-plan-anatomy` and pushing. No front matter. It
contains, in this order:

1. The line: *Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock
   against it.*
2. Branch and tip (`git rev-parse --short HEAD` after the final push), and the `origin/dev`
   commit you rebased onto.
3. What changed: every file added or modified, one line each.
4. Codes allocated with `--next-code`, if any.
5. Review verdict: the agent type and brief used, each finding (severity, one line) and its
   disposition.
6. The last ten lines of each of the four gate runs, verbatim.
7. Ideas for local Ideation, one line each.
8. Open owner questions and stated assumptions.

If you were started from `master-prompt.md`, update your row in `status.md` as its step 6 says,
in the same commit as the handoff file, after the gates.

The local Session Manager re-runs the gates and relays the merge to the owner. You do not merge.

## The owner's question, as given (2026-09-27)

> "we need to reinvestigate the anatomy of a plan that we created and look at the anatomy of a
> plan folder ... Should we have a separate document just to hold the decisions for the plan and
> should all plans be in a folder? No free form plan files or even if the plan is a single file to
> start, should it still be in a folder? The decision should be kept separate from the plan. So we
> can trace back to them, but the specific decisions and reasoning is only necessary for auditing,
> not for actually planning. We might need a separate file or folder for the various prompt packs.
> Do we put all of this in the plan folder? I think it's currently scattered throughout the
> repository. Maybe some more investigating to do here."

Read idea `000505` through `fold()` for the full record. Context ideas, also through `fold()`:
`000501` (archive one-time plans and prompts), `000502` (how requirements are generated),
`000500` (the planning protocol document). Prompt 1a writes that document and is merged before
this session starts, so read it if it is on `dev`. Do not amend it; list anything it gets wrong
in the handoff file.

## Read first

- `AGENTS.md`, especially "Key conventions" (governed vs ephemeral plans, `docs/00-working/`,
  `_tmpagent/`).
- `docs/08-governance/GOV-001-protocol.md`, `GOV-005-document-codes.md` (child codes such as
  `PLAN-050.01`), `GOV-010-plan-quality-standard.md` (which puts decisions inside the plan),
  `GOV-008-prompt-pack-protocol.md`, `GOV-018-three-altitude-review-procedure.md` (review records
  under `docs/08-governance/reviews/`), and `docs/04-decisions/ADR-010-idea-staging.md`.
- `docs/01-plans/PLAN-029-idea-graph-lifecycle.md` and phase `phase-idg-11` in
  `docs/09-backlog/backlog.yaml`. That phase is queued to define where a promoted plan lives
  before it earns a code. Its deliverables, `ADR-019` (promoted-plan staging decision) and
  `GOV-011` (promoted-plan staging protocol), are reserved in `docs/08-governance/catalog.md`
  and not yet written. Your proposal overlaps that phase. Say how, and do not take either code.

## Step 1: inventory (do this before forming any view)

Build the inventory from the repository, with the command for each count, into
`docs/00-working/plan-anatomy/inventory.md`:

1. **Every plan.** Each document with `kind: plan` (use the catalog or the front matter, not
   directory names): code, path, single file or folder, child plans, status, created date,
   whether it passes `GOV-010`'s entry check (the script in `GOV-018` step 1; plans created
   before 2026-09-22 are exempt).
   When this prompt was written, five plans were folders: `PLAN-003`, `PLAN-017`, `PLAN-023`,
   `PLAN-048` and `PLAN-050`. Verify this; do not copy it.
2. **What each folder holds** and how its files are named.
3. **Everything that belongs to a plan but lives outside it:** its requirement
   (`docs/06-requirements/`), decisions (inside the plan, ADRs in `docs/04-decisions/`, entries
   in `GOV-003-backlog-decisions.md`), prompt packs and prompts (`docs/02-prompts/`,
   `docs/00-working/`), review records (`docs/08-governance/reviews/`), session records
   (`docs/03-sessions/`), backlog phases, evidence files. For each, find how it is linked back to
   the plan (`depends_on`, the phase `plan` field, a code in prose, nothing). Pick at least five
   plans of different sizes and ages and trace every artifact for each.
4. **What you cannot see.** `_working/` is gitignored and not in your clone, and ephemeral plans
   live there. Say that the inventory excludes it.
5. **What depends on the layout.** Search `src/`, `tools/` and `test/` for code that finds plans
   by path or pattern (for example `docs/01-plans`, `PLAN-`, `glob`). A folder standard that
   breaks one of these is a cost to report.

## Step 2: findings

In `docs/00-working/plan-anatomy/findings.md`, answer each of the owner's questions from the
inventory, with evidence:

1. Should every plan be a folder, even when it is one file?
2. Should decisions be kept in a separate document from the plan, traceable from it? Note that
   `GOV-010` currently requires decisions in the plan (quote it), and what separating them would
   change for `GOV-018`'s entry check and for review.
3. Where should prompt packs, review records and session records for a plan live?
4. How scattered is it today? Give numbers from the inventory.

For each question, give at least two options with what each costs (files to move, tools and tests
to change, governance checks affected, links that break). Separate what the inventory shows from
what you recommend.

## Step 3: proposed standard

In `docs/00-working/plan-anatomy/proposed-standard.md`: a proposed layout for a plan folder, with
a worked example drawn from one real plan, the naming rule, and what stays outside the folder and
why. Mark it plainly as a proposal for the owner. List the owner decisions it needs, each with
your recommendation. List what adopting it would require (documents to amend, tools to change,
a migration of existing plans) as candidate work. Do not register phases or write a plan.

Ask the owner (batched) only if an answer would change what the inventory measures. Otherwise
state the assumption and continue.

## Adversarial review

Dispatch `partition-adversary` with this brief. The partition being audited is the inventory's
assignment of each artifact to a plan, and the proposal's division of files into in-folder and
out-of-folder.

> You are auditing an investigation at `{ABS}/docs/00-working/plan-anatomy/`. Assume it is wrong.
> You are read-only: do not edit, create or delete any file, and do not write
> `_data/ideas.jsonl`. Check: (1) **Coverage arithmetic.** Count every `kind: plan` document
> yourself and compare with the inventory. Report any plan missing, counted twice, or
> misdescribed as file or folder. (2) **Traceability claims.** For three plans of your choice,
> re-trace their artifacts and report any the inventory missed or linked wrongly. (3)
> **Costs.** For each option, check the claimed tool and test impact by searching `src/`,
> `tools/` and `test/`. Report any path dependency not mentioned. (4) **Overlap.** Compare the
> proposal with `phase-idg-11` in `docs/09-backlog/backlog.yaml` and with `GOV-010`; report
> contradictions the findings do not state. (5) **Evidence versus recommendation.** Report any
> recommendation stated as a finding. (6) **Scope.** Confirm no file outside
> `docs/00-working/plan-anatomy/` and the handoff file changed (`git diff --stat origin/dev...HEAD`).
> Rank each finding blocker, major or minor, with evidence.

Fix or disposition every finding.

## Kickoff for running this prompt directly

Normally the owner pastes the master prompt's kickoff instead. Use this one only to run this
prompt out of order, and only once every earlier row in `status.md` is merged.

Kickoff: you are running owner-directed, unclaimed work in a cloud clone of this repository. Run `git fetch origin dev`, then read `docs/00-working/cloud-prompts/plan-anatomy.md` from `origin/dev` (`git show origin/dev:docs/00-working/cloud-prompts/plan-anatomy.md`) and follow it exactly. It is a read-only investigation of plan anatomy and plan folders for idea 000505 (plan and plan-folder anatomy), on branch `agent/cloud-plan-anatomy`. It ends in findings and a proposed standard under `docs/00-working/plan-anatomy/` and moves no file. Tests run only in this clone on that branch, never on `dev`. Never commit to, merge into or push `dev`. Ask me questions with AskUserQuestion, batched, drafts in the message text and never in previews. Finish by pushing your branch with the handoff file the prompt describes.
