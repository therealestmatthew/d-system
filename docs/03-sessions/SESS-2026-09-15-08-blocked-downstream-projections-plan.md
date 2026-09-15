---
schema_version: 1
id: doc-session-blocked-downstream-projections-plan
code: SESS-2026-09-15-08
title: Finalize the blocked downstream projections plan (P7)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-projection, sys-portfolio]
depends_on: [doc-blocked-downstream-projections]
---

# Finalize the blocked downstream projections plan (P7)

## Phase

`phase-prog-09` — Finalize the blocked downstream projections plan (P7).

Seventh phase of the unattended overnight batch run by `agent-night`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 241 documents, 25 memories, 242 backlog phases
```

Exit 0. Documents 239 → 241: `REQ-019`, and this record. Phases 238 → 242 for the four `phase-proj-*`
phases. An earlier run during the session reported `240 documents`, before this record existed.

`uv run python -m src.governance --ready`

```
| phase-proj-01 | Answer the portfolio data question against the real root | — | 2 | ready | — | — |
| phase-proj-02 | Deterministic as-of snapshots and two-point diffs | — | 3 | ready | — | phase-prog-09 |
```

Two of four are `ready`. The other two were created `deferred` with `resume_when` gates, which is
deliberate and is the substance of this phase's third acceptance condition. `phase-proj-01` shows
`Conflicts: —` against this phase's own live claim, because it declares `sys-portfolio` where
`phase-prog-09` declares `sys-projection`.

`uv run pytest`

```
580 passed, 2 warnings
```

### The measurement the scope asked for, and why it stops where it does

```
$ for d in projects people commitments tasks; do printf "%-14s %s\n" "$d" "$(ls _data/$d | wc -l)"; done
projects       5
people         1
commitments    1
tasks          3

