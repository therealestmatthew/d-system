# Overnight autonomous run — programme finalize batch

Written 2026-09-15 for an unattended sequential run. Ungoverned staging per
[ADR-010](../04-decisions/ADR-010-idea-staging.md): no code, no front matter. Lives here rather than
in `_working/` because an agent in a worktree must be able to read it, and rather than in
`_tmpagent/` because it is not a frozen inter-agent artifact and needs no claim.

---

You are running an unattended sequential session. **The owner is asleep and will review in the
morning. Do not stop to ask questions.** Where you would normally ask, record the question and
proceed on a stated assumption.

`AGENTS.md` governs everything. Where this prompt and `AGENTS.md` differ, `AGENTS.md` wins — **except**
for the explicit authority grants below, which the owner gave on 2026-09-15 and which override the
corresponding "ask first" steps.

## Authority granted by the owner, in advance

These are pre-approved for this batch only. Do not generalize them into standing policy.

1. **Creating worktrees and branches** — no confirmation needed.
2. **Merging into local `dev`** — no confirmation needed, subject to the gates below.
3. **Writing `status: complete`** — authorized **only** for the ten phases named below, and **only**
   when the mandatory independent review confirms every acceptance condition. This is a delegation of
   the owner's keystroke, not of the judgement: the review still decides.

**Not granted, and not to be assumed:**

- **No pushes to `origin`.** Merge to local `dev` only. The owner pushes in the morning.
- **No changes under `ts/` or `src/`.** The demo is today. If a phase's work appears to require
  application code, that phase has left its scope — stop that phase, do not edit, and treat it as a
  failure per the protocol below.
- **No writes to `_data/ideas.jsonl`.** Idea capture is staged instead; see below.
- **Do not touch `_tmpagent/`, peer worktrees, or peer claims.** `phase-arch-01`
  (`agent-arch-vocab`) and `phase-lit-07` (`agent-lit`) may still be live. Leave their files,
  branches, worktrees and backlog lines strictly alone.
- **Never edit `AGENTS.md` or `CLAUDE.md`.** If either looks wrong, record it and move on.

## The batch, in order

Ten programme finalize phases. Each turns a placeholder plan into a real requirement, a stated
design, and session-sized implementation phases under a new prefix registered in
`docs/09-backlog/README.md`.

```
phase-prog-01   Finalize the concurrency, git safety and enforcement plan (P3)
phase-prog-04   Finalize the idea graph and lifecycle plan (P1)
phase-prog-05   Finalize the document and backlog governance plan (P2)
phase-prog-06   Finalize the agent engineering and delegation plan (P4)
phase-prog-07   Finalize the autonomous agent operations plan (P5)
phase-prog-08   Finalize the retrieval and knowledge infrastructure plan (P6)
phase-prog-09   Finalize the blocked downstream projections plan (P7)
phase-prog-10   Finalize the schema consistency and testing plan (P8)
phase-prog-11   Finalize the HTML generation and design system plan (P9)
phase-prog-12   Finalize or disperse the standalone explorations bucket (P12)
```

**They must run strictly sequentially.** All 45 pairs collide on the `docs/06-requirements/`
deliverable — verified with `collisions()` on 2026-09-15. A phase is claimed only after the previous
one has completed **and merged**. The validator will reject an overlapping claim; that rejection is
correct behaviour, not an obstacle to work around.

`phase-prog-02` and `phase-prog-03` are already complete. Read their records — `SESS-2026-09-14-08`
and `SESS-2026-09-14-10` — and `PLAN-028`/`PLAN-027` as worked examples of the shape expected.

## Per-phase procedure

For each phase in order:

1. **`/session-start`**, skipping its step-2 confirmation (pre-approved). Claim on `dev` in the
   primary checkout, then work in `../d-system-worktrees/<phase-id>`. Use agent id `agent-night`.
2. **Do the work.** Requirement document with observable rows and verification methods; replace the
   placeholder with a stated design; session-sized phases under a **new** prefix registered in the
   backlog README; remove the phase from `next_up` in the same change.
3. **Allocate every document code** with `uv run python -m src.governance --next-code <kind>`. Never
   pick a number by reading a directory.
4. **Run the phase's `verification` list** and keep the real output.
5. **Run the checkpoint procedure** (`.claude/skills/checkpoint/SKILL.md`) in full, writing the
   session record with fresh acceptance verdicts.
6. **Mandatory independent review.** Spawn a **fresh, non-fork** sub-agent (never
   `subagent_type: fork` — a fork inherits your conclusions and defeats the point). Give it, in the
   prompt itself: the phase id, its `scope`/`acceptance`/`verification` pasted verbatim, the exact
   commit range `dev...agent/<phase-id>`, the session record path, and instructions to run the
   verification commands itself and decide independently whether each acceptance condition holds.
   Tell it that "no discrepancies found" is a valid result.
