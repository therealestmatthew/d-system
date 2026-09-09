---
name: checkpoint
description: Record real progress on the active phase into its session record — verification output, backlog status, evidence, next_up — without ever claiming a phase is complete. The owner or an agent may invoke it any number of times in a session; a run against unchanged state produces no diff.
---

# checkpoint

Records what has actually happened, leaves the tree honest, and stops. It never decides a session
is over — that judgement, and the `status: complete` transition, belong only to `session-close`
(`phase-ses-05`). Checkpointing mid-work is the ordinary case this skill is built for, not a
fallback; most invocations will find acceptance unmet and record that plainly.

Read `AGENTS.md` first if you have not already this session — this skill assumes its concurrency and
governance rules and does not repeat them.

## What this skill must never do

- **Never set a phase's `status` to `complete`.** Only `session-close` does that, and only after its
  own sub-agent review. This skill only ever leaves a phase `queued` or `active`.
- **Never run `git worktree`, `git rebase`, or anything touching a remote.** This skill edits files
  in whatever working tree it is invoked from and nothing else. It gives identical instructions
  whether that tree is the primary checkout or an agent's worktree — see
  [GOV-003](../../../docs/08-governance/GOV-003-backlog-decisions.md) for when each is required.
  Integration, rebasing and hand-off remain the separate procedure in `AGENTS.md`.
- **Never touch a backlog line, session record, or `next_up` entry that belongs to a phase you are
  not currently working.** A peer's claim is a peer's claim.

## The session record contract

Both this skill and `session-close` read and write **one file** per session: a `kind: session`
document under `docs/03-sessions/`. This is the authoritative definition of its shape — `session-close`
extends it but does not redefine it.

### Front matter

```yaml
schema_version: 1
id: doc-session-<slug>          # permanent, independent of the code
code: SESS-YYYY-MM-DD-NN         # from --next-code session; date must equal `created`
title: <human title for this session>
kind: session
status: active                   # the only status the schema allows for kind: session
owner: repository-owner
created: 'YYYY-MM-DD'
updated: 'YYYY-MM-DD'
systems: [...]                   # systems this session actually touched
depends_on: [...]                # the plan(s) this session advances, e.g. doc-session-lifecycle
```

### Body sections, in this fixed order

Each checkpoint run **regenerates sections 2 through 6 from scratch**, from the state actually
observed at run time. It does not append a new block per run and does not keep a log of past runs —
that is what makes a no-op run produce a no-op diff, and what keeps the file readable after the
tenth checkpoint instead of the first.

1. `# <title>` — matches the front matter title.
2. `## Phase` — one line per phase this record covers: the id and title, e.g.
   `` `phase-ses-03` — Build the checkpoint skill. `` A record normally covers one phase; note here if
   it genuinely covers more (e.g. a phase whose acceptance requires an adjacent tidy-up).
3. `## Verification` — for each entry in the phase's `verification` list that is a runnable command,
   the literal command and the literal output actually produced just now. For a verification entry
   written in prose rather than as a command (a behavioural check), one line stating what was
   actually done and observed. Never paraphrase a failure into a pass.
4. `## Acceptance` — one line per entry in the phase's `acceptance` list: `Met` or `Not met`, with a
   short reason that points back to the evidence in `## Verification` above rather than restating the
   condition.
5. `## Backlog` — the phase's `status`, `next_action`, and (once genuinely true) evidence, exactly as
   written to `backlog.yaml` this run.
6. `## Unresolved` — anything real left open. Write `None.` when that is honestly true; do not pad
   this section to look thorough.

`session-close` appends further sections after these (decisions, the sub-agent review, the full
narrative) when it finalizes the file. It never replaces sections 2-6 with different facts — only
this skill's own next run does that, as the state moves forward.

## Running it

### 1. Identify the phase

Find the phase you are checkpointing: the one entry in `docs/09-backlog/backlog.yaml` with
`status: active` and `agent:` set to whoever is running this session. If invoked by the owner
directly with no agent context, or if more than one phase looks plausible, ask which phase this
checkpoint concerns rather than guessing — a checkpoint written against the wrong phase is worse
than one you took a moment to confirm.

If no phase is active for this session, say so and stop. There is nothing to record.

