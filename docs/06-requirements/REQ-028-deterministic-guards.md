---
schema_version: 1
id: doc-deterministic-guards-requirements
code: REQ-028
title: Deterministic guards requirements — a trunk that cannot go red unnoticed, and branch checks that refuse lost tests, silenced type errors and unplanned phases
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-governance, sys-backlog, sys-gov-docs]
depends_on: [doc-multi-session-coordination-protocol, doc-backlog-decisions]
---

# Deterministic guards requirements

Observable statements for the deterministic guards the owner ruled on 2026-09-23. The plan that
delivers them is [PLAN-045](../01-plans/PLAN-045-deterministic-guards.md).

## Observed problem and scope

Each failure below is recorded in the repository or in the idea log, with its source.

1. **`dev` was red for days and no session acted on it.** CI failed on 30 consecutive pushes to
   `dev`, starting at `77cbbd9` (2026-09-16 23:45 EDT) (Scout report
   `_working/session-manager/scout/orchestration-1-evidence.md`, headline 1, which also corrects
   the "23 consecutive runs" in idea `000399`'s triage finding). Nothing in the
   multi-session protocol (`GOV-017`) reads the CI result before a session is given the primary
   checkout.
2. **CI's catalog step cannot fail.** `.github/workflows/ci.yaml` runs
   `uv run python -m src.governance --catalog > /tmp/catalog.md` and then diffs
   `docs/08-governance/catalog.md` against `/tmp/catalog.md`. `--catalog` writes the file and then
   prints the same text (`src/governance/__main__.py`, the `elif args.catalog` branch:
   `write_catalog(ROOT, rendered)` then `print(rendered)`), so the two sides are always equal.
   `AGENTS.md` lines 155-156 say "CI diffs it and fails when it is stale". A stale catalog is
   caught in CI today only by `test_committed_catalog_matches_regenerated_output` in the pytest
   step (`test/test_codes.py:177`).
3. **The governance check passes with a stale catalog or a stale `ideas.md`.** Two writes to `dev`
   on 2026-09-23 ran governance only and left `dev` red: `024443c` omitted the regenerated
   `docs/00-working/ideas.md`, and `f6216e9` (completing `phase-irs-06`) changed `backlog.yaml`
   without regenerating the catalog, fixed by `b928817` (ideas `000405`, `000406`, `000198`).
   `GOV-017`'s merge-gate step 6 and `PROMPT-037` item 4(iii) say the completion edit runs
   "governance only" and do not name `--catalog`.
4. **The pre-commit hook does not run governance.** `tools/git-hooks/pre-commit` runs only
   `tools/check_no_private_content.py`. `core.hooksPath` in this repository is
   `/code/d-system/tools/git-hooks`, so every worktree runs the primary checkout's copy of the hook.
5. **Nothing notices a deleted or newly skipped test.** No stored baseline of passed or skipped
   tests exists and neither the merge gate nor CI compares counts (idea `000409`, triage finding).
6. **Silenced type errors enter unreviewed.** 25 `# type: ignore` comments that are not
   `import-untyped` exist across `src/`, `tools/` and `test/`, including logic-level ones at
   `src/orchestrator/graphs/intake.py:90` and `tools/generate_ideas_md.py:73-135` (idea `000408`,
   triage finding). Ruff selects only `E`, `F`, `I` and `UP`.
7. **A plan and its registered phases can drift apart.** Of the 40 plans in `docs/01-plans/` that
   have registered phases, 25 do not name 92 of those phases anywhere in their text (measured on
   `dev` at `f1b891d` with a script that compares each phase whose `plan` is the document's `id`
   against the `phase-…` ids in that document's text). The one such plan created on or after
   2026-09-20 (`PLAN-043`) names all four of its phases. No plan names a phase id that is not
   registered. The owner ruled on 2026-09-23 (Scout decision O-4 (b)) that planning keeps
   registering phases on its own branch through G4, with a plan-versus-registered check in this
   guards work.

Scope: the checks, their placement in the governance command, CI, the pre-commit hook and the
multi-session merge gate, and the text changes that make each one part of the procedure. The
deliverables-diff check (idea `000398`) is already specified as `phase-dgov-06` under `REQ-015`
R12-R13 and is not restated here (`PLAN-045`, Decisions).

## Observable requirements and verification

| ID | Required observable behaviour | Verification |
|---|---|---|
| R01 | `uv run python -m src.governance` exits 1 with an error naming `docs/08-governance/catalog.md` when the committed catalog differs from the rendered one, and exits 0 once `--catalog` has been run. Running the plain check writes no file | On a scratch branch, change one phase's `status` without regenerating: exit 1 naming the catalog. Run `--catalog`: exit 0. Run the plain check on a clean tree and confirm `git status --porcelain` is empty afterwards |
| R02 | The same command exits 1 with an error naming `docs/00-working/ideas.md` when that file differs from what `tools/generate_ideas_md.py` renders from the idea log, and exits 0 after regeneration | Append an idea to a scratch copy of the log through the sanctioned writer without regenerating: exit 1 naming `ideas.md`. Regenerate: exit 0 |
| R03 | CI fails on a commit whose committed catalog is stale, at a step that compares the committed file with a rendering that did not overwrite it | Run the CI job's Python steps locally on a scratch commit with a stale catalog: a nonzero exit before pytest starts. The same steps on `dev` exit 0 |
| R04 | The pre-commit hook refuses a commit when the governance check fails, and still runs the private-content check | In a scratch worktree, stage a stale-catalog change and run `sh tools/git-hooks/pre-commit` directly (a plain `git commit` there runs the primary checkout's copy of the hook, because `core.hooksPath` is shared): exit nonzero, with the governance error printed. Regenerate and run it again: exit 0. A staged private identifier fixture still makes it exit nonzero |
| R05 | The completion-edit instructions name the catalog regeneration: `GOV-017` merge-gate step 6, `PROMPT-037` contract item 4(iii) and `PROMPT-037`'s builder role script (the step that says "the completion edit on dev as GOV-003 sanctions") all say to run `--catalog` and commit the result with the edit | Read the three passages; `grep -n "governance only"` in `PROMPT-037` returns no completion-edit line. A completion edit made without the regeneration fails R01's check before it can be committed (R04) |
| R06 | `tools/check_dev_ci.py` exits 0 only when the most recent completed CI run for `dev`'s current head commit succeeded; exits 1, naming the run's URL, when that run failed; and exits 2 when no completed run exists for that commit or the `gh` query fails. `GOV-017` and `PROMPT-037` require a 0 before any `GRANTED` | Unit tests with recorded `gh run list` JSON for five cases: success at head (0), failure at head (1), in progress (2), a run only for an older commit (2), `gh` error (2). Read the two passages |
| R07 | A test-baseline check compares a base run and a branch run of the suite and exits 1, listing the test ids, when a test that passed in the base is missing from the branch run or is skipped there. Added tests and tests that were already skipped do not fail it | Unit tests over pairs of JUnit XML fixtures: one removed test (1), one newly skipped test (1), one added test (0), an unchanged run (0), a test skipped in both (0) |
| R08 | A diff-pattern check over `<base>..<head>` exits 1, naming file and line, for each **added** line containing a `# type: ignore` whose code list is not exactly `[import-untyped]`, a `cast(Any,` call, or an `except` clause that is bare or catches `Exception` or `BaseException` and whose body is only `pass`. Unchanged and removed lines are never reported, and an `except` naming a specific exception type with a `pass` body is not reported | Unit tests over fixture diffs for each pattern (1), for `# type: ignore[import-untyped]` (0), for `except FileNotFoundError: pass` (0), for an unchanged existing ignore in context lines (0), and for a removed ignore (0). Run against `dev~20..dev`: its output is recorded, whatever it is |
| R09 | The governance check exits 1 when a phase registered with `plan: <id>` is not named by id anywhere in that plan's text, for plans whose `created` date is on or after 2026-09-22; and when any plan names a `phase-…` id that is registered nowhere, for every plan | A fixture plan dated 2026-09-23 with an unnamed registered phase: exit 1 naming both. The same plan dated 2026-09-21: exit 0. A fixture plan naming `phase-zzz-99`: exit 1. The repository as it stands: exit 0, with the counts recorded |
| R10 | The merge gate names the new checks: a `READY` carries the output of R07's and R08's checks, and a nonzero result from either proceeds only with the owner's recorded sign-off naming the tests or lines it accepts | Read `GOV-017`'s merge gate and `PROMPT-037` item 4 |
| R11 | `AGENTS.md` lines 155-156 describe what CI and the governance check actually do, in wording the owner approved for that specific change; if the owner has not approved it, the lines are unchanged and the session record says so | `git diff` of `AGENTS.md` shows either the approved text or nothing; the session record names which |

## What each requirement is not

- **R01 and R02 do not make governance regenerate anything.** The check compares and reports. The
  write stays with `--catalog` and `tools/generate_ideas_md.py`.
- **R03 does not require a new CI job.** Correcting the existing step satisfies it.
- **R04 is not a pre-push or merge hook.** It fires on commits in whichever checkout makes them.
  `refuse_dirty_integration.py` keeps its own placement (`OPS-001`).
- **R06 does not decide what happens while CI is running.** Exit 2 means "not yet known"; the
  Session Manager waits or asks the owner. It is not a rule that a grant is refused forever.
- **R07 is not a coverage or test-count target.** It compares one run against another and says
  nothing about how many tests a phase should add.
- **R08 does not ban the patterns in existing code.** Only added lines are checked. Cleaning up the
  25 existing ignores is separate work.
- **R09 does not check the order, titles or dependencies of phases** named in a plan, only that the
  ids on each side match. It does not apply the first direction to plans created before
  2026-09-22, the date `GOV-010`'s own scope starts.
- **R11 is not approval to edit `AGENTS.md`.** Approval is given by the owner for that change, per
  `AGENTS.md`'s own rule.
