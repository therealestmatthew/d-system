---
schema_version: 1
id: doc-session-schema-consistency-testing-plan
code: SESS-2026-09-15-09
title: Finalize the schema consistency and testing plan (P8)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-contracts, sys-delivery]
depends_on: [doc-schema-consistency-testing]
---

# Finalize the schema consistency and testing plan (P8)

## Phase

`phase-prog-10` — Finalize the schema consistency and testing plan (P8).

Eighth phase of the unattended overnight batch run by `agent-night`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 243 documents, 25 memories, 248 backlog phases
```

Exit 0. Documents 241 → 243: `REQ-020`, and this record. Phases 242 → 248 for the six `phase-sch-*`
phases. An earlier run during the session reported `242 documents`, before this record existed.

`uv run python -m src.governance --ready`

```
| phase-sch-01 | Record 000024's real state, propose the CLAUDE.md text, and add the drift check | — | 2 | ready | — | phase-prog-10 |
| phase-sch-03 | Add a lint and test gate for ts/ to CI | — | 2 | ready | — | — |
| phase-sch-05 | Add the committed-output drift test for the overview page | — | 2 | ready | — | — |
```

Three of six are `ready` — the three declaring no prerequisites — and two of them show `Conflicts: —`
even against this phase's own live claim. That is the widest genuine concurrency this batch has
planned.

`uv run pytest`

```
580 passed, 2 warnings
```

### The two repository checks that reshaped the plan

**`G36` — delivered.**

```
$ ls schemas/workbench-layout.schema.json
schemas/workbench-layout.schema.json

