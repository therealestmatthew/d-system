---
schema_version: 1
id: doc-html-generation-design-system
code: PLAN-036
title: HTML generation and design system (P9)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-30'
systems: [sys-html]
depends_on: [doc-html-generation-design-system-requirements, doc-engine-pages-house-style-requirements, doc-html-00-overview]
---

# HTML generation and design system (P9)

## Summary

Programme `P9` of the twelve. Six ideas across three fine groups: the template, component and palette
layer of the generation pipeline, and its relationship to plans written before the workbench existed.

| Group | Ideas | What it covers |
|---|---|---|
| `G37` Libraries and designer agent | `000083`, `000084`, `000085`, `000092` | Three cross-linked asset layers, plus the agent that would populate all three by scanning shipped pages |
| `G38` Governance atlas page | `000093` | A content deliverable from the existing atlas family |
| `G39` HTML-gen plan reconciliation | `000123` | Dispositions each old `phase-html-*` requirement as accomplished, open, superseded or retired |

Partition-time sizing was 5–6 phases, "mostly gated on `PLAN-003`". This plan lands **six**, and
changes what they are gated on — see design decision 1.

**Amended on 2026-09-30.** The owner moved this programme's priority to the idea realization
engine's generated pages. The amendment adds six phases (`phase-des-07` to `-12`), cancels one
(`phase-des-05`) and re-gates four. Its requirement is
[REQ-036](../06-requirements/REQ-036-engine-pages-house-style.md). The section
"Amendment, 2026-09-30" below states the decisions and their reasons. The sections between here
and that one are the plan as written on 2026-09-15. Where they conflict with the amendment, the
amendment wins.

## What was checked before sizing

**Ten `phase-html-*` phases are `queued` and none is complete**, against a `PLAN-003` whose front
matter reads `status: approved` and which carries six child plans. All of it predates the live demo
and the workbench, both of which shipped real generated pages.

**Two template families already exist**, not one:

```
$ ls templates/html/ templates/styles/
atlas-components.html  atlas-page.html  atlas.css
overview-bar.html  overview-page.html  overview.css
overview-concept-row.html  overview-concepts-panel.html
overview-metrics-section.html  overview-system-row.html
overview-systems-panel.html  overview-term-row.html
```

**Five shipped pages exist** for a designer agent to scan:

```
$ ls _public/
d-system-architecture.html  prompt-pack-protocol.html  research-protocol.html
skills-and-agents-lexicon.html  overview/  images/
```

So the family convention `000092` would follow is demonstrated twice, and `000093`'s governance atlas
page has a working companion in `_public/prompt-pack-protocol.html` built from the same family.

## The boundary against `PLAN-029`'s `G03`

The phase's acceptance requires this stated explicitly, and it became sharper while this batch ran.

`G03` is idea and backlog **reporting** — what a report says and whether it is wanted. It landed in
`phase-idg-08` earlier tonight, whose scope includes ruling "on `000042`: whether a generated
ideas-and-backlog HTML page is still wanted now that `IdeaExplorerRegion` and `BacklogExplorerRegion`
both ship in the workbench."

`P9` is the **supply**: the families, components and palettes any generated page is assembled from.

**The relationship runs one way.** If `phase-idg-08` rules the page is wanted, it gets built from
`P9`'s assets instead of bespoke markup — `000084`'s composability point meeting a real consumer. If
it rules the page is not wanted, `P9` is unaffected, because its assets already serve five pages.

The failure this prevents is concrete: `P9` sizing a phase to build an ideas-and-backlog page while
`phase-idg-08` separately decides whether that page should exist. `R12` forbids any phase here to
carry such a deliverable — checked by a reviewer reading the `deliverables` field, not by anything
running in `src/governance`.

The boundary is not this plan's invention. A triage annotation on `000093` from 2026-09-11 already
separates the two: `000042` is "about HTML page generation from governed data, but for a different
topic (idea/backlog prioritization rather than governance system documentation)." This plan states
what was already found rather than drawing a new line.

## The chosen design

### 1. `G39` runs first, and the asset work is gated on it rather than on `PLAN-003`

The scope requires `G39` ahead of `G37`'s detailed scoping, because `G39` produces that scope. This
plan goes further and **changes what `G37` is gated on**.

