---
schema_version: 1
id: doc-deterministic-guards
code: PLAN-045
title: Deterministic guards — trunk integrity checks, green CI before each grant, and branch diff guards
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
by the Session Manager, which records them on its board (`_working/session-manager/board.md`,
gitignored). The rulings answer decision lists in the Scout's reports, also gitignored, under
`_working/session-manager/scout/`. Each ruling is quoted from the board as written there:

- "OWNER mapping rulings: ... Q8 guards (000408/000409/S7) as own phase now" (answering Builder A's
  mapping of the owner's agentic-SDLC design, `reports/owner-design-mapping.md` section 8, Q8).
- "OWNER Scout rulings: ... O-2 widen guards phase" (answering `orchestration-3-architecture.md`,
  "Owner decisions", O-2: "Widen the ruled guards phase with CI-green-before-grant and the ci.yaml
  fix").
- "OWNER Scout rulings: O-4 (b) planning registers on branch via G4 now + plan-vs-registered check in
  guards phase".

The widened scope is the Scout's staged path, step 1 (`orchestration-3-architecture.md`, section F),
which lists seven items: (a) each grant waits for green `dev` CI; (b) fix `ci.yaml`'s catalog diff
and correct `AGENTS.md` 155-156; (c) catalog and `ideas.md` checks in governance; (d) governance in
the pre-commit hook; (e) the test-count baseline guard; (f) a type-ignore diff check; (g) the
deliverables-diff check, "by moving phase-dgov-06 earlier or merging it into this phase". Two more
come from the rulings above: the plan-versus-registered check (O-4) and the completion edit's catalog
regeneration (ideas `000405`, `000406`). The Session Manager's task message to the Prompt Planner
on 2026-09-23 listed the same nine; that message is not on disk, so this plan cites the sources
above instead.

Ideas covered: `000399` (a full test run after every write to `dev`; the finding that nobody reads
CI), `000405` and `000406` (the completion edit leaves the catalog stale), `000198` (governance
passes with a stale catalog), `000408` (type-ignore, `cast(Any`, except-pass), `000409` (test-count
baseline), `000398` and `000027` (diff inside declared deliverables, through `phase-dgov-06`). The
Scout's two CI ideas were not yet recorded when this plan was written; their ids are added before
G3 (OQ5).

## Decisions

**D1. Three phases, not one.** The nine items are three new tools with operations documents and
tests, two governance checks, CI and hook changes, and procedure text in `GOV-017` and `PROMPT-037`.
That does not fit one session. The split follows what each check protects:

- `phase-grd-01` makes `dev` fail loudly on stale generated files: (b), (c), (d) and the completion
  edit. These share one fixture (a stale catalog) and one code path (the governance command), which
  is why they stay together.
- `phase-grd-02` is (a), `tools/check_dev_ci.py` and the grant rule. It shares no fixture or code
  with `phase-grd-01`; it queries `gh` and has its own operations document and tests.
- `phase-grd-03` checks what a branch brings: (e), (f) and the plan-versus-registered check, plus
  the merge-gate text that uses them.

(g) is `phase-dgov-06`, moved rather than merged (D2). One phase per tool was rejected: the three
trunk checks would each re-edit the governance command and the same `GOV-017` passages and run in
sequence anyway. The owner ruled on 2026-09-22 that whether a phase fits one session is judged by the
agent planning it, not put to the owner; the judgement is reported here and at G3.

**D2. Move `phase-dgov-06`; do not merge it in.** `phase-dgov-06` already specifies the
deliverables-diff check against `REQ-015` R12-R13 under `PLAN-030`, with acceptance that includes a
known failing case (the `phase-prog-*` phases that rewrite `backlog.yaml` without declaring it).
Merging it into `phase-grd-03` would mean cancelling a phase another plan owns, amending `PLAN-030`
and `REQ-015`, and re-deriving acceptance that already exists, with no change to what gets built.
The cost of moving it is only a queue position: this plan proposes `phase-gov-01` (its dependency,
which it collides with on file) and `phase-dgov-06` in `next_up` directly after `phase-grd-03`.
`phase-dgov-06` reports rather than blocks (`REQ-015` R13); idea `000398` asked for a commit-time
refusal. That difference is kept, not resolved here (OQ3). `next_up` ranking is the owner's; the
order on this branch is a proposal ratified or changed at G3.

**D3. The staleness checks live inside the governance command.** The alternative, adding
`tools/generate_ideas_md.py --check` and a catalog comparison as separate CI and hook steps, was
rejected because the failure it prevents came from sessions that ran governance and nothing else
(`000405`). Putting the checks inside `uv run python -m src.governance` makes the command sessions
already run the one that fails. The cost: every governance run renders the catalog and `ideas.md`,
so the phase measures the added time and records it. The owner ruled the placement (item (c));
`phase-conc-08` will write the general enforcement-placement rule and takes this placement as one of
its inputs (see Execution order).

**D4. The CI catalog step runs first and compares without overwriting.** The step is moved ahead of
the governance step and changed to run `--catalog` and then
`git diff --exit-code docs/08-governance/catalog.md`. The alternative, deleting the step because D3
makes governance fail on a stale catalog, would leave that failure reported as one error among the
governance command's output. With the step first, a stale catalog fails a step whose name says what
is wrong. The cost is one check run twice.

**D5. The pre-commit hook runs the full governance check.** As ruled (item (d)). The alternative,
only the staleness checks in the hook, would let a commit through with other governance errors.
The cost: a work-in-progress commit that leaves any governance error is refused, including in a
worktree mid-phase. The hook runs from the primary checkout's `tools/git-hooks/` for every worktree
(`core.hooksPath` is `/code/d-system/tools/git-hooks`, a shared setting), so the change reaches all
sessions the moment it is on `dev`, and a commit in `phase-grd-01`'s own worktree runs the **old**
hook. The phase therefore tests the new hook by running `sh tools/git-hooks/pre-commit` directly
against staged changes in its worktree, not through `git commit`, and changes no git configuration.
It measures the hook's run time and records it.

**D6. CI-green-before-grant is a tool the Session Manager runs.** `tools/check_dev_ci.py` asks `gh`
for the latest completed run for `dev`'s head commit and exits 0, 1 or 2 (`REQ-028` R06). The
alternative, the Session Manager reading `gh run list` by eye, is what failed for six days. A GitHub
branch-protection rule was not chosen: it acts on a push to `origin`, after the commit already
exists on the local `dev`, and says nothing about whether the next session should be given the
primary checkout while the last commit is red. Exit 2 fails closed: no grant while the result is
unknown, unless the owner rules otherwise for that grant.

**D7. Test baseline and diff patterns are diff-scoped tools, not repository-wide lint.** For R08,
enabling ruff rules was rejected because none of them catches the case that matters. Run on `dev`
at `f1b891d`, `uv run ruff check --select S110,PGH003,BLE001 src tools test --statistics` reports
0 for `PGH003` (every existing ignore already carries an error code, which is all `PGH003` checks),
0 for `S110`, and 2 for `BLE001`. A new `# type: ignore[arg-type]` passes all three, and `BLE001`
would also fail on the two existing sites, which this plan does not fix. For R07, a committed
baseline file was rejected: it would be one more generated file that every merge rewrites, the
failure class of `000405`. The tool compares two JUnit XML reports the caller produces, so the base
run is the Session Manager's own merge-gate re-run on `dev`.

**D8. The plan-versus-registered check has two directions with different reach.** A registered
phase not named in its plan fails only for plans created on or after 2026-09-22, because 25 older
plans would fail today (`REQ-028` problem 7) and `GOV-010`'s own scope starts on that date. A plan
naming an unregistered phase id fails for every plan; there are none today.

**D9. A nonzero R07 or R08 result blocks the merge unless the owner signs off.** Both checks exist
to refuse (`000409`: "refuse a branch whose count drops"; `000408`: "refuses new `# type: ignore`").
Advisory-only output was rejected: problem 1 in `REQ-028` shows that output nobody is required to act
on is not read. The owner's sign-off names the tests or lines it accepts, so a justified deletion or
a documented ignore can still merge.

## Implementation phases

| Phase | What | Requirements | Depends on |
|---|---|---|---|
| `phase-grd-01` | Stale generated files fail loudly: catalog and `ideas.md` checks inside governance; the CI catalog step; governance in the pre-commit hook; the catalog regeneration named in the completion edit; the `AGENTS.md` 155-156 proposal | R01-R05, R11 | none |
| `phase-grd-02` | Green `dev` CI before each grant: `tools/check_dev_ci.py`, its operations document and tests, and the grant rule in `GOV-017` and `PROMPT-037` | R06 | `phase-grd-01` (both edit `GOV-017` and `PROMPT-037`) |
| `phase-grd-03` | Branch guards: the test-baseline tool, the diff-pattern tool, the plan-versus-registered check, and the merge-gate text that uses them | R07-R10 | `phase-grd-02` (same two documents; and the governance entry point `phase-grd-01` changes) |

Moved, not new: `phase-gov-01` (code-reservation enforcement, `PLAN-010`) and `phase-dgov-06` (the
deliverables diff, `PLAN-030`, `REQ-015` R12-R13), proposed in `next_up` after `phase-grd-03` (D2).
`phase-gov-01` is listed only because `phase-dgov-06` depends on it.

## Requirement coverage

| Requirement | Phase | Acceptance evidence |
|---|---|---|
| R01, R02 | `phase-grd-01` | Scratch-branch runs from `REQ-028`, output in the session record; added run time recorded |
| R03 | `phase-grd-01` | The CI steps run locally on a stale-catalog commit and on `dev` |
| R04 | `phase-grd-01` | Direct hook runs: refusal, acceptance, private-content fixture still refused; run time recorded |
| R05 | `phase-grd-01` | The `GOV-017` step 6 and both `PROMPT-037` passages |
| R06 | `phase-grd-02` | Five-case unit test; the two procedure diffs |
| R07 | `phase-grd-03` | Five-case unit test over JUnit fixtures |
| R08 | `phase-grd-03` | Unit tests per pattern plus the `dev~20..dev` run recorded |
| R09 | `phase-grd-03` | Three fixture plans; repository run exits 0 with counts |
| R10 | `phase-grd-03` | The `GOV-017` and `PROMPT-037` diffs |
| R11 | `phase-grd-01` | `AGENTS.md` diff or the record of no approval |

Every row maps to a phase, and each new phase carries at least one row.

## Execution order and real concurrency

Computed from declared `systems` and `deliverables` with `uv run python -m src.governance --ready`
on this branch:

- `phase-part-03` is active and declares `sys-governance`. All three guards phases, `phase-dam-01`
  (`PLAN-046`), `phase-gov-01` and `phase-dgov-06` declare it, so none can be claimed until
  `phase-part-03` completes.
- The three guards phases share `sys-governance`, `GOV-017` and `PROMPT-037`; they run in order.
- `phase-dam-01` shares `sys-governance`, `AGENTS.md` and `docs/08-governance/` with
  `phase-grd-01`; they cannot run at the same time.
- `phase-conc-08` (`PLAN-026`, queued, not in `next_up`) declares `sys-governance` and
  `docs/08-governance/`, so it cannot run beside any of these. Its scope applies a
  placement rule to "the governance check, catalog staleness, the private-content gate". The owner
  ruled this plan's placements directly (items (c) and (d)), so `phase-conc-08` records them as
  given; if its rule then concludes otherwise, that is a finding for the owner, not a reason for
  this plan to wait.

Real concurrency is one of these phases at a time. The proposed `next_up` order on this branch is
`phase-grd-01`, `phase-grd-02`, `phase-dam-01`, `phase-grd-03`, `phase-gov-01`, `phase-dgov-06`,
inserted after `phase-part-03` and before `phase-cap-08` (OQ1). `phase-grd-01` goes first so its
check catches a stale catalog in every later phase's own commits.

## Out of scope

- **Cleaning up the 25 existing type-ignore comments and the except-pass sites.** R08 checks added
  lines only; the existing sites are a separate decision because some are explained (`intake.py:90`
  names a gap in LangGraph's type stubs).
- **Mutation testing** (idea `000400`). The owner's Q8 ruling named `000408`, `000409` and S7 only.
- **The S3 `next_up` review-record rule** (idea `000394`), ruled by the owner on 2026-09-23 ("S3
  next_up rule refuses, grandfathers current 19"). It is a governance check but was not in the
  Scout's step 1; OQ4 asks where it goes.
- **Automatic merge by a non-builder session.** Scout O-3 kept builders' self-merge under `GOV-017`
  until P3's merge-gate nodes exist.
- **Security review** (idea `000410`, mapping Q9). It changes the plan standard and the merge
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
  after `phase-grd-03`, since it adds another check to the same command.
- **OQ5. The Scout's two CI ideas.** Their ids are pending from Ideation. Who: the planner, before
  G3; this plan's idea list and the partition reconciliation (OQ6) cite them.
- **OQ6. Partition reconciliation.** The owner's partition-before-planning rule applies, and the
  `phase-part-03` sweep covers these ideas. Who: the planner, when the sweep's result is accepted and
  before G3. If the sweep puts any of these ideas in a different track, this plan is revised or the
  difference is put to the owner.
