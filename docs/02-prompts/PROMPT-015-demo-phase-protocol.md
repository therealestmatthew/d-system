---
schema_version: 1
id: doc-prompt-demo-phase-protocol
code: PROMPT-015
title: Demo pack — phase execution protocol
kind: prompt
status: active
owner: repository-owner
created: '2026-09-10'
updated: '2026-09-10'
systems:
- sys-backlog
depends_on:
- doc-prompt-demo-build-orchestration
---

# Demo pack — phase execution protocol

Child of the build orchestration prompt ([PROMPT-014](PROMPT-014-demo-build-orchestration.md)),
read at its Step 1. How the coordinator runs one phase, from claim to hand-off. This restates
nothing from `AGENTS.md` except where the demo build narrows it further; where silent, `AGENTS.md`
governs.

## Claim

1. On clean, up-to-date `dev`: set the phase `status: active`, `agent:` the driving orchestrator's
   claim id (`agent-demo-stage`, `agent-demo-data`, or `agent-demo-content` — one id per
   orchestrator, each holding at most one active phase, per the backlog schema and AGENTS.md),
   and bump the
   catalog `updated` date — one commit, nothing else in it. Run
   `uv run python -m src.governance` before committing; a rejected claim means a peer moved —
   re-pull, re-check, re-decide.
2. Create the worktree: `git worktree add -b agent/<phase-id> ../d-system-worktrees/<phase-id> dev`,
   then resolve that path to an **absolute path** — every prompt sent for this phase carries it.
3. In the worktree: `uv venv && uv sync --extra dev`, `uv run python tools/rebuild_db.py`, and
   `cd ts && npm install` for frontend phases. Dev servers use ports 8010 (backend) and 5180
   (frontend) only.

## Dispatch

4. Send the phase's orchestrator its kickoff prompt from the delegation pack **verbatim**, spawned
   as the agent the pack names. The orchestrator dispatches its own creators and validators using
   the pack's task prompts, also verbatim, and runs the creator→validator loop: at most two fix
   cycles per work item, then judge, then report up.
5. If any agent's output is truncated by its turn limit, **resume that agent** to recover the
   work; never re-run the task from scratch (idea `000077`).
6. While a phase runs, the coordinator does not idle-poll; it processes completed reports, prepares
   the next dispatch, or handles an owner interaction.

## Verify and hand off

7. On the orchestrator's completion report, independently confirm in the worktree: every
   verification command from the backlog phase passes with output captured; deliverables exist;
   `git rebase dev` is clean and the post-rebase governance + pytest run is green; the staged
   private-content check passes.
8. Run the phase's completion gate (the demo-track completion decision in `GOV-003`): dispatch
   the phase's adversarial review (`demo-adversary`, pack section D0N-A) and, for a phase with a
   browser-facing deliverable, the Playwright web checks (`demo-validator-web`, pack sections
   D02-W / D04-W / D05-W) — at most two fix cycles for findings, then escalate to the owner.
   Write/update the session record via the checkpoint skill (the orchestrator's report is the
   input); the checkpoint itself never sets `complete`.
9. Report the branch ready for the owner's integration decision. After the approved merge, and
   only if step 8's gate is green, set the phase `status: complete` on `dev` — with `session`,
   `completion_evidence` and `result` recording what actually happened — in one small commit, per
   the demo-track completion decision in `GOV-003`; the owner reviews retroactively. Then remove
   the worktree and delete the branch, and tell the still-running orchestrators to rebase their
   branches onto `dev`.

## Collisions

`backlog.yaml` conflicts: keep both sides, never `--ours`/`--theirs`. A conflict in `src/`, `ts/`,
`schemas/` or `sql/` between demo branches means the phase declarations were wrong — stop both
phases and report; do not force a merge. Duplicate document codes: the branch integrating second
renumbers.
