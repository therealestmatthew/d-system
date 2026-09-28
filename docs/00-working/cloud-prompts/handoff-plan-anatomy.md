# Handoff: plan anatomy investigation (idea 000505)

*Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock against it.*

## 1. Branch and tip

- Branch: `agent/cloud-plan-anatomy`.
- Rebased onto `origin/dev` at `518188a`. `git rebase origin/dev` reported "Current branch
  agent/cloud-plan-anatomy is up to date".
- Content tip, on which the gates ran: `c3b8618`. The commit that adds this handoff file and sets
  the tracker row to `ready` sits on top of it and changes only those two ungoverned files.
  `git log -1 origin/agent/cloud-plan-anatomy` gives the final tip.

Commits on the branch:

```text
c3b8618 Plan anatomy: disposition the second adversarial pass
08c4778 Plan anatomy: count heading words in the decisions total so the published shares reproduce
2c3d9ae Plan anatomy: findings and proposed plan-folder standard (000505)
b2242aa Plan anatomy: inventory of plans, plan folders and their artifacts (000505)
28ecf34 Cloud prompts: start plan anatomy investigation
```

## 2. What changed

- `docs/00-working/plan-anatomy/inventory.md` (added): every plan, every plan folder, where each
  plan's artifacts live and how they link back, what the clone cannot see, and what code depends on
  the layout. Every count has a command.
- `docs/00-working/plan-anatomy/findings.md` (added): answers to the owner's four questions, with
  costed options and a recommendation for each, kept apart from the measurements; seven other
  findings.
- `docs/00-working/plan-anatomy/proposed-standard.md` (added): a proposed plan-folder layout,
  marked as a proposal, with a worked example from the plugin audit remediation plan
  (`PLAN-052`), what stays outside the folder, the overlap with `phase-idg-11`, twelve owner
  decisions (A to L), and candidate work.
- `docs/00-working/plan-anatomy/measure.py` (added): the read-only script behind the inventory's
  counts.
- `docs/00-working/cloud-prompts/status.md` (modified): row 1 marked `merged` (tip `280584c`), this
  row `in progress`, then `ready`.
- `docs/00-working/cloud-prompts/handoff-plan-anatomy.md` (added): this file.

No file was moved, renamed or deleted. No governed document, backlog phase or idea was written.

## 3. Codes allocated

None. `ADR-019` and `GOV-011`, reserved for `phase-idg-11`, were not taken.

## 4. Review verdict

Agent type `partition-adversary`, dispatched twice. The first dispatch used the prompt's brief
verbatim, with `{ABS}` replaced by `/home/user/d-system`. It stopped at its 50-turn limit and was
asked to report what it had verified. It left checks 2 (four of seven traces), 3 (part), 4 (the
search for unstated contradictions) and 5 unfinished. The second dispatch gave those unfinished
checks as a narrowed brief, with the same read-only rule.

First pass:

| # | Severity | Finding | Disposition |
|---|---|---|---|
| 1 | major | `measure.py decisions` left heading words out of the body total, so its shares did not reproduce the published table (for example `PLAN-045` 42% against 41% published) | **fixed** in `08c4778`: heading words now count toward the total; all seven published rows reproduce exactly |
| 2 | — | Coverage arithmetic holds: 81 plans, table matches the catalog and the script output byte for byte | no finding |
| 3 | — | Traces of `PLAN-029`, `PLAN-048`, `PLAN-052` hold | no finding |
| 4 | — | Section 5 line citations, the entry-check fault, and layout tests (a), (b), (d) reproduce | no finding |
| 5 | — | `phase-idg-11` and the quoted `GOV-010`, `GOV-018` text match | no finding |
| 7 | — | Scope: only the plan-anatomy files and `status.md` changed | no finding |

Second pass:

