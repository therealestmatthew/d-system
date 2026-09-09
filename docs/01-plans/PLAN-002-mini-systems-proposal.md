---
schema_version: 1
id: doc-mini-systems
code: PLAN-002
title: Mini Systems Proposal
kind: plan
status: approved
owner: repository-owner
created: '2026-09-05'
updated: '2026-09-05'
systems:
- sys-signals
- sys-synthesis
depends_on: []
---

> Delivery is approved in phases. The [accepted user choices](../08-governance/GOV-003-backlog-decisions.md) resolve conflicting details below; the [session backlog](../09-backlog/README.md) tracks execution and completion. This document is a design source, not evidence of implementation.

# Mini Systems Proposal

Systems that act on the existing schemas (projects, commitments, tasks, people, tags) to derive meaning from accumulated data. Organized into three tiers: **collection** (what we already have), **signals** (computed from data), and **synthesis** (signals combined into language).

---

## Tier Architecture

```
Tier 1 — Collection (existing)
  _data/ JSON files → DuckDB tables
  projects, commitments, tasks, people, tags

Tier 2 — Signals (SQL-computable derived views)
  Health Signal, Load Estimator, Stale Radar,
  Accountability Ledger, Velocity Tracker, Tag Clusters

Tier 3 — Synthesis (AI-assisted, reads Tier 2)
  Context Pack, Session Briefing, Weekly Review,
  Portfolio Digest
```

Tier 2 systems are DuckDB views — always current, free to query. Tier 3 systems pull from Tier 2 and use an AI pass for language and judgment.

---

## Tier 2: Signal Systems

### 1. Project Health Signal
**Reads:** `projects`, `commitments`, `tasks`  
**Computes:** RAG status (Red / Amber / Green) per project based on:
- Days since `last_reviewed` vs expected cadence interval
- Count of open + overdue commitments
- Count of blocked tasks
- Whether project status is mismatched with activity (active but no commitments ever added)

**Output:** `v_project_health` view with columns: `project_id`, `status`, `health`, `days_overdue_review`, `open_commitments`, `blocked_tasks`

**Why it matters:** Surfaces neglected projects before they become embarrassing gaps.

---

### 2. Cognitive Load Estimator
**Reads:** `projects`, `commitments`  
**Computes:** Weighted load score per project:
```
load = Σ (commitment_weight × priority_multiplier) × cadence_multiplier
  priority_multiplier: high=3, medium=2, low=1
  cadence_multiplier:  daily=4, weekly=2, monthly=1, ad-hoc=0.5
```
Rolled up to a portfolio-level load total and a "top 5 heaviest" ranking.

**Output:** `v_cognitive_load` view; drives the session briefing.

**Why it matters:** Makes invisible mental weight visible. Shows where you're overloaded before you feel it.

---

### 3. Stale Radar
**Reads:** `projects`  
**Computes:** Projects where time elapsed since `last_reviewed` exceeds the cadence interval:
```
daily     → stale after  2 days
weekly    → stale after 10 days
biweekly  → stale after 18 days
monthly   → stale after 45 days
ad-hoc    → stale after 90 days
ongoing   → stale after 60 days
```

**Output:** `v_stale_projects` view ordered by days overdue.

**Why it matters:** Commitment cadence is a promise to yourself. The stale radar makes broken promises visible.

---

### 4. Accountability Ledger
**Reads:** `commitments`, `people`  
**Computes:** All open commitments where `promised_to IS NOT NULL`, joined with person name, grouped by person, sorted by due date.

**Output:** `v_accountability_ledger` view — what you owe, to whom, by when, how overdue.

**Why it matters:** External commitments carry social weight. This view tracks your word.

---

### 5. Commitment Velocity Tracker
**Reads:** `commitments` (requires time-series data to accumulate)  
**Computes:**
- Commitments created per week (rolling 4-week window)
- Commitments completed per week (same window)
- Net backlog delta: created − completed
- Trend: accelerating, stable, or draining

**Output:** `v_commitment_velocity` view + weekly snapshot appended to `_data/snapshots/velocity_YYYY-WW.json` (append-only log)

**Why it matters:** Velocity exposes whether your system is sustainable. Consistent creation > completion = burnout trajectory.

---

### 6. Tag Cluster Analyzer
**Reads:** `project_tags`, `tags`, `projects`  
**Computes:**
- Tag co-occurrence matrix (which tags appear together most)
- Project clusters: groups of projects sharing ≥2 tags
- Orphaned projects: active projects with 0 tags or only 1 tag (under-classified)
- Tag density: which tags span the most projects

