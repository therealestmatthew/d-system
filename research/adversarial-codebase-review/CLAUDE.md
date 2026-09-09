# CLAUDE.md — D-System Adversarial Codebase Review

## Mission

Perform an adversarial review of the existing D-System codebase before any formal literature review or major architectural refactor.

The objective is **not** to improve the codebase immediately.

The objective is to discover:

1. what architecture actually exists,
2. what assumptions are encoded in implementation,
3. where implementation diverges from the current conceptual model,
4. which abstractions are accidental versus intentional,
5. where the model is internally inconsistent,
6. which design decisions lack rationale or provenance,
7. which parts should be preserved because they already solve real problems,
8. and which questions must be resolved before formal research or refactoring.

Treat the codebase as empirical evidence about the system.

Do not assume the conceptual documents are correct merely because they are newer or cleaner.

---

# 1. Adversarial posture

Your default stance is:

> The implementation probably contains hidden assumptions, semantic conflations, duplicated concepts, accidental constraints, and contradictions that the current conceptual architecture has not yet recognized.

Actively try to falsify the apparent design.

Do not flatter the architecture.

Do not optimize for agreement.

Do not rewrite unclear architecture into a cleaner story unless the code itself supports that interpretation.

Distinguish:

- **EXPLICIT DESIGN** — clearly documented or intentionally encoded.
- **IMPLICIT DESIGN** — behavior or schema that implies an architectural decision.
- **ACCIDENTAL DESIGN** — implementation detail that has become structurally important without clear intent.
- **INCONSISTENCY** — two parts of the system encode incompatible semantics.
- **UNKNOWN** — insufficient evidence to determine intent.

---

# 2. Research context

D-System began as a practical personal system for tracking ideas, workload, tasks, responsibilities, deadlines, commitments, and development work.

It evolved into a broader architecture concerning:

- knowledge construction,
- memory,
- context,
- ideas,
- claims,
- evidence,
- beliefs,
- decisions,
- provenance,
- append-only state transitions,
- planning,
- agentic development,
- code generation,
- verification,
- runtime observation,
- feedback,
- and traceability from ideation to implemented reality.

Current conceptual work proposes two tightly coupled systems:

## A. Knowledge Construction & Management

Concerned with:

- information,
- ideas,
- observations,
- claims,
- assumptions,
- hypotheses,
- beliefs,
- evidence,
- inference,
- conclusions,
- decisions,
- provenance,
- context,
- memory,
- conflict,
- convergence,
- authority,
- and learning.

## B. Implementation & Experience

Concerned with:

- requirements,
- constraints,
- specifications,
- plans,
- phases,
- tasks,
- artifacts,
- code,
- tests,
- deployments,
- functionality,
- runtime events,
- telemetry,
- outcomes,
- and feedback.

The conceptual boundary is approximately:

```text
Knowledge / Reasoning
        |
        | DECIDE
        v
Decision / Directive
        |
        | DERIVE / SPECIFY
        v
Requirements / Constraints
        |
        v
Specification
        |
        v
Plan
        |
        v
Phase
        |
        v
Implementation
```

Do not assume the codebase actually follows this model.

Your job is to determine what it really does.

---

# 3. Core review questions

## Data model

Determine:

- What are the actual first-class entities?
- What are stored as enums?
- What are stored as tags?
- What are stored as relationships?
- What are represented only in prompts or application logic?
- Which concepts are overloaded?
- Which concepts are duplicated under different names?
- Which entities exist only because of storage convenience?
- Which entities appear conceptually important but are absent from persistence?

Inspect:

- database schema,
- ORM models,
- migrations,
- validation schemas,
- serialization models,
- API contracts,
- enums,
- constants,
- type definitions.

---

## Knowledge-state semantics

Determine how the code currently represents:

- ideas,
- knowledge,
- memory,
- claims,
- observations,
- evidence,
- decisions,
- tasks,
- plans,
- events,
- relationships,
- state,
- status,
- history.

Pay special attention to whether the code conflates:

- idea vs claim,
- claim vs belief,
- observation vs evidence,
- event vs transition,
- state vs version,
- task vs commitment,
- decision vs directive,
- memory vs stored record,
- context vs retrieval result,
- epistemic status vs lifecycle status,
- temporal validity vs truth status.

---

## Classification model

Current conceptual architecture uses three independent dimensions:

### Ontological
- Concepts & Mental Models
- Artifacts & Entities
- Processes & Workflows
- Events

