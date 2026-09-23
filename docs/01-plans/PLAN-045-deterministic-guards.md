---
schema_version: 1
id: doc-deterministic-guards
code: PLAN-045
title: Deterministic guards — trunk integrity checks and branch diff guards
kind: plan
status: draft
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-governance, sys-backlog, sys-gov-docs]
depends_on: [doc-deterministic-guards-requirements, doc-multi-session-coordination-protocol, doc-document-backlog-governance]
---

# Deterministic guards

Delivers [REQ-028](../06-requirements/REQ-028-deterministic-guards.md): checks that run as code
and refuse, instead of rules a session has to remember.

## Context and scope

`REQ-028`'s problem section lists the failures, each with its record: `dev` red on 30 consecutive
pushes with no session reading CI; a CI catalog step that compares the file with itself; two
governance-only writes that left `dev` red on 2026-09-23 (`024443c`, `f6216e9`); a pre-commit hook
that runs only the private-content check; no guard against a deleted or newly skipped test; 25
logic-level type-ignore comments that entered unreviewed; and 25 of 40 plans that no longer name
their registered phases.

The owner's rulings of 2026-09-23 set the scope. They were given in the owner's session and relayed
by the Session Manager, which recorded them on its board (`_working/session-manager/board.md`,
gitignored); each is quoted where it decides something.

- **Mapping Q8** (on Builder A's mapping of the owner's agentic-SDLC design): "guards
  (000408/000409/S7) as own phase now".
- **Scout O-2**: "widen guards phase" with CI-green-before-grant and the `ci.yaml` fix.
- **Scout O-4**: "(b) planning registers on branch via G4 now + plan-vs-registered check in guards
  phase".
- **The Session Manager's task statement of 2026-09-23**, which lists nine items (a)-(i) for this
  work and says, for the deliverables-diff check, "phase-dgov-06: move it or merge it in".

Ideas covered: `000399` (a full test run after every write to `dev`; the finding that nobody reads
CI), `000405` and `000406` (the completion edit leaves the catalog stale), `000198` (governance
passes with a stale catalog), `000408` (type-ignore, `cast(Any`, except-pass), `000409` (test-count
baseline), `000398` and `000027` (diff inside declared deliverables, through `phase-dgov-06`). The
Scout's two CI ideas were not yet recorded when this plan was written; their ids are added before
G3 (Open questions, OQ5).

## Decisions

**D1. Two phases, not one.** The task statement groups nine items as one phase. Each item is small,
but together they are three new tools with operations documents and tests, two governance checks,
CI and hook changes, and four procedure texts. That does not fit one session. The split follows what
each check protects: `phase-grd-01` protects `dev` itself (items a, b, c, d, i); `phase-grd-02`
checks what a branch brings (items e, f, h). Splitting further, one phase per tool, was rejected:
the three trunk checks share one test fixture (a stale catalog) and the two diff tools share the
same merge-gate text, so separate phases would each re-edit `GOV-017` and `PROMPT-037` and
serialise anyway. The owner ruled on 2026-09-22 that whether a phase fits one session is judged by the
agent planning it, not put to the owner; the judgement is reported here and at G3.

**D2. Move `phase-dgov-06`; do not merge it in.** `phase-dgov-06` already specifies the
deliverables-diff check against `REQ-015` R12-R13 under `PLAN-030`, with acceptance that includes a
known failing case (the `phase-prog-*` phases that rewrite `backlog.yaml` without declaring it).
Merging it into `phase-grd-02` would mean cancelling a phase another plan owns, amending `PLAN-030`
and `REQ-015`, and re-deriving acceptance that already exists, with no change to what gets built.
The cost of moving it is only a queue position: this plan proposes `phase-gov-01` (its dependency,
which it collides with on file) and `phase-dgov-06` in `next_up` directly after `phase-grd-02`.
`phase-dgov-06` reports rather than blocks (`REQ-015` R13); idea `000398` asked for a commit-time
refusal. That difference is kept, not resolved here (OQ3). `next_up` ranking is the owner's; the
order on this branch is a proposal ratified or changed at G3.

