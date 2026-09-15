---
schema_version: 1
id: doc-session-workbench-features-defects-plan
code: SESS-2026-09-14-10
title: Finalize the workbench features and defects plan (P11)
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-ui
depends_on:
- doc-workbench-features-defects
- doc-workbench-features-defects-requirements
---

# Finalize the workbench features and defects plan (P11)

## Phase

`phase-prog-02` — Finalize the workbench features and defects plan (P11): turn the placeholder
[PLAN-027](../01-plans/PLAN-027-workbench-features-defects.md) into a real requirement, design and
implementation phases.

**Taken out of `next_up` order on the owner's explicit ruling, not on a queue read.** `next_up` read
`phase-part-02`, `phase-prog-01`, `phase-port-02`, `phase-ses-01`, `phase-prog-02`; the first four
were deliberately jumped on the owner's instruction, and the queue was not reordered to make the jump
look routine.

## Verification

Both entries in the phase's `verification` list, run in the worktree at close, after the rebase onto
`dev`.

`uv run python -m src.governance` — must exit 0:

```
Governance OK: 20 systems, 224 documents, 24 memories, 180 backlog phases
EXIT=0
```

`uv run python -m src.governance --ready` — must show the new phases:

```
180 phases; every phase has a one-session budget.
active: 2, complete: 69, deferred: 5, ready: 35, waiting: 69
| phase-wbf-01 | Open a viewer tab's file in a new browser tab on double-click | — | 2 | ready | — | phase-prog-02 |
| phase-wbf-07 | Decide the external terminal interaction API | — | 2 | ready | — | — |
| phase-wbf-09 | Terminal route defects: cap race, shell override, close reason | — | 2 | ready | — | — |
| phase-wbf-02 | Show a last-modified badge on the HTML Viewer header | — | 3 | ready | — | phase-prog-02 |
| phase-wbf-10 | Silence the flag-off workbench probes | — | 4 | ready | — | phase-prog-02 |
```

Five of the ten are `ready`; `phase-wbf-03` through `-06` and `-08` are `waiting` on `phase-arch-01`
or on their own group's ADR, which is the intended shape. Phase count moved 169 → 180 (ten from this
session, one from a peer merged during it).

Not in the phase's list, but run because the work touches governed documents and the idea log:

```
$ uv run pytest
580 passed, 2 warnings
```

It failed twice before reaching that, and both are recorded rather than retried into silence:

```
FAILED test/test_ideas.py::test_the_committed_markdown_matches_regenerated_output
1 failed, 579 passed, 2 warnings
```
— appending idea events left `docs/00-working/ideas.md` stale; `tools/generate_ideas_md.py` fixed it.

```
FAILED test/test_codes.py::test_committed_catalog_matches_regenerated_output
FAILED test/test_codes.py::test_catalog_flag_writes_committed_file
2 failed, 578 passed, 2 warnings
```
— a peer's phase merged during the session, so the rebase left the committed catalog stale;
`--catalog` fixed it.

## Acceptance

1. **PLAN-027 carries no placeholder banner and states a chosen design — Met.** Zero matches for the
   banner text or "Do not build from this document" in the file; one `## The chosen design` section,
   carrying six numbered decisions.
2. **A requirement document exists for P11 and every row maps to at least one phase — Met.**
   `REQ-012` carries 23 `R`-numbered rows; `PLAN-027`'s coverage table carries 23 rows naming
   phases, and all ten `phase-wbf-*` ids it names resolve to a defined phase in `backlog.yaml`.
   Every phase carries at least one row.
3. **G56 is recorded as already delivered and gets no implementation phase — Met.** `000099` and
   `000129` appear in `REQ-012`'s delivered table and in `PLAN-027`'s group table marked
   `[DELIVERED]`. In `backlog.yaml` they appear only in historical `phase-wb-*` result text and in
   `phase-arch-17`'s source note; no `phase-wbf-*` phase mentions either, and none implements G56.
4. **phase-prog-02 is removed from next_up in the same change that completes it — Met.** `next_up`
   no longer lists it; the removal is in commit `5680d2a`, the same commit that finalized the plan,
   the requirement and the ten phases.

## Backlog

`phase-prog-02` — status at checkpoint time: `active`. All four acceptance conditions `Met`, which
is what makes this record eligible for `session-close`'s review; the checkpoint itself never writes
`complete`.

`next_up` pruned of `phase-prog-02`. Ten `phase-wbf-*` phases added, all `queued`; none was added to
`next_up`, matching how `PLAN-028`'s `phase-arch-*` phases were registered.