The partition gates `G37` on `PLAN-003`. But `PLAN-003` is exactly what `G39` audits, and the audit
may find parts of it accomplished, superseded or retired. Gating the asset libraries on a plan whose
current standing is the thing under audit would hold them behind a document that might not survive
the audit intact.

There is a sharper reason, surfaced by this phase's review. **`PLAN-003` and the shipped families
describe different technologies.** Its six child plans are a FastAPI/React pipeline — build tooling,
backend endpoints, frontend components. The two families that actually exist and serve five pages
today are static HTML, CSS and vanilla JavaScript, produced by a different mechanism. So gating
static-asset work on an unbuilt dynamic pipeline gates it on something largely irrelevant to what
exists, as well as on something the audit may retire.

So `phase-des-03`, `-04` and `-05` depend on `phase-des-01`, not on `PLAN-003`. `R04` makes the asset
phases cite the audit's findings, so the sequencing is a real dependency rather than an ordering
preference.

### 2. The audit must change the backlog, not just describe it

`R02` is the half that gives `G39` teeth. Ten phases sit `queued`; a disposition recorded in a
document while all ten stay `queued` has changed nothing a coordinator reads, and `--ready` keeps
offering obsolete work.

`R03` adds the discipline that makes "accomplished" checkable: it must name the demo or workbench
work that accomplished it. "Covered by the workbench" with no reference is an assertion, and this
batch has already found four documented blockers that dissolved on inspection — the same failure in
the other direction would retire phases that are still needed.

### 3. The three asset layers are separate phases because they have different unknowns

`000083`, `000084` and `000085` are cross-linked and could plausibly be one phase. They are three,
because each carries a distinct open question the others do not: the template library's is *how a
template declares its population method* (`R06` — deterministic slot-filling or AI adaptation, and
machine-readable so a generator can dispatch on it); the component library's is *which components
earn their place and which need script* (`R07`, `R08`); the palette library's is *what a palette's
role set is and whether it carries variants* (`R10`), both of which `000085` explicitly leaves open.

Bundling them would produce one phase with three unresolved design questions and no way to review it
as a unit.

### 4. The designer agent comes last, because it populates libraries that must exist

`000092` scans shipped pages and extracts their design into families. It depends on all three asset
phases: without a template contract there is nowhere to write a family, without a component
vocabulary there is nothing to name the extracted patterns as, and without a palette format the
extracted token set has no shape to land in.

`R11` requires its output to follow the existing convention — header comment with provenance and
usage, token contract, canonical component markup — which is checkable precisely because `atlas`
demonstrates it.

### 5. `G38` is independent and can be claimed today

`000093` needs the atlas family, which exists, and nothing else. It is not gated on the audit, the
asset libraries or the agent. The owner deferred it once on 2026-09-10 — "protocol + case studies for
now, note to come back and build the broader governance atlas later" — and that deferral was about
sequencing attention, not a missing prerequisite.

It is the only phase in this programme that ships reader-facing content rather than machinery.

### Which of these need a decision record

**One, conditionally.** If `phase-des-01`'s audit concludes that `PLAN-003` is substantially
superseded, that needs an ADR: retiring or rewriting an approved plan with six children and ten
phases is an architectural commitment a future reader must be able to trace. If the audit finds
`PLAN-003` broadly intact, the dispositions in the backlog are the record and no ADR is needed.
`phase-des-01`'s scope says so conditionally.

Decisions 1, 3, 4 and 5 are recorded here and in `REQ-021`'s rows. Decision 2 is `R02` itself.

## Amendment, 2026-09-30: the engine pages and the house style

### What changed and who decided it

The Session Manager relayed the owner's change of course on 2026-09-30. The owner answered the
questions below in the amending session. `REQ-036` records each ruling.

- **The house style is approved.** The owner approved the round-2 gallery as shown
  (`https://claude.ai/artifact/D15aCx8HqwfVmKmKtKDKFi`). It shows the magazine house style with
  Swiss and technical-mono variants on shared tokens, light and dark through one colour-only flag,
  and Google Fonts with a system-font fallback. Repository tokens are the source of truth, as
  recorded on idea `000511`.
- **The first page set is four pages.** (1) A pipeline overview: the stages with counts and what
  is waiting at each gate. (2) An idea funnel and ledger: every idea by status and axis, from
  `fold()`. (3) A per-idea trace: capture, then plan, then phases, then delivered, with gate
  decisions. (4) A backlog and batch graph: batches, stages and dependencies with their states,
  showing what is blocked and why.

