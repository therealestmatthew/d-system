---
schema_version: 1
id: doc-idea-plan-idea-lifecycle
code: PLAN-017.01
title: Idea capture, triage, resolution and promotion
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-portfolio, sys-governance, sys-backlog]
depends_on: [doc-idea-plan-lifecycle-requirements]
parent: doc-idea-plan-lifecycle
---

# Idea capture, triage, resolution and promotion

## What we know

Capture is a record of the owner's thought, not a deduplication decision. ADR-010 preserves overlap
and leaves interpretation to later triage. Existing statuses are open, triaged, reviewing, promoted
and discarded; nine ordinary transitions are declared in the schema. A discarded idea may revisit
once, returning to reviewing. The supplied audit snapshot has no status transitions to analyze.

The brief requires triaging (L7), supersession as a relationship and discarded state (L6),
many-to-many promotion (L9), terminal annotations (L10), and assessments as annotations (L11).
The transcript export confirms the broader lifecycle goals and L1–L4; the later locks are brief
inputs. PLAN-016 currently omits triaging and the existing triage phase remains unbuilt.

## What we propose

### Capture versus correction

Default to recording each new thought as given. Use an amendment only when the owner identifies an
existing record as mistaken or explicitly requests updating that idea's content. A new judgment,
review finding or effort estimate is an annotation. A related new concept is another idea plus a
relationship. Uncertainty is recorded as a question; it does not block capture. This is a proposed
operating rule, not an automatic semantic classifier. Never turn a link into identity equivalence.

Do not rewrite or merge historical captures. The known corrupted record remains unchanged as this
task directs. Any later historical relationship proposal must preserve original prose/IDs and name
its supporting evidence without manufacturing past timestamps. No historical repair is authorized
by this architecture alone.

### Complete transition contract

Retain all existing transitions for compatibility. Extend the schema table with exactly
`open -> triaging` and `triaging -> triaged`. The initial agent can enter and finish triage; it
cannot move to reviewing, promoted or discarded on its own. Recommend owner-controlled
`triaging -> reviewing` and `triaging -> discarded` for interruption/withdrawal, with the same
writer checks. These two additional transitions remain an explicit choice before the notes phase.

| Event/source | Destination allowed | Actor/process |
|---|---|---|
| created | open | Capture tool |
| status/open | triaging, triaged, reviewing, promoted, discarded | Agent only to triaging/triaged; owner decides later states |
| status/triaging | triaged; reviewing/discarded proposed for owner | Agent completes scouting to triaged |
| status/triaged | reviewing, promoted, discarded | Owner judgment |
| status/reviewing | promoted, discarded | Owner judgment |
| status/promoted | None | Terminal state, still accepts annotations/links/amendments |
| status/discarded | None | Exit only through one legal revisited event |
| revisited/discarded with revisits=0 | reviewing, revisits becomes 1 | Explicit revisit |
| revisited in any other condition | Refuse | Full replay enforces this, not just CLI |

Transitions in this table are a design specification, not a second runtime transition registry.
The JSON schema remains the runtime source read by every consumer. Every status event must match
current `from`; every corrected history must obey the same rules. An interrupted triage stays
triaging. Resuming produces further timestamped findings and completes the same triage, never
silently resetting to open. No triage-in-progress event type, actor registry or scheduler is added.

The existing `phase-idea-02` should be updated before execution to enter triaging, emit typed
annotations and complete at triaged using the sanctioned writer. The delivery child gives the exact
proposed backlog update. Scouting only is not owner approval to promote or discard. Assessment
annotations can be rescored later without replacing an earlier judgment's historical existence.

### Supersession

Store `supersedes` from replacement idea to replaced target. Its inverse is derived. If the target
is an idea being retired, explicitly discard it through a legal status event. A link does not mutate
another idea or a governed document/phase. If the retired idea is revisited once, the relation remains
historical; report a diagnostic that its current state is working while related as superseded.
Do not reject a legal revisit because of graph interpretation. New owner judgment may amend the link.

### Promotion bridge

