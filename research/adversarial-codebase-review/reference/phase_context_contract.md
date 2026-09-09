# Phase Context Contract

## 1. Working hypothesis

A D-System **Phase** is the smallest planned unit of work intended to be completed during one bounded agentic development session.

Its deeper purpose is to provide a stable contract between persistent knowledge and ephemeral agent context.

```text
Persistent Knowledge
       |
       | context construction
       v
PHASE CONTEXT PACKAGE
       |
       | agentic execution
       v
Phase Outputs
       |
       | consolidation
       v
Persistent Knowledge
```

## 2. Phase input contract

A phase should be executable without requiring the agent to rediscover the entire project history.

Candidate inputs:

```yaml
phase_id:
plan_id:
objective:

upstream_intent:
  decisions: []
  requirements: []
  constraints: []
  acceptance_criteria: []

context:
  relevant_knowledge: []
  prior_phase_outputs: []
  relevant_artifacts: []
  code_locations: []
  known_failures: []
  unresolved_questions: []

execution:
  permitted_tools: []
  permissions: []
  expected_tasks: []
  dependencies: []

expected_outputs:
  artifacts: []
  tests: []
  documentation: []
  state_changes: []

completion_definition:
  acceptance_criteria: []
  verification_required: []
```

## 3. Phase output contract

After execution, the session should return more than code.

Candidate output:

```yaml
status:
actual_actions: []

artifacts_created: []
artifacts_modified: []
tests_run: []
verification_results: []

decisions_made_during_execution: []
new_assumptions: []
observations: []
new_evidence: []
failures: []
unexpected_findings: []
open_questions: []
technical_debt: []

requirements_satisfied: []
requirements_partially_satisfied: []
requirements_unsatisfied: []

recommended_followup: []
```

## 4. Consolidation

Phase outputs should be transformed into persistent states and transitions.

Examples:

```text
Agent discovered undocumented constraint
        |
        | CAPTURE
        v
New Constraint

Test disproved performance assumption
        |
        | FALSIFY
        v
Revised Knowledge State

Implementation required architectural choice
        |
        | DECIDE
        v
New Architecture Decision

Phase completed requirement
        |
        | VERIFY
        v
Requirement Satisfaction State
```

## 5. Failure and interruption

The one-phase/one-session mapping is an aspiration, not an invariant.

The model must support:
- interrupted session,
- failed phase,
- partial completion,
- retry,
- agent handoff,
- human escalation,
- phase split,
- requirement change during execution.

Research should determine whether phase identity survives these cases or successor phases should be created.

## 6. Research questions

1. Is "phase" the correct established term?
2. Is a phase better modeled as an episode, work package, checkpoint, transaction, or task?
3. What information maximizes execution quality without context overload?
4. How should context packages be evaluated?
5. What must always be returned from an agent session for reliable memory consolidation?
6. Can context packages be generated automatically from graph lineage?
7. How should conflicting upstream knowledge be represented in the context package?
8. When should dissenting/superseded information be included?
9. How should context construction change by agent role?
10. Can phase-level provenance support reproducible agentic development?
