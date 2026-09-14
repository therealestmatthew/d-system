---
schema_version: 1
id: doc-session-reusable-partition-pack
code: SESS-2026-09-14-04
title: Write the reusable partition pack (PROMPT-034)
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-governance
depends_on:
- doc-repeatable-idea-partition
- doc-prompt-pack-protocol
---

# Write the reusable partition pack (PROMPT-034)

## Phase

`phase-part-01` — Write the reusable partition pack. Claimed as `agent-partition`, worked in
`../d-system-worktrees/phase-part-01` on `agent/phase-part-01`.

This record covers one phase. It is a separate record from `SESS-2026-09-14-03`, which closed
earlier today and covered no phase at all; that record's `## Phase` section names none, so this is
the first record for `phase-part-01` rather than a duplicate.

## Verification

The phase declares four verification entries. Two are prose checks and two are commands.

**1. Read `PROMPT-034` for a pinned number or a per-build ruling.** Run as a grep for the first
sweep's pinned corpus size, its dates, and its kick-off language:

```
grep -nE "\b129\b|2026-09-1[23]|kick-off|kickoff delta" docs/02-prompts/PROMPT-034-reusable-partition-pack.md
  -> no output
```

**2. Diff the control brief against the analyst brief.** The `R4` fenced block was extracted
programmatically and searched for every term `REQ-009` R08 forbids:

```
R4 dispatched block: 59 lines
NO LEAKS in the dispatched text.
  (searched: finding, control, other analyst, another analyst, differs, R1, ablation, bias, layered)
```

The `R4` block reads `_working/idea-corpus/corpus-R4.md` and writes `report-R4.md`, matching the
control's corpus file.

**3. `git diff dev -- docs/02-prompts/PROMPT-032-idea-batching-delegation-pack.md` is empty.**

```
git diff dev -- docs/02-prompts/PROMPT-032-idea-batching-delegation-pack.md | wc -l
  -> 0
```

**4. `uv run python -m src.governance` exits 0 with `PROMPT-034` present and the catalog
regenerated.**

```
uv run python -m src.governance
  -> Governance OK: 20 systems, 212 documents, 23 memories, 148 backlog phases
```

Additional checks run beyond the declared list:

```
uv run pytest -q
  -> 580 passed, 2 warnings

uv run python tools/check_no_private_content.py
  -> check_no_private_content: OK (574 tracked files, 0 identifiers checked)
```

The identifier count is `0` because this is a worktree and `_private/portfolio/` exists only in the
primary checkout. That is the gate's known weakness, not a pass; the primary-checkout run must be
the one that gates integration.

Per-block structure, computed from the document:

```
### R1 — the finding-reading analyst    idempotency=YES  fenced=yes
### R4 — the control (no findings)      idempotency=YES  fenced=yes
### A1 — adversarial audit 1            idempotency=YES  fenced=yes
### S  — synthesis protocol             idempotency=no   fenced=yes
### A2 — adversarial audit 2            idempotency=YES  fenced=yes
### G  — the gate                       idempotency=YES  fenced=yes
```

## Acceptance

**1. All six blocks present, each independently dispatchable and opening with the idempotency
sentence — NOT MET as written.** All six blocks exist in order. Five carry the idempotency sentence.
`S` does not, and is not dispatchable, because it is not a dispatch: it is the protocol the
coordinating session runs itself, and `PROMPT-032` marks its own `S` the same way — "**Not a
dispatch.**", with no idempotency sentence. The document follows the established convention
correctly; the condition as drafted demands dispatchability of a block that is defined as not being
one. This is a defect in the acceptance condition rather than in the deliverable, and it is recorded
as unmet rather than silently reinterpreted. Resolving it is an owner decision at close: amend the
condition to exempt `S`, or require an idempotency sentence on `S` against the precedent.

**2. No pinned corpus size, per-build owner ruling or kick-off delta anywhere — Met.** The grep in
verification 1 returns nothing.

**3. The control brief mentions findings, other analysts and differing input nowhere — Met.** The
dispatched `R4` block is clean across all nine searched terms. Stated precisely, because the
distinction matters: the prose *above* the fence does name findings and the control, in the standing
warning that tells the dispatching coordinator never to leak them. That warning is instruction to
the dispatcher, not part of the brief that gets sent, and `PROMPT-032` carries the identical warning
above its own control block. The brief — the text actually dispatched — carries nothing.

**4. The dispatch table states the ordering variation is dropped and cites `000205` — Met.** The
"Section letters" table lists the six letters, and the paragraph beneath it records that `R2` and
`R3` go unused, why the first sweep ran them, that audit 1 found the variation changed presentation
but not the answer, and cites `000205` as the record of that result.

**5. `PROMPT-032` is unchanged by this phase — Met.** The diff in verification 3 is empty, and
`PROMPT-032` keeps `status: active` as the record of the first sweep.

## Backlog

`phase-part-01` stays **`status: active`** with `agent: agent-partition`. Acceptance condition 1 is
unmet, so this phase is not a candidate for closure in its current state regardless of anything
else.

`next_action`: Rule on acceptance condition 1, which demands an idempotency sentence and
dispatchability of `S` — a block that is by definition not a dispatch, and that `PROMPT-032`
marks the same way. Either exempt `S` in the condition or require the sentence against precedent.
The deliverable itself needs no change for conditions 2 through 5.

`deliverables` was widened on `dev` to include `docs/08-governance/codes.yaml`, because
`src/governance/codes.py:205` requires a code's reservation to be removed in the same change that
spends it, and this repository has had repeated code races, so the lock belongs where peers can see
it.

`next_up` was **not** pruned. `phase-part-01` is still listed and is still `active`; nothing reached
`complete` this run.

## Unresolved

- **Acceptance condition 1's wording**, as above — the one thing blocking this phase.
- **The branch is unmerged.** `agent/phase-part-01` carries `b503db5` and is pushed; integration
  needs the owner's approval and a primary-checkout gate run.
- **`phase-part-02` and `phase-part-03` remain blocked.** `phase-part-02` declares `sys-portfolio`,
  which the active `phase-demo-07` locks, and `phase-part-03` depends on `phase-part-02`. So the
  `/partition-ideas` skill cannot be built until that lock clears. The owner ruled on 2026-09-14 to
  leave the declaration as-is and defer both rather than narrow it.
- **`max_active` is 3 of 3** with this claim, so no further phase can be claimed until one
  completes.
- **The idea-triage sweep is deferred** for the same `sys-portfolio` lock. 23 ideas are open,
  `000208`–`000223` plus later arrivals.
- **`tools/build_idea_corpus.py` still emits `corpus-R2.md` and `corpus-R3.md`** unconditionally.
  `PROMPT-034` documents only the files it reads, which is correct for the pack, but the tool
  produces two corpora a four-dispatch sweep never opens. Tidying that belongs to `phase-part-02`,
  which owns the tool, and is not a defect in this phase's deliverable.
