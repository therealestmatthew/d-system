# 1. Purpose and Research Boundary

D-System is an extremely early-stage system. The repository is less than 48 hours old at this research pause.

Development was intentionally interrupted for architectural and prior-art investigation. The implementation is therefore a baseline, not a finished architecture. This document captures the project's state before formal literature review. No novelty conclusions have yet been established.

> Absence from the current implementation must not be interpreted as evidence that a proposed mechanism failed. In many cases implementation simply has not reached that stage.

**Provenance**: `REPOSITORY_EVIDENCE` (Repository age and commit history)

# 2. Original Problem and Motivation

The broader architecture emerged from attempting to connect:

```text
Ideas
-> Plans
-> Development
-> Functioning Systems
-> Observed Experience
-> New Knowledge
```

The system originally attempted to solve the problem of maintaining a consistent, traceable path from raw captured thoughts and ideas through the development lifecycle, ensuring that implementation intent is preserved and can be updated by observed experience.

**Provenance**: `REPOSITORY_EVIDENCE` (Ideas log, plans, memory context) and `CONCEPTUAL_PROPOSAL` (Two-system architecture connection)

# 3. Implemented Baseline

Describe only what is demonstrably implemented.

*   **Persistence**: Uses JSON source files (e.g., `_data/ideas.jsonl`) with a DuckDB rebuild process (`tools/rebuild_db.py`) that drops and recreates SQL projections, not incrementally. Ideas use an append-only JSONL format. Other records are mutable files.
*   **Idea/event handling**: `src/db/ideas.py` implements an append-only event log for ideas with typed transitions (`created`, `status`, `revisited`, `amended`, `annotated`, `linked`).
*   **Workload handling**: `schemas/backlog.schema.json` defines a one-session plan phase backlog with locks, dependencies, and evidence obligations (`session_budget: 1`).
*   **Memory**: `brain/` holds Markdown entries with YAML frontmatter containing 5 types (concept, entity, procedure, episode, decision).
*   **Retrieval/Context construction**: `tools/load_context.py` selects records into Markdown using substring/metadata SQL retrieval ranked by confidence and date. There are no embeddings, graph expansion, or topology-aware retrieval.
*   **Plans/Phases/Tasks**: Phases are bounded planned outcomes. Agent execution is mediated by instructions (AGENTS.md).
*   **ADRs/Requirements**: ADRs exist in `docs/04-decisions/` but are just Markdown files, untracked by the relational graph.
*   **Development/session evidence**: Session records capture work in `docs/03-sessions/`.
*   **Code/test traceability**: There is no direct code/test traceability in the implemented graph.
*   **Human/agent boundaries**: Handled implicitly through `author` fields in annotations and agent logs.
*   **Projections/materialized state**: Handled by DuckDB via `sql/001_schema.sql`.
*   **Correction/history behavior**: Append-only log corrections are handled by `amended` events in ideas.py without rewriting history.

**Provenance**: `REPOSITORY_EVIDENCE` (`01_actual_architecture.md`, `03_conceptual_vs_implemented.md`, `schemas/*`, `src/db/ideas.py`)

> What did the working system actually do when development was paused?
It acted as a local workload record store, an event-sourced idea notebook, a curated Markdown memory store, and a document-governance work scheduler.

# 4. Work Already Planned or In Progress

The following mechanisms and features were already planned or partially implemented before the research pause.

*   **Derive plan status consistency from phase state**
    *   **Status**: `PLANNED_BEFORE_RESEARCH` (Queued)
    *   **Evidence**: `backlog.yaml` (`phase-idea-05`)
*   **Implement structuring, evidence scoring and routing**
    *   **Status**: `PLANNED_BEFORE_RESEARCH` (Queued)
    *   **Evidence**: `backlog.yaml` (`phase-cap-05`)
*   **Enforce source references and global identities**
    *   **Status**: `PLANNED_BEFORE_RESEARCH` (Queued)
    *   **Evidence**: `backlog.yaml` (`phase-rel-03`)
*   **Correct global-memory and all-results retrieval**
    *   **Status**: `PLANNED_BEFORE_RESEARCH` (Queued)
    *   **Evidence**: `backlog.yaml` (`phase-rel-08`)
*   **Reconcile memory-agent contracts with accepted choices**
    *   **Status**: `PLANNED_BEFORE_RESEARCH` (Queued)
    *   **Evidence**: `backlog.yaml` (`phase-mem-01`)

**Provenance**: `EXISTING_PLAN` (`docs/09-backlog/backlog.yaml`)

# 5. Proposed Architecture at Research Pause

