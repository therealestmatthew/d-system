---
schema_version: 1
id: doc-portable-framework-document-templates
code: PLAN-040
title: Portable framework document template and schema family
kind: plan
status: draft
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-19'
systems: [sys-fw-templates]
depends_on: [doc-portable-framework-document-templates-requirements, doc-governance-protocol, doc-document-code-protocol]
---

# Portable framework document template and schema family

## Summary

Six of the thirteen ideas captured 2026-09-19 about a portable multi-developer agentic framework
(`000269`, `000270`, `000271`, `000277`, `000278`, `000279`, all linked to the batch anchor `000281`)
each name one document shape a new repository would need before it could run d-system's
plan-before-phase-before-claim workflow on its own: a governance-rule document, a protocol document,
a backlog phase, a requirement, a plan, a session record, and GitHub issue/PR templates.

This plan produces that family as a matched set of Markdown templates and JSON Schemas, so a document
written from a template can be checked against its schema rather than trusted by eye. It does not
build the starter kit `000281` describes, write the workflow/governance narrative prose the
`docs/00-working/framework/README.md` draft outlines, or extract any content from d-system's own
history — that is `PLAN-041`'s scope.

[REQ-024](../06-requirements/REQ-024-portable-framework-document-templates.md) states the observable
requirements this plan satisfies.

## Raw material and what changes

`docs/00-working/framework/05-schemas/` already holds five drafted templates
(`requirement.template.md`, `plan.template.md`, `session-record.template.md`,
`github-issue-idea.template.md`, `github-pr.template.md`) and no schemas. They were written before
the thirteen ideas existed and are ungoverned scratch per
[ADR-010](../04-decisions/ADR-010-idea-staging.md) — raw input, not an authority this plan must
preserve. Where a draft's shape does not hold up against a requirement below, this plan overrides it.

Nothing this plan produces is a governed d-system document. Every template and schema is a deliverable
*for a future repository's own governance engine* — the shape a document like this one's kind should
take there, not an addition to `docs/document.schema.json` here. That is also why the deliverables
stay under the existing ungoverned `docs/00-working/framework/` staging directory rather than a new
governed location: they are not decisions, protocols or plans about d-system, and inventing a new
governed kind to hold them would be exactly the pressure `ADR-010` exists to relieve.

## The workstream question (`000272`)

`000272` asks whether a "workstream" layer — one per developer or machine, holding several plans,
each plan holding phases, cross-referencing many requirements — belongs in this template family.

**Verdict: no. The layer is not adopted.**

The concurrency check this framework exists to reproduce (`ADR-003`, mirrored for a new repository)
locks on exactly two declarations a phase makes: `systems` and `deliverables` paths, plus the
`depends_on` chain between phases. Nothing about *who* owns a plan, or which other plans share an
informal track with it, changes what that check does. A workstream as `000272` describes it would be
a grouping label sitting above the lock-relevant declarations, not a new declaration the lock reads —
which means it cannot express anything about concurrency that `systems` does not already express more
precisely, and a phase author who wanted the workstream label to *mean* something for locking would
have to duplicate its content into `systems` anyway.

What already covers the need `000272` names:

- **A `systems.yaml` `domain`** already groups components by area (`data`, `governance`,
  `application`, `delivery`, `memory`) — the same axis a UI/agent-orchestration/backend split would
  use. `sys-fw-templates` and the three `sys-fw-analysis-*` systems this plan and `PLAN-041` register
  both carry `domain: governance` for exactly this reason: the domain is the coarse grouping, the
  system ID is the lock-relevant one.
- **A plan's `systems` field**, read against `systems.yaml`, already tells a reader which area of the
  repository a plan belongs to, and by extension which developer or machine would naturally own it in
  a multi-developer setting. `depends_on` between plans already expresses containment and prerequisite
  order without a new field.
- **`000280`** — adapting the claim system for developers on separate machines — is the idea that
  would actually change what the lock reads, if anything does. It is not ready to promote (see below),
  and this plan does not pre-empt its answer by inventing a layer above the lock that `000280`'s
  eventual decision would then have to account for.

