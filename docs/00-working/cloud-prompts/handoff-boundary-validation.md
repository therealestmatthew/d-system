# Handoff: boundary validation

*Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock against it.*

## 1. Branch and tip

- Branch: `agent/cloud-boundary-validation`
- Tip of the last content commit: `afddda1`. This handoff and the `status.md` row are committed
  together on top of it; that commit's hash is the branch head after the final push.
- Rebased onto: `origin/dev` at `9772c21`. `git fetch origin dev && git rebase origin/dev` reported
  the branch up to date, because `origin/dev` had not moved since the session started.

## 2. What changed

- `docs/00-working/cloud-prompts/status.md`: row 2 (plan anatomy) marked `merged` with tip `9772c21`;
  row 3 set to `in progress` at start and `ready` at the end.
- `docs/07-architecture/ARCH-012-system-boundary-decision-report.md`: the default-entry-point split
  corrected from 13 / 14 / 12 / 1 to 15 / 18 / 7 / 0, old values kept with the date; `updated`
  2026-09-28. No reasoning, option or recommendation changed.
- `docs/00-working/boundary-study/prompt-navigation-findings.md`: "Twenty-three" corrected to
  "Twenty-six", with a dated note (owner-approved in this session).
- `docs/01-plans/PLAN-050-system-boundary-study/PLAN-050-overview.md`: dated amendment note,
  rejected-alternatives table, next steps per option, requirement coverage and concurrency for
  them, failure paths, three new open questions.
- `docs/01-plans/PLAN-050-system-boundary-study/PLAN-050.01` to `.05`: a *When a check fails*
  paragraph each; `.02` and `.03` gain *Execution order and real concurrency*.
- `docs/09-backlog/backlog.yaml`: `phase-bnd-06` to `phase-bnd-14` added, all `deferred`, priority 4,
  none in `next_up`; `updated` 2026-09-28.
- `docs/08-governance/reviews/2026-09-28-plan-050.json`: new review record, nine findings, status
  `dispositioned`.
- `docs/00-working/boundary-study/validation-report.md`: new; the validation report.
- `docs/00-working/boundary-study/boundary-overview.html`: new; the one-page overview.
- `docs/00-working/boundary-study/build_boundary_overview.py`: new; generates the HTML and the report's
  per-system and per-prompt tables from git at named commits.
- `docs/00-working/cloud-prompts/handoff-boundary-validation.md`: this file.
- `docs/08-governance/catalog.md`: regenerated after every governed change; unchanged in content.

## 3. Codes allocated

None. No governed document was created, so `--next-code` was not run. The review record and the
working files carry no code.

## 4. Review verdicts

All dispatches used `partition-adversary` (read-only). None used `general-purpose`.

**Plan altitude**, `PROMPT-038` with the prompt's additions (re-derive the four figures; attack
rejecting C and recommending A). Recorded as F01 to F06 in the review record:

| Id | Severity | Finding | Disposition |
|---|---|---|---|
| F01 | blocker | `ARCH-012`'s "no concern ready for extraction" is contradicted by the built plugin | escalated-g3 (`phase-bnd-10` added; `ARCH-012` wording proposed in the report's section 6) |
| F02 | major | Entry-point classification inconsistent across identical prompts | fixed (`ARCH-012` figure, report section 2.2, `phase-bnd-08`); its `PROMPT-025` example rejected as wrong |
| F03 | major | No decision names its rejected alternative (`GOV-010` P2) | fixed (overview *Chosen design*) |
| F04 | major | No failure paths | fixed (overview and five children) |
| F05 | minor | 40 prompts is drift | accepted-no-change |
| F06 | minor | Claim limit fully occupied is drift | accepted-no-change |

**Later-added-phase altitude**, `PROMPT-038` over `phase-bnd-06` to `-13` (F07 to F09):

