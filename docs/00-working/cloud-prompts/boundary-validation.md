# Cloud prompt 2: independent validation of the system boundary study

Run this in its own fresh cloud session, normally started by [`master-prompt.md`](master-prompt.md),
which picks it from [`status.md`](status.md). It is third in the order, after prompts 1a and 1b are
merged into `dev`.

**Branch:** `agent/cloud-boundary-validation` · **Handoff file:**
`docs/00-working/cloud-prompts/handoff-boundary-validation.md`

## The task

The system boundary study asked whether this repository should stay one repository or split. It
ran as five phases (`phase-bnd-01` to `phase-bnd-05`, all complete) and ended in a draft decision
report with three options: A (keep one repository with explicit contracts, recommended), B
(prepare selective extraction) and C (split now, rejected). The owner chooses A, B or C **after**
this validation, so its job is to tell the owner whether the evidence and reasoning hold.

You do four things:

1. **Re-derive the study's figures** from the current repository and report every one that
   differs.
2. **Attack its reasoning** at plan altitude through the three-altitude review procedure
   (`GOV-018`), and at phase altitude in the validation report.
3. **Act as PLAN-050's planner** (owner's ruling, 2026-09-27): disposition every finding, and
   revise the plan for completeness and next steps, including backlog phases for the next steps.
4. **Re-assess options A, B and C** against the corrected evidence. Do not choose. The owner
   decides.
5. **Build one HTML page** that shows the key systems and the study's findings visually
   (Step 6). This is a requirement of this prompt, not an option.

The documents:

- `docs/07-architecture/ARCH-012-system-boundary-decision-report.md`: the draft decision report
- `docs/06-requirements/REQ-033-system-boundary-study.md`: the study's requirements (R01 to R07)
- `docs/01-plans/PLAN-050-system-boundary-study/`: the plan overview and children `PLAN-050.01`
  to `PLAN-050.05`
