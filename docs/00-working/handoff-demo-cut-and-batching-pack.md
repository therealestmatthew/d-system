# Handoff — demo fast-lane cut and the idea-batching pack

Ungoverned staging ([ADR-010](../04-decisions/ADR-010-idea-staging.md)). Written 2026-09-12 at the
close of `SESS-2026-09-12-06`, then rewritten the same day once the owner ruled on every open item.

Full account: [`SESS-2026-09-12-06`](../03-sessions/SESS-2026-09-12-06-demo-cut-and-batching-pack.md).

## What remains

Three items, none blocking.

### 1. `GOV-008` stage 5 — the adversarial audit of the pack

The pack is manufactured, independently reviewed at session close, and the one defect that review
surfaced is fixed (see item 2.4 below, now closed). It has **not** had its stage 5 adversarial
audit. **No analyst may be dispatched before that audit and the owner's approval.**

### 2. Re-run the private-content check where the portfolio exists

`tools/check_no_private_content.py` ran **path-only** for this entire session — `_private/portfolio/`
is not present in the worktree, so **0 identifiers were actually checked**:

```text
note: _private/portfolio/ not found — content check skipped (path check still ran)
check_no_private_content: OK (532 tracked files, 0 identifiers checked)
```

The `phase-wb-10` precedent symlinked `_private` into the worktree to get real coverage. This
session had no direction to touch `_private/` and did not.

### 3. Remove the worktree

`/code/d-system-worktrees/demo-cut-pack-factory`, once the branch is merged. It holds 1.7MB of
gitignored corpora at `_working/idea-corpus/` that no merge carries, but they regenerate exactly:

```bash
uv run python tools/build_idea_corpus.py --seed 20260912
```

Nothing needs backing up first.

## Resolved — recorded so nobody reopens them

**Integration.** Owner ruled 2026-09-12: merge everything, not just the demo commit. The split
option was offered and declined once `dev` was clean.

**The `AGENTS.md` push self-contradiction — fixed by someone else.** The *Concurrent agents* section
said "ask the owner before pushing" while citing the *Confidentiality and publishing* section that
says the opposite. A parallel Codex session corrected it; `AGENTS.md` line 192 now reads "branch
needs no approval; **ask before integrating into `dev`**", consistent with line 55. This session
reported it and never edited either file.

**Item 2.4 — the worktree rule, now applied.** `e6b32a3` and `33f931a` installed the
worktree-everywhere rule after the pack was written, and the pack told the build session nothing
about a worktree — `PROMPT-033` had no occurrence of the word, and the pack's stated ground ("no
agent in this build writes a repository file") was false at one point, since the integrator writes
the staging document into `docs/00-working/`.

Owner ruling: **read `PROMPT-025`'s "must not carry worktree setup" narrowly** — it scopes to the
dispatches, not the session — and amend no ratified decision. Applied:

- `PROMPT-032`'s scoping paragraph now says "no **per-dispatch** worktree setup" and states why the
  analysts and adversary need none (subagents, gitignored output) while the session does.
- `PROMPT-032`'s `K` gains step 1: create and enter the worktree, never switch the primary
  checkout's branch. Remaining steps renumbered.
- `PROMPT-033`'s kick-off paragraph carries the same instruction.

**Open ideas stay out of the corpus.** Owner ruling: work with the fixed set. The corpus is the 129
triaged ideas; the open ones are resolved in a future iteration.

## An unguarded race worth knowing about

**Two different ideas were both allocated `000153`.** This session's handoff idea (12:16:28) and a
peer's *"The session hand-off protocol is now described in three places and drifts between them"*
(14:47:02). `tools/append_idea.py` allocates by reading the log, and the peer's session read a log
that did not contain this one, because it sat on an unintegrated branch.

This is exactly the duplicate-code race `AGENTS.md` describes for document codes — *"codes are free
before merge and permanent after"* — happening to idea ids, where **nothing guards it**. Document
codes at least fail loudly on a duplicate; the idea log does not, and the collision surfaced only
as a rebase conflict. Resolved per the same rule: the agent integrating second renumbers, so this
session's idea was dropped and re-appended through the writer for a fresh id, `000157`. The race
itself is recorded as `000158`.

## Already done — do not redo

- **No claim held.** No phase was claimed this session; none reached `complete`.
- **The session record is committed**, and an independent sub-agent review of the diff passed 21
  conditions against its own command runs. It could not verify one (the historical PTY measurement)
  and re-tested it three times instead. It found two faults in the record; both were fixed.
- **Two phases created**, `phase-wb-11` and `phase-wb-12`, both `queued`, both in `next_up` behind
  `phase-wb-07`.

### The incident worth knowing about

This session created a branch inside the **shared** primary checkout while a peer was live in it.
Two of the peer's commits landed on the wrong branch; both were restored to `dev` by fast-forward
and nothing was lost. The sharper lesson was that during the same window *both* sessions drew false
conclusions from the transient shared tree — this one nearly recorded a real ordering failure as an
intermittent test. `e6b32a3` withdrew the documentation-only primary-checkout exception in response,
and `GOV-003` records the incidents.
