---
schema_version: 1
id: doc-prompt-literature-review-kickoff
code: PROMPT-031
title: Literature-review campaign kick-off record — the pinned starting state, the owner's per-campaign deltas, and the kick-off paragraph
kind: prompt
status: active
owner: repository-owner
created: '2026-09-12'
updated: '2026-09-14'
systems:
- sys-research
- sys-backlog
depends_on:
- doc-prompt-literature-review-coordinator
- doc-lit-campaign
- doc-research-protocol
---

# Literature-review campaign kick-off record

The kick-off record for the adversarial D-System literature-review campaign
([GOV-009](../08-governance/GOV-009-research-protocol.md) stage 8). It pins the state the
campaign starts from, carries the owner's per-campaign rulings, and ends with the kick-off
paragraph.

**Precedence: where this record and the coordinator prompt
([PROMPT-030](PROMPT-030-literature-review-coordinator.md)) differ, this record wins.** The
coordinator prompt is generic and reusable across every session; this record is specific to this
campaign and is the later, narrower instrument.

## Pinned starting state (2026-09-12)

- **Repository**: branch `dev` at `74fbeae`, clean tree, governance exits 0 (19 systems, 181
  documents, 129 backlog phases), 578 tests passing.
- **The campaign branch does not exist yet.** `phase-lit-01`'s kickoff creates
  `agent/lit-campaign`; every phase commits to that one branch thereafter.
- **Queue**: `phase-lit-01` is in `next_up`, in **last** position — behind `phase-wb-07`,
  `phase-port-02` and `phase-ses-01`. It is promoted, not prioritised: ratified decision 4 gives
  demo work precedence, and `phase-wb-07` is demo work.
- **Peer claims**: one active claim, `phase-demo-07` (`agent-demo-glossary`), locking `sys-brain`
  and `sys-portfolio`. No overlap with the campaign's `sys-research`. One of three claim slots in
  use.
- **Phase state**: all seven `phase-lit-01`–`phase-lit-07` are `queued`, each declaring
  `systems: [sys-research]`, dependency-chained so Pass 1 → 2 → 3 → 4 is forced.
- **The frozen baseline's identity**, as the campaign must find it:
  - last modified by commit `b2b564b` (2026-09-09) — nothing has touched it since;
  - `research/pre-literature-baseline.md` = blob `635bcfa`;
  - `research/pre-literature-hypotheses.yaml` = blob `a53ecdb`;
  - `research/adversarial-codebase-review/` — the twelve-file audit, unmodified.
  A baseline whose identity differs from this is a blocking finding, not something to restore.
- **Deadline**: none. The live demo is the week of 2026-09-15 and the campaign is not
  demo-critical; it runs alongside demo prep and yields to it (ratified decision 4). Runway is
  seven sessions, range six to eight.
- **No campaign deliverable exists yet.** `research/literature-review/` holds only the
  methodology (`CLAUDE.md`) and the handoff note; `00_search_ledger.csv` and everything numbered
  `01`–`13` are created by the campaign itself.

## The owner's per-campaign deltas (ratified 2026-09-12)

These four are this campaign's deltas on the standing rules. Prompt A's seven ratified decisions
([PROMPT-027](PROMPT-027-literature-review-pre-plan-package.md)) remain in force and are not
restated here.

1. **Gate check-in cadence: one pause, before synthesis.** The evidence phases run through
   without waiting. The campaign pauses once, after `phase-lit-06`'s gate and before
   `phase-lit-07` starts. `phase-lit-07` may not start until this record carries a dated entry of
   the form `pre-synthesis check-in held: <date>, ruling: proceed` — appended to the section at
   the end of this document, which is empty by construction until the check-in happens. That
   pause is also the first of the two owner integrations of `agent/lit-campaign` into `dev`.

   A critical issue outside that gate — a collision that falsifies scope, a methodology defect
   invalidating collected evidence — gets `GOV-009`'s dual adversarial review first, and pauses
   the campaign only if it survives that review unresolved.

2. **Descope authority: rung 1 is autonomous; rungs 2–5 are not.** The coordinator may take
   **rung 1** (fold near-synonym domains into their parents for Pass 1 breadth, with that rung's
   gate re-parameterization) on its own judgment if Pass 1 overruns, and reports it afterward in
   the session record. Every other rung needs the owner's explicit direction. This is the stated
   exception `GOV-009` permits a kick-off record to grant; it does not extend to any other rung,
   and a rung taken without its gate re-parameterization is a defect, not a descope.

3. **The single Opus escalation is the coordinator's to spend, documented.** `GOV-009` allows at
   most one Opus escalation per campaign, never pre-assigned. The coordinator may spend that one
   on its own judgment where a judgment-heavy step genuinely needs it, and must name it in the
   session record — which work item, why, and what it changed. A second escalation needs the
   owner.

4. **Start: `phase-lit-01` is promoted to `next_up` now**, in last position (see the pinned state
   above). The campaign begins whenever a session picks it up; nothing further is needed from the
   owner to start it.

## What this record deliberately does not do

