# D-System Terminology & Ontology Investigation

**Status:** Research plan  
**Objective:** Pressure-test D-System's foundational vocabulary before committing terminology to the architecture, ontology, storage model, APIs, or research claims.

## 1. Why this investigation exists

D-System originated as an implemented personal idea/workload system and expanded into a broader architecture for representing how ideas become plans, commitments, tasks, code, functioning systems, observations, conclusions, and subsequent ideas.

That evolution creates a terminology risk:

Terms that were appropriate for the original application — particularly **idea** — may not be sufficiently precise as universal primitives for a human-agent knowledge architecture.

Before formalizing the next schema, this investigation should determine:

1. Which concepts are genuinely distinct?
2. Which are synonyms or contextual roles?
3. Which are node-like entities?
4. Which are relationships?
5. Which are transitions/processes?
6. Which are properties?
7. Which are derived/system-level concepts?
8. Which terms already have established meanings in relevant research fields?
9. Where D-System terminology conflicts with established terminology?
10. Which distinctions actually improve implementation or reasoning performance?

---

# 2. Core research method

Every candidate term must pass the following analysis.

## A. Definition

Write the narrowest useful definition.

The definition should identify necessary characteristics without accidentally including neighboring concepts.

## B. Positive examples

Provide at least three examples that clearly fit.

## C. Counterexamples

Provide at least three superficially similar cases that should *not* fit.

Counterexamples are mandatory because they expose weak definitions faster than examples.

## D. Boundary cases

Identify ambiguous cases and explain why classification is difficult.

## E. Relationships

Determine how the term relates to all neighboring concepts.

Use statements such as:

```text
Belief IS_STANCE_TOWARD Claim
Evidence SUPPORTS Claim
Observation MAY_SERVE_AS Evidence
Decision PRODUCES Directive
Task MAY_SATISFY Commitment
Memory RETAINS Experience
Retrieval SELECTS Context
```

These are hypotheses until validated.

## F. Temporal behavior

Ask:
- Can this concept change?
- If so, does it mutate or produce a successor state?
- Can it be superseded?
- Can it expire?
- Can it be contradicted?
- Does it have valid-time and transaction-time semantics?

## G. Actor dependence

Ask:
- Does the concept exist independently of an actor?
- Is it inherently actor-relative?
- Can multiple actors hold different instances/states simultaneously?

Example:

```text
Claim: actor-independent proposition candidate
Belief: inherently actor-relative
```

## H. Epistemic applicability

Ask:
- Can this concept meaningfully be true/false?
- supported/unsupported?
- valid/invalid?
- fulfilled/unfulfilled?
- completed/incomplete?

Do not force factual epistemic vocabulary onto prescriptive concepts if a different status model is required.

## I. Representation candidate

Classify the concept provisionally as one or more of:

- first-class state/node,
- transition/activity,
- semantic relationship,
- actor relationship,
- property,
- composite/subgraph,
- derived metric,
- runtime construct,
- system capability,
- user-facing abstraction only.

## J. Existing terminology

Search relevant research fields for established equivalents.

Do not invent new terminology where an established term has adequate semantics.

---

# 3. Terms to investigate

## Tier 1 — Foundational

These should be resolved first because other definitions depend on them.

1. Information
2. Representation
3. State
4. Knowledge
5. Memory
6. Context
7. Experience
8. Actor
9. Event
10. Transition

## Tier 2 — Epistemic / reasoning

11. Claim
12. Proposition
13. Belief
14. Assumption
15. Hypothesis
16. Observation
17. Evidence
18. Inference
19. Conclusion
20. Confidence
21. Certainty
22. Truth
23. Validity
24. Reliability
25. Authority
26. Trust
27. Conflict
28. Consensus
29. Corroboration
30. Convergence

## Tier 3 — Ideation / planning / action

31. Idea
32. Question
33. Proposal
34. Alternative
35. Decision
36. Directive
37. Goal
38. Plan
39. Commitment
40. Obligation
41. Task
42. Action
43. Outcome
44. Retrospective insight

## Tier 4 — Temporal / lineage

45. History
46. Provenance
47. Lineage
48. Version
49. Revision
50. Supersession
51. Retraction
52. Temporal validity
53. Recency
54. Sequence
55. Episode