If a real multi-developer deployment later shows that `systems`/`domain` cannot express the grouping
it needs, that is a fact to bring back to this decision — not a reason to add the layer speculatively
now. Recording the reasoning here means the next reader does not have to re-derive it: three ideas
back-referenced the workstream question (`000280` cites the shared-checkout assumption it inherits
from `000272`'s framing); this section is the settled answer they can point at.

### Amendment, 2026-09-19: ownership is a different question (`000288`)

The owner ruled on this the same day, for a hackathon repository built for five developers on
separate machines (idea `000288`, recorded because the reasoning behind it exists nowhere else).
**This supersedes the verdict above, not the reasoning that produced it.**

The locking argument two sections up is correct and stays correct: the concurrency check reads
`systems`, `deliverables` and `depends_on`, nothing else, and a workstream label carries no
information that check does not already get more precisely from `systems`/`domain`. Read as an
answer to "does a workstream change what the lock does," the verdict was and remains **no**.

That is not the question the owner was asking. A workstream, on the owner's ruling, is not a
locking primitive at all — it is an **ownership** unit. It names who owns what and which paths that
ownership covers: the user interface, the product's own agent orchestration, the deterministic
backend, and so on, one per developer, each running a single agent rather than orchestrating many.
Ownership and locking are different questions because they operate at different rates and different
scopes. The lock arbitrates concurrent phases within one shared checkout, rechecked on every claim.
A workstream is claimed once per developer, rarely enough that the git-based race the phase-level
lock exists to prevent almost never fires at this rate — see `000288`'s point that rarity is what
makes a git-based claim viable here. It is the outer of two layers: the inner layer is this
repository's existing single-developer multi-agent claim and coordination design, kept as is; the
outer layer coordinates *between* developers, and the two are designed to work in conjunction rather
than one replacing the other.

**A workstream is a source of path declarations, not a competitor to `systems` or `deliverables`.**
It does not sit above a plan the way `000272` originally framed it (a container holding several
plans, cross-referencing many requirements) and it does not add a field the lock reads. Instead, a
developer's workstream claim — a record committed once to a shared file on the integration branch —
declares the paths that developer owns, and those declared paths become the boundary that feeds the
*existing* lock: other developers' plans should not declare `systems`/`deliverables` that fall inside
paths another workstream already claims. The workstream record is upstream of a plan's `systems`
declaration, supplying the ownership fact a plan author consults before writing that declaration; it
is not a new field on the plan or a new thing the concurrency check parses. Whether that record takes
the shape of a new template (`workstream.template.md`/`workstream.schema.json`, as `000272`
originally asked for) or a simpler shared file is downstream design work this amendment does not
settle — it settles only that the concept has a place, as ownership metadata, not as a locking
primitive.

**What does not change.** No document in this template family needs a `workstream` field to
participate in the concurrency check; `sys-fw-templates`'s `domain: governance` grouping and every
other phase's `systems` declaration mean exactly what they meant before this amendment. What changes
is that "no new document kind" is no longer the complete answer to `000272` — the layer above locking
that the original verdict declined to add is a different layer than the ownership layer the owner
asked for on 2026-09-19, and the latter is accepted.

## Design: five document shapes, one shared system

| Shape | Ideas | Deliverables (under `docs/00-working/framework/05-schemas/`) |
|---|---|---|
| Governance + protocol | `000269`, `000270` | `governance.template.md`, `governance.schema.json`, `protocol.template.md`, `protocol.schema.json` |
| Phase | `000271` | `phase.template.md`, `phase.schema.json` |
| Requirement + plan | `000278` | `requirement.schema.json`, `plan.schema.json` (existing templates reconciled against them) |
| Session record | `000277` | `session-record.schema.json` (existing template reconciled against it) |
| GitHub issue + PR | `000279` | additional issue-type templates (defect, at minimum), `github-pr.template.md` reconciled to carry completion evidence |

All five clusters share one system, `sys-fw-templates`, registered in `systems.yaml`. That is a
deliberate serialization, not the reflexive `sys-governance` habit this batch was asked to avoid
(idea `000253`'s finding on `phase-conc-01..03`): the five shapes have to read as one coherent family
— the same front-matter conventions, the same section-naming discipline, the same relationship
between "what a template requires" and "what its schema enforces" — and that discipline is easiest to
hold by having one phase sequence build all five with the earlier ones as visible precedent, not five
independent authors inventing five vocabularies in parallel. The cost is real: these five phases
cannot run concurrently with each other. The benefit is a template family a new repository can trust
to be internally consistent, which is the actual point of `000281`'s starter kit.

This is unlike `PLAN-041`'s three analysis phases, which share no such coherence requirement and are
registered on three separate systems specifically so they *can* run in parallel — see that plan's
design section for the contrasting case.

## Phasing

Proposed phases are recorded in `_working/framework-phases-proposed.md` for the owner's review before
they enter `docs/09-backlog/backlog.yaml` — this plan does not edit the backlog directly. In outline:

1. `phase-fwt-01` — governance and protocol templates/schemas (`000269`, `000270`).
2. `phase-fwt-02` — phase template/schema (`000271`).
3. `phase-fwt-03` — requirement and plan schemas (`000278`).
4. `phase-fwt-04` — session-record schema (`000277`).
5. `phase-fwt-05` — GitHub issue/PR templates (`000279`).

Each phase's `verification` includes a small `jsonschema`-based check (already a project dependency)
validating a filled example against its schema and a deliberately incomplete example against the same
schema, per REQ-024's per-requirement verification methods.

## Out of scope

- `000281`'s starter kit packaging — depends on this plan's and `PLAN-041`'s deliverables existing.
- `000273`'s master HTML document — depends on framework content that does not exist yet; not ready
  to promote (see the idea disposition below).
- `000280`'s multi-machine claim adaptation — a design decision this plan does not need and should
  not pre-empt; not ready to promote (see below).
- Any change to d-system's own `src/governance/`, `schemas/document.schema.json` or
  `docs/09-backlog/backlog.yaml` validator.

## Ideas not promoted in this batch

- **`000272`** (workstream layer) — answered above rather than promoted; the original answer was "no
  new document kind" for locking purposes, and that holds. The owner's 2026-09-19 ruling (`000288`,
  see the amendment above) qualifies the conclusion: a workstream is accepted as an ownership unit
  that feeds the lock with path declarations, not as a locking primitive itself. Recorded as a design
  decision in this plan, amended in place, rather than left as an open idea.
- **`000273`** (master HTML document) — not ready. Its own text says it links and summarizes
  "workflows, governance, templates, schemas, and analysis findings **once available**"; none of
  those exist yet outside two ungoverned drafts. Promoting it now would produce a document about
  content that does not exist, which is the 2026-09-06 failure mode `ADR-010` records. Revisit once
  `PLAN-040` and `PLAN-041` have shipped deliverables to summarize.
- **`000280`** (multi-machine claim adaptation) — not ready. It proposes a real change to the claim
  model itself (PR-gated integration, a shared board, a documented race-recovery path) and explicitly
  offers several unresolved candidate approaches rather than one. It also sits in the same territory
  as the active concurrency track (`phase-conc-01`/`02`/`03`, held by `agent-conc` on `dev` as of this
  writing) — planning it now risks declaring `systems` or `deliverables` that collide with that live
  claim before either side has seen the other's diff. Revisit once the concurrency track's current
  phases land and the owner has a chance to pick one candidate approach.
