---
schema_version: 1
id: doc-session-reusable-partition-pack
code: SESS-2026-09-14-06
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
  -> Governance OK: 20 systems, 218 documents, 24 memories, 150 backlog phases
```

Additional checks run beyond the declared list:

```
uv run pytest -q
  -> 580 passed, 2 warnings

uv run python tools/check_no_private_content.py
  -> check_no_private_content: OK (609 tracked files, 0 identifiers checked)
```

Every figure above is the run **at close**, not at the mid-session checkpoint; the document and
phase counts moved because peers integrated throughout.

The identifier count is `0` because this is a worktree and `_private/portfolio/` exists only in the
primary checkout. That is the gate's known weakness, not a pass. The gating run happened in the
primary checkout at integration and reported **`31 identifiers checked`**.

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

**1. All six blocks present; the four dispatchable blocks open with the idempotency sentence; `S`
present and marked as not a dispatch — Met, against the condition as amended on 2026-09-14.**

This condition was **recorded unmet first**, and the sequence matters enough to keep in the record.
As originally drafted it required all six blocks to be "independently dispatchable and opening with
the idempotency sentence." All six blocks exist in order, and `R1`, `R4`, `A1`, `A2` and `G` each
carry the sentence — but `S` carries neither, because `S` is not a dispatch: it is the protocol the
coordinating session runs itself after the audits return, and `PROMPT-032` marks its own `S` as
"**Not a dispatch.**" with no idempotency sentence either. The deliverable followed the precedent;
the condition demanded dispatchability of a block defined as not being one.

The owner ratified the amendment on 2026-09-14: require the sentence of the dispatchable blocks, and
require `S` to be present and explicitly marked as not a dispatch. The rejected alternative was
adding the sentence to `S` so the original wording passed literally. The decision and its reasoning
are recorded in [GOV-003](../08-governance/GOV-003-backlog-decisions.md) under "A non-dispatch block
carries no idempotency sentence", including why it is recorded rather than quietly edited — an
acceptance list that can be amended silently after seeing the deliverable is worth nothing, because
nothing then distinguishes a wrong condition from a moved bar.

Against the amended condition: all six blocks present; `R1`, `R4`, `A1`, `A2` each open with the
idempotency sentence; `S` is headed "synthesis protocol" and marked `**Not a dispatch.**` in the
document. **Met.**

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

`phase-part-01` is **`status: complete`**, written by the owner-invoked `/session-close` on
2026-09-14 after the independent review in `## Review` corroborated all five acceptance verdicts.
`agent: agent-partition` is kept as the record of who did the work.

`result:` was rewritten at close to state the actual verification and review outcome. The review
found its previous text stale — it still said the branch was "pushed, unmerged" after integration —
and that was the only defect the review raised.

`next_action`: Complete. Closing this released `sys-governance`, unblocking `phase-port-02`,
`phase-ses-01`, `phase-prog-01`, `phase-prog-12`, `phase-gov-01`, `phase-gov-04`, `phase-gov-05`,
`phase-idea-05` and `phase-tool-02`. `phase-part-02` is next in this plan.

**`next_up` pruned:** `phase-part-01` removed, per `AGENTS.md`'s rule that a phase leaves `next_up`
in the same change that completes it.

`deliverables` was widened twice. `docs/08-governance/codes.yaml` was added on `dev` in its own
commit, because `src/governance/codes.py:205` requires a code's reservation to be removed in the
same change that spends it, and this repository has had repeated code races, so the lock belongs
where peers can see it. `docs/08-governance/GOV-003-backlog-decisions.md` was added later, on the
branch rather than on `dev`, to carry the acceptance amendment. That is a deviation from
`AGENTS.md`'s "update the declarations on `dev`" instruction, taken because integration followed
within minutes and no peer held `sys-governance` at the time — recorded here rather than left
implicit.



## Unresolved

- **Nothing blocks this phase.** Condition 1's wording was resolved by owner ruling on 2026-09-14
  and recorded in `GOV-003`; the branch is integrated. Only `/session-close` remains, which is the
  owner's to run.
- **`phase-part-02` is now unblocked.** `phase-demo-07` reached `complete` later on 2026-09-14,
  releasing `sys-portfolio`, so `phase-part-02` shows no conflict and is ready to claim.
  `phase-part-03` — the `/partition-ideas` skill — still waits on `phase-part-02` by `depends_on`,
  and additionally needs `sys-governance` free, so it follows this phase's closure.
- **This phase's claim is now the queue's bottleneck.** It holds `sys-governance`, which conflicts
  with nine ready phases — `phase-port-02`, `phase-ses-01`, `phase-prog-01` (P3), `phase-prog-12`,
  `phase-gov-01`, `phase-gov-04`, `phase-gov-05`, `phase-idea-05` and `phase-tool-02`. Closing it
  releases all nine. `max_active` is 1 of 3 since two peers closed.
