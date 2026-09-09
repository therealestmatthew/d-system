---
schema_version: 1
id: doc-session-agents-update
code: SESS-2026-09-08-09
title: Framework-Agnostic Multi-Agent Rules
kind: session
status: active
owner: repository-owner
created: '2026-09-08'
updated: '2026-09-08'
systems: [sys-brain]
depends_on: []
review_after: '2026-12-08'
---

# Session: Framework-Agnostic Multi-Agent Rules

**Phase:** `phase-agnt-02`
**Agent:** `agent-gemini`

## Outcomes
- Updated `AGENTS.md` to remove hardcoded framework assumptions (like `.claude/skills/checkpoint`) and refer to framework-specific orientations and skills generally.
- Modified the handoff rules to explicitly forbid integration when `dev` is dirty, instructing agents to leave unmerged branches for review rather than force integrating via stashes or unsafe merges.

## Evidence
- `AGENTS.md`
- `docs/09-backlog/backlog.yaml`
- `docs/08-governance/catalog.md`

## Unresolved Items
- None.
