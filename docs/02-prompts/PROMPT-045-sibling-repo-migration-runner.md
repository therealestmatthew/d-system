---
schema_version: 1
id: doc-prompt-sibling-repo-migration-runner
code: PROMPT-045
title: Sibling-repository migration runner — the starter prompt for the session that orchestrates PLAN-053's phases
kind: prompt
status: draft
owner: repository-owner
created: '2026-10-10'
updated: '2026-10-10'
systems: [sys-gov-docs, sys-backlog]
depends_on: [doc-sibling-repo-feature-migration, doc-sibling-repo-feature-migration-requirements, doc-prompt-session-manager-starter-messages]
---

# Sibling-repository migration runner

The text the owner pastes into the session that executes
[PLAN-053](../01-plans/PLAN-053-sibling-repo-feature-migration.md). It is a phase runner with
resume semantics, in the form of `PROMPT-041`: it selects one eligible phase, runs it under
`AGENTS.md`, hands off, and names the next one. It is not permission to run the whole plan in one
session, and it is not a coordinator: it claims and builds the phase itself, one at a time.

Under a Session Manager run (`GOV-017`, `PROMPT-037`), the owner pastes this into a builder session
after that session has acknowledged the shared contract. The contract wins where the two differ:
claims go through `TURN?`, reviews through `REVIEW-REQUEST`, and merges through `GRANTED merge`.
Outside such a run, the session follows `AGENTS.md` directly and asks the owner before integrating.

## Inputs

- The plan: `docs/01-plans/PLAN-053-sibling-repo-feature-migration.md`.
- The requirement: `docs/06-requirements/REQ-038-sibling-repo-feature-migration.md`.
- The phases: `phase-mig-01` to `phase-mig-06` in `docs/09-backlog/backlog.yaml`, which is the
  authority for their state, scope, acceptance, verification and deliverables. Read them there at
  run time; this prompt does not copy them.
- The review record: `docs/08-governance/reviews/2026-10-10-plan-053.json`, for the findings each
  phase must not reopen.
- The source repositories, when the phase ports code: `autoclaude-api` at commit
  `c7abe1389cd7593810dee345b5a3e2dd2b332540` and `life` at
  `1754e3de0bc2ad6a2b4d536d2ccf8796de7c0f8b`, read-only. If neither checkout is available in the
  session, the phase stops before writing code and reports it; the plan's D8 provenance rule
  cannot be met from memory.
- Repository workflow and safety rules: `AGENTS.md`. It overrides this prompt wherever they differ.

## Expected output

One phase worked to a terminal hand-off: a pushed `agent/<phase-id>` branch, its session record,
every verification command run with its real result quoted, the phase's `session`,
`completion_evidence` and `result` fields filled, and a closing message naming the phase, its state,
the evidence and the next eligible phase or the blocker. The phase is not marked `complete` by this
session: `/session-close` does that, invoked by the owner or a coordinator under `GOV-003`'s three
conditions.

## Prompt

> Run one phase of the sibling-repository feature migration using this runner. First read
> `AGENTS.md`, then `docs/01-plans/PLAN-053-sibling-repo-feature-migration.md` and
> `docs/06-requirements/REQ-038-sibling-repo-feature-migration.md`, then the six `phase-mig-*`
> entries in `docs/09-backlog/backlog.yaml`. The backlog is the authority for phase state.
>
> Run `uv run python -m src.governance --ready` in the primary checkout, reading only. Select the
> earliest eligible phase in this order: `phase-mig-01`, `phase-mig-02`, `phase-mig-03`,
> `phase-mig-04`, `phase-mig-05`. A phase is eligible when it is `queued`, every phase in its
> `depends_on` is `complete`, its Conflicts column is empty, and `max_active` is not reached.
> `phase-mig-06` is `deferred` and is never selected by this runner; it resumes only when the owner
> clears its `resume_when`. If no phase is eligible, report the exact blocker, with the `--ready`
> row that shows it, and stop. Do not start a phase of another plan.
>
> Claim the selected phase exactly as `AGENTS.md` "Concurrent agents: claim a phase" says: one
> small commit on `dev` in the primary checkout that sets `status: active` and your `agent` id and
> regenerates the catalog, validated by `uv run python -m src.governance` before the commit. Under
> a Session Manager run, that commit happens only inside a `GRANTED` claim turn. Then cut
> `agent/<phase-id>` and work in `../d-system-worktrees/<phase-id>` with its own `.venv`
> (`uv venv && uv sync --extra dev`). Never run `pytest`, a rebuild or the catalog test in the
> primary checkout.
>
> Work only inside the phase's `scope`, `deliverables` and declared `systems`. Write the phase's
> tests first, as each scope says, and record the failing run before the fix where the acceptance
> names a case that must fail. When the phase copies code from a source repository, read the file
> at the commit named in the plan's D8 and put the repository name, the path and that commit in
> the copied unit's header. Do not copy the source tests; write tests against this repository's
> fixtures. Do not reopen a finding the review record marks `fixed`; if the phase cannot be done
> as its scope states, stop, say which scope line fails and why, and put the choice to the owner
> rather than widening the phase.
>
> If a question arises that changes what gets built, ask the owner at that point with the options
> and your recommendation; otherwise state the assumption in the session record and continue.
> Record any new ask the owner makes as an idea through `tools/append_idea.py` (under a Session
> Manager run, send it to Ideation instead), one idea per ask, and continue the phase.
>
> Before hand-off: run every command in the phase's `verification` list in the worktree and keep
> the real output; write the session record with `kind: session` and a code from
> `--next-code session`; fill `session`, `completion_evidence` and `result` on the phase; rebase
> onto `dev`; re-run `uv run python -m src.governance`, `uv run pytest`,
> `uv run ruff check src/ test/ tools/` and `uv run mypy src/`; run
> `uv run python tools/check_no_private_content.py` with the changes staged; push the branch.
> Then request review: under a Session Manager run send `REVIEW-REQUEST <branch> <tip>` and wait
> for the verdict; otherwise dispatch an independent validator or adversary agent type with the
> diff, the requirement rows the phase covers and the verification commands, never your rationale,
> and fix or explicitly accept every blocker and major it returns.
>
> Never integrate into `dev` yourself. Report that the branch is ready and name
> `git diff dev..agent/<phase-id>`. Under a Session Manager run send `READY` with the items its
> contract lists. End by naming the selected phase, its backlog state, the session record, the
> verification outcome, and the next eligible phase in the order above or the blocker that stops it.

## Constraints

- One phase per run of this prompt. A second phase is a second paste, after the first has reached
  hand-off, so the owner can stop between them.
- No change to `AGENTS.md` or `CLAUDE.md`. If a phase appears to need one, quote the passage,
  propose the wording, and stop.
- No idea is moved past `triaged` by this session. Ideas `000673` to `000677` are delivered or
  decided by these phases; the owner moves them.
- Tests never run in the primary checkout.
- No `--no-verify`. A failing hook is a result to report.

## Close-out for the owner

When all five queued phases are complete, the remaining work under this plan is `phase-mig-06`'s
resume condition and the owner's decision on the draft ADR `phase-mig-05` produced. The plan's
open questions 1 to 4 name who decides each and when.
