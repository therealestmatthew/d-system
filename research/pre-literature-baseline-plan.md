# Pre-Literature Baseline — Execution Plan

**Created:** 2026-09-09
**Purpose:** Document the plan for creating the pre-literature research baseline before executing it.

## Objective

Create three research artifacts that freeze D-System's intellectual state before formal literature review begins:

1. **`research/pre-literature-baseline.md`** — 18-section canonical document
2. **`research/pre-literature-hypotheses.yaml`** — Machine-readable H1–H11 register
3. **`research/literature-review/HANDOFF.md`** — Short handoff for the future literature-review agent

## Constraints

- **No implementation changes** — no code, schemas, tests, plans, or configuration
- **No external research** — no web searches, no academic databases
- **No novelty claims** — the null hypothesis is that D-System recombines existing prior art
- **Provenance discipline** — every statement tagged as `REPOSITORY_EVIDENCE`, `EXISTING_PLAN`, `CONCEPTUAL_PROPOSAL`, `ADVERSARIAL_INFERENCE`, or `OPEN_QUESTION`
- **Status vocabulary** — `IMPLEMENTED`, `PARTIALLY_IMPLEMENTED`, `PLANNED_BEFORE_RESEARCH`, `PROPOSED_DURING_EXPLORATION`, `OPEN_RESEARCH_QUESTION`, `UNKNOWN`
- **Hypothesis preservation** — do not weaken/strengthen H1–H11 based on implementation gaps

## Discovery Status: COMPLETE

All source artifacts have been read:

| Source | Files | Status |
|---|---|---|
| Adversarial review 01–12 | 12 files | ✅ All read |
| Architecture docs | 8 files (architecture, two-system, phase-context, traceability, transition-vocab, knowledge-glossary, terminology-investigation, implementation-glossary) | ✅ All read |
| Hypotheses | novelty_hypotheses.md | ✅ Read |
| Protocols | 4 files (agent-instructions, literature-review, addendum, expansion) | ✅ Read |
| Sources | source_ledger.md, cited_sources_chat_seed.md | ✅ Read |
| Evidence | repository-inventory.md, verification.md | ✅ Read |
| Literature-review setup | CLAUDE.md | ✅ Read |
| Implementation | ideas.py, schemas (idea, memory, backlog, document, decision, evidence), load_context.py, rebuild_db.py, 001_schema.sql | ✅ Read |

## Baseline Document Structure (18 Sections)

| # | Section | Key sources |
|---|---|---|
| 1 | Purpose and Research Boundary | Repository age, AGENTS.md, adversarial review scope |
| 2 | Original Problem and Motivation | architecture.md, two_system_architecture.md, schemas |
| 3 | Implemented Baseline | adversarial review 01, 03; schemas; ideas.py; load_context.py; backlog.py |
| 4 | Work Already Planned or In Progress | backlog.yaml phases, plans, requirements |
| 5 | Proposed Architecture at Research Pause | architecture.md, two_system_architecture.md |
| 6 | Proposed State Model | architecture.md (O/E/L), ARCH-005 |
| 7 | Proposed Transition and Memory Model | architecture.md, transition_vocabulary.md |
| 8 | Proposed Provenance and Collective Reasoning | architecture.md sections on provenance/authority/convergence |
| 9 | Proposed Ideation-to-Reality Traceability | development_traceability_model.md, adversarial 06 |
| 10 | Phase Hypothesis | phase_context_contract.md, backlog.schema.json, adversarial 10 |
| 11 | Epistemic Blast Radius Hypothesis | implementation_glossary.md, adversarial 06, 10 |
| 12 | Runtime-to-Knowledge Closure Hypothesis | two_system_architecture.md, adversarial 10 |
| 13 | Implementation vs Proposed Architecture Matrix | adversarial 03, 10 (16 claim tests) |
| 14 | Preserve List | adversarial 09 |
| 15 | H1–H11 Pre-Literature Hypothesis Register | novelty_hypotheses.md, research_expansion.md |
| 16 | Strongest Internal Challenges | adversarial 10 (final adversarial challenge section) |
| 17 | Formal Literature Review Questions | adversarial 11, protocols, research_expansion.md |
| 18 | Research Categories (Established / Proposed / Unknown) | Synthesis of all above |

## Hypothesis Register Schema (YAML)

```yaml
id:
name:
claim:
origin_status:
implementation_baseline:
existing_internal_evidence:
what_would_falsify_it:
prior_art_families_to_search:
experimental_baseline_if_applicable:
status: UNTESTED_PRE_LITERATURE
```

## Handoff Structure

10-point list per the specification, directing the future literature-review agent to the baseline, hypotheses, and review protocol.
