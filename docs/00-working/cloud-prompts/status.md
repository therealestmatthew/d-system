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
| 2 | [Plan anatomy investigation](plan-anatomy.md) | 000505 | `agent/cloud-plan-anatomy` | merged | 9772c21 | [handoff-plan-anatomy.md](handoff-plan-anatomy.md) | Inventory, findings and proposed plan-folder standard; two partition-adversary passes, 7 findings fixed; gates green |
| 3 | [Boundary validation](boundary-validation.md) | — | `agent/cloud-boundary-validation` | merged | 238b6a0 | [handoff-boundary-validation.md](handoff-boundary-validation.md) | One figure error corrected in ARCH-012; A still favoured, C's rejection stronger; plugin weighed for B; 9 review findings dispositioned (1 escalated); phase-bnd-06 to -14 deferred; gates green |
| 4 | [Boundary follow-up for option A](boundary-option-a.md) | — | `agent/cloud-boundary-option-a` | not started | | | Owner chose A on 2026-09-28; applies the seven F01 wording changes and releases, defers or cancels phase-bnd-06 to -14 |
