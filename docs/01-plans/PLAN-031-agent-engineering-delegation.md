---
schema_version: 1
id: doc-agent-engineering-delegation
code: PLAN-031
title: Agent engineering and delegation (P4)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-governance, sys-delivery]
depends_on: []
---

# Agent engineering and delegation (P4)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-06`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P4` of the twelve, sixth in the owner's delivery order. How agents in general are
instructed, observed, coordinated and reviewed — as distinct from `P1`'s idea-log agents, which are
one application of it, and from `P5`'s unattended execution infrastructure, which none of this
assumes.

**19 ideas across 10 fine groups**, from the accepted partition of 2026-09-13. The largest
programme, sized at 12–15 phases. It also carries the most internal near-duplication, and the
partition says explicitly that it **deserves a scoping pass before any phase count is committed**.

| Group | Ideas | What it covers |
|---|---|---|
| `G14` Framework umbrella | `000078`, `000079`, `000080`, `000081`, `000082` | `000078` and its four named children — guides, sensors, context pipelines, orchestration |
| `G15` Truncation handling | `000077` | Resume a truncated subagent rather than rerunning it |
| `G16` Lifecycle roster | `000069`, `000072` | The planner/executor/verifier/auditor roster, and whether to build it in a Claude-specific format at all |
| `G17` Deliberation trio | `000073`, `000074`, `000075` | Expander, minimalist, arbiter — none of the three is useful alone |
| `G18` Anti-pattern tracking | `000097`, `000138` | The same ask a day apart at two scales; `000138` is the fuller description |
| `G19` Delegation methodology | `000139` | Dispatch-cost estimation, per-role model assignment, escalation, and a retrospective that updates the rules |
| `G20` Commands/skills/agents audit | `000013`, `000126` | `000126`'s "missing-and-needed" output is exactly `000013`'s question |
| `G21` Shared state model | `000128` | Extend `_tmpagent/` so cross-agent context stops being hand-carried by a coordinator |
| `G22` Runtime-evidence pack convention | `000136` | Browser smoke dispatch and runtime instruments as a pack-authoring convention |
| `G23` Transcript review | `000009` | Deterministic transcript extraction plus an independent adversarial reviewer |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P4`.
- **The prompt-pack protocol** ([GOV-008](../08-governance/GOV-008-prompt-pack-protocol.md)) and its **methodology decision** ([ADR-017](../04-decisions/ADR-017-prompt-pack-methodology.md)) — the delegation practice `G19` and `G22` would extend.
- **Portable agent workflows** ([PLAN-020](PLAN-020-portable-agent-workflows.md)) and [REQ-005](../06-requirements/REQ-005-portable-agent-workflows.md) — `G16` is gated on this.
- **`brain/procedures/`** — where anti-pattern records land today; relevant to both `G18` and `G22`.
- **Concurrency, git safety and enforcement** ([PLAN-026](PLAN-026-concurrency-git-safety.md)) — `P4` designs agents, `P3` constrains the ground they run on.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section, applied to
this programme — **plus a scoping pass first**. This is the one programme the partition flags as
needing its near-duplication resolved before any phase count means anything.

## Known facts not to rediscover

- **`000072`'s planner bullet duplicates `000046`**, which lives in `P1`'s `G04`. Only the control
  analyst caught it. The partition recommends striking the bullet rather than building it twice.
- **`G18`'s capture half is already delivered** by the `log-anti-patterns` skill. Derivation is what
  remains.
- **`G22` may already be satisfied.** Its substance may sit in
  `brain/procedures/runtime-behavior-needs-runtime-evidence.md` — verify before sizing it.
- **`G15` is shippable today** as prose guidance and was split from `G14` on that basis: `000080`
  needs monitoring infrastructure that does not exist, `000077` does not.
- **`G17` was kept out of `G16` on `000072`'s own instruction** — a different family, planned
  alongside but not merged.
- **`G21` is the light alternative to `000020`** in `P5`, which the control analyst nominated for
  decline in its favour.
- **`G23` is the weakest-evidenced placement in the whole partition.** It carries no recorded links
  to anything and was filed here by subject alone.
- **`000082` stays here rather than joining `P3`'s `G09`**: it is an open survey of orchestration,
  not the two diagnosed incidents.
