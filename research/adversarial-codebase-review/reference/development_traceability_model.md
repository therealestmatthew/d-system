# Development Traceability Model

## 1. Purpose

Define the minimum semantic relationships needed to trace cognition and knowledge into implemented systems and observed outcomes.

This is a conceptual relationship model, not a database schema.

## 2. Core chain

```text
Idea / Observation / Commitment
        |
        | informs
        v
Claim / Problem / Need
        |
        | evaluated_with
        v
Evidence / Alternatives
        |
        | DECIDE
        v
Decision / Directive
        |
        | derives
        v
Requirement
        |
        | constrained_by
        v
Constraint
        |
        | formalized_as
        v
Specification / Design
        |
        | planned_by
        v
Plan
        |
        | decomposed_into
        v
Phase
        |
        | contains
        v
Task
        |
        | produces
        v
Artifact / Code / Test
        |
        | realizes
        v
Functionality
        |
        | deployed_as
        v
Running System
        |
        | emits / produces
        v
Telemetry / Event / Outcome
        |
        | observed_as
        v
Observation
        |
        | supports / challenges
        v
Knowledge State
```

## 3. Candidate relationship vocabulary

### Knowledge-to-intent
- `INFORMS`
- `MOTIVATES`
- `SUPPORTS`
- `CHALLENGES`
- `ASSUMES`
- `CONCLUDES`
- `DECIDES`
- `AUTHORIZES`

### Intent-to-specification
- `DERIVES_REQUIREMENT`
- `IMPOSES_CONSTRAINT`
- `SATISFIED_BY`
- `FORMALIZED_AS`
- `SPECIFIED_BY`
- `DESIGNED_BY`

### Specification-to-execution
- `PLANNED_BY`
- `DECOMPOSED_INTO`
- `DEPENDS_ON`
- `ASSIGNED_TO`
- `EXECUTED_IN`
- `CONSUMES_CONTEXT`

### Execution-to-artifact
- `PRODUCES`
- `MODIFIES`
- `IMPLEMENTS`
- `TESTS`
- `VERIFIES`
- `FAILS_CRITERION`

### Artifact-to-reality
- `DEPLOYED_AS`
- `REALIZES`
- `PROVIDES_CAPABILITY`
- `EMITS`
- `CAUSES`

### Reality-to-knowledge
- `OBSERVED_AS`
- `MEASURED_BY`
- `GENERATES_EVIDENCE`
- `CORROBORATES`
- `CONTRADICTS`
- `TRIGGERS_RECONSIDERATION`

## 4. Trace queries the system should eventually support

### Why does this code exist?
Traverse backward from artifact/code to:
- phase,
- plan,
- specification,
- requirement,
- decision,
- rationale/evidence,
- originating idea/need.

### What became of this idea?
Traverse forward into:
- decisions,
- requirements,
- plans,
- artifacts,
- functionality,
- observed outcomes.

### Which code depends on this assumption?
Traverse dependency/provenance paths from assumption through decisions and specifications to artifacts.

### Which requirements are unimplemented?
Find requirements with no verified realization path.

### Which implemented functions have no current justification?
Find functionality whose upstream requirement/decision has been superseded, retracted, or lost.

### Which decisions have not been realized?
Find authorized decisions with no downstream verified implementation.

### Which runtime observations challenge design assumptions?
Connect telemetry/observations back to assumptions and claims.

### What changed because of this retrospective insight?
Traverse the next cycle from insight into revised decisions, plans, and artifacts.

## 5. Trace integrity

A trace should not be considered complete merely because a path exists.

Candidate integrity properties:

- provenance is known,
- relationship type is explicit,
- temporal order is coherent,
- decision authority is known,
- requirement scope is known,
- artifact version is identified,
- verification evidence exists,
- deployment/environment is identified,
- observed outcome refers to the correct deployed version.

These properties should be researched before formalization.