7. **Record the review verbatim** in a `## Review` section, condition by condition — not your summary
   of it.
8. **Close only if the review confirms every condition.** Then write `status: complete`, `session`,
   `completion_evidence` (files that exist) and `result` (actual verification and review outcome).
   Add `## Decisions`, `## Corrections` and `## Left undone` sections.
9. **Rebase onto `dev`, re-run `uv run python -m src.governance` and `uv run pytest`.** This
   post-rebase run decides whether the branch may merge. Never merge a red rebase.
10. **Confirm the primary checkout is clean.** If a peer has left uncommitted work, **stop the
    chain** — never stash it, never merge around it.
11. **Merge `--ff-only`, remove the worktree, delete the branch.** Then go to the next phase.

Run `tools/check_no_private_content.py` **with changes staged** before every commit — it reads
`git ls-files`, so an unstaged run passes by not looking.

## Failure protocol

A failure is: a red gate, a review that finds any condition unmet, a merge that is not a clean
fast-forward, or work that would require touching `ts/` or `src/`.

On any failure, **do not retry it quietly and do not push on**. Instead:

1. **Spawn a fresh non-fork triage agent.** Give it the failure output verbatim, the phase, and the
   remaining batch. Its job is twofold: attempt a bounded fix (**at most two attempts**, per
   `GOV-008`), and then judge whether this failure **blocks the remaining phases**.

2. **Treat as BLOCKING — full stop, leave state clean for morning review — if any of these hold:**
   - `dev` is left red on governance or `pytest`;
   - the backlog schema is broken, or a document code collides;
   - a merge conflict cannot be resolved cleanly without judgement;
   - the primary checkout has a peer's uncommitted work;
   - the failure indicates the shared understanding is wrong — e.g. two phases claiming the same
     prefix, or a requirement pattern that does not fit.

3. **Otherwise treat as NON-BLOCKING and continue.** The failing phase must then be **returned to
   `queued`**, its `agent`, `session`, `completion_evidence` and `result` cleared in the same edit,
   and an exact `next_action` written naming precisely what remains. **This is mandatory, not
   optional**: every remaining phase in the batch collides with it on `docs/06-requirements/`, so a
   failed phase left `active` silently blocks the entire rest of the chain. Releasing the claim is
   what lets the chain continue.

4. Record the failure, the triage verdict and the reasoning in that phase's session record, and carry
   it into the morning report.

## Questions and ideas — record, do not ask, do not write to the log

- **Questions**: where you would normally use `AskUserQuestion`, write the question, the options you
  considered, and the assumption you proceeded on, into that phase's session record under
  `## Unresolved`. Proceed on the assumption; do not block.
- **Ideas**: **do not run `tools/append_idea.py`.** Collect candidates in
  `docs/00-working/overnight-idea-candidates-2026-09-15.md`, one per heading, recorded as given, with
  the phase and moment that raised each. The owner reviews them in the morning and decides which
  enter the log.

## Agent hygiene and spend

Standing conventions from `GOV-008`'s cost protocols and `PROMPT-016`. Binding.

- **Sonnet is the standard** for judgement work — every phase's work and every review. **Haiku** for
  mechanical gates. **Opus is never pre-assigned**, and is available as **at most one documented
  escalation for the entire run**, only after two failed sonnet attempts with findings attached.
- **At most two fix cycles per work item**, then report. A third quiet retry is forbidden.
- **Truncated agent output: resume with `SendMessage`, never re-run.** Re-running pays for the whole
  context twice (idea `000077`).
- **Reviews are blind**: diff, requirement and commands only — never your rationale.
- **One dispatch per work item.** Do not spawn an agent for what a `grep` settles.
- Per-worktree `.venv`, `data/`, `ts/node_modules/`; `uv sync --extra dev` or governance fails on a
  missing `jsonschema`. Explicit free ports if anything is served — never assume 8000 or 5173.

## Morning report

Write the whole run's summary into `docs/00-working/overnight-run-2026-09-15.md`, and lead your final
message with it. Include:

- **Per phase**: id, title, the new prefix registered, the phases created with titles, the real
  output of both verification commands, and the review's actual verdict — not a rosier restatement.
- **Phases completed and merged**, phases returned to `queued` with why, and phases never reached.
- **Every failure**, its triage verdict (blocking or not) and the reasoning.
- **Spend posture**: dispatches run, resumptions after truncation, any escalation above sonnet, fix
  cycles against the cap of two, and wall-clock.
- **The idea candidates file** and the questions recorded across all session records, gathered in one
  list so the owner can act on them in one pass.
- **State of `dev`**: green or not, and the exact `git log --oneline` range the run produced.

Paste real failure output in full. Summarise walls of passing checks. A summary of a failure is not a
result.

**Begin with `phase-prog-01`.**
