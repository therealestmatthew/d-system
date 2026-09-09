# Omitted and represented idea candidates

**Update:** the sibling `top-7-expansion-ideas.md` selections this file cross-references were recorded
as ideas 000028-000036. The five "genuinely omitted" entries below were deliberately left un-recorded,
respecting the reasons already given for holding each one back — not re-litigated.

The two independent reports produced 20 source proposals. Several were intentionally merged into the
top seven or into the always-on additions. After deduplication, only five concepts were genuinely
omitted. This file preserves thirteen source-level candidates separately so none disappears during
review. Entries marked “represented” are already covered by a selected umbrella idea; entries marked
“omitted” were not selected for the current top list.

None of these entries has been appended to `_data/ideas.jsonl`.

## Genuinely omitted candidates

### 1. Tamper-evident event lineage — omitted

Hash-chain append-only events with periodic checkpoints and a verifier that identifies the first
broken, deleted or reordered line. It adds cryptographic evidence to the existing structural
append-only check. Touches the idea writer, event schema, source validation, integrity tooling and
tests. Verify by altering, deleting and reordering synthetic lines and checking the reported break.
Held back until the event model and confidentiality boundary settle.

### 2. Dependency-aware next-best-action planner — omitted

Rank an explainable action queue from due dates, blockers, stale reviews, effort and available
capacity, with manual override events. This composes planned signals into decisions. Touches signal
SQL, commitment/task logic, an API and the React UI. Verify fixture ranking changes and reason fields.
Held back until the underlying portfolio and signal data are exercised.

### 3. Privacy-aware artifact classification and redaction gate — omitted

Classify fields and generated artifacts as public, internal, sensitive or prohibited; redact or block
context packs and exports according to policy. Touches source validation, retrieval, report generation,
model adapters and export tests. Verify prohibited fixture fields never reach an outbound payload.
Held back because the confidentiality sweep and runtime capability boundary should establish the first
policy contract.

### 4. Universal activity ledger — omitted

Extend immutable event history to projects, commitments, tasks, people and plans, then derive current
projections and “what changed since review” timelines. Touches every entity schema, rebuild tooling,
DuckDB and future APIs. Verify arbitrary-time reconstruction against replay fixtures. Held back because
it is a large cross-domain commitment before the idea lifecycle has proven its event model.

### 5. Conflict-aware multi-agent source editing — omitted

Use leases, optimistic versions, patch previews and semantic conflict detection for JSON, Markdown
front matter and append-only logs. Touches source writers, validation, agent jobs and a conflict queue.
Verify disjoint edits merge, overlapping edits become explicit conflicts and stale versions are rejected.
Held back until durable runs and the capability broker exist.

## Source proposals represented by selected umbrellas

### 6. Source/projection provenance manifest — represented by top idea 3

Record source hashes, schema hashes, tool version, validation result and row counts for every DuckDB
build. This is the reproducible-build slice of the selected evidence-backed provenance graph.

### 7. Evidence-backed claim registry — represented by top idea 3

Store claims with source anchors, confidence, reviewer, contradiction and stale state. This is the
claim-lifecycle slice of the selected provenance graph.

### 8. Adaptive review planner — represented by top idea 7

Combine stale items, commitments, project health and owner capacity into a small ranked review agenda.
The selected recommendation calibration loop evaluates the quality of such recommendations; this
candidate remains a possible later consumer.

### 9. Policy-gated agent write broker — represented by top idea 2

Give each job explicit capabilities and require scoped approvals for mutation, network and publication.
The selected capability and approval broker preserves this proposal as its complete policy boundary.

### 10. Contract-driven fixtures and mutation testing — represented by top idea 6

Generate valid and invalid fixtures from schemas and mutate contracts to test rejection behavior. The
selected contract compiler includes this negative-testing capability rather than treating generation
alone as sufficient.

### 11. Portfolio scenario simulator — represented by top idea 5

Run isolated what-if changes against a copied projection and compare signal deltas. The selected
scenario simulator is the same capability and is included in the top seven.

### 12. External trigger gateway — represented by always-on idea 8

Normalize filesystem, cron, webhook and CLI events into durable workflow requests. It is separated from
run persistence so trigger adapters can be evaluated independently.

### 13. Resumable workflow run ledger — represented by always-on idea 9

Persist model, input, output, retry, cost, checkpoint and artifact metadata so interrupted runs resume
safely. It is separated from the worker host so durability is testable without requiring a daemon.

## Why the source count differs from the unique count

The reports independently named several of the same capabilities: provenance, approval brokering,
scenario simulation, contract testing and durable trigger-driven runs. The top list merges those
agreements into one proposal each. The five genuinely omitted ideas remain separately reviewable
above; the other eight are preserved as distinct source-level variants but already have a selected
home.
