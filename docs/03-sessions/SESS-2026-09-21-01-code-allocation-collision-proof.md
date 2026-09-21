---
schema_version: 1
id: doc-session-code-allocation-collision-proof
code: SESS-2026-09-21-01
title: Collision-proof document-code allocation, and the phase-lit-07 close review that preceded it
kind: session
status: active
owner: repository-owner
created: '2026-09-21'
updated: '2026-09-21'
systems:
- sys-governance
depends_on:
- doc-concurrency-git-safety
- doc-concurrency-git-safety-requirements
---

# Collision-proof document-code allocation, and the phase-lit-07 close review that preceded it

## Phase

`phase-conc-03` — Make document-code allocation collision-proof across concurrent sessions.
Claimed as `agent-conc` at `54d1e82`, worked on `agent/phase-conc-03` in
`../d-system-worktrees/phase-conc-03`.

This session did not start on this phase. It was dispatched to run `phase-lrr-01` (deterministic
extraction of the literature-review corpus), which reported a conflict against `phase-lit-07` and
could not be claimed. Resolving that conflict became the first half of the session, at the owner's
direction, and is recorded below because it produced committed work on `dev` and three new ideas.

## What this session did, in order

1. **Stopped on the `phase-lrr-01` conflict rather than working around it.** The dispatch said to
   stop if `phase-lrr-01` reported a conflict against `phase-lit-07`; it did, both declaring
   `sys-research`.
2. **Established why `phase-lit-07` was still `active`.** The owner believed they had run
   `/session-close` against it. They had run one — `5a2a609`, against `phase-tax-02`. No completion
   commit for `phase-lit-07` exists, and `SESS-2026-09-20-02` says in its own `## Backlog` section
   that no phase was marked complete in that session.
3. **Ran the independent close review `GOV-003` requires**, at the owner's direction, and recorded
   it verbatim in `SESS-2026-09-20-02`'s `## Review` section (`f637b7b`). It found acceptance
   condition 1 does not hold. The phase stayed `active`.
4. **Captured three corpus-integrity defects as ideas** (`cb81f51`): `000295`, `000296`, `000297`.
5. **Claimed `phase-conc-03`** (`54d1e82`) — second in `next_up`, Conflicts column empty — and built
   it (`e05b82b`).

## The `phase-lit-07` close review

Dispatched as a fresh non-fork subagent with the phase's `scope`, `acceptance` and `verification`
pasted in full, the four commits constituting the phase's diff, and the session record's path. Its
verdict: **not safe to mark complete.**

Acceptance condition 2 holds as amended, and the review specifically hunted for an agent widening
its own bar and cleared it — the ruling was recorded at `28f4d56`, *before* the phase was claimed at
`db15eca`, and the one phrase the amendment adds beyond the ruling ("as they stand at the gate") is
a tightening rather than a relaxation.

Acceptance condition 1 does not hold, on three counts. Because a review that overturns a close
deserves the same scepticism as the close it overturns, all four of the following were re-checked
directly by the coordinator before being recorded, and all four reproduced:

| Claim | Check | Result |
|---|---|---|
| `06`'s H4 carries one status token, not a split | line 793 → `status: LIKELY_ALREADY_KNOWN` | `09` and `12` both assert otherwise |
| `12` quotes a sentence from `06` that is not there | `grep -c 'graph-topological reading stays' 06...` → `0` | present at `12:19` as a quotation |
| `13` missing the two sources `988dcea` added to `07` | both → `0` in `13`, `1` in `07` | scope item 3 requires their promotion |
| Six deliverables state "49 rows, 24 flagged" | matrix measures **67 rows, 30 flagged** | stale population |

The last is the same defect class the 2026-09-14 `LIT-07 A` review graded **blocking** at "34 vs
49". It recurred at 49 vs 67 and was not caught.

One finding cuts against the record rather than for it: the review could reproduce neither figure in
the record's own duplicate-rate finding, measuring 386 distinct against the printed 402/387 and the
earlier 392. That is a fourth defensible value for one denominator. It strengthens `000289` rather
than undermining it, and it is now `000295`.

**The owner's decision** was a reconciliation pass over `09`–`13` in a future session rather than an
amendment to condition 1. `phase-lit-07` stays `active` under `agent-lit`, holding `sys-research`,
with the gap named in its `next_action`. The `agent` field was deliberately kept: `AGENTS.md`'s
completion step 5 names it the record of who did the work, and `status` is what holds the lock.

