---
schema_version: 1
id: doc-prompt-demo-delegation-pack-spec
code: PROMPT-013
title: Demo pack — delegation prompts and validation gate specification
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

# Demo pack — delegation prompts and validation gate specification

Child of the agent factory prompt ([PROMPT-010](PROMPT-010-demo-agent-factory.md)), read at its
Steps 3 and 4. Specifies the delegation prompt pack, the permission fences, and the validation gate
that certifies the factory's whole output.

## 1. The delegation pack

One governed prompt document (allocate its code) titled "Demo build delegation pack", containing
**every prompt the build coordinator will send during PROMPT-014**, one clearly delimited section
per dispatch:

- One orchestrator kickoff prompt per phase (five total), each naming: the phase id, the agent to
  spawn it as, the **absolute worktree path** (`../d-system-worktrees/<phase-id>` resolved to an
  absolute path), the branch (`agent/<phase-id>`, from `dev`), the assigned dev ports (backend
  8010, frontend 5180 — never 8000/5173), the phase's deliverables and verification commands
  verbatim from the backlog, and which creator/validator prompts from this pack to use.
- Creator task prompts and validator task prompts for each work item within a phase. Validator
  prompts include only the diff reference, the requirement text and the commands to run — creator
  rationale is deliberately excluded.

Every prompt in the pack is **idempotent**: it opens with "Assess the current state of the
worktree and repository against the deliverables below; do only what is missing; report what
already existed." This makes the build session one-shottable and resumable with the same pack,
across as many sessions as needed.

Prompts reference repository documents by path instead of inlining them, so context is loaded when
used, not when dispatched.

## 2. Permission fences (`.claude/settings.json`)

Add deny rules so the standing limits are mechanical rather than instructional: no edits to
`AGENTS.md` or `CLAUDE.md`; no writes under `_private/`, `.agents/`, `.codex/`; no direct writes to
`_data/ideas.jsonl` (the sanctioned writer runs via Bash and is unaffected). Keep the rules narrow
— fence exactly these paths, nothing else — and note each rule's reason in the session record.

## 3. The validation gate

Dispatch `demo-validator-check` (haiku) over everything the factory produced, against this
checklist:

1. Every agent file parses; frontmatter has `name`, `description`, `tools`, `model`, `maxTurns`;
   model assignment matches the policy in `PROMPT-012`; workers lack the `Agent` tool,
   orchestrators have it.
2. Every delegation prompt names its agent, its absolute worktree path, its branch, its ports, and
   its stop condition; every prompt opens with the idempotency clause.
3. The five phases exist, are internally consistent (dependencies, systems disjoint from the
   peer's), and their verification commands are runnable as written.
4. The governed documents carry valid front matter and allocated codes; the catalog regenerates
   cleanly; `uv run python -m src.governance` exits 0.
5. No file names a confidential identifier (run the private-content check with changes staged).
6. The descope ladder, the Windows rehearsal gate, and the live-segment timeboxes appear verbatim
   where PLAN and runbook-related documents claim them.

Then smoke-test each of the eight agents once with a trivial in-character task (e.g., a validator
validates one file, a creator writes to the scratch directory — never to the repository). A smoke
test that fails is a finding.

Fix findings and re-run the gate, at most twice. Whatever remains goes to the owner as a ranked
findings list, per `GOV-006` — never silently accepted.
