---
schema_version: 1
id: doc-session-idea-planner-agent
code: SESS-2026-10-06-01
title: Build the idea planner agent and check it against the standard
kind: session
status: active
owner: repository-owner
created: '2026-10-06'
updated: '2026-10-06'
systems: [sys-governance]
depends_on: [doc-idea-graph-lifecycle, doc-idea-graph-lifecycle-requirements]
---

# Build the idea planner agent and check it against the standard

## Phase

`phase-idg-12`: Build the idea planner agent and check it against the standard (`PLAN-029`;
`REQ-014` R19 and R20, `REQ-022` R09 and R20; idea `000046`). Stage 2 of `batch-004`. Built on
2026-10-05 and 2026-10-06 by Session 5 (Batch Runner, `agent-batch-runner`) under `PROMPT-036`. It
was claimed on `dev` at `eeab5ee`, with the owner's approval given in-session, after Builder B's
`phase-sch-03` merged, as the owner had ruled.

## Owner decisions

These were made at the batch opening on 2026-10-05 and applied to the phase's own lines in the claim
commit, together with Standby's review fixes 1, 2, 6 and 7:

- **Input.** The planner builds the GOV-014/ARCH-006 shape: an accepted partition track goes in, one
  draft comes out per track, and the amendment case is honoured. R19's single promoted idea is
  tested as a one-member track.
- **Requirement drafting.** Only `phase-dgov-01`'s mandatory-requirement rule (GOV-001) decides
  whether a requirement is drafted. Amending GOV-014 and ARCH-006 to match is a separate change, not
  made here.
- **Conformance check.** The GOV-010 section check is built as code. The loop that returns a draft
  to the planner and escalates belongs to `phase-irs-14`.
- **Fixtures.** Tests use synthetic ideas, never the live idea log.
- **Agent definition (2026-10-05).** The planner is generated the same way as the triage agent: a
  source in `agent-workflows/` plus a manifest entry, Claude target only. `agent-workflows/` lies
  outside the declared deliverables; the owner approved it for this phase.
