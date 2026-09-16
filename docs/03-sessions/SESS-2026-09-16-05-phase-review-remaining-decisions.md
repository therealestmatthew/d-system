---
schema_version: 1
id: doc-session-phase-review-remaining-decisions
code: SESS-2026-09-16-05
title: The queued phase review's remaining decisions ruled and applied
kind: session
status: active
owner: repository-owner
created: '2026-09-16'
updated: '2026-09-16'
systems: [sys-realization, sys-backlog, sys-governance]
depends_on: [doc-session-queued-phase-review-run, doc-prompt-queued-phase-review-pack, doc-idea-graph-lifecycle, doc-idea-realization-system-plan]
---

# The queued phase review's remaining decisions ruled and applied

The continuation of `SESS-2026-09-16-04`. That session ruled on 31 of the review's decisions and
left the rest filed. This one put **every remaining decision** to the owner and applied the results —
22 further rulings, R32 through R53.

Evidence is in `_working/phase-review/` in the primary checkout: `remaining.md` holds the
cross-reference that produced these questions, `rulings.md` the full ruling text and the authority
for each.

## Two corrections to the previous session's reporting

Both were errors in how the last session reported to the owner, and both were found by
cross-referencing the rulings against the merged repository state rather than trusting the rulings
document.

- **The remaining-decisions count was wrong.** `SESS-2026-09-16-04` reported "15 of 46 ranked
  decisions remain unruled". The verified figure was **23 live** after merging two duplicate pairs
  (#38 with #44, #5 with #26). The 15 was an unverified estimate.
- **`phase-idg-08`'s tracking reference was false.** The previous session recorded, in `R18` and in
  its report, that `phase-idg-08` "sits behind idea `000253`'s review". Idea `000253` covers
  `phase-auto-03`/`phase-auto-04`'s `sys-api` collision. **No idea mentioned `phase-idg-08` at
  all** — it had neither a fix nor a tracking record. `R48` closes it directly.

## A regression the cross-reference caught

`R18` moved `phase-idg-10` and `phase-idg-11` onto the new `sys-gov-docs` id and was reported as a
clean fix. It was not: the two now collide with **each other** on that id, so `PLAN-029`'s "widest
genuinely parallel front" claim remained false, for a narrower reason than originally diagnosed.

Ruling `R49` corrected the plan rather than splitting the id further. Applying it turned up more than
the diagnosis had: running `collisions()` directly rather than reasoning from the summary showed
`phase-idg-06` also collides with `phase-idg-08` on `.claude/commands/`, and `phase-idg-01` with
`phase-idg-11` on `docs/04-decisions/`. **The only mutually disjoint trio is `phase-idg-01`,
`phase-idg-06`, `phase-idg-10`.** The plan now states that precisely.

## An impossible option, offered and caught

`R36` raised `phase-irs-12`'s `session_budget` to 2. That option should never have been offered:
`schemas/backlog.schema.json:138-141` enforces `session_budget` as `const: 1`, and all 277 phases
carried it — the one-session budget is a design invariant, not a default.

The applying agent tried it, governance rejected it
(`backlog:items.272.session_budget: 1 was expected`), and it **reverted and reported rather than
editing the schema to make its instruction succeed.** That is the behaviour that turned a bad
instruction into a surfaced error instead of a silent repository-wide change.

`R52` supersedes `R36`: `phase-irs-12` was split, the same remedy `R5` applied to `phase-irs-04`.

## What changed

- **`phase-irs-17`** created — "Forced-failure drill across the assembled pipeline", carrying
  `REQ-022` R12. `phase-irs-12` keeps R24 and becomes "End-to-end trace and metrics baselines".
  Both halves keep the full stage dependency set, since each independently exercises every stage —
  one to trace it, one to break it — and `phase-irs-17` additionally depends on `phase-irs-12`,
  whose traced run its own verification text presumes.
- **`phase-irs-08`** gains the unit-run hand-off duties from `PLAN-039.01` §6 that no phase owned.
- **`phase-agx-03`** grows deliberately: it writes up the three starter-catalog anti-patterns that
  existed only as prose in idea `000138`, indexes all four `log-anti-patterns` capture destinations
  rather than `brain/procedures/` alone, and names which procedure files qualify.
- **`phase-irs-01`**'s stopgap tool checks the `_working/orchestrator-halt` flag before dispatching,
  making "halts all pipeline dispatch" literally true from day one rather than once the daemon lands.
- **`phase-idg-10`** broadens to cover requirement documents as well as plans, layers beside
  `templates/governance/document.md` rather than superseding it, and states that its two prose
  acceptance bullets are judged at session close.
- **`phase-idg-08`** moved to `sys-gov-docs` with `GOV-012` reserved and its bare directory
  deliverable narrowed.
- **`src/db/ideas.py`** registered under `sys-portfolio` — a registry gap predating this review.
- `phase-irs-06` defers the adversary-to-trio seam; `phase-irs-05` states its review hand-off is
  status-marking only; `phase-idg-11` builds on `GOV-005` reservations; `phase-part-03` stamps the
  corpus build date and refuses or suffixes a same-day rerun; `phase-irs-15` adds `sys-portfolio`.

## Deliberate no-changes

Recorded so they are not re-opened as oversights: `phase-irs-11` adds nothing to docs (`R45`);
`phase-auto-02` keeps `session_budget: 1` pending `phase-auto-01`'s shape ruling (`R50`);
`phase-irs-03` keeps a reviewer read rather than a brittle prose grep, and `phase-auto-01` stays
ADR-only (`R51`).

## Deferred with a record

`R53`: no registered `sys-wb-*` id covers `phase-irs-13`'s gate-queue surface, because the surface
does not exist yet and the phase's own scope says its host "is not a settled one". Rather than
invent an id, the requirement to add one is recorded in the phase's `next_action`, so the
collision-detection gap is tracked rather than forgotten.

## Verification

- `Governance OK: 31 systems, 259 documents, 25 memories, 278 backlog phases`
- `580 passed, 2 warnings`
- `check_no_private_content: OK (666 tracked files, 0 identifiers checked)`, staged
- `next_up` is 30 entries with **zero ordering violations**
- **No phase carries a `session_budget` other than 1** — the invariant holds
- `PLAN-039`'s phase table matches the backlog's `depends_on` on every row

## State

All 46 ranked decisions from the review are now ruled. Nothing from
`docs/00-working/phase-review-decisions.md` remains outstanding.
