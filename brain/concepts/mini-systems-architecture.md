---
id: mem-concept-mini-systems
title: Mini Systems Architecture
type: concept
tags: [frameworks, agentic-systems, knowledge-base]
source_model: anthropic/claude-sonnet-4-6
project: d-system
created: 2026-09-05
updated: 2026-09-05
confidence: high
related: [mem-concept-json-sot]
scope: global
---

## Summary

Ten derived systems that act on the project/commitment/task/person/tag data to surface awareness, diagnose health, and synthesize actionable output. Organized in three tiers.

## Tier Architecture

```
Tier 1 — Collection (existing _data/ + brain/)
Tier 2 — Signals (SQL-computable DuckDB views, always live)
Tier 3 — Synthesis (AI-assisted, reads Tier 2, produces language)
```

## Tier 2: Signal Systems (pure SQL)

| System | Key Output |
|---|---|
| Project Health Signal | RAG status per project (review recency + commitments + blocks) |
| Cognitive Load Estimator | Weighted load score per project and portfolio total |
| Stale Radar | Projects overdue for review relative to their own cadence |
| Accountability Ledger | Open external commitments (promised_to) sorted by due date |
| Commitment Velocity Tracker | Created vs. completed per week — backlog growth trend |
| Tag Cluster Analyzer | Co-occurrence matrix, project clusters, orphaned projects |

## Tier 3: Synthesis Systems (AI-assisted)

| System | Reads | Produces |
|---|---|---|
| Context Pack | All Tier 1 + health/load | Project reload block for any AI session |
| Session Briefing | Stale + Ledger + Load | "What to work on today" — 3-5 items |
| Weekly Review | Briefing + Velocity + Health | Append-only session doc |
| Portfolio Digest | All Tier 2 | Monthly strategic view |

## Composition Patterns

```
Daily:   Stale Radar + Ledger + Load  →  Session Briefing
Weekly:  Briefing + Velocity + Health →  Weekly Review
Switch:  Tier 1 + Health + Ledger     →  Context Pack
Monthly: All Tier 2                   →  Portfolio Digest
```

## Minimum Data Habit

When you make a commitment → log it. When you complete it → mark it complete. Everything else derives from that.

Full spec: `docs/01-plans/PLAN-002-mini-systems-proposal.md`
