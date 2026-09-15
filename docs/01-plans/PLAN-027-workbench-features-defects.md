---
schema_version: 1
id: doc-workbench-features-defects
code: PLAN-027
title: Workbench features and defects (P11)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: [doc-workbench-features-defects-requirements, doc-workbench-requirements, doc-workbench-terminal-decision, doc-workbench-api-decision]
---

# Workbench features and defects (P11)

## Summary

Programme `P11` of the twelve, **third in the owner's delivery order**. Discrete, mostly small,
user-facing features and bugs in the shipped workbench. The programme is an administrative rollup
rather than a single design: each group touches a different panel or route and is independently
shippable.

It runs behind `P10` on the owner's ruling of 2026-09-14, so that `G40`'s vocabulary is settled
before any work here renames anything. The plan codes were already permanent by then, which is why
`PLAN-027` sits before `PLAN-028` while running after it; `next_up` is the authority on order.

**16 ideas across 9 fine groups**, from the accepted partition of 2026-09-13. Six of the sixteen were
already delivered when this plan was written. This plan turns the remaining ten into **10 phases**
under the `phase-wbf-*` prefix, governed by
[REQ-012](../06-requirements/REQ-012-workbench-features-defects.md).

| Group | Ideas | What it covers | Phases |
|---|---|---|---|
| `G48` HTML Viewer | `000109`, `000102` open; `000119`, `000110`, `000118`, `000232` delivered | Four of the five partition-time ideas plus `000232` shipped on 2026-09-14. What remains is the new-tab open and the freshness badge | `phase-wbf-01`, `phase-wbf-02` |
| `G49` File bookmarks | `000111`, `000120` | `000120` exists because `000111`'s "open a category as a set" has no mechanism without a batch panel-bridge contract | `phase-wbf-03` … `phase-wbf-05` |
| `G50` Rotator | `000131`, `000132` | Two variants of the same notes-strip component | `phase-wbf-06` |
| `G51` Terminal interaction API | `000087` | External HTTP inject/read and output buffering — the part `ADR-014` did not absorb | `phase-wbf-07`, `phase-wbf-08` |
| `G52` Session-cap race | `000095` | TOCTOU between the session-count check and `accept()` | `phase-wbf-09` |
| `G53` Shell override docs | `000096` | `D_SYSTEM_DEMO_SHELL` silently overrides per-session selection | `phase-wbf-09` |
| `G54` Flag-off 404 noise | `000100` | Cosmetic console noise when the terminal flag is unset | `phase-wbf-10` |
| `G55` Websocket close reason | `000137` | A global-cap refusal reaches the browser as a bare 1006 instead of a structured close | `phase-wbf-09` |
| `G56` PTY tests **[DELIVERED]** | `000099`, `000129` | **Already fixed** — the suite is green. Carried for completeness; no phase | — |

## What shipped on 2026-09-14, before this plan existed

A demo-driven session delivered a large part of `G48` the same evening this plan was finalized, and
that changed the programme's shape before any of it was planned. The delivery is recorded here
first, because planning around it without recording it would have produced phases for work that
already exists.

**`G48` is no longer the largest group.** Four of its ideas are done:

- **`000119` (render location)** — ruled and implemented route-side. `ts/vite.config.ts` imports
  `marked` and renders markdown inside the `serveRepositoryFiles` plugin at the `/workbench-file/`
  route (`593597e`), so the in-panel iframe and a new-tab open resolve to the same rendered output.
  The ruling in `_tmpagent/viewer-render-location-ruling.md` is **consumed**; it is not an open
  decision and this plan does not re-litigate it.
- **`000110` (markdown rendering)** — shipped in the same change. The `marked` dependency creates an
  `npm install` prerequisite, recorded in the runbook (`bdd1aa0`).
- **`000232` (the six image formats)** — shipped (`6896efc`), plus a fitted centred wrapper document
  for image presentation (`2e35ae7`) and a `?raw=1` discriminator that serves image bytes to
  sub-resource requests rather than the wrapper (`71cc841`).
