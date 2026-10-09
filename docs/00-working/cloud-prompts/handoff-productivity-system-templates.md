# Handoff: productivity-system review, portfolio guide, template exploration and GOV-022

*Ran unclaimed: owner-directed work with no backlog phase; no peer holds a lock against it. Not a
row of `status.md`: this session ran from the owner's own kickoff, not from `master-prompt.md`, and
its hand-off follows the shape `GOV-022` prescribes.*

## 1. Branch and tip

- Branch: `claude/productivity-system-templates-ie1x8d` (assigned by the cloud harness).
- Cut from `origin/dev` at `6951bb6`. `origin/dev` had not moved when the final gates ran.
- Tip when the gates ran: `acd52ba`. Commits after it: the guide page citing the recorded idea ids
  (`197a246`, `_public/` only), the hand-off (`0f673e4`), the GOV-022 amendment recording the
  owner's orchestrator-only ruling (`1f84815`), and the final commit adding the brain procedure, its
  index line, two GOV-022 cross-reference edits and this hand-off update. Governance was re-run on
  each; the gate output in section 5 is from `acd52ba`.
- The clone opened shallow (52 commits). `git fetch --unshallow origin dev` was run for the gate;
  see section 5.

## 2. What changed

- `docs/08-governance/GOV-022-single-session-orchestration-protocol.md`: added, `status: draft`.
  The multi-session coordination protocol (`GOV-017`) restructured for one session that runs
  subagents in its own checkout. Collapses the roster into the session, drops the
  primary-checkout lock, turn messages, claim slots and the board, keeps every trunk and review
  protection, adds the subagent model-tier and dispatch rules, the hand-off shape and a kickoff
  text. Every rule not already in `GOV-017` or `GOV-013` is marked **proposed**; six open
  questions.
- `brain/procedures/an-orchestrator-dispatches-the-writing-too.md` and its `brain/index.md` line: added, on the owner's approval of the text, recording the orchestrator-only correction (section 6, item 1).
- `GOV-022`: amended after the owner's correction with the subsection *The session writes no deliverable* (owner ruling, 2026-10-08), a first dispatch rule, a hand-off clause and the brain cross-reference.
- `docs/08-governance/catalog.md`: regenerated for the new document.
- `_public/portfolio-guide.html`: the executive guide to the personal productivity system, set in
  the house family with native `<details>` cards and no script: records, data flow, using it
  today, built versus planned, open work, the four template families, the timeline and Gantt
  assessment, twelve further proposals, a build order, and decisions for the owner. Also published
  as a private claude.ai artifact (link given to the owner in the session).
- `_data/ideas.jsonl`: sixteen ideas appended through `tools/append_idea.py add --file`, ids
  `000673` to `000688` (section 3). `docs/00-working/ideas.md` regenerated.
- This file.

Commits: `7537268` (GOV-022, catalog, guide), `acd52ba` (the sixteen ideas and `ideas.md`), then
the guide citation and this hand-off.

## 3. Codes and ids allocated

- `GOV-022` (`uv run python -m src.governance --next-code governance`, run once, after
  `uv sync --extra dev`). `--next-code` reserves only on this machine, so the gate should check it
  is still free on current `dev`.
- Ideas `000673` to `000688`, taken from `append_idea.py`'s own output after `git fetch origin dev`
  showed `origin/dev` at `6951bb6` (last idea there: `000599`). If ideas were recorded on `dev`
  after that, these ids collide and `_data/ideas.jsonl` conflicts on rebase; `GOV-022` Open
  question 3 is this hazard. The ids and titles:

  | Id | Title |
  |---|---|
  | 000673 | Template: simple timeline of a project's dated events |
  | 000674 | Template: Gantt chart, project level first |
  | 000675 | Template: commitments ledger |
  | 000676 | Template: portfolio dashboard |
  | 000677 | Template: one-page project brief |
  | 000678 | Template: person profile and stakeholder card |
  | 000679 | Template: kanban status board |
  | 000680 | Template: agenda and calendar view |
  | 000681 | Template: waiting-on board |
  | 000682 | Template: stale radar and review queue page |
  | 000683 | Template: weekly review page |
  | 000684 | Template: decision register |
  | 000685 | Template: commitment velocity trend |
  | 000686 | Template: RACI and role matrix |
  | 000687 | Shared portfolio data loader and a richer fictional fixture set |
  | 000688 | phase-syn-05 depends on the cancelled phase-html-10 and a retired page pipeline |

## 4. Review

