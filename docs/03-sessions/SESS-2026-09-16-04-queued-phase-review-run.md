---
schema_version: 1
id: doc-session-queued-phase-review-run
code: SESS-2026-09-16-04
title: Queued phase review executed across the twenty-three queued phases
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-backlog, sys-governance]
depends_on: [doc-prompt-queued-phase-review-pack, doc-idea-realization-system-plan, doc-irs-orchestrator-design, doc-backlog-decisions]
---

# Queued phase review executed across the twenty-three queued phases

The run of `PROMPT-035`. An unclaimed, owner-directed session acting as a minimal-context
orchestrator: agents read and wrote, the session routed and verified. Twenty-three queued phases
reviewed, critiqued and enhanced; thirty-one owner rulings taken in eight question batches; three
phases outside the frozen scope captured as ideas, triaged, independently re-critiqued and then
corrected on the owner's instruction.

Evidence for every claim below is in `_working/phase-review/` in the primary checkout, copied out of
the worktree before removal because the directory is gitignored and a merge never carries it.

## Scope and mechanics

- Unclaimed — owner-directed work with no backlog phase, so peers held no lock against it.
- Branch `agent/phase-review`, worktree `/code/d-system-worktrees/phase-review`, own venv and DB.
- Preflight in the worktree: `Governance OK: 28 systems, 258 documents, 25 memories, 276 backlog
  phases` and `580 passed`.
- Scope frozen from `next_up`, every entry from `phase-irs-03` onward — 23 phases, all `queued` at
  freeze time. Taken by id, never by position.
- `uv run python -m src.governance --ready` re-run before every pass-2 dispatch. Only
  `phase-lit-07` (`agent-lit`, `sys-research`) was ever active. **No phase was skipped as
  peer-claimed.**

## The passes

**Pass 1** — eight group agents in parallel, read-only, one critique file each. All 23 phases
critiqued; roughly 35 `fix` and 47 `question` findings.

**Pass 2** — eight write agents, strictly one at a time. 21 of 23 phases edited, **zero hunks
outside the frozen scope**. `phase-idg-10` and `phase-idg-11` were deliberately left unedited at
this stage: their fixes needed document codes reserved in `codes.yaml`, outside the original grant.
Committed as `6e23e1d`.

**Pass 3** — one fresh adversarial sweep. **No cross-phase breakage from the enhancements.** One
finding — `phase-idg-12`'s new `phase-dgov-01` prerequisite missing from `next_up` — was *not*
applied, because a `next_up` edit was outside the grant at that point; it became a question instead.
Two earlier questions were resolved on evidence:

- `phase-idg-11` does **not** need an edge onto `phase-idg-10`. `REQ-014` keeps R17 and R18 as
  independent rows and R20 sits on `phase-idg-12`, which already has that edge.
- `phase-irs-13`'s missing edges were not a backlog slip against `PLAN-039` — the plan's own
  coverage table listed `phase-irs-04` only, so the plan needed the same correction.

**Group I** — a ninth, owner-ordered pass-1-equivalent over `phase-agx-09`, `phase-auto-03` and
`phase-auto-04` after those phases' defects were captured as ideas and triaged.

## What the review actually found

- **A schema filename collision.** `phase-irs-04` was scoped to create `schemas/decision.schema.json`,
  already owned by `phase-cap-02`'s entity schema and wired to `sql/001_schema.sql:93-94`.
- **Gate 3 ratification was claimed by three phases at once** — `phase-irs-04`'s `gate` verb,
  `phase-irs-07` and `phase-irs-14` — unreconciled by `PLAN-039.01`'s own revision log.
- **Missing `depends_on` edges were systemic.** Groups B, D and F found them independently. Group D
  established why they survive: `src/governance/backlog.py` validates dependency completeness only
  at claim time, so a missing edge stays invisible until someone claims the phase.
- **`sys-governance` was being used to mean "writes a file in the governance folder".** Its declared
  paths are the engine — `src/governance`, the schemas, the registries. None of the phases tagged
  with it touched that engine.
- **Narrowing a `systems` list is not enough to create concurrency.** `collisions()`
  (`src/governance/backlog.py:38-52`) reports shared systems *and* shared deliverable paths
  independently. This bit twice: for `phase-idg-08/-10/-11` on `docs/08-governance/`, and for
  `phase-auto-03/-04` on `schemas/`, `test/` and `src/api/routes/`.