`PROPOSED ARCHITECTURE — NOT YET VALIDATED`

The conceptual architecture developed before formal literature review proposes a two-system model.

## Knowledge Construction & Management System (KCMS)
Concerns include: information, ideas, observations, claims, assumptions, hypotheses, beliefs, evidence, inference, conclusions, decisions, provenance, memory, context, conflict, convergence, authority, learning.

## Implementation & Experience System (IES)
Concerns include: requirements, constraints, acceptance criteria, specifications, plans, phases, tasks, artifacts, code, tests, deployments, functionality, runtime events, telemetry, outcomes, feedback.

The proposed lifecycle is:
```text
Ideation
-> Reasoning
-> Decision
-> Requirements
-> Specification
-> Plan
-> Phase
-> Implementation
-> Verification
-> Deployment
-> Runtime Observation
-> Outcome / Experience
-> Reflection / Learning
-> Revised Knowledge
-> New Ideation
```

**Provenance**: `CONCEPTUAL_PROPOSAL` (`architecture.md`, `two_system_architecture.md`)

# 6. Proposed State Model

The proposed architecture introduces three independent classification dimensions for knowledge states.

## Ontological
```text
Concepts & Mental Models
Artifacts & Entities
Processes & Workflows
Events
```

## Epistemic
```text
Axioms & Ground Truths
Hypotheses & Assumptions
Anti-Patterns & Falsified Concepts
```

## Lifecycle
```text
Generative Seeds
Strategic Directives
Operational Tasks
Retrospective Insights
```

The candidate abstraction is:
```text
S = (Content, O, E, L, TemporalScope, Metadata)
```

**Unresolved Questions**:
* Must every node receive all three classifications?
* Is Ground Truth verification, permanence, or both?
* How are temporally true facts represented?
* Should prescriptive states receive epistemic classifications?
* Is Lifecycle actually temporal?
* Should validity and immutability be separated?

**Provenance**: `CONCEPTUAL_PROPOSAL` (`architecture.md`, `ARCH-005`) and `OPEN_QUESTION`.

# 7. Proposed Transition and Memory Model

The working hypothesis is:
```text
S_t --[T, P]--> S_t+1
```
where:
```text
T = typed transition
P = provenance
```

There is a proposed distinction between:
```text
Semantic relationships
```
and:
```text
State-transition relationships
```

> Nodes represent states of knowledge; transition lineage preserves much of the history that gives those states meaning.

The proposition that "memories are edges" is a hypothesis requiring conceptual and literature investigation, not an established conclusion.

Candidate transition vocabulary includes: Extends, Supersedes, Relates To, Amends.

**Provenance**: `CONCEPTUAL_PROPOSAL` (`architecture.md`, `transition_vocabulary.md`) and `OPEN_QUESTION`

# 8. Proposed Provenance and Collective Reasoning Model

The candidate structure for knowledge and reasoning is:
```text
STATE
TRANSITION
PROVENANCE
WEIGHT
```

Potential provenance includes: actor, actor type, participants, evidence, rationale, method, authority, timestamp, lineage, independence.

The proposed actor model is:
```text
Human
Agent
Group
System
```

The hypothesis posits that epistemic weight may depend on:
```text
Evidence
Authority
Historical Reliability
Independence
Convergence
Temporal Relevance
```

A core concern is that repeated derivative agreement must not be treated as independent corroboration.

**Provenance**: `CONCEPTUAL_PROPOSAL` (`architecture.md`)


# 9. Proposed Ideation-to-Reality Traceability

The proposed forward lineage is:
```text
Idea
-> Claim
-> Decision
-> Requirement
-> Specification
-> Plan
-> Phase
-> Artifact / Code
-> Test
-> Deployment
-> Functionality
-> Runtime Outcome
```

The proposed backward lineage is:
```text
Functionality
<- Artifact / Code
<- Phase
<- Plan
<- Specification
<- Requirement
<- Decision
<- Evidence / Conclusion
<- Idea / Observation / Commitment
```

**Existing Traceability (Implemented)**:
Currently, traceability is limited to:
- Ideas linking to other ideas (`extends`, `supersedes`, `relates_to`).
- Phases pointing to Parent Plans (`plan` field) and Documents pointing to other Documents (`depends_on`).
- Phases carrying `completion_evidence` paths pointing to files.
- The `promoted_to` field in ideas linking to generated document codes.
This implemented traceability is NOT the proposed epistemic traceability.

**Provenance**: `CONCEPTUAL_PROPOSAL` (`development_traceability_model.md`, `two_system_architecture.md`) and `REPOSITORY_EVIDENCE` (`06_traceability_audit.md`)