- `docs/00-working/boundary-study/`: the evidence files, including `phase-status.md`
- The session records the phases name (`SESS-2026-09-26-03` to `-07`, in `docs/03-sessions/`)

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
git switch -c agent/cloud-boundary-validation origin/dev
git config core.hooksPath tools/git-hooks     # the pre-commit hook does not install itself
command -v uv >/dev/null || pip install uv
uv sync --extra dev                           # without --extra dev the governance check cannot import jsonschema
uv run python -m src.governance               # baseline: must exit 0 before you change anything
```

Then check that every document this prompt names exists in your clone (`git ls-files | grep`). If
one is missing, `origin/dev` is behind the local `dev` this prompt was written against. Stop, ask
the owner (see *Questions*), and do not work from a guess.

**Where you work.** Your clone is your only checkout. Work on `agent/cloud-boundary-validation` only. Never commit to
`dev`, never push `dev`, never merge anything into `dev`. Pushing `agent/cloud-boundary-validation` to `origin` is
expected and needs no approval: `AGENTS.md` says backing up your own work is not publishing. Push
at least once before you finish.

**Tests.** Run `pytest`, `ruff`, `mypy` and the governance check only in this clone, on
`agent/cloud-boundary-validation`. Never run them against the local primary checkout on `dev`; you have no access to it,
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
for i in ['000500']: print(i, json.dumps(s.get(i), indent=1, default=str))"
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
`docs/00-working/cloud-prompts/handoff-boundary-validation.md` on `agent/cloud-boundary-validation` and pushing. No front matter. It
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

If you were started from `master-prompt.md`, update your row in `status.md` as it says, in the
same commit as the handoff file.

The local Session Manager re-runs the gates and relays the merge to the owner. You do not merge.

## What the owner ruled for this session (2026-09-27)

- **Phase altitude.** All five `PLAN-050` phases are complete, and `GOV-018` step 2 reviews only
  `queued`, `waiting` or `blocked` phases. So the review record covers the plan altitude with an
  empty `target.phases` and a stated reason. The phase-level attack on the five completed phases
  still runs. It goes in the validation report instead of the record.
- **You act as the planner.** You write the planner dispositions in the review record
  (`by: planner`), revise the plan, and set `status: dispositioned` when every finding has one.
  What you cannot resolve after one revision cycle is `escalated-g3`, for the owner.
- **Enhance the plan for completeness and next steps.** All of the following are in scope:
  - revise `PLAN-050` and its children to close the completeness findings;
  - add a next-steps section giving the follow-up work under each of options A, B and C;
  - register backlog phases for those next steps (see Step 5);
  - correct directly in `ARCH-012` any figure that is simply wrong. A change to `ARCH-012`'s
    reasoning, options or recommendation is **not** a figure correction. Propose it in the
    validation report instead.

## Read first

`AGENTS.md`; `GOV-018` in full; `docs/02-prompts/PROMPT-038-single-adversary-engine.md`;
`docs/08-governance/GOV-010-plan-quality-standard.md`; `GOV-002-backlog-protocol.md` (phase
fields and statuses); `schemas/adversarial-finding.schema.json`; one existing record for shape,
for example `docs/08-governance/reviews/2026-09-27-plan-052.json`; then the study documents
above.

## Step 1: re-derive the figures

For each figure, find the evidence file and baseline commit the study used. Derive the figure at
that commit (`git show <commit>:<path>`, `git worktree add` in a scratch directory outside the
clone, or `git grep <commit>`) **and** at your `origin/dev` tip. That separates a study error
(wrong at its own baseline) from drift (right then, changed since). Record each command.

| Figure in `ARCH-012` | What to count |
|---|---|
| 40 governed prompts | documents with `kind: prompt` |
| entry-point split 13 / 14 / 12 / 1 (direct operational entries or planning starts / sequence steps / owner-launched campaigns / no known entry) | re-apply the rubric in `docs/00-working/boundary-study/prompt-classification-rubric.md` to each prompt yourself; do not copy `prompt-corpus-inventory.md` |
| registry: 17 implemented, 4 scaffold, 21 planned, 1 retired | systems in `docs/08-governance/systems.yaml` by their `status` field |
| "the current four-slot claim limit is fully occupied" | `max_active` in `docs/09-backlog/backlog.yaml` and the phases with `status: active` |

Also check every other number and factual claim in `ARCH-012` and the evidence files that can be
checked by a command. A figure that is wrong at the study's own baseline is a study error:
correct it in `ARCH-012` and record the old and new value. A figure that has only drifted is not
an error. Report it with both values and do not edit it. Before calling any figure wrong, re-read
the method the study documented for it: a figure that will not reproduce usually means your
counting rule differs from its rule. State the rule difference.

## Step 2: the GOV-018 review at plan altitude

Follow `GOV-018` steps 1 to 5 exactly, with these specifics:

- **Entry check** (step 1): run the script on
  `docs/01-plans/PLAN-050-system-boundary-study/PLAN-050-overview.md`. `PLAN-050` was created
  2026-09-26, so it is not exempt. If it returns, write the returned record as step 1 says,
  using `review_id` `<date>-plan-050-entry`. Then, as planner, add the missing sections, re-run
  the check, and continue.
- **Target** (step 2): the plan altitude is the overview and its requirement `REQ-033`.
  `GOV-018` says a child plan gets its own review. Six separate reviews do not fit one session,
  so the adversary reads the five children as part of the plan. The schema's `target` has a
  single `plan` field (`PLAN-050`), so name the five children, and this departure from `GOV-018`,
  in the record's `notes`. List separate child reviews as an open owner question.
  `target.phases` is empty; give the reason above in `notes` too.
- **Dispatch** (step 3): `partition-adversary` with `PROMPT-038` filled in for the `plan`
  altitude, every path absolute in your clone. Add to its brief: re-derive the four figures
  above independently of you, and attack whether the evidence supports rejecting C and
  recommending A.
- **Record** (step 4): `docs/08-governance/reviews/<date>-plan-050.json`, findings copied
  unedited. Validate with `uv run pytest test/test_adversarial_finding_schema.py`.
- **Dispositions** (step 5): as planner. One revision cycle. `fixed` names where the plan
  changed.

## Step 3: the phase-level attack (validation report)

For each of `phase-bnd-01` to `phase-bnd-05`, apply `PROMPT-038`'s six phase checks in
retrospect. Also ask whether the phase's evidence file satisfies the `REQ-033` row it claims (R01
to R07), and whether its session record's stated results match the evidence. You may run this
yourself, or dispatch `partition-adversary` with `PROMPT-038`'s phase section and this
retrospective framing. Findings go in the validation report, not the record.

## Step 4: the validation report

Write `docs/00-working/boundary-study/validation-report.md` (ungoverned, no front matter). Start
with the unclaimed line. Then:

1. A summary: whether the study's conclusion holds, in three sentences.
2. The figures table: each figure, the study's value, the value at the study's baseline, the value
   at your tip, and one of *correct*, *drift* or *error*, with the command used.
3. The plan-altitude findings and their dispositions, pointing to the record.
4. The phase-level findings.
5. Options A, B and C re-assessed. For each: what the corrected evidence says for and against,
   and what would have to be true to choose it. Do not recommend a different option unless the
   evidence requires it, and then say which evidence.
6. Proposed changes to `ARCH-012` that go beyond figures, each with the passage quoted and
   replacement wording.
7. What you changed in `ARCH-012` and `PLAN-050`, one line each.
8. A link to the HTML overview (Step 6).

## Step 5: next steps and backlog phases

Add a next-steps section to the `PLAN-050` overview: the follow-up work under each option. Then
register backlog phases for it. Before you do, ask the owner (batched with any other question
that has come up) whether to register phases for all three options or only for option A. The
owner said "all of the above" to registering phases without choosing between these two. Your
recommendation is all three, so no option is favoured before the decision.

For each phase:

- Use the next free `phase-bnd-NN` id (check `backlog.yaml`) and `plan: doc-system-boundary-study`.
- Fill every field `GOV-002` requires, including `systems`, `deliverables`, `scope`,
  `acceptance` (with at least one case that must fail, per `GOV-010` P6), `verification` and
  `depends_on`.
- Make sure none of them can be picked up before the owner decides. Use a status that
  `--ready` does not offer, with `blocked_reason` and `resume_when` naming the owner's A/B/C
  decision in `ARCH-012`. Check `GOV-002` for which status fits: `deferred` probably fits. If
  the validator rejects it, report the output and ask the owner. Do not add them to `next_up`.
- Size each to one session. Split where it does not fit.
- Run `uv run python -m src.governance`, and `--ready` to confirm none is offered.

These phases are later-added phases of `PLAN-050`. Dispatch `partition-adversary` once more with
`PROMPT-038` for the `later-added-phase` altitude over them, append the findings to the same
review record (`target.later_added_phases`, `altitudes_run`), and disposition them. `GOV-018`
step 2 reviews only `queued`, `waiting` or `blocked` phases at this altitude, and these are
`deferred`. Reviewing them anyway is a departure from the procedure: state it, with the reason
(they must not be offered by `--ready` before the owner decides, and they still need review), in
the record's `notes` and in the validation report. This dispatch
counts as the adversarial review of your own backlog work.

## Step 6: the HTML overview (required)

Write `docs/00-working/boundary-study/boundary-overview.html`: one self-contained page the owner
can open to see the system boundary at a glance before deciding A, B or C. It must look
professional and be easy to read. It must be concise: short labels and captions, with prose only
where a diagram needs it to be understood (what each concern owns, what each option commits to).
Its content comes from the validation report and the corrected figures, never from the study's
uncorrected numbers.

**Required content**, each as a diagram or visualization with a one-line caption:

1. **Concern map:** the three cores (personal productivity, idea realization, workbench), the
   governance/framework layer, and the adjacent and incubating systems, with each registered
   system from `systems.yaml` placed in its concern.
2. **Crossings:** the allowed interfaces between concerns as labelled edges (what data or
   capability crosses), with the prohibited ownership crossings marked.
3. **Registry maturity:** implemented, scaffold, planned and retired counts, overall and per
   concern.
4. **Prompt entry points:** the 40-prompt (or corrected) split by entry-point class.
5. **Backlog and claim load:** phases by status, and active claims against `max_active`.
6. **Options A, B and C:** a side-by-side comparison of what each keeps together, what it
   separates, its cost and its extraction trigger, with the study's recommendation and your
   re-assessment both shown, clearly labelled as such. The page does not choose.
7. **Figures check:** the study's value, the value at your tip, and the verdict (*correct*,
   *drift*, *error*) for each figure.
8. **Next steps:** the deferred phases for each option.

**Required form:**

- Self-contained: inline CSS and inline SVG only. No external scripts, stylesheets, fonts or
  images, so it renders offline from a clone.
- A header with the title, the `origin/dev` commit the figures come from, and the date. A
  footer naming the validation report and review record as sources.
- A consistent colour per concern across every diagram. Readable in light and dark mode
  (`prefers-color-scheme`). Text contrast at least WCAG AA. No colour is the only carrier of
  meaning: label it as well.
- Works from a phone width (390px) to a desktop (1440px) with no horizontal scroll.
- Every number on the page matches the validation report. Generate the figures with a script
  if that is easier to keep consistent, but commit only the HTML and, if you wrote one, the
  script under `docs/00-working/boundary-study/`.
- No confidential identifier. Run the staged private-content check with it staged.

**Verify it.** Parse it (`uv run python -c "import html.parser; html.parser.HTMLParser().feed(open('docs/00-working/boundary-study/boundary-overview.html').read())"`).
If a headless browser is available in the session (for example `npx playwright` or Python
Playwright), screenshot it at 390px and 1440px in light and dark mode and look at the
screenshots. If none is available, say so in the handoff file: the page has not been seen
rendered.

## Adversarial review of the report

Dispatch `partition-adversary` once more over the validation report and your `ARCH-012` and
`PLAN-050` edits:

> You are auditing a validation of a completed study, at `{ABS}`. Assume it is wrong. You are
> read-only: do not edit, create or delete any file, and do not write `_data/ideas.jsonl`. Check:
> (1) each figure in `docs/00-working/boundary-study/validation-report.md`'s figures table,
> re-counted yourself at both commits it names; (2) every edit to `ARCH-012`
> (`git diff origin/dev...HEAD -- docs/07-architecture/`) is a figure correction and changes no
> reasoning, option or recommendation; (3) the A/B/C re-assessment follows from the corrected
> evidence, and no claim in it lacks a source; (4) every finding in
> `docs/08-governance/reviews/<date>-plan-050.json` has a disposition, and each `fixed` names a
> change that exists in the diff; (5) every number in
> `docs/00-working/boundary-study/boundary-overview.html` matches the report, each of its eight
> required diagrams is present, and it loads nothing external (grep for `http`, `src=`,
> `@import`); (6) no file changed outside `ARCH-012`, `PLAN-050`,
> `backlog.yaml`, the catalog, the review records, `docs/00-working/boundary-study/`,
> `docs/00-working/cloud-prompts/status.md` and the handoff file. Rank each finding blocker, major or minor, with evidence.

Fix or disposition every finding. List them in the handoff file.

## After this

A fourth prompt, the boundary follow-up, is drafted only after the owner's A/B/C decision. Do not
start it.

## Kickoff for running this prompt directly

Normally the owner pastes the master prompt's kickoff instead. Use this one only to run this
prompt out of order, and only once every earlier row in `status.md` is merged.

Kickoff: you are running owner-directed, unclaimed work in a cloud clone of this repository. Run `git fetch origin dev`, then read `docs/00-working/cloud-prompts/boundary-validation.md` from `origin/dev` (`git show origin/dev:docs/00-working/cloud-prompts/boundary-validation.md`) and follow it exactly. It is an independent adversarial validation of the system boundary study (`ARCH-012`, `REQ-033`, `PLAN-050`), on branch `agent/cloud-boundary-validation`. You re-derive its figures, review the plan under GOV-018 acting as its planner, extend it with next steps and deferred phases, and re-assess options A, B and C without choosing. Tests run only in this clone on that branch, never on `dev`. Never commit to or push `dev`. Ask me questions with AskUserQuestion, batched, drafts in the message text and never in previews. Finish by pushing your branch with the handoff file the prompt describes.
