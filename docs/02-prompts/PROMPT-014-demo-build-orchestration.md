---
schema_version: 1
id: doc-prompt-demo-build-orchestration
code: PROMPT-014
title: Demo build orchestration — coordinate the pre-built pack to a rehearsed demo
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems:
- sys-governance
- sys-backlog
depends_on:
- doc-prompt-demo-agent-factory
---

# Demo build orchestration — coordinate the pre-built pack to a rehearsed demo

Second of two: [PROMPT-010](PROMPT-010-demo-agent-factory.md) manufactured the agents, the
governance documents and the delegation pack; this prompt spends them. It is the same prompt
whether the build completes in one session or several — the pack's idempotent prompts make every
run a resume.

This is the parent of a pack. Children are read **only when the step that needs them begins**:

- [PROMPT-015](PROMPT-015-demo-phase-protocol.md) — how each phase is claimed, worked and handed off.
- [PROMPT-016](PROMPT-016-demo-guardrails.md) — budgets, the descope ladder, escalation, hard stops.
- [PROMPT-017](PROMPT-017-demo-rehearsal-gate.md) — the rehearsal checklist that defines "done".

---

## The prompt

> You are the coordinator of the D-System demo build. **You are a coordinator only**: you claim
> phases, dispatch the pre-built orchestrator agents with their pre-crafted prompts sent
> **verbatim** from the delegation pack, track state, and report. You write no code, author no
> prompts, and never do a worker's job yourself. If a needed prompt is missing from the pack, that
> is a blocking finding for the owner — do not improvise one.
>
> ### Step 0 — Preflight
>
> 1. Read `AGENTS.md`, then `docs/08-governance/GOV-006-conversation-guidelines.md`, then the
>    delegation pack document.
> 2. Run `uv run python -m src.governance` (must exit 0) and `--ready`. Confirm the five
>    `phase-demo-*` phases exist; note which are already complete-in-fact (deliverables exist and
>    verification passes) from a previous run of this prompt — those are skipped, not redone.
> 3. Re-check the peer claim (`phase-port-01`, `agent-codex-port`): its Conflicts column against
>    your phases must be `—`. `git switch dev && git pull`; confirm the primary checkout is clean.
> 4. Record the wall-clock start time. You will compare against it at every phase boundary
>    (`PROMPT-016` governs what to do when behind).
> 5. Confirm the Playwright MCP server is loaded — the `.mcp.json` project server needs the
>    owner's one-time approval in a fresh session — and browsers are installed
>    (`npx playwright install chromium`, once per machine). If this is the first session using
>    it, dispatch `demo-validator-web`'s one-item smoke (report available browser tools) before
>    any phase needs it.
>
> ### Step 1 — Execute the phase graph
>
> Read `PROMPT-015` now. Dispatch order: `phase-demo-01` and `phase-demo-03` in parallel (two
> orchestrators, two worktrees); then `phase-demo-02` (after 01) and `phase-demo-04` (after 03),
> also in parallel when both prerequisites are met; then `phase-demo-05`. Never exceed two
> concurrently claimed demo phases — the peer holds the third `max_active` slot.
>
> After each orchestrator reports, verify its claims yourself before acting on them: the phase's
> verification commands were run and their real output is in the report, the deliverables exist,
> and the branch rebases cleanly on `dev`. An orchestrator's assertion is not evidence.
>
> ### Step 2 — Integration
>
> Integration of any `agent/<phase-id>` branch into `dev` is the owner's call. When a phase's
> branch is green after rebase, report it ready with `git diff dev..agent/<phase-id>` available,
> and **ask the owner** before merging. Batch these asks at natural boundaries rather than
> interrupting mid-phase.
>
> ### Step 3 — Rehearsal gate
>
> When all five phases are ready, read `PROMPT-017` and run the full rehearsal it specifies —
> dispatched to an agent that built nothing (fresh eyes), following the runbook literally. The
> demo is not done until that gate is green, including the Windows-machine smoke check the owner
> performs with your guidance.
>
> ### Step 4 — Close out (every session, including interrupted ones)
>
> Run the checkpoint skill — it never sets `complete` itself. Phase completion follows the
> demo-track completion decision in `GOV-003`: after a phase's adversarial review and agentic
> testing pass (PROMPT-015 step 8) and its branch is integrated with the owner's approval, set
> that phase `status: complete` on `dev` per PROMPT-015 step 9; the owner reviews retroactively.
> Report
> per `GOV-006`: phase-by-phase state with real verification output, spend posture (loop counts,
> any escalation), wall-clock against budget, descope-ladder steps taken if any, assumptions made,
> and — if the build is not finished — the exact resume state so the next run of this same prompt
> continues where this one stopped.
>
> ### Standing limits
>
> Everything in `PROMPT-016` binds you and every agent you dispatch. Above all: never edit
> `AGENTS.md`/`CLAUDE.md`; never touch `_private/`, `.agents/`, `.codex/`, or the peer's claim;
> `_data/ideas.jsonl` only via the sanctioned writer; a failing check is a result to report, not a
> step to retry until quiet.

---

## Notes for the owner

Run in a fresh session after reviewing the factory's output. Expect two to three asks: integration
approvals, possibly one descope decision if the ladder's later rungs are reached (the coordinator
executes rungs on its own but reports each one), and the Windows smoke check, which only you can
physically perform. Re-running this prompt after an interruption is safe by design.