- **The idea-triage sweep is no longer blocked** — `sys-portfolio` is free. 24 ideas are open,
  `000208` onward, and the set has grown every time it was checked this session.
- **`tools/build_idea_corpus.py` still emits `corpus-R2.md` and `corpus-R3.md`** unconditionally.
  `PROMPT-034` documents only the files it reads, which is correct for the pack, but the tool
  produces two corpora a four-dispatch sweep never opens. Tidying that belongs to `phase-part-02`,
  which owns the tool, and is not a defect in this phase's deliverable.

## Review

Independent review at close by a fresh general-purpose sub-agent (sonnet), given the six commit
hashes individually, the scope, acceptance and verification lists, the record's path, and none of
this session's reasoning. It was asked specifically to scrutinise the condition-1 amendment as a
possible lowered bar rather than accept this record's framing of it. Its findings, verbatim:

**1. PROMPT-034 contains all six blocks; R1/R4/A1/A2 open with the idempotency sentence; S present
and marked not-a-dispatch — CONFIRMED (against the amended wording).**

Read `docs/02-prompts/PROMPT-034-reusable-partition-pack.md` directly and extracted each fenced
block programmatically:

```
### R1 — the finding-reading analyst    idempotency=YES  fenced=yes
### R4 — the control (no findings)      idempotency=YES  fenced=yes
### A1 — adversarial audit 1            idempotency=YES  fenced=yes
### S  — synthesis protocol             idempotency=no   fenced=yes   ("**Not a dispatch.**")
### A2 — adversarial audit 2            idempotency=YES  fenced=yes
### G  — the gate                       idempotency=YES  fenced=yes
```

All six blocks exist, in order. R1/R4/A1/A2 each literally open with "Assess the current state of
the repository against the deliverables below; do only what is missing; report what already
existed." S is headed "**Not a dispatch.**" (line 318) and its fenced block opens with "You have two
analyst reports and audit 1's findings" — no idempotency sentence, matching the amended condition
exactly.

**2. No pinned corpus size, per-build owner ruling or kick-off delta anywhere — CONFIRMED.**

```
grep -nE "\b129\b|2026-09-1[23]|kick-off|kickoff delta|pinned|per-build" PROMPT-034-...md
41:This pack carries no pinned corpus size, no per-run owner ruling and no record of what any
```

The only hit is the sentence *disclaiming* those things. No actual pinned number, date, or ruling
appears anywhere.

**3. The control brief mentions findings, other analysts, differing input nowhere — CONFIRMED.**
Extracted the R4 fenced block (59 lines) and searched it for: finding, control, other analyst,
another analyst, differs, R1, ablation, bias, layered — zero hits. Diffed R1's fenced block against
R4's: the only differences are the corpus filename (`corpus-R1.md` vs `corpus-R4.md`, "title, body,
links and findings" vs "title, body and links"), the removal of the "MORE THAN ONE finding"
paragraph, and the report filename — exactly the REQ-009 R08 removals, nothing more, nothing less.

**4. Dispatch table states the ordering variation is dropped and cites 000205 — CONFIRMED.**
The "Section letters" table plus its following paragraph (lines 56–64) states R2/R3 go unused,
explains the first sweep tested presentation order, that "audit 1 found that it changed presentation
but not the answer," and cites idea `000205` as that record. Single, correct citation.

**5. PROMPT-032 unchanged by this phase — CONFIRMED.**

```
git diff 9a513e2~1 7ebf55a -- docs/02-prompts/PROMPT-032-idea-batching-delegation-pack.md | wc -l
0
git log --oneline 9a513e2~1..7ebf55a -- docs/02-prompts/PROMPT-032-...md
(no output)
```

Diffed the actual commit range attributable to this phase (not just `dev` vs itself, which is
trivially empty) — genuinely zero touches.

### Its judgement on the condition-1 amendment