### 2. Find or create the session record

Search `docs/03-sessions/` for an existing record whose `## Phase` section already names this phase
id and whose `code` carries today's date. If one exists, that is the record to update — open it and
edit it in place. Never create a second record for the same phase on the same day; that is exactly
the duplication this contract exists to prevent.

If none exists, allocate a code and create it:

```bash
uv run python -m src.governance --next-code session
```

Name the file `<code>-<topic>.md` under `docs/03-sessions/`. The code's date must equal `created`.

### 3. Run verification and record actual output

Run every command in the phase's `verification` list, in the working tree you are actually in (no
assumption about primary checkout vs. worktree — just run them where you stand). Capture the real
output, including a real failure. Write it into `## Verification`, replacing whatever was there
before.

**Strip run-specific noise that carries no information for the acceptance decision** — wall-clock
timings, temp paths, PIDs — before writing it down. `290 passed, 2 warnings in 1.97s` becomes
`290 passed, 2 warnings`. This is not rounding a result to look better; a rerun against genuinely
unchanged state must produce byte-identical text, and a timer is the one part of most command output
that changes even when nothing else does. A real change in the numbers that matter — pass/fail
counts, error messages, exit codes — is never stripped.

### 4. Check acceptance against what you just observed

Go through the phase's `acceptance` list one condition at a time. For each, decide `Met` or
`Not met` using only what `## Verification` actually shows plus a direct look at the deliverables —
never mark something met because the scope says it should be by now. Write the result into
`## Acceptance`, replacing whatever was there before.

**Finding conditions unmet is the expected outcome of most checkpoints.** Write it down plainly and
move on; this is not a problem to solve before finishing the record.

### 5. Update the backlog entry — status stays `queued` or `active`

Edit only this phase's lines in `docs/09-backlog/backlog.yaml`:

- Keep `status` at `active` (or return it to `queued` if you are handing the phase off unfinished
  with nobody continuing it right now). **Never write `status: complete` here** — that is
  `session-close`'s alone to do, after its own review.
- Update `next_action` to describe, precisely, what remains — grounded in the `Not met` reasons from
  step 4. If everything is genuinely met, say so in `next_action` and leave `status: active`;
  `session-close` is what turns that into `complete`.
- While the phase stays `active` or `blocked`, `session`, `completion_evidence` and `result` may all
  be recorded incrementally — not only at close — so a long or complex session can checkpoint real
  interim evidence rather than manufacturing it retroactively at the end
  (`src/governance/backlog.py`'s `CLAIMED_STATES` gate, not just `complete`, permits this). Write
  real evidence only: files that exist right now and actually demonstrate what they are cited for,
  and a `result` that describes actual progress, not a completion claim.
- If you return the phase to `queued`, clear `session`, `completion_evidence` and `result` in the
  same edit — a released claim carries none of the three, and the governance check rejects them on a
  `queued` phase. The session record itself is untouched and still carries the same facts.
- Leave every other phase's lines untouched.

Mirror the same facts into the record's `## Backlog` section.

### 6. Prune `next_up`

Remove any phase id from `next_up` that is now genuinely `status: complete` (never one you just left
active, however close). Leave every other entry alone.

### 7. Regenerate the catalog

```bash
uv run python -m src.governance --catalog > docs/08-governance/catalog.md
```

### 8. Confirm governance is green

```bash
uv run python -m src.governance
```

If this fails, fix the cause before finishing the checkpoint — do not hand back a red tree with a
session record describing it as fine. A failing check is itself something to record in
`## Verification`, not a step to retry silently until it passes.

### 9. Report

Say what changed, in plain terms: the session record's code, whether backlog fields changed, whether
`next_up` was pruned, and the actual acceptance verdicts from step 4. Do not claim more than steps
1-8 actually produced.

## Why a repeat run is a no-op

Nothing here is appended, timestamped per-run, or written from memory of a previous run. Every
section is recomputed from the phase's declared `verification`/`acceptance` lists against the state
that exists right now. If nothing in the repository changed since the last checkpoint, every
recomputed value is identical to what is already on disk, so steps 2-8 touch nothing and `git diff`
after the run is empty. This is what makes checkpointing cheap enough to run on impulse rather than
something to ration.