## Unresolved

**The four delivered ideas have no honest terminal status, and are held in place rather than
mis-stated.** `000110`, `000118` and `000119` remain `triaged`; `000232` remains `open`. This is the
one piece of the session's work that is deliberately not finished, and it is unresolved in the
lifecycle, not in this phase — the phase's acceptance does not require a status move. Tracked as
`000236` and by the standing note in `PLAN-027`. See *The idea-status gap* below.

## What was produced

- **[REQ-012](../06-requirements/REQ-012-workbench-features-defects.md)** — 23 observable
  requirement rows with verification methods, plus a table of the six already-delivered ideas that
  deliberately carry no rows.
- **[PLAN-027](../01-plans/PLAN-027-workbench-features-defects.md)** — placeholder banner removed,
  six design decisions stated, ten phases, a sizing account against the partition, and a full
  requirement-coverage map.
- **Ten `phase-wbf-*` phases** in `docs/09-backlog/backlog.yaml`, with the prefix registered in
  [the backlog index](../09-backlog/README.md).
- **Idea records** — finding annotations on `000119`, `000110`, `000118` and `000232`; a new idea
  `000236`.
- `phase-prog-02` removed from `next_up`.

## What shipped before the planning, and how it was handled

A demo-driven session delivered four `G48` ideas on 2026-09-14, hours before this phase ran. The
first job was to record that rather than plan around it.

Every claim was **verified against the code, not against the note that reported it**:

| Claim | Verified |
|---|---|
| `COMPATIBLE_EXTENSIONS` holds `.html`, `.htm`, `.svg`, `.md` and six image formats | `ts/src/stage/HtmlViewerRegion.tsx:25-36` — confirmed, all ten entries |
| `FileBrowserRegion.tsx` imports the same constant | Line 4 imports it; line 500 reads it for `viewerCompatible` — confirmed, no second copy |
| `000119`'s render location is implemented route-side | `ts/vite.config.ts:6` imports `marked`; rendering happens in `serveRepositoryFiles` at the `/workbench-file/` route — confirmed, ruling consumed, not re-litigated |
| `GET /api/v1/workbench/search` was already extension-agnostic | `src/api/routes/workbench.py:439` takes `ext` from the caller — confirmed, no change was needed |

The four remaining defect claims were also checked before requirement rows were written about them,
because a row describing already-fixed code is worse than no row:

- `000095` and `000137` both confirmed live, and **within twenty-six lines of each other** — the cap
  check at `src/api/routes/demo_terminal.py:287`, the pre-accept close at 288, the accept at 313.
  That measurement is why they share `phase-wbf-09` rather than getting a phase each.
- `000100` confirmed — `InjectionDropdowns.tsx` fetches unconditionally, while `TerminalRegion.tsx:405`
  already probes `/api/v1/demo/stage/terminal-enabled`. The fix reuses an existing probe.

## Decisions the owner made in this session

1. **`000102` (freshness badge) keeps the partition's ruling and gets its own phase.** The partition
   had flagged this as its own weakest call — "ruled on a principle, not a repository check" — and
   invited reversal. The owner affirmed it, and declined folding it into `phase-wbf-01`.
2. **The prefix is `phase-wbf-*`.**
3. **The four delivered ideas keep their current status**, recorded in place with annotations. See
   below.
4. **Phases declare `sys-ui` as it exists today**, with no edge to `phase-arch-00`. Declining the
   accompanying revisit note was also the owner's call, so no phase carries one.

## The idea-status gap, and the standing note it left

`000110`, `000118` and `000119` remain `triaged`; `000232` remains `open`. This is deliberate and is
the one piece of this phase's work that is **not finished**.

The lifecycle has no honest terminal state for an idea that was built. `promoted` requires
`promoted_to` naming the governed documents produced, and these produced none. `discarded` means
*rejected*. The `G56` precedent (`000099`, `000129`) used `discarded` anyway, with an annotation
reading *"Verified resolved; discarded by owner ruling 2026-09-13"* doing the work the status could
not — a record contradicting its own status field in prose, which is the evidence that the status is
wrong rather than merely awkward.

The owner ruled: use a `resolved` status if one exists, otherwise record in place and hold with a
note to pick the work up later. `schemas/idea.schema.json`'s enum is
`open | triaged | reviewing | promoted | discarded`; none exists. So the four are annotated in place,
`PLAN-027` carries the standing note, and the gap is captured as **`000236` (a terminal `resolved`
idea status, distinct from promoted and discarded)**, linked to all four plus `000129`. It belongs to
`P1` ([PLAN-029](../01-plans/PLAN-029-idea-graph-lifecycle.md)) by subject matter.

