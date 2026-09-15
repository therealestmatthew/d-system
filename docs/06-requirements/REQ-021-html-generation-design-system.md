---
schema_version: 1
id: doc-html-generation-design-system-requirements
code: REQ-021
title: HTML generation and design system requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-html]
depends_on: [doc-html-00-overview]
---

# HTML generation and design system requirements

## Observed problem and scope

Six ideas covering the template, component and palette layer of the generation pipeline — and its
relationship to plans written before the workbench existed.

**The unresolved question underneath all of them is how much of the pre-build plan still applies.**

```
$ python3 -c "... status counts for phase-html-*"
{'queued': 10}

$ grep -n "^status:" docs/01-plans/PLAN-003-dynamic-html-generation/PLAN-003-overview.md
7:status: approved
```

`PLAN-003` is `approved`, has six child plans, and carries **ten `queued` phases, none complete**.
Those plans and phases were written before the live demo and the workbench were built. Both of those
builds shipped real generated pages and real template families. Nobody has established which of the
ten phases the later work already accomplished under a different name, which remain open, which are
superseded and which should be retired (`000123`).

That matters because everything else in this programme is scoped against it. A template library, a
component library and a palette library are all extensions of a pipeline whose current state nobody
has audited.

### What already exists, verified

The programme is not starting from nothing, and the existing work is the precedent the rest builds on.

```
$ ls templates/html/ templates/styles/
atlas-components.html   atlas-page.html      atlas.css
overview-bar.html       overview-page.html   overview.css
overview-concept-row.html   overview-concepts-panel.html
overview-metrics-section.html   overview-system-row.html
overview-systems-panel.html     overview-term-row.html

$ ls _public/
d-system-architecture.html  prompt-pack-protocol.html  research-protocol.html
skills-and-agents-lexicon.html  overview/  images/
```

**Two template families exist** — `atlas` and `overview` — so the family convention `000092`'s
designer agent would follow is demonstrated twice rather than once. **Five shipped pages exist** for
that agent to scan. `000093`'s governance atlas page has a working companion in
`_public/prompt-pack-protocol.html`, built from the same family.

### The gaps

1. **The template layer is a fixed set, not a growing library.** `templates/html/` and
   `templates/styles/` hold exactly what the two shipped families needed. Nothing makes them
   accumulating, reusable assets with a stated population method — deterministic slot-filling or AI
   adaptation (`000083`).

2. **There is no component library.** Page generation emits bespoke markup rather than assembling
   from known-good blocks: menu bars, hover dialogs, toolbars, tooltips, in-page search, an embedded
   terminal (`000084`).

3. **Colours are hard-coded per family.** No palette library exists, so a generated page or family
   cannot pick a pre-vetted combination (`000085`).

4. **Nothing extracts design from shipped pages.** Five pages exist; their token sets, type scales
   and component patterns live only in those files (`000092`).

5. **The governance atlas page is deferred, not built.** The owner deferred it on 2026-09-10 when
   scoping the protocol page — "protocol + case studies for now, note to come back and build the
   broader governance atlas later" (`000093`).

This requirement covers the HTML generation and design system programme (`P9`): the asset layers, the
agent that would populate them, one content deliverable, and the audit that scopes the rest. The
boundary against `P1`'s reporting work is stated below, because the phase's acceptance requires it.

## The boundary against `PLAN-029`'s `G03`

`P1`'s `G03` is idea and backlog **reporting** — what gets reported and whether a given report is
wanted. It lands in `phase-idg-08`, whose scope includes ruling "on `000042`: whether a generated
ideas-and-backlog HTML page is still wanted now that `IdeaExplorerRegion` and `BacklogExplorerRegion`
both ship in the workbench."

`P9` is the **supply**: the template families, components and palettes any generated page is
assembled from.

**Neither owns the other, and the relationship runs one way.** If `phase-idg-08` rules that a
generated ideas-and-backlog page is wanted, that page is built from `P9`'s assets rather than emitting
bespoke markup — which is `000084`'s composability point applied to a real consumer. If it rules the
page is not wanted, `P9` is unaffected, because its assets serve the five pages that already exist.

