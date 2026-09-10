---
schema_version: 1
id: doc-prompt-demo-agent-factory
code: PROMPT-010
title: Demo agent factory — build the roster and prompt pack for the live demo
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems:
- sys-governance
- sys-backlog
depends_on: []
---

# Demo agent factory — build the roster and prompt pack for the live demo

First of two: this prompt is run in its own session and produces every accessory the build session
needs — the governance documents, the agent definitions, and the complete set of delegation prompts.
[PROMPT-014](PROMPT-014-demo-build-orchestration.md) then runs the build using only what this
session produced. Nothing is authored mid-build; if this session did not write it, the build session
does not send it.

Single-use in intent (it exists for the 2026-09-10 demo), reusable in shape: the factory pattern —
roster, delegation pack, validation gate — applies to any future multi-agent build.

This is the parent of a pack. The child documents carry the detailed specifications and are read
**only when the step that needs them begins**, never up front:

- [PROMPT-011](PROMPT-011-demo-governance-docs-spec.md) — the governance documents to write.
- [PROMPT-012](PROMPT-012-demo-agent-roster-spec.md) — the eight agent definitions.
- [PROMPT-013](PROMPT-013-demo-delegation-pack-spec.md) — the delegation prompts and the
  validation gate that certifies the whole factory output.

---

## The prompt

> You are the agent factory for the D-System live demo. Your session produces documents and agent
> definitions only — **you write no `src/`, `ts/`, `templates/` or `tools/` code in this session.**
> The build itself happens later, in a separate session driven by `PROMPT-014`, using exactly and
> only what you produce now.
>
> This is a documentation-and-`.claude/`-only session with no deliverable outside `docs/`,
> `_data/ideas.jsonl` (via the sanctioned writer), and `.claude/`, so per `GOV-003` you work
> directly in the primary checkout on `dev`. Do not create a worktree.
>
> ### Step 0 — Preflight
>
> 1. Read `AGENTS.md`, then `docs/08-governance/GOV-006-conversation-guidelines.md`.
> 2. Run `uv run python -m src.governance` — it must exit 0 before you change anything. If it does
>    not, stop and report; do not fix pre-existing failures.
> 3. Run `uv run python -m src.governance --ready` and confirm the peer claim on `phase-port-01`
>    (`agent-codex-port`) is still the only active phase. Never touch `.agents/`, `.codex/`, or any
>    file of that phase.
> 4. Confirm you are on `dev` and it is clean apart from your own work.
>
> ### Step 1 — Governance documents
>
> Read `PROMPT-011` now and produce what it specifies: the demo requirements document, the demo
> plan, the terminal-capability ADR, the five `phase-demo-*` backlog phases, the `systems.yaml` and
> `next_up` updates, and the idea-log annotations on `000070`/`000071`. Allocate every code with
> `uv run python -m src.governance --next-code <kind>`; never pick a number by reading a directory.
>
> ### Step 2 — Agent roster
>
> Read `PROMPT-012` now and write the eight agent definitions under `.claude/agents/` exactly as
> specified — names, models, tools, `maxTurns`, and the truncation rule. The model policy in that
> document is binding: haiku for mechanical work, sonnet as default, opus never pre-assigned.
>
> ### Step 3 — Delegation prompt pack and write fences
>
> Read `PROMPT-013` now and produce the delegation pack — every prompt the build coordinator
> will send, one delimited section per dispatch, each idempotent — plus the `.claude/settings.json`
> permission fences it specifies.
>
> ### Step 4 — Validation gate
>
> Still following `PROMPT-013`: dispatch the checklist validator over every artifact you
> produced, then smoke-test each agent once. Fix findings and re-validate, at most twice; residual
> findings are reported to the owner, not silently accepted.
>
> ### Step 5 — Close out
>
> 1. Regenerate the catalog (`--catalog`), regenerate `docs/00-working/ideas.md` if you touched the
>    idea log, and run `uv run python -m src.governance` — exit 0 is a completion condition.
> 2. Stage everything and run `uv run python tools/check_no_private_content.py` **with changes
>    staged**.
> 3. Run the checkpoint skill. Do not mark any phase complete; only `/session-close` does that.
> 4. Report per `GOV-006`: what exists now, file by file; the validator's findings and their
>    dispositions; every assumption you made; and the exact sentence the owner should paste to start
>    the build session.
>
> ### Standing limits
>
> - Never edit `AGENTS.md` or `CLAUDE.md`.
> - Never write to `_data/ideas.jsonl` except through `tools/append_idea.py`.
> - Never read or write `_private/`, `.agents/`, or `.codex/`.
> - Do not integrate anything into `dev` beyond your own commits of the artifacts above; do not
>   push without asking; do not touch the peer's claim.
> - If a specification in the pack conflicts with repository reality, stop and ask the owner with
>   the AskUserQuestion tool — do not reinterpret.

---

## Notes for the owner

Run this in a fresh session, alone — it assumes no peer beyond `phase-port-01`. Budget roughly
60–90 minutes including the validation gate. Its output is reviewable before anything builds: read
the delegation pack and the phase definitions the way you would read a contract, because `PROMPT-014`
executes them without judgment.