No adversarial review was dispatched. The owner's kickoff asked for a review-and-summarise pass, an
artifact, a template exploration and the protocol restructuring, and set the subagent budget at
Haiku by default with Sonnet as the ceiling; it did not ask for a review of the outputs. `GOV-022`
is `draft` and its *Reviews in a single session* section says what a review of it would need. The
gate may dispatch one (`partition-adversary`, Sonnet, brief: `GOV-022`, `GOV-017`, `GOV-013`, the
three `cloud-prompts` hand-offs; nothing from this session's reasoning).

## 5. Gate output

Run in this clone at `acd52ba` after `uv sync --extra dev` and `cd ts && npm ci`.

```text
$ uv run python -m src.governance
Governance OK: 45 systems, 456 documents, 37 memories, 347 backlog phases

$ uv run ruff check src/ test/ tools/
All checks passed!

$ uv run mypy src/
Success: no issues found in 50 source files

$ uv run python tools/check_diff_patterns.py origin/dev..HEAD
Diff patterns OK: no added type-ignore, cast(Any, or broad except/pass in origin/dev..HEAD.

$ cd ts && npm test
 Test Files  2 passed (2)
      Tests  7 passed (7)

$ uv run pytest -q  (shallow clone, 52 commits)
4 failed, 1649 passed, 1 skipped, 1 deselected   [the deselected test failed in the -x run first]
FAILED test/test_containment.py::test_repository_history_reports_the_known_phase_prog_cases
FAILED test/test_idea_classification.py::test_every_pre_change_idea_folds_to_identical_state
FAILED test/test_idea_classification.py::test_the_log_before_the_change_is_a_byte_identical_prefix
FAILED test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused

$ git fetch --unshallow origin dev   (1879 commits)
$ uv run pytest -q test/test_idea_classification.py test/test_run_review_checks.py test/test_containment.py
1 failed, 80 passed
FAILED test/test_run_review_checks.py::test_an_unwritable_worktree_parent_is_refused
E   Failed: DID NOT RAISE Refused
```

- Three failures were the shallow clone: the tests read `0f142ce:_data/ideas.jsonl` and walk
  `phase-prog-*` history, neither of which the 52-commit clone held. They pass with full history.
- One failure is the container: the test makes a directory unwritable and expects the runner to
  refuse it; this session runs as `root`, for which `chmod` denies nothing. It does not touch this
  branch's changes (`tools/run_review_checks.py` is unchanged) and should pass on the gate's
  machine. Not fixed here: a fix would widen the branch into a tool this session did not change.
- `docs/08-governance/catalog.md` was checked with `git diff --exit-code` after every `pytest` run:
  unchanged each time.
- The test-baseline check (`tools/check_test_baseline.py`, `OPS-031`) was not run: it needs a
  base JUnit report from `dev`'s tip, and the same two environmental failures would appear in both.
  The gate's machine should run it.

## 6. Assumptions made

Ranked by how much a different answer would change.

1. **Correction, 2026-10-08.** The session dispatched two research agents and then wrote GOV-022,
   the guide page, the scripts and the idea files itself, against `GOV-013`'s context-discipline
   rule. The owner corrected it to orchestrate only. After the correction every file was written by
   a creator agent: the GOV-022 amendment, the brain procedure, and this hand-off's update. The
   session's own writes before the correction are listed in section 2 and stay as the record of
   what happened.
2. **The clone is the worktree.** No sibling worktree was cut inside the container; the clone is the
   isolation `AGENTS.md`'s rule exists for, as the three earlier cloud sessions did. `GOV-022`
   departure 1, Open question 4.
3. **Ideas recorded on the branch, not handed to Ideation.** The owner chose "record each as an
   idea"; the id-collision hazard is stated in section 3 and in `GOV-022` Open question 3.
4. **`GOV-022` is `draft`, with the model-tier rule marked proposed.** The owner's Haiku-default
   instruction was treated as the rule for this session and recorded as a proposal, not a standing
   rule, per `CLAUDE.md`'s rule against generalising a one-time instruction. Open question 1.
5. **The guide's as-of figures are from this branch on 2026-10-08** and were computed by script
   from `backlog.yaml` and `ideas.jsonl`, with three figures corrected after a verification run
   (14, not 20, open phases sit on the blocker chain; 8 overview templates; 15 templates in all).
6. **Sonnet for one agent.** The template exploration is design judgment; Haiku ran the document
   digest. Stated in the kickoff reply before dispatch.

## 7. Open questions and anything left undone

- The six open questions in `GOV-022`, starting with whether the Haiku-default rule is standing.
- The decisions list in the guide (section 9): the portfolio data question (`phase-proj-01`),
  which template first, timeline shape, Gantt scope and the `start_date` field, the as-of date
  rule, re-scoping `phase-syn-05`, and the structuring command gap.
- `GOV-017` and `PROMPT-037` were not edited to point at `GOV-022`; that is Open question 6.
- `docs/00-working/cloud-prompts/status.md` was not edited; this session is not one of its rows.
- No pull request was opened; `dev` is the integration branch and the merge is the owner's call.

## 8. Spend posture

| Dispatch | Type | Model | Why this tier |
|---|---|---|---|
| Document digest (schemas, data root, capture, API, plans, procedures) | `Explore`, read-only | Haiku | Cited-fact extraction |
| Template exploration (timeline, Gantt, further proposals, build order) | `general-purpose`, read-only | Sonnet | Design judgment and ranking; Haiku judged not fit |
| GOV-022 amendment (orchestrator-only ruling) | `general-purpose`, creator | Haiku | Mechanical edit from a specified brief |
| Brain procedure draft | `general-purpose`, creator | Haiku | Shaped by the logging skill and schema |
| Index line, cross-references, hand-off update | `general-purpose`, creator | Haiku | Mechanical edits |

Five agents in total: two read-only researchers dispatched together at the open, and three creators dispatched after the owner's correction. No Opus. No fix cycles. One worker
restart mid-session, with nothing lost because every result was already in a file.


## 9. Owner rulings after the hand-off (2026-10-08)

The owner answered the guide's decisions list in the session, after the hand-off was first pushed. Recorded here so the gate and the next session see them; none has been applied to backlog.yaml, which a cloud session does not edit.

1. **The portfolio data question (`phase-proj-01`).** Owner ruling: yes, people and commitments hold real records; they are simply not tracked and are absent from the cloud clone. This is the answer `phase-proj-01` exists to obtain; the phase's record and 000022's correction remain to be written on the local side.
2. **Which template first.** Owner ruling: approved as recommended, the shared loader and fixture set (000687) first, then the commitments ledger (000675).
3. **Timeline shape and Gantt scope.** The owner asked for a recommendation; the session gave one in its reply (per-project chronological timeline with created dates excluded as events, milestone development events accepted as the milestone source, a shared card component; project-level Gantt first with a separate small schema phase adding start_date to task and commitment, no interim dependency field). Not yet ruled.
4. **The as-of date rule.** The owner asked for clarity; the session explained the determinism requirement and recommended an explicit --as-of parameter, required for committed and test output and defaulting to today for renders to gitignored locations, stamped on the page. Not yet ruled.
5. **Re-scoping `phase-syn-05`.** The owner asked for more detail; the session gave it in its reply. Not yet ruled. Idea 000688 carries the finding.
6. **The structuring command gap.** Owner ruling: yes, a command-line entry point for the structuring step should exist. Recorded as idea 000689.

## 10. Idea ids renumbered (2026-10-09)

The workbench run (branch `ccr-b69b05b4-tdcrux`) recorded its own ideas `000600` to `000672` on
the same base, so this branch's ids collided. Owner ruling, 2026-10-08: the workbench run keeps its
numbers, and this branch's seventeen ideas are renumbered in order. They were re-recorded on
`agent/renumber-productivity-ideas` through `tools/append_idea.py add --file` with the title and
body unchanged. Each carries a `finding` annotation by `agent-renumber` that records its original id,
branch and time. The ids in this document and in `_public/portfolio-guide.html` were replaced in
place. Sections 2 and 3 describe the original allocation; the ids they now show are the new ones.

| original id | new id | originally recorded (2026-10-08, UTC) |
|---|---|---|
| 000600 | 000673 | 10:04:06 |
| 000601 | 000674 | 10:04:07 |
| 000602 | 000675 | 10:04:07 |
| 000603 | 000676 | 10:04:07 |
| 000604 | 000677 | 10:04:08 |
| 000605 | 000678 | 10:04:08 |
| 000606 | 000679 | 10:04:08 |
| 000607 | 000680 | 10:04:09 |
| 000608 | 000681 | 10:04:09 |
| 000609 | 000682 | 10:04:09 |
| 000610 | 000683 | 10:04:09 |
| 000611 | 000684 | 10:04:10 |
| 000612 | 000685 | 10:04:10 |
| 000613 | 000686 | 10:04:10 |
| 000614 | 000687 | 10:04:11 |
| 000615 | 000688 | 10:04:11 |
| 000616 | 000689 | 14:59:17 |
