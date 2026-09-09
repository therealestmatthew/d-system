# D-System Knowledge & Cognition Glossary

**Status:** Working research vocabulary  
**Purpose:** Establish precise terminology before D-System's conceptual model is translated into storage schemas, APIs, or agent behavior.

> These definitions are working definitions, not claims of novelty or final alignment with established academic terminology. The literature review should test and revise them.

## 1. Foundational distinctions

D-System should distinguish:

- **represented content** from the system's memory capability,
- **claims** from actors' beliefs about claims,
- **observations** from inferences drawn from observations,
- **events in the represented world** from transitions in D-System's representation,
- **semantic state** from implementation versioning,
- **history** from provenance,
- **retained information** from information selected into active context.

A useful high-level lifecycle is:

```text
Experience
    |
    | retained / represented
    v
Memory / Knowledge Store
    |
    | retrieve
    v
Context
    |
    | reason
    v
Idea / Claim / Inference / Decision
    |
    | act / observe
    v
New Experience
```

This diagram is conceptual; it does not imply that every term is a database node type.

---

## 2. Information

### Working definition
Any representable content available to the system, regardless of whether it is true, useful, believed, remembered, or currently relevant.

### Examples
- A sentence from a document.
- A task deadline.
- A benchmark result.
- A false claim retained for historical purposes.
- An agent-generated hypothesis.

### Important distinction
Information is the broadest term in this glossary. Something can be information without being knowledge, evidence, memory, or context.

### Candidate representation
Umbrella concept rather than necessarily a concrete node type.

---

## 3. Idea

### Working definition
A represented unit of cognitive content introduced for consideration, development, combination, evaluation, or action.

### Examples
- "Maybe D-System should use PostgreSQL."
- "Commitments may need to be modeled separately from tasks."
- "Provenance could help resolve conflicting conclusions."

### Non-examples / boundary cases
- "Deployment failed at 14:32" is better represented as an observation/event claim.
- "Implement authentication by Friday" is better represented as a task/directive.
- A raw sensor measurement is an observation rather than an idea in the ordinary sense.

### Open issue
"Idea" was useful as the original application primitive, but it may be too narrow to serve as D-System's universal underlying primitive.

### Candidate representation
User-facing concept and/or subtype of a more neutral knowledge-state primitive.

---

## 4. Knowledge State

### Working definition
A semantically meaningful representation of something at a particular point in its reasoning or operational history.

A candidate abstraction is:

```text
S = (Content, O, E, L, TemporalScope, Metadata)
```

where:

- `O` = ontological classification,
- `E` = epistemic classification,
- `L` = lifecycle classification.

### Important distinction
A state is semantic. A database version is an implementation mechanism.

### Candidate representation
Core first-class object.

---

## 5. Claim

### Working definition
A proposition capable of being evaluated epistemically: supported, challenged, validated, falsified, uncertain, etc.

### Example
"Neo4j will outperform PostgreSQL for D-System's target traversal workload."

### Important distinction
A claim is what is asserted. It is not the same as an actor's belief in that assertion.

### Candidate representation
First-class knowledge state or proposition subtype.

---

## 6. Belief

### Working definition
An actor's epistemic stance toward a claim.

### Example

```text
Claim C17: "Neo4j is preferable for D-System."

Human A  -- SUPPORTS --> C17
Agent B  -- REJECTS  --> C17
Agent C  -- UNCERTAIN --> C17
```

### Important distinction
Multiple actors can hold incompatible beliefs about the same claim without requiring duplicate claims.

### Candidate representation
Likely actor-to-claim relationship or reified stance record when metadata is required.

---

## 7. Knowledge

### Working definition
Structured retained information available to the system for reasoning, retrieval, explanation, or action.

### Caution
In precise epistemic analysis, avoid using "knowledge" as a synonym for "true claim." D-System deliberately retains hypotheses, disagreement, superseded states, and falsified concepts.

### Candidate representation
System-level collective concept rather than a single node class.

---

## 8. Memory

### Working definition
Retained information about prior states, experiences, events, transitions, and relationships that can influence later reasoning or action.

### Key hypothesis
Memory is not necessarily a node type.

D-System's richer memory may emerge from:

```text
retained states
+ transitions
+ temporal ordering
+ provenance
+ relationships
+ retrieval capability
```

### Important distinction
An idea has semantic content. Memory describes persistence and later influence across time.

