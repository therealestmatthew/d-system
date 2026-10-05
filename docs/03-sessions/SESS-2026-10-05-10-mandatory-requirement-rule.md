---
schema_version: 1
id: doc-session-mandatory-requirement-rule
code: SESS-2026-10-05-10
title: Rule when a requirement is mandatory, classify the corpus, enforce forward
kind: session
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-governance]
depends_on: [doc-document-backlog-governance, doc-document-backlog-governance-requirements]
---

# Rule when a requirement is mandatory, classify the corpus, enforce forward

## Phase

`phase-dgov-01`: Rule when a requirement is mandatory, classify the corpus, enforce forward
(`PLAN-030`, `REQ-015` R01–R03). Stage 1 of `batch-004`. Built on 2026-10-05 by Session 5 (Batch Runner,
`agent-batch-runner`) under `PROMPT-036`. The owner approved the claim in-session, and the
claim landed on `dev` at `72e405b`.

## Owner decisions

- **R03 fixture.** The plan that breaks the rule is built inside the pytest test and is never a
  real document under `docs/`.
- **R02 surface.** A new `uv run python -m src.governance --classify-requirements` flag prints the
  unpaired plans and states their count as a number. It is added as the phase's third
  verification item.

## What was built

- `docs/08-governance/GOV-001-protocol.md`, section *When a requirement document is mandatory*: a
  plan needs a paired requirement once more than one backlog item names it in its `plan` field. The
  rule is a count, with no judgment involved.
- `src/governance/requirement_rule.py`: the rule, the classification and the forward check, with
  `GRANDFATHERED_PLAN_IDS` holding the 12 plans written before the rule.
- `src/governance/__main__.py`: the `--classify-requirements` flag, and the forward check added to
  the plain governance run.
- `test/test_requirement_rule.py`: 8 tests covering R01 (a separately written second reader agrees
  on five plans picked by name order), R02 (the count is a number) and R03 (an unpaired fixture
  plan fails and is named, while paired and grandfathered fixtures pass).

The rule was written and committed (`2680efb`) before the classification (`dee784f`), as
`next_action` requires.

## Verification

Run in the phase worktree at `dee784f`:

```
uv run python -m src.governance                          Governance OK: 45 systems, 451 documents, 37 memories, 347 backlog phases
uv run python -m src.governance --classify-requirements  Unpaired mandatory plans: 12.
uv run ruff check src/ test/ tools/                      All checks passed!
uv run mypy src/                                         Success: no issues found in 50 source files
uv run pytest -q                                         1646 passed, 1 warning
```

## Review

The validator (`demo-validator-code`) passed the build. The Session Manager ran the build review at
`dee784f`, with the runner manifest at `_working/review-checks/phase-dgov-01/dee784f73add/`.

- Gating `demo-adversary`: **pass**
  (`docs/08-governance/reviews/verdicts/2026-10-05-phase-dgov-01-demo-adversary.json`).
- Shadow `review-judge`: **pass**
  (`docs/08-governance/reviews/verdicts/2026-10-05-phase-dgov-01-review-judge.json`).

The owner ruled on the gating findings in-session on 2026-10-05:

- **F01 (minor), accepted.** The scope estimated "14-plus" plans to grandfather; the classified
  count is 12. The estimate was scope prose, and the code and tests use the classified count.
- **F02 (major), accepted with a follow-up.** The rule counts backlog items per plan, so
  splitting one multi-phase plan into several one-phase plan documents escapes it, and
  GOV-001's text shares the gap. The owner chose to merge as built and fix the loophole later. The
  follow-up is idea `000593` (close the mandatory-requirement rule's split loophole),
  recorded through Ideation.

The shadow findings decide nothing and are recorded only. F01: no test drives the
`--classify-requirements` CLI path itself. F02: the same 12 versus 14-plus point.