### Epistemic
- Axioms & Ground Truths
- Hypotheses & Assumptions
- Anti-Patterns & Falsified Concepts

### Lifecycle
- Generative Seeds
- Strategic Directives
- Operational Tasks
- Retrospective Insights

Investigate:

- whether the code treats these as truly independent,
- whether one classification can overwrite another,
- whether every object is forced to receive all three,
- whether some objects do not fit a dimension,
- whether classification is used computationally or only decoratively,
- whether subject tags are properly separated from semantic classification,
- whether classifications are mutable,
- whether historical classifications are preserved.

Do not assume the current classification system is correct.

---

# 4. State-transition review

The current conceptual hypothesis is:

```text
State_t --[Transition + Provenance]--> State_t+1
```

Possible transition concepts include:

- CONSIDER
- CAPTURE
- PROPOSE
- HYPOTHESIZE
- ASSUME
- EVALUATE
- TEST
- VALIDATE
- FALSIFY
- CONCLUDE
- DECIDE
- SELECT
- REJECT
- PLAN
- DECOMPOSE
- DESIGN
- EXECUTE
- IMPLEMENT
- COMPLETE
- FAIL
- OBSERVE
- ASSESS
- REFLECT
- LEARN
- RECONSIDER
- SUPERSEDE
- DEPRECATE
- RETIRE

Inspect the code for actual transition semantics.

Determine:

- whether changes mutate records or create successors,
- whether transitions are explicit,
- whether transitions are inferred from timestamps/status changes,
- whether transition metadata is retained,
- whether the system distinguishes semantic relationships from state transitions,
- whether transitions are edges, records, events, logs, or hidden application behavior,
- whether actor and rationale are captured,
- whether prior state remains reconstructable,
- whether state evolution is deterministic,
- whether supersession is modeled or approximated by deletion/update.

Identify any place where append-only claims are violated.

---

# 5. Provenance review

Inspect whether the implementation currently records:

- initiator,
- participant,
- approver,
- human actor,
- agent actor,
- system actor,
- evidence,
- source,
- method,
- rationale,
- authorization,
- timestamp,
- upstream dependency,
- derivational lineage.

Determine whether provenance is:

- explicit,
- partial,
- inferred,
- absent,
- or conflated with audit logging.

Test whether the system could answer:

> Why does this state exist?

> Who caused it?

> What evidence supported it?

> Which prior states did it depend on?

> Was the decision authorized?

> Is this conclusion independent or derivative?

---

# 6. Memory and context review

Inspect actual memory behavior.

Determine:

- what is persisted,
- what is retrieved,
- what is injected into prompts,
- what is summarized,
- what is discarded,
- what is compressed,
- how context is selected,
- whether retrieval is similarity-based, graph-based, rule-based, recency-based, or hybrid,
- whether prior reasoning lineage is preserved,
- whether superseded information can reappear incorrectly,
- whether dissenting evidence is preserved,
- whether context contains provenance,
- whether context selection is explainable.

Do not assume "stored" equals "remembered."

Do not assume "retrieved" equals "relevant."

---

# 7. Planning and implementation review

Inspect how the code models:

- goals,
- requirements,
- plans,
- phases,
- tasks,
- dependencies,
- acceptance criteria,
- execution sessions,
- agent handoff,
- implementation outputs.

Current working definition:

> A Phase is the smallest planned unit of work intended to be completed within one bounded agentic development session.

Test whether the actual implementation supports this.

Look for:

- phase/task confusion,
- plans that are only task containers,
- task state used as plan state,
- no explicit context boundary,
- no phase completion contract,
- no traceability from decision to requirement,
- no traceability from requirement to code,
- no return path from code/test/runtime observation to knowledge.

---

# 8. Traceability review

Attempt to trace actual examples in both directions.

## Forward

```text
Idea
 -> Decision
 -> Requirement
 -> Specification
 -> Plan
 -> Phase
 -> Task
 -> Artifact / Code
 -> Test
 -> Deployment
 -> Functionality
 -> Runtime Outcome
```

## Backward

```text
Functionality
 <- Code
 <- Phase
 <- Plan
 <- Specification
 <- Requirement
 <- Decision
 <- Evidence / Rationale
 <- Idea / Observation / Commitment
```

Record where the chain breaks.

Do not invent missing links.

Classify each expected trace link as:

- `EXPLICIT`
- `DERIVABLE`
- `AMBIGUOUS`
- `ABSENT`

---