# 10. Phase Hypothesis

**Working definition**:
> A Phase is the smallest planned unit of work intended to be completed within one bounded agentic development session.

**Implemented meaning**:
In the repository, a Phase is a governed document record in `backlog.yaml` representing a bounded planned outcome with locks, dependencies, and evidence obligations, strictly constrained to `session_budget: 1`.

**Proposed future context-boundary behavior**:
```text
Phase
   ↓
Construct Context Package
   ↓
Agentic Development Session
   ↓
Artifacts + Decisions + Evidence + Failures + Questions
   ↓
Consolidation into Persistent Knowledge
```

The literature review must determine whether this is an established concept, equivalent to an episode, work package, task boundary, checkpoint, planning step, execution unit, or something meaningfully distinct.

**Provenance**: `CONCEPTUAL_PROPOSAL` (`phase_context_contract.md`), `REPOSITORY_EVIDENCE` (`backlog.schema.json`), and `OPEN_QUESTION`

# 11. Epistemic Blast Radius Hypothesis

**Working definition**:
> The set of downstream decisions, requirements, specifications, plans, artifacts, functionality, or conclusions whose justification materially depends on an assumption, claim, evidence source, or reasoning state that has been revised, falsified, weakened, or superseded.

Example:
```text
Assumption A17
    ↓ supports
Decision D4
    ↓ derives
Requirement R8
    ↓
Specification S3
    ↓
Plan / Phase P9
    ↓
Artifact C22
```

**Research question**:
> If A17 becomes invalid, can the system identify the downstream implementation and knowledge states requiring reassessment?

This mechanism is not claimed as novel. It may already be subsumed by prior-art areas such as:
- change impact analysis
- requirements traceability
- design rationale
- assumption dependency

**Provenance**: `CONCEPTUAL_PROPOSAL` (`implementation_glossary.md`) and `ADVERSARIAL_INFERENCE` (`10_adversarial_findings.md`)

# 12. Runtime-to-Knowledge Closure Hypothesis

The proposed loop:
```text
Knowledge
-> Decision
-> Requirement
-> Implementation
-> Runtime
-> Observation
-> Evidence
-> Revised Knowledge
```

This is distinct from the runtime/test/session evidence that currently exists in the implementation (which is limited to session transcripts and test command outputs).

Formal research must investigate:
- runtime verification
- requirements monitoring
- observability
- continuous requirements engineering
- self-adaptive systems
- MAPE-K
- DevOps feedback loops

**Provenance**: `CONCEPTUAL_PROPOSAL` (`two_system_architecture.md`) and `OPEN_QUESTION`

# 13. Implementation vs Proposed Architecture Matrix

