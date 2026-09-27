# Cloud prompt 1a: the end-to-end planning protocol document (idea 000500)

Run this in its own fresh cloud session, normally started by [`master-prompt.md`](master-prompt.md),
which picks it from [`status.md`](status.md). It is first in the order. Sessions run one at a time:
each starts only after the previous one is merged into `dev`.

**Branch:** `agent/cloud-planning-protocol` · **Handoff file:**
`docs/00-working/cloud-prompts/handoff-planning-protocol.md`

## The task

Write one short governance document that lists the planning steps in order, from an idea to
completed work. Each step points to the document that already defines it. This is idea
`000500` (a short end-to-end planning protocol document). The document is a map, not a new
procedure: it must not create any rule the owner has not given.

**Scope is `000500` only (owner).** Ideas `000501` (archive one-time plans and prompts),
`000502` (formalize how requirements are generated) and `000505` (plan and plan-folder anatomy)
are related and will be planned later. Do not address them. Where a step touches one of them,
name the idea id in one line and move on.

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
git switch -c agent/cloud-planning-protocol origin/dev
git config core.hooksPath tools/git-hooks     # the pre-commit hook does not install itself
command -v uv >/dev/null || pip install uv
uv sync --extra dev                           # without --extra dev the governance check cannot import jsonschema
uv run python -m src.governance               # baseline: must exit 0 before you change anything
```

Then check that every document this prompt names exists in your clone (`git ls-files | grep`). If
one is missing, `origin/dev` is behind the local `dev` this prompt was written against. Stop, ask
the owner (see *Questions*), and do not work from a guess.

**Where you work.** Your clone is your only checkout. Work on `agent/cloud-planning-protocol` only. Never commit to
`dev`, never push `dev`, never merge anything into `dev`. Pushing `agent/cloud-planning-protocol` to `origin` is
expected and needs no approval: `AGENTS.md` says backing up your own work is not publishing. Push
at least once before you finish.

**Tests.** Run `pytest`, `ruff`, `mypy` and the governance check only in this clone, on
`agent/cloud-planning-protocol`. Never run them against the local primary checkout on `dev`; you have no access to it,
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
for i in ['000500', '000445', '000492']: print(i, json.dumps(s.get(i), indent=1, default=str))"
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
`docs/00-working/cloud-prompts/handoff-planning-protocol.md` on `agent/cloud-planning-protocol` and pushing. No front matter. It
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

## Read first

1. `AGENTS.md` in full.
2. Idea `000500` and its findings, through `fold()` (command above). The findings hold the
   owner's rulings. The earliest finding's ruling (2) and the wording "is to be designed" in its
   ruling (3) were superseded by later findings on the same day. Where findings differ, the later
   one governs.
3. The documents the steps point to:
   - `docs/07-architecture/ARCH-006-idea-realization-system.md`: the nine stages and gates G1 to G5
   - `docs/08-governance/GOV-010-plan-quality-standard.md`: the plan quality standard
   - `docs/08-governance/GOV-018-three-altitude-review-procedure.md`: the three-altitude review
   - `docs/08-governance/GOV-016-batch-orchestration-protocol.md`: batches
   - `docs/08-governance/GOV-002-backlog-protocol.md`: the backlog, phases and dependencies
   - `docs/08-governance/GOV-008-prompt-pack-protocol.md`: the pre-plan package ("Prompt A")
   - `docs/08-governance/GOV-001-protocol.md` and `GOV-005-document-codes.md`: front matter and codes
4. Ideas `000445` (resolve the phase-fit heuristic) and `000492` (reference artifacts, which
   lists a Planning Procedure), through `fold()`. Read phase `phase-irs-05` in
   `docs/09-backlog/backlog.yaml` (find its `- id:` line).

## What the document must carry (owner's rulings, 2026-09-27)

The owner's statement of the protocol, as given: *"plan -> audit -> decompose plan into phases
-> audit phases -> further decomposition -> additional audit (repeat until still undetermined
criteria is met)... assign systems to phases, batch phases and order dependencies"*.

The owner's rulings, which the document states explicitly:

1. **The requirement comes first**, before the plan.
2. **The owner gates:** G2 (the owner's words: "partition acceptance") and G3 (plan approval,
   and ratification of the proposed `next_up` ordering). `ARCH-006` names G2 "Track acceptance".
   Check what `ARCH-006`'s G2 decides. If it is the same gate, use `ARCH-006`'s name and add the
   owner's wording as a gloss. If it is not, ask the owner.
3. **Execution and after:** validators, the realization check, and the learning loop.
4. **The pre-plan investigation, or prompt pack, is OPTIONAL.** It points to `GOV-008`'s pre-plan
   package ("Prompt A"). It is tracked (a governed document) when it will be re-run, has owner
   gates, or needs its own review. Otherwise it lives in `docs/00-working/`. Note that `GOV-008`
   itself does not say this: its pipeline treats Prompt A as a governed prompt document, with no
   optional or ungoverned case (read its "The pipeline" section). The new document carries the
   owner's ruling and points to `GOV-008` for what the package contains. It must not claim
   `GOV-008` already says Prompt A is optional. List the difference in the "Open questions"
   section, and list `GOV-008` in the handoff file as a document that needs amending to match.
   Do not amend it yourself.
5. **The decompose -> audit loop stops** by default when every phase fits one session by a
   measured heuristic. That heuristic is `000445` and `phase-irs-05`, and it is not built yet:
   say so, and do not invent a stand-in. **The exception:** when the audit proposes no split but
   the heuristic says the phase does not fit, the case escalates to G3 with both results. At G3
   the owner chooses: split by hand, accept with a recorded reason, or adjust the heuristic. The
   owner's words, to quote: *"We still need to figure out the Heuristics. Once that is finalized
   maybe we change this to audit wins or always split."*
6. **Home:** a new short governance document (`kind: governance`, a `GOV-` code).

## How to write it

- Allocate the code with `uv run python -m src.governance --next-code governance`. Name the file
  `docs/08-governance/<code>-planning-protocol.md` (you may choose a better slug). Use `GOV-001`'s
  front matter; copy the shape of an existing `GOV-` document. Set `status: draft`: the owner
  approves it after the merge. List each document it points to in `depends_on` by `id`.
- One numbered list of steps, in order. Each step: what happens, who does it, the gate (if any),
  and where it is defined (document code plus section). One to three lines per step. Aim for one
  page. Do not restate what the pointed-to document says; point to it.
- Every pointer must be true. Open each target and confirm it says what the step claims. A step
  the owner named that no document defines yet (the phase-fit heuristic, for example) says
  "not yet defined" and names the idea or phase that will define it.
- Where two existing documents disagree, or the owner's order differs from `ARCH-006`'s stage
  order, do not settle it. Say so in an "Open questions" section and ask the owner if the answer
  changes the step order.
- No new rules, conventions or requirements the owner did not give (`CLAUDE.md`, "Do not turn a
  one-time instruction into a standing rule"). If a step seems to need one, propose it as an open
  question.
- Do not edit the documents you point to. If one is wrong or stale, list it in the handoff file
  with the passage quoted.
- Regenerate the catalog in the same commit.

## Adversarial review

Dispatch `partition-adversary` with this brief. The partition being audited is the document's
division of the planning process into ordered steps.

> You are auditing a draft governance document at `{ABS}/docs/08-governance/<file>`. It claims
> to list the planning steps in order, each pointing to where the step is already defined.
> Assume it is wrong. You are read-only; do not edit, create or delete any file, and do not
> write `_data/ideas.jsonl`. Check: (1) **Fidelity.** Read idea 000500's findings with
> `uv run python -c "from src.db.ideas import fold, load_events; import json; print(json.dumps(fold(load_events())['000500'], indent=1))"`
> in `{ABS}`. Each owner ruling appears in the document, unchanged in meaning, and later
> findings override earlier ones. (2) **Pointers.** Open every document and section the draft
> points to. Report any that does not say what the step claims. (3) **Coverage.** Every stage
> and gate in `ARCH-006` is either a step or explicitly out of scope; nothing is covered twice.
> (4) **Invented rules.** Report any sentence that states a rule, threshold or convention found
> neither in the owner's rulings nor in a pointed-to document. (5) **Scope.** The document
> does not decide anything belonging to ideas 000501, 000502 or 000505. Rank each finding
> blocker, major or minor, with the file and line or the command and its output as evidence.

Fix or disposition every finding, then re-run the checks you changed.

## Kickoff for running this prompt directly

Normally the owner pastes the master prompt's kickoff instead. Use this one only to run this
prompt out of order, and only once every earlier row in `status.md` is merged.

Kickoff: you are running owner-directed, unclaimed work in a cloud clone of this repository. Run `git fetch origin dev`, then read `docs/00-working/cloud-prompts/planning-protocol.md` from `origin/dev` (`git show origin/dev:docs/00-working/cloud-prompts/planning-protocol.md`) and follow it exactly. It has you write one short governance document listing the planning steps in order for idea 000500 (a short end-to-end planning protocol document), on branch `agent/cloud-planning-protocol`. Tests run only in this clone on that branch, never on `dev`. Never commit to or push `dev`. Ask me questions with AskUserQuestion, batched, drafts in the message text and never in previews. Finish by pushing your branch with the handoff file the prompt describes.
