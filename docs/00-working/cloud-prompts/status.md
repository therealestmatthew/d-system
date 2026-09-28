# Cloud prompt status

The tracker for the cloud-session prompts in this folder. Cloud sessions run by
[`master-prompt.md`](master-prompt.md) own this file: each session updates its own row on its own
branch, and the row reaches `dev` with that branch's merge.

**Sessions run one at a time, in the order below.** A row may start only when every row above it
is `merged`: that branch must be on `origin/dev` before the next session begins, so each session
starts from the previous one's merged work.

Status values: `not started` · `in progress` (branch pushed, work under way) · `ready` (handoff
file committed; waiting for the local Session Manager and the owner's merge) · `merged` (the
branch is on `origin/dev`) · `stopped` (the session ended without a handoff file; see Notes).

| Order | Prompt | Idea | Branch | Status | Tip | Handoff | Notes |
|---|---|---|---|---|---|---|---|
| 1 | [Planning protocol document](planning-protocol.md) | 000500 | `agent/cloud-planning-protocol` | merged | 280584c | [handoff-planning-protocol.md](handoff-planning-protocol.md) | GOV-021 drafted; partition-adversary review run, 5 findings fixed; gates green |
| 2 | [Plan anatomy investigation](plan-anatomy.md) | 000505 | `agent/cloud-plan-anatomy` | in progress | | | |
| 3 | [Boundary validation](boundary-validation.md) | — | `agent/cloud-boundary-validation` | not started | | | |

A fourth prompt, the boundary follow-up, is added here only after the owner's A/B/C decision.