| Mechanism | Status | Evidence | Research status |
|---|---|---|---|
| Append-only idea history | `IMPLEMENTED` | `src/db/ideas.py` | `UNKNOWN` |
| Generalized append-only knowledge state | `PROPOSED_DURING_EXPLORATION` | `architecture.md` | `OPEN_RESEARCH_QUESTION` |
| O/E/L classification | `PROPOSED_DURING_EXPLORATION` | `ARCH-005` | `OPEN_RESEARCH_QUESTION` |
| Typed state transitions | `PARTIALLY_IMPLEMENTED` | `schemas/idea.schema.json` | `UNKNOWN` |
| Semantic vs transition edges | `PROPOSED_DURING_EXPLORATION` | `architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Provenance | `PARTIALLY_IMPLEMENTED` | `schemas/idea.schema.json` | `UNKNOWN` |
| Actor model | `PROPOSED_DURING_EXPLORATION` | `architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Authority | `PROPOSED_DURING_EXPLORATION` | `architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Reliability | `PROPOSED_DURING_EXPLORATION` | `architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Independence-aware convergence | `PROPOSED_DURING_EXPLORATION` | `architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Conflict preservation | `PARTIALLY_IMPLEMENTED` | `ideas.jsonl` (annotations) | `UNKNOWN` |
| Memory persistence | `IMPLEMENTED` | `brain/` | `UNKNOWN` |
| Memory retrieval | `IMPLEMENTED` | `tools/load_context.py` | `UNKNOWN` |
| Graph-based memory | `PROPOSED_DURING_EXPLORATION` | `architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Topology-aware context | `PROPOSED_DURING_EXPLORATION` | `architecture.md` | `OPEN_RESEARCH_QUESTION` |
| ADR traceability | `PARTIALLY_IMPLEMENTED` | `docs/04-decisions/` | `UNKNOWN` |
| Requirement traceability | `PROPOSED_DURING_EXPLORATION` | `two_system_architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Plan | `IMPLEMENTED` | `docs/01-plans/` | `UNKNOWN` |
| Phase | `IMPLEMENTED` | `backlog.yaml` | `UNKNOWN` |
| Task | `PROPOSED_DURING_EXPLORATION` | `two_system_architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Phase context package | `PROPOSED_DURING_EXPLORATION` | `phase_context_contract.md` | `OPEN_RESEARCH_QUESTION` |
| Requirement-to-code lineage | `PROPOSED_DURING_EXPLORATION` | `two_system_architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Epistemic-to-code lineage | `PROPOSED_DURING_EXPLORATION` | `development_traceability_model.md` | `OPEN_RESEARCH_QUESTION` |
| Backward functionality-to-rationale lineage | `PROPOSED_DURING_EXPLORATION` | `development_traceability_model.md` | `OPEN_RESEARCH_QUESTION` |
| Epistemic blast radius | `PROPOSED_DURING_EXPLORATION` | `implementation_glossary.md` | `OPEN_RESEARCH_QUESTION` |
| Runtime observation | `PROPOSED_DURING_EXPLORATION` | `two_system_architecture.md` | `OPEN_RESEARCH_QUESTION` |
| Runtime-to-knowledge closure | `PROPOSED_DURING_EXPLORATION` | `two_system_architecture.md` | `OPEN_RESEARCH_QUESTION` |

**Provenance**: `ADVERSARIAL_INFERENCE` (`03_conceptual_vs_implemented.md`, `10_adversarial_findings.md`)

# 14. Preserve List

Implementation patterns identified by the adversarial review as `PRESERVE_UNLESS_DISPROVEN`. These are constraints on future redesign, not immutable requirements.

*   **Separation of source truth from disposable projections**: The raw JSON/JSONL sources (e.g., `_data/ideas.jsonl`) are the truth; DuckDB tables are disposable projections. Rebuilding drops and recreates tables. `REPOSITORY_EVIDENCE` (`tools/rebuild_db.py`).
*   **Raw capture before interpretation**: Ideas are captured as they occur (append-only log), without deduplication or merging at entry. `REPOSITORY_EVIDENCE` (`schemas/idea.schema.json`).
*   **Stable identities**: Entities use stable, short, lexicographically sortable identities (`eid`, `mem-*`). `REPOSITORY_EVIDENCE` (`src/db/ideas.py`).
*   **Event-addressed correction/history**: Corrections use `amended` events targeting an `eid` rather than mutating rows in place. `REPOSITORY_EVIDENCE` (`src/db/ideas.py`).
*   **Task/commitment/waiting-on distinctions**: The backlog clearly delineates active phases, blocked statuses, and single-session budgets. `REPOSITORY_EVIDENCE` (`schemas/backlog.schema.json`).
*   **Human judgment boundaries**: Non-owner author annotations are restricted in kind (e.g., `finding`), preserving the owner's unambiguous voice in the log. `REPOSITORY_EVIDENCE` (`schemas/idea.schema.json`).
*   **Existing traceability mechanisms**: Link types (`extends`, `supersedes`, `relates_to`) and document dependencies (`depends_on`) provide foundational traceability. `REPOSITORY_EVIDENCE` (`schemas/document.schema.json`, `schemas/idea.schema.json`).

**Provenance**: `ADVERSARIAL_INFERENCE` (`09_preserve_list.md`) and `REPOSITORY_EVIDENCE`.


# 15. H1–H11 Pre-Literature Hypothesis Register

The full reconstructed H1–H11 hypothesis register is maintained in a machine-readable format in:
```text
research/pre-literature-hypotheses.yaml
```
These hypotheses represent the exact state of reasoning prior to the literature review. They remain `UNTESTED_PRE_LITERATURE`. Lack of implementation does not falsify them.

# 16. Strongest Internal Challenges

The adversarial codebase review generated several strong arguments and challenges to the proposed architecture. These must be converted into literature-review targets rather than resolved by intuition:

*   D-System may be over-modeled.
*   D-System may be under-modeled.
*   Three classifications (Ontological, Epistemic, Lifecycle) may be unnecessary.
*   Three classifications may be insufficient.
*   Graph/state-transition memory may be unnecessary.
*   Audit logging may cover much provenance.
*   Requirements traceability may already solve substantial implementation lineage.
*   Phase may correspond to an established work-unit concept.
*   Knowledge and implementation may not require separate systems.
*   Knowledge and implementation may require separation.

**Provenance**: `ADVERSARIAL_INFERENCE` (`10_adversarial_findings.md`)

# 17. Formal Literature Review Questions

## A. Ontology and Knowledge Representation
1. **How is knowledge represented for mixed human-agent teams?**
   *Why it matters*: D-System proposes a 3-dimensional classification (O/E/L).
   *D-System mechanism*: O/E/L classification, idea schema.
   *Prior art*: IBIS, QOC, Semantic Web, concept mapping.

## B. Epistemics and Belief
2. **How is the epistemic status (belief, assumption, truth) of an artifact tracked?**
   *Why it matters*: Must distinguish between verified facts and assumptions.
   *D-System mechanism*: Epistemic classification dimension.
   *Prior art*: Epistemic logic, belief revision frameworks, Truth Maintenance Systems.

## C. Provenance
3. **How is reasoning history and lineage tracked across states?**
   *Why it matters*: To establish authority and resolve conflicts.
   *D-System mechanism*: Provenance weight, transition lineage.
   *Prior art*: PROV-O, Git-like versioning for knowledge.

## D. Memory and Context
4. **How do agents construct context from a graph of knowledge?**
   *Why it matters*: Current substring matching is insufficient for deep context.
   *D-System mechanism*: Topology-aware context transfer, Graph-based memory.
   *Prior art*: Agent memory systems, RAG, knowledge graph embeddings.

## E. Human-Agent Collective Reasoning
5. **How is convergence and independence assessed when humans and agents collaborate?**
   *Why it matters*: Derivative agreement shouldn't be treated as independent corroboration.
   *D-System mechanism*: Independence-aware convergence.
   *Prior art*: Argumentation theory, crowdsourcing consensus models.

## F. Requirements and Design Rationale
6. **How are architectural decisions and rationale preserved alongside code?**
   *Why it matters*: To trace functionality back to the 'why'.
   *D-System mechanism*: ADR traceability, decision schema.
   *Prior art*: Architecture Decision Records, Design rationale models.

## G. Software Traceability
7. **How does epistemic traceability differ from traditional requirements traceability?**
   *Why it matters*: Needs to trace beyond requirements to raw ideas and assumptions.
   *D-System mechanism*: Epistemic-to-code lineage, backward traceability.
   *Prior art*: Requirements Traceability Matrix, Trace recovery.
8. **How is epistemic blast radius calculated?**
   *Why it matters*: To know what code breaks when an assumption is invalidated.
   *D-System mechanism*: Epistemic blast radius.
   *Prior art*: Change impact analysis, assumption dependency graphs.

## H. Agentic Development
9. **What defines the boundary of an agent's work unit?**
   *Why it matters*: The definition of 'Phase' and its context package.
   *D-System mechanism*: Phase context boundary.
   *Prior art*: Task management, episode modeling in RL.

## I. Runtime Feedback
10. **How does runtime telemetry update upstream knowledge?**
    *Why it matters*: To close the loop from experience back to ideas.
    *D-System mechanism*: Runtime-to-knowledge closure.
    *Prior art*: MAPE-K, self-adaptive systems, DevOps loops.

## J. Integrated Architecture
11. **Does the integration of these systems represent a distinct architecture?**
    *Why it matters*: Testing H0 vs H6.
    *D-System mechanism*: KCMS + IES two-system model.
    *Prior art*: Integrated cognitive architectures (e.g., SOAR, ACT-R), DevSecOps pipelines.

**Provenance**: `ADVERSARIAL_INFERENCE` (`11_research_questions_generated.md`) and `CONCEPTUAL_PROPOSAL` (`protocols/*`)

# 18. Research Categories

## Established internally
Mechanisms demonstrably present in the current implementation (Not necessarily established scientifically):
*   Append-only event log (Ideas)
*   Event-addressed correction (`amended` events)
*   Governed document scheduler (Backlog, phases)
*   Curated Markdown memory store (`brain/`)
*   Disposable SQL projections (DuckDB rebuilds)

## Proposed
Mechanisms developed as D-System design ideas but not yet validated externally:
*   Three-dimensional state classification (O/E/L)
*   Typed state transitions representing reasoning history
*   Provenance-weighted epistemic conflict resolution
*   Independence-aware topological convergence
*   Topology-aware context package construction
*   Bidirectional epistemic traceability (Idea <-> Code)
*   Epistemic blast radius analysis
*   Runtime-to-knowledge closure loop

## Unknown
Questions that should remain unresolved until literature review:
*   Are three dimensions (O/E/L) necessary and sufficient?
*   Are memories simply edges in a graph?
*   Does "Phase" correspond to an established work-unit concept?
*   Do knowledge and implementation require strictly separate systems?

There is no "novel" category. Novelty has not been established.
