---
id: mem-concept-terms-plans-and-work
title: Plans and Work
type: concept
tags: []
systems: [sys-backlog, sys-governance]
source_model: anthropic/claude-sonnet-5
project: d-system
created: 2026-09-07
updated: 2026-09-07
confidence: high
related: [mem-concept-terms-documents-and-governance]
scope: global
---

Grouped definitions per [PROMPT-004](../../docs/02-prompts/PROMPT-004-terminology-and-architecture.md).
Each term: what it is, what it is not, where it is governed.

### Governed plan

A document under `docs/01-plans/` (or `plans/`) describing how the system should work, that outlives
the task that produced it. Not a checklist for one task — a document that would be deleted rather
than rewritten once its subject leaves the repository was never a plan. See
`docs/01-plans/PLAN-015-ephemeral-working-plans.md`.

### Ephemeral plan

A file in `_working/` describing how one task gets done, that dies with it — task detail for a phase
that already exists, not a proposal about how the system should work. Carries no code, no front
matter, and is not scanned by the governance check. See
`docs/01-plans/PLAN-015-ephemeral-working-plans.md`.

### Phase

One entry in `docs/09-backlog/backlog.yaml` (`phase-<track>-NN`) naming one independently verifiable
outcome sized to a single session. Not a governed document itself — it references a governed `plan`
and carries its own schema (`schemas/backlog.schema.json`), separate from `document.schema.json`. See
`docs/08-governance/GOV-002-backlog-protocol.md`.

### Track

The shared prefix grouping phases from one plan or work stream — `phase-rel-*`, `phase-term-*`, and
so on. Not a schema field; it is a naming convention read off the phase ID, glossed in
`docs/09-backlog/README.md`.

### next_up

The catalog-level ordered list of phase IDs that jump the queue — the front of the backlog. Not a
ranking of everything; phases absent from it fall back to priority, then ID. See
`docs/08-governance/GOV-002-backlog-protocol.md`.

### Session budget

The phase field `session_budget`, always exactly `1`. Not an automatic timing guarantee — a review
promise that the phase's scope fits one focused session, enforced by the schema constant rather than
by a clock.

### Next action

The phase field naming the first useful action for the next session, or a precise resume instruction.
Not a summary of the whole phase — it is the single next step, read by whichever agent picks the
phase up next.

### Acceptance

The phase field listing at least two observable conditions that must hold for the phase to be
complete. Not verification — acceptance states *what* must be true; verification states *how* that
gets checked.

### Verification

The phase field listing commands or specific review/experiment checks, run and recorded during
execution. Not a promise of correctness by itself — the governance check confirms the field exists
and is followed by a session record; it does not run the commands for you or judge the output.

### Deliverable

An expected file path named on a phase, which may not exist yet when the phase is claimed. Not
completion evidence — a deliverable is what the phase expects to produce; completion evidence is what
is confirmed to exist, with real results, once the phase is done.

### Completion evidence

The phase fields (`session`, `completion_evidence`, `result`) recorded only at close: a governed
session ID, existing evidence file paths, and an actual-results summary. Not written at claim time,
and never a placeholder — an empty evidence file does not satisfy this field. See
`docs/08-governance/GOV-001-protocol.md`.