The owner also settled the placement question `SESS-2026-09-20-02` left open — the 2026-09-20
closing ruling stays as its own dated section in `PROMPT-031`, not folded into the numbered check-in
list.

## `phase-conc-03` — the design question, answered empirically

The phase's `next_action` named one question as deciding the whole phase: whether `codes.yaml` on
`dev` can serve as the reservation point, or whether a pre-merge reservation needs somewhere else to
live.

**It cannot, and the reason is mechanical rather than stylistic.**

```
$ git -C /code/d-system-worktrees/phase-conc-03 switch dev
fatal: 'dev' is already used by worktree at '/code/d-system'
```

A worktree cannot check out `dev` at all, so it cannot commit a reservation there even if the
protocol allowed it — and `AGENTS.md` does not. Reading `git show dev:docs/08-governance/codes.yaml`
returns committed state, which is the defect rather than a fix for it. `_tmpagent/` is tracked and
fails the same way. Every tracked location fails for one reason: `REQ-013` R05 requires the
reservation to be visible *before the first caller has merged*, and tracked state is by definition
not visible until it merges.

The one location every worktree of a repository already shares, with no commit and no merge:

```
$ git -C /code/d-system rev-parse --git-common-dir                     # primary
.git
$ git -C /code/d-system-worktrees/phase-conc-03 rev-parse --git-common-dir   # worktree
/code/d-system/.git
```

Reservations live there, untracked. That also scopes them correctly rather than as a compromise: a
reservation is a statement about work in flight on this machine, and it is meaningless to a fresh
clone.

Mutual exclusion is the kernel's. Each reservation is one file created with `O_CREAT | O_EXCL`, so
of two callers racing for one code exactly one create succeeds. No lock file, no ordering
assumption, nothing to repair after a crash mid-write.

## The defect, demonstrated before and after

Run against the live register with nothing committed, which is the concurrent-worktree case:

```
OLD behaviour (no reservations consulted) — two worktrees, nothing committed:
  worktree A -> SESS-2026-09-05-01
  worktree B -> SESS-2026-09-05-01
  COLLIDE: True

NEW behaviour (reservation from A visible to B):
  worktree A -> SESS-2026-09-05-01
  worktree B -> SESS-2026-09-05-02
  COLLIDE: False
```

And end to end through the CLI, twice in a row with nothing committed between:

```
$ uv run python -m src.governance --next-code session
SESS-2026-09-21-01
$ uv run python -m src.governance --next-code session
SESS-2026-09-21-02
```

Before this change both runs returned `SESS-2026-09-21-01`. This record's own code was allocated by
the new mechanism.

## Verification

### `uv run python -m src.governance`

```
Governance OK: 35 systems, 302 documents, 28 memories, 292 backlog phases
```

Exit code 0.

### `uv run pytest test/test_codes.py`

```
57 passed, 2 warnings in 2.50s
```

48 before this session; nine added. The full suite was also run as a regression check and is green
at `647 passed, 2 warnings in 51.02s`, against 638 on `dev`.

### `uv run python tools/check_no_private_content.py` with the changes staged

**This run did not check content, and is reported as such rather than as a pass.**

```
note: _private/portfolio/ not found — content check skipped (path check still ran; this is expected in CI / a fresh clone)
check_no_private_content: OK (748 tracked files, 0 identifiers checked)
```

`0 identifiers checked` is the gate passing by not looking, which is the failure mode `AGENTS.md`
names in writing. It is structural here: `_private/` is gitignored and never travels to a worktree.
The path half did run across all 748 tracked files. The content half must be re-run from the primary
checkout at integration, where `_private/portfolio/` exists — the two runs on `dev` earlier in this
session both reported `31 identifiers checked`, so the mechanism is working; it simply cannot see
this branch's files from there until they merge.

This diff adds Python source, a test module and one governance document, and names no client,
person or engagement.

## Acceptance

1. **`REQ-013` R05 holds: the same kind allocated from two worktrees before either commits yields
   two different codes — Met.** `test_two_worktrees_allocating_the_same_kind_get_different_codes`
   builds a real git repository with two real linked worktrees, allocates `session` from each with
   nothing committed, and asserts `SESS-2026-09-05-01` and `SESS-2026-09-05-02`.
2. **The reservation is observable to the second caller pre-merge, demonstrated by a test rather
   than by inspection — Met.** `test_two_worktrees_share_one_reservation_store` asserts both
   worktrees resolve the same store, that a reservation taken in the first is in `active()` as read
   from the second, and that the second's attempt to take the same code returns `False`. Nothing is
   committed in either worktree at any point.
