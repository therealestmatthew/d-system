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
  mapping of the owner's agentic-SDLC design, `reports/owner-design-mapping.md` section 8, Q8; the
  design is tracked at `docs/00-working/agentic-sdlc-2026-09/`).
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
baseline), `000398` and `000027` (diff inside declared deliverables, through `phase-dgov-06`),
`000412` (CI's catalog check cannot fail; `phase-grd-01`) and `000413` (nothing reads `dev`'s CI
result before a grant; `phase-grd-02`). The work sits under the owner's framing in `000411`: agents
with defined contracts and the orchestration systems that manage them are designed in parallel;
these guards are orchestration-side checks that hold whichever agent does the work.

**Partition placement.** The owner accepted the `phase-part-03` partition at GATE 3 on 2026-09-23
(`docs/00-working/idea-partition-2026-09-23.md` and `.json`, on `agent/phase-part-03` at `6051dad`):
371 ideas in 87 groups under 12 tracks, plus 12 unbatched. This plan's ideas sit as follows:

| Idea | Track | Group | Covered by |
|---|---|---|---|
| `000399`, `000408`, `000409`, `000394` | Governance checks, document hygiene and the portable framework | Delivery-safety gates in governance and CI | `phase-grd-01`-`04` |
| `000405`, `000406`, `000198` | Governance checks, document hygiene and the portable framework | Catalog print-versus-write and stdout contamination | `phase-grd-01` |
| `000398`, `000027` | Concurrency, claims, backlog and git safety | Lock-check blind spots and declared-path enforcement | `phase-dgov-06` (`PLAN-030`) |
| `000411`, `000412`, `000413` | not in the partition | recorded at `99bf868`, after the corpus of 383 was built | `000412` `phase-grd-01`, `000413` `phase-grd-02` |

None of this plan's ideas is among the four the owner declined or the ten held out. Where the
partition differs from this plan:

- **The rest of the delivery-safety group.** The group also holds `000400` (mutation checks) and
  `000410` (security review), which this plan leaves out by the owner's rulings (mapping Q8 and Q9),
  `000402` (consistency checks), which `PLAN-046` covers for one instance only, and `000401`
  (evidence tracing for numbers), which no plan here covers.
- **The rest of the catalog group.** `000208` duplicates `000198` and is fixed on `dev` (`--catalog`
  writes the file). `000324`, `000325`, `000335`, `000353` and `000357` are about the catalog tests
  and warnings on stdout; this plan's checks do not use `--catalog`'s stdout, so they neither fix nor
  depend on them. `000155` (the idea writer leaves `ideas.md` stale) becomes a governance failure
  under `phase-grd-01`, which reports it without fixing its cause. `000351` (regenerate the catalog
  only at merge time) points the other way from this plan, which makes the committed catalog
  stricter (OQ10).
- **The deliverables diff is in a different track.** The partition puts `000398` and `000027` under
  concurrency, with `000242`, `000245` and `000336` on what a deliverables entry means and how globs
  are read. `phase-dgov-06` stays under `PLAN-030` by the owner's ruling to move it rather than
  merge it (OQ1, D2), but its classifier reads declared deliverables, so it inherits the glob and
  directory questions those ideas raise (OQ10).

## Decisions

**D1. Three phases, not one; a fourth added by ruling.** The nine items are three new tools with
operations documents and tests, two governance checks, CI and hook changes, and procedure text in `GOV-017` and `PROMPT-037`.
That does not fit one session. The split follows what each check protects:

- `phase-grd-01` makes `dev` fail loudly on stale generated files: (b), (c), (d) and the completion
  edit. These share one fixture (a stale catalog) and one code path (the governance command), which
  is why they stay together.
- `phase-grd-02` is (a), `tools/check_dev_ci.py` and the grant rule. It shares no fixture or code
  with `phase-grd-01`; it queries `gh` and has its own operations document and tests.
- `phase-grd-03` checks what a branch brings: (e), (f) and the plan-versus-registered check, plus
  the merge-gate text that uses them. It is judged to fit one session because each of the three
  compares two known inputs and prints a difference: two JUnit reports, the added lines of one diff,
  and plan text against `backlog.yaml`. None calls a network service or changes state, and the
  acceptance for each is a short fixture table already written in `REQ-028`. If the session runs
  short, `GOV-002`'s rule applies: the unbuilt check becomes a new phase id rather than the phase
  staying labelled as one session.

(g) is `phase-dgov-06`, moved rather than merged (D2). `phase-grd-04`, the S3 `next_up` rule, was
added after review by the owner's ruling (D11). One phase per tool was rejected: the three
trunk checks would each re-edit the governance command and the same `GOV-017` passages and run in
sequence anyway. The owner ruled on 2026-09-22 that whether a phase fits one session is judged by the
agent planning it, not put to the owner; the judgement is reported here and at G3.

