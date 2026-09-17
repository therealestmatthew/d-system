---
schema_version: 1
id: doc-session-agent-surface-audit
code: SESS-2026-09-17-01
title: The agent surface audited and the Claude Code dependency ruled
kind: session
status: active
owner: repository-owner
created: '2026-09-17'
updated: '2026-09-17'
systems: [sys-delivery, sys-governance]
depends_on: [doc-agent-engineering-delegation, doc-agent-engineering-delegation-requirements, doc-claude-code-dependency, doc-agent-surface-audit]
---

# The agent surface audited and the Claude Code dependency ruled

`phase-agx-02`, built by dispatched agents from a coordinating session. Delivered
[GOV-015](../08-governance/GOV-015-agent-surface-audit.md), a 44-row audit of every item under
`.claude/` plus the shipped Codex agent definition, and
[ADR-021](../04-decisions/ADR-021-claude-code-dependency.md), the ruling on idea `000069`.

## The ruling

**This repository needs an agent runner, not Claude Code specifically.** `PLAN-020` already makes
`.claude/` generated output and ships working Codex equivalents for seven substantive workflows,
and a live capability probe confirmed the coordinator role is performable on Codex with named
adjustments. `REQ-016` R05 requires the answer to state what would change it; three concrete
reversal triggers are recorded in the ADR.

The ruling rests on evidence gathered the same day: a real Codex session was run against this
repository and reported its own capabilities, tagging each claim `[demonstrated]`,
`[documented]` or `[uncertain]`. The raw response is in `docs/00-working/`, and the summary is
annotated on idea `000069` where the ruling would look for it. An adversarial reviewer checked
every `[uncertain]` claim against both documents and confirmed none is asserted as established.

## The audit

44 rows: 43 files under `.claude/` plus `.codex/agents/idea-triage.toml`. **38 keep, 6 redesign,
0 retire.** The six are `.claude/prompts/rung-*` and `anti-pattern-gallery.md` — sound content in
a directory nothing in the harness loads. Relocation to `docs/02-prompts/` is the fix; it was
**reported, not executed**, because that path is outside this phase's declared deliverables. The
same applies to the one missing-and-needed finding answering idea `000013`: a
code-allocation-plus-document-stub command that does not exist.

Seven of the 43 `.claude/` files are generated from `agent-workflows/`, so their real source is
elsewhere — established before judging any item, since a verdict on a generated file is a verdict
on the wrong artifact.

## Review

Two adversarial passes. The first found **R05 holding but R03 and R04 not**:

- **R03** — `REQ-016` R03 reads "one row per item under `.claude/` **and per shipped agent
  definition**", two clauses. The audit covered 43 `.claude/` files but gave no row to
  `.codex/agents/idea-triage.toml`, which is tracked and generated as a real `host: codex`
  target. The owner ruled the second clause includes Codex-side definitions; a 44th row was added.
- **R04** — five independently chosen rows included two carrying a dimension as filler: a bare
  `n/a.` model cell, and a context-cost phrase repeated verbatim six times across unrelated rows.

Fix cycle 1 added the row, corrected every downstream count, and swept ~30 filler cells across 23
rows. A re-check — required to sample rows neither the first reviewer nor the fixer had used —
confirmed R03 held but found **one surviving row**, `demo-orch-stage.md`, with an unreasoned model
cell and two bare cross-references. It had survived precisely because the fixer's own self-check
sample did not include it. Fix cycle 2 rewrote it; a filler sweep now returns zero.

## Decisions

- **"Shipped agent definition" includes Codex-side definitions** (owner, 2026-09-17). The
  alternative reading makes R03's second clause redundant, and an agent-surface audit that saw only
  the Claude half would have contradicted `ADR-021` sitting beside it in the same branch.
- **The audit was not split**, despite the phase's own `next_action` offering that at claim time.
  Delegating the reading to an agent is what made ~37 files on four dimensions fit one session.

## Corrections

The claim commit for this phase used `git add -A` and swept in an unrelated idea annotation without
regenerating its derived page, leaving `dev` red on
`test_the_committed_markdown_matches_regenerated_output`. A claim commit should change nothing but
the claim and the catalog. Repaired on `dev` before this branch merged.

## Left undone

Both are reported findings outside this phase's deliverables, and each needs its own phase:

- Relocating the six `.claude/prompts/` files to `docs/02-prompts/`. The edit belongs in
  `agent-workflows/` for generated items, which this phase could not touch.
- Building the missing code-allocation-plus-document-stub command (idea `000013`).

## Verification

- `Governance OK: 31 systems, 275 documents, 25 memories, 278 backlog phases`
- `629 passed, 2 warnings` — post-rebase, against peers' merged work
- `check_no_private_content: OK`, staged
- All three `GOV-003` completion conditions met: green verification with output captured, the
  adversarial review resolved across two fix cycles, and owner-approved integration.