### Research question
How does this definition compare with agent-memory literature, cognitive memory taxonomies, episodic/semantic memory, event sourcing, and temporal knowledge representation?

### Candidate representation
Derived/system capability, potentially with explicit memory structures where required.

---

## 9. Experience

### Working definition
A temporally bounded sequence of events, observations, actions, outcomes, and resulting state transitions involving one or more actors.

### Example

```text
Requirement changed
    ->
Architect observed change
    ->
Prior directive reconsidered
    ->
Alternatives reevaluated
    ->
New directive selected
    ->
Implementation changed
    ->
Outcome observed
```

The whole episode can be treated as an experience.

### Important distinction
Experience is the occurrence/episode; memory is the retained representation capable of influencing later behavior.

### Candidate representation
Composite/subgraph, episode object, or derived temporal window. Requires research.

---

## 10. Observation

### Working definition
A recorded perception, measurement, or detection concerning the represented world.

### Example
"Median query latency was 420 ms during benchmark B17."

### Important distinction

```text
Observation:
"Latency was 420 ms."

Inference:
"At this latency, the current architecture will not satisfy the target SLA."
```

Keeping these separate preserves reasoning provenance.

### Candidate representation
First-class state/claim with observation-specific provenance.

---

## 11. Evidence

### Working definition
Information used to support, challenge, validate, falsify, or otherwise alter the epistemic treatment of a claim or transition.

### Important properties
Evidence may itself have:
- provenance,
- methodology,
- actor/source,
- timestamp,
- confidence,
- applicability,
- dependencies on other evidence.

### Candidate representation
First-class object or role played by another knowledge object. Research should determine which is cleaner.

---

## 12. Inference

### Working definition
The derivational process by which a new proposition is produced from existing information, claims, evidence, rules, or observations.

### Example

```text
Observation(s) + Requirements
        |
        | INFER
        v
Conclusion
```

### Candidate representation
Transition/activity rather than resulting node type; the result may be a claim/conclusion.

---

## 13. Conclusion

### Working definition
A proposition produced as the outcome of an evaluation, inference, investigation, or synthesis.

### Important distinction
A conclusion need not be a final organizational commitment.

```text
Conclusion
    |
    | DECIDE
    v
Strategic Directive
```

### Candidate representation
Knowledge state with derivational provenance.

---

## 14. Decision

### Working definition
A transition or resolution process that selects among alternatives and establishes commitment or direction.

### Working hypothesis
Decision is better modeled primarily as a transition/activity than as a lifecycle node classification.

### Example

```text
Evaluated alternatives
       |
       | DECIDE
       v
Strategic Directive
```

### Candidate representation
First-class transition/activity with actor, authority, rationale, alternatives, and evidence.

---

## 15. Directive

### Working definition
A prescriptive state establishing intended direction, policy, commitment, or goal.

### Example
"Use PostgreSQL for D-System V1."

### Important distinction
A directive is not primarily a descriptive truth claim. Its epistemic treatment may therefore require different semantics from factual claims.

### Candidate representation
First-class state; currently associated with lifecycle classification `Strategic Directive`.

---

## 16. Task

### Working definition
A bounded executable unit of intended action, generally derived from a directive, plan, commitment, obligation, or operational need.

### Candidate representation
First-class state; currently associated with lifecycle classification `Operational Task`.

---

## 17. Commitment

### Working definition
An obligation accepted by an actor or group to perform, deliver, maintain, or honor something.

### Why it matters
A commitment is not necessarily identical to a task. One commitment can generate many tasks, and a task can exist without representing an external commitment.

### Example
Commitment: "Deliver the architecture review by Friday."

Tasks:
- update diagram,
- run benchmarks,
- write findings,
- schedule review.

### Candidate representation
Likely first-class object/relationship because personal workload management was one of D-System's originating use cases.

---

## 18. Event

### Working definition
A distinct occurrence in the represented world.

### Example
"The production deployment failed."

### Important distinction
An event in reality is not the same as the transition by which D-System learns about or reacts to it.

```text
World Event
    |
    | OBSERVE / CAPTURE
    v
Represented State
```

### Candidate representation
First-class ontological category.

---

## 19. Transition

### Working definition
A typed transformation or derivational relationship by which one or more represented states produce, influence, supersede, or lead to one or more subsequent states.

### Candidate abstraction

```text
S_t --[T, P]--> S_t+1
```

where:
- `T` = transition type/verb,
- `P` = provenance.

