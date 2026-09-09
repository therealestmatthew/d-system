# Top seven expansion ideas for review — RECORDED as ideas 000028-000036

Prepared from two independent repository audits. The agents reviewed the current idea view, plans,
schemas, source, projection tooling, tests and governance inventory. These are proposals only: they
have not been appended to `_data/ideas.jsonl`, and no implementation is claimed.

**Update:** this file's origin was unaccounted for when discovered — a separate, unexplained process
produced it alongside a parallel `omitted-idea-candidates.md`, independent of the two brainstorming
agents this session knowingly launched. Per the owner's direction, it was reviewed, deduplicated
against the session's other idea batch (000021-000027, unrelated in topic — governance/testing gaps
versus this file's agent-orchestration-infrastructure focus) and against itself (item 1 below
duplicates items 8+9 in "Always-on additions" — the split framing was kept, the combined one dropped),
then recorded as ideas **000028-000036**. The five "genuinely omitted" candidates in
`omitted-idea-candidates.md` were left un-recorded, respecting that document's own stated reasons for
holding them back. This file is kept as the review trail; it is no longer an action item on its own.

The selection removes duplicates, excludes capabilities already substantially covered by current
plans, and favors ideas that create a new application capability rather than another planning artifact.

## 1. External trigger gateway and durable workflow runs

Create a local trigger gateway that accepts filesystem, scheduled, webhook and CLI events, then
starts bounded agent jobs. Persist each run with a correlation ID, trigger payload hash, model/tool
versions, context-pack hash, budget, timeout, retries, checkpoint, artifacts and final disposition.
A run must resume after interruption without repeating completed side effects.

This fills a gap between the repository’s agent prompts and a continuously useful application. The
current system has owner-invoked commands and planned agent workflows, but no external trigger
protocol, durable job identity or restart semantics. It is distinct from an always-running model:
the gateway owns triggers and durable state while an execution adapter can remain provider-neutral.

Touches: new job/trigger modules, DuckDB run tables, API routes, operations configuration, agent
adapters and a small UI for run status.

Verification: submit synthetic schedule, filesystem and webhook triggers; prove idempotent delivery,
retry and timeout behavior, cancellation, restart recovery, context limits and no duplicate execution
for one event key. An interrupted fixture run must resume from its last completed step.

## 2. Capability and approval broker for agent actions

Give every agent run an explicit capability set: read-only repository access, source mutation,
external network, publication, or other narrowly defined actions. Route sensitive operations through
an approval request with scope, reason, expiry and an immutable decision record. Denied capabilities
must be enforced at the tool boundary rather than merely described in prompts.

The repository governs documents and phase claims, but it does not yet authorize runtime agent
actions. This is the missing control needed before trigger-driven work can safely operate between chat
sessions, and it composes with the run ledger above without choosing a model provider.

Touches: capability and approval schemas, job execution boundary, tool wrappers, API approval routes,
DuckDB audit records and a review UI.

Verification: test allow, deny and escalation paths; prove a denied action cannot mutate a source or
reach the network; expire and scope approvals; replay the audit trail to explain every attempted action.

## 3. Evidence-backed provenance graph

Record the sources behind each memory, recommendation, generated report, context pack and dashboard
metric: source file/event and anchor, query, prompt, model/tool version, human decision and derived
artifact. Make the graph queryable in both directions: “why does this claim exist?” and “what outputs
must be reconsidered if this source changes?”

Current evidence fields and memory confidence are local concepts, while generated outputs lack an
end-to-end lineage model. This unifies the two agents’ proposals for a provenance manifest, claim
registry and provenance graph into one auditable capability. It also helps distinguish a captured fact,
a derived interpretation and a recommendation without changing the append-only source record.

Touches: evidence/claim and memory metadata, DuckDB provenance tables, rebuild/generation tooling,
retrieval, report generation, API endpoints and detail views.

Verification: generate a fixture artifact and assert its complete dependency graph; modify one source
and identify only affected outputs; preserve provenance across rebuilds; surface contradictory or stale
claims without silently deleting them.

## 4. Temporal projection explorer

Expose deterministic “as of” snapshots and two-point diffs for ideas, plans and portfolio entities.
Show which status, annotation, relationship, promotion or plan-phase fact changed, when it became
known, and which source event supports it. Keep raw event time and effective state position explicit.

The repository is investing in immutable histories and derived projections, but current consumers
primarily expose present state. A temporal explorer turns retained history into a usable application
capability and forces the time-axis definitions in the lifecycle architecture to become testable.
It is complementary to provenance: provenance explains origin; temporal views explain change.

Touches: replay/query layer, DuckDB temporal views, FastAPI routes, React views and synthetic history
tests.

