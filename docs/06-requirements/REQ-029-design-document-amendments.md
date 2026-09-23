---
schema_version: 1
id: doc-design-document-amendments-requirements
code: REQ-029
title: Design-document amendments requirements — bring the realization design, role contracts, review procedure and session commands into line with the owner's 2026-09-23 rulings
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-23'
updated: '2026-09-23'
systems: [sys-gov-docs, sys-realization]
depends_on: [doc-idea-realization-system, doc-realization-role-contracts, doc-three-altitude-review-procedure, doc-backlog-decisions]
---

# Design-document amendments requirements

Observable statements for the one documentation phase the owner ruled on 2026-09-23 ("one docs
phase now"). The plan that delivers them is
[PLAN-046](../01-plans/PLAN-046-design-document-amendments.md).

## Observed problem and scope

The governing documents contradict each other and the owner's rulings. Each case is recorded:

1. **Phase-completion authority.** `GOV-003` ("Coordinator completion replaces owner-invoked
   /session-close, repository-wide", 2026-09-16) lets a coordinator mark a phase complete under
   three conditions. These still say completion is owner-only through `/session-close`:
   `.claude/commands/session-start.md` lines 191-192 and 224, the orient skill's source
   (`agent-workflows/orient.md`, rendered to `.claude/skills/orient/SKILL.md` lines 77-80),
   `.claude/commands/resume-lit-review.md` line 182, `GOV-014` lines 34, 175 and 195,
   `ARCH-006`'s G5 row and authority model, and `AGENTS.md` lines 179-180 (idea `000378`, with the
   owner's ruling of 2026-09-23 that `GOV-003` governs).
2. **G4.** `ARCH-006` says integration is "enforced at the tool boundary by P5's capability
   broker". No such enforcement exists: the broker's approval store is not connected to its check,
   and no hook is configured (Scout report `orchestration-1-evidence.md`, stage 8 row). The owner
   ruled on 2026-09-23 (Scout O-3) that builders keep self-merging under `GOV-017` until P3's
   merge-gate nodes exist.
3. **Revision cycles.** `ARCH-006` stage 8 allows "one revise cycle per finding class", stage 5
   "one revision cycle", and `GOV-018` step 5 follows stage 5. The owner ruled two cycles on
   2026-09-23 (mapping Q6).
4. **Test Author.** `GOV-014` has nine role contracts and no Test Author; its Developer writes its
   own tests. The owner ruled on 2026-09-23 (mapping Q5) to add a Test Author to the `unit` graph now
   and amend `GOV-014`.
5. **Spot-audit.** `GOV-014`'s Validator contract, `ARCH-006`'s cost and safety controls and
   `REQ-022` R23 require the owner to spot-audit one in ten passed validations at each G5 sitting.
   No session record of 2026-09-22 or 2026-09-23 shows one (Scout report, control 28). The owner
   ruled on 2026-09-23 to replace it with sampled independent re-review (the same report's item 9,
   option (c)).
6. **The close reviewer sees the developer's rationale.** `/session-close` step 3 gives the review
   sub-agent "the session record's current path and content"
   (`.claude/commands/session-close.md`, step 3), while `GOV-014` says a validator sees the
   requirement and the diff, never the developer's rationale. The owner ruled on 2026-09-23 that the
   close reviewer gets no session record (the same report's item 4, option (a)).
7. **Standing rulings with no durable record.** The owner ruled on 2026-09-23 that remote branch
   deletion is owner-only (protocol Q15), that every worktree removal needs the owner's approval
   (protocol Q8), and that agent-originated ideas carry an "agent-proposed" label (Scout report
   `orchestration-1-evidence.md`, "Owner decisions needed", item 3, option (c)). They exist only on the Session Manager's gitignored board.
8. **`CLAUDE.md` is stale.** Line 137 lists four schema files (`schemas/` holds 26 files); line
   141 lists seven tables (`sql/001_schema.sql` creates 16); line 144 says tasks are embedded in
   commitment JSON, while `tools/rebuild_db.py` reads them from `_data/tasks/` as first-class
   records. The owner approved correcting these on 2026-09-23, relayed by the Session Manager.

## Observable requirements and verification

| ID | Required observable behaviour | Verification |
|---|---|---|
| R01 | No document in problem 1's list, other than `AGENTS.md`, states that phase completion is owner-only; each states the `GOV-003` rule or points to it | `grep -n -i -E "owner-invoked|owner-only|owner-reserved via"` over the listed files returns no line about phase completion; each file's changed passage names `GOV-003` |
| R02 | `ARCH-006`'s owner-reserved list and `GOV-014`'s verbatim quote of it are identical after the change, and the completion item reads as `GOV-003` allows | `diff` of the two quoted lists is empty |
| R03 | `ARCH-006`'s G4 row states that the owner approves every integration, that until P3's merge-gate nodes exist the builder session performs the fast-forward under `GOV-017`, and that tool-boundary enforcement is not yet built | Read the row; `grep -c -i "enforced at the tool boundary"` in `ARCH-006` is 0 (it is 1 before the change: the text is capitalised, "Enforced at the tool boundary") |
| R04 | `ARCH-006` stages 5 and 8 and `GOV-018` step 5 allow two revision cycles before escalation | Read the three passages; `grep -n "one revision cycle\|one revise cycle"` in both files returns only stage 3 (partition), which this change leaves alone |
| R05 | `GOV-014` has a Test Author contract with inputs, outputs, never-do and a per-dispatch ceiling; its write scope is `test/` only; the Developer contract excludes `test/`; every count of the roles says ten; `ARCH-006` stage 8's Role and Failure path columns name the Test Author, its order relative to the Developer, and what happens when a Developer disputes one of its tests | Read the contract and the stage 8 row; `grep -n "nine"` in `GOV-014` returns no count of roles |
| R06 | The spot-audit is replaced in `GOV-014`, `ARCH-006` and `REQ-022` R23 by a sampled independent re-review with a stated sampling rule, reviewer type and inputs | `grep -n -i "spot-audit"` over the three files returns no line requiring the owner to spot-audit; the new rule is readable in `GOV-014`'s Validator contract |
| R07 | `/session-close` step 3 does not give the reviewer the session record, and says why; `GOV-014` states that the close review is bound by the Validator's input rule | Read step 3; the only mention of the session record in step 3 is the prohibition |
| R08 | `GOV-003` has a dated entry for each ruling in problem 7, quoting the ruling, stating it is standing, and naming what it changes | Read the three entries |
| R09 | `CLAUDE.md` lines 137, 141 and 144 read exactly as the text the owner confirmed in the executing session; if the owner has not confirmed it there, the lines are unchanged and the session record says so | `git diff CLAUDE.md` shows either the confirmed text or nothing |
| R10 | `AGENTS.md` lines 179-180 change only with the owner's approval of the exact old and new text, given for that change; otherwise they are unchanged and the session record says so | `git diff AGENTS.md` shows either the approved text or nothing |
| R11 | The generated orient skill matches its source, and governance and the catalog are current | `uv run python tools/generate_agent_workflows.py --check` exits 0; `uv run python -m src.governance` exits 0; `git diff --exit-code docs/08-governance/catalog.md` after `--catalog` |

## What each requirement is not

- **R01 does not change who approves integration.** Every merge onto `dev` still needs the owner's
  yes (`GOV-003` condition 3).
- **R03 does not move merges to another session.** Scout O-3 (b) and (c) were not chosen.
- **R04 does not change the partition's stage 3.** Q6 named stage 8 and `GOV-018`; stage 5 changes
  only because `GOV-018` implements it (`PLAN-046`, D2).
- **R05 does not build the Test Author** or apply it to interactive builders. Mapping Q5 option (b),
  a rule for interactive sessions, was not chosen.
- **R06 does not decide the re-review's tooling.** Scout O-5 (a judge without Bash plus a fixed
  command runner) is a separate ruling with its own work.
- **R08 does not build the agent-proposed label** in the idea schema or writer. It records the
  ruling (`PLAN-046`, OQ2).
- **R09 and R10 are not approvals.** `CLAUDE.md` and `AGENTS.md` each require the owner's explicit
  approval of the specific change; a relayed summary is not treated as that approval.