### Candidate representation
First-class record, even if graph APIs expose it as an edge.

---

## 20. Provenance

### Working definition
The origin and derivational lineage of a state or transition, including relevant actors, evidence, methods, authority, time, and upstream dependencies.

### Questions provenance should answer
- Who initiated this?
- Who participated?
- Who approved it?
- What evidence was used?
- How was the evidence generated?
- Which prior states influenced the result?
- Was authority delegated?
- Are apparently independent conclusions actually derived from the same source?

### Candidate representation
Structured first-class metadata/subgraph attached to transitions and evidence.

---

## 21. History

### Working definition
The temporally ordered record of states, events, and transitions.

### Important distinction
History answers **what happened and in what order**.

Provenance answers **where something came from and through whom/what process**.

### Candidate representation
Derived from append-only state/transition records rather than stored as a separate duplicated object.

---

## 22. Context

### Working definition
The subset of available information selected as relevant to a particular reasoning, communication, or action episode.

### Important distinction

```text
Stored knowledge/memory != active context
```

Context is selected.

### Research significance
D-System's potential contribution may involve constructing context using epistemic topology, provenance, dissent, authority, and reasoning lineage rather than semantic similarity alone.

### Candidate representation
Ephemeral/derived runtime object.

---

## 23. Retrieval

### Working definition
The process of selecting retained information, states, experiences, or reasoning lineage for inclusion in active context.

### Candidate D-System distinction
Retrieval may consider:
- semantic relevance,
- current/superseded status,
- temporal applicability,
- epistemic status,
- provenance,
- actor authority,
- evidence,
- independent convergence,
- dissent,
- unresolved uncertainty.

### Candidate representation
System behavior / algorithm.

---

## 24. Reasoning

### Working definition
A process that transforms available context into new claims, evaluations, conclusions, plans, decisions, or actions.

### Candidate representation
Process composed of transitions and possibly explicit reasoning traces. Exact treatment requires research.

---

## 25. Actor

### Working definition
An identifiable participant capable of generating, observing, evaluating, authorizing, transforming, or acting upon information.

### Candidate actor classes
- Human
- AI agent
- Group/team
- Organization
- Automated system

### Important distinction
Actor identity, actor type, domain authority, authorization, and historical reliability should not be collapsed into a single scalar weight.

---

## 26. Authority

### Working definition
The context-dependent legitimacy or permission of an actor to make, approve, enforce, or supersede a particular kind of transition or directive.

### Important distinction
Authority is not identical to epistemic reliability.

A manager may have authority to approve a deployment without being the most technically reliable source regarding database performance.

---

## 27. Reliability

### Working definition
An empirically informed estimate of how dependably an actor, source, process, or system has produced accurate/useful outputs within an applicable domain and context.

### Candidate representation
Derived metric, not a universal static actor property.

---

## 28. Convergence

### Working definition
The condition in which multiple reasoning/evidence paths arrive at materially compatible conclusions or states.

### Key requirement
Convergence should be weighted by independence.

```text
Five repetitions of one source
!=
five independent confirmations
```

### Candidate representation
Derived graph/topological signal.

---

## 29. Conflict

### Working definition
A condition in which claims, beliefs, directives, observations, or transition outcomes are mutually incompatible within an applicable scope.

### Important distinction
Conflict should generally be represented rather than immediately erased.

### Candidate statuses
- unresolved,
- contested,
- dominant,
- superseded,
- reconciled.

---

## 30. Version

### Working definition
An implementation-level representation of change to a stored object.

### Important distinction
Version is not synonymous with semantic state. A state transition may create a new version, a new node, multiple nodes, or another representation depending on implementation.

---

# Summary model

```text
REAL / EXTERNAL WORLD
        |
        | events / observations / inputs
        v
REPRESENTED INFORMATION
        |
        +--> Idea
        +--> Claim <---- Belief (actor stance)
        +--> Observation
        +--> Evidence
        +--> Directive
        +--> Task / Commitment
        +--> Event representation
        |
        | typed transitions + provenance
        v
EVOLVING KNOWLEDGE STATES
        |
        | retained through time
        v
MEMORY / HISTORY
        |
        | retrieval
        v
CONTEXT
        |
        | reasoning + action
        v
NEW STATES / TRANSITIONS / EXPERIENCES
```

## Design rule

No term in this glossary should automatically become a database table, node label, or edge type merely because it has been defined conceptually.

**Conceptual ontology first. Storage ontology second.**