It does not restate the content methodology, the phase graph, the delegation-pack sections or the
completion gate. Those live in the campaign plan
([PLAN-023](../01-plans/PLAN-023-literature-review-campaign/PLAN-023-overview.md)), the
delegation pack ([PROMPT-029](PROMPT-029-literature-review-delegation-pack.md)) and the
coordinator prompt. A kick-off record that duplicates them becomes a second source of truth to
keep consistent, which is the failure `GOV-009`'s precedence rule exists to contain.

## Pre-synthesis check-in

The coordinator appends the dated ruling here when the check-in is held, and `LIT-07 K` reads
this section to decide whether synthesis may start. A description of the planned pause is not a
held check-in.

```text
pre-synthesis check-in held: 2026-09-14, ruling: proceed
```

Held after `phase-lit-06`'s gate, by the owner, in the session recorded as
[SESS-2026-09-14-01](../03-sessions/SESS-2026-09-14-01-literature-review-pass-3.md). Eight
rulings, anchored on idea `000230`. They are recorded here because this record wins over the
coordinator prompt; where a ruling changes how a gate or a dispatch behaves it was also written
into the document that gate or dispatch actually reads, as noted.

1. **The nineteen critical-collision flags stand.** Six reviewers re-derived a score one level
   lower and concluded no trigger fires; those are recorded as `disputed` in `second_review` and
   in `05_critical_collisions.md`, and no score, `critical_collision` or `hypotheses_challenged`
   value was changed. `LIT-06 G`'s measurement 2 therefore needs no re-run. Idea `000229`.
2. **A patent's whole published disclosure is prior art** — specification and claims together.
   Written into `PLAN-023.03`. This rejects the claims-only re-derivation applied to
   `us20250165226a1-ai-digital-thread-patent` during `phase-lit-06` as using the wrong standard;
   that row's architecture overlap of 4 and its flag both stand. Idea `000227`.
3. **"Adjacent" in the fourth flag trigger means contiguous** — four consecutive stages, no gap.
   Written into `PLAN-023.03`. Idea `000228`.
4. **`LIT-07 X1` reconciles `06_hypothesis_tests.md` against the corrected matrix before writing
   anything else**, as its item 0. Written into `PROMPT-029`. H11's and H1's named challengers
   are known to need it. Idea `000225`.
5. **No row is re-read.** The 42 factual corrections already landed and the scores stand under
   ruling 1. Instead `Block D` now requires a deep-extraction dispatch to declare what it
   actually read and what it could have read but did not. Written into `PROMPT-029`. Idea
   `000226`.
6. **The five recommended narrowings of `hypotheses_challenged` are recorded, not applied** —
   consistent with ruling 1. `LIT-07 X1` weighs them when it reconciles 06.
7. **Rulings that change behaviour are written into the documents that govern it**, not only
   here, because `LIT-07 G` reads the evidence contract and the dispatches read the pack.
8. **Saturation is not demonstrated and `phase-lit-07` must not claim it.** `LIT-06 G` measured
   a 20.0% duplicate rate (44/220), recomputed independently and reproduced exactly. Four
   results in five were new. The methodology's stop condition is that additional searches
   "mostly yield duplicates or clearly adjacent work"; 20% is not that. `LIT-07 G`'s saturation
   measurement reports the trend and must not assert the condition holds.

Not a ruling, recorded because it bears on the runway: the campaign has used six sessions of a
seven-session estimate, against an owner-accepted range of six to eight. `phase-lit-07` is the
seventh.

---

## The kick-off paragraph

Paste this into a fresh terminal session to run one session of the campaign. It is the one
artifact `GOV-009` never governs and never tracks; this record is its durable copy.

> Run one execution session of the D-System adversarial literature-review campaign. Read
> `AGENTS.md`, then `docs/08-governance/GOV-006-conversation-guidelines.md`, then the kick-off
> record `docs/02-prompts/PROMPT-031-literature-review-kickoff.md` — it carries the pinned
> starting state and the owner's four per-campaign deltas, and it wins wherever it differs from
> the coordinator prompt — and then the coordinator prompt
> `docs/02-prompts/PROMPT-030-literature-review-coordinator.md` in full.
>
> You are the coordinator. Run the preflight and record the real output. Determine the current
> phase from `docs/09-backlog/backlog.yaml` — the first `queued` `phase-lit-*` whose dependencies
> are complete, or the `active` one if this is a resume. Dispatch that phase's sections from the
> delegation pack `docs/02-prompts/PROMPT-029-literature-review-delegation-pack.md` verbatim, one
> at a time, assembled per its dispatch rules, in the order the pack lists them.
>
> You coordinate and verify. You do not search, read sources, score collisions, write
> deliverables or findings, author prompts, or fix a worker's output. A missing prompt is a
> blocking finding for the owner. A failing gate is a result to record, not a retry loop. The
> campaign works to support H0 — that D-System is primarily a recombination of known ideas — and
> no agent may mutate a hypothesis or rewrite scope to avoid a collision.
>
> Stop at the phase boundary: checkpoint, write the session record with the gate measurements and
> spend posture, state the resume state, and leave the tree clean with governance exiting 0. Do
> not mark the phase complete and do not integrate into `dev` — both are the owner's.