| Id | Severity | Finding | Disposition |
|---|---|---|---|
| F07 | blocker | `phase-bnd-07` is a registry edit, which `ARCH-012` says choosing A does not cause | fixed (needs the owner's separate approval) |
| F08 | major | `phase-bnd-08` too large for one session | fixed (split; `phase-bnd-14` added) |
| F09 | minor | `phase-bnd-09` has no constructed failing case | fixed (control question) |

**Final review of the report**, with the brief in `boundary-validation.md` plus the six phase checks
on `phase-bnd-14`. The agent reached its turn limit and was asked to report from what it had
checked. It reported these checks as not completed and taken on trust: the registry recount, the
domain counts, the dependency depths, the plan counts and the test-collection counts. All five were
derived in this session by command (report section 2.1). Findings:

| # | Severity | Finding | Disposition |
|---|---|---|---|
| R1 | blocker | The handoff file does not exist and `status.md` still reads `in progress` | rejected: the prompt orders the handoff after the gates, and the review ran before them. This file and the row update close it |
| R2 | major | `phase-bnd-14`'s acceptance does not require settlements to cite a line | fixed (`afddda1`: new acceptance line) |
| R3 | minor | `phase-bnd-*` phases lock `sys-gov-docs` while their deliverables sit outside `docs/08-governance/` | accepted-no-change: the same convention as `phase-bnd-01` to `-05`, and the validator does not check path membership; listed as an idea below |
| R4 | minor | The independent analyst's raw classification was not persisted | fixed (`afddda1`: an *Independent analyst* column in report section 2.2, kept in the script) |

A `partition-analyst` dispatch did the independent prompt classification (report section 2.2). It
was a classification, not a review.

## 5. Gate output (last ten lines of each)

`uv run python -m src.governance` (exit 0):

```
Governance OK: 43 systems, 398 documents, 34 memories, 341 backlog phases
exit=0
```

`uv run pytest` (exit 0):

```
test/test_workbench_layout_schema.py .....................               [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/starlette/testclient.py:53
  /home/user/d-system/.venv/lib/python3.12/site-packages/starlette/testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============ 1156 passed, 1 skipped, 1 warning in 247.60s (0:04:07) ============
exit=0
```

`uv run ruff check src/ test/` (exit 0):

```
All checks passed!
exit=0
```

`uv run mypy src/` (exit 0):

```
Success: no issues found in 46 source files
exit=0
```

Each gate ran once after the last content commit and passed. Also run: the staged private-content
check before every commit (OK every time; `_private/portfolio/` is absent in this clone, so only
the path check ran), `git diff --exit-code docs/08-governance/catalog.md`, and
`uv run pytest test/test_adversarial_finding_schema.py` (101 passed). The generator script is
outside the gated paths. `ruff check` on it reports 118 `E501` line-length findings in its embedded
CSS and HTML strings, and no others.

**The HTML was seen rendered.** Chromium through the pre-installed Playwright: full-page screenshots
at 390px and 1440px, light and dark. Page scroll width equalled the viewport at both widths after one
fix, and no external request was made. It parses with `html.parser`; `grep` finds no `http`, `src=`
or `@import`.

## 6. Ideas for local Ideation

- The registry lists the eight `sys-plugin*` systems and `sys-demo-overview` as `planned`, while
  tracked code and completed phases (`phase-plug-01` to `-09`, `phase-demo-03` and `-04`) show them
  built. Correct `systems.yaml`.
- `GOV-002` says "this repository sets `3`" for `max_active`; `backlog.yaml` sets `4`.
- CI does not run the idea-realization plugin's own test suite (`pyproject.toml`
  `testpaths = ["test"]`), and at `9772c21` that suite has 3 failing tests
  (`test_no_source_references.py::test_plugin_names_no_source_instance` and two cases of
  `test_templates.py`).
- The backlog validator does not check that a phase's `deliverables` lie under its declared
  `systems`' paths. `phase-bnd-01` to `-14` lock `sys-gov-docs` (`docs/08-governance/`) while
  writing to `docs/00-working/`, `docs/02-prompts/` and `docs/07-architecture/`.
- Review procedures that summarise a subagent's classification should commit its raw output before
  summarising it (final review, R4).
- `GOV-018`'s entry check, run on child plans, returned `PLAN-050.02` and `.03` for a missing
  execution-order section. Other child plans may carry the same gap.

## 7. Open owner questions and stated assumptions

**Open questions**

1. **Option A, B or C.** The owner decides at `ARCH-012`'s owner decision gate, after reading the
   validation report. The study recommends A. The validation does not choose. It finds the evidence
   still favours A, strengthens the rejection of C, and shows B's plugin candidate to be further
   along than the study recorded.
2. **F01, escalated to G3.** Adopt the seven `ARCH-012` wording changes in the report's section 6
   before deciding? They were not applied because the 2026-09-27 ruling limits this session to
   figure corrections.
3. **Separate `GOV-018` reviews for the five child plans?** `GOV-018` says each child is its own
   target; this review read them as part of the plan. The reviewer's leaning is no: all five phases
   are complete.
4. **`phase-bnd-07`** now needs the owner's own approval of a registry change, beyond choosing A.

**Stated assumptions**

- "Tip" for every figure is `origin/dev` at `9772c21`, where the session started. `origin/dev` had
  not moved at the end.
- The default-entry-point figure uses the rubric's own pilot reading (position in a sequence),
  applied to every prompt. The rule difference is stated in report section 2.2.
- Each system's concern comes from the study's system inventory, which gives one disposition per
  system. Nine are marked contested, not reassigned.
- `deferred` was used for the next-step phases, per `GOV-002` ("deliberately postponed"). The
  validator accepted it, and `--ready` offers none of them.
- The study's baselines were read through scratch `git worktree add --detach` copies in the
  session's scratch directory, outside the clone. All were removed before the handoff.

No change to `AGENTS.md` or `CLAUDE.md` is proposed.
