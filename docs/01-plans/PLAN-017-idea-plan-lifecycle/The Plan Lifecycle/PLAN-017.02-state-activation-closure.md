---
schema_version: 1
id: doc-idea-plan-plan-lifecycle
code: PLAN-017.02
title: Plan state consistency, activation and closure
kind: plan
status: draft
owner: repository-owner
created: '2026-09-06'
updated: '2026-09-06'
systems: [sys-governance, sys-backlog]
depends_on: [doc-idea-plan-lifecycle-requirements]
parent: doc-idea-plan-lifecycle
---

# Plan state consistency, activation and closure

## What we know

The validator already rejects open plans without noncancelled phases, unfinished work attached to
closed plans, invalid kind/status combinations, and complete plans lacking existing evidence files.
The six HTML children have 3/3/2/3/1/2 attributed phases; no migration for zero-phase children exists.
The baseline four plans with completed work under draft/approved are reliability follow-up (PLAN-004),
confidentiality sweep (PLAN-006), capture build (PLAN-009), and idea record system (PLAN-016).
These were pre-task measurements; future repair must rescan rather than freeze that list.

The owner confirmed phase-derived consistency and at least one phase for every plan. The current
brief additionally fixes activation before work and the asymmetry that active/all-complete may remain
in acceptance review while complete/unfinished fails. Approval and meaningful closure remain human
judgments. Plan metadata records current state, not a permanent event history.

## What we propose

### Attribution and exhaustive severity matrix

`phases(P)` is the set of backlog items whose `plan` **or** `sources` names P's document ID, counted
once. No inferred ancestor expansion: parent and affected children are explicitly listed. A phase's
sources that are requirements/ADRs are dependencies/context, not plans to activate.

Classify distributions in the following disjoint, exhaustive order:

| Class | Definition |
|---|---|
| Z | No attributed phases |
| X | Nonempty, all cancelled |
| A | Any active phase, regardless of the others |
| U | No active or complete; at least one queued/blocked/deferred, cancelled optional |
| P | No active; at least one complete plus queued/blocked/deferred, cancelled optional |
| C | Nonempty, all complete |
| M | Only complete/cancelled, at least one of each |

| Stored plan status | Z | X | U | A | P | C | M |
|---|---|---|---|---|---|---|---|
| draft | fail | fail | ok | fail | fail | fail | fail |
| approved | fail | fail | ok | fail | fail | fail | fail |
| active | fail | fail | ok | ok | ok | ok | warn |
| accepted | fail | fail | fail | fail | fail | fail | fail |
| complete | fail | fail | fail | fail | fail | ok | warn |
| deprecated | fail | ok | fail | fail | fail | ok | ok |
| superseded | fail | ok | fail | fail | fail | ok | ok |

`accepted` is included for completeness of the global schema enum but is invalid for kind plan.
For retired plans, all-cancelled phases satisfy historical existence; for open plans, preserve the
stronger current rule requiring a noncancelled phase. Always report stored status, counts by phase
status, distribution, severity, and reason, including every ok result. An active/C plan reports
that phase work finished and acceptance review remains; it is not a warning and never auto-closes.
Avoid duplicate per-phase and per-plan diagnostics for the same closed-plan contradiction.

"Derived" means deriving consistency constraints and closure eligibility. Counts cannot choose
between draft and approved, prove consent, or show that an outcome satisfies intent. Keep explicit
plan metadata and let validation reject contradictions. No automatically assigned approval status.

### Activation before claims and work

Use the existing `.claude/commands/backlog.md`, rather than another execution tool:

1. Orientation reads and reports without activation.
2. Claim/go resolve all plan-valued attribution and check underlying authorization. Reuse explicit
   session authorization where applicable; the text `approved` alone cannot manufacture consent.
3. Before the claim-only commit, record authorized approval where needed and activate the affected
   plans in a separate narrow commit. Regenerate catalog and validate. Record a real dated activation
   in the governed session evidence. A draft awaiting actual implementation approval cannot be
   activated merely because a phase is ready.
4. Commit the ordinary active phase claim, validate it, then begin work. Implementation must never
   precede activation. Preserve existing orient/claim/go invocation boundaries.

