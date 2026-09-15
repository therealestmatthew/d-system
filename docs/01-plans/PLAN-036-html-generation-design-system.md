---
schema_version: 1
id: doc-html-generation-design-system
code: PLAN-036
title: HTML generation and design system (P9)
kind: plan
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-15'
systems: [sys-html]
depends_on: [doc-html-generation-design-system-requirements, doc-html-00-overview]
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

## Implementation phases

Six phases under `phase-des-*`, registered in [the backlog index](../09-backlog/README.md).

| Phase | Title | Group | Depends on |
|---|---|---|---|
| `phase-des-01` | Audit the pre-build HTML plans and disposition every `phase-html-*` phase | `G39` | — |
| `phase-des-02` | Build the governance atlas page in the atlas family | `G38` | — |
| `phase-des-03` | Make the template layer a growing library with declared population methods | `G37` | `01` |
| `phase-des-04` | Build the HTML component library | `G37` | `01` |
| `phase-des-05` | Build the colour palette library | `G37` | `01` |
| `phase-des-06` | Build the HTML Designer agent | `G37` | `03`, `04`, `05` |

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
| R09 Palettes are selectable data, not code branches | `phase-des-05` |
| R10 Each palette states its roles and variant coverage | `phase-des-05` |
| R11 The designer agent follows the existing family convention | `phase-des-06` |
| R12 No phase here builds a page `phase-idg-08` is ruling on | `phase-des-01`, `phase-des-02` |
| R13 The governance atlas page ships in the atlas family | `phase-des-02` |

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
