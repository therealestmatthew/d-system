---
schema_version: 1
id: doc-session-document-backlog-governance-plan
code: SESS-2026-09-15-04
title: Finalize the document and backlog governance plan (P2)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-governance, sys-backlog]
depends_on: [doc-document-backlog-governance]
---

# Finalize the document and backlog governance plan (P2)

## Phase

`phase-prog-05` — Finalize the document and backlog governance plan (P2).

Third phase of the unattended overnight batch run by `agent-night`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 233 documents, 25 memories, 209 backlog phases
```

Exit 0. Documents 231 → 233: `REQ-015`, and this record. Phases 202 → 209 for the seven
`phase-dgov-*` phases. An earlier run during the session reported `232 documents`, correctly — this
record did not exist yet. The final figure is the one recorded here.

`uv run python -m src.governance --ready`

```
| phase-dgov-01 | Rule when a requirement is mandatory, classify the corpus, enforce forward | — | 1 | ready | — | — |
| phase-dgov-03 | Audit every index width against a stated horizon and widen what is short | — | 1 | ready | — | — |
| phase-dgov-04 | Split completed phases into a backlog archive, and measure the saving | — | 2 | ready | — | phase-prog-05 |
| phase-dgov-05 | Write the backlog review and re-prioritisation procedure | — | 3 | ready | — | phase-prog-05 |
| phase-dgov-07 | Register _tmpagent in the systems maturity registry | — | 3 | ready | — | — |
```

Five of seven are `ready`. The two absent are correct and are the interesting result: `phase-dgov-02`
waits on `phase-idg-10` in `P1`, and `phase-dgov-06` waits on `phase-gov-01` in `PLAN-010`. Both
dependencies reach outside this programme.

`uv run pytest`

```
580 passed, 2 warnings
```

### The `phase-gov-01` overlap check, which the acceptance requires

Read `phase-gov-01`'s backlog entry directly rather than inferring from its title.

- **Function: distinct.** `phase-gov-01` rejects a backlog *deliverable whose filename carries an
  unreserved code* — pre-hoc, on declarations, before work starts. `G07`'s check diffs a *completed
  phase's actual change set* against those declarations — post-hoc, on what happened. Neither
  subsumes the other.
- **Files: collide.** Both declare `src/governance/backlog.py` and `test/test_backlog.py`. They
  cannot run concurrently.

Ruled: not merged, and `phase-dgov-06` declares `depends_on: [phase-gov-01]`. The `--ready` output
above confirms the tool agrees — `phase-dgov-06` does not appear as ready.

## Acceptance

- **`PLAN-030` carries no placeholder banner and states a chosen design.** Met. Banner removed,
  `status` `draft` → `active`, seven numbered rulings each naming the option refused and its cost.
- **A requirement document exists for P2 and every row maps to at least one phase.** Met. `REQ-015`
  carries fourteen rows; the mapping is total in both directions, checked against the backlog
  entries rather than the plan's own table.
- **Overlap with the already-queued `phase-gov-01` is checked and stated.** Met. Checked against
  that phase's real entry and stated twice — as design decision 6 in `PLAN-030`, and as a
  `depends_on` edge the validator enforces. The distinction recorded is that the overlap is on
  files, not on function.
- **`phase-prog-05` is removed from `next_up` in the same change that completes it.** Met. Removed in
  the same commit that registers the track.

## Backlog

`phase-prog-05` is `status: complete`, `agent: agent-night`,
`session: doc-session-document-backlog-governance-plan`. Completion evidence is `PLAN-030`,
`REQ-015`, `docs/09-backlog/README.md` and this record.

Written under the owner's advance authority for this batch, and only after the read-only independent
review below confirmed all four conditions.

Seven phases added under `phase-dgov-*`, all `status: queued`, none claimed.

## Review

A fresh non-fork sub-agent with read-only tools reviewed `dev...agent/phase-prog-05`. Its own runs:

```
$ uv run python -m src.governance
Governance OK: 27 systems, 233 documents, 25 memories, 209 backlog phases
EXIT=0