This ordering is necessary: the new upstream rule would otherwise reject a claim-only commit under
an approved plan. Update the command, AGENTS.md, GOV-001 and GOV-002 together so their ordering agrees.
The first fix sets the four baseline mislabeled plans active after checking their real work, and
reconciles all additional contradictions found by the fresh inventory in that same change.

### Closure and evidence

All-complete phases trigger acceptance review, not automatic closure. If intent is still unmet, keep
the plan active and write one genuine remediation phase with observable acceptance. If abandoned,
deprecate with rationale and explicitly cancel unfinished phases. Replacement uses existing
supersession metadata, retaining old documents. Do not turn cancellations into fake completions.

The complete/M cell is **warn**, not fail. A plan may finish with some phases cancelled — dropping an
optional phase is an ordinary scope decision, and forcing such a plan to deprecate instead would
convert an honest outcome into a failure record. The warning clears when `completion_evidence` states
why those phases were dropped, which puts the pressure on the explanation rather than on the status.
`GOV-002`'s complete-or-cancelled closure is unchanged, so nothing in force today is reversed.
Complete plans already need nonempty `completion_evidence` paths that exist. Review evidence quality
separately: an empty file is not proof. Deferred phases keep a plan open.

## What is open

- Q-H1: the unruled matrix cells above are recommendations. The zero-phase requirement and stated
  active/C versus complete/unfinished asymmetry are fixed; do not reopen them.
- Q-H2/C10 is decided: complete tolerates cancelled phases and warns until the evidence explains
  them. What remains open is what the check should accept as an explanation — recommend that it only
  verifies the evidence file exists and is non-empty, leaving quality to human review, because a
  validator that grades prose will be gamed by prose. Never silently weaken an original goal to make
  a plan complete; the warning exists to make that visible, not to be argued away.
- Q-H5: amend existing GOV-001/GOV-002, not a second GOV protocol. Q-H6: keep current ADR status and
  supersession checks; the plan/phase matrix does not apply to ADRs.
- Blocked can mean before or after work; metadata alone cannot distinguish. Do not invent a historical
  trigger from that status. The execution command supplies the pre-work guard.
- C16: authoring this architecture is a completed documentation phase under the existing ephemeral
  policy (PLAN-015), which is draft. This exposes another policy-versus-lifecycle contradiction.
  Preserve honest draft proposals now; first repair must include that measured case. Do not fabricate
  implementation approval or add a schema exemption merely to hide it.
- C15: full machine-readable plan history is outside current metadata capability. Future session
  evidence can preserve real activation/closure observations. It cannot reconstruct missing past
  instants, and planned history squash prevents relying on old commits as retained evidence.

Q-H3 and Q-H4 are removed: evidence existence is enforced and the alleged zero-phase migration is false.

## What it touches

`src/governance/backlog.py`, `src/governance/__main__.py`, backlog/governance tests, existing backlog
command, AGENTS.md, GOV-001/GOV-002 and any decision amendment in GOV-003; affected plan headers,
generated catalog and governed session evidence. No event or document schema change is needed for
the first repairs. The complete matrix and cancellation decision may finish in integrated verification.

## How it is verified

R14–R16: parameterize every matrix cell and prove the distribution classifier is disjoint/exhaustive
across combinations of six phase states. Attribute by plan alone, sources alone and both; count once.
Existing HTML children remain covered. Active phase under draft/approved fails, preactivation makes a
claim valid, active/all-complete passes and complete/unfinished fails. Preserve missing/invalid evidence
checks. Review orient, claim and go behavior for consent and pre-work ordering. Run targeted backlog
and governance tests, governance, and post-rebase full pytest.

## Conflicts with other categories

C08/C09 separate approval, status and claim ordering. C10 is resolved in favour of a warning, so
GOV-002 and this matrix now agree rather than conflict. C11: promotion
into a draft plan creates a reference, not approval. C15 limits history claims. C16 names a real
architecture-phase side effect rather than treating the baseline count as timeless. Shared category
coverage never requires one synthetic phase per child; document count and phase count are independent.