## The two P10 rulings, honoured

- **`000233` (panel maximize) gets no `P11` phase.** It is `phase-arch-17` in `P10`'s `G43`. No
  `REQ-012` row covers it, and `PLAN-027` design decision 2 says so explicitly, because the idea was
  raised on the HTML Viewer and a future reader will look for it there.
- **Four phases declare `depends_on: [phase-arch-01]`** — `phase-wbf-03`, `-04`, `-05` and `-06`,
  each because it names or rewrites a slot, panel or layout identifier. Six carry no edge. The edge
  is on `phase-arch-01`, the settled vocabulary, never `phase-arch-02`, the migration.

## Sizing: the delta and its reason

Partition-time sizing was **8–10 phases excluding `G56`**. This plan lands **10** — the top of the
range, against a corpus six ideas smaller.

That is stated rather than smoothed over. The delivery removed work from `G48` without removing a
phase from it: `G48` was sized at 2 phases for 5 ideas, the render half shipped, and its two
survivors (`000109`, `000102`) still need 2 phases because they are unrelated surfaces and the owner
declined folding them. Consolidating `G52`/`G53`/`G55` into one phase and `G54` into another takes 2
back; `G49` and `G51` landing at the top of their ranges because their ADRs are separate phases adds
2. The movements nearly cancel.

**The delivery shrank the work without shrinking the phase count.** A coordinator should expect
`phase-wbf-01`, `-02` and `-10` to be short sessions, not expect fewer of them.


## What was found wrong in the source material

1. **The placeholder's `000232` note was stale on its own terms.** `PLAN-027` listed `000232`'s
   image-presentation question as one for the planning session to settle. It was answered in the
   build instead — images are wrapped in a fitted centred document (`2e35ae7`), with the same answer
   for all six formats, as the idea required. Nothing remained to settle.

2. **The partition's `G48` sizing cannot survive its own delivery.** Two phases for five ideas
   assumed the five could be grouped; the two survivors cannot be. Recorded in `PLAN-027`'s sizing
   section rather than absorbed silently.

3. **The idea lifecycle cannot record a delivered idea** — `000236`, above. Found by trying to
   satisfy this phase's own third acceptance condition.

4. **Markdown rendering and image wrapping live only in the Vite dev-server plugin.** There is no
   FastAPI equivalent of `/workbench-file/` — `serveRepositoryFiles` in `ts/vite.config.ts` is the
   only implementation. This is pre-existing architecture, not something the 2026-09-14 delivery
   introduced, and the workbench is run through `npm run dev` today, so it is correct as it stands.
   Noted because a future reader tracing "the workbench file server" will look in `src/api/routes/`
   and not find it. No requirement row and no phase; raising it as work would be scope this phase
   was not given.

## Notes for whoever runs P11

- **`phase-wbf-07` and `phase-wbf-09` are ready now and collide with nothing** — `phase-wbf-07`
  declares `sys-contracts`, `phase-wbf-09` declares `sys-api` and `sys-demo-stage`. They are the two
  to start with if `P10` is holding `sys-ui`.
- **Seven of the ten declare `sys-ui`** and will serialise against each other and against most of
  `P10` until `phase-arch-00` lands. That is the lock table as it exists, declared honestly, per the
  owner's ruling.
- **`phase-arch-02` may rename `HtmlViewerRegion.tsx`**, which `phase-wbf-01` and `phase-wbf-02`
  edit. That is a file-level sequencing question for a coordinator, not a dependency — `PLAN-028`'s
  rule puts the edge on `phase-arch-01` only, and blocking two small viewer features behind the
  largest rename in the sibling programme would be the wrong trade.
- **`phase-wbf-07` should read `000087` through `fold()`**, not through the partition's summary. One
  analyst lost the idea entirely, so the partition's evidence on it is thinner than on the rest. Its
  `next_action` says so.

## Concurrency

No `_tmpagent/` claims were opened. `_tmpagent/viewer-render-location-ruling.md` was deliberately
**not** claimed: its ruling is consumed, so the code was read instead of the file.

A peer committed to `dev` during orientation (`7e506d0`, splitting `phase-arch-00` and adding
`phase-arch-18`). The claim commit was made on top of it and disturbed nothing.