**D3. The staleness checks live inside the governance command.** The alternative, adding
`tools/generate_ideas_md.py --check` and a catalog comparison as separate CI and hook steps, was
rejected because the failure it prevents came from sessions that ran governance and nothing else
(`000405`). Putting the checks inside `uv run python -m src.governance` makes the command sessions
already run the one that fails. The cost: every governance run renders the catalog and `ideas.md`,
so the phase measures the added time and records it (acceptance).

**D4. The CI catalog step compares without overwriting.** Two ways to fix it: run `--catalog` and
then `git diff --exit-code docs/08-governance/catalog.md`, or delete the step because D3 makes the
governance step fail first. The phase keeps a separate named step using `git diff --exit-code`,
because a CI failure that names the catalog is faster to act on than a governance error inside a
longer log. The cost is one duplicated check.

**D5. The pre-commit hook runs the full governance check.** As ruled (item d). The alternative,
only the staleness checks in the hook, would let a commit through with other governance errors.
The cost: a work-in-progress commit that leaves any governance error is refused, including in a
worktree mid-phase. The hook runs from the primary checkout's `tools/git-hooks/` for every worktree
(`core.hooksPath`), so the change reaches all sessions the moment it is on `dev`. The phase measures
the hook's run time and records it.

**D6. CI-green-before-grant is a tool the Session Manager runs.** `tools/check_dev_ci.py` asks `gh`
for the latest completed run for `dev`'s head commit and exits 0, 1 or 2 (`REQ-028` R06). The
alternative, the Session Manager reading `gh run list` by eye, is what failed for six days. A
GitHub branch-protection rule was not chosen: it acts on a push to `origin`, after the commit
already exists on the local `dev`, and says nothing about whether the next session should be given
the primary checkout while the last commit is red. Exit 2 fails
closed: no grant while the result is unknown, unless the owner rules otherwise for that grant.

**D7. Test baseline and diff patterns are diff-scoped tools, not repository-wide lint.** For R08,
enabling ruff rules was rejected because none of them catches the case that matters. Run on `dev`
at `f1b891d`, `uv run ruff check --select S110,PGH003,BLE001 src tools test --statistics` reports
0 for `PGH003` (every existing ignore already carries an error code, which is all `PGH003`
checks), 0 for `S110`, and 2 for `BLE001`. A new `# type: ignore[arg-type]` passes all three, and
`BLE001` would also fail on the two existing sites, which this plan does not fix. For R07, a committed baseline file was rejected: it would
be one more generated file that every merge rewrites, the failure class of `000405`. The tool
compares two JUnit XML reports the caller produces, so the base run is the Session Manager's own
merge-gate re-run on `dev`.

**D8. The plan-versus-registered check has two directions with different reach.** A registered
phase not named in its plan fails only for plans created on or after 2026-09-22, because 25 older
plans would fail today (`REQ-028` problem 7) and `GOV-010`'s own scope starts on that date. A plan
naming an unregistered phase id fails for every plan; there are none today.

## Implementation phases

| Phase | What | Requirements | Depends on |
|---|---|---|---|
| `phase-grd-01` | Trunk integrity: catalog and `ideas.md` staleness inside governance; the CI catalog step; governance in the pre-commit hook; catalog regeneration named in the completion edit; `tools/check_dev_ci.py` and the grant rule; the `AGENTS.md` 155-156 proposal | R01-R06, R11 | none |
| `phase-grd-02` | Branch guards: the test-baseline tool, the diff-pattern tool, the plan-versus-registered governance check, and the merge-gate text that uses them | R07-R10 | `phase-grd-01` (both edit `GOV-017`, `PROMPT-037` and the governance entry point) |
| `phase-gov-01`, `phase-dgov-06` | Existing phases, moved in `next_up` (D2) | `REQ-015` R12-R13 | as registered |

`phase-grd-01` makes the governance check fail on staleness before `phase-grd-02` adds a second
check to the same command, so a failure in `phase-grd-02`'s tests cannot be a stale file left by
its own session.

## Requirement coverage