| # | Severity | Finding | Disposition |
|---|---|---|---|
| 1 | major | `findings.md` section 4 ended with a judgement ("is borne out", "has no reason recorded") under no recommendation heading | **fixed**: moved under a "Reading (this session's view, not a measurement)" heading and reworded to state an absence of evidence |
| 2 | minor | The "folder only pays for itself" paragraph sat under Options | **fixed**: moved under Recommendation |
| 5 | major | The `GOV-008` row in the proposal's contradiction table understated the conflict: four `GOV-008` stages are one-build prompts, not only the pre-plan package | **fixed**: the row and decision E now name Prompt A, Prompt B, the coordinator and the kick-off record |
| 6 | — | Splitting decisions out does not drop any checked plan below the two-phase-id threshold for the Execution order section | no finding |
| 7 | minor | `.claude/skills/partition-ideas/SKILL.md:203` reads `docs/02-prompts/PROMPT-034-…` by path and was not listed | **fixed**: added to inventory section 5 |
| 8 | — | The plugin's `plan_check.py` resolves ids at any depth, as the inventory says | no finding |
| 9 | minor (unranked by the reviewer) | Layout test (e) reproduced with six missing sections, not seven | **fixed**: the test's `depends_on` is now stated; the seventh, "Requirement coverage", is the entry-check fault, and the row says so |
| 10 | major | The trace table had no row for other documents a plan's own `depends_on` names (governance, architecture, other plans), so `PLAN-050`'s dependency on `PLAN-039`, `ARCH-002` and `GOV-008`, and `PLAN-023`'s on `GOV-009`, were missing | **fixed**: a row added to inventory 3.7 for all seven plans; a row added to findings section 4 and to the proposal's outside-the-folder table. The reviewer's aggregate ("5 plan families … 10") counted documents, not plans; it was re-measured as 23 of 49 families naming a governance document, 13 another plan, 6 an architecture document |
| 11 | — | `PLAN-023` and `PLAN-050` session counts and decision headings hold | no finding |

## 5. Gates

Run on `c3b8618` after the rebase. Last ten lines of each, verbatim.

`uv run python -m src.governance`:

```text
Governance OK: 43 systems, 398 documents, 34 memories, 332 backlog phases
exit=0
```

`uv run pytest`:

```text
test/test_workbench_layout_schema.py .....................               [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/starlette/testclient.py:53
  /home/user/d-system/.venv/lib/python3.12/site-packages/starlette/testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============ 1151 passed, 1 skipped, 1 warning in 252.94s (0:04:12) ============
exit=0
```

`uv run ruff check src/ test/`:

```text
All checks passed!
exit=0
```

`uv run mypy src/`:

```text
Success: no issues found in 46 source files
exit=0
```

## 6. Ideas for local Ideation

- The `GOV-018` entry-check script's `depends_on` lookup searches `docs/*/*.md` only, and `xargs -r`
  exits 0 on empty input, so it demands "Requirement coverage" from any plan that depends on a
  document inside a plan folder (11 of 13 entry-check failures today).
- `GOV-005`'s "a plan set lives in a folder" is not enforced by `naming_errors`; `PLAN-039.01` is
  the one child plan stored flat.
- `docs/01-plans/README.md` is stale: it says to name plans `YYYY-MM-DD-topic.md` and mentions root
  `plans/` paths, which `PLAN-018` retired.
- Pre-plan packages name the wrong plan: `PROMPT-020` names `PLAN-021`, and `PROMPT-025` and
  `PROMPT-026` name `PLAN-016`, because each was written before the plan it led to existed.
- `PLAN-048` and `PLAN-052` cite six `_working/` paths as evidence, which no clone can open.
- Records produced by phases are typed as child plans (`PLAN-048.10`, `PLAN-048.11`, trace tables
  of 13,915 and 18,945 words) because only plan documents can be Markdown in a plan folder.

## 7. Open owner questions and stated assumptions

Owner decisions, from `proposed-standard.md`, each with its recommendation there:

- A. Is every new plan a folder? (yes)
- B. Are the 44 existing single-file plans migrated? (no)
- C. Are decisions split into a one-line ruling in the plan and a record beside it? (yes, new plans)
- D. Is the decision record an uncoded member file `decisions.md`? (yes)
- E. Do one-time prompts go in a `prompts/` member folder? (yes, boundary per `000501`; may reach
  four `GOV-008` stages)
- F. Do review records stay in `docs/08-governance/reviews/`? (yes)
- G. Is there an `evidence/` member, and is `_working/` evidence a plan relies on copied into it? (yes)
- H. Is the entry point always `PLAN-NNN-overview.md`? (yes)
- I. Is the `GOV-018` entry-check script fixed now, independently? (yes)
- J. What happens to the flat child `PLAN-039.01`? (leave as the recorded exception; enforce for
  new children)
- K. Is this settled before `phase-idg-11` runs? (yes, or give `phase-idg-11` this proposal as input)
- L. Does the plugin adopt the same standard? (decide after the repository does)

Assumptions stated and not asked, because none changed what the inventory measures:

- "A plan" is every `kind: plan` document in the catalog, including the two trace tables typed
  as plans.
- An artifact "belongs" to a plan when it was written for it; documents that only cite a plan as an
  example were left out of the seven traces.
- The proposal covers this repository only; the plugin's copy of the rules is listed as decision L.

The planning protocol (`GOV-021`) was read. Nothing in it is contradicted by the inventory. It
points to `GOV-005` "Assigning a code" for step 6 and not to `GOV-005` "Multi-file plans", which is
where the current folder rule is written. No change to `AGENTS.md` or `CLAUDE.md` is proposed.