## The correction that overturned a ruling

The owner ruled (R10) to amend `phase-agx-09` to build the stale-claim recovery mechanism
`PLAN-039` said `phase-irs-04` consumes. Group I's independent review found the premise wrong:
`phase-conc-04` already owns that deliverable in full (`backlog.yaml:9061-9092`, under
`PLAN-026`), and `PLAN-031` — `phase-agx-09`'s own plan — never mentions claim or worktree recovery
anywhere. Amending `phase-agx-09` would have duplicated `phase-conc-04` and violated
`phase-agx-09`'s own acceptance row (`REQ-016` R14: grounded in a recorded incident, not an invented
mechanism).

**R25 supersedes R10.** `PLAN-039`, `REQ-022` R19 and `ARCH-006` were repointed at `phase-conc-04`;
`phase-agx-09` was left untouched. The owner's instruction to re-review before fixing is what caught
this.

## What changed

- **23 phases enhanced**; `phase-irs-16` created (daemon process model) with `phase-irs-04` narrowed
  to match, splitting a phase two groups independently judged oversized.
- **`next_up` went from 27 to 29 entries** and now has **zero ordering violations** — verified by
  mapping every entry's `depends_on` against queue position. `phase-irs-13` moved after
  `phase-irs-07`; `phase-part-03` moved before `phase-irs-14`; `phase-dgov-01` and `phase-irs-16`
  woven in.
- **Three system ids registered**: `sys-gov-docs`, `sys-auto-gateway`, `sys-auto-ledger`, each with
  deliverables narrowed so the concurrency is real rather than nominal.
- **Three document codes reserved**: `GOV-010`, `ADR-019`, `GOV-011`.
- **Four governed documents corrected**: `PLAN-039` (boundary table, supply table, eight phase-table
  rows, a new `phase-irs-16` row), `PLAN-039.01` (schema and data paths), `REQ-022` (R19),
  `ARCH-006` (the recovery boundary).
- **Four ideas recorded** through the sanctioned writer: `000251` (anchor), `000252`, `000253`,
  `000254`; all linked to the anchor, all triaged, with `000252` also linked to `000082`.

## Decisions

**55 question entries** accumulated, merged to **46 live decisions**, one dropped as resolved by
pass 3. **31 were put to the owner and ruled on, in eight batches** — the pack caps in-session
batches at three, and the owner waived that cap explicitly when asking for the deferred items.
The full ranked set is in `docs/00-working/phase-review-decisions.md` (ungoverned staging per
`ADR-010`); every ruling and its authority is in `_working/phase-review/rulings.md`.

## Authority

The pack's grant covered in-scope phases' backlog lines, the `updated` date and the forced catalog
regeneration. The owner extended it in session, per ruling, to cover `next_up` edits, creating a
backlog phase, `codes.yaml` reservations, `systems.yaml` registrations, and named plan and
requirement corrections. Each extension is recorded against its ruling. Nothing was edited outside a
granted authority; where an agent hit a boundary it stopped and reported rather than improvising —
which is how the `codes.yaml` reservations surfaced as questions instead of silent edits.

## Verification

- `Governance OK: 31 systems, 258 documents, 25 memories, 277 backlog phases`
- `580 passed, 2 warnings`
- `check_no_private_content: OK (665 tracked files, 0 identifiers checked)`, run with changes staged
- `next_up` ordering check: **zero violations**
- `PLAN-039` phase table vs backlog `depends_on`: **all rows match**

## Residuals

- `phase-irs-16`'s row in `PLAN-039`'s phase table carries `—` for Requirements. The splitting agent
  declined to invent a requirement number; whether the daemon process model inherits any of
  `phase-irs-04`'s `R16`–`R19` is unresolved.
- 15 of the 46 ranked decisions remain unruled, in `docs/00-working/phase-review-decisions.md`.
- `phase-idg-08` keeps `sys-governance` and a bare `docs/08-governance/` deliverable — it sits
  outside the frozen scope and now behind idea `000253`'s review.
- One agent misreported which phases its diff touched, naming `phase-irs-10` and `phase-idg-02`
  when it had edited neither. Caught by mapping changed lines to enclosing phase ids rather than
  trusting the report; later dispatches were told to verify against the file, not diff context.
