---
schema_version: 1
id: doc-portable-agent-workflow-requirements
code: REQ-005
title: Portable agent workflow requirements
kind: requirement
status: draft
owner: repository-owner
created: '2026-09-09'
updated: '2026-09-09'
systems: [sys-governance, sys-backlog, sys-delivery]
depends_on: [doc-governance-protocol, doc-session-lifecycle]
---

# Portable agent workflow requirements

## Observed problem and scope

D-System's shared working agreement, governed prompts, governance rules, and command-line tools are
usable without Claude Code. Its reusable skills, commands, and triage-agent definition are currently
exposed through Claude-specific discovery and invocation surfaces. A Codex session can read and
follow the orient procedure, but cannot discover it as a repository skill. Two untracked conversion
experiments also show that copying the same instructions into multiple host formats creates drift
before the copies are committed.

This requirement covers safe workflow discovery and execution by Claude Code, Codex, and agents
without a native skill mechanism. It preserves each workflow's authority boundary. It does not make
session completion autonomous, standardize every agent framework, or require one framework to emulate
controls it does not provide.

## Observable requirements and verification

| ID | Required observable behavior | Verification method |
|---|---|---|
| R01 | Every supported workflow has one authoritative behavioral definition; any checked-in host representation is demonstrably equivalent to it. | Change the authoritative definition and confirm stale host representations fail validation until refreshed; compare all refreshed representations with a clean regeneration. |
| R02 | Claude Code and Codex can each discover and invoke repository orientation and checkpoint workflows using their supported repository mechanisms. | Start a clean session in each host, enumerate available workflows from live state, invoke orientation, and invoke checkpoint against a synthetic or active phase without manually pasting the procedure. |
| R03 | An agent with no supported native skill mechanism can execute the same orientation and phase workflow from a documented plain-prompt entry point. | Run the entry point in a clean session that exposes no repository skill feature and compare its decisions and repository effects with the native-host runs. |
| R04 | Host differences in discovery, arguments, tool names, model selection, reasoning effort, execution limits, and permissions are explicit; unsupported controls are reported rather than silently dropped. | Inspect the declared capability matrix and generated host representations; remove a required mapping or mark an unavailable control as supported and confirm validation fails. |
| R05 | Porting a workflow does not change its sanctioned write paths, folded-state reads, status-transition authority, question boundaries, or other safety decisions. | Run behavioral fixtures for each portable workflow in every supported host representation and compare allowed and refused outcomes. |
| R06 | Session closure remains owner-invoked and is absent from every autonomous or implicitly discoverable agent workflow surface. No portable workflow can mark a backlog phase complete. | Enumerate agent-reachable workflows in each supported host, attempt autonomous discovery and invocation of closure, and scan portable workflow outputs for a completion transition. |
| R07 | The idea-triage role keeps one equivalent instruction body across supported custom-agent formats and retains its configured economical model class, medium reasoning intent, bounded execution where available, and finding-only authority. | Compare rendered agent definitions, inspect each host's effective configuration, and run a scoped triage fixture that can annotate only the supplied idea and cannot change status or links. |
| R08 | Workflow inventory is derived from current repository state and identifies unavailable, owner-only, and fallback-only workflows without relying on a remembered list. | Add and remove a fixture workflow, regenerate the inventory, and confirm the reported categories change accordingly. |
| R09 | Repeating generation against unchanged sources is byte-identical, and ordinary repository checks detect hand edits or omitted generated representations. | Generate twice and compare bytes; tamper with one representation and run the targeted drift check and full test suite. |
| R10 | The portability layer introduces no dependency on confidential data, generated DuckDB state, network access, or a remote service for normal discovery and execution. | Run the workflow checks in a fresh clone with the fictional data set, no private data root, no generated database, and network access disabled. |

## Boundaries and unresolved compatibility

Claude Code and Codex are the first native targets because their repository mechanisms can be tested
directly. Gemini and other agents satisfy the initial contract through the plain-prompt path unless a
native mechanism is verified during implementation. A native adapter may be added only when its
discovery and authority behavior can be tested; a guessed format does not count as support.

Exact model names and execution-limit controls are host capabilities that change independently of
the behavioral contract. The implementation must preserve the current Claude triage intent and make
every other mapping visible for owner review. It must not claim equivalence for a control the target
host cannot enforce.
