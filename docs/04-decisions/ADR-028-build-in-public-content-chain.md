---
schema_version: 1
id: doc-adr-build-in-public-content-chain
code: ADR-028
title: Build in public — the owner's answer for the X series, multi-platform presence and content automation
kind: adr
status: accepted
owner: repository-owner
created: '2026-10-05'
updated: '2026-10-05'
systems: [sys-content]
depends_on: [doc-standalone-explorations-housekeeping]
---

# Build in public — the owner's answer for the X series, multi-platform presence and content automation

## Status

Accepted. This records the owner's answer. It does not make the decision.
[`PLAN-037`](../01-plans/PLAN-037-standalone-explorations-housekeeping.md) (group `G58`) and
`phase-expl-02` exist to put the question and record the answer. The owner ruled on 2026-09-13
that the question is theirs: *"Dormancy is not deadness. Wholly isolated in `G58`; a
business-priority question, not a technical one."*

**Provenance of the answer.** The owner gave it on the evening of 2026-10-04, as a preloaded
ruling for the overnight run of 2026-10-04/05. It is recorded in the Session Manager's restart file
(`_working/session-manager/restart-2026-10-04.md`, §P, item P2) and was relayed to the session
that wrote this record. That session did not hear it from the owner directly. The owner's own
earlier directives of 2026-10-03/04, in the same file's §3, agree with it. So does the work already
merged: the build-in-public strategy under `content/` and the `sys-content` registry entry
(owner, 2026-10-04).

## The question

Ideas `000015` → `000016` → `000017` form one expanding chain: one platform, then several, then
automation.

> **Do you want to build in public, and how far along this chain?**

| Rung | Idea | What a yes commits to |
|---|---|---|
| 1. One platform | `000015` X content series documenting D-System development | A recurring series on X, drafted from repository records (ADRs, completed phases, lessons, milestones). The owner's time to approve and publish each post. Confidentiality discipline on every draft. A public narrative of the work |
| 2. Several platforms | `000016` Multi-platform public presence strategy | Choosing which platforms (LinkedIn, Bluesky, GitHub, Mastodon or others) and a format and cadence for each. Per-platform adaptation of the same material. Accounts the owner creates and runs. More publishing time |
| 3. Automation | `000017` AI-powered content automation pipeline | Agents that draft, adapt and schedule posts from D-System work and track engagement. A build: requirements, a plan and phases. Platform API access and credentials the owner holds. An automated confidentiality gate. A rule for what may publish without the owner |

Each rung could be answered *yes*, *not now* (stays parked, with a condition for asking again) or
*no* (declined). A yes to a higher rung presupposes the rungs below it.

## The answer

Quoted as given (owner, 2026-10-04 evening; restart file §P, P2):

> "phase-expl-02: the owner's answer is YES to all three rungs: 000015 X series (realized by the
> content/ strategy), 000016 multi-platform presence, 000017 content automation pipeline. Tonight
> expl-02 records that answer and a short sizing note per rung (effort, prerequisites, first step);
> governed plans/phases for 000016 and 000017 wait for a planning session with the owner. No
> content and no platform account (the phase's acceptance)."

The surrounding directives (restart file §3, owner 2026-10-03/04) say: build in public, yes; an X
series; the strategy in the top-level `content/` directory; a cadence of five posts a week; and
media of diagrams and AI briefs, with animations, videos and shareable reference documents later.

## Disposition per rung

### Rung 1 — `000015`, the X series: yes, under way

- **Disposition.** Accepted. It is realized by the content strategy under `content/`
  (`sys-content`, registered at draft maturity): the arc, the five pillars, the image style, the
  post queue and the first drafts.
- **Effort.** Ongoing rather than a build: five posts a week, drafted with agents and approved and
  published by the owner. At that rate the eight-stage arc in `content/arc.md` runs about eight
  weeks (`content/README.md`).
- **Prerequisites.** In place: the strategy, the queue and the confidentiality rules. Still open,
  and the owner's, per `content/README.md`:
  - when the repository becomes visible, since no repository link goes out before that;
  - whether to set engagement targets;
  - the release date the arc builds toward.
- **First step.** The owner approves and publishes the first queued post in `content/calendar.md`,
  after the private-content check that file's rules require.

### Rung 2 — `000016`, multi-platform presence: yes, planning deferred to the owner

- **Disposition.** Accepted. Its governed plan and phases wait for a planning session with the
  owner, as the answer directs. Nothing is planned or built tonight.
- **Effort.** One planning session to choose the platforms and set each one's format and cadence.
  After that, per-platform adaptation work, sized once the platforms are known.
- **Prerequisites.**
  - The X series running, so there are published posts and their reception to learn from.
  - The owner's platform choices.
  - Accounts the owner creates. No agent creates a platform account.
- **First step.** A planning session with the owner that turns `000016` into a plan: which
  platforms, why, and the cadence for each.

### Rung 3 — `000017`, content automation: yes, planning deferred to the owner

- **Disposition.** Accepted. Its governed plan and phases wait for a planning session with the
  owner, after rung 2's platforms are chosen. Nothing is planned or built tonight.
- **Effort.** A multi-phase build, sized in its own planning session. The idea names:
  - drafting from repository records;
  - adaptation per platform;
  - scheduling;
  - engagement tracking.
- **Prerequisites.**
  - Rung 2's platform choices.
  - A manual workflow proven on rung 1, so automation follows a process that works.
  - Platform API access and credentials held by the owner.
  - The confidentiality check (`tools/check_no_private_content.py`) as a gate inside the
    pipeline.
  - An explicit rule for what, if anything, publishes without the owner. Today the owner
    publishes every post (`content/README.md`).
- **First step.** A requirements and planning session with the owner for `000017`. The template
  library's adaptation briefs (`tools/template_library.py`, `phase-des-03`) are one existing
  mechanism such a pipeline could draft through.

## Consequences

- None of the three ideas stays collectively parked: rung 1 is under way, and rungs 2 and 3 are
  accepted with a named next step.
- The ideas' statuses in `_data/ideas.jsonl` are moved by the idea writer, not by this record. This
  phase sends the Ideation session one note per idea; Ideation records them.
- No content was produced and no platform account was created by `phase-expl-02`, as its
  acceptance requires.
- Because the answer reached this record by relay, the owner is asked to confirm it in the morning
  report. If they amend it, this record is amended to match.
