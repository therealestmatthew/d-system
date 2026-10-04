# Post calendar

The ordered post queue. Posts are published in this order at five a week; dates are set by the owner
when a post is `approved`, not here. Status values are defined in [README.md](README.md). Rows past
the drafted ones are `planned`: a topic and its sources, no text yet. The queue follows the arc in
[arc.md](arc.md); post 003 is a lesson pulled forward from stage 5 so that the first week includes an
incident.

Image column: **D** generated or hand-drawn diagram, **B** AI image brief, **S** screenshot or
shared file, **A** animation (later stage), **—** text only.

| # | Topic | Stage | Pillar | Image | Status | Main sources |
|---|---|---|---|---|---|---|
| 001 | [What I'm building](posts/001-what-im-building/post.md) | 1 | Mechanism | B | draft | `README.md`, `ARCH-006` |
| 002 | [The idea log can never be edited](posts/002-the-idea-log/post.md) | 2 | Mechanism | D | draft | `tools/append_idea.py`, `src/db/ideas.py` |
| 003 | [One worktree per agent session, even for a docs edit](posts/003-one-worktree-per-session/post.md) | 5 | Incident | — | draft | `GOV-003` 2026-09-12 ruling |
| 004 | The confidential data went before the first push: structure and content separated | 1 | Mechanism | D | planned | `ADR-009`, `GOV-003` "History is squashed, not filtered" |
| 005 | Why I direct agents instead of writing the code | 1 | Reflection | — | planned | `README.md` |
| 006 | Raw capture is stored before anything interprets it | 2 | Mechanism | — | planned | `ADR-007` |
| 007 | Heavy schemas made agents write documents that existed only to satisfy the schema | 2 | Incident | — | planned | `ADR-010` |
| 008 | 564 ideas in a month: what the log shows | 2 | Numbers | D | planned | `fold()` at the drafting commit |
| 009 | The idea writer's docstring | 2 | Artifact | S | planned | `tools/append_idea.py` |
| 010 | One triage agent per idea | 3 | Mechanism | — | planned | `.claude/agents/idea-triage.md`, `ARCH-006` stage 2 |
| 011 | Grouping hundreds of ideas: an analyst, an adversary and a control run | 3 | Mechanism | D | planned | `PLAN-025`, `REQ-009`, `docs/00-working/idea-partition-2026-09-23.md` |
| 012 | 371 ideas, 87 groups, 12 tracks | 3 | Numbers | D | planned | `docs/00-working/idea-partition-2026-09-23.md` |
| 013 | The adversary prompt | 3 | Artifact | S | planned | `.claude/agents/partition-adversary.md` |
| 014 | Deciding at a gate instead of in every conversation | 3 | Reflection | — | planned | `ARCH-006` "The gate model" |
| 015 | Nine stages, five gates, a failure path for each stage | 4 | Mechanism | D | planned | `ARCH-006` |
| 016 | A stage with no failure path is a defect | 4 | Incident | — | planned | `ARCH-006` stage table note |
| 017 | 100 review findings, 18 blockers | 4 | Numbers | D | planned | `docs/08-governance/reviews/*.json` |
| 018 | A plan review record | 4 | Artifact | S | planned | one file in `docs/08-governance/reviews/` |
| 019 | What adversarial review changed in my plans | 4 | Reflection | — | planned | `GOV-018`, `docs/08-governance/reviews/` |
| 020 | The backlog is a lock table | 5 | Mechanism | D | planned | `docs/09-backlog/backlog.yaml`, `ADR-003` |
| 021 | The same idea id, twice, and a collision git never reported | 5 | Incident | A | planned | `GOV-003` "Concurrency collisions" |
| 022 | 46 of 74 ready phases blocked by one claim | 5 | Numbers | D | planned | `GOV-017` |
| 023 | Session roles and the message protocol | 5 | Artifact | S | planned | `GOV-017` |
| 024 | Running several agent sessions at once | 5 | Reflection | — | planned | `GOV-017` |
| 025 | What runs on every commit | 6 | Mechanism | D | planned | `tools/git-hooks/pre-commit`, `src/governance/` |
| 026 | Four phases silently reverted while every check passed | 6 | Incident | — | planned | `src/governance/regression.py` |
| 027 | A check that cannot fail is not a check | 6 | Artifact | S | planned | `brain/procedures/a-check-that-cannot-fail-is-not-a-check.md` |
| 028 | A pipe that hid a failed merge | 6 | Incident | A | planned | `brain/procedures/a-pipe-discards-the-exit-code-you-were-guarding-on.md` |
| 029 | Corrections written for the next model, not this one | 6 | Reflection | — | planned | `CLAUDE.md` "When you get something wrong", `brain/procedures/` |
| 030 | Pages the system generates about itself | 7 | Mechanism | S | planned | `tools/generate_engine_pages.py`, `_public/engine/` |
| 031 | Every number on a page names its source | 7 | Mechanism | S | planned | `tools/generate_engine_pages.py` docstring |
| 032 | A page that rendered nothing passed every check | 7 | Incident | — | planned | `brain/procedures/runtime-behavior-needs-runtime-evidence.md` |
| 033 | The idea funnel page | 7 | Artifact | S | planned | `_public/engine/ideas.html` |
| 034 | Reading the system's own record | 7 | Reflection | — | planned | `_public/engine/` |
| 035 | The IRE: the pipeline as a Claude Code plugin | 8 | Mechanism | D | planned | `plugins/idea-realization/README.md` |
| 036 | Shipping the mechanism without the history | 8 | Mechanism | — | planned | `test/test_no_source_references.py` |
| 037 | The portable working agreement | 8 | Artifact | S | planned | `plugins/idea-realization/templates/` |
| 038 | Installing the IRE into an empty repository | 8 | Mechanism | A | planned | `plugins/idea-realization/README.md` |
| 039 | What is not built yet | 8 | Reflection | — | planned | `PLAN-039`, `ADR-018` |
| 040 | Release | 8 | — | — | planned | set by the owner |

Every number in a planned row is recomputed when the post is drafted.
