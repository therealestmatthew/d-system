---
schema_version: 1
id: doc-prompt-demo-glossary-diagram-audit
code: PROMPT-019
title: Skills-and-agents glossary and diagram library — audit and build
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems:
- sys-brain
- sys-demo-overview
depends_on:
- doc-live-demo
- doc-live-demo-requirements
---

# Skills-and-agents glossary and diagram library — audit and build

Single-agent prompt for `phase-demo-07`. Unlike the rest of the live-demo pack
([PROMPT-010](PROMPT-010-demo-agent-factory.md) through [PROMPT-018](PROMPT-018-demo-build-delegation-pack.md)),
this is not multi-agent orchestration — one fresh agent audits the phase as drafted, revises what
the audit finds wrong, then builds it. The plan it is auditing was written in a separate session at
the owner's direction, for the owner's live training session on 2026-09-10 (idea `000070`): a
skills-and-agents glossary and a standalone SVG diagram library the owner presents from, distinct
from and running alongside the terminal/overview stage build in `phase-demo-01` through
`phase-demo-06`.

## The prompt

> You are auditing and then building `phase-demo-07` in `docs/09-backlog/backlog.yaml` — read it
> now, in full, before anything else. It covers REQ-006 R13
> (`docs/06-requirements/REQ-006-live-demo.md`) and the matching entry in
> `docs/01-plans/PLAN-021-live-demo.md`'s Build structure section. Read both.
>
> ### Step 0 — Preflight
>
> 1. Read `AGENTS.md` in full, then `docs/08-governance/GOV-006-conversation-guidelines.md`.
> 2. Read `docs/08-governance/GOV-003-backlog-decisions.md`'s "demo track completes through its
>    testing gate" section. It names five `phase-demo-*` phases plus `phase-demo-06` by explicit
>    owner decision — `phase-demo-07` is not on that list. Treat it as **not** covered by that
>    exception unless you find the owner extended it somewhere you can cite. That means: you do not
>    self-mark this phase `complete`. Leave it `active` (if the audit and build succeed) or `queued`
>    (if they do not) with an honest `next_action`, per `/session-close` remaining the only path to
>    `complete` outside the named exception.
> 3. Run `uv run python -m src.governance --ready` and confirm `phase-demo-07`'s Conflicts column
>    is `—`. If a peer now locks `sys-brain` or `sys-demo-overview`, stop and report — do not pick a
>    substitute phase.
>
> ### Step 1 — Audit
>
> Before writing anything, review the plan as drafted with genuine skepticism — the session that
> wrote it had no fresh pair of eyes on it. Check specifically:
>
> - **Term accuracy and completeness.** Is each core term (LLM, Agent, Sub-agent, Tool, MCP,
>   Context, Command, Skill) definable precisely and correctly against this repository's actual
>   `.claude/` conventions (look at a real skill under `.claude/skills/`, a real agent under
>   `.claude/agents/`, and how MCP is configured in `.mcp.json` if present) rather than generically?
>   Is the proposed additional-term set (Prompt/System prompt, Token, Tool call, MCP server,
>   Session, Memory, Orchestration/Multi-agent) worth keeping in full, worth trimming, or missing
>   something a skills-and-agents audience would need? You have the authority to finalize this list
>   yourself — the phase's `next_action` flags it as open specifically so you resolve it here, not
>   so you pause and ask. Record your reasoning for any change.
> - **Diagram set.** Are the five diagrams (LLM vs agent, skill architecture, the agentic loop, MCP
>   architecture, command/skill/tool distinction) the right five — any redundant, any missing, any
>   better split or merged? You may revise this set with reasoning recorded.
> - **Mechanism fit.** `brain/concepts/terms-skills-and-agents-demo.md` is meant to follow the
>   grouped-entry convention in `brain/concepts/terms-systems-vocabulary.md` — read that file as the
>   style model. Confirm `tools/generate_glossary.py --tag demo-glossary --out
>   docs/00-working/demo-glossary.md` is the right mechanism by reading the tool's source and
>   `docs/08-governance/OPS-004-generate-glossary.md`; confirm writing to `docs/00-working/` (per
>   [ADR-010](../04-decisions/ADR-010-idea-staging.md)) rather than committing a second canonical
>   glossary is consistent with OPS-004's rule that only the unfiltered `GLOSSARY.md` is committed.
> - **Deliverable paths and systems.** Confirm `docs/07-architecture/diagrams/demo/` is a sane
>   location per this project's Directory Reference in `CLAUDE.md`, and that `sys-brain` /
>   `sys-demo-overview` are the right systems to lock — revise the phase's `systems:` field if not.
>
> If the audit changes scope, acceptance, deliverables, the term list or the diagram list, edit
> `phase-demo-07` in `docs/09-backlog/backlog.yaml` and the corresponding text in
> `REQ-006`/`PLAN-021` directly — these are ordinary governed documents you may edit as part of your
> work (unlike `AGENTS.md` and `CLAUDE.md`, which no agent ever edits without the owner's explicit
> approval). Note every change and its reason in your session record (Step 4).
>
> ### Step 2 — Claim and set up
>
> A peer (`agent-demo-stage` on `phase-demo-06`, `agent-codex-port` on `phase-port-01`) holds an
> active claim right now, so per AGENTS.md's "Concurrent agents: work in a worktree" section, a
> worktree is required — do not work directly on `dev`.
>
> 1. Pick an agent ID: `agent-demo-glossary`.
> 2. On `dev`: set `phase-demo-07`'s `status: active` and `agent: agent-demo-glossary` (plus any
>    Step 1 revisions), run `uv run python -m src.governance`, commit, push.
> 3. `git worktree add -b agent/phase-demo-07 ../d-system-worktrees/phase-demo-07 dev`, then `cd`
>    into it and `uv venv && uv sync --extra dev`.
>
> ### Step 3 — Build
>
> Inside the worktree, per the phase's (possibly revised) scope:
>
> 1. Write `brain/concepts/terms-skills-and-agents-demo.md` — `type: concept`, `tags: [demo-glossary]`,
>    grouped term entries in the style of `terms-systems-vocabulary.md`, covering the finalized term
>    set from Step 1 plus one-line entries for the advanced topics named out of scope for depth
>    (Hooks, Agent permissions, Observability, Agent SDK).
> 2. Run `uv run python tools/generate_glossary.py --tag demo-glossary --out
>    docs/00-working/demo-glossary.md` twice; confirm byte-identical output.
> 3. Build the finalized diagram set as standalone SVGs under `docs/07-architecture/diagrams/demo/`,
>    each self-contained (no external asset or network dependency), legible at a projector-safe
>    1024×768, and terminology-consistent with the glossary entries. Add
>    `docs/07-architecture/diagrams/demo/README.md` indexing them with a one-line caption each.
>
> ### Step 4 — Verify, record, hand off
>
> 1. Run every command in `phase-demo-07`'s `verification` list and keep the real output.
> 2. Write a session record: allocate its code with `uv run python -m src.governance --next-code
>    session`, name it `<code>-demo-glossary-diagrams.md`, and cover outcomes, evidence, every Step 1
>    revision and its reasoning, and anything unresolved.
> 3. Confirm each `acceptance` condition against the actual output — do not assert one that is not
>    genuinely met.
> 4. Per Step 0.2, do not set `status: complete`. Update `next_action` honestly: what is done, what
>    verification shows, and that the phase awaits the owner's `/session-close` (or an explicit
>    owner decision extending the `GOV-003` demo-track exception to this phase).
> 5. `git rebase dev`, re-run `uv run python -m src.governance` and
>    `uv run python tools/check_no_private_content.py` with your changes staged.
> 6. Report to the owner: the branch is `agent/phase-demo-07`, ready for review — do not integrate
>    it onto `dev` yourself (per AGENTS.md, integration is the owner's call even though pushing your
>    own branch needs no approval).
