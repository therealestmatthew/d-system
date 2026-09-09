# Implementation-Side Glossary

These terms extend the D-System knowledge glossary across the knowledge-to-reality boundary.

## Requirement

A statement of a need, capability, behavior, quality, or condition that a resulting system or process is expected to satisfy.

**Distinguish from:** decision, specification, task.

A decision may generate a requirement; a requirement describes what must be satisfied.

---

## Constraint

A limitation on the acceptable solution space.

Examples:
- must use PostgreSQL,
- cannot transmit regulated data externally,
- must execute within 500 ms,
- must remain backward compatible.

A constraint can arise from reality, policy, architecture, regulation, prior decisions, or resource limitations.

---

## Acceptance Criterion

An explicit condition used to determine whether a requirement, phase, feature, or deliverable has been satisfactorily completed.

Acceptance criteria create a bridge between intent and verification.

---

## Specification

A structured description of intended system behavior, structure, interfaces, constraints, or implementation-relevant design.

A specification operationalizes requirements sufficiently to guide planning and implementation.

---

## Design

A proposed structural or behavioral solution for satisfying requirements and constraints.

Design should retain links to:
- requirements,
- alternatives,
- decisions,
- assumptions,
- rationale.

---

## Architecture Decision

A decision affecting significant system structure, technology, behavior, constraints, or long-lived design direction.

Architecture Decision Records (ADRs) are an important prior-art area for D-System research.

---

## Plan

An organized intended path from a defined starting state to a desired outcome.

A plan may contain ordered/dependent phases.

A plan is not itself execution.

---

## Phase

### D-System working definition

> The smallest planned unit of work intended to be completed within one bounded agentic development session.

A phase is an **execution and context boundary**, not necessarily the smallest action.

A phase may contain multiple tasks.

Candidate structure:

```yaml
phase:
  objective:
  inputs:
  context_requirements:
  requirements:
  constraints:
  decisions:
  tasks:
  dependencies:
  acceptance_criteria:
  expected_outputs:
  actual_outputs:
  unresolved_questions:
  resulting_knowledge:
```

This definition must be compared against established concepts such as episode, work package, checkpoint, task, sprint, step, transaction, and agent session.

---

## Task

A bounded executable action contributing to a phase, plan, requirement, commitment, or operational objective.

A task may be smaller than a phase.

---

## Development Session

A bounded period of human/agent execution in which a selected context is loaded and one or more planned actions are performed.

A session is a runtime occurrence.

A phase is a planned unit.

One phase may ideally map to one session under the current D-System hypothesis, but the model must handle interruption, failure, retries, and multi-session phases.

---

## Context Package

The deliberately constructed information supplied to an agent/human for execution of a phase.

Candidate contents:
- objective,
- relevant requirements,
- specification,
- applicable decisions,
- constraints,
- relevant prior knowledge,
- code locations,
- dependencies,
- prior phase outputs,
- known failures,
- open questions,
- acceptance criteria.

A context package is a projection of persistent knowledge, not the persistent knowledge itself.

---

## Artifact

A concrete output produced during development or operation.

Examples:
- source file,
- commit,
- test,
- schema,
- configuration,
- documentation,
- deployment package,
- generated report.

---

## Implementation

The realization of a design/specification through artifacts, code, configuration, infrastructure, procedures, or other operational mechanisms.

---

## Functionality / Capability

Observable behavior or ability provided by the implemented system.

Research question: whether `functionality` and `capability` require separate definitions.

---

## Verification

The process of determining whether an implementation or artifact satisfies its specified requirements, constraints, acceptance criteria, or design rules.

Verification asks approximately:

> Did we build what was specified?

---

## Validation

Potential implementation-side meaning:

> Does the realized system actually satisfy the underlying need or intended use?

This must be reconciled with D-System's epistemic use of `VALIDATE` as a transition verb.

Terminology collision is expected and should be researched.

---

## Test

A controlled procedure or executable check that produces evidence relevant to verification, validation, performance, reliability, or another property.

A test result is evidence; the test procedure is not identical to its result.

---

## Deployment

The transition by which an implementation becomes available in a target environment.

---

## Runtime Event

An occurrence produced or detected while the realized system operates.

Examples:
- request processed,
- error raised,
- job completed,
- service restarted,
- deadline missed.

---

## Telemetry

Recorded operational measurements emitted by a system.

Telemetry can become observation and evidence in the knowledge system.

---

## Outcome

The realized consequence of an action, implementation, decision, or system behavior.

An outcome may be intended or unintended.

---

## Feedback

Information generated by outcomes or observation and routed back into evaluation, reasoning, planning, or implementation.

Feedback closes the ideation-to-reality loop.

---

## Change Impact

The set of downstream states, artifacts, requirements, plans, functionality, or operations potentially affected by a changed upstream state.

---

## Epistemic Blast Radius

### D-System working term

The set of downstream decisions, requirements, specifications, plans, artifacts, functionality, or conclusions whose justification depends materially on an assumption, claim, evidence source, or reasoning state that has been revised, falsified, weakened, or superseded.

Example:

```text
Assumption A17 --supports--> Decision D4
D4 --derives--> Requirement R8
R8 --specified_by--> S3
S3 --planned_by--> P9
P9 --implemented_by--> Code C22
```

If A17 is falsified, D-System should identify D4, R8, S3, P9, and C22 as candidates for reassessment.

This term is provisional and must be checked against established impact-analysis and requirements-traceability terminology.
