---
schema_version: 1
id: doc-standalone-explorations-housekeeping
code: PLAN-037
title: Standalone explorations and housekeeping (P12)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-governance, sys-api, sys-html]
depends_on: []
---

# Standalone explorations and housekeeping (P12)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-12`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P12` of the twelve, last in the owner's delivery order. **Nothing binds these together.**
The partition is explicit that this is a readability bucket: every group is independent of every
other idea in the corpus, including its bucket-mates. Six singletons and two small chains would
otherwise have inflated the programme count without adding a programme.

**11 ideas across 7 fine groups**, from the accepted partition of 2026-09-13. Size each member
alone — the bucket's total is not a meaningful number, and the partition says so.

| Group | Ideas | What it covers |
|---|---|---|
| `G57` Observability and telemetry | `000054` | System-wide logging, metrics and tracing |
| `G58` Content strategy | `000015`, `000016`, `000017` | One expanding chain: one platform → multi-platform → automation |
| `G59` Research scouting | `000068` | A capture pass over the `research/` corpus |
| `G60` Repo tracker | `000086` | A tracked-repo list plus a cross-repo awareness agent |
| `G61` Platform evaluation | `000122` | Non-web rebuild language and platform comparison |
| `G62` Websockets education | `000140` | An owner-education deep dive using this repository's terminal stack |
| `G63` Demo rehearsal placeholders | `000088`, `000090`, `000103` | Self-declared timing artifacts from dry runs, carrying no product content |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P12`, and the decline tiers covering `G63`.
- **`docs/08-governance/systems.yaml`** — `G57` has no home system; see the first known fact below.
- **The research protocol** ([GOV-009](../08-governance/GOV-009-research-protocol.md)) and `sys-research` — the corpus `G59` would scout without editing.
- **Workbench features and defects** ([PLAN-027](PLAN-027-workbench-features-defects.md)) — its `G55` websocket close-reason defect is the worked example `G62` would teach from.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

This programme is the one case where finalizing may reasonably produce **several small plans or
none at all**, rather than one. The bucket exists for readability; it is not a design. The finalize
phase should rule on each member separately and may conclude that some belong in other programmes,
some get their own plan, and some are declined.

## Known facts not to rediscover

- **`G63` was nominated for decline by all four analysts** — the strongest decline signal in the
  partition. Three ideas, zero product content, self-declared as rehearsal timing artifacts. Rule on
  them before spending a phase on them.
- **`G57` is unscoped and needs a scoping pass.** No `sys-observability` exists, and the work spans
  `sys-api`, `sys-projection` and `sys-html`. The partition also rules that it is **not** a child of
  `000080`, despite the surface resemblance.
- **`G58` is the cleanest mutual-exclusivity case in the corpus** — it shares no file, system or
  consumer with anything. Its internal order is fixed: `000015` → `000016` → `000017`. One session
  to decide.
- **`G59` produces ideas, not features**, and edits no research file.
- **`G61` is deliberately future-only** — a document, not code.
- **`G62` produces no product code.** It is owner education, and should not be sized as a build.
- **`G60` may split into two ideas on contact** — the tracked list and the agent over it are
  arguably separate asks.
