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

- **Round 4, at `4be47bdb`.** Gating pass, shadow pass. Records:
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-demo-adversary-3.json` and
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-review-judge-3.json`. The space and
  apostrophe case is fixed. Both reviewers raised a minor F01: double quotes do not survive a path
  containing `"`, and they expand `$` and backticks, so a path can change silently and the wrong
  file is read. On 2026-10-06 the owner ruled, relayed by the Session Manager, to fix it with a
  quoted heredoc. Fix cycle 5 (`753787de`) passes the path on stdin through `<<'EOF'`, reads it
  with `sys.stdin.read()`, and puts no path text on the command line or in Python source. The
  tests run the extracted command against paths that combine `"`, `$HOME`-style text, a backtick,
  an apostrophe and a space, and they assert that the exact file is read.

- **Round 5, at `d466d577`.** Gating pass, shadow pass. Records:
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-demo-adversary-4.json` and
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-review-judge-4.json`. The heredoc
  fix held against 11 path hazards. Both reviewers raised a minor F01: a path containing a newline
  plus a line reading exactly `EOF` ended the heredoc early, and the rest ran as shell commands. On
  2026-10-06 the owner ruled, relayed by the Session Manager, to enforce the slug. Fix cycle 6
  (`b84bf61e`) does three things. The planner's instructions limit the slug to `[a-z0-9-]+`. The
  delimiter is a fixed, quoted token (`PLANNER_DRAFT_PATH_EOF_9f3b6a2d1e8c4caa`). Python refuses,
  before opening anything, any path that does not `re.fullmatch`
  `docs/00-working/promoted/[A-Z]+-[0-9]{3}(?:\.[0-9]{2})?-[a-z0-9-]+\.md`. The tests prove that a
  newline-plus-`EOF` path is refused and that the remainder never runs. One limit remains and is
  recorded rather than claimed fixed. A path that already breaks the slug rule and contains the
  fixed delimiter on its own line still ends the heredoc in the shell, before Python runs. No path
  the planner legitimately builds can contain that line, and
  `test_delimiter_cannot_be_produced_by_any_legitimate_slug_or_code` covers that.

- **Round 6, at `d09dc52b`.** Gating **reject**, shadow pass with a major. Records:
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-demo-adversary-5.json` and
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-review-judge-5.json`. The blocker,
  reproduced live: the fixed delimiter is public in the agent text, so a path payload containing
  that line plus a `touch` command ran the command, and Python's check never ran. This is the
  limit recorded under round 5. The Session Manager also noted that the planner was told to use a
  file-write tool it did not have. On 2026-10-06 the owner ruled, relayed by the Session Manager,
  to give the planner the Write tool. Fix cycle 7 (`59290bbe`) does three things. `Write` is added
  to the planner's tools, and it writes only its draft under `docs/00-working/promoted/` plus the
  draft's path to the fixed, gitignored file `_working/idea-planner/draft-path.txt` (named by the
  coordinator). The heredoc is removed. The check is a constant command: Python reads the path
  file and refuses, before opening anything, any path that does not `re.fullmatch`
  `docs/00-working/promoted/(PLAN|REQ)-[0-9]{3}(?:\.[0-9]{2})?-[a-z0-9]+(?:-[a-z0-9]+)*\.md`. The
  slug part is stricter than the ruling's `[a-z0-9-]+`: it also forbids leading, trailing and
  doubled hyphens. The tests cover the reviewer's live payload (refused, and its marker never
  created), the 11 earlier hazards, `PLAN`, `REQ` and child-code paths, and a refused non-`PLAN`/`REQ`
  series.

- **Round 7, at `41dbfbb8`.** Gating pass, shadow pass. Records:
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-demo-adversary-6.json` and
  `docs/08-governance/reviews/verdicts/2026-10-06-phase-idg-12-review-judge-6.json`. The round-6
  blocker is closed. Gating F01 (major): the single fixed path file was shared, so two concurrent
  dispatches in one worktree could overwrite each other's path. F02 (minor): Write is scoped in
  prose only, not at tool level; it is left as is, as for every other agent with Write. Shadow
  minor: `depends_on` and `documents` are still filled in by hand, which is now stated in the
  prose. On 2026-10-06 the owner ruled, relayed by the Session Manager, to use per-code path
  files. Fix cycle 8 (`dd709923`) writes each draft's path to
  `_working/idea-planner/<reserved-code>.path`. A fixed command globs those files and fullmatches
  each file name against the code pattern and each file's content against the ADR-019 pattern,
  whose code must equal the file name's code. It refuses mismatches without opening them and
  prints one result line per draft, and the planner reads only its own line. The run exits
  nonzero if any path file is refused.

Fix cycles used: eight, all on the same safe-write command after cycle 1. Two is `PROMPT-036`'s
cap; the owner granted cycles 3 to 8.
