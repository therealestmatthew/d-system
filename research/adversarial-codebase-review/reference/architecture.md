# D-System: Current Research Architecture

## 1. Core problem

D-System is an append-only knowledge architecture intended for collective human-agent reasoning. It aims to represent not only *what is known*, but:

- what kind of knowledge a state represents,
- how its truth status should be regarded,
- where it sits in an idea/action lifecycle,
- how it changed from prior states,
- who or what caused those changes,
- what evidence and rationale supported them,
- how conflicting transitions should be evaluated,
- and how reasoning lineage should affect later retrieval and knowledge transfer.

The fundamental distinction is:

> **State describes what the system represents at a point in reasoning history. Transition describes how one state became another. Provenance describes the lineage and responsibility of that transition.**

---

## 2. Knowledge-state classifications

Each knowledge state is classified across three independent dimensions.

### 2.1 Ontological classification — What is this?

1. **Concepts & Mental Models**  
   Theoretical constructs, principles, paradigms, abstractions, or conceptual models.

2. **Artifacts & Entities**  
   Concrete digital or physical outputs/entities, including systems, reports, code artifacts, commits, architectures, datasets, etc.

3. **Processes & Workflows**  
   Sequential operations, methods, and procedures describing how something is performed.

4. **Events**  
   Distinct occurrences in time, such as failures, deployments, meetings, or observed changes.

### 2.2 Epistemic classification — What is its truth status?

1. **Axioms & Ground Truths**  
   Claims currently accepted as verified/reliable within the applicable scope.

2. **Hypotheses & Assumptions**  
   Untested or provisionally accepted claims requiring validation.

3. **Anti-Patterns & Falsified Concepts**  
   Disproven theories, failed approaches, known dead ends, or explicitly rejected propositions retained to prevent cyclic mistakes.

> Open research issue: temporal validity should likely be represented separately from epistemic status. A proposition can have been true within a prior interval without becoming a falsified proposition.

### 2.3 Lifecycle classification — Where is it in its evolution?

1. **Generative Seeds**  
   Raw or developing ideas under consideration before commitment.

2. **Strategic Directives**  
   High-level commitments, goals, or plans that consolidate prior evaluation into direction.

3. **Operational Tasks**  
   Executable actions derived from strategic direction.

4. **Retrospective Insights**  
   Post-execution learning, gaps, technical debt, observations, or context discovered after action.

The lifecycle is not assumed to be strictly linear. Retrospective insights may trigger reconsideration and produce new generative seeds.

---

## 3. State-transition model

D-System treats the lifecycle as a graph of state transitions rather than mutable records.

Illustrative path:

```text
Not Considered
    |
    | CONSIDER
    v
Generative Seed
    |
    | HYPOTHESIZE / EVALUATE
    v
Evaluated Conclusion
    |
    | DECIDE
    v
Strategic Directive
    |
    | DECOMPOSE / PLAN
    v
Operational Task(s)
    |
    | EXECUTE
    v
Event / Artifact / Outcome
    |
    | OBSERVE / REFLECT
    v
Retrospective Insight
    |
    | RECONSIDER
    v
Generative Seed
```

Important interpretation:

- A **decision** need not be a node classification; `DECIDE` can be the transition that produces a Strategic Directive.
- A prior state is not overwritten when a new state appears.
- The reasoning lineage remains available for historical reconstruction and later challenge.

---

## 4. Two families of graph relationships

### 4.1 Semantic relationships

These describe relationships in the represented domain.

Examples:

- `ALTERNATIVE_TO`
- `DEPENDS_ON`
- `PART_OF`
- `IMPLEMENTS`
- `RELATES_TO`
- `USES`

### 4.2 State-transition relationships

These describe the evolution of knowledge or action.

Examples:

- `CONSIDER`
- `HYPOTHESIZE`
- `EVALUATE`
- `VALIDATE`
- `FALSIFY`
- `DECIDE`
- `DECOMPOSE`
- `EXECUTE`
- `OBSERVE`
- `REFLECT`
- `RECONSIDER`
- `SUPERSEDE`

This distinction is foundational: semantic edges model the world; transition edges model the history of reasoning and action.

---

## 5. Provenance

A transition is a first-class research object even if exposed ergonomically as a graph edge.

Proposed transition record:

```yaml
transition_id:
verb:
from_nodes: []
to_nodes: []

actors:
  initiator: []
  participants: []
  approvers: []

actor_types:
  - human
  - agent
  - group
  - system

evidence: []
rationale:
method:
timestamp:

authority_context:
domain:
role:
authorization:

lineage:
upstream_transitions: []
upstream_evidence: []
```

Provenance answers questions such as:

- Who initiated the transition?
- Who participated?
- Was the transition individual, collective, delegated, or automated?
- Which evidence was used?
- Which methods produced that evidence?
- What prior reasoning influenced the actor?
- Under what authority was the transition made?
- Were multiple supposedly independent transitions actually derived from the same source?

---

## 6. Conflict, authority, and convergence

D-System should preserve conflicting state-transition branches rather than deleting losing branches.

Example:

```text
                 +-- T1 --> State A
Prior State -----+
                 +-- T2 --> State B
```

Conflict resolution should not use a single global actor score.

A candidate epistemic weighting function may consider:

- **Evidence strength**
- **Domain-specific actor authority**
- **Historical actor/system reliability**
- **Independence of supporting paths**
- **Degree of corroboration/convergence**
- **Temporal relevance / recency**
- **Applicability to the current context**
- **Strength of contradictory evidence**
- **Formal authorization where decisions are organizational**

A useful conceptual form is:

```text
Weight = f(Evidence,
           DomainAuthority,
           Reliability,
           Independence,
           Convergence,
           TemporalRelevance,
           Contradiction)
```

This is intentionally not yet a finalized mathematical formula.

### Convergence

Repeated arrival at the same conclusion strengthens confidence only to the extent that the paths are meaningfully independent.

Five agents repeating one source should not be treated as five independent confirmations.

Independent human reasoning, separate experiments, telemetry, and distinct agents using non-overlapping evidence may constitute stronger convergence.

---

## 7. Memory interpretation

Working hypothesis:

> Nodes preserve states; transition lineage preserves much of what should be understood as memory.

A single frozen state is not sufficient to reconstruct change. Historical meaning often resides in the delta between states and in the transition that produced the delta.

This does **not** claim that all memory must literally be implemented as graph edges. It is a conceptual hypothesis to test against work in memory systems, temporal knowledge representation, event sourcing, provenance, and cognitive models.

---

## 8. Append-only principle

Prior states and transitions are retained.

Instead of mutating:

```text
Hypothesis -> Ground Truth
```

and losing the former state, D-System records a new state and the transition between them.

This permits:

- historical reconstruction,
- reasoning provenance,
- contradiction analysis,
- supersession chains,
- post-hoc audits,
- counterfactual analysis,
- reliability measurement,
- and knowledge transfer with rationale.

---

## 9. Knowledge transfer / retrieval

The intended retrieval primitive is richer than nearest-neighbor semantic search.

An agent should be able to retrieve:

- current dominant state,
- reasoning lineage,
- supporting evidence,
- dissenting branches,
- actor provenance,
- unresolved hypotheses,
- superseded directives,
- confidence/authority signals,
- and relevant temporal context.

Example desired output:

> PostgreSQL is the current strategic direction, reached through multiple evaluations, affirmed by authorized architecture actors, superseding an earlier alternative, with one unresolved concern around long-term traversal performance.

The research question is whether graph topology, provenance, and epistemic/lifecycle state can improve downstream reasoning compared with standard document or vector-memory retrieval.

---

## 10. Candidate formal abstraction

A state may be represented conceptually as:

```text
S = (O, E, L, Content, TemporalScope, Metadata)
```

where:

- `O` = ontological classification
- `E` = epistemic classification
- `L` = lifecycle classification

A transition may be represented as:

```text
S_t --[T, P]--> S_t+1
```

where:

- `T` = typed transition
- `P` = provenance

Provenance may contain:

```text
P = (Actors, Evidence, Method, Authority, Time, Lineage)
```

These are working abstractions, not yet a formal ontology or mathematical theory.

---

## 11. Current research boundary

No novelty claim is established.

The working hypothesis is that individual components overlap with substantial prior work, while possible differentiation may lie in the integration of:

> **typed multi-dimensional knowledge states + explicit state-transition semantics + provenance-weighted human/agent convergence and conflict + topology-aware context transfer.**

This hypothesis must be aggressively tested against prior art.
