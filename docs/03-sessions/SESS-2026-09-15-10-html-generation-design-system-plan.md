---
schema_version: 1
id: doc-session-html-generation-design-system-plan
code: SESS-2026-09-15-10
title: Finalize the HTML generation and design system plan (P9)
kind: session
status: active
owner: repository-owner
created: '2026-09-15'
updated: '2026-09-15'
systems: [sys-html]
depends_on: [doc-html-generation-design-system]
---

# Finalize the HTML generation and design system plan (P9)

## Phase

`phase-prog-11` — Finalize the HTML generation and design system plan (P9).

Ninth phase of the unattended overnight batch run by `agent-night`.

## Verification

`uv run python -m src.governance`

```
Governance OK: 27 systems, 245 documents, 25 memories, 254 backlog phases
```

Exit 0. Documents 243 → 245: `REQ-021`, and this record. Phases 248 → 254 for the six `phase-des-*`
phases. An earlier run during the session reported `244 documents`, before this record existed.

`uv run python -m src.governance --ready`

```
| phase-des-01 | Audit the pre-build HTML plans and disposition every phase-html-* phase | — | 2 | ready | — | phase-prog-11 |
| phase-des-02 | Build the governance atlas page in the atlas family | — | 3 | ready | — | phase-prog-11 |
```

Two of six are `ready` — the two declaring no prerequisites. The other four wait on the audit.

`uv run pytest`

```
580 passed, 2 warnings
```

Coverage was checked mechanically rather than by reading, after `phase-prog-10` found a row that read
as uncovered to a grep: all thirteen `REQ-021` rows are cited by at least one phase, and all six
phases cite at least one row.

### What was checked before sizing

```
$ python3 -c "... phase-html-* status counts"
{'queued': 10}

$ grep -n "^status:" docs/01-plans/PLAN-003-dynamic-html-generation/PLAN-003-overview.md
7:status: approved

$ ls templates/html/ templates/styles/
atlas-components.html  atlas-page.html  atlas.css
overview-bar.html  overview-page.html  overview.css
overview-concept-row.html  overview-concepts-panel.html
overview-metrics-section.html  overview-system-row.html
overview-systems-panel.html  overview-term-row.html

$ ls _public/
d-system-architecture.html  prompt-pack-protocol.html  research-protocol.html
skills-and-agents-lexicon.html  overview/  images/
```

Ten `phase-html-*` phases `queued` and none complete, against an `approved` `PLAN-003` with six child
plans, all predating the demo and the workbench. **Two** template families exist, not one, so the
convention `000092`'s agent would follow is demonstrated twice. **Five** shipped pages exist for it to
scan. `000093`'s page has a working companion in `_public/prompt-pack-protocol.html`.

## Acceptance

- **`PLAN-036` carries no placeholder banner and states a chosen design.** Met. Banner removed,
  `status` `draft` → `active`, five numbered rulings plus the verification and boundary sections.
- **A requirement document exists for P9 and every row maps to at least one phase.** Met. `REQ-021`
  carries thirteen rows; the mapping is total in both directions, checked by grep against the backlog
  rather than by reading the plan's own table.
- **The boundary against `PLAN-029`'s `G03` reporting work is stated explicitly.** Met. `PLAN-036`
  carries a dedicated section, and `R12` gives it somewhere to fail: no phase here may carry a
  deliverable that builds a report page whose existence `phase-idg-08` is ruling on. The boundary is
  stated as one-way — `P9` supplies assets, `G03` decides whether a given report exists — and two
  phases cite `R12`. It is settled by a reviewer reading the `deliverables` field; nothing in
  `src/governance` enforces it, and the requirement now says so.
- **`phase-prog-11` is removed from `next_up` in the same change that completes it.** Met, in the
  same commit that registers the track.

## Backlog

`phase-prog-11` is `status: complete`, `agent: agent-night`,
`session: doc-session-html-generation-design-system-plan`. Completion evidence is `PLAN-036`,
`REQ-021`, `docs/09-backlog/README.md` and this record. Written under the owner's advance authority
for this batch, after the read-only independent review below confirmed all four conditions.

Six phases added under `phase-des-*`, all `status: queued`, none claimed.

## Review

A fresh non-fork sub-agent with read-only tools reviewed `dev...agent/phase-prog-11`, told that
earlier phases in this batch had found stale premises and one fabricated verification result, and
asked to check every factual claim with a command that distinguishes the cases — in both directions.

```
$ uv run python -m src.governance
Governance OK: 27 systems, 245 documents, 25 memories, 254 backlog phases
EXIT: 0

$ uv run pytest  →  580 passed, 2 warnings
```

**All four conditions Met.** Coverage verified programmatically "not by reading the plan's own table".
The `next_up` check: "the *only* line removed anywhere in `backlog.yaml` across the whole diff is
`- phase-prog-11`". Catalog regenerated and diffed byte-for-byte against the committed file —
identical.

**Every factual claim was re-checked and held**, including ones this phase asserted from a directory
listing: the ten `queued` `phase-html-*` phases (`Counter({'queued': 10})`), `PLAN-003`'s `approved`
status and six child plans, the two template families, and `_public/`'s five pages — where the
reviewer was more precise than this phase had been: it counted with `find _public -name "*.html"`,
noting "the `.zip` and `images/` in the raw `ls` are correctly not counted as pages".

It also read `atlas-page.html`, `atlas.css` and `atlas-components.html` directly to confirm the
convention `R11` checks against is real: "all three convention elements the plan claims are real —
header comment with provenance/usage…, a token contract…, and canonical component markup with a
documented class contract."

**The boundary held under attack, and the reviewer found corroboration this phase had not.** It
grepped all six phases and traced the only two matches, then went further:

> "I traced this to idea `000093`'s own body and an existing 2026-09-11 triage annotation that
> pre-dates this phase and explicitly separates it from `000042`: *'000042 … about HTML page
> generation from governed data, but for a different topic (idea/backlog prioritization rather than
> governance system documentation).'* The boundary is grounded in prior evidence, not invented here."

That annotation is now cited in `PLAN-036`.

**One minor finding, and it was a fair hit on my wording.**

> "R12's verification method … is a manual/judgment check, not anything wired into `src.governance` —
> 'R12 makes it checkable' overstates what's mechanically enforced (nothing greps this automatically
> today)."

Correct. **Fixed** in `REQ-021`, `PLAN-036` and the backlog README: all three now say the boundary is
settled by a reviewer reading the `deliverables` field, and state plainly that nothing in
`src/governance` enforces it. The reviewer noted this is house style for most rows in the document;
the fix is to stop claiming more than that.

**The gating override was judged sound, with a better argument than the one I gave.**

> "`PLAN-003` describes a FastAPI/React 'dynamic' generation pipeline…, while the two template
> families that actually exist and ship five pages today are static HTML/CSS/vanilla-JS, built
> through a different mechanism entirely. Gating new library work on a plan describing an
> apparently-unbuilt, possibly-superseded pipeline would either stall the work indefinitely or gate
> it on something irrelevant to what actually exists."

I verified that before adopting it — four of `PLAN-003`'s six child plans reference FastAPI, React or
npm — and added it to design decision 1. It is a stronger reason than "the audit may retire it",
because it holds even if the audit finds `PLAN-003` entirely intact.

**The second minor finding**, `phase-des-04`'s possible terminal duplication, the reviewer noted was
"already surfaced by the phase, not a gap I'm introducing".

## Decisions

**`G37` is gated on the audit, not on `PLAN-003`.** The partition gates the asset libraries on
`PLAN-003`. But `PLAN-003` is precisely what `G39` audits, and the audit may find parts of it
accomplished, superseded or retired. Gating the libraries on a document whose standing is the thing
under examination would hold them behind something that might not survive. So `phase-des-03`, `-04`
and `-05` depend on `phase-des-01`, and `R04` requires them to cite its findings — making the
sequencing a real dependency rather than a preference.

**The audit must change the backlog, not just describe it.** `R02` is what gives `G39` teeth: ten
phases sit `queued` and `--ready` offers them today. A disposition written in a document while all ten
stay `queued` has changed nothing a coordinator reads.

**`R03` guards the opposite error to the one this batch kept finding.** Six times tonight a documented
blocker dissolved on inspection. The same carelessness in the other direction — declaring a phase
"accomplished by the workbench" without naming what accomplished it — would retire work that is still
needed. `R03` requires a named phase, commit or shipped file.

**The three asset layers are three phases because each carries a different open question.** How a
template declares its population method; which components earn their place and which need script;
what a palette's role set is and whether it carries variants. `000085` leaves the last two explicitly
open. Bundling them would produce one phase with three unresolved design questions.

**`G38` is claimable today.** `000093` needs the atlas family, which exists. The owner's deferral of
2026-09-10 was about sequencing attention — "protocol + case studies for now" — not a missing
prerequisite.

## Corrections

**`R12` claimed more enforcement than exists.** The requirement said the boundary was "checkable",
which reads as mechanically enforced; nothing in `src/governance` greps for it, and it is settled by
a reviewer reading one field. Found by the review. Corrected in all three places the claim appeared.

The self-test that preceded it is worth recording too: running `R12`'s own check as first written
returned `phase-des-01`, whose scope says *"Do not build or decide on any report page"* — the rule
quoting itself. A check that cannot tell a prohibition from a violation reports a breach on the one
phase restating the boundary. `R12` now inspects `deliverables`, where a violation would appear. That
is the same defect shape as `phase-prog-10`'s directory check, caught this time before review because
that phase taught the habit of running my own checks against my own work. The two habits that produced corrections earlier tonight were applied up front
instead: every factual claim was checked with a command whose output distinguishes the cases, and
requirement coverage was verified by grep rather than by reading.

## Unresolved

**Whether `phase-des-04`'s embedded terminal duplicates the workbench's.** `000084` names an embedded
terminal among its components, and `phase-wb-03` shipped a terminal panel. Options: rule it out here,
or flag it. **Flagged it** in the phase's `next_action`, because whether a *generated static page*
needs a terminal component is a different question from what an interactive panel app needs, and
answering it properly requires reading what `phase-wb-03` built — which is `phase-des-01`'s audit
territory rather than this phase's.

**Whether the audit should be allowed to retire `PLAN-003` outright.** `phase-des-01` may conclude the
plan is substantially superseded. Options: forbid that, or permit it with an ADR. **Permitted it with
a conditional ADR requirement**, because an audit that cannot reach its own most likely conclusion is
not an audit. The ADR requirement is what keeps a retirement traceable.

**Whether `P9` should run before or after `P1`.** `phase-idg-08` rules on the ideas-and-backlog page;
if it rules the page is wanted, `P9`'s assets are what it would be built from. Options: add an
ordering constraint, or leave them independent. **Left them independent**, because the boundary is
one-way: `P9`'s assets serve five pages that already exist, so nothing here waits on that ruling.
Only a hypothetical sixth page would.

## Left undone

**All six phases.** This phase finalizes a plan and builds nothing.

**The ten `queued` `phase-html-*` phases are untouched.** `phase-des-01` dispositions them; this phase
only establishes that none is complete and that all ten predate the builds that may have accomplished
them. Changing another plan's phases was not this phase's to do.

**`PLAN-003`'s status is unchanged at `approved`.** Whether that is still right is the audit's
question.