## Tier 5 — System behavior

56. Retrieval
57. Recall
58. Reasoning
59. Learning
60. Forgetting
61. Consolidation
62. Reflection
63. Context construction
64. Knowledge transfer
65. Conflict resolution

---

# 4. High-priority conceptual collisions

These pairs/groups should receive explicit comparative analysis.

## Idea vs. Claim vs. Thought

Questions:
- Does every idea assert something?
- Can questions be ideas without being claims?
- Is "idea" a user-facing umbrella rather than a formal ontology class?

## Information vs. Knowledge

Questions:
- Does D-System need the philosophical true-belief implications of "knowledge"?
- Should "knowledge" simply mean structured retained information at the system level?

## Memory vs. Knowledge

Questions:
- Is memory the retained representation, the retention mechanism, the retrieval capability, or some combination?
- Does semantic knowledge count as memory?
- Should D-System distinguish episodic and semantic memory?

## Memory vs. History

Questions:
- Can history exist without being retrievable?
- Is memory history plus relevance/retrievability?
- Does memory require influence on later behavior?

## Experience vs. Event

Questions:
- Is experience an episode containing multiple events?
- Must experience be actor-relative?
- Can an automated system have an "experience" in a useful technical sense?

## Observation vs. Evidence

Questions:
- Is evidence an intrinsic type or a contextual role?
- Can the same observation support one claim and challenge another?

## Claim vs. Belief

Questions:
- Is a claim actor-independent?
- Is belief best represented as a reified actor-claim stance?
- How should confidence attach to belief versus claim?

## Truth vs. Validity vs. Confidence

Questions:
- Truth concerns the proposition?
- Validity concerns scope/method/use?
- Confidence concerns an actor/system's degree of belief?
- How should temporally true facts be represented?

## Authority vs. Reliability vs. Trust

Questions:
- Authority = permission/legitimacy?
- Reliability = empirical performance?
- Trust = willingness to rely?
- Should these remain completely separate?

## Decision vs. Directive

Working hypothesis:

```text
Alternatives
    |
    | DECIDE
    v
Directive
```

Test whether established decision-provenance literature supports or challenges this model.

## Task vs. Commitment

This is especially important to the originating workload application.

A task is work to perform.

A commitment is an obligation to another actor, oneself, a team, a deadline, or an outcome.

Determine whether commitments should generate tasks rather than be represented as tasks.

## Event vs. Transition

Working distinction:

```text
Event = occurrence in represented world
Transition = change in D-System representation/reasoning
```

Test against event calculus, event sourcing, temporal databases, provenance models, and process ontologies.

## State vs. Version

State is semantic; version is implementation-level.

Test whether this distinction holds across event-sourced and temporal KG literature.

## Provenance vs. Lineage vs. History

Determine whether:
- history = temporal sequence,
- lineage = derivational ancestry,
- provenance = richer origin/explanation including lineage + actors + methods + evidence.

## Retrieval vs. Recall

Determine whether "recall" is useful as an agent/cognitive concept or whether retrieval is sufficient.

## Learning vs. State Transition

Is learning:
- any durable state change caused by experience,
- a particular family of transitions,
- or a system-level capability inferred from changed future behavior?

---

# 5. Cross-disciplinary literature domains

The terminology investigation should deliberately search outside computer science subfields that use D-System-like vocabulary.

## Knowledge representation
- Semantic Web
- RDF/OWL
- knowledge graphs
- ontologies
- provenance

## Epistemology and formal reasoning
- epistemic logic
- doxastic logic
- belief revision
- defeasible reasoning
- argumentation theory
- truth maintenance systems

## Cognitive science
- episodic memory
- semantic memory
- working memory
- autobiographical memory
- learning
- experience

## AI agent systems
- agent memory
- long-term memory
- episodic agent memory
- reflection
- multi-agent belief
- context engineering

## Distributed systems / software architecture
- event sourcing
- CQRS
- append-only logs
- temporal databases
- version control
- state machines

## Organizational / decision science
- decision provenance
- commitments
- obligations
- collective decision-making
- organizational authority
- knowledge management

## Scientific knowledge representation
- nanopublications
- micropublications
- evidence graphs
- scientific argumentation
- provenance

