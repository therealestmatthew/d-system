---
schema_version: 1
id: doc-session-sibling-repo-migration-planning
code: SESS-2026-10-10-01
title: Sibling-repository feature migration planning — surveys, adversarial review, idea capture, PLAN-053 with its phases and review, and the runner prompt
kind: session
status: active
owner: repository-owner
created: '2026-10-10'
updated: '2026-10-10'
systems: [sys-portfolio, sys-backlog, sys-gov-docs]
depends_on: [doc-sibling-repo-feature-migration]
---

# Sibling-repository feature migration planning

## Phase

Unclaimed — owner-directed work, no backlog phase. `sibling-repo-migration-planning` — the owner
asked on 2026-10-10 for a review of the `life` and `autoclaude-api` repositories, a proposal of
features to integrate, an adversarial review of that proposal, idea capture and triage, the plan
with its phase decomposition and reviews, the starter prompt for the session that executes it,
and a pull request to `dev`. No peer holds a lock against this session.

Two deviations from `AGENTS.md`, stated rather than hidden. The session ran in the primary
checkout on the branch the cloud harness designated, `ccr-1f7a3866-smac3h`, cut from `dev` at
`2cccfff`, because the harness had already checked that branch out there and the container holds
no peer agent; no worktree was cut. Ideas were appended on that feature branch rather than on
`dev`, which `PLAN-053` open question 4 records as an id-collision risk at merge.

## What was done, in order

1. **Surveys.** Three read-only Explore agents on Sonnet, one per repository (`life`,
   `autoclaude-api`, `d-system`), each with a scoped brief and a word cap: 75,668, 211,438 and
   136,035 tokens. The proposal was written as a shared document outside the repository.
2. **Adversarial review of the proposal.** One general-purpose agent checked every claim against
   the three checkouts. Its ranked findings removed two ports (no run ledger exists; the budget
   cap contradicts the `phase-irs-11` ruling), moved the sanitiser from capture to structuring,
   corrected the "single-writer rule" claim, found three design-input targets mis-scoped, and
   found the governance path skipped `GOV-021`'s gates. `PLAN-053`'s Context table records each
   finding and its disposition.
3. **Mechanics digest.** One Explore agent on Sonnet compiled the plan-authoring mechanics
   (front matter, codes, backlog fields, idea writer, review record, session record, checks).
4. **Idea capture and triage.** One Ideation agent on Sonnet recorded sixteen ideas,
   `000673` to `000688`, each opening with `[agent-proposed by Session Manager - migration
   planning]`, wrote one `finding` annotation per idea as `agent-ideation`, moved each to
   `triaged`, and regenerated `docs/00-working/ideas.md`. No link or promotion was written.
   Commit `82c3038`.
5. **Requirement, plan, phases, prompt.** `REQ-038`, `PLAN-053`, six `phase-mig-*` entries (five
   `queued`, `phase-mig-06` `deferred`), the track row in the backlog README, and `PROMPT-045`.
   Codes from `--next-code`. Commit `666d162`.
6. **`GOV-018` review.** Entry check: exit 0. Two `partition-adversary` dispatches with
   `PROMPT-038`, plan altitude and phase altitude. Both hit the 50-turn limit and were asked to
   deliver what they had verified. Sixteen findings: two blockers (the sanitiser had no reader
   to sit in front of and a verbatim copy fails its own test; the timeline routes reversed
   `ADR-015` unnamed), five majors, nine minors. Every finding dispositioned `fixed` by the
   planner in `docs/08-governance/reviews/2026-10-10-plan-053.json`, and the requirement, plan
   and phases revised. Entry check after revision: exit 0.

## Verification

Fixed gates for an unclaimed session, run in this checkout after the revision:

```
$ uv run python -m src.governance
Governance OK: 45 systems, 480 documents, 37 memories, 363 backlog phases

$ bash <GOV-018 step 1 script> docs/01-plans/PLAN-053-sibling-repo-feature-migration.md
exit 0

$ uv run pytest -q test/test_adversarial_finding_schema.py test/test_review_gate.py test/test_codes.py \
    test/test_governance.py test/test_backlog.py test/test_plan_phases.py test/test_requirement_rule.py \
    test/test_governance_staleness.py test/test_ideas.py test/test_containment.py
FAILED test/test_containment.py::test_repository_history_reports_the_known_phase_prog_cases
1 failed, 426 passed, 1 warning in 111.57s

$ git add -A docs/ && uv run python tools/check_no_private_content.py
check_no_private_content: OK (1493 tracked files, 0 identifiers checked)

$ uv run python -m src.governance --check-ideas
Idea field check: 118 phases name 193 ideas; 0 phases differ (0 missing, 0 extra)
```

The one failure is the containment history test, which walks git history for `phase-prog-04`
and reported `not locatable: entered the backlog already complete, with no claim on this
history`. The cloud checkout was a shallow clone (`git rev-parse --is-shallow-repository` printed
`true`), so the history it needs was absent. After `git fetch --unshallow origin` the same file
passed:

```
$ uv run pytest -q test/test_containment.py
19 passed, 1 warning in 23.91s
```

Nothing in this session touches `src/governance/containment.py` or the `phase-prog-*` entries.

Idea state, read through `fold`: `000673` to `000688` are all `triaged` with one finding each.

## Acceptance

Not applicable: no phase was claimed, so no `acceptance` list applies. The owner's ask is met
item by item: surveys and proposal (step 1), adversarial review (2), ideation agent capture and
triage (4), plan and phase decomposition and reviews (5, 6), starter prompt (5), commit, push and
pull request (below).

## Backlog

No phase was claimed and no line of `backlog.yaml` was changed other than the six new
`phase-mig-*` entries and the catalog `updated` date. `next_up` is unchanged: the owner places
the phases. The owner's gates all ride on the pull request: G1 on the sixteen ideas, G2 on the
one-track partition `PLAN-053` proposes, G3 on the plan and its phases, G4 on the merge.

## Unresolved

- `PLAN-053` open questions 1 to 4: whether the owner wants the timeline entity, the overlap
  threshold, where engagement templates live, and the idea-id collision risk from appending on a
  feature branch.
- `GOV-002` and `PROMPT-037` say `max_active` is 3 while `backlog.yaml` sets 4. Found by the
  mechanics survey; not this session's to change.
- `000308` marks `000296` as superseded while `000296` is only `triaged`; a pre-existing warning
  from `tools/generate_ideas_md.py`, unrelated to this session's ideas.
