---
schema_version: 1
id: doc-session-programme-planning-coordination
code: SESS-2026-09-14-12
title: Programme planning and multi-track coordination, demo eve
kind: session
status: active
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems:
- sys-backlog
- sys-governance
depends_on:
- doc-workbench-architecture-quality
- doc-workbench-features-defects
---

# Programme planning and multi-track coordination, demo eve

## Phase

**None. This session ran unclaimed**, as owner-directed work with no backlog phase, under
`AGENTS.md`'s provision for exactly that. Peers therefore held no lock against it, and nothing here
reaches `status: complete` — there was no phase to complete.

It is the coordination half of a longer sitting. The claimed half, `phase-prog-03`, has its own
record at [SESS-2026-09-14-08](SESS-2026-09-14-08-workbench-architecture-quality-plan.md) and is not
restated here. This record covers what followed it: the two coordinator prompts, the `phase-arch-00`
split, the integrations, and the sequencing decisions that produced four session prompts.

Written at the owner's direction after `phase-prog-03` closed, because the work shaped nineteen
phases across two programmes and would otherwise survive only as conversation.

## What this session produced

- **Two coordinator prompts** in `_tmpagent/`, created and activated per that directory's contract:
  `demo-track-coordinator.md` (Track A, demo-mandatory) and `p10-track-coordinator.md` (Track B, P10
  execution), the latter superseded the same evening by `p10-track-coordinator-v2.md`.
- **`phase-arch-00` and `phase-arch-18`**, the `sys-ui` decomposition split into a seam-finding phase
  and a retirement phase.
- **Four session prompts** handed to the owner: Track A, `phase-prog-02`, `phase-arch-00`, and
  `phase-arch-01` with a three-check preamble.
- **Five ideas** captured through the sanctioned writer: `000234` (decompose `sys-ui`), `000235`
  (reusable coordinator pack), `000237` (amend the checkpoint and session-close skills for a session
  with no claimed phase), and confirmation of the owner's `000232`/`000233`.
- **Integrations**: `phase-prog-03` and the `phase-arch-00` split merged to `dev`; 55 commits pushed
  to `origin`; the stale `origin/agent/phase-prog-03` pruned.

## Verification

This session declared no phase and therefore no `verification` list. The gates below were run at
every integration point, and again fresh while writing this record:

```
uv run python -m src.governance
Governance OK: 27 systems, 226 documents, 24 memories, 181 backlog phases
EXIT=0

uv run pytest
580 passed, 2 warnings
```

