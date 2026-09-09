# Literature Review Expansion: Ideation to Reality

## 1. Objective

Extend the existing D-System literature review beyond knowledge/memory into the complete path from reasoning to implemented systems and observed reality.

The review must search for prior art that already provides all or part of:

```text
Idea
 -> reasoning
 -> decision
 -> requirement
 -> specification
 -> plan
 -> bounded agent execution
 -> artifact/code
 -> verification
 -> deployment
 -> functionality
 -> runtime observation
 -> feedback
 -> revised knowledge
```

## 2. New research domains

### Requirements engineering
Search:
- requirements traceability,
- requirements provenance,
- requirements evolution,
- requirement-to-code traceability,
- requirement-to-test traceability,
- bidirectional traceability,
- requirements change impact.

### Design rationale
Search:
- design rationale,
- architecture rationale,
- rationale management,
- architecture knowledge management,
- issue-based information systems (IBIS),
- Questions Options Criteria (QOC),
- design decision provenance.

### Architecture Decision Records
Search:
- ADR provenance,
- ADR supersession,
- ADR traceability,
- architecture decisions to code,
- architecture decision knowledge graphs.

### Software traceability
Search:
- software artifact traceability,
- end-to-end lifecycle traceability,
- traceability information models,
- trace links,
- trace recovery,
- change impact analysis.

### Model-based / systems engineering
Search:
- digital thread,
- digital engineering,
- model-based systems engineering,
- requirements-to-design-to-verification,
- verification traceability,
- lifecycle provenance.

### Spec-driven development
Search:
- specification-driven development,
- executable specifications,
- behavior-driven development,
- formal specification to implementation,
- specification traceability,
- specification mining.

### Software provenance
Search:
- code provenance,
- software supply chain provenance,
- build provenance,
- artifact lineage,
- source-to-binary provenance.

### Agentic software engineering
Search:
- coding agent memory,
- software engineering agent episodic memory,
- cross-session coding agents,
- persistent agent memory,
- agent task decomposition,
- long-horizon coding agents,
- agent session handoff,
- agent context reconstruction,
- agent checkpointing.

### Planning and hierarchical execution
Search:
- hierarchical task networks,
- AI planning,
- plan decomposition,
- work packages,
- episodic task boundaries,
- execution monitoring,
- replanning.

### Verification and validation
Search:
- requirement verification,
- evidence-based verification,
- continuous verification,
- test provenance,
- test-to-requirement traceability.

### Observability and feedback
Search:
- observability-driven development,
- telemetry-to-requirement traceability,
- runtime verification,
- requirements monitoring,
- runtime evidence,
- feedback loops software engineering.

### Self-adaptive systems
Search:
- MAPE-K,
- autonomic computing,
- knowledge-based adaptation,
- runtime models,
- feedback-driven software evolution.

### DevOps / continuous engineering
Search:
- continuous requirements engineering,
- continuous architecture,
- continuous verification,
- DevOps traceability,
- deployment provenance.

---

## 3. New research questions

### RQ8 — Knowledge-to-requirement translation
How have systems represented the derivation of requirements from decisions, rationale, evidence, needs, and assumptions?

### RQ9 — Rationale-to-code traceability
Can existing systems reconstruct why a particular implementation artifact exists from its upstream reasoning history?

### RQ10 — Forward ideation traceability
Can existing systems trace an originating idea/need through decisions, requirements, implementation, verification, and runtime outcome?

### RQ11 — Agentic phase boundaries
What concepts exist for bounded development episodes that also act as context-management boundaries for coding agents?

### RQ12 — Context reconstruction
How do coding agents reconstruct sufficient project context across sessions without replaying the entire project history?

### RQ13 — Execution-to-memory consolidation
How are discoveries, decisions, failures, and evidence generated during coding sessions consolidated into persistent project memory?

### RQ14 — Epistemic change impact
Can existing systems propagate a changed/falsified assumption through decisions, requirements, plans, code, tests, and functionality?

