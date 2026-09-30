---
schema_version: 1
id: doc-prompt-openai-agent-interoperability-preplan
code: PROMPT-043
title: OpenAI-agent interoperability pre-plan package — ratified MVP input for later planning
kind: prompt
status: draft
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-30'
systems: [sys-governance, sys-delivery, sys-realization]
depends_on: [doc-governance-protocol, doc-prompt-pack-protocol]
---

# OpenAI-agent interoperability pre-plan package

This is a **Prompt A pre-plan package**, preserving the owner's approved MVP input for a later
planning process. It is not a `PLAN-*` document, an execution plan, a backlog item, or authority
to implement an OpenAI or Claude agent integration. The later planning protocol, its adversarial
audit, and any revision remain future work.

The intended outcome is a narrowly bounded interoperability layer: independent OpenAI-backed,
advisory roles that a person can invoke directly or through Claude Code, without granting a
remote agent repository write access. Current repository behavior is unchanged.

It serves idea `000506` (OpenAI agents callable from Claude Code, for mostly read-only
investigations to start and for adversarial audits). The owner drafted the ratified content with
ChatGPT on 2026-09-27, outside the interactive `AskUserQuestion` process `GOV-008` stage 1
describes; that is why its status is `draft`. The Prompt Planner added the `GOV-008` structure
around it on 2026-09-30 (sections *Feature inventory*, *What the planning session must produce*,
*Open questions*, *Related ideas and rulings*, *Deadline context*, and the rewritten seed) without
changing any ratified decision's choice.

**Tests never run in the primary checkout** (`/code/d-system`). Every `pytest`, rebuild, `ruff`,
`mypy` and governance run in any session this package starts happens in that session's own
worktree. `test/test_codes.py` overwrites the tracked `catalog.md` while it runs.

## How to use this package

When the owner elects to resume this work, use this document as the ratified starting input for a
planning session. That session must decompose the MVP into requirements, decisions, and
one-session backlog phases before any implementation is authorized. It must distinguish confirmed
decisions below from unresolved questions; it must not re-open a ratified decision merely because
the implementation details are not yet designed.

## Ratified decisions (do not re-ask)

1. **MVP runtime: OpenAI Agents API.** Use the managed OpenAI Agents API for this MVP. It owns
   managed sessions, context compaction, multi-agent capability, and MCP support. The Agents SDK
   is a future local-orchestration enhancement, not an MVP substitute. *(The choice of runtime is
   ratified. The capability description is the vendor's, as given in the owner's source plan, and
   is unverified here: confirm it against official documentation at planning time.)*

2. **One Python core, two thin adapters.** The eventual integration has a shared Python invocation
   core, exposed through a direct CLI and a Claude Code stdio MCP adapter. The adapters do not
   duplicate role logic, request construction, or boundary enforcement.

3. **Three independent, read-only roles.** The MVP roles are:

   - **Reviewer** — reviews requirements, specifications, and diffs and returns actionable
     findings.
   - **Adversarial auditor** — tries to falsify acceptance claims and verification evidence.
   - **Research synthesizer** — performs web-grounded research and returns sources,
     uncertainties, and a concise recommendation.

4. **No remote filesystem writes.** Remote delegates receive only explicitly selected permitted
   inputs and are advisory. They do not write the repository, modify the local filesystem, or
   produce patches for automatic application. Patch-producing delegates are a later capability.

5. **Credential location for the MVP.** An OpenAI Platform API key belongs in ignored local
   `.env` configuration, never in tracked files, prompts, results, or logs. A later decision will
   investigate OS secret-manager and CI injection options, rotation, and lifecycle management.

6. **Repository content boundary.** Never send private, secret, untracked, or oversized inputs to
   a remote agent. The eventual wrapper must reject, rather than silently trim, disallowed or
   oversized requested content. The boundary includes `_private/`, `.env*`, credentials and
   sensitive configuration, generated data, and any untracked path.

## MVP shape to preserve during decomposition

The later planning work should turn this approved shape into observable requirements and security
decisions, without treating it as existing implementation:

