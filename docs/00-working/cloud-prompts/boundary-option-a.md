# Cloud prompt 4: the boundary follow-up for option A

Run this in its own fresh cloud session, normally started by [`master-prompt.md`](master-prompt.md),
which picks it from [`status.md`](status.md). It is fourth in the order, after prompt 3 (boundary
validation) is merged into `dev`.

**Branch:** `agent/cloud-boundary-option-a` · **Handoff file:**
`docs/00-working/cloud-prompts/handoff-boundary-option-a.md`

## The task

The system boundary study (`ARCH-012`, `REQ-033`, `PLAN-050`) asked whether this repository should
stay one repository or split. Prompt 3 validated it. On 2026-09-28 the owner chose **option A**:
one repository with explicit ownership and interface contracts. The owner's rulings are recorded in
[`owner-rulings-2026-09-28.md`](owner-rulings-2026-09-28.md). Read that file first; it is the
authority for this session.

You do four things, and nothing else:

1. **Apply the seven `ARCH-012` wording changes** the owner approved (validation review finding
   F01), exactly as worded in section 6 of `docs/00-working/boundary-study/validation-report.md`.
2. **Record the owner's decisions** where the documents carry them: option A at `ARCH-012`'s owner
   decision gate, F01's owner disposition in the review record, and the no-separate-child-reviews
   exception in `PLAN-050`.
3. **Review the deferred boundary phases** `phase-bnd-06` to `phase-bnd-14` against current `dev`,
   then release, keep deferred, or cancel each one, as *Step 3* sets out.
4. **Review the phases you release** at `GOV-018`'s later-added-phase altitude, and disposition the
   findings.

You do not execute any `phase-bnd-*` phase. Releasing a phase puts it in the backlog for a local
session to claim; the cloud session never claims.

The documents:

- `docs/07-architecture/ARCH-012-system-boundary-decision-report.md`: the decision report (`draft`)
- `docs/06-requirements/REQ-033-system-boundary-study.md`: the study's requirements
- `docs/01-plans/PLAN-050-system-boundary-study/PLAN-050-overview.md` and its five children
- `docs/00-working/boundary-study/validation-report.md`: prompt 3's report; section 6 holds the
  seven wording changes
