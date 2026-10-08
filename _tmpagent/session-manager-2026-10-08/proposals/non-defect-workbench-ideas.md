# Uncovered workbench ideas that are not defects (proposal, not committed)

Written 2026-10-08 by the Prompt Planner for branch `agent/plan-wbf-defects`. The branch adds phases
`phase-wbf-12` to `phase-wbf-18` for the defect ideas; these five were left out because they are not
defects. Each paragraph says what the idea would take and where it belongs. Statements about code
were checked on the branch; statements about plans come from the idea log findings.

## 000360 (API routes and ts/ views for projects, people, commitments and tasks)

This is a feature with its own surface, not workbench work. `src/api/routes/` holds only
`demo_stage.py`, `demo_terminal.py` and `workbench.py`, so no route serves the four entities, and
`ts/` has no view of them. A first phase would add read-only routes that read DuckDB through the
shared access helper, following the rules `ADR-015` set for the workbench routes (repository-bounded
paths, server-side validation, gated mounting), plus one list view per entity in `ts/`. It should
wait for `phase-rel-07` (unify database paths and application access helpers, queued) so the routes
do not add another database-path variant, and it must read `D_SYSTEM_DATA_ROOT` and never place
private content in tracked output (`ADR-009`). Until `phase-cap-08` runs there are no real people,
commitments or tasks, so early views would show only the fictional example set. It belongs in a new
plan, not `PLAN-027` or `PLAN-028`, which cover the existing workbench only. It pairs with `000361`
(the quick-entry writer), which is the write side; any write route faces the capture-boundary
question in `ADR-007`. Suggested size: one ADR-free phase for read-only routes, one for the views,
two sessions.

## 000122 (evaluate a non-web rebuild)

Already planned. `phase-expl-06` (evaluate languages and platforms for a non-web rebuild, queued,
priority 4, plan `doc-standalone-explorations-housekeeping`) is this idea's phase; it produces a
comparison with a recommendation and no code. Nothing needs adding to `PLAN-027`. The only action is
to list `000122` in that phase's `ideas:` field if `--check-ideas` does not already show it. Feature
parity with the current FastAPI and React workbench is the evaluation's baseline, so it is best run
after `PLAN-028` settles the workbench's vocabulary and structure; it should not block anything.

## 000123 (audit the pre-build HTML generation plans against what the workbench became)

An audit with a document-by-document table as its output. `PLAN-003` is now deprecated and `ADR-027`
retired it, and `phase-html-01`, which the idea says still sits ready, is `cancelled`, so part of
the reconciliation was done by those decisions; the audit would record the disposition (accomplished
with evidence, still open, superseded, retire) for each remaining requirement in the `phase-html-*`
line and the plans that came after it. One session, deliverable a working note under
`docs/00-working/`, no code. It belongs with `PLAN-028`'s audit group (`G41`, the duplication and
code-structure audits, `phase-arch-03` and `phase-arch-04`), which omits it today, or with the
HTML-generation track under `PLAN-036`. The owner should choose; the audit's output feeds neither
workbench defect work nor `PLAN-027`. Before scheduling it, confirm the idea's premise against the
current backlog, since its text predates `ADR-027`.

## 000569 (error boundary and accessible loading/error status)

Mostly delivered. Commits `c054cb8` to `51c55d5`, recorded in `SESS-2026-10-04-15`, added an error
boundary around the stage root and around each panel (`ts/src/stage/ErrorBoundary.tsx`,
`guardedPanel.tsx`), `role="status"` and `role="alert"` on the loading and error messages, a Retry
that remounts the panel, and vitest tests (`ErrorBoundary.test.tsx`, `wiring.test.tsx`). What the
record leaves open is a short list: the notes strip's loading and error states share one element
with no live region, Retry on a crashed terminal opens a new session, whether screen readers
announce the File Browser's status inside `role="tree"` is unconfirmed, and `cd ts && npm test` does
not yet run in CI (`000582`). The remainder fits one small `PLAN-028` phase (quality) with a
`REQ-011` row, or can be folded into the `000582` CI work. Recommend first asking the owner to move
`000569` to `delivered` or `resolved` with the commits as the pointer, and to record the residual
list as a new idea, because phase work against an idea that is mostly done will be sized wrongly.

## 000583 (tests that read the live idea log should use a fixed fixture)

A test-hygiene audit and a set of edits, not a workbench feature. The incident was fixed twice
(`e66b42d` and the schema-enum checks in `test/test_workbench_api.py:550` and
`test/test_overview_tools.py`), but eleven test files still read `_data/ideas.jsonl`
(`test_ideas.py`, `test_demo_reset.py`, `test_idea_classification.py`, `test_backlog.py` and others)
and nobody has checked which assume a fixed set of statuses. The work is: list the readers, mark
each as needing the live log or not, move the ones that do not to a fixed fixture log, and keep a
check that the schema's status enum is the only vocabulary a test hard-codes. It fits `PLAN-035`
(schema consistency and testing), next to `phase-sch-04` (the per-layer testing standard, queued),
which would state the rule the audit then applies, or `PLAN-029` (idea graph and lifecycle) by
subject. One audit session plus one fix session. It is not `PLAN-027` work.
