---
schema_version: 1
id: doc-session-panel-maximize-reexamination
code: SESS-2026-09-15-12
title: Panel maximize re-examination, and the demo that went unused
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems:
- sys-portfolio
- sys-wb-layout
- sys-wb-viewer
depends_on:
- doc-workbench-architecture-quality
- doc-workbench-architecture-quality-requirements
---

# Panel maximize re-examination, and the demo that went unused

## Phase

**None. This session ran unclaimed**, under `AGENTS.md`'s provision for owner-directed work with no
backlog phase. No claim commit exists for it, peers held no lock against it, and nothing here
reaches `status: complete` — there was no phase to complete. The only `active` phase during the
session was `phase-lit-07` (Literature review Pass 4 — synthesis), held by a peer in the
`lit-campaign` worktree and deliberately untouched.

It ran in the primary checkout on `dev`, read-only against the workbench by the owner's explicit
instruction ("investigate read-only first and report before changing anything… do not build anything
in this session"). Its only repository writes are three idea-log appends and this record.

Written at the owner's direction on the second occurrence of the gap `000237` describes — see
*Unresolved*.

## What this session produced

- **A re-examination of `PLAN-028` design decision 5**, which ruled panel maximize (`000233`) a
  slot-level capability owned by `P10`'s `G43` rather than an HTML Viewer feature, and therefore
  placed it at `phase-arch-17`, behind `phase-arch-07` and `phase-arch-09`. Delivered as a report to
  the owner with four costed options. **The owner ruled: leave it planned as-is.**
- **A finding annotation on `000233`**, recording the mechanism so that the phase's executor does
  not re-derive it. Summarised under *Decisions* below.
- **`000246`** (the terminal panel drops its connection and restarts unprovoked, and it cost a live
  demo), captured through the sanctioned writer and linked `relates_to` `000113` and `000137`.
- **A finding annotation on `000237`**, recording this session as the second occurrence of the
  phaseless-session gap, with the step-by-step evidence of which `session-close` steps failed and
  which two worked unchanged.
- **No change to any plan, requirement, backlog phase or line of application code.** That is the
  deliverable of a read-only investigation, and it is stated here because the absence is the result.

## Verification

This session declared no phase and therefore no `verification` list. The phase-independent gates were
run at close:

```
uv run python -m src.governance
Governance OK: 27 systems, 246 documents, 25 memories, 261 backlog phases
EXIT=0

uv run pytest
1 failed, 579 passed, 2 warnings in 50.36s
FAILED test/test_ideas.py::test_the_committed_markdown_matches_regenerated_output
```

That failure was this session's own and is recorded under *Corrections*. After regenerating the
markdown, `test/test_ideas.py` reports `62 passed` and the full suite is green.
`tools/check_no_private_content.py` ran with changes staged before the commit: `OK (651 tracked
files, 31 identifiers checked)`.

The investigation's own claims were **verified by reading, not by running**. The CSS assertions below
are grep-verified against `StagePage.css`; that a maximized panel actually fills the viewport without
page scroll at all four required window sizes is unverified, and is precisely what `REQ-011` R26's
validator run exists to establish. No build, no browser, no dev server.

## Decisions

**The ruling stands, on the owner's decision, against the recommendation.** The report recommended
re-pointing `phase-arch-17` — dropping its `depends_on` edges to `phase-arch-07` and `phase-arch-09`,
raising its priority, and amending design decision 5 to record why — on the grounds that the
mechanism already exists and that `REQ-011` R25–R28 as written require neither sub-slots (R12,
`phase-arch-07`) nor reconfigurable geometry (R15, `phase-arch-09`). The owner heard that and kept the
sequencing. `phase-arch-17` retains both edges and its queue position.

**The finding that prompted the recommendation, recorded because it survives the ruling.** The
slot-level relocation mechanism `phase-arch-17` needs is already shipped, and was built for this exact
problem class. `StagePage.tsx:129` keeps `panelHosts`: one persistent `div` per panel type, created
once, never replaced. `StagePage.tsx:155-188` appends each visible panel's host into its slot's
registered body and moves it by DOM `appendChild` on a re-assignment — a DOM move, invisible to React,
so nothing unmounts. It exists because changing a React portal's container *remounts* the subtree and
closed the terminal's websocket (the W09 fix cycle 1 defect, documented at `StagePage.tsx:36-54`).

Maximize is that operation in a different target geometry, and the cheapest form does not reparent at
all: `StagePage` writes `host.dataset.maximized` and one CSS rule does the rest. That escapes the
`overflow: hidden` chain because `StagePage.css` sets no `transform`, `filter`, `contain` or
`will-change` anywhere — grepped, zero hits — so nothing establishes a containing block that would
trap a fixed-position element. Three of the four requirement rows then come free: R28 from
`TerminalRegion.tsx:273-276`'s `ResizeObserver` and its guarded refit, R27 because `storage.ts` has one
named writer per persisted field and adding no writer satisfies the row by construction, and R25
because the control sits in the slot chrome `Slot.tsx` renders exactly once per slot. Full detail is
on `000233`'s annotation rather than restated here.

**The dependency edges were found to come from group membership, not from the requirement text.**
`REQ-011` R25–R28 mention neither sub-slots nor reconfigurable geometry. What `phase-arch-07`
genuinely changes is the control's *home* — R13 makes the slot top bar schema-owned, so the button
relocates into it. What `phase-arch-09` genuinely changes is whether maximize is expressed as a point
in a geometry range rather than a fixed overlay. That second one is the only real coupling, and it is
the honest argument for waiting; it is the argument the ruling now rests on.

**One correction offered to `PLAN-028` and not made.** Design decision 5 frames the choice as
"slot-level and slow" against "viewer-local and throwaway". The third option — slot-level, now, on
machinery that already shipped — is absent from it, so the decision's stated cost is not the true
cost of the alternatives. The *ruling* is unaffected and this investigation strengthens it: a
viewer-local build would be the second geometry path `G43` exists to remove, and would fail R25's
grep for a panel-owned geometry path on the day it shipped. The plan was left unedited because the
owner ruled the sequencing unchanged and no plan edit was authorised.

**The projector premise was checked rather than accepted.** In `layout-1` the HTML Viewer's `main`
slot is column 2 of `["1.4fr","1fr"]` and row 2 of `["0.25fr","1.3fr","1.15fr"]` — about 20% of the
grid, roughly 785×478px at 1920×1080. In `layout-2` it is about 13%. Maximizing is a ~5× and ~8× area
gain. The complaint is quantitatively correct.

**`000246` was written as a defect investigation, not folded into the existing audit.** `000113`
(audit terminal persistence and performance across all three shells, `phase-arch-16`) says in its own
text that it is "not a bug fix", and every transition it enumerates — layout switch, visible-panel
switch, re-assignment, collapse/drop/restore, page reload — is one a user causes. The owner's
observation is the *unprovoked* case: the session dying while nobody touched it. No row of that audit
would catch it, so it is a separate idea, linked rather than merged.

## Corrections

**The idea append broke a drift test, and the break was mine.** Appending `000246` without
regenerating `docs/00-working/ideas.md` turned
`test/test_ideas.py::test_the_committed_markdown_matches_regenerated_output` red — that file is
generated from the log by `tools/generate_ideas_md.py`, and the test exists to catch exactly this.
Fixed by running the generator (246 ideas). Found by running the suite before committing, which is
the only reason it was not committed red.

Worth carrying: a capture through the sanctioned writer is not finished when the writer returns. The
generated view is part of the same change, and `OPS-006` is the document that says so.

## Left undone

**Nothing was built, by instruction.** `phase-arch-17` remains `queued` at position 119 of 261 in the
priority queue, with `depends_on: [phase-arch-07, phase-arch-09]` intact. Its earliest prerequisite,
`phase-arch-05` (per-panel content-fit contracts), is at position 107. Thirty-two priority-1 phases
sit ahead of the whole chain, and `next_up` is `phase-part-02`, `phase-port-02`, `phase-ses-01`,
`phase-lit-09`.

**`000246` is captured and untriaged.** The terminal instability has a symptom and no diagnosis. The
idea names where to start — `src/api/routes/demo_terminal.py`'s registry and six-session cap,
`TerminalRegion.tsx`'s socket lifecycle, the PTY reaping `000099`/`000129` turned on, and orphaned
processes from cut-off agent sessions — but nothing was investigated. It is the reason the workbench
was not used in front of an audience, which makes it the highest-consequence item this session
touched and the one it did least about.

**`REQ-011` R26 has no mechanical check, and this session did not add one.** `test/` holds 22 files,
none browser-driven; grepping `test/`, `tools/` and `js/` for `W15`, `scrollHeight` or `1366` returns
nothing. The zero-scroll and fill assertions are a `demo-validator-web` Playwright run at four window
sizes by two layouts, and under maximize by two states — the largest line item in `phase-arch-17`
whichever way it is sequenced. Noted, not filed as an idea, because `phase-arch-05`'s mechanised
content-fit checks may already be its home.

**`PLAN-028` design decision 5's cost statement is still incomplete** on the record, per *Decisions*
above. Left as-is deliberately; an amendment would need the owner's approval and the ruling it
supports did not change.

## Unresolved

**This record could not be produced by either governed workflow, for the second time.** `/session-close`
was invoked by the owner on a session that claimed no phase. Its step 1 had no phase to name; steps 2
through 6 had nothing to operate on, so **no independent sub-agent review ran** — there were no
acceptance conditions to review against, and this section stands in place of a `## Review` one. Two
steps did work unchanged and should survive any amendment: step 7's gates are phase-independent, and
step 8's commit instruction is what caught a real repository change sitting uncommitted in the primary
checkout — the thing a phaseless session most needs, since it has no branch and no integration
procedure to catch stray work.

This is the gap `000237` (amend the checkpoint and session-close skills to cover a session with no
claimed phase) already describes, now annotated with this occurrence. The first was
`SESS-2026-09-14-12`, a long planning session; this one is a single short investigation, which is
evidence the gap is not specific to large sittings. Both records were written by hand to the same
six-section shape, which is the argument for making that shape the contract rather than re-deciding
it a third time.

**One datum toward `000237`'s open question** about what replaces the independent review as the
honesty gate when there are no acceptance conditions. Here there was nothing for a reviewer to verify
against a declared list — but the session's own error was still caught mechanically, by the ideas
drift test. For a phaseless session whose output is data writes rather than code, the existing drift
tests may already be the proportionate gate, and the sub-agent review may be the wrong instrument
rather than a missing one. A candidate answer, not a settled one.

**The demo itself.** The application built for it went unused; the owner presented out of Claude Code
directly. Nothing in this repository records why that happened except `000246` and this paragraph, and
`000246` covers only the terminal. Whether anything else about the workbench contributed to the
judgement that it was not presentable was not asked and is not known.
