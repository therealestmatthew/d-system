---
schema_version: 1
id: doc-session-design-document-amendments
code: SESS-2026-10-04-06
title: Amend the governing documents to the 2026-09-23 rulings
kind: session
status: active
owner: repository-owner
created: '2026-10-04'
updated: '2026-10-04'
systems: [sys-governance, sys-gov-docs, sys-realization]
depends_on: [doc-design-document-amendments]
---

# Amend the governing documents to the 2026-09-23 rulings

## Phase

`phase-dam-01` — Amend ARCH-006, GOV-014, GOV-018, REQ-022 and the session commands to the
2026-09-23 rulings.

## Verification

Run in `/code/d-system-worktrees/phase-dam-01` on `agent/phase-dam-01`, after rebasing onto dev
`92777af` and committing the owner-regenerated adapter.

`uv run python tools/generate_agent_workflows.py --check`

```
16 workflow adapter(s) current
```

`uv run python -m src.governance --catalog` then `uv run python -m src.governance`

```
Governance OK: 44 systems, 430 documents, 36 memories, 347 backlog phases
```

`git diff --exit-code docs/08-governance/catalog.md`: exit 0, no diff.

`uv run pytest`

```
1436 passed, 1 skipped, 1 warning
```

`.agents/skills/orient/SKILL.md` is closed to agents by a deny rule. The owner regenerated it in the
Owner Terminal (entry C14, exit 0, "wrote 16 workflow adapter(s)"); the file matched this session's
generator output byte for byte and was committed here. The `.claude` copy was regenerated in this
session.