---

# 6. Investigation template

For every term create a record using this structure:

```yaml
term:
working_definition:

examples:
  - 
  - 
  - 

counterexamples:
  - 
  - 
  - 

boundary_cases:
  -

closest_terms:
  -

distinguishing_test:

actor_dependent:
epistemically_evaluable:
temporally_scoped:

candidate_representation:
  - node
  - edge
  - transition
  - property
  - composite
  - derived
  - runtime
  - system_behavior

existing_academic_meanings:
  -

candidate_d_system_definition:

unresolved_questions:
  -

sources:
  -
```

---

# 7. Distinguishing-test requirement

Every important neighboring pair should eventually have a simple test.

Examples:

### Claim vs. Belief

> Can two actors disagree about it while referring to the same proposition?

If yes, the shared object is likely the **claim**; each actor's position is a **belief/stance**.

### Observation vs. Evidence

> Is the information being described by how it was acquired, or by how it is being used in an argument?

Acquisition suggests **observation**. Argumentative role suggests **evidence**.

### Event vs. Transition

> Did something change in the represented world, or did D-System's representation/reasoning change?

World occurrence suggests **event**. Representational evolution suggests **transition**.

### Task vs. Commitment

> Is this describing work to perform, or an obligation that must be satisfied?

Work unit suggests **task**. Obligation suggests **commitment**.

---

# 8. Representation matrix

After terminology research, produce a matrix:

| Concept | Node/State | Transition | Relationship | Property | Composite | Derived | Runtime/System |
|---|---:|---:|---:|---:|---:|---:|---:|
| Claim | ? | | | | | | |
| Belief | ? | | ? | | | | |
| Memory | | | | | ? | ? | ? |
| Experience | ? | | | | ? | | |
| Decision | | ? | | | ? | | |
| Evidence | ? | | ? | | | | |
| Context | | | | | ? | ? | ? |

Do not fill this based only on intuition. Fill it after comparative research.

---

# 9. Required adversarial questions

The investigation must try to falsify the following assumptions:

1. Every stored object needs all three D-System classifications.
2. "Idea" deserves to remain a formal primitive.
3. Memory is best understood through state-transition lineage.
4. Claims can exist independently of actor belief.
5. Evidence should be a node rather than a contextual role.
6. Decisions are transitions rather than states.
7. Directives should receive the same epistemic classification as descriptive claims.
8. Experiences deserve explicit representation rather than being reconstructed from subgraphs.
9. Authority should influence conflict resolution.
10. Independent convergence should strengthen epistemic weight.
11. Context is best treated as an ephemeral projection rather than persistent knowledge.
12. Event and transition are sufficiently distinct to justify separate concepts.

A failed assumption is a successful research outcome.

---

# 10. Deliverables

The terminology investigation should eventually produce:

1. **Canonical D-System glossary**
2. **Concept relationship diagram**
3. **Representation matrix**
4. **Academic terminology mapping**
5. **Rejected/merged terminology list**
6. **Open semantic questions**
7. **Ontology/schema recommendations**
8. **Migration implications for the existing implementation**
9. **Research citations supporting each important distinction**
10. **Change log explaining why definitions evolved**

---

# 11. Integration with the literature review

This investigation should run alongside, not after, the broader D-System novelty review.

When research discovers an established concept:

```text
D-System term
      |
      | maps_to
      v
Established term
```

record whether the outcome is:

- `ADOPT` — use established terminology directly.
- `SPECIALIZE` — D-System concept is a narrower specialization.
- `GENERALIZE` — D-System concept intentionally covers several established concepts.
- `DISTINGUISH` — similar words describe materially different concepts.
- `RENAME` — current D-System term is misleading.
- `MERGE` — distinction is unnecessary.
- `REJECT` — concept should not exist in the formal model.

---

# 12. Implementation guardrail

Until this investigation reaches a first stable synthesis:

> Do not treat the current glossary as a mandate to refactor the existing D-System implementation.

The existing idea/workload system is empirical input to the research. Its successful abstractions should be preserved where useful.

Research should inform migration only after conceptual distinctions demonstrate practical value.

The system grew from an actual need. The ontology should explain and improve that system, not replace useful working behavior merely for theoretical cleanliness.