- A shared typed invocation service supplies the three role contracts to both adapters.
- The CLI supports independent invocation. The project-local stdio MCP adapter exposes
  `openai_review`, `openai_adversarial_audit`, and `openai_research`, each with explicit task,
  scope, and input-reference fields.
- The local wrapper selects permissible, deliberately requested repository material: named tracked
  files, a bounded Git diff, and named specifications. Reviewer and adversary roles have no local
  tools or sandbox. The research role has hosted web search only.
- Reports are structured and include role, verdict, ranked findings, evidence locations or URLs,
  uncertainties, recommended next action, session identifier, and usage or error metadata.
  Claude or a human remains responsible for applying any change.
- The implementation design must cover mocked unit and adapter-level integration testing of path
  policy, exclusions, size caps, role routing, result parsing, refusal behavior, error
  propagation, and secret non-leakage. A real-key smoke test is an owner-controlled later step.

## Standing constraints

- Do not create or record an API key, secret value, secret-bearing prompt, or secret-bearing log.
- Direct remote filesystem writes are out of scope for the MVP.
- Repository content is opt-in and limited to material that passes the explicit local boundary.
- The existing Claude roster remains authoritative for Claude-native workflows. These roles add
  independent review and research; they do not seek roster parity.
- No dependency, MCP registration, API integration, implementation file, backlog phase, or
  execution plan is authorized by this package.

## Feature inventory

The owner's MVP, itemized from the decisions and shape above. Letters are for reference.

- **A. Invocation core.** One typed Python service holding the three role contracts, request
  construction and the content boundary (decisions 2, 6).
- **B. CLI adapter.** Direct invocation of any role (decision 2).
- **C. Claude Code stdio MCP adapter.** Tools `openai_review`, `openai_adversarial_audit` and
  `openai_research`, each with task, scope and input-reference fields (decision 2).
- **D. The three roles.** Reviewer, adversarial auditor and research synthesizer; read-only; the
  research role has hosted web search only (decision 3).
- **E. Content boundary.** Named tracked files, a bounded Git diff and named specifications only;
  reject, never trim; `_private/`, `.env*`, credentials, generated data and untracked paths
  excluded (decision 6). `tools/check_no_private_content.py` is the repository's existing
  confidential-identifier check; the planning session decides whether the boundary reuses or
  extends it.
- **F. Structured reports.** Role, verdict, ranked findings, evidence locations or URLs,
  uncertainties, next action, session id, usage or error metadata (*MVP shape*).
- **G. Credential handling.** The key in ignored local `.env` only (decision 5).
- **H. Tests.** Mocked unit and adapter-level tests of the items the *MVP shape* lists; a real-key
  smoke test is the owner's later step.

## What the planning session must produce, in order

Through the `GOV-008` pipeline. Nothing is implemented, no dependency is added, no MCP server is
registered and no credential is set up until the owner signs off the coordinator prompt.

1. **Prompt B**, the pack-factory prompt (`--next-code prompt`), drafted from this package. It
   stops for its own adversarial review and the owner's sign-off (`GOV-008` stage 3).
2. Then, by executing Prompt B: a requirement (`--next-code requirement`) with observable rows for
   items A to H; decision records (`--next-code decision`) at least for the runtime and its
   relation to `ADR-018`, the content boundary, and credential handling; a plan
   (`--next-code plan`) with one-session backlog phases, reviewed under `GOV-018`; agent-roster
   deltas; the delegation pack, coordinator prompt and kick-off record (`GOV-008` stages 4 to 8).

## Related ideas and rulings

