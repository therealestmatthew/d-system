# Research Agent Addendum: Knowledge-to-Implementation Lifecycle

Read this file in addition to the existing D-System research-agent instructions.

## Mission

Investigate the boundary between D-System's knowledge construction system and its implementation/execution system.

Your job is to find the strongest prior art for:

- decision-to-requirement derivation,
- rationale-to-design traceability,
- requirement-to-code/test traceability,
- agent session/context boundaries,
- software-development memory,
- runtime feedback to design knowledge,
- change impact from invalidated assumptions,
- end-to-end lifecycle provenance.

## Required adversarial behavior

For every candidate D-System mechanism, first formulate:

> "This already exists as ______."

Then search aggressively for the strongest framework that fills the blank.

## Special terminology warning

D-System's terms may differ from established fields.

Translate:

```text
D-System term                  Candidate research terms

Phase                          episode, work package, task boundary,
                               checkpoint, planning step, execution unit

Epistemic blast radius         change impact, impact analysis,
                               assumption dependency, rationale impact,
                               requirements volatility propagation

Knowledge-to-code lineage      traceability, digital thread,
                               design rationale, artifact provenance

Context package                task context, working set,
                               agent memory retrieval, session state,
                               execution context

Runtime-to-knowledge feedback  runtime verification, requirements
                               monitoring, feedback control, MAPE-K,
                               continuous requirements engineering
```

Do not conclude a concept is distinct because the phrase itself is uncommon.

## Required outputs

For each critical collision:
1. identify exact semantic overlap,
2. identify implementation overlap,
3. identify what D-System could reuse directly,
4. identify what remains uncovered,
5. identify whether D-System terminology should change,
6. update the relevant H7-H11 challenge.

## High-value collision

A source is `CRITICAL_COLLISION` if it can trace at least four adjacent stages in:

```text
Reasoning
 -> Decision
 -> Requirement
 -> Specification
 -> Plan
 -> Execution
 -> Artifact
 -> Verification
 -> Deployment
 -> Runtime Evidence
 -> Knowledge Update
```

A source that covers the entire loop requires independent review by a second research agent.