A new promotion writes a nonempty, duplicate-free array of governed **document codes** in
`promoted_to`. One idea can produce `[PLAN-017, REQ-003]`; two ideas can both name `PLAN-017`.
These are synthetic structural examples, not claims that these documents originated in a logged idea.

Build one resolver from the governance document inventory: code to stable doc ID, kind, status and
path. The reservation register alone is insufficient: a reserved code has no document. Resolve actual
documents, not filenames guessed from code, and keep the public code as the log's stable reference.
The initial recommendation permits plans and requirements (both represent adopted work); broader
kinds and promotion directly to phases remain Q-I2. Ordinary links already address documents/phases.

| Target situation | New promotion/replacement | Existing historical contribution |
|---|---|---|
| Existing permitted kind, draft/approved/active | Accept reference; does not approve or activate target | Resolve normally |
| Existing complete permitted kind | Accept as recording an actual result, using today's timestamp | Resolve normally |
| Missing, reserved-only, retired-only, wrong kind | Refuse before append; imported unresolved effective reference fails validation | Retain raw evidence; missing effective target is an actionable validation error, never auto-delete |
| Deprecated/superseded permitted kind | Refuse new association; propose current successor for owner judgment | Retain resolved edge; diagnostic of target's current state, not historical invalidation |
| Document path renamed with same code/ID | Resolve via inventory | No log edit |

Read existing scalar `promoted_to` as a singleton list without changing raw bytes. Newly written
promotion and amendment replacement values are arrays. An effective promotion has at least one
target. A later genuine additional target is expressed by an amendment replacing that promotion's
whole target array while retaining existing targets unless explicitly withdrawn. It records when
that association became known; it does not pretend the new document existed at the original stamp.
No second promoted status transition or generic promotion link type is introduced.

Derive reverse lookup by inverting effective promotion memberships: document code to contributing
idea IDs and source event positions. Do not add mandatory `from_ideas` to plan metadata or keep a
second editable inverse list. Promotion into a plan does not prove its code shipped; join the target
plan's current state, phase acceptance and evidence for that question.

## What is open

- Q-I2: initial target kinds plans/requirements, or all governed document kinds and phases? Recommend
  plans/requirements for promotion and use typed ordinary links for the larger reference universe.
- Q-I3: reverse index suffices; no extra plan field recommended. Confirm only if a real authoring
  workflow needs a stored backward reference.
- Preserve bypass `open -> triaged` for existing manual capture; agent uses triaging. Confirm the two
  owner interruption transitions before schema implementation.
- Revisit does not reset triage or the graph. Record any owner request for different semantics before
  changing these independent axes.
- Q-I1 is excluded as an enforcement feature. Never fabricate history. Tags/classification questions
  remain deferred with the parent plan's evidence gates, despite the directly recorded tag request.
- A history that needs several simultaneously corrective state amendments is not supported by the
  minimal single-append writer; the event contract records that limit.

## What it touches

Existing idea schema, validating fold, sanctioned writer and idea command; existing triage phase and
agent command; governance document resolver; raw/effective projection; generated idea view. Existing
PLAN-016 wording about triaging must change only when that behavior is implemented. Promotion uses
existing document kinds and codes; it does not change their governance schema.

## How it is verified

R01, R09, R11–R15: synthetic captures remain distinct; corrected prose creates no capture; every old
transition stays legal; interrupted/resumed triage and every revisit refusal are exercised; terminal
notes leave state unchanged. One idea to two targets and two ideas to one both resolve forward and
backward. Missing/reserved/wrong-kind targets fail. Renaming paths and later target retirement do
not erase raw history. Triage cannot promote, and promotion cannot activate a plan. The integrated
phase verifies these contracts together without production idea writes.

## Conflicts with other categories

C05/C06 distinguish lifecycle finality from contributions and graph interpretation. C11/C20 distinguish
new references, legacy scalar shape and historical target retirement. C12/C13 reconcile existing
triage scope with the new schema. C17 preserves identity and capture counts. Plan closure is not idea
promotion, and future full plan-history analysis remains C15 rather than an implied bridge feature.