- **R19 evidence location (coordinator's assumption, reported to the owner).** The live run is
  quoted here rather than saved under `docs/00-working/promoted/`. ADR-019 staging needs a reserved
  code, and this run reserves none.

## What was built

- `agent-workflows/idea-planner-agent.md` and its manifest entry in `agent-workflows/workflows.yaml`,
  rendered to `.claude/agents/idea-planner.md` by `tools/generate_agent_workflows.py`. The agent
  takes one accepted track and the code or codes already reserved for it. It decides the
  requirement pairing with `requirement_mandatory()`, writes
  `docs/00-working/promoted/<reserved-code>-<slug>.md`, and stops if a needed code is missing. It
  never reserves a code and never marks an idea promoted.
- `src/governance/plan_quality.py`: `check_plan_conformance()` and `check_requirement_conformance()`
  check a draft against GOV-010's named sections and name every missing one. The pairing inputs
  (`depends_on`, `documents`) are required keyword arguments.
- `test/test_plan_quality.py` and `test/test_planner_safe_write.py`, both on synthetic fixtures.
- `docs/08-governance/GOV-014-realization-role-contracts.md`: the planner's agent-definition line,
  plus one sentence marking conditional pairing as a temporary exception pending the owner's
  amendment.

## R19 live run

The verification's third item. On 2026-10-05 the generated definition at `7028efd` was run
verbatim on Haiku, the model it names, inside a scratch clone of the branch. It was dispatched as a
general-purpose agent with the definition as its instructions, because the `idea-planner` type
existed only on the branch. The input was idea `000275` (a sub-agent per session record, to
extract decisions and outstanding items) as a one-member accepted track, `kind: amendment` of
`PLAN-041`, with `PLAN-041` as its code.

- It wrote `docs/00-working/promoted/PLAN-041-portable-framework-content-extraction.md` (132
  lines) in the scratch clone only. Nothing from the run is committed.
- The requirement rule: `PLAN-041` has 3 registered phases, so a requirement is mandatory. It is
  already paired with `REQ-025`, so no requirement was drafted.
- The draft cites `000275`'s triage finding: *"Session-record decision extraction scope
  (`000275`): The triage finding for idea 000275 specifies exact…"*; and *"scope for phase-fwa-02
  (000275) is now tightly specified via triage findings … per REQ-025 R02."* It also cites
  `000275`'s links to `000276`, `000281` and `000332`.
- `check_plan_conformance()` judged the draft conformant, with all ten sections present (Summary,
  Decisions, Design, Implementation phases, Execution order and real concurrency, Requirement
  coverage, Out of scope, Open questions, Member idea findings cited, Ideas not promoted alongside
  this plan).
- `git status` in the clone afterwards showed only the new untracked draft. `codes.yaml` and the
  idea log were unchanged, so no code was allocated and nothing was marked promoted.

The later fixes change how step 7 calls the check and how the draft is written. They do not change
what the draft cites.

## Verification

Run in the phase worktree at `7eca001`:

```
uv run python -m src.governance                      Governance OK: 45 systems, 454 documents, 37 memories, 347 backlog phases
uv run python tools/generate_agent_workflows.py --check   17 workflow adapter(s) current
uv run ruff check src/ test/ tools/                  All checks passed!
uv run mypy src/                                     Success: no issues found in 51 source files
uv run pytest -q                                     1673 passed, 1 warning
```

## Review

The validator (`demo-validator-code`) failed the first build. Its high-severity finding: the draft
filename omitted the reserved code that ADR-019 step 3 and GOV-011 require. The fix in `7028efd`
passes the reserved code in as an input. The validator passed that fix and each fix after it.

The Session Manager dispatched three rounds of build review:

- **Round 1, at `7028efd`.** Gating `demo-adversary` pass, shadow `review-judge` pass. Records:
  `docs/08-governance/reviews/verdicts/2026-10-05-phase-idg-12-demo-adversary.json` and
  `docs/08-governance/reviews/verdicts/2026-10-05-phase-idg-12-review-judge.json`. The owner ruled
  in-session to fix all three gating findings, in fix cycle 2 (`9dcbae8`):
  - F01 (major): the planner called the check without its pairing inputs, so a paired draft
    missing "Requirement coverage" passed.
  - F02 (major): GOV-014 still said the pair is always drafted. One temporary-exception sentence was
    added.
  - F03 (minor): the agent had no safe-write rule for long drafts.
  The shadow finding (the phase text cites `REQ-022` R20 in scope and `REQ-014` R20 in acceptance)
  was recorded only.
- **Round 2, at `9dcbae8`.** Gating pass, shadow pass. Records:
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-demo-adversary.json` and
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-review-judge.json`. F01 and F02 were
  closed. F03 was reopened as major: the safe-write rule put `$(cat …)` inside Python source, so a
  draft containing `"""` failed. On 2026-10-06 the owner ruled, relayed by the Session Manager, to
  allow one extra fix cycle for this finding only. Fix cycle 3 (`7eca001`) passes the path as
  `sys.argv[1]`, and `test/test_planner_safe_write.py` runs the documented command against such a
  draft.
- **Round 3, at `7eca001`.** Gating pass, shadow pass with no findings. Records:
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-demo-adversary-2.json` and
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-review-judge-2.json`. The reopened
  F03 is fixed. New F01 (minor): the draft path in the safe-write command is unquoted, so a path
  with a space or apostrophe breaks it. It was first relayed as accepted as is. The Session Manager
  then withdrew that acceptance on 2026-10-06, because it had rested on the wrong claim that paths
  never contain spaces; the owner corrected it. The owner's ruling, relayed by the Session Manager,
  replaces it: fix the finding in this phase before it merges. Fix cycle 4 quotes the path and
  extends `test/test_planner_safe_write.py` to cover a path containing a space and an apostrophe.
  Idea `000596` (quote the draft-path argument in the idea planner's safe-write command) records
  this fix.

Fix cycles used: four. Two is `PROMPT-036`'s cap, and the owner granted the third and fourth.
