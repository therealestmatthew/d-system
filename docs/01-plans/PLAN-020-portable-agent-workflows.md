---
schema_version: 1
id: doc-portable-agent-workflows
code: PLAN-020
title: Portable agent workflows from one canonical source
kind: plan
status: draft
owner: repository-owner
created: '2026-09-09'
updated: '2026-09-09'
systems: [sys-governance, sys-backlog, sys-delivery]
depends_on: [doc-portable-agent-workflow-requirements, doc-session-lifecycle, doc-idea-record-system]
---

# Portable agent workflows from one canonical source

## Context and scope

[REQ-005](../06-requirements/REQ-005-portable-agent-workflows.md) defines the observable contract.
The audit attached to idea `000067` found that most current workflow bodies are repository-neutral,
while `.claude/` supplies host-specific discovery, arguments, tool names, model settings, and
permission metadata. It also found two untracked experiments: a byte-identical checkpoint copy under
`.agents/` and a real Codex custom-agent translation under `.codex/`. The copy would require two
maintainers to make every change, and the translation already contains a bad path and silently omits
some source configuration.

This plan creates one source for each portable workflow and generates or validates host adapters from
it. The initial native targets are Claude Code and Codex. Gemini and agents without a verified native
skill mechanism use the existing governed prompt chain as the fallback. Orientation and checkpoint
ship first; idea capture, backlog orientation, and idea triage follow once the adapter contract is
proven.

Session closure remains an owner-only command. It may be documented for another owner's interface,
but it will not appear in an agent-discoverable skill set or custom-agent package.

## Chosen design

### Canonical behavior is independent of every host directory

Create `agent-workflows/` as the canonical source: one neutral Markdown body per workflow plus a
manifest that declares its audience, authority, inputs, required capabilities, and supported output
targets. A body describes repository decisions and procedures. The manifest carries the metadata a
renderer needs but does not pretend host-specific controls are universal.

Generate checked-in adapters for the hosts that need repository-local discovery:

- Claude skill and command wrappers under `.claude/`, including Claude tool names and argument syntax.
- Open Agent Skills adapters under `.agents/skills/` for Codex and compatible hosts.
- Codex custom-agent TOML under `.codex/agents/` where a bounded role needs model, reasoning, sandbox,
  or tool configuration.

The generated files identify their source and reject hand maintenance. A deterministic generator and
test own equivalence, following `generate_tool_docs.py` and `generate_glossary.py`. The generator
ships with its required operations document, `OPS-010`.

This design satisfies REQ-005 R01, R04, R08, and R09. It does not make `.agents/skills` the universal
source: that directory is a native adapter for some hosts, and an owner-only command or a custom
subagent role is not necessarily a skill.

### Governed prompts remain the universal fallback

The reusable idea-to-delivery prompts already begin from `AGENTS.md` and express most behavior
without assuming Claude. Keep them human-readable and governed. Replace their remaining direct
references to Claude skill paths with a host-neutral workflow lookup or an embedded fallback pointer.
An unsupported host can then execute a complete procedure by reading a prompt, without claiming a
native skill exists.

This satisfies REQ-005 R02 and R03. The generator does not rewrite governed prompt prose; tests check
that every prompt reference resolves to a canonical workflow or an explicit owner-only procedure.

### Authority is part of the manifest contract

Each workflow is classified as agent-invocable, owner-invocable, or read-only. Generation refuses an
agent adapter for an owner-only workflow. `session-close` stays owner-only and remains the only route
to `status: complete`; checkpoint can record evidence but cannot complete a phase. Idea capture and
triage continue to use `append_idea.py`, current-state reads continue through `fold()`, and triage
continues to propose links or promotions without applying them.

This satisfies REQ-005 R05, R06, and R07. The existing malformed untracked adapters are audit input,
not files to preserve verbatim.

### Host capabilities are mapped, not normalized away

The manifest records behavioral intent and per-target adapter settings separately. Claude's triage
adapter retains Haiku, medium effort, and its current turn bound. Codex receives an explicit economical
model mapping and medium reasoning setting after the implementation phase verifies the model available
on the target host. If Codex or another host cannot enforce a comparable turn or token bound, the
capability matrix says so and verification checks that the omission is visible. No adapter invents an
equivalent control.

## Sequence and dependencies

1. Define the canonical manifest and renderer, port orientation and checkpoint, and establish exact
   drift tests before expanding the surface.
2. Move the safe command behaviors and idea-triage instruction body behind the same contract, then
   render Claude and Codex adapters with explicit capability mappings.
3. Exercise native Claude and Codex discovery plus the plain-prompt fallback in clean sessions,
   correct documentation, and remove or replace the untracked experiments only after the generated
   forms pass.

The phases are sequential because later adapters depend on the generator contract, and cross-host
verification must exercise the final generated set. Each implementation phase must use a worktree
because it touches `tools/` or `test/`.

## Alternatives considered

**Keep `.claude/` canonical and copy it elsewhere.** Rejected because Claude-only paths and tool names
would remain embedded in the source, and the untracked Codex translation already proves hand copying
loses information.

**Use `.agents/skills/` as the canonical location for everything.** Rejected because Open Agent Skills
is a useful adapter format, not a universal execution model. It cannot safely represent an owner-only
command merely by changing prose, and some hosts expose no native skill discovery.

**Use symlinks between host directories.** Rejected as the portability contract. Codex documents
symlinked skill discovery, but equivalent behavior was not verified for every target, and symlinks do
not translate command arguments or custom-agent metadata.

**Treat the governed prompts as the only interface.** Retained as the fallback but rejected as the
whole solution because it would leave native discovery unavailable and would not validate model,
permission, or execution-limit configuration for bounded agents.

## Acceptance and verification

- Every REQ-005 statement is mapped to at least one phase and verified with recorded evidence.
- Claude and Codex discover orientation and checkpoint natively from generated adapters.
- The idea-to-delivery prompt chain runs without a Claude-only path dependency.
- A clean regeneration is byte-identical; tampering with any generated adapter fails the targeted
  check and the full test suite.
- The idea-triage role has one behavioral source, retains finding-only authority, and exposes every
  host-specific model or execution-control difference.
- No autonomous adapter exposes session closure or can set a phase to complete.
- `uv run python -m src.governance` and `uv run pytest` pass from the final integrated tree.

## Out of scope and open questions

This plan does not build a general agent SDK, remote workflow service, scheduler, or universal tool
protocol. It does not port session closure into an autonomous surface. It does not edit `AGENTS.md` or
`CLAUDE.md`; any future need to change either requires the owner's separate, exact approval.

The first phase must choose a schema version for the workflow manifest and document how a host adapter
declares an unsupported capability. The second phase must verify the currently available economical
Codex model before recording that model in generated configuration. A Gemini-native adapter remains
optional until its mechanism can be verified from primary documentation and exercised locally; the
plain-prompt path is the required initial support.