At the time of this session's own integrations the figures were `20 systems, 222 documents, 169
backlog phases`; the difference is peer work merged since, chiefly `phase-prog-02`'s eleven
`phase-wbf-*` phases and the seven new workbench system ids from `phase-arch-00`. Both commands were
run again after every rebase, per `AGENTS.md`'s rule that the post-rebase run decides whether a
branch may integrate. `tools/check_no_private_content.py` was run with changes staged before every
commit.

State at the close of this record: **19 `phase-arch-*` phases** and 11 `phase-wbf-*` phases.

## Decisions

**Two tracks, not one fan-out.** Asked for a coordinator prompt to run parallel agent sessions, the
measurement said not to. Every Track A candidate lands in `ts/src/stage/HtmlViewerRegion.tsx` or its
neighbours, so parallel agents would have produced conflicting branches at the worst hour. Track A
was written as one implementation agent with sequential commits, plus a browser validator and a docs
agent on genuinely different surfaces. The owner ruled the two tracks separate, demo first.

**Hygiene and cost conventions were reused, not invented.** Both prompts carry `GOV-008`'s cost
protocols and `PROMPT-016`'s guardrails verbatim in substance: sonnet standard, opus never
pre-assigned and at most one documented escalation, two fix cycles then report, resume truncated
agents rather than re-run, validator blindness, explicit ports, staged private-content check. Two
additions were specific to these tracks — dispatch discipline (subagents buy output isolation, not
parallelism, on a track whose concurrency is 1–2) and a bound on the audit phases, which sweep the
tree and are cheap to over-run.

**`phase-arch-00` was split after measuring what retirement costs.** Retiring `sys-ui` touches 33
governed documents and 28 backlog phases, 13 of them `complete` and one an active peer's claim.
Editing that last one is what `AGENTS.md` forbids, so the seam-finding half became `phase-arch-00`
and the retirement became `phase-arch-18`, gated on no peer holding the id. `REQ-011` was left
untouched because it sits under `docs/06-requirements/`, which `phase-prog-02` held — the coarse lock
working as intended, against this session.

**`phase-arch-01` was recommended over `phase-arch-00` as the next phase, then deferred.** Once
`phase-prog-02` released `sys-ui`, `phase-arch-01` became mechanically claimable — but
`phase-arch-00` had already rewritten `phase-arch-01`'s own backlog lines on its branch, changing its
systems from `sys-ui` to `sys-wb-layout`. Claiming it would have put two agents into one phase's
lines, the one `backlog.yaml` case the keep-both-sides rule does not resolve. Deferred, with a
preamble written to verify the merge before the session starts.

**Queue order was overridden four times, each on the owner's explicit ruling**, and recorded as such
rather than by silently reordering `next_up`. `phase-part-02` remains at the front, jumped five
times.

## Corrections

**The concurrency measurement was wrong in the document that claimed to be measured.** `PLAN-028`'s
execution-order table stated the wave-1 ceiling as 2 while silently omitting `phase-arch-00` — the
phase added in the same commit to fix that very problem. The true ceiling is 3, and `max_active` is
reachable in wave 1. Found by `phase-prog-03`'s independent review, not by the session that wrote it.
The Track B coordinator prompt was built on the wrong number and required a successor,
`p10-track-coordinator-v2.md`, because `_tmpagent` files are frozen once active.

**`phase-arch-00` was written oversized and colliding.** Its original scope required editing an
active peer's claim line. Caught by measuring the blast radius before handing the owner a prompt for
it, rather than by the session that would have run it.

**Acceptance condition 3 on `phase-prog-03` was first argued on bad ground** — that `phase-arch-00`
"is not an implementation phase", which that plan's own heading and coverage row contradict. The
reviewer rejected the argument and supplied a better one.

**A `sys-ui` claim was nearly taken on stale declarations.** `phase-arch-01` would have locked
`sys-ui` under today's `dev` when the correct lock after `phase-arch-00` merges is `sys-wb-layout`.

The pattern across all four: every error was in a claim about *concurrency or lock state*, and every
one was caught by running `collisions()` rather than by reading the dependency graph. Worth carrying
into `000235`'s reusable pack — the coordinator should compute the table, never restate it.

## Left undone

**`phase-arch-00` is mid-flight** under `agent-arch` and has not merged. `phase-arch-01` waits on it,
with a three-check preamble already written: confirm the merge, recompute the collision set against
the narrower ids, and verify P11's `depends_on: [phase-arch-01]` edges.

**The P11 edges are unverified.** `PLAN-028` requires any `phase-wbf-*` phase that renames a slot,
panel, region or layout identifier to declare `depends_on: [phase-arch-01]`. Four of the eleven carry
the edge. Three more flagged on a deliberately noisy heuristic and need reading by a human or by the
`phase-arch-01` session; `phase-wbf-11` is a completed backfill and correctly needs none.

**A peer's session record was left dirty in the primary checkout** —
`docs/03-sessions/SESS-2026-09-14-11-decompose-sys-ui-lock.md`, modified and uncommitted, belonging
to `phase-arch-00`. Reported to the owner and deliberately not inspected, stashed or reverted. An
agent should not be writing a session record into the primary checkout at all; whether that is a
protocol breach or an abandoned run is the owner's to determine.

**Two worktrees look abandoned** — `research-article` and `source-archival`, sitting on commits well
behind `dev`, with remote branches still present. Untouched.

**`phase-arch-18` has no scheduling condition beyond its dependency.** It cannot run while any active
claim declares `sys-ui`, which its scope states but no check enforces.

## Unresolved

**Nothing in this session reached a completion gate, because nothing was claimed.** That is the
correct outcome for owner-directed work, not a shortfall — but it does mean none of the nineteen
phases this session shaped has been through an independent review. The review that ran covered
`phase-prog-03`'s four acceptance conditions only.

**`000235` (the reusable coordinator pack) is captured but unplanned.** It sits in the idea log with
no programme, and the analysis it would automate was run by hand three times today.

**This record could not be produced by either governed workflow.** `checkpoint` says to stop when no
phase is active; `session-close` runs the checkpoint procedure and then gates on acceptance
conditions and a phase transition that do not exist here. Both were followed as far as they applied
and the rest was written by hand, which is why this section exists rather than a `## Review` one —
no independent review ran, because there were no acceptance conditions to review against. Captured
as `000237`.
