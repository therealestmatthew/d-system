---
schema_version: 1
id: doc-portable-framework-content-extraction-requirements
code: REQ-025
title: Portable framework content extraction requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-19'
updated: '2026-09-19'
systems: [sys-fw-analysis-patterns, sys-fw-analysis-sessions, sys-fw-analysis-protocol]
depends_on: [doc-governance-protocol, doc-idea-staging]
---

# Portable framework content extraction requirements

## Observed problem and scope

`000274`, `000275` and `000276` — three of the thirteen ideas in the 2026-09-19 portable-framework
batch anchored on `000281` — each propose an agent-driven pass over existing d-system material to
recover something that generalizes beyond this repository or that currently has no mechanism
surfacing it:

- `000274`: mine `AGENTS.md`, `GOV-*`, ADRs and PLANs for patterns that repeat across documents and
  apply to any multi-developer repository, not just this one.
- `000275`: dispatch one sub-agent per session record to extract decisions, newly discovered
  requirements, deferred/out-of-scope items, open investigation items and outstanding action items —
  commitments that today are buried in session prose with nothing surfacing them afterward.
- `000276`: separately from `000275`'s content extraction, assess the *form* of session and decision
  records — structure, length, signal-to-noise — and propose enhancements to the session-writing
  protocols themselves.

`000275` and `000276` are explicitly linked in the idea log and `000276`'s own text calls itself
"separately from" `000275` — two independent lenses on the same source material, not a sequence.
`docs/00-working/framework/06-analysis/agent-workflows.md` already drafts five candidate agent
specifications along similar lines; that file is raw material, written before these ideas existed,
and this requirement is free to depart from it.

## Requirements

**R01 — Pattern extraction cites its sources.**
`docs/00-working/framework/06-analysis/extracted-patterns.md` contains at least five entries, each
naming: the pattern, at least one d-system source document by path, and a generalized form stated
without reference to d-system-specific names (project IDs, agent names, file paths internal to this
repository).
*Verification:* the file exists; grep for a source-path citation on each entry; manual read confirms
the generalized-form prose does not name a d-system-specific identifier.

**R02 — Session-record extraction covers a representative sample and names its categories.**
`docs/00-working/framework/06-analysis/session-record-extraction.md` extracts, per session record
covered, the five categories `000275` names (decisions, new requirements, deferred/out-of-scope
items, open investigation items, outstanding action items) — a category may be stated as empty for a
given record, but the five headings appear for every record covered. The pass covers at least ten
session records, chosen to include records from more than one calendar week so the sample is not one
session's idiosyncrasy.
*Verification:* the file exists; grep for the five category headings recurring per covered record;
count covered records against the source list in `docs/03-sessions/`.

**R03 — The form critique is separable from the content extraction and stays out of `.claude/`.**
`docs/00-working/framework/06-analysis/session-protocol-enhancements.md` assesses structure, length
and signal-to-noise of session and decision records as a question distinct from R02's content
extraction, and proposes specific enhancements to the session-writing protocols. Its deliverables do
not include any edit to `.claude/skills/checkpoint/` or `.claude/commands/session-close.md` — those
are a later, separately-claimed phase gated on this analysis existing, not a mechanical step of
producing it.
*Verification:* the file exists and names specific, concrete enhancement proposals (not only
"consider improving X"); `git diff` for the phase that produces it touches no path under
`.claude/skills/` or `.claude/commands/`.

**R04 — Every analysis file traces back to its originating idea.**
Each of the three files produced under R01-R03 states, near its top, which idea (`000274`, `000275`
or `000276`) it answers and that all three trace to the batch anchor `000281`.
*Verification:* grep each file for its idea number and `000281`.

## Out of scope

- Acting on `000276`'s proposed enhancements by editing the checkpoint skill or session-close command
  — a future, separately-claimed phase.
- Any claim that a "pattern" extracted here is already validated outside d-system. Generalization is
  a hypothesis this pass states; testing it on a second repository is `000281`'s eventual job, not
  this one's.
- Re-analyzing session records already covered by a prior pass if one exists; this requirement does
  not mandate re-doing completed analysis work.