| Requirement | Phase | Acceptance evidence |
|---|---|---|
| R01, R02 | `phase-grd-01` | Scratch-branch runs from `REQ-028`, output in the session record; added run time recorded |
| R03 | `phase-grd-01` | The CI steps run locally on a stale-catalog commit and on `dev` |
| R04 | `phase-grd-01` | Hook refusal and acceptance, private-content fixture still refused; hook run time recorded |
| R05 | `phase-grd-01` | The `GOV-017` and `PROMPT-037` diffs |
| R06 | `phase-grd-01` | Five-case unit test; the two procedure diffs |
| R07 | `phase-grd-02` | Five-case unit test over JUnit fixtures |
| R08 | `phase-grd-02` | Unit tests per pattern plus the `dev~20..dev` run recorded |
| R09 | `phase-grd-02` | Three fixture plans; repository run exits 0 with counts |
| R10 | `phase-grd-02` | The `GOV-017` and `PROMPT-037` diffs |
| R11 | `phase-grd-01` | `AGENTS.md` diff or the record of no approval |

Every row maps to a phase, and each of the two new phases carries at least one row.

## Execution order and real concurrency

Computed from declared `systems` and `deliverables` on 2026-09-23:

- `phase-part-03` is active and declares `sys-governance`. Both guards phases declare it, so
  neither can be claimed until `phase-part-03` completes. `phase-gov-01` and `phase-dgov-06` declare
  `sys-governance` and `sys-backlog` and are blocked the same way.
- `phase-grd-01` and `phase-grd-02` share `sys-governance` and three deliverables; they run in
  order.
- `phase-grd-01` and `phase-dam-01` (`PLAN-046`) both list `AGENTS.md` and
  `docs/08-governance/`; they cannot run at the same time. `phase-dam-01` does not declare
  `sys-governance`, so it can run while `phase-part-03` is active.
- `phase-grd-02` and `phase-gov-01` share `sys-governance`; they run in order.

Real concurrency is therefore one of these phases at a time, alongside `phase-dam-01` only when
`phase-grd-01` is not running. The proposed `next_up` order on this branch is `phase-grd-01`,
`phase-dam-01`, `phase-grd-02`, `phase-gov-01`, `phase-dgov-06`, inserted after `phase-part-03` and
before `phase-cap-08` (OQ1).

## Out of scope

- **Cleaning up the 25 existing type-ignore comments and the except-pass sites.** R08 checks added
  lines only; the existing sites are a separate decision because some are explained (`intake.py:90`
  names a gap in LangGraph's type stubs).
- **Mutation testing** (idea `000400`). The owner's Q8 ruling named `000408`, `000409` and S7 only.
- **The S3 `next_up` review-record rule** (idea `000394`), ruled by the owner on 2026-09-23. It is a
  governance check but was not in the task statement's list; OQ4 asks where it goes.
- **Automatic merge by a non-builder session.** Scout O-3 kept builders' self-merge under `GOV-017`
  until P3's merge-gate nodes exist.
- **Security review** (idea `000410`, owner ruling Q9). It changes the plan standard and the merge
  gate's reviewers, not a deterministic check.

## Open questions

- **OQ1. Queue position.** Who: the owner, at G3. Leaning: after `phase-part-03`, ahead of
  `phase-cap-08`, because `phase-cap-08` also waits for the owner's real captures (restart file,
  section 4) and the guards protect every phase after them.
- **OQ2. Hook bypass.** Should a session ever commit with `--no-verify` when the governance check
  fails mid-phase? Who: the owner, at G3. Leaning: no; commit the fix instead, and if the check itself
  is wrong, stop and report.
- **OQ3. Report or refuse for the deliverables diff.** `phase-dgov-06` reports; idea `000398` asked
  to refuse. Who: the owner, when `phase-dgov-06` is claimed. Leaning: keep report-only as `REQ-015`
  R13 states, and have `READY` carry its output so the Session Manager sees it.
- **OQ4. The S3 `next_up` rule.** Who: the owner, at G3. Leaning: its own phase under this plan,
  after `phase-grd-02`, since it adds a third check to the same command.
- **OQ5. The Scout's two CI ideas.** Their ids are pending from Ideation. Who: the planner, before
  G3; this plan's idea list and the partition reconciliation (OQ6) cite them.
- **OQ6. Partition reconciliation.** The owner's partition-before-planning rule applies, and the
  `phase-part-03` sweep covers these ideas. Who: the planner, when the sweep's result is accepted and
  before G3. If the sweep puts any of these ideas in a different track, this plan is revised or the
  difference is put to the owner.
