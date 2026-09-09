# Traceability audit

Two real traces were attempted. These are current repository traces, not invented complete paths. `EXPLICIT` means an identifier/path/reference is written; `DERIVABLE` means code/content allows a human to establish the link; `AMBIGUOUS` means a plausible relationship lacks unambiguous semantics; `ABSENT` means the expected link was not found in the reviewed trace. An explicit link does not imply version fidelity or proof of satisfaction. Confidence HIGH for observed references, MEDIUM for derived interpretations.

## Trace A: raw capture functionality

The actual implemented behavior is CLI/inbox input → immutable raw JSON text record. A real completed phase names the governing decisions, requirement, implementation, test and session. [E32](../evidence/code-evidence.md#e32) (`src/capture/raw.py:63-128`) [E48](../evidence/code-evidence.md#e48) (`docs/09-backlog/backlog.yaml:2598-2648`)

| Forward expected link | Classification | Actual trace / break | Evidence |
|---|---|---|---|
| Idea → Decision | AMBIGUOUS | ADR-007 records an owner need/routing decision, but no verified originating idea ID is linked in the capture chain | `docs/04-decisions/ADR-007-capture-routing.md:17-30` (“zero broken promises”, “friction”); alternative: original discussion was the observation, not an idea entity |
| Decision → Requirement | EXPLICIT | REQ-002 depends_on doc-capture-routing and doc-record-types and points to ADR-007/008 | [E45](../evidence/code-evidence.md#e45) (`docs/06-requirements/REQ-002-capture-requirements.md:10-22`) |
| Requirement → Specification | AMBIGUOUS | Capture JSON Schema operationalizes part of R1, but no distinct specification artifact and typed derivation link | `schemas/capture.schema.json:5-7` (“verbatim…REQ-002 R2”); [E38](../evidence/code-evidence.md#e38) (`schemas/document.schema.json:37-128`) [E46](../evidence/code-evidence.md#e46) (`docs/06-requirements/REQ-002-capture-requirements.md:48-64`) |
| Specification → Plan | AMBIGUOUS | PLAN-009 plans schema and intake work and references requirements, but is not downstream of a separately identified specification | [E47](../evidence/code-evidence.md#e47) (`docs/01-plans/PLAN-009-capture-build.md:10-34`) |
| Plan → Phase | EXPLICIT | phase-cap-04 has plan: doc-capture-build | [E48](../evidence/code-evidence.md#e48) (`docs/09-backlog/backlog.yaml:2598-2648`) |
| Phase → Task | ABSENT | Scope steps exist as strings; no first-class task IDs or phase/task relationship | [E34](../evidence/code-evidence.md#e34) (`schemas/backlog.schema.json:144-240`) [E26](../evidence/code-evidence.md#e26) (`schemas/task.schema.json:5-44`) [E48](../evidence/code-evidence.md#e48) (`docs/09-backlog/backlog.yaml:2598-2648`) |
| Task → Artifact / Code | ABSENT | No task record in this trace. **Bypass:** phase directly names src/capture/raw.py and tools/capture.py | [E48](../evidence/code-evidence.md#e48) (`docs/09-backlog/backlog.yaml:2598-2648`) |
| Artifact / Code → Test | EXPLICIT | test/test_capture_intake.py imports/executes capture writer and CLI; phase names the test | [E49](../evidence/code-evidence.md#e49) (`test/test_capture_intake.py:1-65`) [E48](../evidence/code-evidence.md#e48) (`docs/09-backlog/backlog.yaml:2598-2648`) |
| Test → Deployment | ABSENT | Local CI/config test/build does not establish deployment of a tested version | [E61](../evidence/code-evidence.md#e61) (`.github/workflows/ci.yaml:1-41`) |
| Deployment → Functionality | ABSENT | No deployment identity/environment artifact found; local executable behavior is independently derivable | [E01](../evidence/code-evidence.md#e01) (`src/main.py:6-20`) [E32](../evidence/code-evidence.md#e32) (`src/capture/raw.py:63-128`) |
| Functionality → Runtime Outcome | EXPLICIT, local/manual only | Session records real CLI capture and repeated inbox scan; current probes exercise local behavior. No telemetry relation to deployed version | [E50](../evidence/code-evidence.md#e50) (`docs/03-sessions/SESS-2026-09-08-05-capture-intake.md:19-65`); [probe results](../evidence/review-probe-results.json) |

The observed shorter path is **ADR → requirement → plan → phase → code/tests → recorded local result**. Do not insert Task or Deployment to make the conceptual chain look complete.

| Backward expected link | Classification | What can actually be recovered | Evidence |
|---|---|---|---|
| Functionality ← Code | DERIVABLE | write_raw_capture and scan_inbox produce the behavior; CLI calls them | [E32](../evidence/code-evidence.md#e32) (`src/capture/raw.py:63-128`); `tools/capture.py:55-80` (“scan_inbox”, “write_raw_capture”) |
| Code ← Phase | EXPLICIT | Code module docstring names requirement/ADR; phase completion_evidence names code paths | [E48](../evidence/code-evidence.md#e48) (`docs/09-backlog/backlog.yaml:2598-2648`); `src/capture/raw.py:1-10` (“REQ-002 R1/R2, ADR-007”) |
| Phase ← Plan | EXPLICIT | Primary plan identifier resolves to PLAN-009 | [E48](../evidence/code-evidence.md#e48) (`docs/09-backlog/backlog.yaml:2598-2648`) [E47](../evidence/code-evidence.md#e47) (`docs/01-plans/PLAN-009-capture-build.md:10-34`) |
| Plan ← Specification | AMBIGUOUS | Plan/schema carry design information, but no independent specification edge | [E38](../evidence/code-evidence.md#e38) (`schemas/document.schema.json:37-128`) [E47](../evidence/code-evidence.md#e47) (`docs/01-plans/PLAN-009-capture-build.md:10-34`) |
| Specification ← Requirement | DERIVABLE | Raw schema description and source comments cite REQ-002; treating this as a specification is an analyst interpretation | `schemas/capture.schema.json:5-7`; [E46](../evidence/code-evidence.md#e46) (`docs/06-requirements/REQ-002-capture-requirements.md:48-64`) |
| Requirement ← Decision | EXPLICIT | Requirement frontmatter and prose cite the ADRs | [E45](../evidence/code-evidence.md#e45) (`docs/06-requirements/REQ-002-capture-requirements.md:10-22`) |
| Decision ← Evidence / Rationale | EXPLICIT, narrative | ADR-007 explains why capture precedes interpretation and why review depends on stakes; no versioned evidence IDs | `docs/04-decisions/ADR-007-capture-routing.md:17-40` (“friction”, “bad interpretation recoverable”) |
| Evidence / Rationale ← Idea / Observation / Commitment | AMBIGUOUS | Owner observations are narrated; no durable capture reference/idea identity proves original utterance | Same ADR context; alternative: adequate human rationale, not exact historical provenance |

The CRLF probe weakens the claimed raw fidelity requirement despite a completed phase and passing existing tests. Trace existence alone does not prove acceptance. [E46](../evidence/code-evidence.md#e46) (`docs/06-requirements/REQ-002-capture-requirements.md:48-64`) [E49](../evidence/code-evidence.md#e49) (`test/test_capture_intake.py:1-65`) [E50](../evidence/code-evidence.md#e50) (`docs/03-sessions/SESS-2026-09-08-05-capture-intake.md:19-65`) [E32](../evidence/code-evidence.md#e32) (`src/capture/raw.py:63-128`)

## Trace B: real idea promotion and triage implementation

Read-only inspection of `_data/ideas.jsonl:58` found structural metadata only:

```json
{"idea":"000007","event":"status","from":"open","to":"promoted","promoted_to":["PLAN-016"]}
```

No idea prose or portfolio content is reproduced. This is **EXPLICIT** idea → plan promotion, not idea → decision → requirement. The completed triage phase has `plan: doc-idea-record-system` and completion evidence `.claude/agents/idea-triage.md`, `.claude/commands/idea-triage.md`, `_data/ideas.jsonl`; its result calls this promotion a backfill. [E74](../evidence/code-evidence.md#e74) (`docs/09-backlog/backlog.yaml:3574-3626`)

Forward: idea → PLAN-016 → phase-idea-02 → prompt artifacts is explicit. The plan-to-phase edge bypasses Decision/Requirement/Specification/Task. The phase names `uv run pytest`, but no captured per-idea test invocation ID ties that idea's originating requirement to a particular outcome. Historical session reporting supports three real triage executions, not a deterministic replay of model reasoning. [E74](../evidence/code-evidence.md#e74) (`docs/09-backlog/backlog.yaml:3574-3626`) [E39](../evidence/code-evidence.md#e39) (`.claude/agents/idea-triage.md:15-41`) [E41](../evidence/code-evidence.md#e41) (`.claude/commands/idea-triage.md:62-91`)

Backward: triage behavior → agent/driver is **DERIVABLE** from instructions; artifact → completed phase → plan → promoted idea is **EXPLICIT** by paths/IDs and reverse lookup. Requirement/decision rationale is at best **DERIVABLE/AMBIGUOUS** from PLAN-016 and ADR-010 references in the agent. Draft REQ-003 R11 asks for a `triaging` state the implemented schema lacks, so using it as a fully satisfied trace would be false. [E39](../evidence/code-evidence.md#e39) (`.claude/agents/idea-triage.md:15-41`) [E40](../evidence/code-evidence.md#e40) (`.claude/agents/idea-triage.md:72-94`) [E53](../evidence/code-evidence.md#e53) (`docs/06-requirements/REQ-003-idea-plan-lifecycle.md:30-67`)

## Epistemic blast-radius test

Upstream decision tested: **store raw input before interpretation to make mistaken interpretation recoverable**, ADR-007. Counterfactual: normalization or archival replacement means the retained input is no longer the original evidence.

Known downstream candidates can be found manually: REQ-002 R1/R2 → PLAN-009 → phase-cap-03/04 → capture schema, raw writer, CLI, tests and operations/session documents. That search led to the CRLF counterexample. [E45](../evidence/code-evidence.md#e45) (`docs/06-requirements/REQ-002-capture-requirements.md:10-22`) [E46](../evidence/code-evidence.md#e46) (`docs/06-requirements/REQ-002-capture-requirements.md:48-64`) [E47](../evidence/code-evidence.md#e47) (`docs/01-plans/PLAN-009-capture-build.md:10-34`) [E48](../evidence/code-evidence.md#e48) (`docs/09-backlog/backlog.yaml:2598-2648`) [E32](../evidence/code-evidence.md#e32) (`src/capture/raw.py:63-128`)

Can the system identify **every** impacted artifact/capability automatically? **No; NOT_IMPLEMENTED.** `dependency_closure` walks phase prerequisites for scheduling; document depends_on does not distinguish supports, derives, implements or invalidates. Individual requirements are table/prose labels, code evidence names mutable paths, assumptions lack identities, model contexts are not stored, and no deployment/outcome graph exists. A reverse dependency search would overinclude ordering dependencies and underinclude implicit code/cross-document rationales. [E35](../evidence/code-evidence.md#e35) (`src/governance/backlog.py:30-84`) [E38](../evidence/code-evidence.md#e38) (`schemas/document.schema.json:37-128`) [E53](../evidence/code-evidence.md#e53) (`docs/06-requirements/REQ-003-idea-plan-lifecycle.md:30-67`) [E66](../evidence/code-evidence.md#e66) (`research/architecture/development_traceability_model.md:143-181`)

Alternative: coarse dependency traversal plus human judgment may be sufficient at this scale. That is a baseline to evaluate, not evidence of exhaustive epistemic impact analysis.
