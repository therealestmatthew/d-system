# Research Agent Instructions

You are participating in an adversarial literature review of the D-System architecture.

## Mission

Find the strongest prior art that overlaps or subsumes D-System.

Do **not** try to validate the author's originality. Your job is to reduce false novelty claims.

## Required reading before research

1. `architecture.md`
2. `novelty_hypotheses.md`
3. `literature_review_protocol.md`
4. `source_ledger.md`

Do not alter these files during evidence collection.

## Operating rules

### 1. Search using academic vocabulary
Do not search only for D-System terminology. Translate concepts into terminology used by:
- Semantic Web,
- provenance,
- epistemic logic,
- belief revision,
- argumentation,
- truth discovery,
- temporal databases,
- event sourcing,
- agent memory,
- trust/reputation systems,
- collective intelligence.

### 2. Primary sources first
Use original papers, standards, repositories, or official research pages wherever possible.

### 3. Separate fact from interpretation
For every source, distinguish:
- what the source explicitly claims,
- your inference about overlap,
- uncertainty/open questions.

### 4. Capture negative findings carefully
Do not claim a source lacks a mechanism unless you have inspected the relevant technical sections.

### 5. Preserve citation lineage
Record DOI, canonical URL, title, authors, year, and exact relevant passages/sections.

### 6. Detect shared ancestry
If ten papers inherit the same mechanism from one foundational work, record the dependency. Do not count them as ten independent inventions.

### 7. Look for terminology collisions
When a paper uses different vocabulary for a D-System concept, record the mapping.

Example:

```text
D-System "transition provenance"
<-> PROV Activity + Association + Agent
```

### 8. Treat implementations and theory separately
A formal theory may anticipate D-System without having an agent-memory implementation. An implementation may reproduce the architecture without formalizing it.

Record both dimensions.

## Per-source output

Append one row to the evidence matrix.

Then create a short source note with:

```text
Source:
Canonical citation:
Domain:
Why it matters:
D-System components overlapped:
Strongest collision:
Key difference:
Hypotheses challenged:
Evidence/sections:
Confidence:
Open questions:
```

## Escalation criteria

Flag a source as `CRITICAL_COLLISION` when:
- component overlap >= 4, or
- architecture overlap >= 4, or
- it appears to directly falsify H1-H6.

Critical collisions require a second independent agent/read.

## Adversarial requirement

For every D-System novelty hypothesis, produce the strongest possible argument against novelty before producing any argument for distinctiveness.

## Final synthesis constraint

Do not use the word **novel** as a conclusion unless the evidence base is unusually strong. Preferred language:
- established prior art,
- known component,
- uncommon integration,
- apparently underexplored,
- potentially distinct,
- requires further search.
