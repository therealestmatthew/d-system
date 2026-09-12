---
schema_version: 1
id: doc-prompt-execute-a-phase
code: PROMPT-008
title: Execute one backlog phase
kind: prompt
status: active
owner: repository-owner
created: '2026-09-09'
updated: '2026-09-09'
systems:
- sys-governance
- sys-backlog
depends_on: []
---

# Execute one backlog phase

Third of four: [PROMPT-006](PROMPT-006-idea-capture-and-triage.md) captures and triages,
[PROMPT-007](PROMPT-007-idea-to-plan.md) plans, this one executes, and
[PROMPT-009](PROMPT-009-plan-audit.md) audits.

Reusable. This is the working loop — run it repeatedly to advance the backlog one phase per session.

---

## The prompt

> You are working in the D-System repository. Read `AGENTS.md` first — it is the working agreement
> and governs everything here regardless of which framework you are running under. Then read
> `docs/08-governance/GOV-002-backlog-protocol.md`,
> `docs/08-governance/GOV-003-backlog-decisions.md` (when a worktree is required, and the
> primary-checkout exception) and `docs/08-governance/GOV-006-conversation-guidelines.md`.
>
> Your job is to execute **one** phase, end to end, and stop before closing it.
>
> ### Choose and claim
>
> 1. `uv run python -m src.governance --ready`
> 2. Take the **first ready phase in the rendered order**. `next_up` is the front of the queue and
>    overrides priority. Choose a phase whose **Conflicts** column is `—`; a non-empty Conflicts
>    column means a peer holds one of your systems or paths, so pick something else rather than
>    waiting. Never edit a peer's claim.
> 3. **Claim it before doing any work**: set `status: active` and `agent: agent-<name>` on that phase
>    in `docs/09-backlog/backlog.yaml`, in one small commit that changes nothing else. Run
>    `uv run python -m src.governance` before committing the claim — it rejects a claim that overlaps
>    a peer's systems, paths or dependency chain, or that exceeds `max_active`.
>
> Do not skip the claim. On 2026-09-09 a phase was worked while still `queued`; nothing was lost
> because no peer was active, but the lock table showed the work as not happening.
>
> ### Where to work
>
> Use a git worktree if the phase touches `src/`, `ts/`, `schemas/`, `sql/`, `tools/` or `test/`, or
> if any peer holds an active claim. A documentation-only phase with no peer claim may use the
> primary checkout on `main` — that is the GOV-003 exception, not a general licence.
>
> ### Do the work
>
> The phase's `scope`, `acceptance` and `verification` are the boundary. Do not widen it. If you find
> a real problem outside the scope, record it — an idea, or a note in your report — and leave it.
> Scope creep inside a claimed phase is invisible to the lock table and collides with peers.
>
> If the phase turns out to be wrong — its acceptance is uncheckable, its dependencies are unmet, its
> scope is incoherent — stop and say so. That is a finding, not a failure. Do not reinterpret a phase
> into something you can finish.
>
> ### Verify honestly
>
> Run every command in the phase's `verification` list and record the **literal output**. Never
> paraphrase a failure into a pass; a summary of a failure is not a result. A failing check is
> something to record and report, not to retry until it goes quiet.
>
> Then check each `acceptance` condition one at a time against what you actually observed, and mark
> it Met or Not met. **Finding conditions unmet is the expected outcome of most sessions.** Write it
> down and move on.
>
> ### Record and stop
>
> Follow the canonical checkpoint workflow in `agent-workflows/checkpoint.md`. Invoke the repository's
> discovered checkpoint skill when the host supports one; otherwise read that canonical workflow
> directly as the plain-prompt fallback. Its session-record contract is authoritative, so do not
> restate or reinvent it here. It writes one record per session and regenerates its sections from
> observed state.
>
> **Never write `status: complete`.** Only the owner-invoked `/session-close` does that, after an
> independent sub-agent review. If you believe the phase is done, say so, checkpoint, and stop. Do
> not reproduce session-close's steps yourself.
>
> ### Finishing
>
> - `uv run python -m src.governance --catalog > docs/08-governance/catalog.md` if you touched a
>   governed document.
> - `uv run python -m src.governance` must exit 0. `uv run pytest` must be green. Do not hand back a
>   red tree with a session record describing it as fine.
> - `uv run python tools/check_no_private_content.py` **with your changes staged** — it reads
>   `git ls-files`, so an unstaged file is invisible to it.
> - Never write a confidential identifier into a tracked file, including a document *describing* the
>   identifiers.
> - Commit your work. Never use `--no-verify`; a rejecting hook is a finding, not an obstacle.
> - Do not push without asking the owner.
>
> Report: which phase, which acceptance conditions are Met and Not met with the evidence, what you
> left undone and why. Name things before citing codes — "the session taxonomy phase
> (`phase-ses-01`)", not a bare id.

---

## Notes for the owner

The two rules this prompt states most firmly are the two that were broken most recently: claim
before working, and never self-certify completion. Both failures are survivable alone and compound
badly together — an unclaimed phase that an agent also declares finished leaves no trace that anyone
else could have checked.

The verification instruction is deliberately blunt about failures. The value of a session record is
that it can be trusted without re-running everything, and that property is destroyed the first time
a red result is written down as green.