### Decision A. Pages first: how `phase-des-01` to `-06` fit the new phases

**Decision.** The token phase (`phase-des-07`) and the four page phases are not gated on the audit
of the pre-build plans (`phase-des-01`). Each existing phase changes as follows:

| Phase | Before | After | Reason |
|---|---|---|---|
| `phase-des-01` audit | gated `-03`, `-04`, `-05` | still gates `-03` and `-04`; gates no new phase | The audit dispositions the ten `phase-html-*` phases. That is still real work, but none of the four pages depends on its outcome. They are built from the house family and from records that exist today. |
| `phase-des-02` governance atlas page | atlas family, no dependency | house family, depends on `-07` | The owner chose to move it onto the house style rather than add a fourth page in the old dark atlas design. |
| `phase-des-03` template library | depends on `-01` | depends on `-01` and the four page phases | A library extracted from four working pages has real cases to generalise from. Written before them, it would have to guess what the pages need. |
| `phase-des-04` component library | depends on `-01` | depends on `-01` and the four page phases | Same reason. The pages also show which components are needed and which need script. |
| `phase-des-05` palette library | depends on `-01` | **cancelled** | Its two open questions, the role set and light and dark coverage, are answered by the approved gallery. `phase-des-07` builds the token set that answers them. The phase id is kept and not reused. |
| `phase-des-06` designer agent | depends on `-03`, `-04`, `-05` | depends on `-03`, `-04`, `-07` | The token format it writes into now comes from `-07`. |

**Why not keep the old order.** Under the old order the pages would wait for the audit and all
three library phases. That is five phases, none of which changes what the pages show. The owner
made the pages the priority.

**Why not retire `-03`, `-04` and `-06`.** The owner chose to keep them. The template library's
machine-readable population method (`REQ-021` R05, R06), the component library's script
declaration (R07, R08) and the designer agent (R11) are not covered by the six new phases.

### Decision B. Trace links come from a new structured field on phases

Only 13 ideas carry `promoted_to`, and 38 links point at a document code. No phase field names an
idea. A trace built on that data would show fewer than one idea in ten. The owner chose a
structured `ideas` field on backlog phases, backfilled from the ids named in each phase's own text
(`phase-des-08`). The trace (`phase-des-11`) depends on it. The validator rejects an id that
`fold()` does not contain, so a backfill error fails the governance check instead of producing
a wrong trace.

The backfill reads only the phase's own `scope`, `acceptance` and `next_action`. It does not read
the plan document. A plan that names twenty ideas would otherwise link all twenty to every one of
its phases, and the trace would claim more than the records say.

### Decision C. Gate decisions are derived from records

`_data/gate-decisions.jsonl` does not exist. The owner chose derivation over starting a new log.
`REQ-036` R14 and R20 state the derivation for each gate. Two consequences:

- **G2 shows "not recorded".** The accepted partitions are Markdown documents under
  `docs/00-working/`, not structured records, and parsing prose for gate decisions would make the
  page guess. The trace says so and names the missing record (`REQ-036` R11).
- **G4 and G5 are one entry.** Integration has been fast-forward-only since 2026-09-10, so `dev` has no
  merge commits after that date. It has one from before (`818f64b`, 2026-09-10), so the trace walks
  `dev`'s first-parent history. The completion edit is made on `dev` in the same turn as the merge (the Session Manager's contract,
  item 4). The earliest `dev` commit where a phase reads `complete` is therefore the record of both.
  The owner's wording was "merge commit on dev". This is the nearest record that exists, and the
  page states the reason.

### Decision D. The funnel's axes are the `ARCH-005` axes, shown as they are

No idea carries a classification today, so every idea is "unclassified" on all four axes. The
owner chose to show that state rather than drop the axis view or substitute the partition track.
The view fills in as ideas are classified, with no page change.

### Decision E. Committed snapshots, no staleness gate

Pages are committed under `_public/engine/`, each stamped with its source commit and that
commit's date. The generator is tested for determinism (`REQ-036` R07), not for currency. The idea
log changes many times a day, and a currency gate like the catalog's would fail on most commits.
The owner chose this over a gate and over gitignored output.

### Decision F. One shared generator, then one phase per page

