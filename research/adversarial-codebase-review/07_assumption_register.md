# Architectural assumption register

Statuses below distinguish evidence-supported scope, reproduced contradiction, unimplemented proposal and open operational assumption. Confidence refers to the assessment. Locations resolve to exact excerpts in the [evidence register](../evidence/code-evidence.md); synthetic results are in [review-probe-results.json](../evidence/review-probe-results.json).

```yaml
- assumption: All system records are append-only.
  status: CONTRADICTED
  evidence: Idea append preserves lines; workload and brain sources are current snapshots; checkpoint rewrites sections.
  location: ["tools/append_idea.py:190-195", ".claude/skills/checkpoint/SKILL.md:51-65", "tools/rebuild_db.py:103-130"]
  confidence: HIGH
  risk_if_wrong: Lossless historical knowledge reconstruction is falsely promised.
  alternative_interpretation: Append-only was intended only for the idea source log.

- assumption: Every knowledge object has independent ontological, epistemic and lifecycle classifications.
  status: NOT_IMPLEMENTED
  evidence: Idea schema has additionalProperties false and only event/status/annotation/link vocabulary; ARCH-005 is draft.
  location: ["schemas/idea.schema.json:6-24", "docs/07-architecture/ARCH-005-idea-node-classification.md:17-40"]
  confidence: HIGH
  risk_if_wrong: Novelty or evaluation claims are made about capabilities absent from the implementation.
  alternative_interpretation: This is a proposal awaiting experiments rather than an implementation claim.

- assumption: A valid source tree always yields a safe replacement projection.
  status: CONTRADICTED
  evidence: Duplicate IDs pass per-file preflight; rebuild raises ConstraintException after deleting old projection.
  location: ["src/db/source_validation.py:136-174", "tools/rebuild_db.py:103-130", "research/evidence/review-probe-results.json"]
  confidence: HIGH
  risk_if_wrong: A failed refresh makes working query context unavailable or partial.
  alternative_interpretation: Source truth survives and a repaired rebuild can restore service.

- assumption: Raw inbox records retain exact original bytes.
  status: CONTRADICTED
  evidence: read_text normalizes CRLF; same processed filename replaces older archived input.
  location: ["src/capture/raw.py:110-125", "research/evidence/review-probe-results.json"]
  confidence: HIGH
  risk_if_wrong: Evidence offsets, hashes and exact historical reconstruction can diverge.
  alternative_interpretation: Normalized Unicode text is enough for the intended use, but requirement wording is stronger.

- assumption: Source references are guaranteed to resolve.
  status: CONTRADICTED
  evidence: Dangling task parents/capture and unknown promotion target survive validation in probes.
  location: ["src/db/source_validation.py:136-174", "tools/append_idea.py:229-252", "research/evidence/review-probe-results.json"]
  confidence: HIGH
  risk_if_wrong: A path that looks traceable ends at no actual object.
  alternative_interpretation: References are trusted local conventions pending queued integrity work.

- assumption: Query projections preserve all significant source fields.
  status: CONTRADICTED
  evidence: Entity capture pointers and project repository/stakeholders omitted; commitments tags omitted.
  location: ["tools/rebuild_db.py:146-256", "research/evidence/review-probe-results.json"]
  confidence: HIGH
  risk_if_wrong: Query consumers cannot recover source provenance or project membership reliably.
  alternative_interpretation: Projection is intentionally narrow, with manual source inspection as fallback.

- assumption: Stored memory scope controls retrieval eligibility.
  status: CONTRADICTED
  evidence: Query uses project_id equality or null; stored scope is absent from selection and formatter.
  location: ["tools/load_context.py:44-70", "research/evidence/review-probe-results.json"]
  confidence: HIGH
  risk_if_wrong: Temporary knowledge becomes global context or global guidance disappears.
  alternative_interpretation: Project association is intended as scope; the competing field would then need clarification.

- assumption: High memory confidence is a good proxy for relevance.
  status: OPEN_QUESTION
  evidence: Confidence ranks before created date, but no retrieval quality evaluation is implemented.
  location: ["tools/load_context.py:92-100", "schemas/memory.schema.json:49-54"]
  confidence: HIGH
  risk_if_wrong: Stale high-confidence narratives crowd out current relevant knowledge.
  alternative_interpretation: Manually curated small corpora may make this baseline adequate.

- assumption: Corrections advance effective-state recency.
  status: CONTRADICTED
  evidence: Corrected title retains creation timestamp in updated; amendments are skipped during replay.
  location: ["src/db/ideas.py:247-268", "research/evidence/review-probe-results.json"]
  confidence: HIGH
  risk_if_wrong: Changed meaning is missed by recency-based analysis.
  alternative_interpretation: Updated intentionally means last non-correction event, but the field name does not express that.

- assumption: Actor labels prove authority and independent reasoning.
  status: CONTRADICTED
  evidence: Author is supplied text, status events have no actor/rationale, and no shared-source ancestry is tracked.
  location: ["tools/append_idea.py:142-187", "tools/append_idea.py:311-345"]
  confidence: HIGH
  risk_if_wrong: Agents can be mistaken for authorized or independent sources.
  alternative_interpretation: A trusted single-owner CLI needs social attribution rather than authentication.

- assumption: Idea and semantic relationship history preserve conflicting current branches.
  status: PARTIALLY_SUPPORTED
  evidence: Separate annotations persist; competing amendments produce one effective field value by append precedence.
  location: ["src/db/ideas.py:166-205", "src/db/ideas.py:290-314"]
  confidence: HIGH
  risk_if_wrong: The last correction is treated as epistemic resolution of dissent.
  alternative_interpretation: Historical preservation plus manual comparison is sufficient without branch objects.

- assumption: A phase is a complete reproducible agent session boundary.
  status: PARTIALLY_SUPPORTED
  evidence: Scope, locks, session_budget and completion evidence exist; exact input context and tool-action history do not.
  location: ["schemas/backlog.schema.json:57-240", "src/governance/backlog.py:116-190"]
  confidence: HIGH
  risk_if_wrong: Session outcomes cannot be reproduced or compared as controlled context experiments.
  alternative_interpretation: Phase is a planning/work-package contract rather than a replayable runtime episode.

- assumption: Task and commitment need distinct identities.
  status: SUPPORTED
  evidence: Optional commitment_id and independent task files permit work without an obligation and multiple tasks for one promise.
  location: ["schemas/task.schema.json:5-20", "schemas/commitment.schema.json:5-20"]
  confidence: HIGH
  risk_if_wrong: Over-modeling adds unnecessary bookkeeping; collapsing prematurely loses obligation semantics.
  alternative_interpretation: Both could share an underlying schema while remaining semantically distinct roles.

- assumption: Document links prove requirement satisfaction and runtime realization.
  status: CONTRADICTED
  evidence: Validator checks existing evidence paths and result strings, not test truth, version identity or deployment.
  location: ["src/governance/backlog.py:159-188", ".github/workflows/ci.yaml:1-41"]
  confidence: HIGH
  risk_if_wrong: Complete bookkeeping is mistaken for a working deployed capability.
  alternative_interpretation: Human review supplies the semantic gate, as the close protocol intends.

- assumption: Changed assumptions have a complete machine-computable blast radius.
  status: NOT_IMPLEMENTED
  evidence: Only scheduling dependency closure exists; no assumption-to-decision or versioned requirement-to-code edges.
  location: ["src/governance/backlog.py:22-29", "schemas/document.schema.json:98-127"]
  confidence: HIGH
  risk_if_wrong: Unmapped dependencies remain justified by falsified premises.
  alternative_interpretation: Coarse document dependencies plus manual review may be an adequate baseline.
```