The failure this boundary prevents: `P9` sizing a phase to build an ideas-and-backlog page, and
`phase-idg-08` separately ruling on whether that page should exist. `R12` makes the boundary
checkable.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | Every requirement in the pre-build HTML plans carries a disposition: accomplished, open, superseded, or retired. | Read the audit for one disposition per requirement across `PLAN-003`'s six child plans. A requirement with no disposition is a defect; the audit's value is being total. |
| R02 | Each of the ten `queued` `phase-html-*` phases is dispositioned, and any judged superseded or retired is changed in `backlog.yaml` rather than left `queued`. | Run `--ready` after the audit and confirm no phase judged obsolete still reports as ready. A disposition recorded in prose while the phase stays `queued` has not landed. |
| R03 | Where a disposition says "accomplished", it names the demo or workbench work that accomplished it. | Read for a named phase, commit or shipped file per accomplished item. "Covered by the workbench" without a reference is an assertion. |
| R04 | The audit produces the scope for the asset-library work, rather than that work being scoped independently. | Confirm the template, component and palette phases cite the audit's findings. This is the phase's own sequencing instruction: `G39` precedes detailed scoping of `G37`. |
| R05 | The template layer is a library that can grow: adding a template requires no change to generation code. | Add a template and generate a page from it without editing a generator. Confirm the existing `atlas` and `overview` families still render byte-identically. |
| R06 | Each template states its population method — deterministic slot-filling, AI adaptation, or both — and the method is machine-readable, not prose. | Read a template's declaration and confirm a generator can dispatch on it. A library where the caller must know which templates are AI-populated has not stated it. |
| R07 | A component library exists whose components are composable into a page without bespoke markup. | Assemble a page from components only and confirm it renders. Confirm at least the components `000084` names — menu bar, hover dialog, toolbar, tooltip, in-page search — exist or are explicitly deferred with a reason. |
| R08 | Components that need script behaviour declare it, and a page using none of them ships no script. | Generate a page from script-free components and confirm the output contains no `<script>`. The generated pages in `_public/` are the precedent for staying static where possible. |
| R09 | A palette library exists where each palette is a named, pre-vetted set of roles, selectable per page or per family. | Apply two different palettes to the same template and confirm both render coherently. Confirm the palette is data, not a code branch. |
| R10 | Each palette states its role set and whether it carries light and dark variants. | Read a palette definition for its roles — background, surface, accent, text, at minimum — and its variant coverage. `000085` leaves both open; this row closes them. |
| R11 | A designer agent extracts a shipped page's token set, type scale, component patterns and interaction shell into a named family following the existing convention. | Run it against one of the five pages in `_public/` and compare the output family against `atlas`'s structure — header comment with provenance and usage, token contract, canonical component markup. |
| R12 | No phase in this programme builds a report page whose existence `phase-idg-08` is ruling on. | Inspect each phase's `deliverables` field, not its prose. A violation appears as a deliverable; the prohibition itself appears in `scope`, so a whole-entry grep flags the rule stating itself and settles nothing. Finding such a deliverable means the boundary was crossed; the page is `P1`'s to decide and `P9`'s only to supply assets for. |
| R13 | A governance atlas page ships in the atlas family, covering the document-code series and allocator, the backlog protocol and claim model, the `GOV` series, and the idea lifecycle and sanctioned writer. | Open the page and confirm all four subjects appear. Confirm it uses `templates/html/atlas-page.html` and `templates/styles/atlas.css` rather than a new family. |

## What each requirement is not

**R01 and R02 are one audit measured twice.** R01 is the thinking; R02 is the consequence landing in
the backlog. An audit that dispositions ten phases in a document and leaves all ten `queued` has
changed nothing a coordinator reads.

**R04 is a sequencing requirement.** It is the phase's own instruction — `G39` before `G37`'s detailed
scoping — made checkable, because the asset libraries are extensions of a pipeline whose current
state the audit establishes.

**R12 is a boundary, not a prohibition on report pages.** `P9` may build page *assets* freely. What it
may not do is decide whether a particular report exists, which is `phase-idg-08`'s ruling.

**R12 is checked against `deliverables`, deliberately.** Running the obvious whole-entry grep over
this programme returns `phase-des-01`, whose scope says *"Do not build or decide on any report page"*
— the rule quoting itself. A check that cannot tell a prohibition from a violation would report a
breach on the one phase that restates the boundary.

**R13 is content, not automation.** The atlas family exists and works; this row asks for a page built
from it, which is why `000093` is one phase and independent of the rest.