`phase-des-09` builds the generator, its shared data layer and the first page, the pipeline
overview. The first page is in the same phase so the layer is built against a real consumer. Each
further page is its own phase because each has a different data question. The ledger's is the
axes. The trace's is the gate derivation and its git reads. The graph's is a static SVG layout
with no script (`REQ-036` R12).

All six new phases declare `sys-html` except `phase-des-08`, so the lock table runs the page phases
one at a time. The dependency chain orders most of them already. The exception is `phase-des-12`,
which depends only on `-09` and could otherwise run beside `-10` or `-11`. The lock serialises it
because all four page phases edit the same generator file, `tools/generate_engine_pages.py`.

Deliverables are declared as specific files where a phase shares a directory with another
(`docs/08-governance/`, `test/`), so the lock table does not serialise phases that touch different
files there. The two new operations documents have codes reserved in `codes.yaml` for this reason:
OPS-027 for `phase-des-07`'s CSS generator and OPS-028 for `phase-des-09`'s page generator.
`phase-des-08`'s backfill is a `src.governance` mode rather than a new tool, so it needs no
operations document.

**Sizing.** `phase-des-07` is the densest phase: tokens, a CSS generator, a page shell and five
components. It is kept as one phase because the gallery already fixes every value and every
component, so the session transcribes and tests rather than designs. If it runs over, `GOV-002`'s rule
applies and the remainder gets a new phase id.

### Decision G. `REQ-021`'s rows that this amendment changes

R09 and R10 are superseded by `REQ-036` R01 to R04. R12 is spent: it forbade building a page whose
existence `phase-idg-08` was ruling on, and the owner kept those pages on 2026-09-21 (`GOV-003`).
`phase-idg-08` still records that ruling and wraps the metrics command, and it builds no page. R13
moves to the house family. `REQ-021` carries a note saying so.

### Boundaries

- **Monitoring artifact** (`000497`, investigated by `PROMPT-042`): sessions, branches, worktrees
  and claims are not shown here. These pages cover ideas, plans, phases and batches.
- **Orchestrator batch graph** (`phase-irs-14`): a LangGraph fan-out, not a page. Page 4 draws the
  batch tables.
- **Workbench explorers** (`phase-wb-06`): the live view. These pages are the snapshots.

### Open, not sized here

- **Mirroring the tokens to a Claude Design System artifact.** The owner ruled it later. It is the
  next step after `phase-des-07` and gets a phase when the owner asks for one.
- **Migrating existing pages to the house style.** The atlas, overview and lit-report families and
  the six `_public/` pages are unchanged.
- **Contrast admission for palettes** (`000085`). The owner approved the gallery's values as shown.

### New phases

| Phase | Title | Depends on | Requirement rows |
|---|---|---|---|
| `phase-des-07` | Commit the house-style tokens and generate the house family | — | `REQ-036` R01–R06 |
| `phase-des-08` | Give backlog phases a structured idea field and backfill it | — | `REQ-036` R17, R18 |
| `phase-des-09` | Build the engine page generator and the pipeline overview page | `07` | `REQ-036` R07–R14 |
| `phase-des-10` | Build the idea funnel and ledger page | `09` | `REQ-036` R15, R16 |
| `phase-des-11` | Build the per-idea trace pages | `08`, `10` | `REQ-036` R19, R20 |
| `phase-des-12` | Build the backlog and batch graph page | `09` | `REQ-036` R21–R23 |

`REQ-036` R24 and R25 are this amendment's own edits to the backlog and to `REQ-021`, made in the
amending commit.

The critical path is four deep: `07`, then `09`, then `10`, then `11`. `phase-des-07` and
`phase-des-08` touch different systems and can run at once. The new phases carry priority 1, the
highest in use, because the owner made them this programme's priority. Their place in `next_up` is
the owner's to set at G3. This amendment does not edit `next_up`.

## Implementation phases

Six phases under `phase-des-*`, registered in [the backlog index](../09-backlog/README.md).

