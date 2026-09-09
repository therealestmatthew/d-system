---
id: mem-proc-session-close-no-active-phase
title: Handling /session-close When No Phase Is Active
type: procedure
tags: [ai-tools, agentic-systems, knowledge-base]
source_model: anthropic/claude-sonnet-5
project: d-system
created: 2026-09-09
updated: 2026-09-09
confidence: high
related: [mem-proc-add-memory, mem-proc-resolve-idea-triage-followups]
scope: project
---

## The situation

`.claude/commands/session-close.md`'s mechanical procedure assumes exactly one thing: there is
a phase with `status: active` in `docs/09-backlog/backlog.yaml`, and the command's job is to
checkpoint it, get it independently reviewed, and decide whether it reaches `status: complete`.

That assumption breaks in a specific, recurring pattern: the owner closes a phase mid-session
(a legitimate `/session-close` run reaches `status: complete`), then keeps directing more work
in the *same conversation* — "also fix this," "also triage the rest," "also harden this
against X" — without re-claiming a new phase for it. Eventually the owner types
`/session-close` again, sometimes with extra instructions layered into the invocation itself
(document what we did, plan the next piece, stage follow-ups for later). At that point there is
no active phase for the mechanical procedure to run against.

## What not to do

- **Do not silently force the 9-step procedure onto nothing** — inventing a phase to checkpoint
  that was never claimed, or re-running checkpoint/review against the phase that already closed,
  fabricates a result nobody asked for and re-litigates a decision already made.
- **Do not ignore the extra instructions and just report "nothing to close.**" If the owner
  asked for documentation, a plan, or a follow-up list in the same message, that is the actual
  content of the request — `/session-close` was typed because closing-out documentation is what
  it's associated with, not necessarily because a specific phase needs closing.
- **Do not quietly paper over the gap.** Work happening after a phase's formal close, without a
  new claim, is itself a process deviation worth naming plainly in the report — not a failure to
  hide, but a pattern worth the owner seeing so they can decide whether to tighten the habit of
  claiming a phase before "one more thing" starts.

## What to do instead

1. **State the situation plainly before proceeding**: which phase already closed, when, and that
   everything since happened without a new claim. This is the "say plainly" half of `GOV-006`'s
   correction rule, applied to a process gap rather than a factual error.
2. **Extend the existing session record with an addendum**, rather than opening a second one.
   It is the same continuous session; `checkpoint`'s own contract already permits a record
   "genuinely covering more" than one phase's scope when the extra work is a natural adjacent
   consequence of the first (here: real-world exercise of exactly what the closed phase built,
   surfacing bugs and hardening needs).
3. **For anything the owner wants planned but not built yet, add a new backlog phase in
   `status: queued`** (never `active` or `complete`) under whichever existing governed plan it
   belongs to. Write the actual design into the session record addendum in full, and reference
   it tersely from the phase's `scope`/`next_action` — this satisfies `AGENTS.md`'s
   plan-before-implementing requirement without asserting any acceptance condition is met, because
   none has been attempted yet.
4. **For anything staged as decisions for a future session, build it as an ephemeral file under
   `_working/`** (per `PLAN-015` — gitignored, no code, deleted once worked through), not a
   governed document. A list of proposed links/promotions/follow-ups to review later is task
   detail for upcoming work, not a statement of how the system should work.
5. **Run the normal mechanical hygiene anyway**: regenerate the catalog, confirm governance and
   the test suite are green, commit. None of steps 2-4 change that a red tree is never an
   acceptable thing to close a session on top of.
6. **The final report says clearly that no phase reached `status: complete` in this
   invocation**, names what was actually produced (documentation, a queued phase, a working
   file), and does not let the mechanical report template's language ("the phase reached
   complete") imply a completion that didn't happen.

## Worked example (2026-09-09)

`phase-idea-02` (build the idea triage agent) closed complete earlier in
`SESS-2026-09-08-18`. The owner then directed a branch audit, a full 44-idea triage sweep, a
test-fixture fix, and two guardrails against a data-integrity bug found along the way — all in
the same conversation, none under a new phase claim. `/session-close` was invoked again with
instructions to document the fixes, plan a follow-up hardening piece, and stage the triaged
ideas' follow-up decisions for a fresh session.

Resolution: extended `SESS-2026-09-08-18` with an `## Addendum` section covering everything
since closure; added `phase-idea-10` (`queued`) with the follow-up design written into the
addendum; wrote `_working/idea-triage-followups.md` staging 33+ proposed links/promotions for
a future session to present via `AskUserQuestion` batches. Reported explicitly that no new
phase reached `complete` in that invocation.

## Why this is worth a durable entry

This is not a one-off mistake to correct once — it is a structural property of how sessions in
this repository actually run: a phase closes, the owner keeps going, and eventually
`/session-close` gets invoked again against a state its own written procedure does not
literally describe. Any model working in this repository will hit this exact fork. Filed in
`brain/` rather than only in the session record it originated from, so the next model to hit it
does not have to re-derive the same adaptation from first principles.

## Related standing requirement

`AGENTS.md`'s concurrent-agents section already establishes that a claim should precede
sustained work on `src/`, `ts/`, `schemas/`, `sql/`, `tools/` or `test/`. This procedure is the
session-close-side consequence of the same discipline: the fix for "work happened without a
claim" is to claim earlier next time, not to retroactively manufacture a checkpoint for
unclaimed work after the fact.
