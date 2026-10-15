---
schema_version: 1
id: doc-bootstrap-follow-ons
code: PLAN-001
title: Follow-on work after the day-one scaffold
kind: plan
status: approved
owner: repository-owner
created: '2026-10-14'
updated: '2026-10-14'
systems: [sys-pipeline, sys-agents, sys-control-tools, sys-governance-docs]
depends_on: []
---

# Follow-on work after the day-one scaffold

## Context and scope

This repository started from a deliberately small scaffold so the team could begin on the first
day: the vendored plugin adapted for a control and a product repository, author-scoped idea ids,
the workstream registry with its claim, release and overlap check, the review gate, the planner
and review agents, the AWS agents, and the confidentiality check. Everything the first day did not
need was cut and is listed here as queued phases, so the team works through it with the same
pipeline as the product.

## Decisions

- **Day one is the smallest version that lets five developers start.** The alternative, building
  every piece first, would have delayed the first product commit by several sessions. Decided by
  the owner.
- **Each item below is one phase,** sized to one session, queued in the order the team is likely to
  feel the gap. The owner ranks the queue with `next_up`.
- **The standing-rules extraction and the anti-pattern procedures are sessions with the owner,**
  who reviews and approves each rule or procedure before it enters the repository. Decided by the
  owner.

## Work and dependencies

1. Author-scoped document and session codes, and author-scoped phase ids.
2. A generated workstream board with a staleness check.
3. The mechanical review runner, test baseline, diff-pattern check and CI gate, once the product's
   stack is chosen.
4. Stale-claim evidence and system path checks read from the product repository.
5. Workstream transfer, and the full two-layer protocol written for teammates.
6. The multi-session, coordinator and Session Manager documents rewritten for two repositories,
   with the shadow review judge.
7. Triage and partition that also search the product repository.
8. Git hooks and a pointer `CLAUDE.md` in the product repository.
9. Planning standards generalized: plan quality, promoted-plan staging, the planning reference, the
   planning protocol and single-session orchestration.
10. The standing rules, extracted with the owner.
11. The anti-pattern procedures, approved one by one by the owner.
12. A browser validator agent, once the user interface is designed.
13. The instance and history scanners run over the whole repository, skipping lockfiles.
14. The `checkpoint` skill written for two repositories.
15. A glossary generated from the brain's concept entries.
16. Triage, planning and review agents that search the brain as well as the documents.
17. Search over the brain beyond text matching, once the entries outgrow it.

No step depends on another, except that step 3 waits for the product's stack and step 12 for the
user interface design.

## Acceptance and verification

Each phase in the backlog carries its own acceptance and verification. This plan is done when every
phase below is complete or cancelled by the owner.

## Out of scope

The product itself. Its requirements, plans and phases are written in this repository as the team
designs it, and are not part of this plan.

## Open questions

None outstanding.
