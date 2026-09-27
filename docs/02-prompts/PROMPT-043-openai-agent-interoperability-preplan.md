---
schema_version: 1
id: doc-prompt-openai-agent-interoperability-preplan
code: PROMPT-043
title: OpenAI-agent interoperability pre-plan package — ratified MVP input for later planning
kind: prompt
status: draft
owner: repository-owner
created: '2026-09-27'
updated: '2026-09-27'
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

## How to use this package

When the owner elects to resume this work, use this document as the ratified starting input for a
planning session. That session must decompose the MVP into requirements, decisions, and
one-session backlog phases before any implementation is authorized. It must distinguish confirmed
decisions below from unresolved questions; it must not re-open a ratified decision merely because
the implementation details are not yet designed.

## Ratified decisions (do not re-ask)

1. **MVP runtime: OpenAI Agents API.** Use the managed OpenAI Agents API for this MVP. It owns
   managed sessions, context compaction, multi-agent capability, and MCP support. The Agents SDK
   is a future local-orchestration enhancement, not an MVP substitute.

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

## Prompt A seed

> Treat `PROMPT-043` as the owner-approved pre-plan package for OpenAI-agent interoperability.
> Preserve every item under “Ratified decisions” as do-not-re-ask. Do not implement the integration.
> First create the required governed planning artifacts through the applicable planning protocol:
> requirements, ADRs, an implementation plan, dependency-ordered backlog phases, and a
> pack-factory prompt. Explicitly resolve every item in “Unresolved future work,” arrange an
> adversarial audit before implementation, and return to the owner for approval before any
> implementation session, dependency addition, MCP registration, or credential setup.