3. **`GOV-005` describes the mechanism actually in force, with no surviving instruction to work
   around it by hand — Met for `GOV-005`; see *Left undone* for `AGENTS.md`.** The *Concurrent
   agents* section was rewritten: the workaround is retired explicitly, and the two unrelated things
   now called a reservation are separated in a table, because confusing the committed `codes.yaml`
   register reservation with the ephemeral pre-merge one would waste an afternoon.

## Decisions

- **Reservations expire.** An agent that allocates and never writes would otherwise hold a hole in
  the series forever. Pruning is automatic on every allocation and covers two cases: satisfied (the
  code now appears on a scanned document) and expired (a fortnight). The wall clock decides nothing
  about a code's value, only when an abandoned hole is reclaimed.
- **`--release-code` was added** beyond the phase's literal scope, as the explicit counterpart to
  automatic pruning. Without it, the only way to release a deliberately abandoned code is to wait
  out the TTL or delete a file by hand — which would be a new convention protecting against a
  mechanism gap, the exact thing this phase exists to remove.
- **`next_code()` stays pure**, taking `reserved` as an argument. The impurity lives in the caller
  (`allocate()` in `__main__.py`), which keeps the arithmetic straightforward to test and puts the
  compute-and-take pair in one place, since they must be one operation from a peer's point of view.
- **The stale `main` reference in the rewritten section was corrected to `dev`** as part of
  rewriting it. This does not discharge `REQ-013` R10, which is corpus-wide and belongs to
  `phase-conc-06`; the *Permanence* section of the same file still says `main` and was left alone as
  outside this phase's concern.

## Corrections

- I had `/session-close` recorded in my own standing notes as owner-only. `GOV-003`'s *Coordinator
  completion replaces owner-invoked /session-close, repository-wide* superseded that on 2026-09-16.
  The note was corrected outside the repository. Citing a superseded rule to refuse work is its own
  failure, and the corrected note now says to re-read the governing document before declining on
  governance grounds.

## Left undone

- **`AGENTS.md` still carries the retired workaround** — "Reserve your code in `codes.yaml` alongside
  your backlog claim to avoid the race entirely", in *Concurrent agents: resolve collisions*. It is
  now redundant rather than wrong, and following it is harmless. It was **not** edited: `AGENTS.md`
  and `CLAUDE.md` may not be modified without the owner's explicit approval for that specific
  change, and this phase's declared deliverables do not include it. Proposed replacement, for the
  owner to accept or reject:

  > **A duplicate-code error means you and a peer took the same number.** Codes are free before
  > merge and permanent after, so the agent integrating second renumbers: allocate again, rename the
  > file, and update any reference you added. `--next-code` now reserves the code it hands you
  > against every worktree on this machine, so this should only arise between agents on different
  > machines — see [GOV-005](docs/08-governance/GOV-005-document-codes.md).

- **`ruff` is red on `dev` and remains red**, with 10 pre-existing errors including
  `src/governance/__main__.py:433` E501 inside this phase's deliverable path. Not fixed: it is
  unrelated to this concern, is not in this phase's `verification` list, and fixing ten lint errors
  would widen a narrow diff. Every file this session touched passes `ruff` and `mypy` cleanly.

- **The content half of the private-content gate has not run against this branch.** See
  *Verification*.

- **`phase-lrr-01`, the phase this session was dispatched to run, was never started.** It remains
  blocked behind `phase-lit-07`'s `sys-research` lock.

## Unresolved

- `phase-lit-07` needs a reconciliation pass over `09`–`13` before it can close. Experiment 2 in
  `12_experiment_proposals.md` needs an owner decision rather than a patch: its subject, the H4
  general/graph-topological split, no longer exists.
- Ideas `000295`, `000296` and `000297` are open, linked onto `000296` as the shared anchor.
- Reservations are machine-local by design, so two agents on **different machines** can still
  collide. `GOV-005` names this as one of the two cases renumbering still covers.

## Backlog

`phase-conc-03` stays `status: active` under `agent-conc`. **No phase was marked complete in this
session.** `GOV-003`'s coordinator-completion rule requires an independent adversarial review of the
diff against acceptance plus the owner's approval to integrate; neither has happened for this phase,
and this session's own first half is the argument for not skipping either.

`next_action`: All three acceptance conditions are met and both verification commands are green.
Ready for an independent review of `git diff dev..agent/phase-conc-03` and the owner's integration
decision. The `AGENTS.md` wording in *Left undone* needs the owner's yes or no before anyone edits
that file.