- **`000118` (extension list growth)** — followed once rendering landed, exactly as its own text
  sequenced it.

Verified against the code rather than against the note that reported it:
`COMPATIBLE_EXTENSIONS` at `ts/src/stage/HtmlViewerRegion.tsx:25-36` holds `.html`, `.htm`, `.svg`,
`.md` and the six image formats; `FileBrowserRegion.tsx:4` imports that same constant and reads it at
line 500, so the File Browser's *Open in HTML Viewer* action followed for free; and
`GET /api/v1/workbench/search` was already extension-agnostic (`src/api/routes/workbench.py:439`
takes `ext` from the caller) and needed no change.

**`000232`'s open question was answered in the build, not deferred to planning.** The idea asked
whether bare-image iframe presentation was acceptable or an image needed wrapping for consistency,
and required the same answer for all six formats. The wrapper document is that answer. This plan
inherits it and settles nothing further.

Only **`000109`** (double-click opens a new browser tab) and **`000102`** (freshness badge) remain
open in `G48`.

### These six ideas keep their current status, and that is deliberate

`000110`, `000118` and `000119` remain `triaged`; `000232` remains `open`. Each carries a finding
annotation recording what shipped, where, and the commit that did it.

They were not moved, because the idea lifecycle has no honest state for them. `promoted` requires
`promoted_to` naming the governed documents an idea produced, and these produced none — they were
delivered directly as code. `discarded` means *rejected*, and these were built. The `G56` precedent
(`000099`, `000129`) used `discarded` anyway, with an annotation reading *"Verified resolved;
discarded by owner ruling 2026-09-13"* doing the work the status could not — a record contradicting
its own status field in prose.

