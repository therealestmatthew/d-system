---
schema_version: 1
id: doc-session-checkpoint-skill
code: SESS-2026-09-07-01
title: Build the checkpoint skill
kind: session
status: active
owner: repository-owner
created: '2026-09-07'
updated: '2026-09-07'
systems: [sys-governance]
depends_on: [doc-session-lifecycle]
---

# Build the checkpoint skill

## Phase

`phase-ses-03` — Build the checkpoint skill.

## Verification

```
$ uv run python -m src.governance
Governance OK: 16 systems, 67 documents, 8 memories, 95 backlog phases
```

```
$ uv run pytest -q
290 passed, 2 warnings
```

(Wall-clock timing stripped per `SKILL.md`'s rule against run-specific noise — it varies run to run
even when nothing else does, and would otherwise break the no-diff guarantee below.)

Behavioural check — "invoke the skill twice for a real phase and confirm the second run is a no-op
diff": performed against this very phase. The first checkpoint run created this record and updated
`phase-ses-03`'s `next_action` in `backlog.yaml`. A second checkpoint run, with no other work done in
between, recomputed every section from the same observed state and produced `git diff --stat`
showing nothing for this file or for `backlog.yaml`.

## Acceptance

- The skill is executable end to end without a remote or a worktree. **Met** — `SKILL.md` issues no
  `git worktree`, `git rebase` or remote command anywhere in its procedure; every step is a file edit
  or one of the two governance/test commands above, run wherever the invoking session already is.
- Running it twice with no work between produces no diff, so a checkpoint is cheap to repeat. **Met**
  — demonstrated directly above: the second run's `git diff --stat` was empty.
- A phase with unmet acceptance is left queued or active with a `next_action`, never marked
  complete. **Met by construction** — step 5 of `SKILL.md` states the skill must never write
  `status: complete`, only `queued` or `active`.
- A second run updates the existing session record rather than creating a second one. **Met** — the
  second dogfood run edited this same file (`SESS-2026-09-07-01-checkpoint-skill.md`); no second
  `SESS-2026-09-07-*` file was allocated or created.
- Following it leaves the governance check green and the catalog current. **Met** — see the
  governance output above; `docs/08-governance/catalog.md` was regenerated in the same run and
  `uv run python -m src.governance --catalog | diff docs/08-governance/catalog.md -` reports no
  difference.
- `CLAUDE.md` and `AGENTS.md` both reference the skill, so an agent can know to invoke it
  unprompted. **Met** — `AGENTS.md`'s Session backlog section and `CLAUDE.md`'s Directory Reference
  table both point at `.claude/skills/checkpoint/SKILL.md`.
- No governed document still forbids the primary checkout unconditionally. **Met** — the blanket
  prohibition in `AGENTS.md`, `GOV-001` and `GOV-002` was replaced with the conditional rule GOV-003
  already recorded; `grep -rn "primary checkout"` across governed documents shows no remaining
  unconditional statement.

All seven conditions are met. Per `SKILL.md`'s own rule, this checkpoint still leaves the phase
`active` rather than writing `complete` itself — that transition is `session-close`'s alone
(`phase-ses-05`), and it does not exist yet. Completion below is done through the standard
`AGENTS.md` "complete and hand off" procedure directly, the same procedure `session-close` will
eventually formalize, since no owner-only command exists yet to reach it through.

## Backlog

Final state, after the hand-off below: `phase-ses-03` is `status: complete`, `agent:
agent-checkpoint`, `session: doc-session-checkpoint-skill`, with `completion_evidence` naming this
record, `.claude/skills/checkpoint/SKILL.md`, and the corrected `AGENTS.md`/`GOV-001`/`GOV-002`
sections. Removed from `next_up`.

## Completion (standard hand-off, not the skill)

The checkpoint dogfood above left the phase `active` by design, per `SKILL.md`'s own rule that it
never writes `status: complete`. `session-close` (`phase-ses-05`) is the command meant to perform
that transition, but it does not exist yet — it is the next phase in this same plan, and depends on
this one. So this phase's actual completion follows the standard `AGENTS.md` "complete and hand off"
procedure directly, the same manual path every phase used before either the skill or the command
existed.

All seven acceptance conditions were independently re-confirmed true at the moment of completion
(no repository state changed between the second dogfood run and this hand-off), so the transition
to `status: complete` is genuine, not assumed from the earlier checkpoint.

## Unresolved

None for this phase's own scope. `phase-ses-05` (the session-close command) depends on this phase and
is claimed next, now that this one is complete.

## Independent audit (requested separately by the owner)

Because this phase closed through the standard hand-off rather than `session-close`'s own sub-agent
review (which did not exist yet), the owner separately asked for a fresh, non-fork sub-agent audit
after the fact, alongside the same for `phase-ses-05`. It cross-checked all seven acceptance
conditions against the actual diff and git history — not this record's prose — and re-ran
`uv run python -m src.governance` / `uv run pytest` itself. Verdict: all seven hold. One real,
cosmetic gap found: `GOV-003-backlog-decisions.md` was touched by commit “Replace the blanket primary-checkout prohibition with GOV-003's conditions” (adding the
"Resolved 2026-09-07" note) but was missing from this phase's `deliverables`/`completion_evidence`.
Fixed directly in `backlog.yaml`. No other finding.
