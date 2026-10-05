---
schema_version: 1
id: doc-session-threat-surfaces-security-review
code: SESS-2026-10-05-07
title: 'Threat surfaces in plans, the READY security review, and GOV-003 entries for O-5, O-6 and Q7'
kind: session
status: active
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-gov-docs]
depends_on: [doc-reviewer-contract]
---

# Threat surfaces in plans, the READY security review, and GOV-003 entries for O-5, O-6 and Q7

## Phase

`phase-asr-05` — Second docs phase: threat surfaces in plans, the READY security review, and
GOV-003 entries for O-5, O-6 and Q7. Claimed by agent-standby-3 (Session 3 - Standby Builder) on
the Session Manager's overnight ASSIGN; claim commit `15c60f1` on `dev`.

## Verification

All run in the worktree on `agent/phase-asr-05` at `b944a23`, on `dev` `91bfdf4`.

`uv run python -m src.governance --catalog`: exit 0.

`uv run python -m src.governance`:

```
Governance OK: 45 systems, 443 documents, 37 memories, 347 backlog phases
```

`git diff --exit-code docs/08-governance/catalog.md`: exit 0.

## Acceptance

- GOV-010 has the threat-surface requirement and says how its absence is judged — **Met.** P12
  names the four surfaces and what the plan says for each. Its "How a reviewer judges it" paragraph
  states that silence fails, and that citing a decision without the surface it governs fails.
- GOV-017's READY names `/security-review`, its trigger, and that the coordinator runs it and records
  the verdict — **Met.** "Build reviews" has "The security review" with its trigger, who runs it and
  the record, and merge-gate step 1 has `READY` name the `/security-review` verdict record.
- GOV-010 gives, as a non-conformant example, a plan whose phase edits
  `src/api/routes/demo_terminal.py` without naming a network or authentication surface — **Met.**
  P12's "Does not" paragraph.
- GOV-003 has the three entries — **Met.** O-5, O-6 and Q7, each dated 2026-09-23, quoted from the
  Session Manager's board as `PLAN-047` and `REQ-030` cite them, and marked standing.

## Backlog

`status: active`, `agent: agent-standby-3`, `session: doc-session-threat-surfaces-security-review`.
`next_action`: "Built and reviewed on agent/phase-asr-05 (SESS-2026-10-05-07); waits for the
owner-approved merge and the completion edit on dev." `completion_evidence` and `result` are written
in the completion edit on `dev`, after the merge.

## Unresolved

- Idea `000589`: the verdict schema has no form for a built-in reviewer. Until it does, GOV-017 has
  the coordinator record the sha256 of `claude --version` in `definition_sha256` and say so in
  `notes`.

## Review

This phase was reviewed under the procedure `phase-asr-04` wrote. The Session Manager, as
coordinator, ran the review runner (all entries exit 0). It dispatched `demo-adversary` as the
gating reviewer and `review-judge` in shadow, and returned the verdict records, which are committed
unchanged under `docs/08-governance/reviews/verdicts/`. `/security-review` was not run. The diff
touches only governance documents and verdict records, none of the trigger's paths, and the trigger
rule itself existed only on this branch.

| Round | Commit | Gating `demo-adversary` | Shadow `review-judge` |
|---|---|---|---|
| 1 | `e45c1cf` | `2026-10-05-phase-asr-05-demo-adversary.json`: **reject**, F01 blocker, F02 major, F03 minor | `2026-10-05-phase-asr-05-review-judge.json`: pass, no findings |
| 2 | `8967335` | `2026-10-05-phase-asr-05-demo-adversary-2.json`: **pass**, no findings | `2026-10-05-phase-asr-05-review-judge-2.json`: pass, F01 minor |

The gating findings, as the reviewer titled them:

- **F01 (blocker):** "GOV-017's merge gate step 3 still names only the gating reviewer's and shadow
  judge's verdicts and says 'Only the gating verdict decides', while this phase records the security
  review as a second verdict with gating: true." Fixed: step 3 lists the `/security-review` verdict
  when triggered, and both gating verdicts must pass.
- **F02 (major):** "The security-review trigger's first condition is worded at plan granularity
  ('the phase's plan names a threat surface'), diverging from REQ-030 R08's phase-level wording."
  Fixed: the trigger reads "the phase's plan maps this phase to a threat surface", and `GOV-010` P12
  is phase-level to match.
- **F03 (minor):** "Recording /security-review's definition_sha256 as the sha256 of `claude
  --version` output is a flagged stopgap pointing at idea 000589; schema-valid and not a defect."
  Accepted, no change.

Shadow round 2 F01 (minor): the coordinator's delta file showed idea-log hunks from a rebase, not
from this branch's change. Accepted; the branch does not touch the idea log.

## Decisions

- **The non-conformant example is described, not a named plan.** `GOV-010` applies to plans written
  after 2026-09-22. The plans whose phases edit `demo_terminal.py` (`PLAN-021`, `PLAN-022`,
  `PLAN-027`) are older. `PLAN-022` names no network or authentication surface, but it cites
  `ADR-014`, which does cover loopback binding. Calling it non-conformant would judge an exempt
  document, and the citation would make the verdict arguable. The example describes the case
  instead, and adds that a decision cited without the surface it governs fails.
- **OVERNIGHT ASSUMPTION: the security review gates.** The owner ruled that it is "recorded as a
  verdict" without saying whether it decides. GOV-017 records it with `gating: true` and requires its
  findings to be fixed or accepted, which is the safer reading for a check on authentication and
  network exposure.
- **OVERNIGHT ASSUMPTION: what a built-in reviewer records as `definition_sha256`.** The sha256 of
  `claude --version`, stated in `notes`, until idea `000589` changes the schema. A schema change was
  outside this phase's declared files.
- **The trigger is a path list plus the plan's own P12 statement**, and "when unsure, run it". A
  list alone misses a credential read or a socket opened elsewhere; judgement alone is not
  checkable.
- **OVERNIGHT ASSUMPTION: claim narrowing.** `docs/08-governance/` was narrowed to GOV-010, GOV-017
  and GOV-003, inside the phase's original declaration; `phase-des-03` holds `OPS-033` and
  `codes.yaml`.

## Corrections

- Round 1 rejected the first text on two findings (F01, F02). Both were fixed and re-reviewed in
  round 2, not accepted.

## Left undone

Nothing in scope. The completion edit on `dev` follows the owner-approved merge.
