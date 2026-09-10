# Session backlog

[backlog.yaml](backlog.yaml) is the authoritative phase catalog. Every item contains a one-session scope, acceptance checks, verification, source-plan links, dependencies and a next action.

| Track | Scope | Source |
|---|---|---|
| `phase-rel-*` | Source integrity, failure-safe rebuilds, membership, retrieval, CI and documentation corrections | [Reliability plan](../01-plans/PLAN-004-reliability-follow-up.md) |
| `phase-html-*` | Contracts, generation, API, frontend, samples and end-to-end verification | [HTML overview](../01-plans/PLAN-003-dynamic-html-generation/PLAN-003-overview.md) and all six child plans |
| `phase-sig-*` | Six SQL signals, view lifecycle and durable velocity snapshots | [Mini-systems plan](../01-plans/PLAN-002-mini-systems-proposal.md) |
| `phase-syn-*` | Context packs, briefing, weekly review, digest and HTML export | [Mini-systems plan](../01-plans/PLAN-002-mini-systems-proposal.md) |
| `phase-mem-*` | Memory roles/contracts, candidate processing, hints, retrieval, review, pruning and conditional semantic extensions | [Memory-agent plan](../01-plans/PLAN-001-agent-memory-system.md) |
| `phase-doc-*` | Code register, allocation and catalog commands, backfill of every existing code and filename, enforcement and records | [Document code plan](../01-plans/PLAN-005-document-code-system.md) and [requirements](../06-requirements/REQ-001-document-code-requirements.md) |
| `phase-cap-*` | Entity and capture contracts, raw intake, structuring and routing, review and promotion, projection and seeding | [Capture build](../01-plans/PLAN-009-capture-build.md); the completed definition phase came from [PLAN-007](../01-plans/PLAN-007-capture-and-structuring-system.md) and [PROMPT-002](../02-prompts/PROMPT-002-capture-and-structuring-system.md) |
| `phase-ses-*` | Session type taxonomy, opening entry points, the closing protocol and dogfooding | [Session lifecycle](../01-plans/PLAN-008-session-lifecycle-protocols.md) |
| `phase-priv-*` | Structure/content boundary, identifier scrub, portfolio relocation, leak check and history rewrite before the first push | [Confidentiality sweep](../01-plans/PLAN-006-confidentiality-sweep.md) |
| `phase-gov-*` | Code-reservation enforcement, plus the governance-model and system-complexity reviews | [Code reservation enforcement](../01-plans/PLAN-010-code-reservation-enforcement.md); [Governance and complexity review](../01-plans/PLAN-014-governance-and-complexity-review.md) |
| `phase-term-*` | Shared vocabulary, generated glossaries and the architecture overview | [Terminology system](../01-plans/PLAN-012-terminology-system.md) |
| `phase-tool-*` | Per-tool operations documents and the generated tool reference | [Tooling documentation](../01-plans/PLAN-013-tooling-documentation.md) |
| `phase-idea-*` | Idea capture as an append-only event log, its write tooling and triage agent | [Idea record system](../01-plans/PLAN-016-idea-record-system.md) |
| `phase-scope-*` | Repository boundary — extracting work that belongs elsewhere and recording where it went | [Ephemeral working plans](../01-plans/PLAN-015-ephemeral-working-plans.md) |
| `phase-plc-*` | Retiring root `plans/` as a governed concept and consolidating it into `docs/01-plans/` | [Plans directory consolidation](../01-plans/PLAN-018-plans-directory-consolidation.md) |
| `phase-demo-*` | Live-demo stage backend and frontend, deterministic overview tools, overview generation and demo readiness | [Live demo plan](../01-plans/PLAN-021-live-demo.md) |

```bash
uv run python -m src.governance --ready
uv run python -m src.governance --backlog
```

Read the [accepted decisions](../08-governance/GOV-003-backlog-decisions.md), [session workflow](../08-governance/GOV-002-backlog-protocol.md), and [initial coverage review](../08-governance/GOV-004-backlog-capture.md). The full report includes phase details and a source-plan coverage table. The YAML catalog holds state; this index holds navigation only.

Before starting a phase, validate the entire backlog. Capturing or approving a phase does not mean it is implemented. Deferred work remains visible with a resume condition.

`max_active` bounds how many phases may be claimed at once, and concurrent claims must target disjoint systems, disjoint deliverable paths and unrelated dependency chains. Each active phase names the `agent` holding it, which is also its branch name `agent/<phase-id>`. Both reports open with the active-claims table and mark, per phase, which active claims it would collide with. See [ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md) and the agent steps in [AGENTS.md](../../AGENTS.md).
