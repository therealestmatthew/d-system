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

Run in `/code/d-system-worktrees/phase-dam-01` on `agent/phase-dam-01`, branched from dev `27c3813`.

`uv run python tools/generate_agent_workflows.py --check`

```
missing or stale workflow adapter(s): .agents/skills/orient/SKILL.md
```

`uv run python -m src.governance --catalog` then `uv run python -m src.governance`

```
Governance OK: 44 systems, 428 documents, 36 memories, 347 backlog phases
```

`git diff --exit-code docs/08-governance/catalog.md`: exit 0, no diff.

`uv run pytest`

```
FAILED test/test_agent_workflows.py::test_committed_adapters_match_canonical_sources
1 failed, 1418 passed, 1 skipped, 1 warning
```

Both failures are the same file. `.agents/skills/orient/SKILL.md` is closed to agents by a deny
rule; its regeneration is queued for the owner as Owner Terminal entry C14. The `.claude` copy is
regenerated and current.

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
- Verification list: Not met until Owner Terminal entry C14 regenerates
  `.agents/skills/orient/SKILL.md`; `generate_agent_workflows.py --check` and one test fail on that
  file only.

## Backlog

`status: active`. `next_action`: commit `.agents/skills/orient/SKILL.md` after Owner Terminal entry
C14, rerun the verification list, then the independent review and READY.

## Unresolved

- `.agents/skills/orient/SKILL.md` waits for Owner Terminal entry C14.
- The `GOV-003` worktree-removal entry records that `AGENTS.md` and `/session-start` step 9 still
  remove the worktree without its own approval. Neither text is in this phase's scope; the gap was
  sent to Ideation as an idea.