$ uv run pytest
580 passed, 2 warnings
```

**Condition 1 — no placeholder banner, states a chosen design — Met.** "`grep -ni
"placeholder\|TBD\|TODO\|XXX"` … returned nothing. `status: draft` → `status: active`… Seven numbered
'chosen design' rulings are present…, each naming the rejected alternative and its cost."

**Condition 2 — requirement exists, every row maps to a phase — Met.** "Checked directly against
`docs/09-backlog/backlog.yaml`, not against PLAN-030's own coverage table… every row's id appears
verbatim in exactly one `phase-dgov-*` entry's `acceptance` block… Coverage is total in both
directions."

**Condition 3 — the `phase-gov-01` overlap is checked and stated — Met.** The reviewer read that
phase's real entry and tested both halves of the claim: "its job is rejecting a *declared* deliverable
whose filename carries an unreserved code — pre-hoc… `phase-dgov-06`'s deliverables … are the
identical two paths, but its job is diffing a *completed phase's actual git diff* against its declared
paths — post-hoc… **Functions verified distinct; files verified identical (both halves of the claim
hold).**"

**Condition 4 — removed from `next_up` in the same change — Met.** "`- phase-prog-05` removed from
`next_up` in the same (and only) commit `744d4c8` that adds the seven `phase-dgov-*` phases. No
separate commit does this."

**The cross-programme dependency was verified against the data, not the prose.** "`phase-idg-10` … is
confirmed present on `dev` before this branch… `phase-dgov-02` declares `depends_on: [phase-idg-10]`
in `backlog.yaml`. All asserted, all real."

**`backlog.yaml` integrity.** "Parses cleanly (209 items); no actual YAML anchor/alias syntax
anywhere… Diffed every pre-existing item's parsed dict between `dev` and the branch: **0 changed, 0
missing** — only the 7 new ids were added, and `next_up` lost exactly one entry."

**Three findings, none blocking.**

- *`phase-prog-05`'s own deliverables do not cover `backlog.yaml`, which the diff rewrites by 242
  lines.* The reviewer noted the phase "instantiates the pattern it flags for the future containment
  check." **Not fixed** — it is the known track-wide gap, already staged as an idea candidate and
  already predicted by `R12`. Changing the declaration shape mid-run would make the ten phases
  inconsistent with each other.
- *`phase-dgov-04` collides with `phase-gov-01` and `phase-dgov-06` on `src/governance/` and
  `test/test_backlog.py`, undeclared*, while decision 6 devotes a whole ruling to the identical-file
  collision between the other two. The reviewer ran the repository's own `path_conflict()` to
  establish it. The inconsistency is real: the plan applied its own methodology to one pair and not
  the other. **Fixed** — the concurrency section now states the three-way contention, and says why no
  `depends_on` edge follows from it.
- *The session record's document count was off by one* (232 against 233, this record being the
  233rd). **Fixed.**

## Decisions

**`000056` and `000047` do not merge — the design question the scope named.** They fail differently:
`000047` asks whether a document is well written, `000056` whether it is still true. A beautifully
structured plan describing a system refactored last week passes everything `000047` could test and is
exactly what `000056` exists to catch. Merging would let the easier question crowd out the harder.
The shared surface is handled by `R05` making the staleness mechanism *consume* the plan-quality
standard rather than define a second one.

**That ruling created a cross-programme dependency, recorded rather than left implicit.** `000047` is
no longer unowned — `phase-prog-04` sized it as `phase-idg-10` two hours earlier tonight. So
`phase-dgov-02` depends on a phase in `P1`, and `P1` should run before `P2` even though the queue
orders them the other way. Written into `depends_on`, so the validator carries it rather than a
reader having to notice.

**Staleness is defined against subject, never age.** A date rule is trivial and would flag `ADR-003`,
among the oldest documents and entirely current, while missing one written last week describing a
route renamed since. `CLAUDE.md`'s own no-remote rule — correct when written, false the moment
`phase-priv-05` pushed, stale in two files until someone looked — is the case the mechanism exists
for.

**The requirement rule is applied to the corpus before it is enforced.** Enforcing first would turn
`dev` red on 14-plus plans predating the rule, which is a way of discovering the rule is too strict
by breaking the trunk. Grandfathering is a list, not a blanket exemption, so the backlog of unpaired
plans stays visible and finite.

**The containment check reports and never blocks**, and `R12` predicts its own first result. One
violation class is already known: every `phase-prog-*` phase rewrites `backlog.yaml` without
declaring it — including the three that produced this plan. A first run reporting zero findings would
contradict evidence in hand and should be read as a broken check.

**`phase-dgov-07` is honestly under-sized and says so.** One `systems.yaml` entry. It was not folded
into a neighbour because the candidates are unrelated work, and bundling unrelated trivia produces a
phase that cannot be reviewed as a unit. Its `next_action` tells whoever claims an adjacent phase to
take it in the same sitting.

## Corrections

None this phase. The duplicate-anchor trap from `phase-prog-04` did not recur — the append used an
alias-free dumper and asserted no anchor was emitted before writing.

## Unresolved

**Whether `phase-dgov-05` should exist yet.** `000011` says defining a re-prioritisation process
before it has ever been needed is building ahead of demand, and the backlog is nowhere near empty —
209 phases with 40-plus ready. Options: size it now, or leave the idea parked until an empty ready
set actually occurs. **Sized it**, because the programme is being finalized as a whole and a plan with
a deliberate hole is harder to read than one with a phase carrying its own caveat. The phase's
`next_action` tells whoever claims it to confirm with the owner that the need is real before building
the command half.

**Whether the partition's programme-level sizing or its group table governs.** `P2` is stated at 4–5
phases at programme level, while its own group table sums to 5–6 plus two fragments. **Followed the
group table**, landing at seven, because the group figures were derived per-group from the ideas and
the programme figure appears to be a round-up. Recorded as an idea candidate, since the same
discrepancy may affect the remaining programmes' estimates.

**Whether `phase-dgov-04`'s split should wait for the containment check.** Splitting `backlog.yaml`
moves every completed phase to a new file, which is exactly the kind of change the containment check
would flag against every phase's declarations. Options: sequence the split after the check, or leave
them independent. **Left independent**, because the check reports rather than blocks and the split is
a governed, deliberate move — but whoever runs both should expect the first containment run after the
split to be noisy.

## Left undone

**All seven phases.** This phase finalizes a plan and builds nothing.

**`phase-gov-01` was checked but not claimed.** It is ready, small, blocked by nothing, and it
releases `phase-dgov-06`. Taking it was outside this phase's scope and outside this run's authority,
which covers ten `phase-prog-*` phases only. Flagged in `PLAN-030` as the cheapest unblocking move in
the programme.

**`000204` is named but not addressed.** The plan records that `G07`'s containment check is the
nearest mechanism to hang it on, and that `phase-dgov-06` does not close it. `000204` is not a member
of this programme.