Acceptance greps (`REQ-029`'s verification column):

- R01: `grep -n -i -E "owner-invoked|owner-only|owner-reserved via"` over problem 1's files returns
  only lines that quote the title of `GOV-003`'s entry "Coordinator completion replaces
  owner-invoked /session-close, repository-wide" as the pointer, plus the orient skill's general
  "Flag owner-only commands explicitly." No line states that completion is owner-only.
- R02: the `diff` of `ARCH-006`'s owner-reserved list and `GOV-014`'s quote is empty.
- R03: `grep -c -i "enforced at the tool boundary"` on `ARCH-006` returns `0`.
- R04: `grep -n "one revision cycle\|one revise cycle"` over `ARCH-006` and `GOV-018` returns only
  `ARCH-006` line 83, stage 3 (partition).
- R05: `GOV-014` has `### Test Author`; `grep -n -w nine` returns nothing.
- R06: `grep -n -i spot-audit` over the three files returns only `GOV-014`'s "replaces the owner
  spot-audit (owner ruling of 2026-09-23)".
- R07: within `/session-close` step 3, the only line naming the session record is "**Never the
  session record.**"
- R08: `GOV-003` has the five new entries (seven headings now end "— 2026-09-23"; two predate this
  phase).
- R12: `git grep -n -w main` over `GOV-001`, `GOV-002`, `GOV-005`, `OPS-001` and `session-close.md`
  returns nothing. `GOV-001` and `GOV-002` had no `main` left when this phase started.
  `session-close.md`'s one "primary-checkout exception" line says `GOV-003` withdrew it.
- R13: `PLAN-005` carries "**Superseded, 2026-10-04.**" after the passage; `grep -n triaging` in
  `REQ-003` returns nothing.

## Acceptance

- Completion grep returns no owner-only completion statement outside AGENTS.md: Met (R01 above).
- The two owner-reserved lists diff empty: Met (R02).
- `grep -c -i "enforced at the tool boundary"` on ARCH-006 returns 0: Met (R03).
- The revision-cycle grep returns only ARCH-006 stage 3: Met (R04).
- GOV-014 has a Test Author contract and no count of nine roles, and ARCH-006 stage 8 names the
  Test Author with its order and failure path: Met (R05; stage 8's Role and Failure path columns).
- No line in GOV-014, ARCH-006 or REQ-022 requires the owner to spot-audit: Met (R06).
- session-close.md step 3 mentions the session record only to exclude it: Met (R07).
- GOV-003 has the five entries: Met (R08).
- CLAUDE.md and AGENTS.md show the owner-confirmed text, or the record states confirmation was not
  given, for each of the three changes: Met. The owner answered each in this session on
  2026-10-04: AGENTS.md lines 179-181 left unchanged (they already state the `GOV-003` rule since
  `d9fa3bd`, 2026-09-28); AGENTS.md hand-off step 5 approved and applied as `PLAN-046` D5's text;
  CLAUDE.md's three lines (139, 143 and 146 today; the plan's 137, 141 and 144) approved and
  applied as D5's text. Commit `3f86477`.
- `git grep -n -w main` over the five files lists each remaining main with its reason, and
  session-close.md no longer presents the primary-checkout exception as current: Met (R12; none
  remain).
- PLAN-005's passage carries the superseded note, and REQ-003 has no triaging status: Met (R13).
- Verification list: Met — every command above ran green after Owner Terminal entry C14.

## Backlog

`status: active`. `next_action`: awaiting the owner's merge approval through READY, then the
completion edit on dev.

## Unresolved

- The `GOV-003` worktree-removal entry records that `AGENTS.md` and `/session-start` step 9 still
  remove the worktree without its own approval. Neither text is in this phase's scope; it is idea
  `000566`.

## Review

Independent review by a fresh `demo-adversary` agent over `dev...HEAD` at `3cfb328`, given
`REQ-029`, `PLAN-046` and the phase's acceptance, verification and deliverables, and told not to
read this record (the rule this phase writes into `/session-close` step 3). Its findings, condition
by condition:

1. Completion grep: **Holds**, with finding 2's caveat.
2. Owner-reserved lists diff empty: **Holds** (byte-for-byte).
3. "enforced at the tool boundary" count 0: **Holds**.
4. Revision-cycle grep returns only stage 3: **Holds**.
5. Test Author contract, no "nine", stage 8 names it: **Holds**.
6. No owner spot-audit requirement: **Holds**; the remaining hit is descriptive.
7. session-close step 3 mentions the record only to exclude it: **Holds**.
8. Five GOV-003 entries: **Holds**; each marked standing and names what it changes.
9. AGENTS.md and CLAUDE.md match `PLAN-046` D5's text exactly; 179-181 untouched: **Holds**.
10. No `main` in the five files; session-close states the exception was withdrawn: **Holds**.
11. PLAN-005 note and no `triaging` in REQ-003: **Holds**.

Verification: `--check` and one test fail on `.agents/skills/orient/SKILL.md` only; governance OK;
catalog diff clean; `1 failed, 1418 passed, 1 skipped`, the failure being that adapter. Changes are
confined to the deliverables, the phase's backlog line, the catalog and this record.

Findings:

1. **Major.** `GOV-018` step 5 gained a sentence the rulings do not authorize: "The revised plan from
   the first cycle is reviewed again with this procedure before the second." `PLAN-046` D2 changes
   only the cycle count; the old text disclaimed a second review, and the procedure has no step for
   one. A builder would read a mandatory re-review into the flow.
2. **Minor.** `REQ-029` R01's literal grep returns nine lines, all quoting `GOV-003`'s entry title
   "…replaces owner-invoked /session-close…" as the pointer. None asserts owner-only completion, so
   the backlog acceptance holds, but R01's wording read literally flags them.
3. **Informational.** `GOV-001` and `GOV-002` had no `main` on `dev` when the phase started;
   `REQ-029` problem 9's line numbers are stale for them.

Disposition: finding 1 fixed — the sentence is removed and the original disclaimer kept, with only
the count changed ("This procedure does not define a second review of the revised plan. `ARCH-006`
provides two revision cycles, after which unresolved blockers go to G3."). Finding 2 accepted: the
hits are the pointer R01 asks each file to carry, and changing `REQ-029` is outside this phase.
Finding 3 needs no change.

## Decisions

- The three `AGENTS.md`/`CLAUDE.md` changes were put to the owner before the claim. `AGENTS.md`
  179-181 already stated the `GOV-003` rule after the owner-approved commit `d9fa3bd`
  (2026-09-28), so the owner ruled it unchanged rather than applying `PLAN-046`'s older text.
  The `CLAUDE.md` lines had moved from 137, 141 and 144 to 139, 143 and 146.
- By owner ruling of 2026-10-04 the claim replaced the `docs/08-governance/` deliverable with the
  seven files the scope amends, so the phase could run beside `phase-des-11` and `phase-rel-08`.
- `.agents/skills/orient/SKILL.md` is closed to agents. The generator's output for it was written to
  the session's scratchpad and the regeneration queued for the owner (Owner Terminal entry C14);
  the `.claude` copy was regenerated here.
- The agent-proposed entry uses the label form in use on the log, `[agent-proposed by <session>]`,
  which the owner re-ruled on the Session Manager's board; `REQ-029` R08's "Proposed by <session>,
  not the owner" is its example only.

## Corrections

- A first pass at re-wrapping long lines rewrapped whole blocks, including untouched paragraphs, a
  front-matter block and a shell code block, and broke governance (`GOV-018`'s front matter).
  Caught before any commit; all edits were reverted and re-applied from one script with
  hand-wrapped text.
- The `GOV-018` sentence in review finding 1 was mine; removed.

## Left undone

- The Q8 worktree-removal ruling is recorded, but `AGENTS.md` and `/session-start` step 9 still
  describe the removal as automatic (idea `000566`).