**Output:** `v_tag_clusters` view; JSON export for graph visualization.

**Why it matters:** Hidden connections between projects reveal portfolio coherence and over-concentration risk.

---

## Tier 3: Synthesis Systems

### 7. Context Pack Generator
**Reads:** All Tier 1 tables + Tier 2 health/load signals  
**Trigger:** Called with a `project_id` (or list of them)  
**Produces:** A structured Markdown block containing:
- Project metadata (name, status, category, type, description)
- Health signal and load score
- Open commitments (with priority and due dates)
- Open tasks by commitment
- Stakeholders and their roles
- Related projects (via shared tags — top 3 by overlap)
- Last 3 completed commitments (recent history)

**Format:** Ready to paste as AI context. This is the "reload" mechanism for picking up a project after time away.

**Why it matters:** Eliminates the "re-read everything" tax at the start of every session.

---

### 8. Session Briefing
**Reads:** Stale Radar + Accountability Ledger + Cognitive Load + Project Health  
**Trigger:** Daily or on-demand  
**AI role:** Rank, prioritize, and narrate — not just list. Surfaces the 3–5 things most deserving attention given today's date, upcoming due dates, and load distribution.

**Output format:**
```
## Session Briefing — YYYY-MM-DD

### Needs Attention Now
- [project] has been stale 14 days (weekly cadence)
- [commitment] promised to [person] due in 2 days

### Highest Load Projects
1. [project] — X open commitments, Y high-priority

### Something to Close Today
- [task] is the next step on [commitment] — 15 min

### Long Quiet (no activity > 30 days, still active)
- [project], [project]
```

**Why it matters:** Converts a database into a daily operating rhythm.

---

### 9. Weekly Review Generator
**Reads:** Session Briefing + Velocity Tracker + Project Health (all projects)  
**Trigger:** Weekly (Friday or Sunday)  
**AI role:** Narrative synthesis — what was accomplished, what slipped, what changed in portfolio balance, one recommendation.

**Output:** Markdown document appended to `docs/03-sessions/YYYY-MM-DD-weekly-review.md`

**Why it matters:** Closes the loop. Creates a longitudinal record of how the portfolio evolves.

---

### 10. Portfolio Digest
**Reads:** All Tier 2 signals, all projects  
**Trigger:** Monthly or on-demand  
**AI role:** High-level synthesis across the whole portfolio — health distribution, load concentration, tag cluster shifts, velocity trend, people with most open commitments.

**Output:** Markdown report in `docs/03-sessions/` + HTML export via HTML Generation Framework

**Why it matters:** Monthly recalibration. Surfaces drift before it becomes structural.

---

## Composition Map

```
Daily use:
  Stale Radar
  Accountability Ledger    →  Session Briefing  →  "What do I work on today?"
  Cognitive Load

Weekly use:
  Session Briefing
  Velocity Tracker         →  Weekly Review     →  "What happened? What's next?"
  Project Health (all)

On project switch:
  Project Health
  Accountability Ledger    →  Context Pack      →  "What is the state of this project?"
  Tier 1 (raw data)

Monthly:
  All Tier 2 signals       →  Portfolio Digest  →  "Is my portfolio healthy?"
```

---

## Implementation Sequence (Recommended)

| Phase | Systems | Value Unlocked |
|---|---|---|
| 1 | Stale Radar, Accountability Ledger | Immediate — no AI needed, pure SQL |
| 2 | Project Health Signal, Cognitive Load | Portfolio-level awareness |
| 3 | Context Pack Generator | AI-assisted project reload |
| 4 | Session Briefing | Daily operating rhythm |
| 5 | Velocity Tracker + Weekly Review | Longitudinal tracking |
| 6 | Tag Cluster Analyzer, Portfolio Digest | Strategic portfolio view |

Each phase is independently useful. Phase 1 requires nothing beyond what's already built.

---

## Data Requirements to Make These Meaningful

The systems derive more value as more data accumulates. What feeds them:

| Signal | Requires |
|---|---|
| Stale Radar | Just `last_reviewed` dates on projects (update when you touch a project) |
| Accountability Ledger | Commitments with `promised_to` and `due_date` populated |
| Cognitive Load | Active commitments with `priority` set |
| Velocity Tracker | Commitments marked `complete` with `completed` dates |
| Context Pack | Projects with descriptions + stakeholders populated |
| Tag Clusters | Consistent tagging (at least 2–3 tags per project) |

The minimum viable data habit: **when you make a commitment, log it; when you complete it, mark it complete.**
