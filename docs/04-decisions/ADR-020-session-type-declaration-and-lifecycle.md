---
schema_version: 1
id: doc-session-type-decisions
code: ADR-020
title: Session type declaration, mid-flight change, and brainstorming's output
kind: adr
status: accepted
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-governance]
depends_on: [doc-session-lifecycle, doc-governance-protocol]
---

# Session type declaration, mid-flight change, and brainstorming's output

## Context

[PLAN-008](../01-plans/PLAN-008-session-lifecycle-protocols.md) (`doc-session-lifecycle`) assigns
its Phase 1 four things to resolve: the taxonomy itself, whether brainstorming produces a governed
artifact, how a session that changes type mid-flight behaves, and whether the type is declared by
the owner, inferred from the claimed phase, or both. The taxonomy and its per-type obligations are
written as [REQ-023](../06-requirements/REQ-023-session-type-taxonomy.md)
(`doc-session-type-taxonomy-requirements`). This document records the three decisions behind it.

Two mechanisms already exist and are not renegotiated here: the checkpoint skill
(`.claude/skills/checkpoint/SKILL.md`, `phase-ses-03`) and the session-close command
(`.claude/commands/session-close.md`, `phase-ses-05`), both built before this phase ran. `GOV-003`'s
2026-09-16 entry ("Coordinator completion replaces owner-invoked /session-close") also stands and is
treated as fixed: a coordinator may complete a phase under the three conditions that entry states.
None of the three decisions below contradicts any of this — each was checked against it before being
written down.

## Decision 1 — Brainstorming produces no governed artifact by default

**Decided:** A brainstorming session's output is never written directly into a REQ, PLAN, ADR or GOV
document. When the session reaches something worth keeping, it is recorded as an idea through
`tools/append_idea.py` — one idea per distinct thought, per `GOV-006`'s "Capture new asks as ideas,
immediately" rule — or carried forward as informal input to a later planning session that does the
governed write-up.

**Why.** `PLAN-008`'s own framing states the trade-off precisely: "if nothing is recorded, the
thinking is lost; if everything is recorded, brainstorming inherits the strictness it exists to
avoid." The idea system (`ADR-010`, `doc-idea-staging`, and the fold/triage machinery `GOV-006`
already governs) exists exactly to hold a thought that is not yet a decision, without the ceremony a
governed document demands. Routing brainstorming's output there uses a mechanism that already exists
rather than inventing a fourth thing brainstorming could produce. Nothing is lost — an idea is
retrievable and triaged — and nothing is prematurely formalized, since an idea carries no code, no
front matter, and no catalog entry.

**Rejected alternative.** A dedicated "brainstorm record" document type. Rejected because it would be
a fifth governed kind solely to hold pre-decision content, duplicating what an idea already does, and
because `PLAN-008` explicitly warns against brainstorming inheriting planning's strictness — a new
governed kind would reintroduce exactly that.

## Decision 2 — A mid-flight type change binds the session to the new type from that point forward; it does not restart the session

**Decided:** A session that changes type — a brainstorm that reaches a decision worth planning, or a
planning session that turns into implementation — keeps its one session record (where one exists) and
is bound by the new type's obligations from the moment of the change onward. It is not required to
retroactively satisfy the new type's "must produce" for work already done under the old type, and it
does not split into two session records.

**Why.** `PLAN-008` names this the common case, not the exception, and required it be "answered
rather than deferred." The alternative — restart on every type change — would make the natural
arc of a working session (think first, then decide, then build) require starting over at each turn,
which is friction with no corresponding benefit: nothing about the checkpoint/session-close contract
(`.claude/skills/checkpoint/SKILL.md`'s "one file per session" rule) requires a session record to
have a single type for its whole life. The universal rules (`REQ-023` R1) already bind the session
throughout regardless of type, so there is no confidentiality or governance gap in letting the type
itself flex.

**Rejected alternative.** Requiring a new session record on every type change. Rejected because it
contradicts `checkpoint`'s existing "one file per session" contract, which this phase treats as a
fixed constraint, and because it would produce session-record fragmentation with no benefit — the
narrative sections `session-close` already writes (`## Decisions`) are precisely where a type change
belongs, as a sentence, not as a reason to fork the record.

## Decision 3 — Type is inferred from the claimed phase by default, and the owner may declare or override it at any point

**Decided:** When a session claims a backlog phase (per `/session-start`), the type is inferred by
default from that phase's own nature — its `deliverables` and the kind of document or code it names.
A phase whose deliverables are exclusively under `docs/0*` paths with no code or config path infers
planning; a phase with code, schema, or config deliverables infers implementation. The owner may
declare a type explicitly at any point, which overrides the inference. A session with no claimed
phase (`AGENTS.md`'s "Owner-directed work with no backlog phase" provision) has no phase to infer
from and must have its type declared.

**Why.** `PLAN-008` poses this as "declared by the owner, inferred from the claimed phase, or both"
— not an either/or. Both mechanisms already exist independently: `/session-start` already reads a
phase's `deliverables` and other fields to orient a session, so inference costs nothing new to
compute; the owner already directs unclaimed sessions explicitly, so declaration is not a new
capability either. Requiring the owner to declare a type on every claimed-phase session would repeat
information the phase entry already carries; refusing to let the owner override the inference would
take away judgement from the one party who is allowed to override anything in this system.

**Rejected alternative.** Inference only, with no owner override. Rejected because a phase's
deliverables are not always a clean signal — a phase might name only a documentation deliverable but
genuinely need brainstorming first — and `AGENTS.md`'s "Do not assume. Ask." rule already establishes
that an agent facing genuine ambiguity should ask rather than guess; a hard-coded inference with no
override would force a wrong guess into the record with no way to correct it.

## Consequences

- `REQ-023`'s R5 and R6 state these three decisions as observable obligations; this document is
  their rationale, not a restatement — `CLAUDE.md`'s own discipline against restating rules in a
  second place applies here too.
- Idea `tools/append_idea.py` becomes the standing destination for brainstorming output; no new tool
  or document kind is introduced.
- `phase-ses-02` (build the opening entry points) can proceed against `REQ-023`'s per-type
  obligations without needing to relitigate the three questions this document answers.
