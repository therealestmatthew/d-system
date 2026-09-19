---
schema_version: 1
id: doc-session-taxonomy-investigation
code: PLAN-042
title: Session-type taxonomy investigation
kind: plan
status: draft
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-19'
systems: [sys-governance]
depends_on: [doc-session-taxonomy-investigation-requirements]
---

# Session-type taxonomy investigation

## Summary

A two-session investigation that first proposes a theoretical taxonomy of Claude Code session
types — a portable core plus its d-system binding — and then tests that theory against the
repository's evidence: ~108 raw transcripts under `~/.claude/projects/-code-d-system*/`, ~119
curated session records, and the tooling and governance surface. The theory is registered with
falsifiable predictions before any evidence is examined, so the empirical phase is a test rather
than curve-fitting. [REQ-026](../06-requirements/REQ-026-session-taxonomy-investigation.md)
states the observable requirements.

The findings feed the planned CLAUDE.md / AGENTS.md revamp (session-identification rules), the
governance-obligations question (which session types need records, worktrees, claims), the
orchestrator-variant design, and a portable session-type model for use beyond this repo.

## Run artifacts

Each phase executes a pre-drafted prompt, adversarially reviewed and revised in the session
recorded as `SESS-2026-09-19-06` (`doc-session-session-taxonomy-prompt`) and its follow-up:

| Phase | Prompt | Deliverable |
|---|---|---|
| `phase-tax-01` | `docs/00-working/PROMPT-session-taxonomy-part1-theory.md` | `docs/00-working/session-types-theory.md` |
| `phase-tax-02` | `docs/00-working/PROMPT-session-taxonomy-part2-evidence.md` | `docs/00-working/session-taxonomy.md` + derived data under `_private/analysis/session-taxonomy/` |

The prompts are the plan's method in full: the theory-first hard stop, the three-stage
deterministic-reduction pipeline, the privacy guard routing every derived file to
`_private/analysis/session-taxonomy/`, blind anti-confirmation sampling, and the portability
attack step. This plan does not restate them; a change to the method is a change to the prompt
files.

## Relation to prior and neighboring work

- **`REQ-023` / `ADR-020` (`phase-ses-01`)** — the existing governed session-type taxonomy and
  lifecycle decisions. Prior art and Part 1 input; the investigation evidence-tests them and may
  propose revisions, but amends neither. Any accepted revision is a future, separately-claimed
  change under the `ses` track.
- **`phase-fwa-03` (PLAN-041, idea `000276` — session/decision record form critique)** —
  executes the third prompt of this design,
  `docs/00-working/PROMPT-session-taxonomy-part3-record-templates.md`, and therefore now depends
  on `phase-tax-02`, which supplies its inputs: the evidence-tested taxonomy and the per-record
  structure table (`record-structure.tsv`). This plan collects that table; it does not analyze
  record quality.
- **`phase-fwt-04` (PLAN-040, idea `000277` — session-record document schema)** — consumes the
  schema proposal that `phase-fwa-03`'s run of the Part 3 prompt produces. Unchanged by this
  plan.
- **Ideas `000275` (record decision extraction) and `000237` (unclaimed-session coverage)** —
  served by the Part 3 prompt's design constraints, not by this plan's phases.
- **CLAUDE.md / AGENTS.md** — the deliverables contain proposals only. Neither file is edited
  under this plan.

## Phases

Two phases, one session each, strictly ordered with an owner review between them:

1. **`phase-tax-01` — theoretical taxonomy.** Runs the Part 1 prompt: proposes the portable
   types and their d-system binding with falsifiable predictions (REQ-026 R01–R02), reads no
   transcripts, halts for owner review.
2. **`phase-tax-02` — empirical test.** Runs the Part 2 prompt on the owner's explicit go:
   deterministic reduction, mechanical pre-classification, one judgment wave, prediction
   scorecard (REQ-026 R03–R06). Leaves `record-structure.tsv` ready for `phase-fwa-03`.

## Risks and boundaries

- The transcript corpus is one user in one repo; the portable layer claims existence of types,
  never frequency. The portability attack step is the only external-validity test available.
- Derived prompt extracts contain owner prose that may quote private content; they live only
  under `_private/`, and the promotion path (idea capture, owner decision) covers the reduction
  script alone.
- The deliverables are working documents in `docs/00-working/` (ADR-010 staging); nothing here
  creates governed policy. Promotion of any finding into REQ-023, ADR-020, CLAUDE.md or
  AGENTS.md is the owner's separate decision.
