---
schema_version: 1
id: doc-concurrency-git-safety
code: PLAN-026
title: Concurrency, git safety and enforcement (P3)
kind: plan
status: draft
owner: repository-owner
created: '2026-09-14'
updated: '2026-09-14'
systems: [sys-governance, sys-backlog, sys-delivery]
depends_on: []
---

# Concurrency, git safety and enforcement (P3)

> **Placeholder. Not a finalized plan.** It carries no design, no chosen approach, and no
> implementation phases. Its single phase, `phase-prog-01`, is to finalize it: write the
> requirement, settle the design, and replace the sections below with real content and real
> session-sized phases. **Do not build from this document.**

## Summary

Programme `P3` of the twelve, first in the owner's delivery order. Every member hardens how
concurrent agents share one repository without destroying each other's work. This is the programme
the partition sweep itself kept generating instances of: two fresh cases appeared during triage, and
a third appeared on 2026-09-14 when the private-content check reported `0 identifiers checked` from
a worktree and `31` from the primary checkout.

**10 ideas across 5 fine groups**, from the accepted partition of 2026-09-13. Sizing at partition
time was 6–8 phases, which is an estimate and not a commitment.

| Group | Ideas | What it covers |
|---|---|---|
| `G09` Claim and clobber hardening | `000025`, `000041` | Two observed protocol failures — an abandoned claim with no recovery path, and a `git stash` that destroyed a peer's uncommitted work |
| `G10` Branch protection and PR gate | `000066` | Branch topology, GitHub settings, CI-as-gate, and the multi-agent pull-request protocol |
| `G11` Version control and backup | `000021`, `000058`, `000059` | `000058` is the umbrella, `000059` its git slice, `000021` the concrete gap for gitignored `_private/` |
| `G12` Harness enforcement | `000012`, `000014`, `000051` | Where enforcement belongs — hooks, settings, tests or prose. `000051` was created to parent the other two |
| `G13` `AGENTS.md` push-rule rewrite | `000091` | Two hunks in one file, replacement text already approved and recorded twice |

## Key references

- **The partition** — [`docs/00-working/idea-batching-partition.md`](../00-working/idea-batching-partition.md), section `P3`, for the six-field record and the independence argument against `P4`.
- **The handoff** — [`docs/00-working/handoff-idea-partition-and-triage.md`](../00-working/handoff-idea-partition-and-triage.md), which names convention-without-enforcement as one of the two families dominating the backlog and identifies it as this programme.
- **Multi-agent concurrency** ([ADR-003](../04-decisions/ADR-003-multi-agent-concurrency.md)) — the accepted claim-and-lock model this programme hardens.
- **Accepted backlog decisions** ([GOV-003](../08-governance/GOV-003-backlog-decisions.md)) — carries the incidents that withdrew the documentation-only worktree exception on 2026-09-12.
- **`AGENTS.md`** — the three *Concurrent agents* sections are the rule this programme enforces mechanically rather than in prose.

`depends_on` is deliberately empty. A placeholder has source material, not prerequisite documents,
and the finalize phase sets the real edges rather than inheriting guesses made here.

## What finalizing requires

1. Write the requirement with observable statements and verification methods, allocating its code
   with `uv run python -m src.governance --next-code requirement`.
2. Settle the design questions the partition left open, listed below.
3. Replace this document's Summary and Design with the real plan, and add session-sized phases
   under a new `phase-*` prefix registered in [the backlog README](../09-backlog/README.md).
4. Remove `phase-prog-01` from `next_up` in the same change that completes it.

## Known facts not to rediscover

- **`G10` is no longer blocked.** The repository being public was the named workaround for the 403
  that stalled it; two analysts carried the stale blocker forward.
- **`G12`'s "blocked pending remote/CI" note is stale.** Both now exist.
- **`G13` is blocked by the owner's own tooling**, not by design: `.claude/settings.json` denies
  `Edit(AGENTS.md)`. It needs the owner to apply the approved text by hand or lift the rule. No
  agent may edit `AGENTS.md` regardless — see that file's own standing rule.
- **`G09` should land after `G10`'s document rewrite**, because both touch the same `AGENTS.md`
  passages.
- **`000027` (phase containment) sits in `P2`, not here**, and is the nearest existing mechanism to
  hang `000204` on.
