---
schema_version: 1
id: doc-prompt-demo-agent-roster-spec
code: PROMPT-012
title: Demo pack — agent roster specification
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems:
- sys-governance
depends_on:
- doc-prompt-demo-agent-factory
---

# Demo pack — agent roster specification

Child of the agent factory prompt ([PROMPT-010](PROMPT-010-demo-agent-factory.md)), read at its
Step 2. Specifies the eight agent definitions the factory writes under `.claude/agents/`.

## Model policy (binding)

Haiku for mechanical, checklist-shaped work. Sonnet as the default for everything requiring
judgment. **Opus is never pre-assigned to any agent.** The build coordinator may re-run exactly one
failed work item on opus, only after two sonnet attempts have failed with validator findings
attached, and must report having done so. Nesting is supported (subagents may spawn subagents up to
three layers below the main session), so the coordinator → orchestrator → worker shape works as
designed; orchestrators need the `Agent` tool in their `tools` list, workers must not have it.

## Shared rules (in every agent body)

- Set `maxTurns` generously per the table. If output is ever truncated by the turn limit, the
  dispatcher resumes the same agent to recover the work — never re-runs it from scratch (the
  lesson of idea `000077`).
- Every dispatch prompt received will state an absolute working directory (a worktree path). The
  agent runs all commands against that path and never assumes the primary checkout.
- Never edit `AGENTS.md` or `CLAUDE.md`; never touch `_private/`, `.agents/`, `.codex/`; never
  write `_data/ideas.jsonl` except via `tools/append_idea.py`.
- Report honestly per `GOV-006`: failing output is a result to paste, not a step to retry quietly.

## The roster

| name | model | effort | maxTurns | tools | role |
|---|---|---|---|---|---|
| `demo-orch-stage` | sonnet | medium | 60 | Read, Grep, Glob, Bash, Edit, Write, Agent | Orchestrates `phase-demo-01` and `phase-demo-02`: claims, worktree setup, dispatching creators/validators with their pre-crafted prompts, running phase verification |
| `demo-orch-data` | sonnet | medium | 60 | Read, Grep, Glob, Bash, Edit, Write, Agent | Same, for `phase-demo-03` and `phase-demo-04` |
| `demo-orch-content` | sonnet | medium | 60 | Read, Grep, Glob, Bash, Edit, Write, Agent | Same, for `phase-demo-05`; also runs the fresh-eyes rehearsal dispatch |
| `demo-creator-py` | sonnet | high | 50 | Read, Grep, Glob, Bash, Edit, Write | Python: PTY adapter, websocket route, deterministic tools, tests |
| `demo-creator-web` | sonnet | high | 50 | Read, Grep, Glob, Bash, Edit, Write | TS/React/HTML/CSS: xterm.js wiring, rotator, panels, zero-scroll layout, templates |
| `demo-creator-docs` | haiku | medium | 30 | Read, Grep, Glob, Bash, Write | OPS docs, templated checklists, runbook skeleton. Talking-points *copy* is NOT theirs — it is audience-facing and belongs to `demo-orch-content` (sonnet) |
| `demo-validator-code` | sonnet | medium | 40 | Read, Grep, Glob, Bash | Reviews a diff against its requirement and runs the verification commands. Receives the diff, the requirement text and the commands — **never the creator's rationale** |
| `demo-validator-check` | haiku | medium | 30 | Read, Grep, Glob, Bash | Mechanical gates: governance run, staged private-content check, schema and drift checks, frontmatter and checklist audits |
| `demo-adversary` | sonnet | high | 50 | Read, Grep, Glob, Bash | Adversarial per-phase review of the branch diff against spec and repository reality — part of the demo-track completion gate (`GOV-003`) |
| `demo-validator-web` | sonnet | medium | 50 | Read, Grep, Glob, Bash, mcp__playwright | Playwright-driven browser verification of the stage and generated pages (zero-scroll, popups, terminal echo, rendered figures) — part of the same gate |

**Amended 2026-09-10 (owner decision).** The roster grew from eight to ten: the owner substituted
the mid-build `/session-close` pauses with an adversarial-review + agentic-testing completion gate
(recorded in `GOV-003`), which needs a dedicated adversarial reviewer and a browser-driving
validator using the Playwright MCP server configured in `.mcp.json`. The model policy above is
unchanged and still binding — both additions are sonnet, and opus remains never pre-assigned.

Each definition's body states: its single responsibility, what it must produce, what it must never
do, and its stop condition (deliverables exist and verification output is pasted, or a blocking
finding is reported). Orchestrator bodies additionally carry the creator→validator loop rule: at
most two fix cycles per work item, then judge, then report up — never a third quiet retry.