### RQ15 — Runtime feedback
How are runtime telemetry and observed outcomes connected back to requirements, design assumptions, and prior decisions?

### RQ16 — End-to-end human-agent development provenance
Does any architecture provide provenance across human and AI reasoning, planning, code generation, verification, deployment, and operational feedback?

---

## 4. New novelty hypotheses

### H7 — Development provenance

Software functionality can be represented as the downstream result of an append-only provenance lineage connecting ideas, observations, evidence, decisions, requirements, specifications, plans, execution phases, artifacts, verification, and observed outcomes.

**Falsification condition:** Find an existing framework whose end-to-end provenance model materially subsumes this chain.

### H8 — Phase-bounded context construction

A planned development phase can serve as an explicit context boundary for agentic software engineering, allowing context to be assembled from persistent reasoning/development lineage and execution results to be consolidated back into persistent memory.

**Falsification condition:** Find an established agentic development architecture with materially equivalent semantics and lifecycle.

### H9 — Bidirectional epistemic traceability

A system can support both:
- forward tracing from idea/knowledge to realized functionality/outcome, and
- backward tracing from functionality/artifact to the reasoning, evidence, assumptions, and decisions that justify it.

**Falsification condition:** Find prior art providing materially equivalent bidirectional reasoning-to-runtime traceability.

### H10 — Epistemic blast-radius analysis

When an upstream assumption, evidence source, or claim is weakened, falsified, or superseded, provenance topology can identify downstream decisions, requirements, plans, artifacts, tests, and functionality requiring reassessment.

**Falsification condition:** Find established impact-analysis systems already performing equivalent propagation from epistemic change rather than only artifact/requirement change.

### H11 — Runtime-to-knowledge closure

Operational telemetry, tests, incidents, and user outcomes can be transformed into provenance-bearing evidence that updates the same knowledge structure from which implementation intent originated.

**Falsification condition:** Find an architecture providing materially equivalent closed-loop reasoning from knowledge to implementation to runtime evidence and back.

---

## 5. Critical prior-art families to prioritize

1. Requirements Traceability Matrix / bidirectional traceability
2. Design rationale systems
3. Architecture Knowledge Management
4. Architecture Decision Records
5. IBIS / QOC / decision rationale models
6. Software traceability and trace recovery
7. Change impact analysis
8. Digital thread / digital engineering
9. MBSE
10. MAPE-K and self-adaptive systems
11. Truth-maintenance systems
12. Software provenance / SLSA-like artifact provenance
13. Agent memory for software engineering
14. Long-horizon coding agents
15. Agent planning / hierarchical task networks
16. Runtime verification / requirements monitoring
17. Continuous requirements engineering
18. Knowledge graphs for software engineering
19. Software architecture knowledge graphs
20. Requirements-to-code/test knowledge graphs

---

## 6. Comparison dimensions to add to evidence extraction

For each relevant source/system record:

- idea/need representation,
- rationale representation,
- decision representation,
- requirement derivation,
- specification representation,
- plan representation,
- execution-unit representation,
- context/session boundary,
- artifact/code linkage,
- test/verification linkage,
- deployment linkage,
- functionality linkage,
- runtime observation linkage,
- feedback-to-knowledge mechanism,
- forward traceability,
- backward traceability,
- change impact,
- epistemic change impact,
- human provenance,
- agent provenance,
- append-only history,
- supersession/retraction,
- evaluation evidence.

---

## 7. Adversarial test

The strongest challenge to D-System may be that it is simply a synthesis of:

```text
Knowledge Graph
+ PROV-O
+ Design Rationale
+ Requirements Traceability
+ ADRs
+ Event Sourcing
+ Agent Memory
+ Software Artifact Provenance
+ Observability
+ MAPE-K / feedback loops
```

The research must assume this explanation is correct until evidence demonstrates that a distinct mechanism or useful integration remains.

The goal is not to protect the architecture from prior art.

The goal is to discover exactly what should be reused, what should be integrated, and what—if anything—must be invented.