- `docs/08-governance/reviews/2026-09-28-plan-050.json`: the review record with F01 to F09
- `docs/09-backlog/backlog.yaml`: `phase-bnd-06` to `phase-bnd-14`, all `deferred`
- `docs/00-working/cloud-prompts/owner-rulings-2026-09-28.md`: the owner's rulings

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
git switch -c agent/cloud-boundary-option-a origin/dev
git config core.hooksPath tools/git-hooks     # the pre-commit hook does not install itself
command -v uv >/dev/null || pip install uv
uv sync --extra dev                           # without --extra dev the governance check cannot import jsonschema
uv run python -m src.governance               # baseline: must exit 0 before you change anything
```

Then check that every document this prompt names exists in your clone (`git ls-files | grep`). If
one is missing, `origin/dev` is behind the local `dev` this prompt was written against. Stop, ask
the owner (see *Questions*), and do not work from a guess.

**Where you work.** Your clone is your only checkout. Work on `agent/cloud-boundary-option-a` only. Never commit to
`dev`, never push `dev`, never merge anything into `dev`. Pushing `agent/cloud-boundary-option-a` to `origin` is
expected and needs no approval: `AGENTS.md` says backing up your own work is not publishing. Push
at least once before you finish.

**Tests.** Run `pytest`, `ruff`, `mypy` and the governance check only in this clone, on
`agent/cloud-boundary-option-a`. Never run them against the local primary checkout on `dev`; you have no access to it,
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
`docs/00-working/cloud-prompts/handoff-boundary-option-a.md` on `agent/cloud-boundary-option-a` and pushing. No front matter. It
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


## What the owner ruled (2026-09-28)

From [`owner-rulings-2026-09-28.md`](owner-rulings-2026-09-28.md), quoted where the words matter:

- Boundary direction: **option A**. "Next: the contract-and-measurement follow-up."
- F01, escalated to G3: **apply** the seven `ARCH-012` wording changes in section 6 of the
  validation report. "Not yet applied; they belong in the follow-up."
- Separate `GOV-018` reviews for the five child plans `PLAN-050.01` to `.05`: **no**. "All five
  phases are complete; this is recorded as the exception."
- `phase-bnd-07` (a required `concern` field in `systems.yaml`): **approved**. "It is still
  deferred until `phase-bnd-06` is complete; its scope is reviewed against current `dev` before it
  is released."
- `phase-bnd-07`: **approved**, but "still deferred until `phase-bnd-06` is complete; its scope is
  reviewed against current `dev` before it is released."
- The deferred phases: "The fourth prompt reviews their scope against `dev` and releases or cancels
  them."
- `ARCH-012` and `GOV-021`: **both stay `draft`**. Do not change either document's `status`.

## Read first

`AGENTS.md`; `owner-rulings-2026-09-28.md`; `GOV-018` in full; `GOV-002-backlog-protocol.md`
(phase fields, and the lifecycle: `deferred` to `queued` needs "release evidence reviewed",
`deferred` to `cancelled` needs "scope explicitly withdrawn"); `docs/02-prompts/PROMPT-038-single-adversary-engine.md`
(the `later-added-phase` section); `schemas/adversarial-finding.schema.json` (the `dispositions`
rules for an owner entry); `validation-report.md` sections 5 and 6; then the documents above.

## Step 1: the seven `ARCH-012` wording changes

Apply each of the seven changes in section 6 of `validation-report.md` **word for word**. Do not
improve, shorten or update the proposed wording: the owner approved that text.

1. Before editing, confirm that each *Current* passage still appears in `ARCH-012` on your branch.
   Compare with whitespace collapsed, because the file wraps lines. Change 4's passage sits in the
   *Boundary options* table's option B row, without the trailing full stop. Change 7 is a new last
   bullet under *Constraints and limits*, so it has no current passage.
2. If a passage is missing or has changed since 2026-09-28, do not edit that change. Ask the owner
   (see *Questions*), and put it in the handoff file.
3. If a fact inside a proposed passage is no longer true at your tip (for example, whether CI runs
   the plugin's test suite, or how many of its tests fail), apply the passage unchanged anyway: it
   is dated. Report the fact and its current value in the handoff file, with the command you used.
4. Keep the table in *Boundary options* valid Markdown after change 4 (one row, same column count).
5. Set `updated` to your session date. Leave `status: draft`.

These seven changes are the only edits to `ARCH-012`'s reasoning in this session. Step 2 adds the
decision record.

## Step 2: record the owner's decisions

1. **`ARCH-012`, *Owner decision gate*.** Record the boundary direction decision without removing
   the recommendation: add one line under the table, for example "Decided 2026-09-28: the owner
   selected option A (`docs/00-working/cloud-prompts/owner-rulings-2026-09-28.md`)." Record nothing
   for the other three rows. The owner has not ruled on the first portability candidate, prompt
   navigation, or the evidence threshold.
2. **The review record** `2026-09-28-plan-050.json`. F01 carries a planner `escalated-g3`
   disposition. Append the owner's G3 disposition as the schema requires (`by: owner`,
   `value: fixed`), with a reason naming the ruling file and the commit that applied the seven changes. Validate with
   `uv run pytest test/test_adversarial_finding_schema.py`. If the schema rejects the entry, report
   the output and ask the owner; do not change the schema.
3. **`PLAN-050` overview.** Add a dated amendment line recording that the owner selected option A,
   that separate `GOV-018` reviews for `PLAN-050.01` to `.05` were declined as an exception because
   all five phases are complete, and which phases this session released, kept deferred or
   cancelled. Update the *Next steps after the owner's decision* section to match Step 3.

## Step 3: the deferred boundary phases

For each of `phase-bnd-06` to `phase-bnd-14`, read its full entry in `backlog.yaml` and review its
`scope`, `deliverables`, `systems`, `acceptance`, `verification` and `depends_on` against current
`dev`: paths that moved, systems that were renamed or rescoped, figures that changed, and work that
has since been done elsewhere (search the backlog and `docs/` before assuming nothing overlaps).
Revise a field only where current `dev` makes it wrong, and record each revision.

What this prompt proposes for each phase, from the owner's rulings and `ARCH-012`:

| Phase | Tied to | Proposed action | Why |
|---|---|---|---|
| `phase-bnd-06` (concern ownership and interface contract) | A | Release to `queued` | The owner ruled that A releases it |
| `phase-bnd-07` (a `concern` field in the registry) | A | Keep `deferred`; rewrite `blocked_reason` and `resume_when` | The owner approved it but kept it deferred until `phase-bnd-06` is complete. Record the approval (2026-09-28) so the only remaining condition is `phase-bnd-06`'s completion |
| `phase-bnd-08` (entry-point values and prompt classification) | A | Release to `queued` | The owner ruled that A releases it |
| `phase-bnd-09` (retrieval measurement) | A | Release to `queued` | The owner ruled that A releases it |
| `phase-bnd-14` (independent classification check and prompt operating index) | A | **Ask the owner** | It publishes a prompt operating index, which is `ARCH-012`'s separate *Prompt navigation treatment* decision. The owner has not ruled on that row. Recommendation: keep it `deferred`, with `resume_when` naming that decision and `phase-bnd-08`'s completion |
| `phase-bnd-10` (three extraction candidates against B's preconditions) | B | **Ask the owner** | Change 6 of the approved wording names `phase-bnd-10` as the candidate assessment, and the *Owner decision gate* allows a candidate "after new evidence satisfies its preconditions", even under A. Cancelling it would leave change 6 pointing at a cancelled phase. Recommendation: keep it `deferred`, with `resume_when` naming the evidence threshold row of the *Owner decision gate* |
| `phase-bnd-11` (extraction discovery for a named candidate) | B | **Ask the owner** | It depends on `phase-bnd-10`. Recommendation: the same as `phase-bnd-10` |
| `phase-bnd-12` (migration architecture for a split) | C | Cancel | The owner chose A. Option C's work is withdrawn |
| `phase-bnd-13` (cross-repository governance for a split) | C | Cancel | As `phase-bnd-12` |

**The three questions depart from recorded rules, and the owner must be told so.** The owner's
ruling names only two outcomes ("releases or cancels"), and the `PLAN-050` overview's *Next steps
after the owner's decision* already says: "When the owner chooses, the chosen option's phases are
reviewed against current `dev` and released to `queued`; the other options' phases are cancelled
with the decision as the reason." Under that rule `phase-bnd-14` would be released, and
`phase-bnd-10` and `-11` cancelled. The recommendations above keep all three deferred instead, for
the reasons in the table. So each question states, in the message text: the recorded rule and what
it would do; the recommendation and why; and, for `phase-bnd-10`, that cancelling it leaves the
approved change 6 naming a cancelled phase, because the approved wording is applied unchanged.

Ask the three questions in one batch before editing `backlog.yaml`, with the recommendation first.
Whatever the owner answers, Step 2's `PLAN-050` update rewrites that *Next steps* sentence so the
plan and the backlog agree, and the amendment line records the owner's answer. Then:

- **Release** (`deferred` to `queued`): remove `blocked_reason` and `resume_when`, and make sure
  `next_action` is the first useful step for whoever claims it. The backlog schema has no notes
  field and rejects unknown properties, so do not add one: the release evidence (the owner's
  option A ruling and your scope review, dated) goes in the `PLAN-050` amendment line from Step 2
  and in the handoff file. Do not add any phase to `next_up`: the queue order is the owner's.
- **Keep deferred**: rewrite `blocked_reason`, `resume_when` and `next_action` so none of them
  still says the owner has not chosen between A, B and C.
- **Cancel** (`deferred` to `cancelled`): record why the scope was withdrawn, naming the ruling,
  in the `PLAN-050` amendment line, and rewrite `next_action` so it no longer waits for the A/B/C
  decision. Keep or drop `blocked_reason` and `resume_when` as the
  validator requires for `cancelled`, and report which.
  Check that no remaining phase depends on a cancelled one (`GOV-002`: "a cancelled dependency does
  not silently satisfy its dependents").
- Set the backlog's `updated` date. Run `uv run python -m src.governance`, regenerate the catalog
  with `--catalog`, and run `--ready`. Paste the `--ready` rows for the `phase-bnd-*` phases into the
  handoff file, so the Session Manager can see which are now offered.

If the validator rejects a transition, report its output and ask the owner. Do not find a way
around it.

## Step 4: later-added-phase review of the released phases

Every phase you moved to `queued`, and every phase whose `scope`, `acceptance` or `depends_on` you
revised, is reviewed at `GOV-018`'s later-added-phase altitude. They were last reviewed on
2026-09-28 (F07 to F09) while `deferred`.

Dispatch `partition-adversary` with `PROMPT-038` filled in for the `later-added-phase` altitude, every
path absolute in your clone. Add to its brief: "Check each phase's scope against the current
repository, not against the study's evidence date, and check that no released phase depends on a
cancelled or deferred phase it cannot complete without."

Append the findings to the same review record (`target.later_added_phases`, `altitudes_run`), as
prompt 3 did, and disposition them as planner. One revision cycle; what you cannot resolve is
`escalated-g3`, for the owner.

## Adversarial review of the session's changes

Before the gates, dispatch `partition-adversary` once more, with this brief:

> You are auditing a follow-up to a decision report, at `{ABS}`. Assume it is wrong. You are
> read-only: do not edit, create or delete any file, and do not write `_data/ideas.jsonl`. Check:
> (1) each of the seven changes in `docs/00-working/boundary-study/validation-report.md` section 6
> appears in `docs/07-architecture/ARCH-012-system-boundary-decision-report.md` word for word, in
> the section it names, and nothing else in `ARCH-012` changed beyond them, the decision line under
> *Owner decision gate* and `updated` (`git diff origin/dev...HEAD -- docs/07-architecture/`);
> `ARCH-012`'s `status` is still `draft`; (2) every `phase-bnd-*` status change in
> `docs/09-backlog/backlog.yaml` matches the owner's rulings in
> `docs/00-working/cloud-prompts/owner-rulings-2026-09-28.md` or an owner answer recorded in the
> handoff file, and follows `GOV-002`'s lifecycle; no released phase depends on a cancelled phase;
> no phase was added to `next_up`; (3) F01's owner disposition in
> `docs/08-governance/reviews/2026-09-28-plan-050.json` is valid against
> `schemas/adversarial-finding.schema.json` and names a commit that exists; (4) the `PLAN-050`
> overview's amendment and next steps match the backlog; (5) no file changed outside `ARCH-012`,
> `PLAN-050`, `backlog.yaml`, the catalog, the review record,
> `docs/00-working/cloud-prompts/status.md` and the handoff file. Rank each finding blocker, major
> or minor, with evidence.

Fix or disposition every finding. List them in the handoff file.

## Outside this session

- Deleting the merged branches on `origin` (`agent/cloud-planning-protocol`,
  `agent/cloud-plan-anatomy`, `agent/cloud-boundary-validation`). The cloud session was refused
  with HTTP 403; the owner does this locally or on GitHub.
- The plan-folder standard and `GOV-021` rulings in the same file. Other sessions own them.
- Executing any `phase-bnd-*` phase.

## Kickoff for running this prompt directly

Normally the owner pastes the master prompt's kickoff instead. Use this one only to run this
prompt out of order, and only once every earlier row in `status.md` is merged.

Kickoff: you are running owner-directed, unclaimed work in a cloud clone of this repository. Run `git fetch origin dev`, then read `docs/00-working/cloud-prompts/boundary-option-a.md` from `origin/dev` (`git show origin/dev:docs/00-working/cloud-prompts/boundary-option-a.md`) and follow it exactly. It is the boundary follow-up after the owner chose option A: it applies the seven approved `ARCH-012` wording changes, records the owner's decisions, and releases, keeps deferred or cancels the deferred `phase-bnd-*` phases after reviewing them against `dev`, on branch `agent/cloud-boundary-option-a`. Tests run only in this clone on that branch, never on `dev`. Never commit to, merge into or push `dev`. Ask me questions with AskUserQuestion, batched, drafts in the message text and never in previews. Finish by pushing your branch with the handoff file the prompt describes.
