---
schema_version: 1
id: doc-workbench-features-defects
code: PLAN-027
title: Workbench features and defects (P11)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-ui, sys-demo-stage, sys-api]
depends_on: []
---

# Workbench features and defects (P11)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-02`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P11` of the twelve, second in the owner's delivery order. Discrete, mostly small,
user-facing features and bugs in the shipped workbench. The programme is an administrative rollup
rather than a single design: each group touches a different panel or route and is independently
shippable.

**16 ideas across 9 fine groups**, from the accepted partition of 2026-09-13. Sizing at partition
time was 8–10 phases excluding `G56`, which is already done.

| Group | Ideas | What it covers |
|---|---|---|
| `G48` HTML Viewer | `000102`, `000109`, `000110`, `000118`, `000119` | `000119` is the render-location decision the others collide without; `000118` extends the extension list; `000102` adds a freshness badge |
| `G49` File bookmarks | `000111`, `000120` | `000120` exists because `000111`'s "open a category as a set" has no mechanism without a batch panel-bridge contract |
| `G50` Rotator | `000131`, `000132` | Two variants of the same notes-strip component |
| `G51` Terminal interaction API | `000087` | External HTTP inject/read, detach/reattach, output buffering — the part `ADR-014` did not absorb |
| `G52` Session-cap race | `000095` | TOCTOU between the session-count check and `accept()` |
| `G53` Shell override docs | `000096` | `D_SYSTEM_DEMO_SHELL` silently overrides per-session selection |
| `G54` Flag-off 404 noise | `000100` | Cosmetic console noise when the terminal flag is unset |
| `G55` Websocket close reason | `000137` | A global-cap refusal reaches the browser as a bare 1006 instead of a structured close |
| `G56` PTY tests **[RESOLVED]** | `000099`, `000129` | **Already fixed** — 46 tests pass. Carried for completeness; no work remains |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P11`.
- **Workbench requirements** ([REQ-007](../06-requirements/REQ-007-workbench.md)) and the **workbench plan** ([PLAN-022](PLAN-022-workbench.md)) — the shipped product this programme changes.
- **Workbench terminal capability** ([ADR-014](../04-decisions/ADR-014-workbench-terminal-capability.md)) and **API surface** ([ADR-015](../04-decisions/ADR-015-workbench-api-surface.md)).
- **Demo terminal capability** ([ADR-013](../04-decisions/ADR-013-demo-terminal-capability.md)) — the precedent that says `G51` needs its own ADR.

`depends_on` is deliberately empty; the finalize phase sets the real edges.

## What finalizing requires

The four steps in [PLAN-026](PLAN-026-concurrency-git-safety.md)'s equivalent section, applied to
this programme: requirement, design, real phases under a registered prefix, and pruning
`phase-prog-02` from `next_up` on completion.

## Known facts not to rediscover

- **Decide `000119` first.** It is the load-bearing render-location decision; `000109` and `000110`
  conflict with each other until it is settled.
- **`G56` is already fixed.** 46 tests pass and the suite is green. Do not re-plan it.
- **`G51` needs its own ADR**, following `ADR-013`'s precedent — it is a new capability, not a
  defect fix. One analyst lost this idea entirely, so its evidence is thinner than the rest.
- **`000102` was placed here by content, not provenance.** Check the owner's ruling in the
  partition before assuming it belongs to the HTML Viewer group.
- **Ordering tension worth the owner's attention:** `G40` (vocabulary) sits in `P10`, which is
  sequenced *after* this programme, yet the partition names it a prerequisite wherever `P11` work
  renames anything. Either settle `G40` first or confine early `P11` phases to work that renames
  nothing.