Verification: fixture histories produce stable snapshots immediately before and after boundaries;
diffs identify exactly the changed contributions; amendment timestamps never masquerade as state-change
timestamps; invalid or ambiguous histories are reported rather than reordered.

## 5. Portfolio scenario simulator

Add isolated what-if scenarios over the derived portfolio: defer a project, change capacity, move a
deadline, close a commitment or alter task allocation. Recompute signals and compare the scenario with
the baseline without writing source JSON, the live database or the idea log.

Current signal plans describe the portfolio as it is. A scenario layer supports decisions before the
owner commits to them and creates a concrete consumer for the projection and signal systems. It is a
new capability rather than another signal definition.

Touches: scenario input schema, isolated DuckDB or in-memory projection, signal SQL, API routes,
React comparison UI and export tooling.

Verification: run deterministic fixtures with controlled changes; prove source and baseline projections
remain byte-for-byte unchanged; verify scenario isolation, repeatability and expected metric deltas;
make discarded scenarios unrecoverable from normal source views unless explicitly exported.

## 6. Contract compiler and mutation-driven fixture suite

Make JSON Schema the executable contract source for Python models, TypeScript types, OpenAPI fragments,
valid/invalid fixture factories and rejection tests. Add deterministic generation and mutation checks so
schema, backend, frontend, loader and governance behavior cannot drift silently.

The repository currently has a manual multi-step entity expansion process and separate contract
consumers. Existing fixture work is scoped to HTML; this proposal covers cross-system contract drift
and deliberately tests negative behavior, which the current all-created idea corpus cannot exercise.
It improves expansion velocity without introducing a new runtime subsystem.

Touches: `schemas/`, a contract-generation tool, `src/models/`, frontend types, API metadata, test
fixtures and the governance check.

Verification: repeated generation is byte-stable; a schema mutation produces the expected stale-artifact
failure; generated Python and TypeScript type checks pass; targeted invalid mutations fail at the right
validator boundary; existing hand-authored exceptions remain explicit.

## 7. Recommendation calibration loop

Persist recommendations from signals and agents with their evidence, the owner’s decision (accept,
defer, dismiss or revise), and the later observed outcome. Produce calibration reports for useful
recommendations, false urgency, repeated misses, deferrals and outcome lag.

The system plans signals and idea triage, but it does not measure whether its advice improves the
owner’s work. This creates a feedback loop for tuning thresholds, prompts and review cadence instead
of accumulating persuasive automation with no outcome evidence. It is distinct from a next-best-action
queue: the queue chooses actions; calibration evaluates whether recommendations were worth following.

Touches: recommendation/decision/outcome events, signal generators, agent-run records, weekly review
workflow, SQL reports and UI explanations.

Verification: use synthetic recommendation histories with known outcomes; calculate precision, deferral
rate, false-urgency rate and outcome lag; link every metric to immutable evidence; leave unresolved
outcomes explicitly unresolved rather than treating them as failures.

## Deliberately not selected

Tamper-evident hash chains, adaptive review queues, conflict-aware source editing, runtime redaction
firewalls, universal event sourcing and a separate graph database are valuable candidates. They were
held back because the selected ideas cover their immediate value more broadly, existing governance or
confidentiality work overlaps part of their scope, or they need evidence from trigger-driven runs and
real portfolio usage before their permanent surface is justified.

The selected seven should be evaluated against the complexity review and the existing backlog before
any is promoted into the append-only ideas log. This file is the review surface only.

## Always-on additions

These follow the original seven and are separate review candidates. They are split so trigger intake,
run durability and process supervision can be evaluated independently.

## 8. External trigger gateway

Accept filesystem, cron, webhook and CLI triggers through one provider-neutral local interface. Normalize
each trigger into a deduplicated event with source, payload hash, received time and requested workflow.
This is the ingress boundary for operating the application between chat sessions.

Verification: submit one fixture through each adapter, restart the gateway, replay duplicate delivery,
and prove one logical trigger produces one queued run with its original payload hash.

## 9. Durable agent workflow run ledger

Persist each workflow run, step attempt, checkpoint, artifact, budget, timeout, retry and final
outcome. Resume interrupted runs from the last completed side-effect boundary and expose a queryable
run history independent of the model provider.

Verification: interrupt a multi-step fixture after step two, restart the worker, and prove steps one
and two are not repeated while step three completes exactly once.

## 10. Always-on worker host and watchdog

Add a small supervised worker process that drains queued runs, enforces concurrency and quiet hours,
heartbeats progress, and marks abandoned work for review. Keep it separate from trigger intake and the
workflow ledger so the application can run in one-shot, scheduled or continuously supervised modes.

Verification: kill and restart the worker, test quiet-hour deferral, exceed a run timeout, and prove
stale heartbeats become reviewable without silently retrying unsafe side effects.