$ test -d _private && echo present || echo "absent in this worktree"
absent in this worktree
```

`000022` cites "33 populated `_data/projects/*.json` files… against zero commitments or people". Both
halves have moved, and neither because the gap closed: `phase-priv-03` (`status: complete`) relocated
the real records to `_private/portfolio/` and seeded `_data/` as a fictional example set per
`ADR-009`.

The correct root is therefore `_private/portfolio/`, which is gitignored, absent from every worktree,
and which `AGENTS.md` puts off-limits: "Never read or write there unless the owner directs you to."
This run's prompt does not direct it. **No part of `_private/` was read.**

## Acceptance

- **`PLAN-034` carries no placeholder banner and states a chosen design.** Met. Banner removed,
  `status` `draft` → `active`, three numbered rulings plus the `G31` analysis.
- **`G31` is resolved, or the plan states exactly what the owner must answer.** Met on the second
  branch, which the condition offers explicitly. The plan states one question — do `people` and
  `commitments` hold records in the real portfolio, and if not, is it friction or no need — supplies
  the runnable command against `D_SYSTEM_DATA_ROOT=_private/portfolio`, and records what follows from
  each answer. It could not be met on the first branch without reading the owner's real portfolio.
- **`G32`'s decline nomination is ruled on rather than carried forward silently.** Met, by carrying
  the owner's existing ruling of 2026-09-13 — *kept, gate recorded* — rather than re-deciding it.
  Each of the three now carries a gate: `phase-proj-02` has none because its gate is already met, and
  `phase-proj-03` and `-04` are `deferred` with explicit `resume_when` and `blocked_reason`.
- **`phase-prog-09` is removed from `next_up` in the same change that completes it.** Met, in the
  same commit that registers the track.

## Backlog

`phase-prog-09` is `status: complete`, `agent: agent-night`,
`session: doc-session-blocked-downstream-projections-plan`. Completion evidence is `PLAN-034`,
`REQ-019`, `docs/09-backlog/README.md` and this record. Written under the owner's advance authority
for this batch, after the read-only independent review below confirmed all four conditions.

Four phases added under `phase-proj-*`: two `queued`, two `deferred` with gates. None claimed.

## Review

A fresh non-fork sub-agent with read-only tools reviewed `dev...agent/phase-prog-09`, and was told
`_private/` was off-limits to it as well. Its runs:

```
$ uv run python -m src.governance
Governance OK: 27 systems, 241 documents, 25 memories, 242 backlog phases
EXIT: 0

$ uv run pytest
580 passed, 2 warnings
```

**Condition 1 — no placeholder banner, states a chosen design — Met.** Confirmed by diffing `dev`'s
copy: the banner and its "Do not build from this document" line are gone, `status: draft` → `active`.

**Condition 2 — `G31` resolved, or the plan states exactly what the owner must answer — Met on the
second branch. The reviewer was asked to judge whether that was an evasion, and ruled it was not.**

> "`AGENTS.md:111` reads verbatim: '`_private/` is gitignored. Never read or write files there unless
> the user directs you to.' That is an absolute rule requiring explicit direction, not implication.
> The scope's phrase 'measured against the correct data root' names which root is authoritative; it
> does not instruct a read of it. It is naming, not granting access — a defensible reading, not a
> rules-lawyered one, and the session record's own 'Unresolved' section states this ambiguity plainly
> rather than hiding it."

It also checked the command actually works, which this phase had not verified to that depth:
`tools/rebuild_db.py` and `source_validation.py`'s `data_root()` confirm `D_SYSTEM_DATA_ROOT` support
exists, added by `phase-priv-03`, "whose own acceptance required 'the owner's real records still
rebuild when the data root points at `_private/portfolio/`' — so the mirrored subdirectory structure
the count loop assumes is a documented guarantee, not a guess." And it caught a detail this phase got
right by habit rather than by design: "Plain `ls` (no `-a`) excludes `.gitkeep`, so a placeholder-only
directory correctly counts as 0, avoiding the exact trap that made `000022`'s original reading
ambiguous."

**The privacy boundary was verified independently, not taken on trust.**

```
$ git ls-tree -r agent/phase-prog-09 --name-only | grep '^_private'   → no match (exit 1)
$ git diff --name-only dev...agent/phase-prog-09                      → only the 6 deliverable files
$ uv run python tools/check_no_private_content.py                     → OK (645 tracked files)
```

**Condition 3 — `G32`'s decline nomination ruled on — Met.** The reviewer quoted the owner's ruling
verbatim from the partition and confirmed the implementation: both deferred phases carry
`resume_when` and `blocked_reason`, matching `phase-mem-15`'s shape and the fields
`src/governance/backlog.py` requires for `deferred`. It also caught a distinction worth having: the
ruling's fourth idea, `000030`, "is a different idea in a different programme… PLAN-034 correctly
leaves it alone."

**Condition 4 — removed from `next_up` in the same change — Met**, and the reviewer established
something useful about the whole batch: it checked all eight prior `phase-prog-*` phases and found the
removal always lands in the finalize commit, never in the later close commit, because "only
`/session-close` can set `status: complete`, [so] an agent commit literally cannot satisfy a stricter
reading of 'the same change'."

**Both staleness claims were checked byte-for-byte** through `fold()` and live counts, and both
matched. `phase-idea-07` complete and `fold()` at `src/db/ideas.py:230` both confirmed — "If either
were false, `phase-proj-02` would be wrongly queued — it isn't."

**One minor finding, fixed.** *`PLAN-034`'s coverage table overclaims `phase-proj-02` for `R04`.* That
phase's acceptance cites `R05` and `R06` only, and deliberately carries no gate, so it cannot assert
one. **Fixed**: the table now credits `R04` to `phase-proj-03` and `-04`, with a note explaining that
`000033`'s disposition still satisfies the requirement while the phase has no `resume_when` to check.

## Decisions

**`G31` took the acceptance's second branch, and the reason is a standing rule rather than a
shortfall.** Resolving it requires counting records under `_private/portfolio/`. That path holds the
owner's real client engagements, personal finances and health records; `AGENTS.md` forbids reading it
without direction, and this run has none. Counting files there for a phase-sizing question is not a
boundary worth crossing, so the plan states the question and the exact command instead.

**`000022`'s premise is stale, and saying so is most of `G31`'s value.** A reader checking the idea
against `_data/` today finds all four entities populated and could reasonably conclude the gap closed.
It did not; the ground moved. `R02` makes correcting this an acceptance condition of `phase-proj-01`
so the next reader does not repeat it.

**`G32` was not re-decided.** The control analyst nominated all three for decline; R1 declined to
nominate them at all, calling them "genuinely gated on prerequisites, not dead"; the owner upheld R1
on 2026-09-13 with "kept, gate recorded — each now names what unblocks it". This plan does that,
expressing each gate as a `resume_when` on a `deferred` phase rather than as prose, so the validator
carries it. `R04` makes a plan that declines them a contradiction of a recorded ruling.

**`000033` is not dormant, contrary to the partition.** Its stated prerequisite is `phase-idea-07`'s
fold; that phase is `status: complete` and `fold()` ships at `src/db/ideas.py:230` — this session read
the idea corpus through it. So `phase-proj-02` is `queued`, not `deferred`. This is the second
programme tonight where a gate proved met while the work behind it waited, after `P6`'s
`phase-mem-10`.

**Two phases were deliberately created `deferred`.** A plan is allowed to ship dormant phases when the
dormancy is real and the gate is named; that is what `status: deferred` plus `resume_when` is for, and
several `phase-mem-*` phases already use it. The alternative — omitting them and leaving the ideas
unplanned — would have lost the owner's ruling that they are kept.

## Corrections

None this phase.

## Unresolved

**Whether the owner would have wanted `_private/` counted.** The scope says "measured against the
correct data root", which could be read as directing the read. Options: read it as direction and
count, or treat `AGENTS.md`'s standing rule as governing. **Treated the standing rule as governing**,
because it is absolute in its wording and the phrase in the scope names a root rather than granting
access. If the owner intended the count, `phase-proj-01` becomes a five-minute job for them and the
plan already carries the command.

**Whether `phase-proj-04`'s gate is checkable.** Its `resume_when` says recommendations and outcomes
must have "accumulated in enough volume to calibrate against", which has no number. Options: invent a
threshold, or state the condition qualitatively. **Stated it qualitatively**, because nothing produces
recommendations today, so any number would be arbitrary in a way `P6`'s review date is not — there the
collector exists and is claimable. Flagged because it is the same shape as the gate defect `P6` found,
and it may deserve a number once something produces recommendations.

**Whether `phase-proj-03`'s dependency on `PLAN-002` should be a `depends_on` edge.** It needs
portfolio signals from the `phase-sig-*` line. Options: add the edge, or name it in the gate.
**Named it in the gate**, because the specific signal phases it needs are not determined yet and an
edge to the wrong one would be worse than prose. This is the fifth cross-programme dependency this
batch has produced.

## Left undone

**All four phases.** This phase finalizes a plan and builds nothing.

**`G31` itself.** The question is stated, not answered. That is the acceptance's second branch, taken
deliberately, and the answer needs the owner at a terminal for under a minute.

**The two `deferred` phases are not sized beyond one session each.** `session_budget: 1` is the
schema's requirement rather than an estimate; neither has been scoped in the detail a claimable phase
would need, because both are gated on things that do not exist.