**D2. Move `phase-dgov-06`; do not merge it in.** `phase-dgov-06` already specifies the
deliverables-diff check against `REQ-015` R12-R13 under `PLAN-030`, with acceptance that includes a
known failing case (the `phase-prog-*` phases that rewrite `backlog.yaml` without declaring it).
Merging it into `phase-grd-03` would mean cancelling a phase another plan owns and re-deriving
acceptance that already exists, with no change to what gets built. (`PLAN-030` and `REQ-015` were
later amended on this branch for a different reason: the owner's rulings on the check's change set
and its active-branch mode, D10.)
The cost of moving it is only a queue position: `phase-gov-01` (its dependency, which it collides
with on file) and `phase-dgov-06` go in `next_up` after the guards phases, in the order the owner
ruled (OQ1). `phase-dgov-06` reports rather than blocks (`REQ-015` R13), although idea `000398`
asked for a commit-time refusal; the owner ruled that it stays report-only and that `READY` carries
its output (OQ3, D10).

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
It measures the hook's run time and records it. The owner ruled on 2026-09-23 (answer to OQ2):
"never --no-verify. Commit the fix; if the check is wrong, stop and report". `phase-grd-01` writes
that into `GOV-017` and the hook's operations document (`REQ-028` R13).

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

**D10. `READY` carries the deliverables diff once it exists.** Ruled by the owner on 2026-09-23
(answer to OQ3): "dgov-06 stays report-only, and READY carries its output". A `READY` is sent while
a phase is still active, so the owner also ruled that `phase-dgov-06` gains an active-branch mode
(`dev...agent/<phase-id>`), with `PLAN-030` and `REQ-015` R12 amended to cover it; those amendments
and the revised `phase-dgov-06` entry are made on this plan's branch. `phase-grd-03` writes the `READY`
rule in `GOV-017` and `PROMPT-037`, naming that mode and applying once it exists. The queue puts
`phase-grd-03` first, but either landing order gives the same end state.

**D11. The S3 `next_up` rule is its own phase, `phase-grd-04`.** Ruled by the owner on 2026-09-23
(answer to OQ4): "the S3 next_up rule is its own guards phase, after grd-03". The rule is the owner's
earlier ruling on idea `000394`: "S3 next_up rule refuses, grandfathers current 19". The check reads
the review records `GOV-018` writes. A phase in `next_up` needs a record that lists it, is
`dispositioned`, and has no finding whose last disposition is `escalated-g3`. The exempt set is the
19 phases in `next_up` on `dev` at `f1b891d`, listed in `REQ-028` R12. Folding the rule into
`phase-grd-03` was rejected: the owner asked for its own phase, and `phase-grd-03` already carries two
tools and a governance check. The two phases the exemption does not cover are reviewed before it lands (OQ7). The check matches by
phase id, which the owner's standing rule on id reuse makes safe (OQ8).

## Implementation phases

| Phase | What | Requirements | Depends on |
|---|---|---|---|
| `phase-grd-01` | Stale generated files fail loudly: catalog and `ideas.md` checks inside governance; the CI catalog step; governance in the pre-commit hook; the catalog regeneration named in the completion edit; the `AGENTS.md` 155-156 proposal | R01-R05, R11, R13 | none |
| `phase-grd-02` | Green `dev` CI before each grant: `tools/check_dev_ci.py`, its operations document and tests, and the grant rule in `GOV-017` and `PROMPT-037` | R06 | `phase-grd-01` (both edit `GOV-017` and `PROMPT-037`) |
| `phase-grd-03` | Branch guards: the test-baseline tool, the diff-pattern tool, the plan-versus-registered check, and the merge-gate text that uses them | R07-R10 | `phase-grd-02` (same two documents; and the governance entry point `phase-grd-01` changes) |
| `phase-grd-04` | The S3 `next_up` rule: governance refuses a queued phase with no dispositioned review record, with the 19 grandfathered | R12 | `phase-grd-03` (the governance entry point) |

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
| R12 | `phase-grd-04` | Five fixtures; the repository's result recorded |
| R13 | `phase-grd-01` | The `GOV-017` and hook operations-document diffs |

Every row maps to a phase, and each new phase carries at least one row.

## Execution order and real concurrency

Computed from declared `systems` and `deliverables` with `uv run python -m src.governance --ready`
on this branch:

- `phase-part-03` is active and declares `sys-governance`. All four guards phases, `phase-dam-01`
  (`PLAN-046`), `phase-gov-01` and `phase-dgov-06` declare it, so none can be claimed until
  `phase-part-03` completes.
- The four guards phases share `sys-governance`; the first three also share `GOV-017` and
  `PROMPT-037`, and the last two the governance entry point. They run in order.
- `phase-dam-01` shares `sys-governance`, `AGENTS.md` and `docs/08-governance/` with
  `phase-grd-01`; they cannot run at the same time.
- `phase-conc-08` (`PLAN-026`, queued, not in `next_up`) declares `sys-governance` and
  `docs/08-governance/`, so it cannot run beside any of these. Its scope applies a
  placement rule to "the governance check, catalog staleness, the private-content gate". The owner
  ruled this plan's placements directly (items (c) and (d)), so `phase-conc-08` records them as
  given; if its rule then concludes otherwise, that is a finding for the owner, not a reason for
  this plan to wait.