| Phase | Title | Group | Depends on |
|---|---|---|---|
| `phase-des-01` | Audit the pre-build HTML plans and disposition every `phase-html-*` phase | `G39` | — |
| `phase-des-02` | Build the governance atlas page in the atlas family (house family since 2026-09-30) | `G38` | `07` (since 2026-09-30) |
| `phase-des-03` | Make the template layer a growing library with declared population methods | `G37` | `01`; and `09`–`12` since 2026-09-30 |
| `phase-des-04` | Build the HTML component library | `G37` | `01`; and `09`–`12` since 2026-09-30 |
| `phase-des-05` | Build the colour palette library — **cancelled 2026-09-30**, superseded by `phase-des-07` | `G37` | `01` |
| `phase-des-06` | Build the HTML Designer agent | `G37` | `03`, `04`, `07` (was `05` until 2026-09-30) |

### Sizing against the partition

Group ranges were `G37` 3–4, `G38` 1, `G39` 1 — 5–6 total. This plan lands **six**: `G37` at 4, `G38`
at 1, `G39` at 1. Every group lands inside its own range, which makes `P9` the only programme this
batch has planned where that is true of all groups at once.

The departure is not in the count but in the gating, per decision 1.

## Execution order and real concurrency

`phase-des-01` and `phase-des-02` are both claimable immediately and do not collide — one is an audit
producing documents and backlog dispositions, the other builds a page from an existing family. They
can run at once.

After the audit, `phase-des-03`, `-04` and `-05` are released together. Whether they can run
concurrently depends on what the audit scopes them to; all three declare `sys-html`, so the lock
table will serialise them unless their deliverable paths turn out disjoint. Treat three-at-once as
unlikely.

The critical path is three deep: `01` → `03`/`04`/`05` → `06`.

## Requirement coverage

Every row of `REQ-021` maps to at least one phase, and every phase carries at least one row.

| Requirement | Phases |
|---|---|
| R01 Every pre-build requirement dispositioned | `phase-des-01` |
| R02 Obsolete phases changed in the backlog, not just described | `phase-des-01` |
| R03 "Accomplished" names what accomplished it | `phase-des-01` |
| R04 The audit produces the asset work's scope | `phase-des-03`, `phase-des-04`, `phase-des-05` |
| R05 The template layer grows without generator changes | `phase-des-03` |
| R06 Each template declares a machine-readable population method | `phase-des-03` |
| R07 Components compose a page without bespoke markup | `phase-des-04` |
| R08 Script-free components ship no script | `phase-des-04` |
| R09 Palettes are selectable data, not code branches | superseded by `REQ-036` R01–R04 (`phase-des-07`) |
| R10 Each palette states its roles and variant coverage | superseded by `REQ-036` R01–R04 (`phase-des-07`) |
| R11 The designer agent follows the existing family convention | `phase-des-06` |
| R12 No phase here builds a page `phase-idg-08` is ruling on | spent by the owner's 2026-09-21 ruling (Decision G) |
| R13 The governance atlas page ships in the atlas family (house family since 2026-09-30) | `phase-des-02` |

## Key references

- **The requirement** — [REQ-021](../06-requirements/REQ-021-html-generation-design-system.md).
- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P9`, including the `G39`-before-`G37` sequencing this plan implements and extends.
- **The HTML generation plan** ([PLAN-003](PLAN-003-dynamic-html-generation/PLAN-003-overview.md)) — `approved`, six child plans, ten `queued` phases, and the subject of `phase-des-01`'s audit.
- **Idea graph and lifecycle** ([PLAN-029](PLAN-029-idea-graph-lifecycle.md)) — `phase-idg-08` owns the `000042` ruling this programme must not pre-empt.
- **The existing families** — `templates/html/atlas-page.html`, `templates/styles/atlas.css` and the `overview-*` set, which are the convention `R11` checks against.

## Known facts not to rediscover

- **Two template families exist, not one.** `atlas` and `overview`. The convention is demonstrated
  twice.
- **Five pages ship in `_public/`**, which is the corpus `000092`'s agent scans. It is not
  hypothetical material.
- **All ten `phase-html-*` phases are `queued`.** None is complete, and `--ready` offers them today.
- **`PLAN-003` is `approved`, not draft**, with six child plans. The audit's job is to establish what
  survives, not to assume it is stale.
- **`000093` was deferred by the owner on 2026-09-10 for sequencing, not for a missing
  prerequisite.** Its family exists; it is claimable now.
- **`000085` leaves the palette role set and light/dark variants explicitly open.** `R10` closes them;
  do not treat them as already decided.
- **The `G03` boundary is one-way.** `P9` supplies assets; `phase-idg-08` decides whether a given
  report page exists. `R12` forbids this programme deciding it.