- `000506` is the idea this package serves.
- `000432` (other providers' models per role) carries the owner's 2026-09-27 rulings: a role table
  in configuration (model, fallback model and endpoint per role, one startup check), LiteLLM
  Router not adopted, and "the client-data allow-list is Anthropic endpoints only". Its Scout
  synthesis places per-provider adapters at the `Dispatcher` seam in `src/orchestrator/dispatch.py`.
- `000430` (second-provider models as planners and in ideation) and `000359` (other providers'
  sessions under the multi-session protocol) are the owner's related asks.
- `ADR-018` says the Claude Agent SDK executes every agent a LangGraph node dispatches. These
  OpenAI roles are invoked by a person or by Claude Code through MCP, not dispatched by the
  orchestrator; the planning session states that relation in a decision record.
- `PROMPT-040` (the Gemini review sequence) is the nearest precedent for sending repository content
  to another provider.

## Open questions for the owner

Asked by the planning session with `AskUserQuestion`, batched, one batch at a time, at the point
each matters; drafts in the message text, never in option previews.

1. **Gate check-in** (`GOV-008`, always asked up front): should the build session stop at gates for
   check-in, or push through to close-out?
2. **Client-data allow-list.** Does the 2026-09-27 ruling on `000432` ("the client-data allow-list
   is Anthropic endpoints only") cover only `_private/` client records, which decision 6 already
   excludes, or any repository content sent to OpenAI?
3. **Role table.** Do these roles join the per-role table ruled on `000432`, or stay a separate
   configuration because the orchestrator does not dispatch them?

## Unresolved future work

The following are deliberately open and must be resolved through the planning protocol rather than
assumed here:

1. Decompose the MVP into requirements, ADRs, an approved plan, and dependency-ordered backlog
   phases.
2. Draft the pack-factory prompt that will create those planning artifacts.
3. Subject the pack-factory prompt and resulting pack to adversarial review.
4. Decide the final agent roster and how these roles relate to existing Claude agent definitions.
5. Design write-mode security before considering patch-producing delegates: pre-created worktrees,
   path allowlists, audit logs, scoped permissions, and human review are minimum topics.
6. Decide API-key lifecycle, rotation, secret-manager use, and CI injection.
7. Confirm detailed dependency, model/configuration, result-schema, testing, operational, and MCP
   registration choices against repository reality at planning time.

## Source inventory and planning boundary

This package derives from the owner-supplied OpenAI-backed-review-agents plan attached to the
request that created it. Its external product references and implementation suggestions are
preserved as approved MVP input, not independently revalidated design commitments. The planning
session must verify mutable platform details against official documentation before producing
implementation artifacts.

## Standing rules for the sessions this starts

- `AGENTS.md` governs. Every governed document takes its code from `--next-code`.
- Work in a worktree; tests never run in the primary checkout.
- Ideas are recorded only through the sanctioned writer; under the coordination contract
  (`GOV-017`), a session sends them to the Ideation session.
- Never write a confidential identifier into a tracked file; run
  `tools/check_no_private_content.py` with changes staged, and read its identifier count.
- Reviews are dispatched on an adversary or validator agent type, never `general-purpose`.

## Deadline context

No deadline binds this work. `000506` was recorded as lower priority, capture only.

## Prompt A seed

> You are the planner for OpenAI-agent interoperability (idea `000506`). Read `AGENTS.md`, then
> `docs/08-governance/GOV-006-conversation-guidelines.md`, then
> `docs/08-governance/GOV-008-prompt-pack-protocol.md`, then this document
> (`docs/02-prompts/PROMPT-043-openai-agent-interoperability-preplan.md`) in full. Preserve every
> item under "Ratified decisions" as do-not-re-ask. Read ideas only through `fold()`. Work in your
> own worktree; tests never run in the primary checkout. Produce exactly one artifact: **Prompt B**,
> the pack-factory prompt (`--next-code prompt`), carrying this package's decisions, feature
> inventory, open questions and unresolved work forward, and naming in order what its "What the
> planning session must produce" section lists. Ask the owner, through AskUserQuestion, only the
> open questions whose answers change what Prompt B says. Do not write the requirement, decisions,
> plan or phases, and do not run Prompt B: it runs only after its adversarial review (`GOV-008`
> stage 3) and the owner's sign-off. Do not add a dependency, register an MCP server or set up a
> credential. Stop when Prompt B exists, governance exits 0, and the owner has a summary of it.