Real concurrency is one of these phases at a time. The `next_up` order, ruled by the owner on
2026-09-23 (answer to OQ1), is `phase-grd-01`, `phase-grd-02`, `phase-dam-01`, `phase-grd-03`,
`phase-gov-01`, `phase-dgov-06`, after `phase-part-03` and before `phase-cap-08`. `phase-grd-04` is
placed directly after `phase-grd-03`, per the owner's answer to OQ4. `phase-grd-01` goes first so its
check catches a stale catalog in every later phase's own commits.

## Out of scope

- **Cleaning up the 25 existing type-ignore comments and the except-pass sites.** R08 checks added
  lines only; the existing sites are a separate decision because some are explained (`intake.py:90`
  names a gap in LangGraph's type stubs).
- **Mutation testing** (idea `000400`). The owner's Q8 ruling named `000408`, `000409` and S7 only.
- **Automatic merge by a non-builder session.** Scout O-3 kept builders' self-merge under `GOV-017`
  until P3's merge-gate nodes exist.
- **Security review** (idea `000410`, mapping Q9). It changes the plan standard and the merge
  gate's reviewers, not a deterministic check.

## Open questions

Closed on 2026-09-23: owner rulings relayed by the Session Manager, and items the planner resolved
(OQ5 by Ideation's records, OQ6 against the accepted partition):

- **OQ1. Queue position.** Ruled: "queue after part-03 is grd-01, grd-02, dam-01, grd-03, gov-01,
  dgov-06, then cap-08, as proposed." Applied in `next_up`, with `phase-grd-04` after `phase-grd-03`
  (OQ4).
- **OQ2. Hook bypass.** Ruled: "never --no-verify. Commit the fix; if the check is wrong, stop and
  report." Applied in D5, `REQ-028` R13 and `phase-grd-01`.
- **OQ3. Report or refuse for the deliverables diff.** Ruled: "dgov-06 stays report-only, and READY
  carries its output." Applied in D10, `REQ-028` R10 and `phase-grd-03`.
- **OQ4. The S3 `next_up` rule.** Ruled: "the S3 next_up rule is its own guards phase, after grd-03."
  Applied as `phase-grd-04` (D11, `REQ-028` R12).
- **OQ7. `phase-gov-01` and `phase-dgov-06` under the S3 rule.** Neither is among the 19 exempt
  phases nor reviewed. Ruled: "review gov-01 and dgov-06 before grd-04 lands"; the Session Manager
  assigns those reviews to the Standby Builder. Applied: `phase-grd-04`'s next action and acceptance
  check for the two records.
- **OQ8. Reused phase ids.** Correction recorded here: when this plan split its phases after the first
  review, it reused the id `phase-grd-02` for a different phase, and the first review record lists
  `phase-grd-02` for content that is now `phase-grd-03`. Ruled: "a STANDING rule that a phase id is
  never reused for different content, recorded in GOV-003 through dam-01". Applied: `PLAN-046` D4
  and `REQ-029` R08. The later-added review (`2026-09-23-plan-045-later-added`) covers the instance;
  its finding F01 carries the owner's disposition.

- **OQ5. The Scout's two CI ideas.** Resolved: recorded as `000412` and `000413` at `99bf868` and
  cited in Context and scope.

- **OQ9. How `phase-dgov-06` attributes commits to a completed phase.** The first ruling kept only
  commits whose message names the phase; the `GOV-018` review of `phase-dgov-06`
  (`2026-09-23-plan-030`, F01) found it drops the phase's own registering commits (`3da1295` for
  `phase-prog-04`, `744d4c8` for `phase-prog-05`). Ruled: "INVERT the filter. Keep every commit in
  the claim..completion first-parent range, except those naming a different phase id. This
  supersedes the earlier message-filter ruling." Applied: `REQ-015` R12, `PLAN-030` section 5,
  `phase-dgov-06`.

- **OQ6. Partition reconciliation.** Done against the accepted partition (`6051dad`); see
  "Partition placement" in Context and scope. The two differences that need the owner are OQ10.

Still open:
- **OQ10. Two partition differences.** (a) `000351` asks to regenerate the catalog only at merge
  time; `phase-grd-01` makes a stale committed catalog fail governance, CI and the hook, which
  entrenches the committed catalog `000351` would drop. Who: the owner, at G3. Leaning: proceed with
  `phase-grd-01`; `000351`'s triage finding already notes that dropping the committed catalog would
  reverse `phase-doc-02`'s accepted design and needs its own ruling. (b) `phase-dgov-06` compares a
  change set against declared deliverables, and the partition groups it with `000336` (globs read as
  literal filenames) and `000245` (what a deliverables entry means). Who: the owner, at G3. Leaning:
  add one scope line to `phase-dgov-06` that it matches directory deliverables by prefix and glob
  deliverables by pattern (`path_conflict` in `src/governance/backlog.py` already matches directories
  by prefix), and leave `000336`'s fix to the lock itself to its own track.