# 9. Epistemic blast-radius test

Find at least one upstream assumption or decision and ask:

> If this assumption became false tomorrow, could the codebase identify every downstream decision, requirement, plan, artifact, test, or capability requiring reassessment?

If not, identify exactly why not.

Possible causes:

- missing relationship,
- missing version history,
- mutation destroyed provenance,
- dependency is implicit in text,
- no requirement-to-code mapping,
- no assumption-to-decision mapping,
- inadequate identifier model.

---

# 10. Hidden ontology review

Search for architecture hidden in:

- table names,
- column names,
- enums,
- booleans,
- status strings,
- filenames,
- directory structure,
- route names,
- prompts,
- agent system instructions,
- UI terminology,
- logging,
- test fixtures,
- migration history,
- comments,
- commit messages if available.

Examples:

```text
status = "done"
```

may imply an undocumented lifecycle model.

```text
is_memory = true
```

may imply memory is being treated as an intrinsic node type.

```text
parent_id
```

may encode hierarchy where the conceptual model expects typed relationships.

Surface these assumptions explicitly.

---

# 11. Contradiction search

Actively search for contradictions such as:

- docs say append-only, code updates in place,
- docs say classifications independent, validation couples them,
- schema allows many beliefs but UI assumes one truth,
- prompts call a decision a node while architecture calls it a transition,
- code stores only final answer while documentation claims reasoning provenance,
- tasks and commitments share one state model despite different semantics.

Every contradiction must include concrete evidence.

---

# 12. Preserve useful implementation

Do not assume conceptual purity is better than working behavior.

Identify implementation patterns that:

- solve a real user need,
- are simpler than the proposed abstraction,
- have proven useful,
- should constrain future ontology design.

Label these:

`PRESERVE_UNLESS_DISPROVEN`

---

# 13. Do not refactor during review

Unless explicitly instructed otherwise:

- do not rewrite schemas,
- do not rename entities,
- do not alter migrations,
- do not normalize tables,
- do not change prompts,
- do not implement the conceptual architecture.

Review first.

Recommendations belong in the final report.

---

# 14. Required deliverables

Create a review directory such as:

```text
research/adversarial-codebase-review/
```

Produce:

## `01_actual_architecture.md`

Describe what the codebase actually implements.

Include diagrams where useful.

## `02_implicit_ontology.md`

List every significant concept found in schema, code, prompts, and workflows.

Classify each as explicit, implicit, accidental, inconsistent, or unknown.

## `03_conceptual_vs_implemented.md`

Comparison matrix:

| Concept | Conceptual model | Implemented model | Match | Risk |
|---|---|---|---|---|

## `04_state_transition_audit.md`

Document mutation, append-only behavior, transitions, supersession, deletion, and history.

## `05_memory_context_audit.md`

Document persistence, retrieval, context construction, summaries, and agent/session behavior.

## `06_traceability_audit.md`

Test forward and backward traces through real examples.

## `07_assumption_register.md`

For every architectural assumption:

```yaml
assumption:
evidence:
location:
confidence:
risk_if_wrong:
```

## `08_contradictions.md`

Concrete inconsistencies with file/line references.

## `09_preserve_list.md`

Useful implementation patterns that should not be discarded casually.

## `10_adversarial_findings.md`

Rank findings:

- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`
- `OPEN_QUESTION`

## `11_research_questions_generated.md`

Questions the literature review must investigate because of codebase findings.

## `12_recommendations.md`

Only after the review is complete, recommend:

- preserve,
- clarify,
- research,
- refactor later,
- deprecate,
- migrate.

---

# 15. Evidence requirements

Every material finding must include:

- file path,
- line range where possible,
- code/schema/prompt excerpt,
- interpretation,
- confidence,
- alternative interpretation where reasonable.

Do not make architecture claims from filenames alone.

---

# 16. Final adversarial challenge

Before completing the review, make the strongest possible argument for each of these:

1. D-System is over-modeled.
2. D-System is under-modeled.
3. The three classifications are unnecessary.
4. The three classifications are insufficient.
5. Memory does not need graph-based state-transition semantics.
6. Provenance can be handled by ordinary audit logs.
7. Requirements traceability already solves the implementation boundary.
8. Phase is just another word for task/work package.
9. The knowledge and implementation systems should not be separated.
10. The knowledge and implementation systems must be separated.

The purpose is not to choose whichever argument sounds best.

The purpose is to expose which claims survive contact with the actual codebase.