The owner ruled on 2026-09-14: use a `resolved` status if one exists, and if not, record in place and
hold. None exists (`schemas/idea.schema.json`'s enum is `open | triaged | reviewing | promoted |
discarded`), so they are recorded in place.

> **Standing note — work to pick up later.** When a terminal `resolved` status exists, return to
> `000110`, `000118`, `000119` and `000232` and move them to it, and decide whether `000099` and
> `000129` are amended from `discarded` or left as the historical record. The gap is captured as
> **`000236` (a terminal resolved idea status, distinct from promoted and discarded)**, which links
> to all five. It belongs to `P1` ([PLAN-029](PLAN-029-idea-graph-lifecycle.md)) by subject matter;
> this programme builds none of it.

## The chosen design

Six decisions shape the ten phases.

### 1. `000102` keeps the partition's ruling, on the owner's affirmation

The partition placed `000102` (freshness badge) in `G48` **by content rather than provenance** — it
surfaced during a rehearsal, and its body still carries the marker *"this idea is part of the demo
record, not a real audience suggestion"* — while flagging the call as *"ruled on a principle, not a
repository check… the weakest resolution in this table"* and inviting the owner to reverse it.

The owner affirmed it on 2026-09-14: it keeps its place and gets its own phase. Content decides
buildability, and a last-refreshed badge on the viewer header is real, small, shippable work. This is
recorded because the partition asked to be checked here; the ruling is now affirmed rather than
merely inherited.

The owner also declined folding it into `phase-wbf-01`. The two remaining `G48` ideas share only the
panel: one is a tab-strip interaction, the other a header element. A phase carrying both would have
two unrelated acceptance halves.

### 2. `000233` (panel maximize) is `P10`'s, and gets no phase here

Ruled into `G43` as `phase-arch-17` by [`PLAN-028`](PLAN-028-workbench-architecture-quality.md)
design decision 5, because the mechanism is slot geometry rather than a viewer feature. **No
`phase-wbf-*` phase implements maximize**, and `REQ-012` carries no row for it.

A `G48` phase adding maximize to the HTML Viewer would duplicate `phase-arch-17` and create the
second geometry path that ruling exists to prevent. The idea was raised on the viewer, which is why
it needs saying here rather than only there.

### 3. `G49` and `G51` are ADR-first, and the ADR is its own phase

Both groups begin with a decision, not a build.

`000111` says so in its own text: the storage and reference model *"needs an owner-reviewed decision
before creators build panels against it."* `000087` inherits `ADR-013`'s precedent that a shell
capability beyond the demo stage starts from its own decision record — and `ADR-014` has since
absorbed its session-registry half, so the ADR's first job is to scope itself to what remains rather
than re-decide what is settled.

In both cases the ADR is a separate phase from the implementation. Fusing them would put an
owner-reviewed decision inside a session that has already built against it, which is the review
arriving after the thing it was meant to gate.

`G49`'s ADR covers **both** its ideas, not one each. `000111`'s "how do other surfaces consume a
category" and `000120`'s "the bridge needs a batch contract" are the same decision surface asked from
two directions; two ADRs would have to agree with each other.

### 4. The four small defect groups become two phases, split by system

`G52`, `G53`, `G54` and `G55` were each sized at under one session. Four phases for four sub-session
items would serialise four sessions on locks they need for minutes each.

`G52` (cap race), `G53` (shell override) and `G55` (close reason) all land in
`src/api/routes/demo_terminal.py`, and `G52` and `G55` land within twenty-six lines of each other —
the cap check at line 287, the pre-accept close at 288, the accept at 313. `G55`'s fix (accept first,
then close with a structured frame) and `G52`'s fix (reserve the slot before accept) are two edits to
the same control flow, and doing them in separate sessions means the second rebases onto the first's
rewrite of the lines it needs. They ship together as `phase-wbf-09`.

`G54` is frontend — `ts/src/stage/InjectionDropdowns.tsx` fetches unconditionally — and stays its own
phase, `phase-wbf-10`, because it shares neither system nor file with the other three.

### 5. `G50`'s two variants ship in one phase, because they share an entry model

`000131` (horizontally scrolling text) and `000132` (image entries) are both changes to the notes
strip, and the partition sized them at one phase together. That sizing holds for a reason worth
stating: a text entry and an image entry are one union type in the rotator's entry model. Splitting
them means designing that model twice, and the second phase rewriting the first's.

`000132` raises a bookmark category as one possible source for its image set, referencing `000111`.
**This plan does not couple them.** `phase-wbf-06` sources images from a directory and carries no
edge to `G49`; a category becomes an additional source later if the bookmark model makes it cheap.
Coupling a one-phase rotator change to a three-phase ADR-first programme would be the expensive half
of the pair deciding when the cheap half ships.

### 6. Phases declare `sys-ui` as it exists today

`phase-arch-00` will decompose `sys-ui`, and `phase-arch-18` retires it, but neither has run. Seven
of these ten phases touch `ts/src/stage/` and declare `sys-ui`, which the validator treats as a
collision — the same effect `PLAN-028` measured as the reason `P10`'s concurrency ceiling is 1 from
its third wave onward.

They declare the lock table that exists rather than the one that is coming. Declaring successor
systems would name systems the validator does not know, and adding an edge to `phase-arch-00` would
block this entire programme behind a phase nobody has claimed. The phases stay claimable now and
widen for free when the decomposition lands. The owner ruled this on 2026-09-14 and declined an
accompanying revisit note, so no phase here carries an instruction to re-declare.

## Sequencing against `P10`

Per [`PLAN-028`](PLAN-028-workbench-architecture-quality.md)'s *What P11 depends on*: any `P11` phase
that renames a slot, panel, region or layout identifier, or that writes requirement rows using those
nouns, declares `depends_on: [phase-arch-01]` — the settled vocabulary, **not** `phase-arch-02`, the
migration.

**Four phases carry that edge**, and six do not:

| Phase | Edge | Why |
|---|---|---|
| `phase-wbf-03` | `phase-arch-01` | Its ADR specifies how panels consume a category as a set; it cannot name the consuming surfaces before the nouns are settled |
| `phase-wbf-04` | `phase-arch-01` | It rewrites `panelBridge.ts`'s `BridgeSlot` contract — a slot identifier, by name and by meaning |
| `phase-wbf-05` | `phase-arch-01` | It adds a consuming surface and writes against `R05`'s reference model |
| `phase-wbf-06` | `phase-arch-01` | `000131`'s own text proposes a substitute panel in the rotator's slot, against `REQ-007` W16's per-panel eligibility model |
| `phase-wbf-01`, `-02` | none | Confined to `HtmlViewerRegion.tsx`; their rows name the HTML Viewer by product name and rename nothing |
| `phase-wbf-07` … `-10` | none | Route-layer and console work; no slot, panel, region or layout identifier appears |

One collision risk is worth naming rather than encoding: `phase-arch-02`, the identifier migration,
may rename `HtmlViewerRegion.tsx` itself, which `phase-wbf-01` and `phase-wbf-02` edit. That is a
file-level conflict for a coordinator to sequence, not a vocabulary dependency — and `PLAN-028`'s
rule is explicit that the edge belongs on `phase-arch-01`. Adding a `phase-arch-02` edge here would
block two small viewer features behind the largest rename in the sibling programme.

## Implementation phases

Ten implementation phases under `phase-wbf-*`, registered in
[the backlog index](../09-backlog/README.md).

An eleventh id, `phase-wbf-11`, is **not** one of them. It was backfilled on 2026-09-14 by the
session that shipped `000232`, `000110`, `000118` and `000119`, as a completed record of work that
was already done — `status: complete`, owned by `agent-demo-a`, carrying that session's own
verification. It implements nothing outstanding and carries no `REQ-012` row, by design: the
delivered ideas get no implementation phase, and a backfill is a record of history rather than a
claim on the future. A coordinator counting work to do should count the ten below.

| Phase | Title | Group | Depends on |
|---|---|---|---|
| `phase-wbf-01` | Open a viewer tab's file in a new browser tab on double-click | `G48` | — |
| `phase-wbf-02` | Show a last-modified badge on the HTML Viewer header | `G48` | — |
| `phase-wbf-03` | Decide the bookmark category storage, reference and batch-bridge model | `G49` | `phase-arch-01` |
| `phase-wbf-04` | Extend the panel bridge to batch, multi-target actions | `G49` | `phase-arch-01`, `03` |
| `phase-wbf-05` | Build the bookmark category surface and its consumers | `G49` | `phase-arch-01`, `03`, `04` |
| `phase-wbf-06` | Rotator variants: horizontally scrolling text and image entries | `G50` | `phase-arch-01` |
| `phase-wbf-07` | Decide the external terminal interaction API | `G51` | — |
| `phase-wbf-08` | Build the flag-gated terminal inject and read API | `G51` | `07` |
| `phase-wbf-09` | Terminal route defects: cap race, shell override, close reason | `G52`, `G53`, `G55` | — |
| `phase-wbf-10` | Silence the flag-off workbench probes | `G54` | — |

### Sizing against the partition

Partition-time sizing was **8–10 phases excluding `G56`**. This plan lands **10**, at the top of that
range, against a corpus six ideas smaller than the one that was sized. That reads like growth and is
not; three stated movements account for it, and they nearly cancel.

- **Down 1, from the delivery.** `G48` was sized at 2 phases for 5 ideas — a render phase and an
  interactions phase. The render half shipped. Its two survivors, `000109` and `000102`, still need
  2 phases, because they are unrelated surfaces and the owner declined folding them (design decision
  1). So `G48` holds at 2 while carrying less than half the work, and the delivery's saving lands in
  the *content* of `G48`'s phases rather than in their count. `000232`, raised after the partition
  and never sized by it, shipped too and adds nothing.
- **Down 2, from consolidating the small defects.** Four sub-session groups become two phases
  (design decision 4). The partition's own 8–10 total implies it counted them as roughly 2 already,
  so this is where the plan matches rather than beats it.
- **Up 2, from ADR-first.** `G49` lands at 3 against a 2–3 range and `G51` at 2 against 1–2 — both at
  the top, both because the ADR is a separate phase (design decision 3). Neither exceeds its range.

`G50` lands at 1, exactly as sized.

**The honest summary: the delivery shrank the work without shrinking the phase count**, because what
shipped was concentrated in one group whose remaining ideas cannot be merged. A coordinator should
expect `phase-wbf-01`, `-02` and `-10` to be short sessions rather than expect fewer of them.

## Requirement coverage

Every row of [`REQ-012`](../06-requirements/REQ-012-workbench-features-defects.md) maps to at least
one phase, and every one of the ten implementation phases carries at least one row. `phase-wbf-11`
is outside this property for the reason given above.

| Requirement | Phases |
|---|---|
| R01 New-tab open shows the same rendered output as the panel | `phase-wbf-01` |
| R02 The new-tab open inherits the sandbox posture | `phase-wbf-01` |
| R03 The viewer header shows the displayed file's last-modified time | `phase-wbf-02` |
| R04 The badge tracks tab switches and on-disk changes | `phase-wbf-02` |
| R05 An ADR records storage shape, reference model and path validity | `phase-wbf-03` |
| R06 The ADR states multi-surface consumption and the bridge consequence | `phase-wbf-03` |
| R07 The panel bridge supports a batch, multi-target action | `phase-wbf-04` |
| R08 The bridge's degradation contract survives the extension | `phase-wbf-04` |
| R09 Categories can be created, renamed, deleted, populated and listed | `phase-wbf-05` |
| R10 Referencing a category opens its files as a set | `phase-wbf-05` |
| R11 A category with a missing file degrades legibly | `phase-wbf-05` |
| R12 Long rotator entries scroll horizontally and can be paused | `phase-wbf-06` |
| R13 Rotation and within-entry scrolling have a stated interaction | `phase-wbf-06` |
| R14 The rotator rotates images, with sizing and a mixing ruling | `phase-wbf-06` |
| R15 An ADR covers gating, binding, identity, auth, buffering, detach | `phase-wbf-07` |
| R16 The ADR scopes itself against what ADR-014 already owns | `phase-wbf-07` |
| R17 HTTP injection reaches a named live session | `phase-wbf-08` |
| R18 HTTP reads do not steal bytes from the websocket pump | `phase-wbf-08` |
| R19 Flag-off means the routes are absent | `phase-wbf-08` |
| R20 The cap's registry slot is reserved before `accept()` | `phase-wbf-09` |
| R21 A cap refusal reaches the browser as a structured close | `phase-wbf-09` |
| R22 The shell override's interaction is documented or reconciled | `phase-wbf-09` |
| R23 Flag-off produces no 404 console entries | `phase-wbf-10` |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P11`.
- **This programme's requirement** — [REQ-012](../06-requirements/REQ-012-workbench-features-defects.md).
- **The sibling programme** — [PLAN-028](PLAN-028-workbench-architecture-quality.md) and [REQ-011](../06-requirements/REQ-011-workbench-architecture-quality.md).
- **Workbench requirements** ([REQ-007](../06-requirements/REQ-007-workbench.md)) and the **workbench plan** ([PLAN-022](PLAN-022-workbench.md)) — the shipped product this programme changes.
- **Workbench terminal capability** ([ADR-014](../04-decisions/ADR-014-workbench-terminal-capability.md)) and **API surface** ([ADR-015](../04-decisions/ADR-015-workbench-api-surface.md)).
- **Demo terminal capability** ([ADR-013](../04-decisions/ADR-013-demo-terminal-capability.md)) — the precedent that says `G51` needs its own ADR.