> **Sound correction, not a lowered bar.** I checked the premise myself rather than taking GOV-003's
> word for it: `PROMPT-032`'s own S section (lines 397–399) is headed `### S — synthesis protocol`
> immediately followed by "**Not a dispatch.** This is what the integrating agent does in the main
> session, after GATE 2," and its fenced block begins "You have four analyst reports and audit 1's
> findings" — no idempotency sentence. This is the exact document PROMPT-034 was instructed to
> extract from "unchanged in substance." The original condition's literal text was structurally
> unsatisfiable without contradicting the precedent it was supposed to preserve, or without bolting
> a nonsensical "re-send this safely" preamble onto a block that is never sent anywhere.
>
> What makes this legitimate rather than convenient: the record shows the condition was checkpointed
> as **unmet** first (`2a5accb`), *before* any amendment existed, and the amendment landed as a
> separate, later, explicitly-justified commit (`769f012`) with the rejected alternative ("add the
> sentence to S anyway") named and rejected on the record. That sequencing — fail first, then argue
> for the change — is the thing that distinguishes a correction from post-hoc rationalization, and it
> actually happened here, not just in prose.

### Discrepancies it found, most serious first

> 1. **`backlog.yaml`'s `result` field is stale.** It reads "Branch `agent/phase-part-01` at
> `b503db5`, pushed, unmerged." — written at the checkpoint (`2a5accb`) when that was true, but never
> updated after integration. Current `dev` HEAD *is* `7ebf55a`, so the branch is in fact merged.
> Minor (informational field, doesn't gate anything), but it will mislead anyone reading `result`
> without also reading `next_action`.
>
> 2. **Self-disclosed process deviation, correctly flagged.** `GOV-003` was added to the phase's
> `deliverables` on the branch itself (`769f012`), not via a `dev`-direct widening commit the way
> `codes.yaml` was (`fa60fc4`). This is a deviation from AGENTS.md's "update declarations on dev"
> instruction. It is not hidden — the session record's Backlog section names it explicitly and gives
> a reason. I confirmed the mechanical fact matches the confession; nothing is concealed. Not a
> defect I'm raising fresh, just confirming the self-report is accurate.
>
> Everything else checked — the codes.yaml removal's necessity, scope containment, AGENTS.md/CLAUDE.md
> untouched, the descope ladder, audit 1's rewrite, the session renumber — matched what the record
> claims, with no unflagged gap.

### Its supporting checks

- **Scope containment**: every file touched across all six commits is inside declared deliverables
  plus the catalog, its own session record and its own backlog lines. Nothing outside.
- **AGENTS.md / CLAUDE.md**: untouched by any of the six commits, verified via `git show --name-only`
  on each.
- **codes.yaml removal necessity**: read `src/governance/codes.py` lines 162–201 — the
  `held.get(code) == "reserved"` check fires unconditionally for every document, not gated behind
  the `strict` flag. Removal was genuinely mandatory, not discretionary.
- **Descope ladder**: three rungs (A2, A1, R4), no mention of R2/R3 as live dispatches.
- **Audit 1 convergence check**: fully rewritten for one reader plus one control — two named
  explanations, a per-divergence argument requirement, "I cannot tell" accepted. No stale
  3-1/majority language survives as active logic.
- **Session renumber**: `-04` appears only in the peer's own untouched file and in peer prose
  describing the collision; no stray reference remains in anything this phase owns.

```
uv run python -m src.governance
  Governance OK: 20 systems, 218 documents, 24 memories, 150 backlog phases
uv run pytest -q
  580 passed, 2 warnings
uv run python tools/check_no_private_content.py
  check_no_private_content: OK (609 tracked files, 31 identifiers checked)
catalog regeneration vs committed file
  CATALOG-IN-SYNC
```

### Its overall verdict

> All five acceptance conditions genuinely hold against the amended condition 1, and the amendment
> itself is a defensible, well-evidenced correction rather than a bar lowered for convenience. [...]
> In my independent judgement, this phase legitimately meets its acceptance and may be marked
> complete.

### Response to the findings

Finding 1 is correct and is fixed in this close: `result:` is rewritten to state the actual
verification and review outcome, which step 6 of `session-close` requires in any case. Finding 2 is
a confirmation of this record's own disclosure rather than a new defect, and the deviation stands as
described — named, reasoned, and not repeated.

## Decisions

**The pack was written by a delegated agent, not by the coordinating session.** The owner asked for
agents to be used, so a general-purpose sonnet agent authored `PROMPT-034` from `PLAN-025`,
`REQ-009` and `PROMPT-032`. Two constraints shaped the dispatch: subagents inherit the primary
checkout as their working directory regardless of the coordinator's worktree, so the prompt carried
the absolute worktree path and forbade writes to `/code/d-system`; and subagents cannot write report
files, so the agent returned its account as text. Both facts are recorded as `000206`.

**Four dispatches, not six.** Carried in from the owner's earlier ruling and `PLAN-025`: audit 1
measured the corpus-ordering variation as changing presentation but not the answer (`000205`), so a
repeat sweep keeps only the findings ablation — one analyst that reads findings, one control that
does not. `R2` and `R3` keep their letters reserved rather than repurposed, so a reader arriving
from `PROMPT-032` is not misled.

**Acceptance condition 1 was amended, and the amendment was recorded rather than absorbed.** The
condition required all six blocks to be independently dispatchable and to open with the idempotency
sentence; `S` is neither, because `S` is the synthesis protocol the coordinator runs itself and
`PROMPT-032` marks its own `S` "**Not a dispatch.**" with no sentence either. The checkpoint recorded
the condition **unmet** first. The owner then ratified amending it to require the sentence of the
dispatchable blocks only. It is written up in
[GOV-003](../08-governance/GOV-003-backlog-decisions.md) with the rejected alternative and with the
reason recording matters: an acceptance list that can be amended silently after the deliverable is
seen cannot distinguish a wrong condition from a moved bar.

**The agent's one out-of-scope edit was verified before being accepted.** It removed `PROMPT-034`'s
reservation from `codes.yaml` and said governance required it. Rather than take that on trust,
`src/governance/codes.py:205` was read directly: it emits `"{code} is reserved; remove the
reservation in this change"`. The edit was required, not discretionary.

**Deliverables were widened twice, once correctly and once by deviation.** `codes.yaml` was added
to the phase's declared deliverables on `dev` in its own commit, so peers could see the lock on a
file this repository has raced repeatedly. `GOV-003` was added later on the branch instead of on
`dev`, because integration followed within minutes and no peer held `sys-governance`. That is a
deviation from `AGENTS.md`'s instruction to update declarations on `dev`, and it is named here
rather than left implicit.

**The idle corpus files were routed rather than fixed.** `tools/build_idea_corpus.py` still emits
`corpus-R2.md` and `corpus-R3.md`, which a four-dispatch sweep never opens. `PROMPT-034` documents
only the files it reads, which is right for the pack. Removing the dead generation belongs to
`phase-part-02`, which owns the tool; doing it here would have edited a file outside this phase's
deliverables to fix something this phase did not break.

**The session record was renumbered rather than the peer's.** `AGENTS.md`'s collision rule is that
the agent integrating second renumbers, and that was this branch.

## Corrections

**My own acceptance condition was wrong, and it took the deliverable to reveal it.** Condition 1
demanded a property — dispatchability, and a dispatch preamble — of `S`, a block whose whole
definition is that nothing dispatches it. I wrote that condition when drafting the phase, and
`PROMPT-032` had already settled the question in the opposite direction. The correction path was the
right one: record unmet, escalate to the owner, amend by ruling, write it into `GOV-003`. The
failure was in drafting an acceptance condition without checking it against the precedent the phase
was extracting from.

**A code race cost a rebase and five red tests.** After rebasing onto `dev`, a peer's
`SESS-2026-09-14-04-lit-06-followups.md` held the code this branch's record had taken, and
`codes.py:199` failed hard. Renumbering to `-06` fixed it (`-05` had gone to the consultant-demo-kit
record). Notable because minutes earlier this same session had written the owner a hand-off prompt
about this exact collision class for `phase-demo-07` — two independent instances in one day, both
caused by a branch holding a dated code while `dev` moved. That is evidence the pattern is
structural, and it belongs to `P3`.

**I ran `git merge --ff-only` inside the worktree, where it is a no-op, before running it in the
primary checkout.** Twice in this session, having already made the same slip earlier in the day. A
repeated slip rather than a one-off, so it is worth naming as a habit: the merge that integrates
always runs where `dev` is checked out, never where the branch is.

**The record's own `## Unresolved` section went stale mid-session.** It asserted that
`phase-part-02` and the triage sweep were blocked by `phase-demo-07`'s `sys-portfolio` lock; that
phase reached `complete` later the same day and the lock cleared. Corrected during close rather than
left to mislead the next reader — the same decay this session documented in `REQ-009` R05, arriving
in the session's own paperwork.

## Left undone

**The `/partition-ideas` skill does not exist.** `phase-part-03` builds it and depends on
`phase-part-02`, which was blocked by a peer's lock for most of the session and is now ready and
unclaimed. `PROMPT-034` is the skill's prerequisite and is the only part of that chain delivered
here. Nothing in this phase's scope covered the skill, so this is sequencing, not shortfall.

**`--status` is still a module constant.** `tools/build_idea_corpus.py` line 63 still fixes the
corpus to `triaged`, and the tool still has no tests at all. Both belong to `phase-part-02`, and
the `--stats` baseline must be captured from `dev` before that work starts, because `REQ-009` R03 is
verified by byte-identical output across the change and cannot be reconstructed afterwards.

**24-plus ideas remain untriaged**, `000208` onward. The set grew on every check during the session.
A partition sweep reads `triaged` ideas only, so an untriaged backlog is invisible to the pack this
phase just built.

**Nine phases were waiting on this claim.** `phase-port-02`, `phase-ses-01`, `phase-prog-01` (P3),
`phase-prog-12`, `phase-gov-01`, `phase-gov-04`, `phase-gov-05`, `phase-idea-05` and
`phase-tool-02` all conflict on `sys-governance`. Closing this phase releases every one of them;
that is the main practical consequence of this record.

**`PROMPT-032` keeps `status: active`** as the record of the first sweep, deliberately. No attempt
was made to consolidate the two packs, and none should be: one is a reusable method, the other is
what one particular run actually sent and cost.
