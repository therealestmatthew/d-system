---
schema_version: 1
id: doc-portable-framework-content-extraction
code: PLAN-041
title: Portable framework content extraction from repository history
kind: plan
status: draft
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-19'
systems: [sys-fw-analysis-patterns, sys-fw-analysis-sessions, sys-fw-analysis-protocol]
depends_on: [doc-portable-framework-content-extraction-requirements]
---

# Portable framework content extraction from repository history

## Summary

Three of the thirteen ideas in the 2026-09-19 portable-framework batch (`000274`, `000275`, `000276`,
all linked to the batch anchor `000281`) each propose an analytical pass over d-system's own history —
governing documents for one, session records for the other two — to recover material the portable
framework (`PLAN-040`) needs but does not yet have: generalized patterns, buried decisions, and an
honest assessment of whether the session/decision-record form itself is worth carrying forward.

[REQ-025](../06-requirements/REQ-025-portable-framework-content-extraction.md) states the observable
requirements. This plan does not build any template or schema (`PLAN-040`'s scope) and does not act on
`000276`'s findings by editing the checkpoint skill or session-close command — that stays a future,
separately-claimed phase once the analysis exists to justify it.

## Design: three independent passes, three systems

`000274`, `000275` and `000276` read overlapping source material (d-system's governing prose and
session records) but produce three disjoint output files and depend on none of each other's results:

*Amended 2026-09-19:* the form-critique pass now runs from a pre-drafted prompt,
`docs/00-working/PROMPT-session-taxonomy-part3-record-templates.md`, and `phase-fwa-03` depends on
`phase-tax-02` ([PLAN-042](PLAN-042-session-taxonomy-investigation.md)), whose evidence-tested
taxonomy and per-record structure table are its inputs. The other two passes stay independent.

| Pass | Idea | Reads | Writes |
|---|---|---|---|
| Pattern extraction | `000274` | `AGENTS.md`, `GOV-*`, ADRs, PLANs | `docs/00-working/framework/06-analysis/extracted-patterns.md` |
| Session decision extraction | `000275` | `docs/03-sessions/*.md` | `docs/00-working/framework/06-analysis/session-record-extraction.md` |
| Session/decision form critique | `000276` | `docs/03-sessions/*.md`, decision records | `docs/00-working/framework/06-analysis/session-protocol-enhancements.md` |

Each pass is registered on its own system — `sys-fw-analysis-patterns`, `sys-fw-analysis-sessions`,
`sys-fw-analysis-protocol` — rather than one shared system or, worse, the repository-wide
`sys-governance` mutex idea `000253` flagged as a finding on the concurrency track's three phases.
There is no coherence requirement forcing these three to run in sequence the way `PLAN-040`'s five
template shapes do: nothing about the pattern-extraction pass's output constrains the shape of the
session-decision extraction, and `000276` is explicit that it is a separate lens from `000275`, not a
follow-on to it. Three agents can genuinely work all three at once without stepping on each other's
files, so the `systems` declarations say that plainly instead of serializing out of habit.

This is the direct answer to the task this batch was reviewed under: a phase gets a narrow system
when narrow is true, and a shared system when sharing is actually the design (see `PLAN-040`'s
contrasting case, where five phases deliberately share one system for a real coherence reason).

## Phasing

Proposed phases are recorded in `_working/framework-phases-proposed.md` for the owner's review before
entering `docs/09-backlog/backlog.yaml`:

1. `phase-fwa-01` — pattern extraction (`000274`).
2. `phase-fwa-02` — session-record decision extraction (`000275`).
3. `phase-fwa-03` — session/decision-record form critique (`000276`).

All three have `depends_on: []` and disjoint `systems`/`deliverables`, so nothing in this plan forces
serialization; the owner or `--ready` ordering decides whether they are actually worked concurrently.

## Out of scope

- Editing `.claude/skills/checkpoint/` or `.claude/commands/session-close.md` in response to
  `000276`'s findings. REQ-025 R03 requires the analysis phase itself to leave those paths untouched.
- Anything under `docs/00-working/framework/06-analysis/` beyond the three files above — the existing
  `agent-workflows.md` draft in that directory is read as reference material, not extended by this
  plan.
- `000281`'s starter-kit packaging, which depends on this plan's and `PLAN-040`'s output existing.

## Ideas not promoted alongside this plan

See `PLAN-040`'s "Ideas not promoted in this batch" section for the disposition of `000272`, `000273`
and `000280`, which apply to the batch as a whole rather than to this plan specifically.