$ uv run pytest test/test_workbench_layout_schema.py -q
21 passed, 2 warnings
```

**`G33`'s drift — closed. Its other two claims — not.**

```
$ grep -in "create table" sql/001_schema.sql
81:CREATE TABLE interactions (   94:CREATE TABLE decisions (
112:CREATE TABLE waiting_on (   128:CREATE TABLE development_events (

$ grep -in "interaction\|decision\|waiting\|development_event" tools/rebuild_db.py
54: "development_events",  55: "waiting_on",  56: "decisions",  57: "interactions",

$ ls schemas/ | wc -l          →  20
$ grep -c "^CREATE TABLE" sql/001_schema.sql  →  16
```

```
$ ls _data/
commitments  ideas.jsonl  people  projects  tags.json  tasks  workbench
```

`000024` claims no DDL table, no data directory, and no `CLAUDE.md` mention for four entities.

- **DDL table — now false.** All four tables exist and `rebuild_db.py` loads all four. This is the
  claim that closed, and it is the one `000035`'s compiler was proposed to prevent.
- **Data directory — still true, and not a defect.** None of the four exists, as the `ls` above
  shows. `source_validation.py:170` is `if not source.is_dir(): continue`, and its comment permits
  exactly this: *"A directory that does not exist yet is not an error."* Missing and empty are
  handled identically.
- **`CLAUDE.md` mention — still true, and wider than stated.** Four schema files named against twenty
  present; seven tables against sixteen created.

The first version of this record said the directories "exist and are empty". They do not exist. See
`## Corrections` — the check I ran could not tell the two apart.

**`G34`'s gap — confirmed open.**

```
$ grep -n "npm\|ts/" .github/workflows/ci.yaml
40:      - run: npm ci
41:      - run: npm run build
```

**`G35`'s gap — confirmed open, and narrower than it reads.** `test/test_generate_overview.py` has
determinism tests only; `test/test_ideas.py:775` has the committed-output drift test the overview
lacks.

## Acceptance

- **`PLAN-035` carries no placeholder banner and states a chosen design.** Met. Banner removed,
  `status` `draft` → `active`, four numbered rulings plus the verification section above.
- **A requirement document exists for P8 and every row maps to at least one phase.** Met. `REQ-020`
  carries twelve rows; the mapping is total in both directions, checked against the backlog.
- **`G33` commits to `000024` or `000035` before sizing either.** Met. Ruled `000024`, in design
  decision 1, with the reason stated: `000035`'s motivation was the drift `000024` found, and that
  drift closed without a compiler. `phase-sch-02` decides `000035` later against what the new check
  actually catches, and `R04` forbids deciding from the proposal's own persuasiveness.
- **`G36` is recorded as already delivered and gets no implementation phase.** Met. No `phase-sch-*`
  covers `000098`; the plan records the schema file and the 21 passing tests as evidence rather than
  asserting delivery; `R12` makes it checkable.
- **`phase-prog-10` is removed from `next_up` in the same change that completes it.** Met, in the
  same commit that registers the track.

## Backlog

`phase-prog-10` is `status: complete`, `agent: agent-night`,
`session: doc-session-schema-consistency-testing-plan`. Completion evidence is `PLAN-035`, `REQ-020`,
`docs/09-backlog/README.md` and this record. Written under the owner's advance authority for this
batch, after the read-only independent review below confirmed all four conditions.

Six phases added under `phase-sch-*`: five `queued`, one `deferred` with a gate. None claimed.

## Review

A fresh non-fork sub-agent with read-only tools reviewed `dev...agent/phase-prog-10`, told explicitly
that earlier phases in this batch had found stale premises and that its highest-value job was
checking whether *this* phase's "already fixed" findings were right **in both directions** — because
work wrongly declared done would be dropped. That framing found the error below.

```
$ uv run python -m src.governance
Governance OK: 27 systems, 243 documents, 25 memories, 248 backlog phases
EXIT:0

$ uv run pytest          →  580 passed
$ ruff check             →  all checks passed
$ mypy src/              →  no issues
$ --catalog vs committed →  zero diff, exit 0
```

**All four conditions Met.** Coverage checked in both directions against `backlog.yaml` and `REQ-020`
directly. `G36` re-verified by running the tests: "The 21 tests are substantive (schema validation,
W06 eligibility invariants, malformed-input rejection), not vacuous." `000098` confirmed `discarded`
through `fold()`. The `next_up` diff: "exactly one removed line… and one region of pure additions. No
pre-existing phase was touched." And the explicitly requested check: `git diff` for `CLAUDE.md` and
`AGENTS.md` is empty.

**One major finding, and it was mine.**

> "`PLAN-035:69` and `REQ-020:44-45` both assert, in the section whose entire purpose is 'checked
> against the repository, not restated from the idea': *'No data directory — now false, and never an
> error. All four exist and are empty'*… None of `_data/interactions`, `_data/decisions`,
> `_data/waiting-on`, `_data/development-events` exist on disk — not 'exist and are empty,' they are
> simply absent. This is exactly idea `000024`'s original claim, which the plan and requirement both
> declare 'now false.' It is not false; it is still literally true today."

And the part that matters most:

> "Neither the session record nor the diff shows a command that actually verified this claim… unlike
> the DDL-table and loader claims, which were genuinely checked and are correct… it is a fabricated
> verification result sitting in a governance-tracked requirement document whose stated authority is
> 'checked, not assumed'."

It also spotted that `R01` was positioned to let the error propagate: the row "only mentions the
DDL/loader half — it never asks `phase-sch-01` to re-verify the data-directory claim". **All of it
corrected** — see `## Corrections`, including `R01`'s widening and the command shape that caused it.

The reviewer judged the functional impact near-zero, since `source_validation.py` treats missing and
empty identically, and confirmed the `G33` ruling survives: "defensible on the evidence, not pretext
— the DDL/loader drift genuinely closed without the compiler, `phase-sch-02` is explicitly gated…
rather than skipped, and `R04`/`R05` set an evidentiary bar for the eventual decision rather than
presupposing 'decline.'"

**Everything else held**, each checked rather than accepted: the four counts (20 schema files, 16
tables, against `CLAUDE.md`'s 4 and 7), `000026`'s CI gap, `000106`'s determinism-versus-drift
distinction — "real, not a quibble" — the `source_validation.py` comment verbatim, all six phases
carrying acceptance and verification, `phase-sch-06`'s `resume_when` and `blocked_reason`, README
registration, and `backlog.yaml` parsing at 248 items with no anchors. It also confirmed
`000035`, `000052`, `000001`, `000026`, `000057` and `000106` all remain `triaged` — "none were
incorrectly treated as resolved.

## Decisions

**`G33` commits to `000024`, and `000035` waits for evidence.** This is the scope's central question.
`000035` proposes a contract compiler generating models, types, OpenAPI fragments and fixture
factories from JSON Schema. Its stated motivation is `000024`'s drift — which closed through ordinary
work while nobody was watching, by someone adding the tables and loaders. Committing to the compiler
now would be building a machine to prevent a class of defect whose only recorded instance has already
healed. So the small mechanism ships first — a check comparing `CLAUDE.md` against `schemas/` and the
DDL — and `phase-sch-02` rules on the compiler against what that check catches.

The asymmetry is the reason: a compiler nobody needed sits between every future schema change and its
consumers and is hard to remove; a check that turns out to be insufficient is cheap to supersede.

**What remains of `000024` is owner-executed.** The surviving gap is in `CLAUDE.md`, which no agent
may edit. `phase-sch-01` writes proposed replacement text and stops, and `R02` makes the *absence* of
a `CLAUDE.md` edit in the diff a checkable condition — so an agent that helpfully applies it fails a
row rather than quietly breaking a rule. Second owner-executed phase this batch, after
`phase-conc-09`.

**`000001` gets a `deferred` phase rather than being folded into the testing standard.** Folding it
would bury three specific decisions — where fixtures live, generated versus hand-authored, governed
artifact versus test asset — inside a document about philosophy. The same `deferred` plus
`resume_when` mechanism `P7` used earlier tonight.

**`G35`'s test mirrors the existing pattern rather than inventing one.** The repository already has
one shape for "committed artifact matches a regeneration"; a second shape for the same assertion is a
maintenance cost with no benefit.

## Corrections

**I asserted a verification result I never produced, in a document whose stated authority is that
its claims are checked.** `PLAN-035` and `REQ-020` both said the four entity directories "exist and
are empty". They do not exist at all:

```
$ ls _data/
commitments  ideas.jsonl  people  projects  tags.json  tasks  workbench
```

The cause is that my check could not fail. I ran:

```
for d in interactions decisions waiting-on development-events; do
  printf "%-20s %s\n" "$d" "$(ls _data/$d 2>/dev/null | wc -l || echo MISSING)"
done
```

Every line printed `0`, and I read that as "exists, empty". But `ls` wrote its error to `/dev/null`
and `wc -l` counted zero lines of empty input, so `0` means *absent or empty* and distinguishes
neither. The `|| echo MISSING` never fired because `wc` succeeded. This is the anti-pattern this
repository already has a procedure for by name —
`brain/procedures/a-check-that-cannot-fail-is-not-a-check.md` — and I wrote the claim into a governed
requirement anyway.

Found by the independent review, not by me. Corrected in three places: `PLAN-035`'s claim-by-claim
breakdown now records the directories as absent and explains why that is designed rather than
drifted; `REQ-020`'s narrative says the same; and `R01` now requires the directory check to
*distinguish absent from empty*, naming the exact command shape that fails to. `phase-sch-01`'s
scope carries the correction too, so the error cannot propagate into its record.

The ruling this sat under is unaffected. `G33`'s commitment to `000024` rests on the DDL and loader
drift having closed, which was genuinely checked and is correct. What changed is the count: one of
`000024`'s three claims closed, one is designed behaviour, one is a real gap — not "half done".

**I miscounted the schema files before measuring them.** The requirement first said `schemas/` holds
nineteen definitions; `ls schemas/ | wc -l` returns twenty. Corrected before the plan was written.
The figure is load-bearing — it is part of the evidence that `CLAUDE.md`'s drift is wider than
`000024` counted — so an approximate number would have weakened the argument it supports.

## Unresolved

**Where `R03`'s check should live.** It could be a pytest, a governance check, or a pre-commit hook.
Options: decide here, or leave it to the phase. **Left it to the phase**, and pointed
`phase-sch-01`'s references at `phase-conc-08`, which writes the enforcement-placement rule this
programme's check is exactly the kind of case for. If `P3` has landed first, the rule decides; if
not, the phase decides and the rule should later be checked against it.

**Whether `phase-sch-02` can be claimed meaningfully at all.** Its acceptance requires weighing drift
instances the check has caught, and a check that has just shipped has caught none. Options: gate it
on a duration, or leave it `queued` with a warning. **Left it `queued`** with a `next_action` saying
not to claim it until the check has run long enough to have caught something or demonstrably nothing.
A duration gate would have been inventing a number, which is the defect `P6` found in its own gate.

**Whether `CLAUDE.md`'s wider drift belongs to this phase at all.** `000024` counts four entities; the
real divergence spans nine tables and sixteen schema files. Options: scope `phase-sch-01` to the four,
or to the whole file. **Scoped it to the whole file**, because a correction that fixes four of nine
omissions leaves the document wrong in a way the new check would immediately flag.

## Left undone

**All six phases.** This phase finalizes a plan and builds nothing.

**The `CLAUDE.md` correction is not written.** `phase-sch-01` writes it; this phase only establishes
that it is needed and how wide it is. Nothing here edits `CLAUDE.md`, and the diff shows none.

**`000035`'s compiler is neither built nor declined**, deliberately. The ruling is that the decision
is premature, not that the answer is no.
